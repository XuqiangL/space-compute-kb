# 第1章 时间系统与历元数学

本章范围：GMAT 时间表示与换算的全部数学。覆盖 `src/gmatutil/util/GmatTime.*`（A1 修正儒略日的高精度时间：日 + 秒 + 秒小数双表示）、`src/gmatutil/util/TimeSystemConverter.*`（A1/TAI/TT/TDB/UTC/UT1 六时间系统换算、跳秒表接入）、`src/gmatutil/util/TimeTypes.hpp`（时间类型与聚合结构）、`src/gmatutil/util/DateUtil.*`（儒略日、公历、年积日、日秒换算）、`src/gmatutil/util/GmatConstants.hpp` 的 `GmatTimeConstants` 命名空间（全部换算常量）、`src/gmatutil/util/LeapSecsFileReader.*` 与数据文件 `application/data/time/tai-utc.dat`（跳秒表），以及 `src/base/solarsys/` 中涉及星历时（TDB/TT）换算的调用链（`DeFile`、`CelestialBody`、`Planet`、`Moon`、`SlpFile`、`Msise90Atmosphere`、`EopFile`）。

> 路径勘误：任务书中提到的 `src/base/foundation/GmatTime.*` 实际位于 `src/gmatutil/util/GmatTime.*`（已用 glob 验证）；GmatTime 是 gmatutil 库的一部分，被 `GmatState`（`src/base/foundation/GmatState.hpp`）等上层引用，本仓库不存在 foundation 下的 GmatTime。本章一律使用真实路径。

> 术语约定与既有文档一致：A1（GMAT 内部原子时标，Math Spec §2.1）、TAI、TT、TDB、UTC、UT1 六个时间系统见 [第2章 §3.5.8](../CH02-foundation.md)；`GmatState` 高/低精度历元切换、`GmatTime` 概览见 [第2章 §3.5.2 与 §3.2](../CH02-foundation.md)；`CelestialBody`/大气模型在动力学中的使用见 [第6章](../CH06-dynamics.md)。本章聚焦"数学公式本身"，不重复上述章节的类职责描述。

## 一、概述：六个时间系统与两个 MJD 基准

GMAT 内部所有历元统一以 **A1 修正儒略日（A1 Modified Julian Date）** 表达，零点是 **1941 年 1 月 5 日正午**（JD 2430000.5 对应的 MJD 0；`A1Mjd.cpp:29-30` 注释明示 "The zero date of the MJD 12 noon on January 5th, 1941"）。注意这与天文学标准 MJD（零点为 1858 年 11 月 17 日，JD 2400000.5）不同——这是理解本文件全部换算的前提：

- **A1**：原子时标，`A1 - TAI = 0.0343817 s`（`GmatConstants.hpp:150`，Math Spec §2.1）。
- **TAI**：国际原子时，由跳秒表给出 `TAI - UTC`。
- **TT**（原 TDT）：`TT - TAI = 32.184 s`（`GmatConstants.hpp:149`，Math Spec §2.3）。
- **TDB**：质心动力学时，`TDB - TT` 为周期项（本章公式 8-1/8-2）。
- **UTC**：协调世界时，含整秒跳秒。
- **UT1**：世界时 1，`UT1 - UTC = ΔUT1` 由 EOP 文件提供。

两个 MJD 基准的差（`GmatConstants.hpp:151-152`）：

$$JD\_JAN\_5\_1941 - JD\_NOV\_17\_1858 = 2430000.0 - 2400000.5 = 29999.5\ \text{天}$$

所有引用 1858 基准的外部表（跳秒表、EOP 文件）在读写前都必须平移这 29999.5 天，详见 §四、§五。

## 二、常量与基础类型

### GmatTimeConstants 时间换算常量
- **公式**：
  $$86400\ \text{s/day},\quad 3600\ \text{s/h},\quad 60\ \text{s/min},\quad 36525\ \text{d/儒略世纪},\quad JD\_MJD\_OFFSET = 2400000.5$$
  $$TT\_TAI\_OFFSET = 32.184\ \text{s},\quad A1\_TAI\_OFFSET = 0.0343817\ \text{s}$$
  $$JD\_OF\_J2000 = 2451545.0,\quad MJD\_OF\_J2000 = 21545.0,\quad JD\_JAN\_5\_1941 = 2430000.0,\quad JD\_NOV\_17\_1858 = 2400000.5$$
- **代码位置**：`src/gmatutil/util/GmatConstants.hpp:134-176`（`GmatTimeConstants` 命名空间）
- **深度讲解**：
  - **天文意义**：`JD_OF_J2000 = 2451545.0` 是 J2000.0 历元（2000 年 1 月 1 日 12 时 TT）的儒略日；`MJD_OF_J2000 = 21545.0 = 2451545 - 2430000` 是同一历元相对 GMAT 1941 基准的修正儒略日；`A1MJD_OF_J2000 = 21545.0`（第 147 行）是 J2000 时刻的 A1 修正儒略日（源码注释标注其公历对应为 `2000/01/01 11:59:27.965622`，属历史标注；由常量可导出 A1 比 TT 慢 $TT{-}TAI - A1{-}TAI = 32.184 - 0.0343817 = 32.1496183$ s）。`TIME_OF_J2000 = 883655990.850`（第 144 行）是 J2000 相对某零点的秒数，与 21545×86400 = 1,861,488,000 不相等，仅作历史遗留常量。
  - `TT_TAI_OFFSET = 32.184 s` 的由来：TAI 与 TT 的差由 1976/1979 年 IAU 决议定义。TT 在 1991 年取代 TDT 时保持连续，而 TDT 被定义为 TAI + 32.184 s——32.184 s 恰好是 1958 年 1 月 1 日 TAI 建立时对历书时（ET）的估计差（ET−TAI ≈ 32.184 s），从此作为常数沿用。
  - `A1_TAI_OFFSET = 0.0343817 s` 是 GMAT 沿用的 A1 时标定义（源自 1995 年的 GSS 项目，见 `TimeTypes.hpp:25` 版权头）：A1 是 GSFC 为任务计算定义的原子时标，其与 TAI 的差为常数 0.0343817 s（Math Spec §2.1）。
  - **实现细节**：全部为编译期 `const Real`，无任何计算；`DAYS_BEFORE_MONTH`/`LEAP_YEAR_DAYS_BEFORE_MONTH`/`DAYS_IN_MONTH`/`LEAP_YEAR_DAYS_IN_MONTH` 四张逐月天数表（第 154-161 行）供 `DateUtil` 的年积日互转使用；`MJD_EPOCH_PRECISION = 7.27e-12`（第 164 行）注释为 "37 bits for decimal piece"——这是双精度在 MJD 尺度（约 2 万量级）下小数部分可保留的精度估计（7.27e-12 天 ≈ 0.628 μs），是设计 `GmatTime` 双表示的直接动机。
  - **使用场景**：被 `TimeSystemConverter`（`TimeSystemConverter.cpp:91-98` 构造初始化列表）、`GmatTime`（`GmatTime.cpp:562`、`602`）、`DateUtil`（`DateUtil.cpp:326-328`）、`DeFile`（`DeFile.cpp:104-105`）、`SlpFile`（`SlpFile.cpp:1189`）等全面引用，是全库时间的"唯一事实来源"。

### TimeTypes.hpp 时间类型与聚合结构
- **公式**：（无换算公式，纯类型声明）
- **代码位置**：`src/gmatutil/util/TimeTypes.hpp:38-88`
- **深度讲解**：
  - typedef 别名（第 38-46 行）：`UtcMjd = Real`、`Ut1Mjd = Real`、`YearNumber = Integer`、`DayOfYear`/`MonthOfYear`/`DayOfMonth`/`HourOfDay`/`MinuteOfHour` 均为整数——语义别名，编译器层面与底层类型相同，作用是在接口签名中表达"这个 Real 是 UTC 修正儒略日"。
  - `GmatTimeUtil::CalDate`（第 50-66 行）：年/月/日/时/分/秒聚合，**默认值是 1941/1/5 00:00:00**（第 58 行），与 A1Mjd 的 1941 基准呼应。
  - `GmatTimeUtil::ElapsedDate`（第 68-81 行）：日/时/分/秒的时长聚合，用于时间区间表示。
  - 月名工具 `IsValidMonthName`/`GetMonthName`/`GetMonth`（第 83-85 行）与 `FormatCurrentTime`（第 86 行）供公历字符串解析/输出使用（`DateUtil::IsValidGregorian` 调用 `IsValidMonthName`/`GetMonth`，`DateUtil.cpp:136-139`）。
  - **使用场景**：`CalDate` 被 GUI 的时间编辑控件与脚本解析使用；`UtcMjd`/`Ut1Mjd` 出现在 `LeapSecsFileReader`、`EopFile` 的接口中。

## 三、GmatTime 高精度时间（日 + 秒 + 秒小数）

### GmatTime 三部分存储结构
- **公式**：
  $$\mathrm{GmatTime} \equiv (Days,\ Sec,\ FracSec),\qquad Sec\in[0,86400),\ FracSec\in[0,1)$$
- **代码位置**：`src/gmatutil/util/GmatTime.hpp:97-101`；默认构造 `src/gmatutil/util/GmatTime.cpp:46-51`
- **深度讲解**：
  - **数学动机（精度处理）**：双精度约 15~16 位有效数字。MJD 数值量级约 2×10⁴，若整体存一个 double，MJD 的小数部分最多保留约 16−5 = 11 位十进制（对应约 37 位二进制，即 `MJD_EPOCH_PRECISION = 7.27e-12` 天 ≈ 0.628 μs）。而航天任务的亚微秒精度要求（μs 级）需要约 1e-11 天分辨率，已逼近 double 极限。GMAT 的解法是把时间拆成 `long Days`（整数天）+ `long Sec`（当日秒，整数）+ `Real FracSec`（秒小数）三部分，使小数部分脱离大数基数，保留完整双精度。
  - 默认构造把 `Days` 置为 21545（= `MJD_OF_J2000`）、`Sec=0`、`FracSec=0`，即默认时刻为 J2000（`GmatTime.cpp:47`）。
  - **使用场景**：`GmatState::theEpochGT`（高精度历元，`GmatState.hpp:86-102`）、`Spacecraft`/`CelestialBody` 的 `stateTimeGT`（`CelestialBody.cpp:243`）、`DeFile` 的 GmatTime 版插值入口（`DeFile.cpp:530`）等。

### GmatTime(Real mjd) 构造函数：double→三部分拆分
- **公式**（归一化后）：
  $$Days = \lfloor |mjd| \rfloor,\quad Sec = \lfloor (|mjd|-Days)\cdot 86400 \rfloor,\quad FracSec = (|mjd|-Days)\cdot 86400 - Sec$$
  再经两级进位/借位使 $Sec\in[0,86400)$、$FracSec\in[0,1)$。
- **代码位置**：`src/gmatutil/util/GmatTime.cpp:76-146`
- **深度讲解**：
  - **实现细节**：
    ```cpp
    // GmatTime.cpp:88-97  先按绝对值拆，最后统一加符号
    Days = (long)time;                 // 整数天（截断）
    Real dayFrac = time - Days;        // 天的小数部分
    Sec = (long)(dayFrac*86400);       // 当日整秒
    FracSec = dayFrac*86400 - Sec;     // 秒的小数部分（[0,1)）
    if (sign == -1) { Days = -Days; Sec = -Sec; FracSec = -FracSec; }
    ```
    第 78-85 行先取绝对值处理，避免 C/C++ 对负数的截断语义歧义；第 92-97 行把符号加回三部分。
    ```cpp
    // GmatTime.cpp:113-144  两级归一化：先规整 FracSec 到 [0,1)，再规整 Sec 到 [0,86400)
    long d1 = (long)(((FracSec < 0.0)? -FracSec: FracSec) / 86400);
    if (FracSec >= 0.0) {
       if (d1 != 0) { FracSec -= d1; Sec += d1; }        // 秒小数每 86400 秒进 1 天
    } else {
       FracSec += (d1 + 1); Sec -= (d1 + 1);             // 负数借位
    }
    long d = (long)(((Sec < 0)?-Sec:Sec) / 86400);
    if (Sec >= 0) {
       if (d != 0) { Sec -= (d * 86400); Days += d; }    // 秒每满 86400 进 1 天
    } else {
       Sec += ((d + 1) * 86400); Days -= (d + 1);        // 负数向 Days 借位
    }
    ```
    第一级把 `FracSec` 规整到 [0,1)：注释掉的代码（第 101-110 行）只处理 ±1 的边界，而实际实现（第 113-126 行）用 `d1 = ⌊|FracSec|/86400⌋` 处理"秒小数本身超过一天"的极端输入（输入 double 的尾数误差可能放大）；第二级（第 130-144 行）把 `Sec` 规整到 [0,86400)。负数走"补一借位"分支保证 `FracSec` 非负、`Sec` 非负的最终不变量。
  - **精度处理**：整个拆分只用截断和减法，不引入除法的尾数噪声；`FracSec` 的精度在 86400 倍缩放后仍然完整保留，这是与"直接存 double MJD"的本质区别。
  - **使用场景**：凡是从 double 历元构造高精度时间的地方（`GmatState::SetPrecisionTimeFlag` 的同步、`GmatTime operator=(Real)`（`GmatTime.cpp:168-176`）、`GmatTime(1721013.5)` 等字面量构造）。

