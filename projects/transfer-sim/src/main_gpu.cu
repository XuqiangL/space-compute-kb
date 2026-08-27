//==============================================================================
// main_gpu.cu — GPU CUDA 版本 + CPU/GPU 逐公式对比 + 批量传播
//
// 工作流：
//   1) 生成 N 个随机状态 → 每个公式函数在 CPU 与 GPU 上各算一遍 → 输出最大/平均
//      绝对差（逐公式对比表，写入 data/gpu_compare.csv）
//   2) 批量传播：M 条轨迹（名义 + 蒙特卡洛扰动）在 GPU 上并行 → 名义轨迹写
//      data/trajectory_gpu.csv，供与 CPU golden（main_cpu）做逐点对比
//   3) 计时对比：CPU 单条 vs GPU 批量吞吐
//==============================================================================
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <vector>
#include <algorithm>

#include "gmath/constants.hpp"
#include "gmath/vec_math.hpp"
#include "gmath/elements.hpp"
#include "gmath/accelerations.hpp"
#include "gmath/integrators.hpp"
#include "gmath/burns.hpp"
#include "gmath/tensors.hpp"

using namespace gmath;

// kernels.cu 中定义的 kernel 声明
__global__ void k_accel_point_mass(const double* r, double mu, double* a, int N);
__global__ void k_accel_j2(const double* r, double mu, double Re, double J2, double* a, int N);
__global__ void k_accel_third_body(const double* rs, const double* rb, double mu_b, double* a, int N);
__global__ void k_kep_to_cart(const double* el, double mu, double* rv, int N);
__global__ void k_E_from_M(const double* M, double e, double* E, int N);
__global__ void k_mdot(double T, double Isp, double g0, double* mdot, int N);
__global__ void k_rocket(const double* m0, double dv, double Isp, double g0, double* mf, int N);
__global__ void k_propagate_batch(const double* y0_batch, int M, int max_steps,
                                  double h0, double tol, double soi_r,
                                  ForceConfig cfg_host, double* traj, int N_OUT,
                                  int* n_rows, double* t_soi_out);
__global__ void k_propagate_fixed(const double* y0_batch, int M, int n_steps,
                                  double h, ForceConfig cfg_host, double* yf_batch);
__global__ void k_energy(const double* y, double mu, double* eps, int N);

#define CUDA_CHECK(e)                                                       \
    do {                                                                    \
        cudaError_t _e = (e);                                               \
        if (_e != cudaSuccess) {                                            \
            std::fprintf(stderr, "CUDA error %s at line %d\n",              \
                         cudaGetErrorString(_e), __LINE__);                 \
            std::exit(1);                                                   \
        }                                                                   \
    } while (0)

// 简单 LCG（与设备无关，仅主机生成测试数据）
static unsigned g_seed = 12345u;
static double urand()
{
    g_seed = g_seed * 1103515245u + 12345u;
    return double(g_seed % 1000000u) / 1000000.0;
}

//------------------------------------------------------------------------------
// 逐公式 CPU vs GPU 对比：统计最大/平均绝对差
//------------------------------------------------------------------------------
struct CompareRow { const char* name; double max_abs, mean_abs; };

static void compare_formula(const char* name, const double* cpu, const double* gpu,
                            int n, std::vector<CompareRow>& rows)
{
    double mx = 0.0, sm = 0.0;
    for (int i = 0; i < n; ++i) {
        double d = std::abs(cpu[i] - gpu[i]);
        if (d > mx) mx = d;
        sm += d;
    }
    rows.push_back({ name, mx, sm / n });
    std::printf("  %-28s max|diff|=%.3e  mean|diff|=%.3e\n", name, mx, sm / n);
}

