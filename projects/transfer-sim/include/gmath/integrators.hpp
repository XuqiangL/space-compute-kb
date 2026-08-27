//==============================================================================
// integrators.hpp — 数值积分器公式（MD-04《数值积分器数学》）
//
// PrinceDormand45（RK 4(5)，7 级 6 次函数求值，FSAL）——系数**逐字迁移**自
// NASA/GMAT 源码 src/base/propagator/PrinceDormand45.cpp:143-209 的
// SetCoefficients()（ai/bij/cj/ee），来源为 Prince & Dormand (1981)。
//
// Runge-Kutta 通式（MD-04 条目）：
//   k_i = f(t + ai_i·h,  y + h·Σ_{j<i} bij_ij·k_j)
//   y_{n+1} = y + h·Σ cj_i·k_i          （5 阶解）
//   误差估计 = h·Σ ee_i·k_i              （4 阶解与 5 阶解之差，FSAL: ee[6]=1/50）
//==============================================================================
#pragma once
#include <cmath>
#include "vec_math.hpp"

namespace gmath {

//------------------------------------------------------------------------------
// PD45 系数表（PrinceDormand45.cpp:150-208 逐字）
//------------------------------------------------------------------------------
GMATH_DEVICE inline void pd45_coefficients(double ai[7], double bij[7][7],
                                           double cj[7], double ee[7])
{
    ai[0]=0.0; ai[1]=2.0/9.0; ai[2]=1.0/3.0; ai[3]=5.0/9.0; ai[4]=2.0/3.0; ai[5]=1.0; ai[6]=1.0;

    for (int i=0;i<7;++i) for (int j=0;j<7;++j) bij[i][j]=0.0;
    bij[1][0]= 2.0/9.0;
    bij[2][0]= 1.0/12.0;    bij[2][1]= 1.0/4.0;
    bij[3][0]= 55.0/324.0;  bij[3][1]=-25.0/108.0;   bij[3][2]= 50.0/81.0;
    bij[4][0]= 83.0/330.0;  bij[4][1]=-13.0/22.0;    bij[4][2]= 61.0/66.0;   bij[4][3]= 9.0/110.0;
    bij[5][0]=-19.0/28.0;   bij[5][1]= 9.0/4.0;      bij[5][2]= 1.0/7.0;    bij[5][3]=-27.0/7.0;   bij[5][4]= 22.0/7.0;
    bij[6][0]= 19.0/200.0;  bij[6][1]= 0.0;          bij[6][2]= 3.0/5.0;    bij[6][3]=-243.0/400.0; bij[6][4]= 33.0/40.0;  bij[6][5]= 7.0/80.0;

    cj[0]= 19.0/200.0; cj[1]=0.0; cj[2]= 3.0/5.0; cj[3]=-243.0/400.0;
    cj[4]= 33.0/40.0;  cj[5]= 7.0/80.0; cj[6]= 0.0;

    ee[0]= 19.0/200.0 - 431.0/5000.0;
    ee[1]= 0.0;
    ee[2]= 3.0/5.0    - 333.0/500.0;
    ee[3]=-243.0/400.0 + 7857.0/10000.0;
    ee[4]= 33.0/40.0   - 957.0/1000.0;
    ee[5]= 7.0/80.0    - 193.0/2000.0;
    ee[6]= 1.0/50.0;
}

// 函数签名：f(t, y[6], ctx, dydt[6])；ctx 由调用方传递（如 ForceConfig*）
template <typename F>
GMATH_DEVICE inline void rk45_step(F f, double t, const double y[6], double h,
                                   void* ctx, double ynew[6], double err[6])
{
    double ai[7], cj[7], ee[7], bij[7][7];
    pd45_coefficients(ai, bij, cj, ee);

    double k[7][6];
    double tmp[6];
    // 级 0：k0 = f(t, y)
    f(t, y, ctx, k[0]);
    // 级 i=1..6：k_i = f(t + ai_i·h, y + h·Σ_{j<i} bij_ij·k_j)
    for (int i = 1; i < 7; ++i) {
        for (int m = 0; m < 6; ++m) {
            double acc = 0.0;
            for (int j = 0; j < i; ++j) acc += bij[i][j] * k[j][m];
            tmp[m] = y[m] + h * acc;
        }
        f(t + ai[i] * h, tmp, ctx, k[i]);
    }
    // 5 阶解与误差（FSAL：第 7 级 k6 即下一步的 k0，此处不缓存）
    for (int m = 0; m < 6; ++m) {
        double acc = 0.0, eacc = 0.0;
        for (int j = 0; j < 7; ++j) {
            acc  += cj[j] * k[j][m];
            eacc += ee[j] * k[j][m];
        }
        ynew[m] = y[m] + h * acc;
        err[m]  = h * eacc;
    }
}

//------------------------------------------------------------------------------
// rk45_adaptive — 误差控制 + 步长自适应（对应 RungeKutta::AdaptStep，MD-04 §步长控制）
// 公式：err_norm = ||err||（6 维欧氏范数）；若 err_norm ≤ tol 接受，
//       否则 h ← h·max(0.2, min(0.9, 0.9·(tol/err_norm)^{1/5})) 重试；
//       接受后下一步 h ← h·max(0.2, min(5, 0.9·(tol/err_norm)^{1/5}))。
//       5 次方根来自 5 阶方法局部误差 ∝ h⁵。
// 返回：建议的下一步步长；*h_taken 输出本次实际采用的步长（重试后 ≠ 请求值！）。
//------------------------------------------------------------------------------
template <typename F>
GMATH_DEVICE inline double rk45_adaptive(F f, double t, const double y[6],
                                         double h, double tol, void* ctx,
                                         double ynew[6], double* h_taken)
{
    double err[6], trial[6];
    double hh = h;
    for (int attempt = 0; attempt < 12; ++attempt) {
        rk45_step(f, t, y, hh, ctx, trial, err);
        const double e = norm6(err);
        if (e <= tol) {
            for (int m = 0; m < 6; ++m) ynew[m] = trial[m];
            double fac = 0.9 * std::pow(tol / (e + 1e-30), 0.2);
            if (fac > 5.0) fac = 5.0;
            if (fac < 0.2) fac = 0.2;
            if (h_taken) *h_taken = hh;
            return hh * fac;      // 建议的下一步步长
        }
        double fac = 0.9 * std::pow(tol / (e + 1e-30), 0.2);
        if (fac > 0.9) fac = 0.9;
        if (fac < 0.2) fac = 0.2;
        hh *= fac;
    }
    // 兜底：以最小步接受（调用方应检查）
    rk45_step(f, t, y, hh, ctx, ynew, err);
    if (h_taken) *h_taken = hh;
    return hh;
}

//------------------------------------------------------------------------------
// propagate — 主传播循环（对应 Propagator::Step 循环 + StopCondition 穿越检测）
// 输入：初状态 y0、步长与容差、终点判据函数 done(t, y, ctx)（如 SOI 穿越）
// 输出：把 (t, y) 追加进轨迹数组 traj（2D 张量，见 tensors.hpp）
// 返回：步数（穿越前最后一步的状态包含在 traj 内）
//------------------------------------------------------------------------------
template <typename F, typename Done>
GMATH_DEVICE inline int propagate(F f, double t0, const double y0[6], double h0,
                                  double tol, void* ctx, Done done,
                                  double* traj, int max_steps)
{
    double t = t0, y[6], h = h0;
    for (int m = 0; m < 6; ++m) y[m] = y0[m];
    for (int m = 0; m < 7; ++m) traj[m] = (m == 0) ? t : y[m-1];   // 行 0 = (t, y)

    int n = 1;
    for (int step = 0; step < max_steps; ++step) {
        double ynew[6], h_taken = 0.0;
        double hnext = rk45_adaptive(f, t, y, h, tol, ctx, ynew, &h_taken);
        t += h_taken;
        for (int m = 0; m < 6; ++m) y[m] = ynew[m];
        for (int m = 0; m < 7; ++m) traj[n*7 + m] = (m == 0) ? t : y[m-1];
        ++n;
        if (done(t, y, ctx)) break;
        h = hnext;
    }
    return n;
}

} // namespace gmath