### GmatTime::GetMjd / GetTimeInSec：合并输出
- **公式**：
  $$\mathrm{MJD} = Days + \frac{Sec + FracSec}{86400},\qquad t_{sec} = Days\cdot 86400 + Sec + FracSec$$
- **代码位置**：`src/gmatutil/util/GmatTime.cpp:560-563`（GetMjd）、`GmatTime.cpp:600-603`（GetTimeInSec）
- **深度讲解**：
  - **实现细节**：
    ```cpp
    Real GmatTime::GetMjd() const
    {
       return (Days + (Sec+FracSec)/GmatTimeConstants::SECS_PER_DAY);
    }
    Real GmatTime::GetTimeInSec() const
    {
       return (Days*GmatTimeConstants::SECS_PER_DAY + Sec + FracSec);
    }
    ```
  - 两个方向：`GetMjd` 把三部分压回 double MJD（供 `TimeSystemConverter` 的 Real 接口、`LeapSecsFileReader` 查表等使用），此时精度回到 double 上限，但"输入时的高精度"已通过 `Sec`/`FracSec` 的分立保存而保留在对象内部；`GetTimeInSec` 用于需要绝对秒数的场景（比较运算 `operator<`/`operator>` 用差值秒数，`GmatTime.cpp:456-461`、`469-474`）。
  - **使用场景**：`TimeSystemConverter` 的 GmatTime 版 `ConvertToTaiMjd` 在调跳秒表时用 `.GetMjd()` 传入（`TimeSystemConverter.cpp:461`、`809`）；`DeFile::GetPosVel` GmatTime 版用 `GetMjd()` 输出调试信息（`DeFile.cpp:541`）。

### GmatTime::SetTimeInSec：秒数→三部分
- **公式**：
  $$Days = \lfloor |sec|/86400 \rfloor,\quad s = |sec| - Days\cdot 86400,\quad fs = s - \lfloor s \rfloor$$
- **代码位置**：`src/gmatutil/util/GmatTime.cpp:566-597`
- **深度讲解**：
  - **实现细节**：
    ```cpp
    // GmatTime.cpp:578-595
    long numdays = (long)(iVal / 86400);   // 整数天
    Real seconds = iVal - numdays*86400;   // 剩余秒
    long s       = (long)seconds;          // 整秒
    Real fs      = seconds - s;            // 秒小数
    if (sign == 1) { Days = numdays; Sec = s; FracSec = fs; }
    else { FracSec = -fs; Sec = -s; Days = -numdays; }  // 负数三部分同时取负
    ```
    与 `GmatTime(Real mjd)` 拆分的区别：此处输入是"绝对秒数"（量级可达 10⁶~10⁹ s），因此先除以 86400 得整天数；负输入不做归一化（`Sec`/`FracSec` 可为负），因为后续 `AddSeconds`/`SubtractSeconds`（`GmatTime.cpp:725-740`）会把结果交给 `operator+`/`operator-` 完成归一化。
  - **使用场景**：`AddSeconds`/`SubtractSeconds` 的实现基础（`GmatTime.cpp:727-728`、`736-737`）；`TimeSystemConverter::ConvertFromTaiMjd` GmatTime 版给 TT 结果加 32.184 s 时直接调 `AddSeconds`（`TimeSystemConverter.cpp:906-908`）。

### GmatTime 算术：operator+ / operator- / operator* / operator/
- **公式**（以 + 为例，逐分量相加后归一化）：
  $$(D_1,S_1,F_1)+(D_2,S_2,F_2) = \big(D_1{+}D_2+\lfloor(S_1{+}S_2+\lfloor F_1{+}F_2\rfloor)/86400\rfloor,\ (S_1{+}S_2+\lfloor F_1{+}F_2\rfloor)\bmod 86400,\ (F_1{+}F_2)\bmod 1\big)$$
