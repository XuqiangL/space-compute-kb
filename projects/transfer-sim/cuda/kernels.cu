//==============================================================================
// kernels.cu — 每个公式函数的 CUDA kernel（与 CPU golden 同一份公式源码）
//
// 设计原则：kernel 不重写数学——直接调用 include/gmath 下与 CPU 完全相同的
// 公式函数（GMATH_DEVICE 宏使它们在 nvcc 下编译为 __host__ __device__）。
// kernel 只负责"把公式并行应用到一批数据上"：
//
//   CPU 公式函数                       GPU kernel（elementwise/batch 并行）
//   ---------------------------------  ----------------------------------------
//   accel_point_mass(r, mu, a)         k_accel_point_mass（N 个状态并行）
//   accel_j2(r, mu, Re, J2, a)         k_accel_j2
//   accel_third_body(r, rb, mu, a)     k_accel_third_body
//   cartesian_from_kepler(el, mu, r,v) k_kep_to_cart（N 组要素并行）
//   anomaly_E_from_M(M, e)             k_E_from_M
//   mdot_from_isp(...)                 k_mdot
//   mass_after_dv(...)                 k_rocket
//   rk45_step / rk45_adaptive          k_propagate_batch（每线程块一条轨迹）
//
// 内存布局：轨迹 = 3D 批量张量 (M × N_OUT × 7)，行主序（tensors.hpp 公式）。
//==============================================================================
#include <cstdio>
#include <cmath>

#include "gmath/constants.hpp"
#include "gmath/vec_math.hpp"
#include "gmath/elements.hpp"
#include "gmath/accelerations.hpp"
#include "gmath/integrators.hpp"
#include "gmath/burns.hpp"
#include "gmath/tensors.hpp"

using namespace gmath;

//------------------------------------------------------------------------------
// 1. accel_point_mass 批量 kernel：每线程一个状态 r（N 个 3 维向量）
//    公式：a_i = -μ·r_i/||r_i||³
//------------------------------------------------------------------------------
__global__ void k_accel_point_mass(const double* r, double mu, double* a, int N)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;
    const double ri[3] = { r[3*i], r[3*i+1], r[3*i+2] };
    accel_point_mass(ri, mu, &a[3*i]);
}

//------------------------------------------------------------------------------
// 2. accel_j2 批量 kernel
//    公式：a = -3/2·J2·(μ/r²)·(Re/r)²·[x/r(1-5(z/r)²), y/r(1-5(z/r)²), z/r(3-5(z/r)²)]
//------------------------------------------------------------------------------
__global__ void k_accel_j2(const double* r, double mu, double Re, double J2, double* a, int N)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;
    const double ri[3] = { r[3*i], r[3*i+1], r[3*i+2] };
    accel_j2(ri, mu, Re, J2, &a[3*i]);
}

//------------------------------------------------------------------------------
// 3. accel_third_body 批量 kernel（每线程一个 (r_sc, r_body) 对）
//    公式：a = -μ_b·(d/||d||³ + r_b/||r_b||³)，d = r_sc - r_body
//------------------------------------------------------------------------------
__global__ void k_accel_third_body(const double* rs, const double* rb,
                                   double mu_b, double* a, int N)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;
    const double rs_i[3] = { rs[3*i], rs[3*i+1], rs[3*i+2] };
    const double rb_i[3] = { rb[3*i], rb[3*i+1], rb[3*i+2] };
    accel_third_body(rs_i, rb_i, mu_b, &a[3*i]);
}

//------------------------------------------------------------------------------
// 4. cartesian_from_kepler 批量 kernel：每线程一组要素
//------------------------------------------------------------------------------
__global__ void k_kep_to_cart(const double* el, double mu, double* rv, int N)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;
    const double el_i[6] = { el[6*i], el[6*i+1], el[6*i+2],
                             el[6*i+3], el[6*i+4], el[6*i+5] };
    cartesian_from_kepler(el_i, mu, &rv[6*i], &rv[6*i+3]);
}

//------------------------------------------------------------------------------
// 5. anomaly_E_from_M 批量 kernel（开普勒方程 Newton 迭代）
//------------------------------------------------------------------------------
__global__ void k_E_from_M(const double* M, double e, double* E, int N)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;
    E[i] = anomaly_E_from_M(M[i], e);
}

//------------------------------------------------------------------------------
// 6. mdot / 火箭方程 批量 kernel
//------------------------------------------------------------------------------
__global__ void k_mdot(double T, double Isp, double g0, double* mdot, int N)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;
    mdot[i] = mdot_from_isp(T, Isp, g0);
}

