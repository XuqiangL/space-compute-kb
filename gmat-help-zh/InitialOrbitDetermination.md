# 初轨确定（InitialOrbitDetermination）

> 译自 GMAT R2026a 帮助文档 InitialOrbitDetermination.html

**Initial Orbit Determination** —— 一组支持早期轨道操作的 Python 函数。

## 描述

一组允许用户执行初轨确定（IOD）的函数集合。其中包括 Gibbs 方法和 Herrick-Gibbs 方法的实现，用户可借此由三个顺序位置矢量确定物体的速度。此外还包含顶层函数，可根据用户提供的输入决定使用哪种方法。

初轨确定函数通过 Python 用户界面访问，使用 GMAT 的 CallPythonFunction 命令，并要求为 Python 安装 Numpy 库。有关 Python 用户界面的详细信息，请参见 Python Interface 参考。有关调用 Python 函数和传递数据的详细信息，请参见 CallPythonFunction 参考。Numpy 包的安装说明可在其网站 https://numpy.org/ 找到。

## 函数

| 字段 | 描述 |
|------|------|
| **CalculateIODGibbs** | Gibbs 方法的实现。计算与第二个输入位置矢量对应的速度。<br>**输入**：<br>r1 —— 第一次观测的 [x,y,z] 位置矢量 (km)<br>r2 —— 第二次观测的 [x,y,z] 位置矢量。将求解此位置处的速度。(km)<br>r3 —— 第三次观测的 [x,y,z] 位置矢量 (km)<br>mu —— 中心天体的引力参数。默认为地球 (3.986004415e5 km^3/s^2)<br>verbose —— 是否记录日志信息的 True/False 标志。默认为 false。<br>**输出**：<br>若 Verbose == False：v2 —— 第二次观测处的 [vx,vy,vz] 速度矢量 (km/s)<br>若 Verbose == True：v2 —— 第二次观测处的 [vx,vy,vz] 速度矢量 (km/s)；log —— 包含计算过程中记录的任何信息的字符串 |
| **CalculateIODHerrickGibbs** | Herrick-Gibbs 方法的实现。计算与第二个输入位置矢量对应的速度。<br>**输入**：<br>r1 —— 第一次观测的 [x,y,z] 位置矢量 (km)<br>r2 —— 第二次观测的 [x,y,z] 位置矢量。将求解此位置处的速度。(km)<br>r3 —— 第三次观测的 [x,y,z] 位置矢量 (km)<br>t1 —— 第一次测量时间，儒略日格式（也可以是修正儒略日，或 秒/86400）<br>t2 —— 第二次测量时间，儒略日格式（也可以是修正儒略日，或 秒/86400）<br>t3 —— 第三次测量时间，儒略日格式（也可以是修正儒略日，或 秒/86400）<br>mu —— 中心天体的引力参数。默认为地球 (3.986004415e5 km^3/s^2)<br>verbose —— 是否记录日志信息的 True/False 标志。默认为 false。<br>**输出**：<br>若 Verbose == False：v2 —— 第二次观测处的 [vx,vy,vz] 速度矢量 (km/s)<br>若 Verbose == True：v2 —— 第二次观测处的 [vx,vy,vz] 速度矢量 (km/s)；log —— 包含计算过程中记录的任何信息的字符串 |
| **ThreePositionIOD** | 执行 IOD 的顶层函数，根据观测之间的分离角选择 Gibbs 或 Herrick-Gibbs 方法。<br>**输入**：r1、r2、r3 —— 三次观测的 [x,y,z] 位置矢量 (km)，求解 r2 处速度；t1、t2、t3 —— 三次测量时间，儒略日格式（也可以是修正儒略日，或 秒/86400）；mu —— 中心天体引力参数，默认为地球 (3.986004415e5 km^3/s^2)；IODType —— 可选字符串，可设为 "Gibbs" 或 "HerrickGibbs" 以覆盖选择逻辑并强制使用指定的 IOD 方法。<br>**输出**：v2 —— 第二次观测处的 [vx,vy,vz] 速度矢量 (km/s)；log —— 包含计算过程中记录的信息以及所执行 IOD 方法的字符串 |
| **ThreePositionIODLean** | 执行 IOD 的顶层函数，根据观测之间的分离角选择 Gibbs 或 Herrick-Gibbs 方法。此版本不返回 log 参数。<br>**输入**：与 ThreePositionIOD 相同（r1、r2、r3、t1、t2、t3、mu、IODType）。<br>**输出**：v2 —— 第二次观测处的 [vx,vy,vz] 速度矢量 (km/s) |

