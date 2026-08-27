//==============================================================================
// test_formulas.cpp — 公式函数单元测试（CPU golden）
//
// 每个被封装公式函数至少一个测试用例；参照值全部由解析计算/已知物理事实给出
// （非"代码算一遍当答案"）。容差按公式量级设定。
//
// 测试清单（对应 math-deep-dive 章节）：
//   MD-01 时间    : jd_from_mjd / mjd_from_ymdhms(J2000) / tai-tt
//   MD-03 要素    : kep↔cart 往返（LEO/GEO/大偏心率）、近点角链、活力公式、SOI
//   MD-06/14 向量 : dot/cross/norm
//   MD-08 引力    : 点质量（地表 g）、J2（赤道/极轴解析值）、第三体（手工值）
//   MD-10 机动    : mdot、火箭方程
//   MD-04 积分器  : PD45 单步 vs RK4 对照、能量守恒（1 圈）、自适应 vs 定步
//   MD-00 场景    : 完整地月转移（近月点、飞行时间、能量漂移界）
//==============================================================================
#include <cstdio>
#include <cmath>
#include <algorithm>

#include "gmath/constants.hpp"
#include "gmath/time_math.hpp"
#include "gmath/elements.hpp"
#include "gmath/accelerations.hpp"
#include "gmath/integrators.hpp"
#include "gmath/burns.hpp"
#include "gmath/vec_math.hpp"
using namespace gmath;

static int g_fail = 0, g_pass = 0;

#define CHECK(cond, name)                                              \
    do {                                                               \
        if (cond) { ++g_pass; }                                        \
        else { ++g_fail; std::printf("FAIL  %-48s (line %d)\n", name, __LINE__); } \
    } while (0)

#define CHECK_NEAR(a, b, tol, name)                                    \
    do {                                                               \
        double _a = (a), _b = (b);                                     \
        if (std::abs(_a - _b) <= (tol)) { ++g_pass; }                  \
        else { ++g_fail;                                               \
               std::printf("FAIL  %-40s got %.12e want %.12e (line %d)\n", \
                           name, _a, _b, __LINE__); }                  \
    } while (0)

//==============================================================================
// MD-01 时间
//==============================================================================
static void test_time()
{
    // JD(MJD 21545) = 2451545.0（J2000）
    CHECK_NEAR(jd_from_mjd(MJD_J2000), 2451545.0, 1e-9, "MD-01 jd_from_mjd(J2000)");
    // 2000-01-01 12:00:00 → JD 2451545.0 → GMAT A.1 MJD 21544.5（= GmatDefaults TWO_BODY_EPOCH）
    CHECK_NEAR(mjd_from_ymdhms(2000, 1, 1, 12, 0, 0.0), 21544.5, 1e-9, "MD-01 mjd_from_ymdhms(J2000)");
    // A.1 MJD 零点 = JD 2430000.5 = 1941-01-06 0h
    CHECK_NEAR(mjd_from_ymdhms(1941, 1, 6, 0, 0, 0.0), 0.0, 1e-9, "MD-01 mjd_from_ymdhms(A.1 MJD0)");
    // TT - TAI = 32.184 s
    CHECK_NEAR(tai_from_tt(1000.0), 1000.0 - 32.184, 1e-12, "MD-01 tai_from_tt");
    CHECK_NEAR(tt_from_tai(1000.0), 1000.0 + 32.184, 1e-12, "MD-01 tt_from_tai");
}

//==============================================================================
// MD-06/14 向量
//==============================================================================
static void test_vec()
{
    double a[3] = {1, 2, 3}, b[3] = {4, 5, 6}, c[3];
    CHECK_NEAR(dot(a, b), 32.0, 1e-12, "MD-06 dot");
    cross(a, b, c);
    CHECK_NEAR(c[0], -3.0, 1e-12, "MD-06 cross.x");
    CHECK_NEAR(c[1],  6.0, 1e-12, "MD-06 cross.y");
    CHECK_NEAR(c[2], -3.0, 1e-12, "MD-06 cross.z");
    CHECK_NEAR(norm(a), std::sqrt(14.0), 1e-12, "MD-06 norm");
}