__global__ void k_rocket(const double* m0, double dv, double Isp, double g0,
                         double* mf, int N)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;
    mf[i] = mass_after_dv(m0[i], dv, Isp, g0);
}

//------------------------------------------------------------------------------
// 7. 轨迹传播 kernel：每线程块一条轨迹（批量 Monte-Carlo 并行）
//    块内串行推进 PD45 自适应步，命中 SOI 停止；输出写 3D 批量张量
//    traj[(i·N_OUT + n)·7 + m]（tensors.hpp 行主序公式）
//------------------------------------------------------------------------------
struct DevOdeFunctor {
    ForceConfig cfg;
    __device__ void operator()(double t, const double y[6], void*, double d[6]) const
    { derivatives_keplerian(y, t, cfg, d); }
};

__global__ void k_propagate_batch(const double* y0_batch, int M, int max_steps,
                                  double h0, double tol, double soi_r,
                                  ForceConfig cfg_host,
                                  double* traj, int N_OUT, int* n_rows,
                                  double* t_soi_out)
{
    int i = blockIdx.x;
    if (i >= M) return;

    ForceConfig cfg = cfg_host;               // 每块私有拷贝（寄存器/本地内存）
    DevOdeFunctor f { cfg };

    double y[6];
    for (int m = 0; m < 6; ++m) y[m] = y0_batch[6*i + m];

    double t = 0.0, h = h0;
    // 首行
    traj[traj3d_offset(i, 0, 0, N_OUT)] = t;
    for (int m = 0; m < 6; ++m) traj[traj3d_offset(i, 0, m+1, N_OUT)] = y[m];

    int n = 1;
    double t_last_row = 0.0;
    for (int step = 0; step < max_steps; ++step) {
        double ynew[6];
        double h_taken = 0.0;
        double hnext = rk45_adaptive(f, t, y, h, tol, nullptr, ynew, &h_taken);
        t += h_taken;
        for (int m = 0; m < 6; ++m) y[m] = ynew[m];

        // 月球位置与 SOI 判据（与 CPU 一致）
        double rb[3];
        moon_position(cfg, t, rb);
        double dx = y[0]-rb[0], dy = y[1]-rb[1], dz = y[2]-rb[2];
        double d = std::sqrt(dx*dx + dy*dy + dz*dz);
        bool hit = (d <= soi_r) || (t > 15.0 * SECS_PER_DAY);

        if ((t - t_last_row >= 30.0) || hit) {
            if (n < N_OUT) {
                traj[traj3d_offset(i, n, 0, N_OUT)] = t;
                for (int m = 0; m < 6; ++m) traj[traj3d_offset(i, n, m+1, N_OUT)] = y[m];
            }
            ++n;
            t_last_row = t;
        }
        if (hit) break;
        h = hnext;
    }
    n_rows[i] = n;
    t_soi_out[i] = t;
}

//------------------------------------------------------------------------------
// 9. 定步传播 kernel（CPU/GPU 权威对比用：两边同 h 同步数，隔离纯浮点差异）
//------------------------------------------------------------------------------
__global__ void k_propagate_fixed(const double* y0_batch, int M, int n_steps,
                                  double h, ForceConfig cfg_host, double* yf_batch)
{
    int i = blockIdx.x;
    if (i >= M) return;
    ForceConfig cfg = cfg_host;
    DevOdeFunctor f { cfg };
    double y[6];
    for (int m = 0; m < 6; ++m) y[m] = y0_batch[6*i + m];
    double t = 0.0;
    for (int step = 0; step < n_steps; ++step) {
        double ynew[6], err[6];
        rk45_step(f, t, y, h, nullptr, ynew, err);
        for (int m = 0; m < 6; ++m) y[m] = ynew[m];
        t += h;
    }
    for (int m = 0; m < 6; ++m) yf_batch[6*i + m] = y[m];
}

//------------------------------------------------------------------------------
// 10. 能量批量 kernel（orbital_energy 的 GPU 并行化）
//------------------------------------------------------------------------------
__global__ void k_energy(const double* y, double mu, double* eps, int N)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;
    const double r[3] = { y[6*i], y[6*i+1], y[6*i+2] };
    const double v[3] = { y[6*i+3], y[6*i+4], y[6*i+5] };
    eps[i] = orbital_energy(r, v, mu);
}