int main(int argc, char** argv)
{
    int N = 1 << 20;      // 逐公式对比的数据量
    int M = 256;          // 批量轨迹数
    const char* outdir = "data";
    for (int i = 1; i < argc; ++i) {
        if      (!strcmp(argv[i], "--N")  && i+1 < argc) N = std::atoi(argv[++i]);
        else if (!strcmp(argv[i], "--M")  && i+1 < argc) M = std::atoi(argv[++i]);
        else if (!strcmp(argv[i], "--out") && i+1 < argc) outdir = argv[++i];
    }

    int dev = 0;
    CUDA_CHECK(cudaSetDevice(dev));
    cudaDeviceProp prop;
    CUDA_CHECK(cudaGetDeviceProperties(&prop, dev));
    std::printf("GPU: %s (CC %d.%d, %.0f MiB)\n", prop.name, prop.major, prop.minor,
                prop.totalGlobalMem / 1048576.0);

    std::vector<CompareRow> cmp;

    // ---------- 1) 逐公式对比 ----------
    std::printf("== 1) per-formula CPU vs GPU comparison (N=%d) ==\n", N);

    // 随机状态：r（3N）、rb（3N）、el（6N）、M（N）、m0（N）
    std::vector<double> hr(3*N), hrb(3*N), ha_cpu(3*N), ha_gpu(3*N);
    std::vector<double> hel(6*N), hrv_cpu(6*N), hrv_gpu(6*N);
    std::vector<double> hM(N), hE_cpu(N), hE_gpu(N), hm0(N), hmf_cpu(N), hmf_gpu(N), hmd(N), heps_cpu(N), heps_gpu(N), h6(6*N);
    for (int i = 0; i < N; ++i) {
        for (int k = 0; k < 3; ++k) {
            hr[3*i+k]  = (urand() - 0.5) * 20000.0;
            hrb[3*i+k] = (urand() - 0.5) * 800000.0;
        }
        hel[6*i+0] = 6500.0 + urand() * 40000.0;   // SMA
        hel[6*i+1] = urand() * 0.8;                 // ECC
        hel[6*i+2] = urand() * PI;                  // INC
        hel[6*i+3] = urand() * 2.0*PI;              // RAAN
        hel[6*i+4] = urand() * 2.0*PI;              // AOP
        hel[6*i+5] = urand() * 2.0*PI;              // TA
        hM[i] = urand() * 2.0*PI;
        hm0[i] = 500.0 + urand() * 2000.0;
        for (int k = 0; k < 6; ++k) h6[6*i+k] = hr[3*i+(k%3)] + ((k<3)?0.0:urand());
    }

    double *dr, *drb, *da, *del, *drv, *dM_, *dE, *dm0, *dmf, *dmd, *deps, *d6;
    CUDA_CHECK(cudaMalloc(&dr,  3*N*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&drb, 3*N*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&da,  3*N*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&del, 6*N*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&drv, 6*N*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&dM_, N*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&dE,  N*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&dm0, N*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&dmf, N*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&dmd, N*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&deps, N*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d6,  6*N*sizeof(double)));
    CUDA_CHECK(cudaMemcpy(dr,  hr.data(),  3*N*sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(drb, hrb.data(), 3*N*sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(del, hel.data(), 6*N*sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(dM_, hM.data(),  N*sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(dm0, hm0.data(), N*sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d6,  h6.data(),  6*N*sizeof(double), cudaMemcpyHostToDevice));

    int block = 256;
    int grid  = (N + block - 1) / block;

    // accel_point_mass
    k_accel_point_mass<<<grid, block>>>(dr, MU_EARTH, da, N);
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(ha_gpu.data(), da, 3*N*sizeof(double), cudaMemcpyDeviceToHost));
    for (int i = 0; i < N; ++i) {
        const double ri[3] = { hr[3*i], hr[3*i+1], hr[3*i+2] };
        accel_point_mass(ri, MU_EARTH, &ha_cpu[3*i]);
    }
    compare_formula("accel_point_mass", ha_cpu.data(), ha_gpu.data(), 3*N, cmp);

    // accel_j2
    k_accel_j2<<<grid, block>>>(dr, MU_EARTH, RE_EARTH, J2_EARTH, da, N);
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(ha_gpu.data(), da, 3*N*sizeof(double), cudaMemcpyDeviceToHost));
    for (int i = 0; i < N; ++i) {
        const double ri[3] = { hr[3*i], hr[3*i+1], hr[3*i+2] };
        accel_j2(ri, MU_EARTH, RE_EARTH, J2_EARTH, &ha_cpu[3*i]);
    }
    compare_formula("accel_j2", ha_cpu.data(), ha_gpu.data(), 3*N, cmp);

    // accel_third_body
    k_accel_third_body<<<grid, block>>>(dr, drb, MU_MOON, da, N);
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(ha_gpu.data(), da, 3*N*sizeof(double), cudaMemcpyDeviceToHost));
    for (int i = 0; i < N; ++i) {
        const double ri[3]  = { hr[3*i],  hr[3*i+1],  hr[3*i+2] };
        const double rbi[3] = { hrb[3*i], hrb[3*i+1], hrb[3*i+2] };
        accel_third_body(ri, rbi, MU_MOON, &ha_cpu[3*i]);
    }
    compare_formula("accel_third_body", ha_cpu.data(), ha_gpu.data(), 3*N, cmp);

    // cartesian_from_kepler
    k_kep_to_cart<<<grid, block>>>(del, MU_EARTH, drv, N);
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(hrv_gpu.data(), drv, 6*N*sizeof(double), cudaMemcpyDeviceToHost));
    for (int i = 0; i < N; ++i) {
        const double el_i[6] = { hel[6*i], hel[6*i+1], hel[6*i+2], hel[6*i+3], hel[6*i+4], hel[6*i+5] };
        cartesian_from_kepler(el_i, MU_EARTH, &hrv_cpu[6*i], &hrv_cpu[6*i+3]);
    }
    compare_formula("cartesian_from_kepler", hrv_cpu.data(), hrv_gpu.data(), 6*N, cmp);

    // anomaly_E_from_M
    k_E_from_M<<<grid, block>>>(dM_, 0.3, dE, N);
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(hE_gpu.data(), dE, N*sizeof(double), cudaMemcpyDeviceToHost));
    for (int i = 0; i < N; ++i) hE_cpu[i] = anomaly_E_from_M(hM[i], 0.3);
    compare_formula("anomaly_E_from_M", hE_cpu.data(), hE_gpu.data(), N, cmp);

    // mdot / rocket
    k_mdot<<<grid, block>>>(1000.0, 300.0, G0_KM, dmd, N);
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(hmd.data(), dmd, N*sizeof(double), cudaMemcpyDeviceToHost));
    double mdot_cpu = mdot_from_isp(1000.0, 300.0, G0_KM);
    {
        double mx = 0.0; for (int i = 0; i < N; ++i) mx = std::max(mx, std::abs(hmd[i] - mdot_cpu));
        cmp.push_back({"mdot_from_isp", mx, 0.0});
        std::printf("  %-28s max|diff|=%.3e\n", "mdot_from_isp", mx);
    }
    k_rocket<<<grid, block>>>(dm0, 3.14, 300.0, G0_KM, dmf, N);
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(hmf_gpu.data(), dmf, N*sizeof(double), cudaMemcpyDeviceToHost));
    for (int i = 0; i < N; ++i) hmf_cpu[i] = mass_after_dv(hm0[i], 3.14, 300.0, G0_KM);
    compare_formula("mass_after_dv", hmf_cpu.data(), hmf_gpu.data(), N, cmp);

    // energy（附加校验 kernel）
    k_energy<<<grid, block>>>(d6, MU_EARTH, deps, N);
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(heps_gpu.data(), deps, N*sizeof(double), cudaMemcpyDeviceToHost));
    for (int i = 0; i < N; ++i) {
        const double r[3] = { h6[6*i], h6[6*i+1], h6[6*i+2] };
        const double v[3] = { h6[6*i+3], h6[6*i+4], h6[6*i+5] };
        heps_cpu[i] = orbital_energy(r, v, MU_EARTH);
    }
    compare_formula("orbital_energy", heps_cpu.data(), heps_gpu.data(), N, cmp);

    // ---------- 2) 批量传播（GPU） ----------
    std::printf("== 2) GPU batch propagation (M=%d) ==\n", M);

    ForceConfig cfg;
    cfg.mu_central = MU_EARTH; cfg.Re = RE_EARTH; cfg.J2 = J2_EARTH;
    cfg.use_j2 = true; cfg.use_moon = true;
    cfg.mu_moon = MU_MOON; cfg.a_moon = A_MOON; cfg.n_moon = N_MOON;
    cfg.moon_lon0 = 0.0;

    // 名义初态 + 相位对齐（与 main_cpu 相同：无月球定相跑）
    double el[6] = { RE_EARTH + 200.0, 0.0, 28.5*PI/180.0, 0.0, 0.0, 0.0 };
    double r0[3], v0[3], v_tli[3];
    cartesian_from_kepler(el, MU_EARTH, r0, v0);
    double vdir[3]; burn_direction_velocity(v0, vdir);
    saxpy(3.14, vdir, v0, v_tli);

    {
        ForceConfig cfg_nm = cfg; cfg_nm.use_moon = false;
        struct NoMoonCtx { ForceConfig cfg; } c0 { cfg_nm };
        auto f0 = [](double t, const double y[6], void* ctx, double d[6]) {
            ForceConfig* c = &static_cast<NoMoonCtx*>(ctx)->cfg;
            derivatives_keplerian(y, t, *c, d);
        };
        double t = 0.0, y[6], h = 60.0, ynew[6];
        for (int m = 0; m < 3; ++m) { y[m] = r0[m]; y[3+m] = v_tli[m]; }
        for (int step = 0; step < 200000; ++step) {
            double h_taken = 0.0;
            double hnext = rk45_adaptive(f0, t, y, h, 1e-11, &c0, ynew, &h_taken);
            t += h_taken;
            for (int m = 0; m < 6; ++m) y[m] = ynew[m];
            if (std::sqrt(y[0]*y[0]+y[1]*y[1]+y[2]*y[2]) >= A_MOON) break;
            h = hnext;
        }
        double theta_arr = std::atan2(y[1], y[0]);
        cfg.moon_lon0 = theta_arr - cfg.n_moon * t;
        std::printf("  moon phasing: lon0 = %.6f rad\n", cfg.moon_lon0);
    }

    // ---------- 1.5) 定步 CPU/GPU 权威对比（同 h 同步数，纯浮点差异） ----------
    std::printf("== 1.5) fixed-step CPU vs GPU (identical step sequence) ==\n");
    {
        const int n_fix = 20000;
        const double h_fix = 30.0;
        std::vector<double> yf_cpu(6), yf_gpu(6);
        // 初态：TLI 后状态（含月球相位），与批量传播一致
        double y0[6];
        for (int m = 0; m < 3; ++m) { y0[m] = r0[m]; y0[3+m] = v_tli[m]; }

        // CPU 定步
        struct FixCtx { ForceConfig cfg; } fc { cfg };
        auto ff = [](double t, const double y[6], void* ctx, double d[6]) {
            ForceConfig* c = &static_cast<FixCtx*>(ctx)->cfg;
            derivatives_keplerian(y, t, *c, d);
        };
        {
            double t = 0.0, y[6], ynew[6], err[6];
            for (int m = 0; m < 6; ++m) y[m] = y0[m];
            for (int s = 0; s < n_fix; ++s) {
                rk45_step(ff, t, y, h_fix, &fc, ynew, err);
                for (int m = 0; m < 6; ++m) y[m] = ynew[m];
                t += h_fix;
            }
            for (int m = 0; m < 6; ++m) yf_cpu[m] = y[m];
        }
        // GPU 定步
        double* d_y0; double* d_yf;
        CUDA_CHECK(cudaMalloc(&d_y0, 6*sizeof(double)));
        CUDA_CHECK(cudaMalloc(&d_yf, 6*sizeof(double)));
        CUDA_CHECK(cudaMemcpy(d_y0, y0, 6*sizeof(double), cudaMemcpyHostToDevice));
        k_propagate_fixed<<<1, 1>>>(d_y0, 1, n_fix, h_fix, cfg, d_yf);
        CUDA_CHECK(cudaDeviceSynchronize());
        CUDA_CHECK(cudaMemcpy(yf_gpu.data(), d_yf, 6*sizeof(double), cudaMemcpyDeviceToHost));
        CUDA_CHECK(cudaFree(d_y0)); CUDA_CHECK(cudaFree(d_yf));

        const char* nm[6] = {"x","y","z","vx","vy","vz"};
        double mx = 0.0;
        for (int m = 0; m < 6; ++m) {
            double d = std::abs(yf_cpu[m] - yf_gpu[m]);
            std::printf("  %-4s cpu=%.12e gpu=%.12e  diff=%.3e\n",
                        nm[m], yf_cpu[m], yf_gpu[m], d);
            if (d > mx) mx = d;
        }
        std::printf("  fixed-step %d steps: max|diff| = %.3e (pure FP divergence)\n", n_fix, mx);
        cmp.push_back({"fixed_step_propagate", mx, mx / 6.0});
    }

    double r_soi = soi_radius(A_MOON, MU_EARTH, MU_MOON);
    const int N_OUT = 24000;      // 每轨迹最多存 24000 行（30 s 采样 × ~8.3 天）
    std::vector<double> y0_batch(6*M);
    for (int i = 0; i < M; ++i) {
        double scale = (i == 0) ? 0.0 : 1.0e-6;   // 名义轨迹 + 微扰系综
        for (int m = 0; m < 3; ++m) {
            y0_batch[6*i+m]   = r0[m]   + scale * (urand() - 0.5) * 2.0;
            y0_batch[6*i+3+m] = v_tli[m] + scale * (urand() - 0.5) * 2.0;
        }
    }

    double *dy0, *dtraj, *dtsoi;
    int *dnrows;
    CUDA_CHECK(cudaMalloc(&dy0,   6*M*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&dtraj, (size_t)M*N_OUT*7*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&dtsoi, M*sizeof(double)));
    CUDA_CHECK(cudaMalloc(&dnrows, M*sizeof(int)));
    CUDA_CHECK(cudaMemcpy(dy0, y0_batch.data(), 6*M*sizeof(double), cudaMemcpyHostToDevice));

    cudaEvent_t ev0, ev1;
    CUDA_CHECK(cudaEventCreate(&ev0));
    CUDA_CHECK(cudaEventCreate(&ev1));
    CUDA_CHECK(cudaEventRecord(ev0));
    k_propagate_batch<<<M, 1>>>(dy0, M, 200000, 60.0, 1e-11, r_soi, cfg,
                                dtraj, N_OUT, dnrows, dtsoi);
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaEventRecord(ev1));
    CUDA_CHECK(cudaEventSynchronize(ev1));
    float ms = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&ms, ev0, ev1));
    std::printf("  GPU batch propagate: %.1f ms for %d trajectories (%.1f us/traj)\n",
                ms, M, ms * 1000.0 / M);

    std::vector<int> n_rows(M);
    CUDA_CHECK(cudaMemcpy(n_rows.data(), dnrows, M*sizeof(int), cudaMemcpyDeviceToHost));

    // 名义轨迹（i=0）写 CSV
    std::vector<double> traj0((size_t)n_rows[0] * 7);
    CUDA_CHECK(cudaMemcpy(traj0.data(), dtraj, (size_t)n_rows[0]*7*sizeof(double),
                          cudaMemcpyDeviceToHost));
    char path[512];
    std::snprintf(path, sizeof path, "%s/trajectory_gpu.csv", outdir);
    FILE* f = std::fopen(path, "w");
    if (f) {
        std::fprintf(f, "# t_sec, x, y, z, vx, vy, vz (GPU nominal)\n");
        for (int i = 0; i < n_rows[0]; ++i) {
            std::fprintf(f, "%.9e,%.12e,%.12e,%.12e,%.12e,%.12e,%.12e\n",
                         traj0[7*i], traj0[7*i+1], traj0[7*i+2], traj0[7*i+3],
                         traj0[7*i+4], traj0[7*i+5], traj0[7*i+6]);
        }
        std::fclose(f);
    }

    // ---------- 3) 对比报告 data/gpu_compare.csv ----------
    std::snprintf(path, sizeof path, "%s/gpu_compare.csv", outdir);
    f = std::fopen(path, "w");
    if (f) {
        std::fprintf(f, "# formula, max_abs_diff, mean_abs_diff\n");
        for (auto& r : cmp)
            std::fprintf(f, "%s,%.6e,%.6e\n", r.name, r.max_abs, r.mean_abs);
        std::fclose(f);
    }
    std::printf("  compare report -> %s/gpu_compare.csv\n", outdir);
    std::printf("done.\n");

    CUDA_CHECK(cudaFree(dr));  CUDA_CHECK(cudaFree(drb)); CUDA_CHECK(cudaFree(da));
    CUDA_CHECK(cudaFree(del)); CUDA_CHECK(cudaFree(drv)); CUDA_CHECK(cudaFree(dM_));
    CUDA_CHECK(cudaFree(dE));  CUDA_CHECK(cudaFree(dm0)); CUDA_CHECK(cudaFree(dmf));
    CUDA_CHECK(cudaFree(dmd)); CUDA_CHECK(cudaFree(deps)); CUDA_CHECK(cudaFree(d6));
    CUDA_CHECK(cudaFree(dy0)); CUDA_CHECK(cudaFree(dtraj)); CUDA_CHECK(cudaFree(dtsoi));
    CUDA_CHECK(cudaFree(dnrows));
    return 0;
}
