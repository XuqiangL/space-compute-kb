//==============================================================================
// main_cpu.cpp — 地月转移轨道仿真（CPU golden 实现）
//
// 场景：patched-conic 地月转移
//   Phase-0 停泊轨道：200 km 圆轨道，i=28.5°，θ=0（要素→状态：cartesian_from_kepler）
//   Phase-1 TLI：+3.14 km/s 顺向冲量（火箭方程：TLI 燃耗 Δm）
//   Phase-2 地心段：点质量 + J2 + 月球第三体（PD45 自适应积分）
//                 直到 |r_sc - r_moon| ≤ r_SOI ≈ 66183 km
//   Phase-3 月心段：切换中心体为月球，积分到近月点，记录 rp
//
// 输出（data/）：trajectory_earth.csv、trajectory_moon.csv、summary.txt、
//                energy_check.csv（能量守恒检验）
//==============================================================================
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <vector>

#include "gmath/constants.hpp"
#include "gmath/elements.hpp"
#include "gmath/accelerations.hpp"
#include "gmath/integrators.hpp"
#include "gmath/burns.hpp"
#include "gmath/tensors.hpp"

using namespace gmath;

// ---- ODE 回调上下文：把 ForceConfig 传给 rk45 ---------------------------------
struct OdeCtx { ForceConfig cfg; };

static void ode_f(double t, const double y[6], void* ctx, double dydt[6])
{
    ForceConfig* c = &static_cast<OdeCtx*>(ctx)->cfg;
    derivatives_keplerian(y, t, *c, dydt);
}

// 停止判据：到达月球影响球（或 15 天上限）
struct SoiDone {
    ForceConfig* cfg;
    double soi_r;
    bool operator()(double t, const double y[6], void*) const
    {
        if (t > 15.0 * SECS_PER_DAY) return true;
        double rb[3];
        moon_position(*cfg, t, rb);
        double dx = y[0]-rb[0], dy = y[1]-rb[1], dz = y[2]-rb[2];
        return std::sqrt(dx*dx+dy*dy+dz*dz) <= soi_r;
    }
};

// 停止判据：月心距离开始增大（过近月点）
struct PeriluneDone {
    bool armed = false;
    double r_prev = 0.0;
    bool operator()(double, const double y[6], void*)
    {
        double r = std::sqrt(y[0]*y[0]+y[1]*y[1]+y[2]*y[2]);
        bool passed = armed && (r > r_prev);
        r_prev = r; armed = true;
        return passed;
    }
};

// 停止判据：到达地月距离（Phase-1 无月球定相跑）
struct ReachMoonDistDone {
    double target_r;
    bool operator()(double, const double y[6], void*) const
    {
        return std::sqrt(y[0]*y[0]+y[1]*y[1]+y[2]*y[2]) >= target_r;
    }
};

//------------------------------------------------------------------------------
static int write_traj(const char* path, const std::vector<double>& traj, int n,
                      bool with_moon, const ForceConfig& cfg)
{
    FILE* f = std::fopen(path, "w");
    if (!f) return -1;
    std::fprintf(f, "# t_sec, x, y, z, vx, vy, vz");
    if (with_moon) std::fprintf(f, ", moon_x, moon_y, moon_z, dist_sm");
    std::fprintf(f, "\n");
    for (int i = 0; i < n; ++i) {
        const double* row = &traj[i * TRAJ_ROW];
        std::fprintf(f, "%.9e,%.12e,%.12e,%.12e,%.12e,%.12e,%.12e",
                     row[0], row[1], row[2], row[3], row[4], row[5], row[6]);
        if (with_moon) {
            double rb[3];
            moon_position(cfg, row[0], rb);
            double dx = row[1]-rb[0], dy = row[2]-rb[1], dz = row[3]-rb[2];
            std::fprintf(f, ",%.12e,%.12e,%.12e,%.12e",
                         rb[0], rb[1], rb[2], std::sqrt(dx*dx+dy*dy+dz*dz));
        }
        std::fprintf(f, "\n");
    }
    std::fclose(f);
    return 0;
}