//==============================================================================
// MD-03 轨道要素
//==============================================================================
static void test_elements()
{
    // LEO 200km 圆轨道往返（e=0 时 ω 与 θ 简并，仅 ω+θ 之和有定义）
    double el[6] = { RE_EARTH + 200.0, 0.0, 28.5*PI/180.0, 1.0, 2.0, 3.0 };
    double r[3], v[3], el2[6];
    cartesian_from_kepler(el, MU_EARTH, r, v);
    kepler_from_cartesian(r, v, MU_EARTH, el2);
    CHECK_NEAR(el2[0], el[0], 1e-9, "MD-03 kep->cart->kep SMA");
    CHECK_NEAR(el2[1], el[1], 1e-12, "MD-03 kep->cart->kep ECC");
    CHECK_NEAR(el2[2], el[2], 1e-9, "MD-03 kep->cart->kep INC");
    CHECK_NEAR(el2[3], el[3], 1e-9, "MD-03 kep->cart->kep RAAN");
    CHECK_NEAR(el2[4] + el2[5], el[4] + el[5], 1e-9, "MD-03 kep->cart->kep AOP+TA (circular)");

    // 大偏心率椭圆（Molniya 型）往返
    double elh[6] = { 26500.0, 0.74, 63.4*PI/180.0, 0.5, -0.7, 2.4 };
    cartesian_from_kepler(elh, MU_EARTH, r, v);
    kepler_from_cartesian(r, v, MU_EARTH, el2);
    CHECK_NEAR(el2[0], elh[0], 1e-6, "MD-03 high-ecc SMA");
    CHECK_NEAR(el2[1], elh[1], 1e-9, "MD-03 high-ecc ECC");
    CHECK_NEAR(el2[5], elh[5], 1e-9, "MD-03 high-ecc TA");

    // 近点角链：M -> E -> TA -> M 往返（e=0.2, M=1.0）
    double M = 1.0, e = 0.2;
    double E  = anomaly_E_from_M(M, e);
    double TA = anomaly_TA_from_E(E, e);
    double M2 = anomaly_M_from_TA(TA, e);
    CHECK_NEAR(M2, M, 1e-12, "MD-03 anomaly chain M->E->TA->M");

    // 开普勒方程解析校验：E - e sinE = M
    CHECK_NEAR(E - e*std::sin(E), M, 1e-13, "MD-03 Kepler equation residual");

    // 活力公式：圆轨道 v = sqrt(mu/r)
    CHECK_NEAR(vis_viva(RE_EARTH+200.0, RE_EARTH+200.0, MU_EARTH),
               std::sqrt(MU_EARTH/(RE_EARTH+200.0)), 1e-9, "MD-03 vis-viva circular");

    // SOI：地月影响球 ≈ 66183 km
    double soi = soi_radius(A_MOON, MU_EARTH, MU_MOON);
    CHECK_NEAR(soi, 66183.0, 100.0, "MD-03 SOI radius ~66183 km");

    // 能量：圆轨道 ε = -mu/2a
    double rl[3] = {RE_EARTH+200.0, 0, 0};
    double vl[3] = {0, std::sqrt(MU_EARTH/(RE_EARTH+200.0)), 0};
    CHECK_NEAR(orbital_energy(rl, vl, MU_EARTH), -MU_EARTH/(2.0*(RE_EARTH+200.0)), 1e-6,
               "MD-03 orbital energy circular");
}