## 备注

在某些情形下，用户对希望进行轨道确定的天体掌握的信息有限。在这种情况下，用户只有若干位置测量值（或可从中导出位置的测量值，如方位角、仰角和测距），用以预测航天器的未来状态。对于这类特定问题，Gibbs 方法和 Herrick-Gibbs 方法非常适合。这两种方法各自接收惯性系中的三个位置矢量，并返回航天器在第二个位置处的速度。由于求解问题所采用的途径不同，每种方法各有其更适用的情形，且两者共享一组共同的假设。两种方法都提供二体问题的解，因此存在显著外部摄动的情形不适合使用此功能。此外，两种方法都假定三个位置矢量按时间顺序排列且共面。为允许真实数据中的偏差，共面要求允许一定的灵活性：观测必须在共面 3 度以内。由于 Gibbs 方法以几何方式求解，更适合分离角较大的观测。相比之下，Herrick-Gibbs 方法本质上是围绕第二次观测进行泰勒级数展开，更适合间隔紧密的测量，但随着观测间分离角增大而精度下降。一种算法优于另一种算法的确切分界点是活跃的研究领域，根据轨道特性的不同，可在 6 度到 16 度之间变化。对于顶层函数，GMAT 采用更保守的 6 度作为分类值：若任一分离角超过此值则选择 Gibbs，若两者都等于或低于此值则选择 Herrick-Gibbs。有关 Gibbs 和 Herrick-Gibbs 方法及其实现算法的更多信息，请查阅参考文献 1。有关分离角选择准则的更多信息，请查阅参考文献 2。

## 示例

由三个间隔紧密的观测求解速度，并输出结果和日志。

```
Create Array R1[1,3] R2[1,3] R3[1,3] V2[1,3];
Create Variable T1 T2 T3;
Create String Log;

BeginMissionSequence;
%Observation 1
T1 = 0.0;
R1(1) = -6775.105759552147;
R1(2) = -2396.512640028521;
R1(3) = 3.17775066150299;

%Observation 2
T2 = 1.0/86400;
R2(1) = -6775.468602539761;
R2(2) = -2395.440370930451;
R2(3) = 10.54007909680081;

%Observation 3
T3 = 2.0/86400;
R3(1) = -6775.824159536231;
R3(2) = -2394.365525912181;
R3(3) = 17.90239606811341;

[V2,Log] = Python.IODFunctions.ThreePositionIOD(R1,R2,R3,T1,T2,T3);
Write V2
Write Log
```

**中文说明**：三次观测间隔 1 秒（时间以天为单位，T2=1/86400），调用 Python 的 ThreePositionIOD 函数自动选择 IOD 方法（间隔紧密时选 Herrick-Gibbs），输出速度矢量 V2 和日志 Log。

由三个间隔较宽的观测求解速度，并输出结果和日志。这些观测之间的测量间隔为 8 分钟。

```
Create Array R1[1,3] R2[1,3] R3[1,3] V2[1,3];
Create Variable T1 T2 T3;
Create String Log;

BeginMissionSequence;
%Observation 1
T1 = 0.0;
R1(1) = -6775.105759552147;
R1(2) = -2396.512640028521;
R1(3) = 3.17775066150299;

%Observation 2
T2 = 480.0/86400;
R2(1) = -6121.441100575906;        
R2(2) = -1612.515594798989;
R2(3) = 3392.148414170606;

%Observation 3
T3 = 960.0/86400;
R3(1) = -3981.62429448081;
R3(2) = -437.0235397882232;
R3(3) =  5955.582570970698;

[V2,Log] = Python.IODFunctions.ThreePositionIOD(R1,R2,R3,T1,T2,T3);
Write V2
Write Log
```

**中文说明**：三次观测间隔 8 分钟（480 秒），分离角较大，ThreePositionIOD 将自动选择 Gibbs 方法求解第二次观测处的速度。

## 参考文献

1. Vallado, David A., and Wayne D. McClain. *Fundamentals of Astrodynamics and Applications*, Fourth Edition. Microcosm Press, 2013.（《航天动力学基础与应用》第四版）
2. Kaushik, Arvind Shankar, *A Statistical Comparison Between Gibbs and Herrick-Gibbs Orbit Determination Methods*. Master's thesis, Texas A & M University, 2016.（《Gibbs 与 Herrick-Gibbs 轨道确定方法的统计比较》，硕士论文）