//------------------------------------------------------------------------------
int main(int argc, char** argv)
{
    // ---- 参数解析 -----------------------------------------------------------
    double dv_tli = 3.14;         // TLI 冲量 km/s
    double tol    = 1e-11;        // PD45 相对误差容差（位置/速度量级混合）
    double h0     = 60.0;         // 初始步长 s
    int    max_steps = 200000;
    bool   finite_burn = false;
    bool   ref_mode = false;      // --ref：与 GMAT reference_1day 同场景（1 天、无月球、J2）
    double thrust_N = 500.0, isp_s = 300.0, m0_kg = 1000.0;
    const char* outdir = "data";
    for (int i = 1; i < argc; ++i) {
        if      (!strcmp(argv[i], "--finite-burn")) finite_burn = true;
        else if (!strcmp(argv[i], "--ref"))         ref_mode = true;
        else if (!strcmp(argv[i], "--tol") && i+1 < argc) tol = std::atof(argv[++i]);
        else if (!strcmp(argv[i], "--out") && i+1 < argc) outdir = argv[++i];
        else if (!strcmp(argv[i], "--dv") && i+1 < argc) dv_tli = std::atof(argv[++i]);
    }
    char path[512];

    // ---- --ref：GMAT 交叉验证场景（point mass + JGM2(2x0)≈J2，无月球，1 天） --
    if (ref_mode) {
        ForceConfig cfg_r;
        cfg_r.mu_central = MU_EARTH; cfg_r.Re = RE_EARTH; cfg_r.J2 = J2_EARTH;
        cfg_r.use_j2 = true; cfg_r.use_moon = false;
        OdeCtx ctxr; ctxr.cfg = cfg_r;
        // 与 reference_1day.script 相同的初态（LEO 200km i=28.5° θ=0 + 3.14 km/s）
        double elr[6] = { RE_EARTH + 200.0, 0.0, 28.5*PI/180.0, 0.0, 0.0, 0.0 };
        double rr[3], vv[3], vdir_r[3], v_tli_r[3];
        cartesian_from_kepler(elr, MU_EARTH, rr, vv);
        burn_direction_velocity(vv, vdir_r);
        saxpy(dv_tli, vdir_r, vv, v_tli_r);
        std::printf("[ref] initial state: r=(%.6f, %.6f, %.6f) v=(%.6f, %.6f, %.6f)\n",
                    rr[0], rr[1], rr[2], v_tli_r[0], v_tli_r[1], v_tli_r[2]);
        double t = 0.0, y[6], ynew[6], h = 60.0;
        for (int m = 0; m < 3; ++m) { y[m] = rr[m]; y[3+m] = v_tli_r[m]; }
        std::vector<double> rows;
        rows.push_back(0.0);
        for (int m = 0; m < 6; ++m) rows.push_back(y[m]);
        double t_last = 0.0;
        for (int step = 0; step < max_steps && t < 86400.0; ++step) {
            double h_taken = 0.0;
            double hnext = rk45_adaptive(ode_f, t, y, std::min(h, 86400.0 - t), tol, &ctxr, ynew, &h_taken);
            t += h_taken;
            for (int m = 0; m < 6; ++m) y[m] = ynew[m];
            if (t - t_last >= 60.0 || t >= 86400.0) {
                rows.push_back(t);
                for (int m = 0; m < 6; ++m) rows.push_back(y[m]);
                t_last = t;
            }
            h = hnext;
        }
        std::snprintf(path, sizeof path, "%s/ref_cpu_1day.csv", outdir);
        FILE* fr = std::fopen(path, "w");
        if (fr) {
            std::fprintf(fr, "# t_sec, x, y, z, vx, vy, vz\n");
            for (size_t i = 0; i < rows.size(); i += 7)
                std::fprintf(fr, "%.9e,%.12e,%.12e,%.12e,%.12e,%.12e,%.12e\n",
                             rows[i], rows[i+1], rows[i+2], rows[i+3],
                             rows[i+4], rows[i+5], rows[i+6]);
            std::fclose(fr);
        }
        std::printf("[ref] final state at t=%.1f s:\n", t);
        for (int m = 0; m < 6; ++m) std::printf("      %+.12e%s", y[m], (m==5) ? "\n" : ",");
        return 0;
    }

    // ---- 输入 1：停泊轨道要素 → 状态（MD-03：cartesian_from_kepler） ---------
    const double a_park = RE_EARTH + 200.0;
    double el[6] = { a_park, 0.0, 28.5 * PI / 180.0, 0.0, 0.0, 0.0 };
    double r0[3], v0[3];
    cartesian_from_kepler(el, MU_EARTH, r0, v0);

    // ---- 输入 2：TLI 冲量（MD-10：沿速度方向；火箭方程算燃料） ----------------
    double vdir[3];
    burn_direction_velocity(v0, vdir);
    double m_tli = m0_kg, m_burn_end = m0_kg;
    if (finite_burn) {
        m_burn_end = mass_after_dv(m0_kg, dv_tli, isp_s, G0_KM);
        double mdot = mdot_from_isp(thrust_N, isp_s, G0_KM);          // kg/s（负）
        double t_burn = (m_burn_end - m0_kg) / mdot;                  // 燃尽时间 s
        std::printf("[finite-burn] mdot=%.6f kg/s  burn_time=%.1f s  m_end=%.3f kg\n",
                    mdot, t_burn, m_burn_end);
    }
    double v_tli[3];
    saxpy(dv_tli, vdir, v0, v_tli);

    // ---- 力模型配置（MD-08/09 组装：点质量 + J2 + 月球第三体） ----------------
    ForceConfig cfg;
    cfg.mu_central = MU_EARTH; cfg.Re = RE_EARTH; cfg.J2 = J2_EARTH;
    cfg.use_j2 = true; cfg.use_moon = true;
    cfg.mu_moon = MU_MOON; cfg.a_moon = A_MOON; cfg.n_moon = N_MOON;
    cfg.mjd0 = MJD_J2000; cfg.moon_lon0 = 0.0;

    OdeCtx ctx; ctx.cfg = cfg;

    // ---- Phase-1（定相跑，无月球）：求到达地月距离处的时刻与经度 ------------
    ForceConfig cfg_nomoon = cfg; cfg_nomoon.use_moon = false;
    OdeCtx ctx_nomoon; ctx_nomoon.cfg = cfg_nomoon;
    ReachMoonDistDone done1 { A_MOON };
    // 传播（不存储中间点，只用终点）
    {
        double t = 0.0, y[6], h = h0;
        for (int m = 0; m < 3; ++m) { y[m] = r0[m]; y[3+m] = v_tli[m]; }
        double ynew[6];
        for (int step = 0; step < max_steps; ++step) {
            double h_taken = 0.0;
            double hnext = rk45_adaptive(ode_f, t, y, h, tol, &ctx_nomoon, ynew, &h_taken);
            t += h_taken;
            for (int m = 0; m < 6; ++m) y[m] = ynew[m];
            if (done1(t, y, nullptr)) break;
            h = hnext;
        }
        double theta_arr = std::atan2(y[1], y[0]);
        cfg.moon_lon0 = theta_arr - cfg.n_moon * t;          // 相位对齐
        ctx.cfg = cfg;
        std::printf("[phase-1] no-moon flight time to %.0f km: %.3f days, arrival lon %.3f deg\n",
                    A_MOON, t / SECS_PER_DAY, theta_arr * 180.0 / PI);
    }

    // ---- Phase-2（地心段）：点质量+J2+月球第三体，至月球 SOI ------------------
    double r_soi = soi_radius(A_MOON, MU_EARTH, MU_MOON);
    std::printf("[phase-2] r_SOI = %.1f km\n", r_soi);
    std::vector<double> traj_e(7);
    traj_e[0] = 0.0;
    for (int m = 0; m < 3; ++m) { traj_e[1+m] = r0[m]; traj_e[4+m] = v_tli[m]; }

    // 能量守恒检验量（沿传播记录 max |Δε|）
    double eps0 = orbital_energy(r0, v_tli, MU_EARTH);
    double max_deps = 0.0;

    {
        double t = 0.0, y[6], h = h0;
        for (int m = 0; m < 3; ++m) { y[m] = r0[m]; y[3+m] = v_tli[m]; }
        double ynew[6];
        SoiDone done2 { &cfg, r_soi };
        for (int step = 0; step < max_steps; ++step) {
            double h_taken = 0.0;
            double hnext = rk45_adaptive(ode_f, t, y, h, tol, &ctx, ynew, &h_taken);
            t += h_taken;
            for (int m = 0; m < 6; ++m) y[m] = ynew[m];
            // 每隔 30 s 记一行（输出张量 N×7）
            double t_last = traj_e[(traj_e.size()/7 - 1) * 7];
            if (t - t_last >= 30.0 || done2(t, y, nullptr)) {
                traj_e.push_back(t);
                for (int m = 0; m < 6; ++m) traj_e.push_back(y[m]);
            }
            double eps = orbital_energy(y, y + 3, MU_EARTH);
            double de = std::abs(eps - eps0);
            if (de > max_deps) max_deps = de;
            if (done2(t, y, nullptr)) break;
            h = hnext;
        }
        int n = (int)(traj_e.size() / 7);
        double t_arr = traj_e[(n-1)*7];
        std::snprintf(path, sizeof path, "%s/trajectory_earth.csv", outdir);
        write_traj(path, traj_e, n, true, cfg);
        std::printf("[phase-2] SOI entry at t=%.3f days, steps stored %d, max|dE|=%.3e\n",
                    t_arr / SECS_PER_DAY, n, max_deps);
    }

    // ---- Phase-3（月心段）：切中心体，积分至近月点 ----------------------------
    {
        int n = (int)(traj_e.size() / 7);
        const double* row = &traj_e[(n-1)*7];
        double t_soi = row[0];
        double rb[3]; moon_position(cfg, t_soi, rb);

        double ym[6];
        for (int m = 0; m < 3; ++m) ym[m] = row[1+m] - rb[m];
        // 月速 v_moon = ω×r_moon（圆轨道），逐分量：
        double vm[3] = { -cfg.n_moon * rb[1], cfg.n_moon * rb[0], 0.0 };
        for (int m = 0; m < 3; ++m) ym[3+m] = row[4+m] - vm[m];

        ForceConfig cfgm = cfg; cfgm.mu_central = MU_MOON; cfgm.use_moon = false;
        cfgm.use_j2 = false;
        OdeCtx ctxm; ctxm.cfg = cfgm;

        std::vector<double> traj_m(7);
        traj_m[0] = 0.0;
        for (int m = 0; m < 6; ++m) traj_m[1+m] = ym[m];

        double t = 0.0, y[6], h = 60.0, ynew[6];
        for (int m = 0; m < 6; ++m) y[m] = ym[m];
        PeriluneDone done3;
        for (int step = 0; step < max_steps; ++step) {
            double h_taken = 0.0;
            double hnext = rk45_adaptive(ode_f, t, y, h, tol, &ctxm, ynew, &h_taken);
            t += h_taken;
            for (int m = 0; m < 6; ++m) y[m] = ynew[m];
            double t_last = traj_m[(traj_m.size()/7 - 1) * 7];
            if (t - t_last >= 10.0 || done3(t, y, nullptr)) {
                traj_m.push_back(t);
                for (int m = 0; m < 6; ++m) traj_m.push_back(y[m]);
            }
            if (done3(t, y, nullptr)) break;
            h = hnext;
        }
        int nm = (int)(traj_m.size() / 7);
        double rp = std::sqrt(y[0]*y[0]+y[1]*y[1]+y[2]*y[2]);
        double vp = std::sqrt(y[3]*y[3]+y[4]*y[4]+y[5]*y[5]);
        std::snprintf(path, sizeof path, "%s/trajectory_moon.csv", outdir);
        write_traj(path, traj_m, nm, false, cfgm);
        std::printf("[phase-3] perilune rp=%.1f km (alt=%.1f km), vp=%.4f km/s, moon-phase time %.3f days\n",
                    rp, rp - RM_MOON, vp, t / SECS_PER_DAY);

        // ---- summary.txt ----------------------------------------------------
        std::snprintf(path, sizeof path, "%s/summary.txt", outdir);
        FILE* fs = std::fopen(path, "w");
        if (fs) {
            std::fprintf(fs, "Earth-Moon transfer (patched-conic, GMAT formula port)\n");
            std::fprintf(fs, "parking orbit : a=%.1f km (alt=200 km), i=28.5 deg\n", a_park);
            std::fprintf(fs, "TLI delta-v   : %.3f km/s\n", dv_tli);
            std::fprintf(fs, "integrator    : PrinceDormand45 (GMAT PD45 coefficients), tol=%.1e\n", tol);
            std::fprintf(fs, "force model   : point mass + J2(%.6e) + Moon 3rd body\n", J2_EARTH);
            std::fprintf(fs, "moon SOI      : %.1f km\n", r_soi);
            std::fprintf(fs, "transfer time : %.3f days\n", traj_e[(traj_e.size()/7-1)*7] / SECS_PER_DAY);
            std::fprintf(fs, "perilune      : rp=%.1f km (alt=%.1f km)\n", rp, rp - RM_MOON);
            std::fprintf(fs, "energy drift  : max|dE|=%.3e (check of integrator)\n", max_deps);
            if (finite_burn) std::fprintf(fs, "TLI fuel      : %.3f kg (finite burn T=%.0f N, Isp=%.0f s)\n",
                                          m0_kg - m_burn_end, thrust_N, isp_s);
            std::fclose(fs);
        }
    }

    std::printf("done. outputs in %s/\n", outdir);
    return 0;
}
