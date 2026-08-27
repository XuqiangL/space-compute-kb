//==============================================================================
// accelerations.hpp — 力模型加速度公式（MD-08《引力场模型数学》）
//
// 每个函数 = 一个力模型公式。与 GMAT 对应实现：
//   - accel_point_mass  : src/base/forcemodel/PointMassForce.cpp（GetDerivatives）
//   - accel_j2          : J2 带谐（球谐 2 阶特例，Harmonic.cpp Pines 递推的解析退化）
//   - accel_third_body  : src/base/forcemodel/PointMassForce.cpp 的第三体间接项
// 单位：km / km/s / s。
//==============================================================================
#pragma once
#include <cmath>
#include "vec_math.hpp"

namespace gmath {

//------------------------------------------------------------------------------
// accel_point_mass(r[3], mu) — 点质量中心引力加速度（MD-08 §牛顿引力）
// 公式：a = -μ·r / ||r||³
// 讲解：牛顿万有引力。GMAT 中每个中心天体就是一个 PointMassForce：
//       a_i = -μ_central·r_i/r³（PointMassForce.cpp GetDerivatives 主项）。
//------------------------------------------------------------------------------
GMATH_DEVICE inline void accel_point_mass(const double r[3], double mu, double a[3])
{
    const double rn = norm(r);
    const double k  = -mu / (rn * rn * rn);
    a[0] = k * r[0]; a[1] = k * r[1]; a[2] = k * r[2];
}

//------------------------------------------------------------------------------
// accel_j2(r[3], mu, Re, J2) — J2 带谐摄动加速度（球谐展开 2 阶 zonal 特例）
// 公式（惯性系分量，经典 Vallado §10 形式）：
//   a_x = -3/2·J2·(μ/r²)·(Re/r)²·(x/r)·(1 - 5(z/r)²)
//   a_y = -3/2·J2·(μ/r²)·(Re/r)²·(y/r)·(1 - 5(z/r)²)
//   a_z = -3/2·J2·(μ/r²)·(Re/r)²·(z/r)·(3 - 5(z/r)²)
// 讲解：这是球谐势 V = μ/r[1 - J2(Re/r)²P₂(sinφ)] 的梯度；P₂(sinφ)=½(3sin²φ-1)，
//       sinφ = z/r。与 Harmonic.cpp 的 Pines 递推在 n=2 时逐位一致
//       （GMAT 默认重力场 EGM96/JGM-2 的 2 阶项即此式，J2 由 C̄20 换算，见 constants.hpp）。
//------------------------------------------------------------------------------
GMATH_DEVICE inline void accel_j2(const double r[3], double mu, double Re, double J2,
                                  double a[3])
{
    const double rn  = norm(r);
    const double zr  = r[2] / rn;
    const double zr2 = zr * zr;
    const double c   = -1.5 * J2 * (mu / (rn * rn)) * (Re / rn) * (Re / rn);

    a[0] = c * (r[0] / rn) * (1.0 - 5.0 * zr2);
    a[1] = c * (r[1] / rn) * (1.0 - 5.0 * zr2);
    a[2] = c * (r[2] / rn) * (3.0 - 5.0 * zr2);
}

//------------------------------------------------------------------------------
// accel_third_body(r_sc[3], r_body[3], mu_body) — 第三体摄动加速度（间接项）
// 公式：a = -μ_b·( d/||d||³ + r_b/||r_b||³ )，d = r_sc - r_body
// 讲解：航天器受摄动体的直接引力减去中心天体所受摄动体引力（非惯性系修正）。
//       对应 PointMassForce.cpp 中 PointMasses 列表的累加项（MD-08 §第三体）。
//       本仿真中 r_body 由两体月球星历给出（circular 近似，见 main_cpu.cpp）。
//------------------------------------------------------------------------------
GMATH_DEVICE inline void accel_third_body(const double r_sc[3], const double r_body[3],
                                          double mu_body, double a[3])
{
    double d[3];
    vsub(r_sc, r_body, d);
    const double dn = norm(d);
    const double bn = norm(r_body);

    a[0] = -mu_body * (d[0] / (dn*dn*dn) + r_body[0] / (bn*bn*bn));
    a[1] = -mu_body * (d[1] / (dn*dn*dn) + r_body[1] / (bn*bn*bn));
    a[2] = -mu_body * (d[2] / (dn*dn*dn) + r_body[2] / (bn*bn*bn));
}

//------------------------------------------------------------------------------
// accel_total(r_sc, v_sc, t, sim) — 本仿真力模型总加速度（中心引力 + J2 + 月球第三体）
// 公式：a = a_point(r,μ⊕) + a_J2(r) + a_third(r, r_moon(t))
// 讲解：即 GMAT 力模型的简化版——ODEModel 对每个 ForceModel 的 GetDerivatives
//       求和（MD-08/09 数据流）；此处不含大气/光压（地月转移段可忽略）。
//------------------------------------------------------------------------------
struct ForceConfig {
    double mu_central;        // 中心天体 μ
    double Re;                // 中心天体赤道半径（J2 用）
    double J2;                // J2 系数（0 表示关闭）
    bool   use_j2;
    bool   use_moon;          // 是否计入月球第三体
    double mu_moon;
    double a_moon;            // 月球轨道半径（圆轨道星历）
    double n_moon;            // 月球角速度
    double mjd0;              // 星历起点（MJ2000Eq 参考历元）
    double moon_lon0;         // 月球初始经度（rad）
};

GMATH_DEVICE inline void moon_position(const ForceConfig& c, double t_sec, double rb[3])
{
    const double lon = c.moon_lon0 + c.n_moon * t_sec;
    rb[0] = c.a_moon * std::cos(lon);
    rb[1] = c.a_moon * std::sin(lon);
    rb[2] = 0.0;
}

GMATH_DEVICE inline void accel_total(const double r[3], const double v[3], double t_sec,
                                     const ForceConfig& c, double a[3])
{
    (void)v;
    accel_point_mass(r, c.mu_central, a);
    if (c.use_j2) {
        double aj[3];
        accel_j2(r, c.mu_central, c.Re, c.J2, aj);
        a[0] += aj[0]; a[1] += aj[1]; a[2] += aj[2];
    }
    if (c.use_moon) {
        double rb[3], am[3];
        moon_position(c, t_sec, rb);
        accel_third_body(r, rb, c.mu_moon, am);
        a[0] += am[0]; a[1] += am[1]; a[2] += am[2];
    }
}

//------------------------------------------------------------------------------
// derivatives_keplerian(s[6], t, cfg, d[6]) — 状态导数（ODE 右手边）
// 公式：d(r)/dt = v；d(v)/dt = accel_total(r, v, t)
// 讲解：与 GMAT ODEModel::GetDerivativesForState 语义一致（MD-08 数据流：
//       传播器把状态交给力模型，力模型返回 6 维导数）。
//------------------------------------------------------------------------------
GMATH_DEVICE inline void derivatives_keplerian(const double s[6], double t_sec,
                                               const ForceConfig& cfg, double d[6])
{
    const double r[3] = { s[0], s[1], s[2] };
    const double v[3] = { s[3], s[4], s[5] };
    double a[3];
    accel_total(r, v, t_sec, cfg, a);
    d[0] = v[0]; d[1] = v[1]; d[2] = v[2];
    d[3] = a[0]; d[4] = a[1]; d[5] = a[2];
}

} // namespace gmath
