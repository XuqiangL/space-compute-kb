//==============================================================================
// constants.hpp — GMAT 物理/天文常量（迁移自 GMAT 源码，来源行号见注释）
//
// 全部数值取自 NASA/GMAT 仓库（L:\gmat888，commit ce6eba2）：
//   - 地球 μ、赤道半径   : src/gmatutil/util/GmatDefaults.hpp:159/186
//   - 月球 μ、赤道半径   : src/gmatutil/util/GmatDefaults.hpp:299/314
//   - EGM96 归一化 C20   : application/data/gravity/earth/EGM96.cof（RECOEF 2 0 行）
//   - 光速等             : src/gmatutil/util/GmatConstants.hpp（使用时另注）
// 单位约定与 GMAT 一致：km, s, km/s, kg, N；角度 rad（内部）。
//==============================================================================
#pragma once

namespace gmath {

// ---- 中心天体（单位 km^3/s^2、km） ------------------------------------------
inline constexpr double MU_EARTH  = 398600.4415;      // GmatDefaults.hpp:186
inline constexpr double MU_MOON   = 4902.8005821478;  // GmatDefaults.hpp:314
inline constexpr double RE_EARTH  = 6378.1363;        // GmatDefaults.hpp:159
inline constexpr double RM_MOON   = 1738.2000;        // GmatDefaults.hpp:299

// ---- 月球轨道（两体圆轨道近似，用于第三体摄动与 SOI 判据） -----------------
inline constexpr double A_MOON    = 384400.0;         // 地心平均距离 km
inline constexpr double N_MOON    = 2.6647544e-6;     // 平均角速度 rad/s = sqrt(MU_EARTH/A_MOON^3)

// ---- EGM96 低阶带谐（J2 由归一化 C20 换算） --------------------------------
// EGM96.cof: RECOEF 2 0 -4.84165371736E-04（归一化 C̄20）
// J2(未归一化) = -√5 · C̄20 = 1.0826269269e-3（与 JGM-2/EGM96 一致）
inline constexpr double EGM96_C20_BAR = -4.84165371736e-04;
inline constexpr double J2_EARTH = 1.0826269269e-3;

// ---- 推进/单位 ---------------------------------------------------------------
inline constexpr double G0       = 9.80665;           // 标准重力加速度 m/s^2（MD-10 注：GMAT 代码默认 9.81，此处取 SI 标准值并在注释中说明差异）
inline constexpr double G0_KM    = 9.80665e-3;        // km/s^2（与 km 单位制一致）

// ---- 时间（MD-01） -----------------------------------------------------------
// GMAT A.1 修正儒略日 = JD - 2430000.5；J2000.0（JD 2451545.0）→ 21544.5，
// 与 GmatDefaults.hpp 的 TWO_BODY_EPOCH = 21544.500370768266 一致。
inline constexpr double MJD_J2000 = 21544.5;          // 2000-01-01 12:00:00 TDB
inline constexpr double MJD_OFFSET_A1 = 2430000.5;    // A.1 基准偏移（JD - MJD_A1）
inline constexpr double SECS_PER_DAY = 86400.0;

} // namespace gmath