//==============================================================================
// MD-08 引力
//==============================================================================
static void test_accel()
{
    // 点质量：地球表面加速度 = mu/Re² = 9.798... m/s² = 9.798e-3 km/s²
    double r[3] = {RE_EARTH, 0, 0}, a[3];
    accel_point_mass(r, MU_EARTH, a);
    CHECK_NEAR(a[0], -MU_EARTH/(RE_EARTH*RE_EARTH), 1e-15, "MD-08 point mass a_x");
    CHECK_NEAR(a[1], 0.0, 1e-18, "MD-08 point mass a_y");
    CHECK_NEAR(a[2], 0.0, 1e-18, "MD-08 point mass a_z");

    // J2 赤道面 (z=0)：a_z = 0；a_x = -(3/2)J2 mu/Re²(1-0)·1（r=Re）
    double rj[3] = {RE_EARTH, 0, 0};
    accel_j2(rj, MU_EARTH, RE_EARTH, J2_EARTH, a);
    double expect_x = -1.5 * J2_EARTH * MU_EARTH/(RE_EARTH*RE_EARTH);
    CHECK_NEAR(a[0], expect_x, 1e-15, "MD-08 J2 equatorial a_x");
    CHECK_NEAR(a[2], 0.0, 1e-18, "MD-08 J2 equatorial a_z=0");

    // J2 极轴 (x=y=0, z=Re)：a_z = -(3/2)J2 mu/Re²(3-5) = +3 J2 mu/Re²（正，向赤道拉）
    double rp[3] = {0, 0, RE_EARTH};
    accel_j2(rp, MU_EARTH, RE_EARTH, J2_EARTH, a);
    double expect_z = 3.0 * J2_EARTH * MU_EARTH/(RE_EARTH*RE_EARTH);
    CHECK_NEAR(a[2], expect_z, 1e-15, "MD-08 J2 polar a_z");
    CHECK_NEAR(a[0], 0.0, 1e-18, "MD-08 J2 polar a_x=0");

    // 第三体：航天器在地球表面 x=Re，月球在 x=A_MOON 方向
    // d = r_sc - r_body：直接项朝 -x，间接项朝 +x；量级校验 vs 手工公式
    double rs[3] = {RE_EARTH, 0, 0}, rb[3] = {A_MOON, 0, 0};
    accel_third_body(rs, rb, MU_MOON, a);
    double d = RE_EARTH - A_MOON;
    double expect_tb = -MU_MOON*(d/(std::abs(d)*d*d) + rb[0]/(A_MOON*A_MOON*A_MOON));
    CHECK_NEAR(a[0], expect_tb, 1e-18, "MD-08 third body a_x hand value");

    // 力模型总加速度 = 三部分之和
    ForceConfig cfg;
    cfg.mu_central = MU_EARTH; cfg.Re = RE_EARTH; cfg.J2 = J2_EARTH;
    cfg.use_j2 = true; cfg.use_moon = true;
    cfg.mu_moon = MU_MOON; cfg.a_moon = A_MOON; cfg.n_moon = N_MOON;
    cfg.moon_lon0 = 0.0;
    double at[3], ap[3], aj[3], am[3];
    accel_total(rs, nullptr, 0.0, cfg, at);
    accel_point_mass(rs, MU_EARTH, ap);
    accel_j2(rs, MU_EARTH, RE_EARTH, J2_EARTH, aj);
    accel_third_body(rs, rb, MU_MOON, am);   // t=0 时月球在 x=A_MOON
    CHECK_NEAR(at[0], ap[0]+aj[0]+am[0], 1e-15, "MD-08 accel_total x sum");
    CHECK_NEAR(at[1], ap[1]+aj[1]+am[1], 1e-15, "MD-08 accel_total y sum");
    CHECK_NEAR(at[2], ap[2]+aj[2]+am[2], 1e-15, "MD-08 accel_total z sum");
}

//==============================================================================
// MD-10 机动
//==============================================================================
static void test_burns()
{
    // ṁ = -T/(Isp·g0)：T=1000N, Isp=300s → ṁ = -1000/(300·9.80665) = -0.33990... kg/s
    double mdot = mdot_from_isp(1000.0, 300.0, G0_KM);
    CHECK_NEAR(mdot, -1000.0/(300.0*9.80665), 1e-12, "MD-10 mdot_from_isp");

    // 火箭方程：m0=1000, dv=3.14 km/s, Isp=300 → m_f = 1000·e^{-3.14/(300·9.80665e-3)}
    double mf = mass_after_dv(1000.0, 3.14, 300.0, G0_KM);
    CHECK_NEAR(mf, 1000.0*std::exp(-3.14/(300.0*G0_KM)), 1e-9, "MD-10 rocket equation m_f");

    // 有限推力加速度：T=500N, m=1000kg → a = 0.5e-3 km/s²
    double dir[3] = {1,0,0}, a[3];
    accel_finite_thrust(500.0, 1000.0, dir, a);
    CHECK_NEAR(a[0], 0.5e-3, 1e-15, "MD-10 finite thrust a");

    // 速度方向单位矢
    double v[3] = {3,4,0}, d2[3];
    burn_direction_velocity(v, d2);
    CHECK_NEAR(d2[0], 0.6, 1e-12, "MD-10 burn dir x");
    CHECK_NEAR(d2[1], 0.8, 1e-12, "MD-10 burn dir y");
}

