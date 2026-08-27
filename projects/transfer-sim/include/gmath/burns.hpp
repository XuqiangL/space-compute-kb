//==============================================================================
// burns.hpp — 机动与推力模型公式（MD-10《机动与推力模型数学》）
//
// 与 GMAT 对应实现：
//   - mdot_from_isp    : src/base/hardware/ChemicalThruster.cpp（ṁ = -T·DC/(g·Isp)）
//   - mass_after_dv    : 齐奥尔科夫斯基火箭方程（ImpulsiveBurn 的燃料消耗计算）
//   - accel_finite_thrust : FiniteBurn / FiniteThrust 的 tOverM 加速度合成
//==============================================================================
#pragma once
#include <cmath>
#include "constants.hpp"

namespace gmath {

//------------------------------------------------------------------------------
// mdot_from_isp(thrust_N, Isp_s, g0_km) — 推进剂质量流率
// 公式：ṁ = -T / (Isp · g0)，g0 = 9.80665e-3 km/s²（单位一致）
// 讲解：火箭方程微分形式。MD-10 实测发现 GMAT 代码默认 gravityAccel=9.81
//       （非 9.80665），此处按 SI 标准值实现并在注释中注明差异；
//       质量流为负（消耗）。返回 kg/s，T 单位 N、Isp 单位 s。
//------------------------------------------------------------------------------
GMATH_DEVICE inline double mdot_from_isp(double thrust_N, double Isp_s, double g0_km)
{
    return -thrust_N / (Isp_s * g0_km) * 1.0e-3;   // N/(km/s²·s) -> kg/s（1 N = 1 kg·m/s²，换算 ×1e-3）
}

//------------------------------------------------------------------------------
// mass_after_dv(m0, dv, Isp_s, g0_km) — 齐奥尔科夫斯基火箭方程（脉冲机动燃料）
// 公式：m_f = m0 · exp(-Δv/(Isp·g0))；Δm = m0(1 - exp(-Δv/(Isp·g0)))
// 讲解：给定冲量 Δv 所需的推进剂质量；对应 ImpulsiveBurn 的
//       "DecrementMass" 逻辑（MD-10 §脉冲机动）。
//------------------------------------------------------------------------------
GMATH_DEVICE inline double mass_after_dv(double m0, double dv, double Isp_s, double g0_km)
{
    return m0 * std::exp(-dv / (Isp_s * g0_km));
}

//------------------------------------------------------------------------------
// accel_finite_thrust(T_N, m_kg, dir[3]) — 有限推力加速度
// 公式：a = T/m · û（û 为单位推力方向）
// 讲解：对应 FiniteBurn/FiniteThrust 的加速度合成（MD-10 §有限推力）：
//       力模型在积分步内把 T/m 叠加进导数；质量按 ṁ 同步积分。
//------------------------------------------------------------------------------
GMATH_DEVICE inline void accel_finite_thrust(double T_N, double m_kg,
                                             const double dir[3], double a[3])
{
    const double k = (T_N * 1.0e-3) / m_kg;     // N -> kN，a 单位 km/s²
    a[0] = k * dir[0]; a[1] = k * dir[1]; a[2] = k * dir[2];
}

//------------------------------------------------------------------------------
// burn_direction_from_attitude(...) 简化版：推力方向 = 速度方向单位矢
// 公式：û = v / ||v||
// 讲解：本仿真 TLI 沿速度方向点火（顺行加速最省燃料）；真实 GMAT 中
//       方向由坐标系/姿态给出，此处取其解析特例。
//------------------------------------------------------------------------------
GMATH_DEVICE inline void burn_direction_velocity(const double v[3], double dir[3])
{
    double vn = std::sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
    dir[0] = v[0]/vn; dir[1] = v[1]/vn; dir[2] = v[2]/vn;
}

} // namespace gmath
