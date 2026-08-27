//==============================================================================
// elements.hpp — 轨道要素与状态转换公式（MD-03《轨道要素与状态转换数学》）
//
// 每个函数 = 一个转换公式；与 GMAT StateConversionUtil.cpp 的实现一致
// （src/gmatutil/util/StateConversionUtil.cpp）。约定：
//   - 角度一律弧度（内部），要素顺序 [SMA, ECC, INC, RAAN, AOP, TA]
//   - 状态顺序 [x, y, z, vx, vy, vz]，单位 km / km/s
//==============================================================================
#pragma once
#include <cmath>
#include <algorithm>
#include "constants.hpp"
#include "vec_math.hpp"

namespace gmath {

inline constexpr double PI = 3.14159265358979323846;

//------------------------------------------------------------------------------
// anomaly_E_from_M(M, e) — 开普勒方程：平近点角 → 偏近点角（Newton 迭代）
// 公式：M = E - e·sin E  ⇒  E_{k+1} = E_k - (E_k - e sin E_k - M)/(1 - e cos E_k)
// 讲解：初值取 E0 = M + e sin M（椭圆）；迭代至 |ΔE|<1e-13 或 30 次。
//       代码对应：StateConversionUtil::TrueToMeanAnomaly 的反向分支（MD-03 条目）。
//------------------------------------------------------------------------------
GMATH_DEVICE inline double anomaly_E_from_M(double M, double e)
{
    double E = M + e * std::sin(M);
    for (int i = 0; i < 30; ++i) {
        double f  = E - e * std::sin(E) - M;
        double fp = 1.0 - e * std::cos(E);
        double dE = -f / fp;
        E += dE;
        if (std::abs(dE) < 1e-13) break;
    }
    return E;
}

//------------------------------------------------------------------------------
// anomaly_TA_from_E(E, e) — 偏近点角 → 真近点角
// 公式：tan(TA/2) = sqrt((1+e)/(1-e)) · tan(E/2)
// 讲解：用半角公式保证全象限正确（TA 与 E 同象限）；这是
//       StateConversionUtil 的标准实现形式。
//------------------------------------------------------------------------------
GMATH_DEVICE inline double anomaly_TA_from_E(double E, double e)
{
    return 2.0 * std::atan2(std::sqrt(1.0 + e) * std::sin(E / 2.0),
                            std::sqrt(1.0 - e) * std::cos(E / 2.0));
}

//------------------------------------------------------------------------------
// anomaly_M_from_TA(TA, e) — 真近点角 → 平近点角（两步：TA→E→M）
// 公式：tan(E/2) = sqrt((1-e)/(1+e)) · tan(TA/2)；M = E - e·sin E
//------------------------------------------------------------------------------
GMATH_DEVICE inline double anomaly_M_from_TA(double TA, double e)
{
    double E = 2.0 * std::atan2(std::sqrt(1.0 - e) * std::sin(TA / 2.0),
                                std::sqrt(1.0 + e) * std::cos(TA / 2.0));
    return E - e * std::sin(E);
}

//------------------------------------------------------------------------------
// anomaly_E_from_TA(TA, e) — 真近点角 → 偏近点角
// 公式：tan(E/2) = sqrt((1-e)/(1+e)) · tan(TA/2)
//------------------------------------------------------------------------------
GMATH_DEVICE inline double anomaly_E_from_TA(double TA, double e)
{
    return 2.0 * std::atan2(std::sqrt(1.0 - e) * std::sin(TA / 2.0),
                            std::sqrt(1.0 + e) * std::cos(TA / 2.0));
}

//------------------------------------------------------------------------------
// cartesian_from_kepler(el[6], mu) — 开普勒要素 → 笛卡尔状态（r[3], v[3]）
// 公式：
//   p = a(1-e²)，r = p/(1+e·cos TA)，h = sqrt(μp)
//   近焦点系：r_pf = (r cos TA, r sin TA, 0)
//            v_pf = (-μ/h·sin TA,  μ/h·(e+cos TA), 0)
//   旋转：R = R3(RAAN)·R1(INC)·R3(AOP)（3-1-3 序列），r_ECI = R·r_pf
// 讲解：这是 GMAT 默认坐标系 MJ2000Eq 下的标准两体状态构造；TLE 之外的
//       脚本轨道定义全部走这条链（Spacecraft 要素参数 → 状态）。
//------------------------------------------------------------------------------
GMATH_DEVICE inline void cartesian_from_kepler(const double el[6], double mu,
                                               double r[3], double v[3])
{
    const double a = el[0], e = el[1], i = el[2], Om = el[3], w = el[4], TA = el[5];
    const double p = a * (1.0 - e * e);
    const double rr = p / (1.0 + e * std::cos(TA));
    const double h = std::sqrt(mu * p);

    // 近焦点系位置/速度
    const double rpf[3] = { rr * std::cos(TA), rr * std::sin(TA), 0.0 };
    const double vpf[3] = { -mu / h * std::sin(TA),
                             mu / h * (e + std::cos(TA)), 0.0 };

    // R = R3(Om)·R1(i)·R3(w)，按列合成后逐项乘
    const double cOm = std::cos(Om), sOm = std::sin(Om);
    const double ci  = std::cos(i),  si  = std::sin(i);
    const double cw  = std::cos(w),  sw  = std::sin(w);

    // R3(w) 先作用于 pf 向量
    double t[3], u[3];
    t[0] = cw * rpf[0] - sw * rpf[1];  t[1] = sw * rpf[0] + cw * rpf[1];  t[2] = rpf[2];
    // R1(i)
    u[0] = t[0];  u[1] = ci * t[1] - si * t[2];  u[2] = si * t[1] + ci * t[2];
    // R3(Om)
    r[0] = cOm * u[0] - sOm * u[1];   r[1] = sOm * u[0] + cOm * u[1];   r[2] = u[2];

    double t2[3], u2[3];
    t2[0] = cw * vpf[0] - sw * vpf[1];  t2[1] = sw * vpf[0] + cw * vpf[1];  t2[2] = vpf[2];
    u2[0] = t2[0];  u2[1] = ci * t2[1] - si * t2[2];  u2[2] = si * t2[1] + ci * t2[2];
    v[0] = cOm * u2[0] - sOm * u2[1];   v[1] = sOm * u2[0] + cOm * u2[1];   v[2] = u2[2];
}

//------------------------------------------------------------------------------
// kepler_from_cartesian(r, v, mu) — 笛卡尔状态 → 开普勒要素
// 公式：
//   h = r×v,  n = ẑ×h,  e_vec = ((v²-μ/r)·r - (r·v)·v)/μ
//   ε = v²/2 - μ/r,  a = -μ/(2ε)
//   INC = acos(h_z/h);  RAAN = acos(n_x/n)（n_y<0 取 2π-·）
//   AOP  = acos(n·e/(n·e))（e_z<0 取 2π-·）;  TA = acos(e·r/(e·r))（r·v<0 取 2π-·）
//   奇点处理：圆轨道（e<1e-11）AOP=0、TA 由 n·r 定；赤道轨道（i<1e-11）RAAN=0、AOP 由 e_vec 定
// 讲解：与 StateConversionUtil::CartesianToKeplerian 一致（MD-03 条目）。
//------------------------------------------------------------------------------
GMATH_DEVICE inline void kepler_from_cartesian(const double r[3], const double v[3],
                                               double mu, double el[6])
{
    double h[3], n[3], ev[3];
    cross(r, v, h);
    const double hm = norm(h);
    const double rn = norm(r);
    const double v2 = dot(v, v);
    const double rdotv = dot(r, v);

    // 偏心率矢量（拉普拉斯-龙格-楞次）
    for (int k = 0; k < 3; ++k)
        ev[k] = ((v2 - mu / rn) * r[k] - rdotv * v[k]) / mu;
    const double em = norm(ev);

    // 能量与半长轴
    const double eps = v2 / 2.0 - mu / rn;
    const double a = -mu / (2.0 * eps);

    // 交点线 n = ẑ×h
    n[0] = -h[1]; n[1] = h[0]; n[2] = 0.0;
    const double nm = std::sqrt(n[0]*n[0] + n[1]*n[1]);

    double inc = std::acos(h[2] / hm);

    double raan = 0.0;
    if (nm > 1e-12)
        raan = std::atan2(n[1], n[0]);          // 等价 acos(n_x/n) + 象限修正

    double aop = 0.0, ta = 0.0;
    if (em > 1e-11) {
        const double ne = dot(n, ev);
        aop = std::acos(std::max(-1.0, std::min(1.0, ne / (nm * em))));
        if (ev[2] < 0.0) aop = 2.0 * PI - aop;
        const double er = dot(ev, r);
        ta = std::acos(std::max(-1.0, std::min(1.0, er / (em * rn))));
        if (rdotv < 0.0) ta = 2.0 * PI - ta;
    } else {
        // 圆轨道：AOP 无定义置 0，TA 由 n·r 决定
        const double nr = dot(n, r);
        ta = std::acos(std::max(-1.0, std::min(1.0, nr / (nm * rn))));
        if (r[2] < 0.0) ta = 2.0 * PI - ta;
    }

    el[0] = a; el[1] = em; el[2] = inc; el[3] = raan; el[4] = aop; el[5] = ta;
}

//------------------------------------------------------------------------------
// orbital_energy(r, v, mu) — 单位质量轨道能量（比机械能）
// 公式：ε = v²/2 - μ/r
// 讲解：ε<0 椭圆、=0 抛物线、>0 双曲线；转移轨道上 ε 应守恒（无耗散时），
//       用作积分器守恒性检验量。
//------------------------------------------------------------------------------
GMATH_DEVICE inline double orbital_energy(const double r[3], const double v[3], double mu)
{
    return dot(v, v) / 2.0 - mu / norm(r);
}

//------------------------------------------------------------------------------
// soi_radius(a_secondary, mu_primary, mu_secondary) — 摄动体影响球半径（Laplace SOI）
// 公式：r_SOI = a · (μ_secondary / μ_primary)^{2/5}
// 讲解：切换中心体的经典判据（patch-conic 拼接）；对地月：
//       r_SOI = 384400 · (4902.8006/398600.4415)^{0.4} ≈ 66,183 km
//------------------------------------------------------------------------------
GMATH_DEVICE inline double soi_radius(double a_secondary, double mu_primary, double mu_secondary)
{
    return a_secondary * std::pow(mu_secondary / mu_primary, 0.4);
}

//------------------------------------------------------------------------------
// vis_viva(r, a, mu) — 活力公式（给定半长轴的轨道速率）
// 公式：v = sqrt(μ(2/r - 1/a))
// 讲解：用于计算圆轨道入轨速度、转移椭圆某点速度（MD-03 能量关系）。
//------------------------------------------------------------------------------
GMATH_DEVICE inline double vis_viva(double r, double a, double mu)
{
    return std::sqrt(mu * (2.0 / r - 1.0 / a));
}

} // namespace gmath