//==============================================================================
// MD-04 积分器：两体圆轨道 1 圈能量守恒 + 与解析解位置对比
//==============================================================================
struct OdeCtx { ForceConfig cfg; };

static void ode_f(double t, const double y[6], void* ctx, double dydt[6])
{
    ForceConfig* c = &static_cast<OdeCtx*>(ctx)->cfg;
    derivatives_keplerian(y, t, *c, dydt);
}

static void test_integrator()
{
    ForceConfig cfg;
    cfg.mu_central = MU_EARTH; cfg.Re = RE_EARTH; cfg.J2 = 0.0;
    cfg.use_j2 = false; cfg.use_moon = false;
    OdeCtx ctx; ctx.cfg = cfg;

    // 圆轨道初态
    const double a = RE_EARTH + 500.0;
    double y[6] = {a, 0, 0, 0, std::sqrt(MU_EARTH/a), 0};
    const double T_orbit = 2.0*PI*std::sqrt(a*a*a/MU_EARTH);
    const double eps0 = orbital_energy(y, y+3, MU_EARTH);

    // 定步 PD45：h = T/200，积分一圈
    double t = 0.0, ynew[6], err[6];
    const double h = T_orbit / 200.0;
    for (int i = 0; i < 200; ++i) {
        rk45_step(ode_f, t, y, h, &ctx, ynew, err);
        for (int m = 0; m < 6; ++m) y[m] = ynew[m];
        t += h;
    }
    double eps1 = orbital_energy(y, y+3, MU_EARTH);
    CHECK_NEAR(eps1, eps0, 1e-10*std::abs(eps0), "MD-04 PD45 fixed-step energy (1 orbit)");
    // 回到出发点：|r - r0| 小（5 阶方法 h=T/200 的截断误差）
    double dr = std::sqrt((y[0]-a)*(y[0]-a) + y[1]*y[1] + y[2]*y[2]);
    CHECK(dr < 1e-3, "MD-04 PD45 1-orbit position return (dr<1e-3 km)");

    // 自适应 vs 定步：tol=1e-12 一圈后位置误差更小
    double y2[6] = {a, 0, 0, 0, std::sqrt(MU_EARTH/a), 0};
    double t2 = 0.0, hh = 60.0;
    int steps = 0;
    while (t2 < T_orbit) {
        double h_taken = 0.0;
        double hnext = rk45_adaptive(ode_f, t2, y2, std::min(hh, T_orbit - t2), 1e-12, &ctx, ynew, &h_taken);
        t2 += h_taken;
        for (int m = 0; m < 6; ++m) y2[m] = ynew[m];
        hh = hnext;
        if (++steps > 100000) break;
    }
    double dr2 = std::sqrt((y2[0]-a)*(y2[0]-a) + y2[1]*y2[1] + y2[2]*y2[2]);
    CHECK(dr2 < 1e-6, "MD-04 PD45 adaptive 1-orbit return (dr<1e-6 km)");
}

//==============================================================================
// MD-00 场景：完整地月转移（与 main_cpu 同一模型，断言物理量级）
//==============================================================================
struct SoiDoneT {
    ForceConfig* cfg;
    double soi_r;
    bool operator()(double t, const double y[6], void*) const
    {
        if (t > 15.0*SECS_PER_DAY) return true;
        double rb[3]; moon_position(*cfg, t, rb);
        double dx=y[0]-rb[0], dy=y[1]-rb[1], dz=y[2]-rb[2];
        return std::sqrt(dx*dx+dy*dy+dz*dz) <= soi_r;
    }
};

