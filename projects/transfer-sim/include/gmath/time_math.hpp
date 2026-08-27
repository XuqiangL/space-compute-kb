//==============================================================================
// time_math.hpp — 时间系统换算公式（MD-01《时间系统与历元数学》对应实现）
//
// 每个函数 = 一个时间换算公式。源公式取自：
//   - src/gmatutil/util/TimeTypes.hpp（A.1/MJD 基准常量）
//   - src/gmatutil/util/DateUtil.cpp（儒略日/公历/年积日）
//   - src/gmatutil/util/TimeSystemConverter.cpp（TT-TAI 等系统差）
// 本仿真只用 MJD 作为内部历元，故只封装轨道仿真必需的最小集合。
//==============================================================================
#pragma once
#include <cmath>
#include "device.hpp"

namespace gmath {

//------------------------------------------------------------------------------
// jd_from_mjd(mjd) — GMAT A.1 修正儒略日 → 儒略日
// 公式：JD = MJD + 2430000.5
// 讲解：GMAT 内部"修正儒略日"不是标准 MJD(1858 基准)，而是 A.1 约定
//       （基准 JD 2430000.5），因此 J2000.0（JD 2451545.0）对应
//       MJD_A1 = 21544.5（与 GmatDefaults 的 TWO_BODY_EPOCH=21544.50037 一致），
//       而非标准 MJD 的 51544.5。GmatTime 的 day 字段即此 A.1 值。
//------------------------------------------------------------------------------
GMATH_DEVICE inline double jd_from_mjd(double mjd) { return mjd + 2430000.5; }

//------------------------------------------------------------------------------
// mjd_from_jd(jd) — 儒略日 → GMAT A.1 修正儒略日
// 公式：MJD = JD - 2430000.5
//------------------------------------------------------------------------------
GMATH_DEVICE inline double mjd_from_jd(double jd) { return jd - 2430000.5; }

//------------------------------------------------------------------------------
// jd_from_ymdhms(y, m, d, h, mi, s) — 公历时刻 → 儒略日（Fliegel–Van Flandern 公式）
// 公式：JD = (1461(y+4800+(m-14)/12))/4 + (367(m-2-12((m-14)/12)))/12
//          - (3((y+4900+(m-14)/12)/100))/4 + d - 32075
//          + (h-12)/24 + mi/1440 + s/86400
// 讲解：整数除法按 C++ 向零截断处理（与公式定义一致）；对应 DateUtil::JulianDate
//       的公历分支。GMAT 用它把用户输入的 UTC 日期转成 A.1 MJD（再经 TAI-UTC 修正）。
//------------------------------------------------------------------------------
GMATH_DEVICE inline double jd_from_ymdhms(int y, int m, int d,
                                          int h, int mi, double s)
{
    const int a = (m - 14) / 12;
    long jdn = (1461L * (y + 4800 + a)) / 4
             + (367L * (m - 2 - 12 * a)) / 12
             - (3L * ((y + 4900 + a) / 100)) / 4
             + d - 32075L;
    // FVF 整数部分 jdn 即"该日正午的 JD"（2000-01-01 → 2451545），
    // 加时刻偏移 (h-12)/24 得任意时刻 JD
    return static_cast<double>(jdn)
         + (h - 12) / 24.0 + mi / 1440.0 + s / 86400.0;
}

//------------------------------------------------------------------------------
// mjd_from_ymdhms(...) — 公历时刻 → GMAT A.1 MJD（两步：JD 后减 A.1 偏移）
// 公式：MJD = jd_from_ymdhms(...) - 2430000.5
//------------------------------------------------------------------------------
GMATH_DEVICE inline double mjd_from_ymdhms(int y, int m, int d,
                                           int h, int mi, double s)
{
    return jd_from_ymdhms(y, m, d, h, mi, s) - 2430000.5;
}

//------------------------------------------------------------------------------
// tai_from_tt(tt) — TT → TAI
// 公式：TAI = TT - 32.184 s
// 讲解：地球时 TT 与原子时 TAI 的固定差（IAU 1976）；GMAT 的
//       TimeSystemConverter 在 UTC/TT 互转链中使用（MD-01 §对应条目）。
//------------------------------------------------------------------------------
GMATH_DEVICE inline double tai_from_tt(double tt) { return tt - 32.184; }

//------------------------------------------------------------------------------
// tt_from_tai(tai) — TAI → TT
// 公式：TT = TAI + 32.184 s
//------------------------------------------------------------------------------
GMATH_DEVICE inline double tt_from_tai(double tai) { return tai + 32.184; }

//------------------------------------------------------------------------------
// secs_from_days / days_from_secs — 日/秒换算
// 公式：t_sec = t_day × 86400；t_day = t_sec / 86400
//------------------------------------------------------------------------------
GMATH_DEVICE inline double secs_from_days(double days) { return days * 86400.0; }
GMATH_DEVICE inline double days_from_secs(double secs) { return secs / 86400.0; }

} // namespace gmath