- **代码位置**：`GmatTime.cpp:182-222`（+）、`GmatTime.cpp:262-318`（−）、`GmatTime.cpp:359-366`（×）、`GmatTime.cpp:372-425`（÷）
- **深度讲解**：
  - **实现细节**（operator+ 的归一化核心）：
    ```cpp
    // GmatTime.cpp:187-219
    gt1.FracSec += gt.FracSec;   // 逐分量相加
    gt1.Sec     += gt.Sec;
    gt1.Days    += gt.Days;
    if (gt1.FracSec >= 1.0)      { gt1.FracSec -= 1.0; ++gt1.Sec; }   // 秒小数进位
    else if (gt1.FracSec < 0.0)  { gt1.FracSec += 1.0; --gt1.Sec; }   // 借位
    long d = (long)(((gt1.Sec < 0) ? -gt1.Sec : gt1.Sec) / 86400);
    if (gt1.Sec >= 0) {
       if (d != 0) { gt1.Sec -= (d * 86400); gt1.Days += d; }         // 秒进位到天
    } else {
       gt1.Sec += ((d + 1) * 86400); gt1.Days -= (d + 1);             // 负数借天
    }
    ```
    与构造函数的归一化模式完全一致，保证任何算术结果都回到 `Sec∈[0,86400)`、`FracSec∈[0,1)` 的规范形。`operator-`（第 262-318 行）先逐分量相减再做同样的两级规整。
  - **operator\***（第 359-366 行）：`GmatTime result(Days*num); result.AddSeconds(Sec*num); result.AddSeconds(FracSec*num);`——把整数天、整秒、秒小数分别乘标量再逐级累加，避免"整体转 double 再乘"的精度损失。
  - **operator/**（第 372-425 行）：先除整数天，把余数折算成秒再除，最后归一化——同样的精度保护思路。
  - **使用场景**：`TimeSystemConverter` 的全部换算都建立在 `operator+`/`operator-` 上（如 `origValue - tttOffset`、`taiEpoch - utcEpoch`）；`GetJulianDaysFromTDBEpoch` 的 `mjdTDB + JD_JAN_5_1941 - JD_OF_J2000`（`CelestialBody.cpp:6254-6255`）。

### GmatTime::ToString：高精度输出（1e-7 天粒度拆分）
- **公式**（将一天的小数部分按 10⁻⁷ 天 = 0.00864 s 的粒度拆成两段，分别格式化后拼接）：
  $$MJD = Days + \underbrace{\lfloor t_{day}\cdot 10^{7}\rfloor/10^{7}}_{\text{前 7 位小数}} + \underbrace{\{FracSec\}}_{\text{余下位数}},\qquad t_{day}=(Sec+FracSec)/86400$$
- **代码位置**：`src/gmatutil/util/GmatTime.cpp:607-659`
- **深度讲解**：
  - **精度处理的动机**：直接 `sprintf("%.15lf", GetMjd())` 会把 `Days`（2×10⁴ 量级）与秒小数压在同一 double 里，第 8 位小数以后全是噪声。`ToString` 用 `DAY_FRAC = 86400/1e7`（= 0.00864 s）把当日秒拆成"10⁻⁷ 天的整数倍部分"（firstValue）与"余数"（secondValue），前者用 `"%.7lf"` 输出 7 位小数，后者用 `"%.22lf"` 输出第 8 位起的小数，最后拼接成 `"Days.s1s2"` 字符串。
  - **实现细节**：
    ```cpp
    // GmatTime.cpp:616-642
    const Real DAY_FRAC = GmatTimeConstants::SECS_PER_DAY / 1.0e7;   // 0.00864 s
    Real remainderSec     = GmatMathUtil::Mod(Sec, DAY_FRAC);
    Real remainderFracSec = GmatMathUtil::Mod(FracSec, DAY_FRAC);
    remainderSec = GmatMathUtil::Round(GmatMathUtil::Mod(remainderSec, 1.0)*1e5)/1e5;
    Real remainder = remainderSec + remainderFracSec;                 // 去除浮点噪声
    if (remainder >= DAY_FRAC) remainder -= DAY_FRAC;
    Real firstValue = timeInSecs - remainder;                         // 1e-7 天整数倍部分
    Real firstValueFrac = GmatMathUtil::Round(GmatMathUtil::Mod(firstValue, 1.0)*1e5)/1e5;
    Real secondValue = FracSec - firstValueFrac;                      // 余下的小数秒
    if (FracSec < firstValueFrac) secondValue = FracSec + (1 - firstValueFrac);
    sprintf(epochbuffer, "%.7lf", firstValue / GmatTimeConstants::SECS_PER_DAY);  // 前 7 位
    std::string s1(&epochbuffer[index + 1]);
    sprintf(epochbuffer, "%.22lf", secondValue / GmatTimeConstants::SECS_PER_DAY); // 第 8 位起
    std::string s2(&epochbuffer[index + 8]);
    ```
    第 623 行的 `Round(Mod(remainderSec,1.0)*1e5)/1e5` 把秒的模运算尾数噪声修到 1e-5 s 量级；第 632 行对 firstValue 的小数做同样处理；第 638-639 行处理 `FracSec` 跨整秒的借位情形。
  - **使用场景**：`TimeSystemConverter` 的调试输出（`TimeSystemConverter.cpp:219`、`227`、`239`）；`DeFile` 调试信息；任何需要保留亚微秒精度的 MJD 文本输出（如 `SetMjdString` 的逆过程）。

### GmatTime::SetMjdString：字符串→三部分
- **公式**（把 MJD 字符串的小数部分按 9 位分割解析）：
  $$\text{fracDay} = 0.d_1d_2\cdots d_9\underbrace{d_{10}\cdots}_{\text{第二部分}},\qquad sec = \text{floor}(0.d_1\cdots d_9\cdot 86400),\qquad fs = \{0.d_1\cdots d_9\cdot 86400\} + 0.d_{10}\cdots\cdot 86400$$
- **代码位置**：`src/gmatutil/util/GmatTime.cpp:662-709`
- **深度讲解**：
  - **实现细节**：
    ```cpp
    // GmatTime.cpp:673-706
    sMjd = sMjd + "000000000";                       // 补 9 个尾零，防止 substr 越界
    std::string dayStr = sMjd.substr(0, pos);
    std::string fracDayStr = "0" + sMjd.substr(pos); // 小数部分补前导 0
    std::string secPart1Str = fracDayStr.substr(0, 9);          // 前 8 位小数（天）
    std::string secPart2Str = "0.0000000" + fracDayStr.substr(9); // 第 9 位起（秒）
    Days = (long)(atoi(dayStr.c_str()));
    Real secPart1 = atof(secPart1Str.c_str()) * GmatTimeConstants::SECS_PER_DAY;
    Real secPart2 = atof(secPart2Str.c_str()) * GmatTimeConstants::SECS_PER_DAY;
    Sec = GmatMathUtil::Floor(secPart1);             // 整秒
    FracSec = GmatMathUtil::Mod(secPart1, 1);        // 秒小数
    FracSec = GmatMathUtil::Round(FracSec*1e5)/1e5;  // 修尾数噪声
    if ((FracSec + secPart2) >= 1) { FracSec = (FracSec - 1) + secPart2; Sec++; }
    else { FracSec = FracSec + secPart2; }
    if (Sec > GmatTimeConstants::SECS_PER_DAY) { Sec -= GmatTimeConstants::SECS_PER_DAY; Days++; }
    ```
    关键技巧：把小数部分拆成"前 8 位小数（对应约 0.864 s 粒度）"与"第 9 位以后"两段分别乘以 86400，避免 `atof` 一次解析 15 位以上小数时 double 截断丢位。`secPart1Str` 取 `substr(0,9)` 含前导 0 共 9 字符（`0.d1..d8`），`secPart2Str` 用 `"0.0000000"` 前缀把第 9 位及以后重定位到秒级小数。
  - **使用场景**：`TimeSystemConverter::Convert` GmatTime 字符串版在 `fromFormat == "ModJulian"` 且输入为字符串时调用（`TimeSystemConverter.cpp:1546`）；脚本 `SetEpoch` 解析、`TimeData` 参数等经 `Convert` 进入。

### GmatTime::IsNearlyEqual / AddSeconds / SubtractSeconds
- **公式**：$\text{equal} \iff |\Delta t_{sec}| < tolerance$，其中 $\Delta t_{sec} = ((this)-(gt))_{sec}$（`operator-` 归一化后取 `GetTimeInSec` 的绝对值）；$this \mathrel{+}= sec$（秒数累加）。
- **代码位置**：`GmatTime.cpp:712-722`（IsNearlyEqual）、`GmatTime.cpp:725-731`（AddSeconds）、`GmatTime.cpp:734-740`（SubtractSeconds）
- **深度讲解**：
  ```cpp
  bool GmatTime::IsNearlyEqual(const GmatTime &gt, Real tolerance)
  {
     Real time = ((*this) - gt).GetTimeInSec();   // 差值的绝对秒数
     if (time < 0.0) time = -time;
     if (time < tolerance) retVal = true;
     return retVal;
  }
  const GmatTime& GmatTime::AddSeconds(const Real sec)
  {
     GmatTime gt; gt.SetTimeInSec(sec);           // 秒数先转三部分
     (*this) = ((*this) + gt);                    // 再走 operator+ 归一化
     return *this;
  }
  ```
  `IsNearlyEqual` 借助 `operator-`（自动归一化）后取 `GetTimeInSec` 绝对值，避免直接对 MJD 做差时的量级损失；`AddSeconds`/`SubtractSeconds` 先 `SetTimeInSec` 构造临时 GmatTime 再加法，确保任意秒数（含小数秒）都走完整归一化。使用场景：`ConvertFromTaiMjd` TT 分支加 32.184 s（`TimeSystemConverter.cpp:906-908`）、UT1 分支加 ΔUT1（`TimeSystemConverter.cpp:874`）、`ModifiedJulianDateGT` 加时分秒（`DateUtil.cpp:326-328`）。

## 四、TimeSystemConverter：六时间系统换算核心

### 单例、换算常量与时间系统枚举
- **公式**：$TDB\_COEFF1 = 0.001658\,\text{s},\ TDB\_COEFF2 = 0.00001385\,\text{s},\ M\_E\_OFFSET = 357.5277233°,\ M\_E\_COEFF1 = 35999.05034°/儒略世纪,\ T\_TT\_OFFSET = JD\_OF\_J2000,\ T\_TT\_COEFF1 = 36525,\ L\_B = 1.550505\times10^{-8},\ NUM\_SECS = 86400$
- **代码位置**：`src/gmatutil/util/TimeSystemConverter.cpp:81-103`（Instance 与构造）；`TimeSystemConverter.hpp:91-98`（常量声明）；`TimeSystemConverter.hpp:100-115`（`TimeSystemTypes` 枚举：A1MJD=0 … TT=11）
- **深度讲解**：
  - 单例 `Instance()`（`TimeSystemConverter.cpp:81-87`）惰性创建；`SpacePoint` 构造即取得（`SpacePoint.cpp:203`），`CelestialBody`/`PlanetaryEphem`/`AtmosphereModel` 均持指针。
  - TDB 公式系数（`TimeSystemConverter.cpp:91-98`）来自 GMAT Math Spec §2.3，即 1984 年天文年历的 TDB−TT 周期项（见公式 8-1）。`L_B = 1.550505e-8` 是 TDB−TCB 的线性漂移系数（IAU 2006 定义），当前代码中未被 Convert 使用，仅作常量保留。
  - 枚举把"时间系统+格式"扁平化为 12 个 ID：`A1MJD/TAIMJD/UTCMJD/UT1MJD/TDBMJD/TTMJD`（MJD 数字格式）与 `A1/TAI/UTC/UT1/TDB/TT`（可配 Gregorian 字符串格式）。`TIME_SYSTEM_TEXT` 映射表在 `TimeSystemConverter.cpp:61-75`；`GetTimeTypeID`（`TimeSystemConverter.cpp:125-134`）做字符串→ID 线性查找。
  - **使用场景**：全部时间换算的入口，被 `SpacePoint`/`CelestialBody`/`DeFile`/`SlpFile`/`Msise90`/`Spacecraft`/`GmatCommand`/`TimeData` 等调用。

### TimeSystemConverter::Convert（Real 版）：两段式换算总管
- **公式**：$t_{TAI} = \mathrm{ConvertToTaiMjd}(from, t_0);\quad t_{out} = \mathrm{ConvertFromTaiMjd}(to, t_{TAI})$
- **代码位置**：`src/gmatutil/util/TimeSystemConverter.cpp:153-200`
- **深度讲解**：
  ```cpp
  Real newTime = ConvertToTaiMjd(fromType, origValue, refJd);   // 先归一到 TAI
  if (insideLeapSec) *insideLeapSec = IsInLeapSecond(newTime);  // 顺带检测是否在闰秒内
  Real returnTime = ConvertFromTaiMjd(toType, newTime, refJd);  // 再从 TAI 转目标
  ```
  **设计模式**：所有换算都以 TAI 为"中间锚点"，12 个系统只需 6 条"进 TAI" + 6 条"出 TAI"路径，而非 12×11 条两两换算——这是整个时间系统的核心结构。`refJd` 默认 `JD_JAN_5_1941`（`TimeSystemConverter.hpp:124`），用于把 GMAT 的 1941 基准 MJD 平移到外部表的 1858 基准。`insideLeapSec` 输出参数供上层在输出 UTC 公历时决定是否显示 23:59:60。
  - **使用场景**：所有以 enum 为参数的高层换算（如 `DeFile::GetPosVel` 的 A1→TDB/TT，`DeFile.cpp:368-385`；`Msise90Atmosphere` 的 A1→UTC，`Msise90Atmosphere.cpp:176-177`）。

### TimeSystemConverter::Convert（GmatTime 版）
- **公式**：同 Real 版，但全程使用 GmatTime 三部分运算。
- **代码位置**：`src/gmatutil/util/TimeSystemConverter.cpp:203-244`
- **深度讲解**：与 Real 版结构完全一致（`ConvertToTaiMjd` → `ConvertFromTaiMjd`），只是把 `Real` 换成 `GmatTime`，从而在整个换算链上保持亚微秒精度。闰秒检测传 `insideLeapSec` 给两端函数（`TimeSystemConverter.cpp:224`、`231`）。**使用场景**：`DeFile::GetPosVel` GmatTime 版（`DeFile.cpp:533-550`）、`CelestialBody` 高精度状态计算（`CelestialBody.cpp:4074-4077`）等。

### ConvertToTaiMjd（Real 版）：各系统→TAI
- **代码位置**：`src/gmatutil/util/TimeSystemConverter.cpp:263-410`；GmatTime 版 `TimeSystemConverter.cpp:412-563`
- **深度讲解**：switch 按 `fromType` 分发，各分支公式见下列子条目；末尾统一 `if (insideLeapSec) *insideLeapSec = IsInLeapSecond(retTime);`（第 406-407 行）。GmatTime 版（第 412-563 行）分支结构与 Real 版一一对应，仅把常量偏移换算改为 GmatTime 运算。

#### 公式 4-1：A1 → TAI
- **公式**：$$\mathrm{TAI_{MJD}} = \mathrm{A1_{MJD}} - \frac{A1\_TAI\_OFFSET}{86400} = \mathrm{A1_{MJD}} - 3.9791377\times10^{-7}$$
- **代码位置**：`TimeSystemConverter.cpp:282-286`（Real）、`TimeSystemConverter.cpp:431-435`（GmatTime）
- **深度讲解**：`A1_TAI_OFFSET = 0.0343817 s` 换算成天再减（`GmatTimeConstants::A1_TAI_OFFSET/GmatTimeConstants::SECS_PER_DAY`）。GmatTime 版 `(origValue - (A1_TAI_OFFSET / SECS_PER_DAY))` 先构造 double 偏移再走 `operator-`（`TimeSystemConverter.cpp:433-434`）。A1 是 GMAT 内部统一时标，几乎所有任务历元都先以 A1 表达，因此这是最常用的一条路径。

#### 公式 4-2：TT → TAI
- **公式**：$$\mathrm{TAI_{MJD}} = \mathrm{TT_{MJD}} - \frac{32.184}{86400} = \mathrm{TT_{MJD}} - 3.725\times10^{-4}$$
- **代码位置**：`TimeSystemConverter.cpp:397-401`（Real）、`TimeSystemConverter.cpp:550-554`（GmatTime）
- **深度讲解**：`TT_TAI_OFFSET = 32.184 s`（`GmatConstants.hpp:149`）换算成天。GmatTime 版同样用常量除法构造偏移（`TimeSystemConverter.cpp:552-553`）。32.184 s 的历史见 §二 GmatTimeConstants 条目。

#### 公式 4-3：UTC → TAI
- **公式**：$$\mathrm{TAI_{MJD}} = \mathrm{UTC_{MJD}} + \frac{N_{LS}(\, \mathrm{UTC_{MJD}} + \Delta_{ref}\,)}{86400},\qquad \Delta_{ref} = refJd - JD\_NOV\_17\_1858 = refJd - 2400000.5$$
- **代码位置**：`TimeSystemConverter.cpp:291-323`（Real）、`TimeSystemConverter.cpp:440-475`（GmatTime）
- **深度讲解**：
  ```cpp
  // TimeSystemConverter.cpp:294-322
  Real offsetValue = 0;
  if (refJd != GmatTimeConstants::JD_NOV_17_1858)
     offsetValue = refJd - GmatTimeConstants::JD_NOV_17_1858;  // 1941基准→1858基准平移
  if (theLeapSecsFileReader == NULL)
     throw TimeFileException("theLeapSecsFileReader is unknown\n");
  Real numLeapSecs =
     theLeapSecsFileReader->NumberOfLeapSecondsFrom(origValue + offsetValue); // 查跳秒表
  retTime = (origValue + (numLeapSecs/GmatTimeConstants::SECS_PER_DAY));      // 加秒
  ```
  默认 `refJd = JD_JAN_5_1941` 时 $\Delta_{ref}=29999.5$ 天。`NumberOfLeapSecondsFrom`（LeapSecsFileReader 版，§五）内部再把 `utcMjd + 2400000.5` 变回 JD 查表，因此净效果是"GMAT 1941 基准 MJD → 1858 基准 JD → 表查询"。
  - **使用场景**：任何 UTC 输入（脚本 `UtcGregorian`/`UtcModJulian` 历元）进入内部 A1 体系的必经之路；`SlpFile::a1_utc_offset` 用它求 A1−UTC（`SlpFile.cpp:1203-1206`）。

#### 公式 4-4：UT1 → TAI（不动点迭代）
- **公式**：$$\mathrm{TAI}^{(n+1)} = \mathrm{UT1} - \Delta\mathrm{UT1}\big(\mathrm{TAI}^{(n)}\big) + \big(\mathrm{TAI}^{(n)}-\mathrm{UTC}^{(n)}\big),\qquad \mathrm{UTC}^{(n)} = \mathrm{TAI}^{(n)} - \frac{N_{LS}}{86400}$$
- **代码位置**：`TimeSystemConverter.cpp:325-356`（Real）、`TimeSystemConverter.cpp:476-509`（GmatTime）
- **深度讲解**：
  ```cpp
  // TimeSystemConverter.cpp:338-354
  taiEpoch = origValue;
  do {
     taiEpochOld = taiEpoch;
     utcEpoch = ConvertFromTaiMjd(UTCMJD, taiEpoch, refJd);        // TAI→UTC（含跳秒）
     taiMinusUtc = taiEpoch - utcEpoch;                            // 当前 TAI−UTC
     ut1MinusUtc = theEopFile->GetUt1UtcOffset(taiEpoch);          // 查 EOP：ΔUT1（秒）
     taiEpoch = origValue - ut1MinusUtc + taiMinusUtc;             // UT1 − ΔUT1 + (TAI−UTC)
  } while (abs(taiEpoch - taiEpochOld) < 1.0e-9);
  ```
  数学上：$\mathrm{TAI} = \mathrm{UT1} - (\mathrm{UT1{-}UTC}) + (\mathrm{TAI{-}UTC})$，其中 $\mathrm{UT1{-}UTC}=\Delta\mathrm{UT1}$ 依赖 TAI 本身（EOP 表按 TAI 时间戳插值），故需不动点迭代。**注意**：循环条件为 `abs(差值) < 1.0e-9`——差值小于 1e-9 天（86.4 μs）时继续迭代，实际首次修正量约 ΔUT1 量级（毫秒）即满足退出条件，因此实践中等价于"单次修正"；GmatTime 版条件 `abs((taiEpoch - taiEpochOld).GetMjd()) < 1.0e-9`（第 505 行）同样如此。这是代码中沿袭的历史写法，读者应了解其行为而非假定收敛循环。

#### 公式 4-5：TDB → TAI
- **公式**（先 TDB→TT 再 TT→TAI）：
  $$T = \frac{t_{MJD} - (JD\_OF\_J2000 - refJd)}{36525}\quad(\text{儒略世纪数，相对 J2000})$$
  $$M_E = \big(357.5277233 + 35999.05034\,T\big)\cdot\frac{\pi}{180}\quad(\text{地球平近点角，rad})$$
  $$\delta_{TDB} = \frac{0.001658\sin M_E + 0.00001385\sin 2M_E}{86400}\quad(\text{天})$$
  $$\mathrm{TT_{MJD}} = t_{MJD} - \delta_{TDB},\qquad \mathrm{TAI_{MJD}} = \mathrm{TT_{MJD}} - \frac{32.184}{86400}$$
- **代码位置**：`TimeSystemConverter.cpp:357-396`（Real）、`TimeSystemConverter.cpp:510-549`（GmatTime）
- **深度讲解**：
  ```cpp
  // TimeSystemConverter.cpp:360-374
  Real tttOffset = T_TT_OFFSET - refJd;                 // = 2451545 − 2430000 = 21545（天）
  Real t_TT = (origValue - tttOffset) / T_TT_COEFF1;    // 自 J2000 起的儒略世纪数
  Real m_E = (M_E_OFFSET + (M_E_COEFF1 * t_TT)) * GmatMathConstants::RAD_PER_DEG;
  Real offset = ((TDB_COEFF1 * Sin(m_E)) + (TDB_COEFF2 * Sin(2 * m_E))) /
        GmatTimeConstants::SECS_PER_DAY;                // 周期项（天）
  Real ttJd = origValue - offset;                       // TDB − δ = TT
  Real taiJd = ConvertToTaiMjd(TTMJD, ttJd, 0.0);       // 复用公式 4-2
  ```
  - **天文意义**：TDB 是太阳系质心坐标系中的时间坐标，因广义相对论引力势与地球运动，TDB 与地心坐标时 TT 之间存在周期性差异，主项振幅 1.658 ms、频率为地球轨道运动（一年一次），次项 13.85 μs 为倍频项。$M_E$ 是地球（太阳）的平近点角，标准历表公式（Astronomical Almanac）为 $M = 357.5277233° + 35999.05034°\,T$，其中 $T$ 为 J2000 起的儒略世纪数。
  - **实现细节**：`tttOffset = T_TT_OFFSET - refJd` 先做减法避免"大数相减"精度损失（MJD 量级 2×10⁴，减完剩 21545 量级再除以 36525 得世纪数）；注释（第 363-364 行）明示第一项严格说应以 TT 而非 TDB 求 $T$，因二者差仅毫秒量级、对 $M_E$ 影响可忽略，故直接使用输入值。GmatTime 版（第 514-527 行）用 `GmatTime tttOffset = T_TT_OFFSET - refJd` 和 `(origValue - tttOffset).GetMjd()` 保持全程高精度。
  - **使用场景**：DE 星历读取（`DeFile::GetPosVel`，`DeFile.cpp:383-387`）、`CelestialBody::GetJulianDaysFromTDBEpoch`（`CelestialBody.cpp:6247-6250`）——JPL DE 星历的自变量是 TDB 儒略日，因此查星历前必须把 A1 历元转成 TDB。

### ConvertFromTaiMjd（Real 版）：TAI→各系统
- **代码位置**：`src/gmatutil/util/TimeSystemConverter.cpp:582-741`；GmatTime 版 `TimeSystemConverter.cpp:744-915`
- **深度讲解**：switch 按 `toType` 分发；末尾 `return 0;`（第 740 行）兜底非法 ID。GmatTime 版结构相同。

#### 公式 4-6：TAI → A1
- **公式**：$$\mathrm{A1_{MJD}} = \mathrm{TAI_{MJD}} + \frac{0.0343817}{86400}$$
- **代码位置**：`TimeSystemConverter.cpp:604-612`（Real）、`TimeSystemConverter.cpp:764-772`（GmatTime）
- **深度讲解**：公式 4-1 的逆。所有内部历元本来就是 A1，此路径用于把 TAI 结果（如跳秒表给出的 TAI 时刻）还原为 A1 表达。

#### 公式 4-7：TAI → UTC（双次查表消闰秒歧义）
- **公式**：$$N_1 = N_{LS}(\mathrm{TAI}+\Delta_{ref}),\quad N_2 = N_{LS}\big(\mathrm{TAI}+\Delta_{ref}-\tfrac{N_1}{86400}\big)$$
  $$\mathrm{UTC_{MJD}} = \mathrm{TAI_{MJD}} - \frac{\min(N_1,N_2)\ \text{对应的跳秒}}{86400}\ \left(\text{实现上 } N_1=N_2 \text{ 用 } N_1,\ \text{否则用 } N_2\right)$$
- **代码位置**：`TimeSystemConverter.cpp:622-666`（Real）、`TimeSystemConverter.cpp:782-832`（GmatTime）
- **深度讲解**：
  ```cpp
  // TimeSystemConverter.cpp:646-665
  Real taiLeapSecs = theLeapSecsFileReader->NumberOfLeapSecondsFrom(origValue + offsetValue);
  Real utcLeapSecs = theLeapSecsFileReader->
     NumberOfLeapSecondsFrom((origValue + offsetValue)
                             - (taiLeapSecs/GmatTimeConstants::SECS_PER_DAY));
  if (utcLeapSecs == taiLeapSecs)
     return (origValue - (taiLeapSecs/GmatTimeConstants::SECS_PER_DAY));
  else
     return (origValue - (utcLeapSecs/GmatTimeConstants::SECS_PER_DAY));
  ```
  **为什么查两次**：跳秒表按 UTC 时间戳存储，而手头是 TAI。第一次用 TAI 值近似查得 $N_1$，第二次用"TAI − $N_1$"（即近似 UTC）查得精确的 $N_2$；若两者一致说明没有跨闰秒边界，直接用 $N_1$；若不一致（输入恰在闰秒内，TAI 与 UTC 跨越了跳秒时刻），用 $N_2$——这是处理闰秒内时刻（23:59:60）的严谨做法，保证 TAI→UTC→TAI 往返一致。
  - **使用场景**：UTC 历元输出、`SlpFile` 转换、`GmatCommand` 的 UTC 显示（`GmatCommand.cpp:2890`）。

#### 公式 4-8：TAI → UT1
- **公式**：$$\mathrm{UTC_{MJD}} = \mathrm{TAI_{MJD}} - \frac{N_{LS}}{86400},\qquad \mathrm{UT1_{MJD}} = \mathrm{UTC_{MJD}} + \frac{\Delta\mathrm{UT1}(\mathrm{TAI})}{86400}$$
- **代码位置**：`TimeSystemConverter.cpp:667-705`（Real）、`TimeSystemConverter.cpp:833-876`（GmatTime）
- **深度讲解**：先按公式 4-7 转 UTC，再从 EOP 文件取 $\Delta\mathrm{UT1}$（秒）换算成天相加。GmatTime 版 `GmatTime val(utcMjd); val.AddSeconds(numOffset);`（`TimeSystemConverter.cpp:874`）用 `AddSeconds` 保持小数秒精度。$\Delta\mathrm{UT1}$ 由 `EopFile::GetUt1UtcOffset`（§五）按 TAI 时间戳线性插值给出。**使用场景**：`Planet::GetHourAngle`（`Planet.cpp:345-350`）计算地方恒星时需要 UT1；`SlpFile`（`SlpFile.cpp:1209-1212`）。

#### 公式 4-9：TAI → TDB
- **公式**（先 TAI→TT 再 TT→TDB，公式 4-5 的逆）：
  $$\mathrm{TT_{MJD}} = \mathrm{TAI_{MJD}} + \frac{32.184}{86400},\qquad \mathrm{TDB_{MJD}} = \mathrm{TT_{MJD}} + \frac{0.001658\sin M_E + 0.00001385\sin 2M_E}{86400}$$
- **代码位置**：`TimeSystemConverter.cpp:706-727`（Real）、`TimeSystemConverter.cpp:877-898`（GmatTime）
- **深度讲解**：
  ```cpp
  // TimeSystemConverter.cpp:713-726
  Real ttJd = ConvertFromTaiMjd(TTMJD, origValue, refJd);   // TAI→TT（+32.184/86400）
  Real tttOffset = T_TT_OFFSET - refJd;
  Real t_TT = (origValue - tttOffset) / T_TT_COEFF1;        // 世纪数
  Real m_E = (M_E_OFFSET + (M_E_COEFF1 * t_TT)) * GmatMathConstants::RAD_PER_DEG;
  Real offset = ((TDB_COEFF1 * Sin(m_E)) + (TDB_COEFF2 * Sin(2 * m_E))) / SECS_PER_DAY;
  Real tdbJd = ttJd + offset;                               // TT + δ = TDB
  ```
  与公式 4-5 互为镜像（注意 $T$ 仍用输入 TAI 值近似，见 4-5 的讨论）。GmatTime 版（第 889-896 行）用 `GmatTime(T_TT_OFFSET) - GmatTime(refJd)` 构造高精度偏移。**使用场景**：DE 星历读取（`DeFile.cpp:548-550`）、`CelestialBody::GetJulianDaysFromTDBEpoch`（`CelestialBody.cpp:6247-6250`）。

#### 公式 4-10：TAI → TT
- **公式**：$$\mathrm{TT_{MJD}} = \mathrm{TAI_{MJD}} + \frac{32.184}{86400}$$
- **代码位置**：`TimeSystemConverter.cpp:728-735`（Real）、`TimeSystemConverter.cpp:899-909`（GmatTime）
- **深度讲解**：Real 版直接加 `TT_TAI_OFFSET/SECS_PER_DAY`；GmatTime 版用 `newValue.AddSeconds(GmatTimeConstants::TT_TAI_OFFSET)`（`TimeSystemConverter.cpp:906-908`）——把 32.184 s 作为秒数累加，比先构造 double 天偏移再相减更精确。**使用场景**：`DeFile::GetPosVel` 的 `overrideTimeSystem` 模式（`DeFile.cpp:368-372`）、`CelestialBody::GetJulianDaysFromTTEpoch`（`CelestialBody.cpp:6219-6222`）。

### TimeSystemConverter::NumberOfLeapSecondsFrom（1941→1858 平移包装）
- **公式**：$$N_{LS} = N_{LS}^{reader}\big(utcMjd + (jdOfMjdRef - 2400000.5)\big)$$
- **代码位置**：`src/gmatutil/util/TimeSystemConverter.cpp:930-952`
- **深度讲解**：
  ```cpp
  Real offsetValue = 0;
  if (jdOfMjdRef != GmatTimeConstants::JD_NOV_17_1858)
     offsetValue = jdOfMjdRef - GmatTimeConstants::JD_NOV_17_1858;  // 默认 29999.5 天
  if (theLeapSecsFileReader == NULL)
     throw TimeFileException("theLeapSecsFileReader is unknown\n");
  Real numLeapSecs = theLeapSecsFileReader->NumberOfLeapSecondsFrom(utcMjd + offsetValue);
  ```
  本方法只做"基准平移 + 空指针保护"，真正的查表在 `LeapSecsFileReader::NumberOfLeapSecondsFrom`（§五）。默认 `jdOfMjdRef = JD_JAN_5_1941`（`TimeSystemConverter.hpp:146`），即把 GMAT 1941 基准 MJD 平移到 1858 基准再查表。**使用场景**：UTC→TAI（公式 4-3）内部调用。

### TimeSystemConverter::GetFirstLeapSecondMJD
- **公式**：$$MJD_{first} = M_{first}^{reader}\big(from+\Delta_{ref},\ to+\Delta_{ref}\big) - 29999.5$$
- **代码位置**：`src/gmatutil/util/TimeSystemConverter.cpp:957-989`
- **深度讲解**：委托 `LeapSecsFileReader::GetFirstLeapSecondMJD`（§五）在区间内找首个跳秒的 1858 基准 MJD，再减去 `JD_JAN_5_1941 − JD_NOV_17_1858 = 29999.5` 平移回 GMAT 基准（`TimeSystemConverter.cpp:980`）。返回 -1 表示区间内无跳秒。**使用场景**：区间历元有效性检查（如传播区间内是否有跳秒）。

### TimeSystemConverter::IsInLeapSecond（1941→1858 平移检测）
- **公式**：$inLeap \iff \mathrm{TAI_{MJD}} + 29999.5 \in \big[\mathrm{tai}_{nearest} - 1/86400,\ \mathrm{tai}_{nearest}\big)$（nearest 为跳秒表中最近的 TAI 时刻）
- **代码位置**：`TimeSystemConverter.cpp:1794-1810`（Real）、`TimeSystemConverter.cpp:1813-1826`（GmatTime）
- **深度讲解**：
  ```cpp
  bool TimeSystemConverter::IsInLeapSecond(Real theTaiMjd)
  {
     Real offsetValue = GmatTimeConstants::JD_JAN_5_1941 -
                        GmatTimeConstants::JD_NOV_17_1858;   // 29999.5 天
     return theLeapSecsFileReader->IsInLeapSecond(theTaiMjd + offsetValue);
  }
  ```
  平移后交给 `LeapSecsFileReader::IsInLeapSecond`（§五）判断。GmatTime 版（第 1813-1826 行）用 `(theTaiMjd + offsetValue).GetMjd()`。**使用场景**：`Convert` 的 `insideLeapSec` 输出（`TimeSystemConverter.cpp:184`、`224`）；`Spacecraft::GetEpoch` 系列判断输出是否显示 23:59:60（`Spacecraft.cpp:7857-7859` 传入 `handleLeapSecond`）。

### ConvertMjdToGregorian：MJD→公历字符串
- **公式**：$Gregorian = f\big(A1Mjd(mjd).ToA1Date(handleLeapSecond)\big)$（内部经 `A1Date` 拆年/月/日/时/分/秒）
- **代码位置**：`src/gmatutil/util/TimeSystemConverter.cpp:1084-1110`
- **深度讲解**：
  ```cpp
  // TimeSystemConverter.cpp:1099-1109
  A1Mjd a1Mjd(mjd);                          // 假定输入是 1941 基准 MJD
  A1Date a1Date = a1Mjd.ToA1Date(handleLeapSecond);  // MJD→日历（闰秒时保留 60 秒）
  GregorianDate gregorianDate(&a1Date, format);      // 格式化
  return gregorianDate.GetDate();
  ```
  `format=1` 输出 `"01 Jan 2000 11:59:28.000"`，`format=2` 输出 `"2000-01-01T11:59:28.000"`（格式定义见 `GregorianDate.cpp:135-136`）。`handleLeapSecond=true` 时 `A1Date` 允许秒=60（UTC 闰秒显示）。
  - **使用场景**：脚本历元输出（`Spacecraft.cpp:7857-7859`）、`TimeData` 参数格式化（`TimeData.cpp:406-408`）、`GmatCommand` 的 UTC/TAI/TT/TDB 并存显示（`GmatCommand.cpp:2890-2893`）、`TextEphemFile` 星历文本输出（`TextEphemFile.cpp:740`）。

### ConvertGregorianToMjd / ConvertGregorianToMjdGT：公历→MJD
- **公式**：$MJD = \mathrm{ModifiedJulianDate}(Y,M,D,H,Min,S)$（默认基准 2430000）
- **代码位置**：`TimeSystemConverter.cpp:1127-1174`（Real）、`TimeSystemConverter.cpp:1191-1238`（GmatTime）
- **深度讲解**：
  ```cpp
  // TimeSystemConverter.cpp:1129-1150
  GregorianDate gregorianDate(greg);
  if (!gregorianDate.IsValid())
     throw TimeFormatException("Gregorian date '" + greg + "' is not valid.");
  A1Date a1Date(gregorianDate.GetYMDHMS());      // 拆出 Y/M/D/H/Min/S
  jules = ModifiedJulianDate(a1Date.GetYear(), a1Date.GetMonth(),
                             a1Date.GetDay(), a1Date.GetHour(),
                             a1Date.GetMinute(), a1Date.GetSecond());
  ```
  核心计算委托 `DateUtil::ModifiedJulianDate`（§六，公式 9-3）；GmatTime 版委托 `ModifiedJulianDateGT`（`TimeSystemConverter.cpp:1212-1214`），返回 GmatTime 保持精度。越界抛 `TimeFormatException`（`TimeSystemConverter.cpp:1167-1171`）。**使用场景**：脚本 `A1Gregorian` 等公历字符串历元解析（`TimeSystemConverter.cpp:1408`）；`NPlateHistoryFileReader` 读历史文件起点（`NPlateHistoryFileReader.cpp:322`）；`Code500EphemerisFile` 的 DUT 参考时刻（`Code500EphemerisFile.cpp:291`）。

### Convert（字符串版）：时间系统+格式解析总管
- **代码位置**：`TimeSystemConverter.cpp:1320-1463`（Real）、`TimeSystemConverter.cpp:1466-1608`（GmatTime）
- **深度讲解**：完整流程——(1) `GetTimeSystemAndFormat` 把 `"TAIModJulian"` 类字符串拆成系统+格式（`TimeSystemConverter.cpp:1346`）；(2) `ValidateTimeSystem`/`ValidateTimeFormat` 校验（第 1355-1373 行）；(3) 输入 `fromMjd == -999.999` 时从字符串解析数值（ModJulian 用 `stringstream` 按 `GmatGlobal::TIME_PRECISION` 精度读，第 1392-1401 行；Gregorian 用 `ConvertGregorianToMjd`，第 1408 行）；(4) 系统不同则调 enum 版 `Convert`（第 1420-1427 行）；(5) 输出 ModJulian 用 `GmatStringUtil::ToString(toMjd, timePrecision)`，Gregorian 用 `ConvertMjdToGregorian`（第 1440-1456 行，UTC 且闰秒时传 `handleLeapSecond`）。GmatTime 版（第 1466-1608 行）ModJulian 解析改走 `fromMjdVal.SetMjdString(fromStr)`（第 1546 行）。
  - `TIME_PRECISION = 16`（`GmatGlobal.hpp:93`）决定 ModJulian 输出的有效数字位数。
  - **使用场景**：脚本 `Epoch`/`TAI`/`UTCGregorian` 等关键字解析的统一入口；`Spacecraft::SetEpoch`、`Propagator` 历元设置的底层。

### GetTimeSystemAndFormat / ValidateTimeSystem / ValidateTimeFormat / GetValidTimeRepresentations
- **代码位置**：`TimeSystemConverter.cpp:1036-1065`（GetTimeSystemAndFormat）、`TimeSystemConverter.cpp:1622-1629`（ValidateTimeSystem）、`TimeSystemConverter.cpp:1652-1730`（ValidateTimeFormat）、`TimeSystemConverter.cpp:1742-1756`（GetValidTimeRepresentations）
- **深度讲解**：`GetTimeSystemAndFormat` 用字符串查找 `"ModJulian"`/`"Gregorian"` 子串把 `"TaiModJulian"` 拆成 `"Tai"`+`"ModJulian"`（第 1043-1064 行）。`ValidateTimeFormat` 对 Gregorian 调 `DateUtil::IsValidGregorian`（`TimeSystemConverter.cpp:1670`），对 ModJulian 用 `GmatStringUtil::ToReal` 校验且在 `checkValue` 时限定 `EARLIEST_VALID_MJD_VALUE=6116.0 ≤ rval ≤ 58127.5=LATEST_VALID_MJD_VALUE`（第 1706-1714 行，范围来自 `DateUtil.cpp:54-59`：斯普特尼克发射至 2100 年）。`GetValidTimeRepresentations` 生成 `{A1ModJulian, TaiModJulian, …, TTModJulian, A1Gregorian, …}` 列表（排除 UT1，因 UT1 依赖 EOP 文件不能由字符串独立表达）。这些是脚本解析与 GUI 校验的支撑函数。

## 五、LeapSecsFileReader 跳秒表与 EopFile

### tai-utc.dat 跳秒表数据文件
- **公式**（每行解析为三元组，见 Parse）：
  $$N_{LS}(t) = off_1 + (t_{MJD} - off_2)\cdot off_3,\qquad \text{适用于 } t \ge jDate$$
- **代码位置**：`application/data/time/tai-utc.dat:1-41`（共 41 行）
- **深度讲解**：文件格式源自 USNO 的 `tai-utc.dat`（`LeapSecsFileReader.cpp:28` 注明来源 `ftp://maia.usno.navy.mil/ser7/tai-utc.dat`），每行 `YYYY MMM D =JD jDate TAI-UTC= off1 S + (MJD - off2) X off3 S`。前 13 行（1961-1968）是线性漂移段（off3≠0，反映早期铯钟对 UTC 的速率修正）；自 1972 年 1 月 1 日起（第 14 行起）off3=0、off1 为整数秒（10, 11, …, 37 s），即现代整秒跳秒。最新一行 2017 年 1 月 1 日 TAI−UTC = 37 s（第 41 行）。**表内 jDate 是 1858 基准 JD**（UTC），`LeapSecsFileReader` 所有查询都先做 `utcMjd + 2400000.5` 还原 JD。

### LeapSecsFileReader::Parse：行解析与 TAI 预计算
- **公式**：$$N_{LS} = off_1 + (jDate - off_2)\cdot off_3,\qquad \mathrm{taiMJD} = jDate - 2400000.5 + \frac{N_{LS}}{86400}$$
- **代码位置**：`src/gmatutil/util/LeapSecsFileReader.cpp:361-424`
- **深度讲解**：
  ```cpp
  // LeapSecsFileReader.cpp:378-417
  ss >> year >> month >> day >> equalsJD >> jDate >> tai_utc >> off1
     >> S >> plus >> mjd >> minus >> off2 >> closeParen >> X >> off3 >> S2;
  if (ss.bad() || ss.fail()) return false;             // 格式错误
  Real numLeapSeconds = off1 + ((jDate - off2) * off3);// 该时刻 TAI−UTC（秒）
  Real taiDate = jDate - GmatTimeConstants::JD_MJD_OFFSET +
                 (numLeapSeconds/GmatTimeConstants::SECS_PER_DAY);  // 1858基准TAI MJD
  LeapSecondInformation leapSecInfo = {jDate, taiDate, off1, off2, off3};
  lookUpTable.push_back(leapSecInfo);                  // 存入查找表
  ```
  **要点**：每行不仅存 `jDate`（UTC 的 1858 JD）与三个系数，还**预计算**该跳秒时刻的 `taiMJD`（1858 基准），供 `IsInLeapSecond` 快速定位。`LeapSecondInformation` 结构含 `{julianDate, taiMJD, offset1, offset2, offset3}`。

### LeapSecsFileReader::NumberOfLeapSecondsFrom：查表
- **公式**：$$N_{LS} = off_1^{(k)} + (utcMjd - off_2^{(k)})\cdot off_3^{(k)},\qquad k = \max\{i : utcMjd + 2400000.5 \ge julianDate^{(i)}\}$$
- **代码位置**：`src/gmatutil/util/LeapSecsFileReader.cpp:176-199`
- **深度讲解**：
  ```cpp
  // LeapSecsFileReader.cpp:180-195
  Real jd = utcMjd + GmatTimeConstants::JD_MJD_OFFSET;   // MJD→JD（1858 基准）
  std::vector<LeapSecondInformation>::iterator info;
  for (std::vector<LeapSecondInformation>::iterator i = lookUpTable.end();
       i > lookUpTable.begin(); i--)                     // 从表尾往前扫
  {
     info = i-1;
     if (jd >= info->julianDate)                         // 找到最后一个 <= jd 的表项
        return (info->offset1 + ((utcMjd - info->offset2) * info->offset3));
  }
  return 0.0;                                            // 早于首行 → 0 秒
  ```
  逆序扫描取"最后一个 julianDate ≤ jd"的表项；现代段 off3=0，返回值即 off1（整数秒）。1972 年前的漂移段返回线性表达式。早于 1961 年返回 0。**使用场景**：公式 4-3、4-7 的查表基础。

### LeapSecsFileReader::GetFirstLeapSecondMJD
- **公式**：$MJD_{first} = \max\{julianDate^{(i)} : fromJD \le julianDate^{(i)} \le toJD\} - 2400000.5$，无则 -1
- **代码位置**：`src/gmatutil/util/LeapSecsFileReader.cpp:214-265`
- **深度讲解**：把输入 MJD 区间转 JD 区间（第 225-226 行），逆序收集落在区间内的表项 JD（第 233-246 行），取最小者（`utcMjdArray.back()` 因逆序压栈即最小 JD，第 256 行）减回 MJD。与 `TimeSystemConverter::GetFirstLeapSecondMJD`（§四）配合完成 1941 基准换算。

### LeapSecsFileReader::IsInLeapSecond：最近跳秒判定
- **公式**：$inLeap \iff \mathrm{taiMJD} \in [\mathrm{tai}_{nearest} - 1/86400,\ \mathrm{tai}_{nearest})$，$\mathrm{tai}_{nearest}$ 为表中与 $\mathrm{taiMJD}$ 距离最小的时刻
- **代码位置**：`src/gmatutil/util/LeapSecsFileReader.cpp:272-343`
- **深度讲解**：
  ```cpp
  // LeapSecsFileReader.cpp:298-334
  for (Integer ii = lookupSize - 1; ii >= 0; ii--) {     // 逆序找最近表项
     currTai  = lookUpTable.at(ii).taiMJD;
     currDiff = GmatMathUtil::Abs(currTai - theTaiMjd);
     if (currDiff >= diff) { nearestLeapSecond = previousTai; break; }  // 第一次回升即停
     else { diff = currDiff; previousTai = currTai; ... }
  }
  Real nearestMinusOne = nearestLeapSecond - (1.0/GmatTimeConstants::SECS_PER_DAY);
  if ((theTaiMjd >= nearestMinusOne) && (theTaiMjd < nearestLeapSecond))
     isLeap = true;                                       // 落在 [最近跳秒-1s, 最近跳秒)
  ```
  边界处理：早于首行取首行（第 292-293 行，注释质疑是否应为 0 但保留现状）、晚于末行取末行（第 294-295 行）。**使用场景**：`TimeSystemConverter::IsInLeapSecond`（§四）的底层，UTC 输出时决定是否渲染 23:59:60。

### EopFile::GetUt1UtcOffset：ΔUT1 线性插值
- **公式**：$$\Delta\mathrm{UT1}(t) = \Delta\mathrm{UT1}_i + \frac{t - t_i}{t_{i+1}-t_i}\big(\Delta\mathrm{UT1}_{i+1}-\Delta\mathrm{UT1}_i\big)\quad(\text{秒}),\qquad t_i \le t < t_{i+1}$$
- **代码位置**：`src/gmatutil/util/EopFile.cpp:387-444`（线性插值主循环 422-442）
- **深度讲解**：EOP 表按 TAI MJD 时间戳存 ΔUT1（秒）。范围外取端点值（第 405-414 行）；范围内二分/顺序定位区间后线性插值（第 422-442 行），并对表间隔非 1 天的记录做整秒修正（第 435-437 行 `diffOff = diffOff - Round(errorInSec)`，消除 ΔUT1 跨整秒跳变的插值偏差）。带缓存（`lastTaiMjd`/`lastOffset`/`lastIndex`，第 393 行）。**使用场景**：公式 4-4、4-8 的 ΔUT1 来源；`Planet::GetHourAngle`（`Planet.cpp:345-350`）、`SlpFile`（`SlpFile.cpp:1209-1212`）。

## 六、DateUtil：儒略日 / 公历 / 年积日 / 日秒

### DateUtil::JulianDay（Fliegel–Van Flandern 整数算法）
- **公式**：$$L = \left\lfloor\frac{M-14}{12}\right\rfloor,\qquad JD = D - 32075 + \left\lfloor\frac{1461(Y+4800+L)}{4}\right\rfloor + \left\lfloor\frac{367(M-2-12L)}{12}\right\rfloor - \left\lfloor\frac{3\left\lfloor\frac{Y+4900+L}{100}\right\rfloor}{4}\right\rfloor$$
- **代码位置**：`src/gmatutil/util/DateUtil.cpp:86-94`
- **深度讲解**：
  ```cpp
  // DateUtil.cpp:89-93
  const Integer L = (month - 14) / 12;        // 1、2月归入上一年（L=1），其余 L=0
  return (day - 32075 + 1461 * (year + 4800 + L) / 4 + 367 *
          (month - 2 - L * 12) / 12 - 3 *
          ((year + 4900 + L) / 100) /4 );
  ```
  经典 Fliegel–Van Flandern 纯整数算法：`L` 把 1/2 月当作上一年的 13/14 月；`1461/4` 项折算闰年（4 年 1461 天）、`367/12` 项折算月长、`3/4` 项扣减世纪年修正（400 年 3 次非闰）。返回值为该日正午的 JD 整数部分（不含时刻小数）。C/C++ 整数除法对正数向下取整，恰好满足公式要求。**使用场景**：`SpacePoint`/`CelestialBody` 内部日期整数计算；`ToDOYFromYearMonthDay` 的对照基准。

### JulianDate（Vallado 算法，含时刻）
- **公式**：$$JD = 367Y - \left\lfloor\frac{7\left[Y+\left\lfloor\frac{M+9}{12}\right\rfloor\right]}{4}\right\rfloor + \left\lfloor\frac{275M}{9}\right\rfloor + D + 1721013.5 + \frac{\left(\frac{S}{60}+Min\right)/60 + H}{24}$$
- **代码位置**：`src/gmatutil/util/DateUtil.cpp:240-250`
- **深度讲解**：
  ```cpp
  // DateUtil.cpp:243-249
  Integer computeYearMon = (7*(year + (Integer)((month + 9)/12)))/4;
  Integer computeMonth = (275 * month)/9;
  Real fractionalDay = ((second/60.0 + minute)/60 + hour)/24.0;   // 时→日
  return ( 367*year - computeYearMon + computeMonth + day +
           1721013.5 + fractionalDay);
  ```
  这是 Vallado《Fundamentals of Astrodynamics and Applications》的 JD 算法（注释第 237 行明示），常数 1721013.5 是该公式的基准日偏移（对应 1900 年 1 月 0.5 日、即 1899-12-31 正午的儒略日，使结果与公元前 4713 年 1 月 1 日正午的 JD 零点对齐）。与 Fliegel–Van Flandern 的差异：本算法显式把时刻换算为 `fractionalDay` 并加到 1721013.5 上；`computeYearMon` 的 `(month+9)/12` 同样是 1/2 月归年技巧。**精度注意**：JD 量级 2.4×10⁶，double 小数位仅约 10 位十进制（≈ 1e-5 天 ≈ 0.86 s），故该函数只用于低精度日期计算，高精度路径走 `ModifiedJulianDate`/`ModifiedJulianDateGT`。

### ModifiedJulianDate（先减基准再加小数，保精度）
- **公式**：$$MJD = \underbrace{367Y - \left\lfloor\frac{7[Y+\lfloor(M+9)/12\rfloor]}{4}\right\rfloor + \left\lfloor\frac{275M}{9}\right\rfloor + D + 1721013.5 - refEpochJD}_{\text{整数部分先算}} + \frac{\left(\frac{S}{60}+Min\right)/60+H}{24}$$
- **代码位置**：`src/gmatutil/util/DateUtil.cpp:273-291`
- **深度讲解**：
  ```cpp
  // DateUtil.cpp:282-290
  Integer computeYearMon = ( 7*(year + (Integer)((month + 9)/12)) )/4;
  Integer computeMonth = (275 * month)/9;
  Real fractionalDay = ((second/60.0 + minute)/60.0 + hour)/24.0;
  Real ModJulianDay = 367*year - computeYearMon + computeMonth + day +
              1721013.5 -  refEpochJD;          // 整数（天）部分
  Real modJulianDate = ModJulianDay  + fractionalDay;   // 小数最后加
  ```
  默认 `refEpochJD = JULIAN_DATE_OF_010541 = 2430000`（`DateUtil.hpp:132`），即 GMAT 的 1941 基准。**精度处理**：第 277-280 行注释明示"先减掉 JD 偏移再加当日小数"——`1721013.5 − 2430000` 在整数部分完成，使小数部分在 ~2×10⁴ 量级而非 2.4×10⁶ 量级上相加，显著提升小数位有效数字（对比 JulianDate 的 0.86 s 精度，本函数可达 μs 级）。**使用场景**：`ConvertGregorianToMjd`（`TimeSystemConverter.cpp:1148-1150`）——所有公历字符串历元解析的数学核心。

### ModifiedJulianDateGT（GmatTime 版）
- **公式**：同 ModifiedJulianDate，但全程 GmatTime 三部分运算：
  $$MJD_{GT} = \mathrm{GmatTime}(1721013.5) + (367Y - \lfloor\cdots\rfloor + D) - refEpochJD + 3600H + 60Min + S$$
- **代码位置**：`src/gmatutil/util/DateUtil.cpp:314-331`
- **深度讲解**：
  ```cpp
  // DateUtil.cpp:320-328
  Integer computeYearMon = ( 7*(year + (Integer)((month + 9)/12)) )/4;
  Integer computeMonth = (275 * month)/9;
  GmatTime modJulianDate(1721013.5);                      // 大数作为起点
  modJulianDate += 367*year - computeYearMon + computeMonth + day;  // 整数天
  modJulianDate -= refEpochJD;                            // 减基准
  modJulianDate.AddSeconds(hour * GmatTimeConstants::SECS_PER_HOUR);
  modJulianDate.AddSeconds(minute * GmatTimeConstants::SECS_PER_MINUTE);
  modJulianDate.AddSeconds(second);                       // 时分秒以秒累加
  ```
  与 Real 版的本质区别：`AddSeconds` 把时分秒作为秒数累加，全程在 `Sec`/`FracSec` 字段运算，彻底绕开 double MJD 的量级限制，是亚微秒精度公历解析的最终实现。**使用场景**：`ConvertGregorianToMjdGT`（`TimeSystemConverter.cpp:1212-1214`），供 GmatTime 版字符串 Convert 使用。

### UnpackDate / UnpackDateWithDOY / UnpackTime（打包格式拆解）
- **公式**：$$\text{YYYYMMDD} \to (Y,M,D):\quad Y=\lfloor v/10000\rfloor,\ M=\lfloor (v\bmod 10000)/100\rfloor,\ D=\lfloor v\bmod 100 + 0.5\rfloor$$
  $$\text{YYYYDDD} \to (Y,DOY):\quad Y=\lfloor v/1000\rfloor,\ DOY=\lfloor v\bmod 1000 + 0.5\rfloor$$
  $$\text{hhmmssnnn} \to (H,Min,S):\quad H=\lfloor (v+20000)/10^7\rfloor,\ Min=\lfloor ((v+20000)\bmod 10^7)/10^5\rfloor,\ S=((v+20000)\bmod 10^5)/1000 - 20$$
- **代码位置**：`DateUtil.cpp:342-353`（UnpackDate）、`DateUtil.cpp:365-380`（UnpackDateWithDOY）、`DateUtil.cpp:392-408`（UnpackTime）
- **深度讲解**：三函数分别处理 GMAT 的打包历元格式。`UnpackDate` 用 `Floor`+`Mod` 逐位拆解 YYYYMMDD，`day` 取 `+0.5` 四舍五入以抵消浮点表示误差（第 349 行）；越界抛 `Date::TimeRangeError`（第 351-352 行）。`UnpackDateWithDOY` 拆 YYYYDDD 并校验闰年（第 372-379 行）。`UnpackTime` 处理 hhmmssnnn（毫秒为 3 位）：先整体加 20000（= 20 秒的毫秒数，第 396 行注释说明"加 20 秒避免分钟边界附近的大误差"），拆出时分后把秒减去 20 还原，允许秒到 61.0（闰秒，第 403-407 行）。

### ToMonthDayFromYearDOY / ToDOYFromYearMonthDay（年积日互转）
- **公式**：$$DOY = \sum_{i=1}^{M-1} daysInMonth_i + D\quad(\text{用 } DAYS\_BEFORE\_MONTH\ \text{表});\qquad (Y,DOY)\to(M,D):\ M=\max\{i: DOY \le before_i\},\ D=DOY - before_{M-1}$$
- **代码位置**：`DateUtil.cpp:420-447`（ToMonthDayFromYearDOY）、`DateUtil.cpp:458-471`（ToDOYFromYearMonthDay）
- **深度讲解**：
  ```cpp
  // DateUtil.cpp:436-446  （ToMonthDayFromYearDOY）
  if (isLeap) ptrDaysList = GmatTimeConstants::LEAP_YEAR_DAYS_BEFORE_MONTH;
  else        ptrDaysList = GmatTimeConstants::DAYS_BEFORE_MONTH;
  for (i=1; i<12; i++)
     if (dayOfYear <= ptrDaysList[i]) break;   // 找到第一个“本月初累计天数≥DOY”的月
  month = i;
  day = dayOfYear - ptrDaysList[i-1];          // 减去上月累计天
  ```
  反向（`ToDOYFromYearMonthDay`）直接查 `DAYS_BEFORE_MONTH[month-1] + day`（第 465-468 行），闰年用 `LEAP_YEAR_DAYS_BEFORE_MONTH`。两张表定义于 `GmatConstants.hpp:154-157`。**使用场景**：`SpacePoint`/`CelestialBody` 的 `GetEpoch` 年积日输出、`TextEphemFile` 的 `YYYYDDD` 列、大气模型的日参数计算（`Msise90Atmosphere` 的 `yd`）。

### ToSecondsOfDayFromHMS / ToHMSFromSecondsOfDay（日秒互转）
- **公式**：$$SOD = 3600H + 60Min + S;\qquad H=\lfloor SOD/3600\rfloor,\ Min=\lfloor (SOD-3600H)/60\rfloor,\ S=SOD-3600H-60Min$$
- **代码位置**：`DateUtil.cpp:483-495`（ToSecondsOfDayFromHMS）、`DateUtil.cpp:509-532`（ToHMSFromSecondsOfDay）
- **深度讲解**：`ToSecondsOfDayFromHMS` 用 `ElapsedTime` 聚合（第 485、493-494 行）校验并换算，允许秒 ≤ 61（闰秒，第 487-491 行）。`ToHMSFromSecondsOfDay` 接受 0~86401.0 秒（含闰秒日 23:59:60），时/分分别截断并夹取到 23/59（第 520-531 行）。**使用场景**：公历时间部分与"当日秒"的中间转换，`A1Date`/`GregorianDate` 内部使用。

### IsLeapYear / IsValidTime / IsValidGregorian
- **公式**：$$\text{leap} \iff (Y \bmod 4 = 0)\ \text{且}\ (Y \bmod 100 \ne 0\ \text{或}\ Y \bmod 400 = 0)$$
- **代码位置**：`DateUtil.cpp:580-590`（IsLeapYear）、`DateUtil.cpp:542-569`（IsValidTime）、`DateUtil.cpp:110-213`（IsValidGregorian）
- **深度讲解**：
  ```cpp
  // DateUtil.cpp:584-589
  if ((year % 100 == 0) && (year % 400 == 0)) result = true;  // 400 整除的世纪年
  else if (year % 4 == 0)                                     // 4 整除（含非世纪年）
     result = true;
  ```
  格里历闰年规则。`IsValidTime` 用 `DAYS_IN_MONTH`/`LEAP_YEAR_DAYS_IN_MONTH` 表校验日数，秒允许 [0,61)（闰秒）（第 554-565 行）。`IsValidGregorian` 解析 `"dd mmm yyyy hh:mm:ss.mmm"` 四段（第 112-154 行），`checkDate=true` 时限定在 `MIN_YEAR=1957` 至 `MAX_YEAR=2100` 区间（第 166-210 行，边界常量 `DateUtil.cpp:64-76`）。**使用场景**：`ValidateTimeFormat`（`TimeSystemConverter.cpp:1670-1688`）、脚本历元字符串校验。

## 七、solarsys 中的星历时换算应用

### DeFile::GetPosVel：A1 → TDB/TT 后插值 DE 星历
- **公式**：$t_{DE} = \mathrm{Convert}(t_{A1},\ \text{A1MJD},\ \text{TDBMJD}\ \text{或}\ \text{TTMJD},\ JD\_JAN\_5\_1941)$（MJD，1941 基准）
- **代码位置**：`src/base/solarsys/DeFile.cpp:322-395`（Real 版）、`DeFile.cpp:529-560`（GmatTime 版）、`DeFile.cpp:705-742`（GmatTime 差分版）、偏移常量 `DeFile.cpp:104-105`、`DeFile.cpp:135`
- **深度讲解**：
  ```cpp
  // DeFile.cpp:364-395  （Real 版核心）
  if (overrideTimeSystem) {                                  // 用 TT 覆盖 TDB 的开关
     double mjdTT = (double) theTimeConverter->Convert(atTime.Get(),
                     TimeSystemConverter::A1MJD, TimeSystemConverter::TTMJD,
                     GmatTimeConstants::JD_JAN_5_1941);
     absJD = mjdTT;                                          // 默认使用 TDB，可强制 TT
  } else {
     double mjdTDB = (double) theTimeConverter->Convert(atTime.Get(),
                     TimeSystemConverter::A1MJD, TimeSystemConverter::TDBMJD,
                     GmatTimeConstants::JD_JAN_5_1941);
     absJD = mjdTDB;
  }
  Interpolate_State(absJD, forBody, &rv);                    // 切比雪夫插值
  ```
  **要点**：JPL DE 星历自变量的时间坐标是 TDB（以 JD 表达）；GMAT 内部把 DE 文件头里的 JD 直接减 `baseEpoch = JD_JAN_5_1941`（`DeFile.cpp:1115-1116`、`135`）存成 1941 基准 MJD，因此插值时间与 `Convert` 输出同尺度、无需二次换算。`overrideTimeSystem`（`DeFile::GetPosVel` 形参，`DeFile.cpp:313`、`322`；`CelestialBody` 侧对应成员 `overrideTime`，`CelestialBody.hpp:578`，在 `CelestialBody.cpp:1195` 等处以第三实参传入）允许用 TT 代替 TDB（TDB−TT ≤ 1.7 ms，对多数任务可忽略）。GmatTime 版（第 529-560 行）全程 GmatTime，`Interpolate_State(GmatTime, …)`（`DeFile.cpp:1922`）在内部 `Read_Coefficients` 归一化切比雪夫自变量。差分版 `GetPosVelDelta`（第 705-742 行）用 GmatTime 做两个时刻的 TDB 转换后插值差分。
  - **使用场景**：`CelestialBody::GetState` → `PlanetaryEphem::GetEphemData` 的默认星历路径；`Moon::GetBodyCartographicCoordinates` 等依赖 `GetState` 的调用链。

### CelestialBody::GetJulianDaysFromTTEpoch / GetJulianDaysFromTDBEpoch
- **公式**：$$d_{TT} = \mathrm{Convert}(t_{A1},\text{A1MJD},\text{TTMJD},JD\_JAN\_5\_1941) + 2430000 - 2451545 = \mathrm{TT_{MJD}} - 21545$$
  $$d_{TDB} = \mathrm{Convert}(t_{A1},\text{A1MJD},\text{TDBMJD},JD\_JAN\_5\_1941) + 2430000 - 2451545 = \mathrm{TDB_{MJD}} - 21545$$
- **代码位置**：`CelestialBody.cpp:6217-6225`（TTEpoch）、`CelestialBody.cpp:6240-6257`（TDBEpoch）
- **深度讲解**：
  ```cpp
  // CelestialBody.cpp:6247-6255
  Real mjdTDB = theTimeConverter->Convert(forTime.Get(),
                                          TimeSystemConverter::A1MJD,
                                          TimeSystemConverter::TDBMJD,
                                          GmatTimeConstants::JD_JAN_5_1941);
  // JD_OF_J2000 (2451545.0) TDB 是 IAU 制图工作组规定的制图数据参考历元
  return (mjdTDB + GmatTimeConstants::JD_JAN_5_1941 -
          GmatTimeConstants::JD_OF_J2000);
  ```
  返回"自 J2000 TDB 起算的儒略日数"（即 `TDB_{MJD} − 21545` 天，可负）。IAU 制图坐标（IAU 2000 报告）规定行星自转参数的时间自变量为自 J2000.0 TDB 起的儒略日。**使用场景**：`CelestialBody::GetBodyCartographicCoordinates` IAU_SIMPLIFIED 分支（`CelestialBody.cpp:4299-4301`，用户定义方向时还减去 `orientationEpoch` 的 TDB 日数）；`Planet::GetBodyCartographicCoordinates` 海王星 IAU_2002 分支（`Planet.cpp:291`）；`Moon::GetBodyCartographicCoordinates`（`Moon.cpp:220`）。

### Planet::GetHourAngle：A1 → UT1 求恒星时
- **公式**：$jd_{UT1} = \mathrm{Convert}(t_{A1},\text{A1MJD},\text{UT1MJD},JD\_JAN\_5\_1941) + 2430000$；$t_{UT1} = (jd_{UT1}-2451545)/36525$
- **代码位置**：`Planet.cpp:339-366`
- **深度讲解**：
  ```cpp
  // Planet.cpp:345-362
  Real mjdUT1 = theTimeConverter->Convert(atTime.Get(),
                             TimeSystemConverter::A1MJD, TimeSystemConverter::UT1MJD,
                             GmatTimeConstants::JD_JAN_5_1941);   // A1→UT1（含 EOP）
  Real jdUT1    = mjdUT1 + GmatTimeConstants::JD_JAN_5_1941;      // MJD→JD
  Real tUT1     = (jdUT1 - GmatTimeConstants::JD_OF_J2000) / GmatTimeConstants::DAYS_PER_JULIAN_CENTURY;
  Real mst = (67310.54841 / 240) +                                 // Vallado 式 3-45（度）
     (((876600 * 15) + (8640184.812866 / 240)) * tUT1) + ...;
  hourAngle = AngleUtil::PutAngleInDegRange(mst,0.0,360.0);        // 归入 [0,360)
  ```
  恒星时计算必须用 UT1（自转相位对应世界时），故先 A1→UT1 再按 Vallado 式 3-45 求格林尼治平恒星时。**使用场景**：地球 `GetHourAngle`（行星时角/地方恒星时相关 GUI 与计算）。

### Moon::GetBodyCartographicCoordinates：TDB 日数驱动 IAU 2000 月球自转
- **公式**：$d = \mathrm{GetJulianDaysFromTDBEpoch}(t)$（公式见上）；$W = 38.3213 + 13.17635815\,d - 1.4\times10^{-12}d^2 + \sum_i A_i\sin p_i$ 等（IAU 2000 月球自转参数表）
- **代码位置**：`Moon.cpp:208-254`（`d` 的取得在第 220-221 行，自转公式第 241-254 行）
- **深度讲解**：月球自转的 IAU 2000 模型把各周期项写成 TDB 日数 $d$ 的线性相位（如 `p3 = Rad(260.008 + 13.0120009*d)`，第 229 行），经度 $W$ 含一次项 `13.17635815·d`（每日自转速率）。**使用场景**：`Moon` 的 `GetBodyCartographicCoordinates`，供月面坐标系/月球指向计算。

### SlpFile::a1_utc_offset：UT1/TT/A1 与 UTC 的秒级差
- **公式**：$$\Delta_{A1-UTC} = (t_{A1} - t_{UTC})\cdot 86400,\qquad \Delta_{UT1-UTC} = (t_{UT1}-t_{UTC})\cdot 86400,\qquad \Delta_{TDT-UTC} = (t_{TT}-t_{UTC})\cdot 86400$$
- **代码位置**：`SlpFile.cpp:1203-1218`
- **深度讲解**：
  ```cpp
  // SlpFile.cpp:1203-1218
  Real mjdA1  = theTimeConverter->Convert(refmjd,
                TimeSystemConverter::UTCMJD, TimeSystemConverter::A1MJD,
                GmatTimeConstants::JD_JAN_5_1941);
  *a1utc      = (mjdA1 - refmjd) * GmatTimeConstants::SECS_PER_DAY;   // 秒
  Real mjdUT1 = theTimeConverter->Convert(refmjd,
                TimeSystemConverter::UTCMJD, TimeSystemConverter::UT1MJD,
                GmatTimeConstants::JD_JAN_5_1941);
  *ut1utc     = (mjdUT1 - refmjd) * GmatTimeConstants::SECS_PER_DAY;
  Real mjdTT  = theTimeConverter->Convert(refmjd,
                TimeSystemConverter::UTCMJD, TimeSystemConverter::TTMJD,
                GmatTimeConstants::JD_JAN_5_1941);
  *tdtutc     = (mjdTT - refmjd) * GmatTimeConstants::SECS_PER_DAY;
  ```
  历史遗留代码（第 1182-1189 行被注释的旧实现是直接对 `coef[][i]` 二次多项式求值）被替换为 `TimeSystemConverter` 统一换算，再把天差乘以 86400 得秒。**使用场景**：SLP（行星自转星历）文件读取时把 UTC 时刻换算为 A1/UT1/TT 供插值（`SlpFile` 读取 `Planet` 自转参数）。

### Msise90Atmosphere::Density：A1 → UTC 供 MSISE-90
- **公式**：$t_{UTC} = \mathrm{Convert}(epoch,\ \text{A1MJD},\ \text{UTCMJD},\ JD\_JAN\_5\_1941)$
- **代码位置**：`Msise90Atmosphere.cpp:176-177`
- **深度讲解**：MSISE-90 经验大气模型的时间自变量是 UTC（太阳天顶角/地方时依赖真实自转相位），故把 A1 历元转 UTC 后喂给 `GetInputs`（`Msise90Atmosphere.cpp:179`）。**使用场景**：`Msise90Atmosphere` 密度计算（见 [第6章 §3.5](../CH06-dynamics.md) 大气模型部分）。

## 八、公式索引表

| 公式 | 文件:行 | 所属类/函数 |
|---|---|---|
| $TAI = A1 - 0.0343817/86400$ | `src/gmatutil/util/TimeSystemConverter.cpp:282-286` | `TimeSystemConverter::ConvertToTaiMjd` |
| $TAI = TT - 32.184/86400$ | `TimeSystemConverter.cpp:397-401` | `TimeSystemConverter::ConvertToTaiMjd` |
| $TAI = UTC + N_{LS}(UTC+\Delta_{ref})/86400$ | `TimeSystemConverter.cpp:291-323` | `TimeSystemConverter::ConvertToTaiMjd` |
| $TAI = UT1 - \Delta UT1 + (TAI-UTC)$（不动点） | `TimeSystemConverter.cpp:325-356` | `TimeSystemConverter::ConvertToTaiMjd` |
| $TT = TDB - (0.001658\sin M_E+0.00001385\sin 2M_E)/86400$ | `TimeSystemConverter.cpp:357-396` | `TimeSystemConverter::ConvertToTaiMjd` |
| $A1 = TAI + 0.0343817/86400$ | `TimeSystemConverter.cpp:604-612` | `TimeSystemConverter::ConvertFromTaiMjd` |
| $UTC = TAI - N_{LS}/86400$（双次查表） | `TimeSystemConverter.cpp:622-666` | `TimeSystemConverter::ConvertFromTaiMjd` |
| $UT1 = UTC + \Delta UT1/86400$ | `TimeSystemConverter.cpp:667-705` | `TimeSystemConverter::ConvertFromTaiMjd` |
| $TDB = TT + (0.001658\sin M_E+0.00001385\sin 2M_E)/86400$ | `TimeSystemConverter.cpp:706-727` | `TimeSystemConverter::ConvertFromTaiMjd` |
| $TT = TAI + 32.184/86400$ | `TimeSystemConverter.cpp:728-735`、`899-909` | `TimeSystemConverter::ConvertFromTaiMjd` |
| $t_{TAI}\to t_{out}$ 两段式总管 | `TimeSystemConverter.cpp:153-200`、`203-244` | `TimeSystemConverter::Convert` |
| $N_{LS} = N_{LS}^{reader}(utcMjd+\Delta_{ref})$ | `TimeSystemConverter.cpp:930-952` | `TimeSystemConverter::NumberOfLeapSecondsFrom` |
| $MJD_{first} = M_{first}^{reader}-29999.5$ | `TimeSystemConverter.cpp:957-989` | `TimeSystemConverter::GetFirstLeapSecondMJD` |
| $inLeap \iff TAI+29999.5\in[tai_{n}-1/86400,\ tai_n)$ | `TimeSystemConverter.cpp:1794-1810`、`1813-1826` | `TimeSystemConverter::IsInLeapSecond` |
| $Gregorian = f(A1Date(mjd))$ | `TimeSystemConverter.cpp:1084-1110` | `TimeSystemConverter::ConvertMjdToGregorian` |
| $MJD = ModifiedJulianDate(Y,M,D,H,Min,S)$ | `TimeSystemConverter.cpp:1127-1174`、`1191-1238` | `TimeSystemConverter::ConvertGregorianToMjd(/GT)` |
| 字符串系统/格式解析与校验 | `TimeSystemConverter.cpp:1320-1463`、`1466-1608`、`1652-1730` | `TimeSystemConverter::Convert`（字符串版）、`ValidateTimeFormat` |
| $MJD = Days + (Sec+FracSec)/86400$ | `src/gmatutil/util/GmatTime.cpp:560-563` | `GmatTime::GetMjd` |
| $t_{sec} = Days\cdot86400+Sec+FracSec$ | `GmatTime.cpp:600-603` | `GmatTime::GetTimeInSec` |
| $Days=\lfloor\|mjd\|\rfloor,\ Sec=\lfloor(\cdot)86400\rfloor,\ FracSec=\{\cdot\}$ | `GmatTime.cpp:76-146` | `GmatTime::GmatTime(Real)` |
| 秒→三部分拆分 | `GmatTime.cpp:566-597` | `GmatTime::SetTimeInSec` |
| 分量相加+两级归一化 | `GmatTime.cpp:182-222`、`262-318` | `GmatTime::operator+ / operator-` |
| 分量乘/除标量 | `GmatTime.cpp:359-366`、`372-425` | `GmatTime::operator* / operator/` |
| 1e-7 天粒度双段格式化 | `GmatTime.cpp:607-659` | `GmatTime::ToString` |
| 9 位小数分段解析 | `GmatTime.cpp:662-709` | `GmatTime::SetMjdString` |
| $\|diff\|_{sec}<tol$ 判近等 | `GmatTime.cpp:712-722` | `GmatTime::IsNearlyEqual` |
| 三部分存储结构 | `src/gmatutil/util/GmatTime.hpp:97-101` | `GmatTime` 数据成员 |
| $N_{LS}=off_1+(utcMjd-off_2)off_3$（逆序查表） | `src/gmatutil/util/LeapSecsFileReader.cpp:176-199` | `LeapSecsFileReader::NumberOfLeapSecondsFrom` |
| $N_{LS}=off_1+(jDate-off_2)off_3$；$taiMjd=jDate-2400000.5+N_{LS}/86400$ | `LeapSecsFileReader.cpp:361-424` | `LeapSecsFileReader::Parse` |
| $MJD_{first}=\max\{JD_i\}-2400000.5$ | `LeapSecsFileReader.cpp:214-265` | `LeapSecsFileReader::GetFirstLeapSecondMJD` |
| 最近跳秒 ±1 s 判定 | `LeapSecsFileReader.cpp:272-343` | `LeapSecsFileReader::IsInLeapSecond` |
| 跳秒表原始数据（37 s 最新） | `application/data/time/tai-utc.dat:1-41` | 数据文件 |
| $\Delta UT1$ 线性插值 | `src/gmatutil/util/EopFile.cpp:387-444` | `EopFile::GetUt1UtcOffset` |
| Fliegel–Van Flandern 整数 JD | `src/gmatutil/util/DateUtil.cpp:86-94` | `DateUtil::JulianDay` |
| Vallado JD（含时刻） | `DateUtil.cpp:240-250` | `JulianDate`（友元函数） |
| $MJD = JD_{int} - refEpochJD + fracDay$ | `DateUtil.cpp:273-291` | `ModifiedJulianDate`（友元函数） |
| GmatTime 版 MJD（AddSeconds 累加） | `DateUtil.cpp:314-331` | `ModifiedJulianDateGT`（友元函数） |
| YYYYMMDD/YYYYDDD/hhmmssnnn 拆解 | `DateUtil.cpp:342-353`、`365-380`、`392-408` | `UnpackDate`/`UnpackDateWithDOY`/`UnpackTime` |
| $DOY = before[M-1]+D$ 互转 | `DateUtil.cpp:420-447`、`458-471` | `ToMonthDayFromYearDOY`/`ToDOYFromYearMonthDay` |
| $SOD=3600H+60Min+S$ 互转 | `DateUtil.cpp:483-495`、`509-532` | `ToSecondsOfDayFromHMS`/`ToHMSFromSecondsOfDay` |
| 格里历闰年/有效性 | `DateUtil.cpp:580-590`、`542-569`、`110-213` | `IsLeapYear`/`IsValidTime`/`IsValidGregorian` |
| 换算常量全表 | `src/gmatutil/util/GmatConstants.hpp:134-176` | `GmatTimeConstants` |
| 时间类型与聚合结构 | `src/gmatutil/util/TimeTypes.hpp:38-88` | `GmatTimeUtil` |
| $t_{DE} = Convert(A1\to TDB/TT)$ | `src/base/solarsys/DeFile.cpp:364-395`、`529-560`、`705-742` | `DeFile::GetPosVel(/Delta)` |
| $d_{TT/TDB} = Convert(...) - 21545$ | `src/base/solarsys/CelestialBody.cpp:6217-6225`、`6240-6257` | `CelestialBody::GetJulianDaysFromTTEpoch(/TDBEpoch)` |
| $jd_{UT1}$ 求恒星时 | `src/base/solarsys/Planet.cpp:345-362` | `Planet::GetHourAngle` |
| TDB 日数驱动 IAU 自转 | `src/base/solarsys/Moon.cpp:220-254`、`CelestialBody.cpp:4299-4301`、`Planet.cpp:291` | `GetBodyCartographicCoordinates` 系列 |
| $\Delta_{A1/UT1/TT-UTC}$（秒） | `src/base/solarsys/SlpFile.cpp:1203-1218` | `SlpFile::a1_utc_offset` |
| A1→UTC 供 MSISE-90 | `src/base/solarsys/Msise90Atmosphere.cpp:176-177` | `Msise90Atmosphere::Density` |