static void test_transfer()
{
    ForceConfig cfg;
    cfg.mu_central = MU_EARTH; cfg.Re = RE_EARTH; cfg.J2 = J2_EARTH;
    cfg.use_j2 = true; cfg.use_moon = true;
    cfg.mu_moon = MU_MOON; cfg.a_moon = A_MOON; cfg.n_moon = N_MOON;
    cfg.moon_lon0 = 0.0;

    // 定相：无月球跑 → 到达地月距离的时间与经度
    ForceConfig cfg_nm = cfg; cfg_nm.use_moon = false;
    OdeCtx ctx_nm; ctx_nm.cfg = cfg_nm;

    double el[6] = { RE_EARTH + 200.0, 0.0, 28.5*PI/180.0, 0.0, 0.0, 0.0 };
    double r0[3], v0[3], v_tli[3];
    cartesian_from_kepler(el, MU_EARTH, r0, v0);
    double vdir[3]; burn_direction_velocity(v0, vdir);
    saxpy(3.14, vdir, v0, v_tli);

    double t = 0.0, y[6], h = 60.0, ynew[6];
    for (int m = 0; m < 3; ++m) { y[m]=r0[m]; y[3+m]=v_tli[m]; }
    for (int step = 0; step < 200000; ++step) {
        double h_taken = 0.0;
        double hnext = rk45_adaptive(ode_f, t, y, h, 1e-11, &ctx_nm, ynew, &h_taken);
        t += h_taken;
        for (int m = 0; m < 6; ++m) y[m] = ynew[m];
        double rr = std::sqrt(y[0]*y[0]+y[1]*y[1]+y[2]*y[2]);
        if (rr >= A_MOON) break;
        h = hnext;
    }
    double theta_arr = std::atan2(y[1], y[0]);
    cfg.moon_lon0 = theta_arr - cfg.n_moon * t;

    // 含月球积分到 SOI
    OdeCtx ctx; ctx.cfg = cfg;
    double r_soi = soi_radius(A_MOON, MU_EARTH, MU_MOON);
    SoiDoneT done { &cfg, r_soi };
    t = 0.0; h = 60.0;
    for (int m = 0; m < 3; ++m) { y[m]=r0[m]; y[3+m]=v_tli[m]; }
    double t_soi = -1.0;
    for (int step = 0; step < 200000; ++step) {
        double h_taken = 0.0;
        double hnext = rk45_adaptive(ode_f, t, y, h, 1e-11, &ctx, ynew, &h_taken);
        t += h_taken;
        for (int m = 0; m < 6; ++m) y[m] = ynew[m];
        if (done(t, y, nullptr)) { t_soi = t; break; }
        h = hnext;
    }
    CHECK(t_soi > 0.0, "MD-00 transfer: reached Moon SOI");
    // 月球第三体引力会提前拉近航天器：无月定相 3.76 天，含月 SOI 进入 2.93 天
    CHECK(t_soi > 2.5*SECS_PER_DAY && t_soi < 9.5*SECS_PER_DAY,
          "MD-00 transfer: flight time in [2.5,9.5] days");

    // 月心段到近月点
    double rb[3]; moon_position(cfg, t_soi, rb);
    double ym[6];
    for (int m = 0; m < 3; ++m) ym[m] = y[m] - rb[m];
    double vm[3] = { -cfg.n_moon*rb[1], cfg.n_moon*rb[0], 0.0 };
    for (int m = 0; m < 3; ++m) ym[3+m] = y[3+m] - vm[m];

    ForceConfig cfgm = cfg; cfgm.mu_central = MU_MOON; cfgm.use_moon = false; cfgm.use_j2 = false;
    OdeCtx ctxm; ctxm.cfg = cfgm;

    double tm = 0.0, hm = 60.0, r_prev = norm(ym);
    bool passed = false;
    for (int step = 0; step < 200000; ++step) {
        double h_taken = 0.0;
        double hnext = rk45_adaptive(ode_f, tm, ym, hm, 1e-11, &ctxm, ynew, &h_taken);
        tm += h_taken;
        for (int m = 0; m < 6; ++m) ym[m] = ynew[m];
        double rr = norm(ym);
        if (rr > r_prev) { passed = true; break; }
        r_prev = rr;
        hm = hnext;
    }
    CHECK(passed, "MD-00 transfer: passed perilune");
    double rp = r_prev;
    CHECK(rp > RM_MOON, "MD-00 transfer: perilune above surface");
    CHECK(rp < 20000.0, "MD-00 transfer: perilune < 20000 km (capture-class)");
}

//==============================================================================
int main()
{
    std::printf("== GMAT formula unit tests (CPU golden) ==\n");
    test_time();
    test_vec();
    test_elements();
    test_accel();
    test_burns();
    test_integrator();
    test_transfer();
    std::printf("== RESULT: %d passed, %d failed ==\n", g_pass, g_fail);
    return g_fail == 0 ? 0 : 1;
}
