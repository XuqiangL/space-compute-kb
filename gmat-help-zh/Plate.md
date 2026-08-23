# 板件（Plate）
> 译自 GMAT R2026a 帮助文档 Plate.html

**Plate** —— 用于指定单个航天器表面（本体面板、太阳翼侧面或其他表面）的属性，用于高保真太阳光压（SRP）建模，包括镜面反射、漫反射和吸收效应。

## 描述

Plate 资源允许用户构建详细的航天器面积模型，用于更高保真度的太阳光压（SRP）建模。航天器通常建模为板件的集合；至少需要六块板件才能将航天器表示为长方体或箱体。您还可以指定板件来表示太阳翼或高增益天线等附属部件。这些板件可以建模为相对于航天器本体具有动态姿态，方法是将其指定为面向太阳（法向垂直于瞬时航天器-太阳矢量），或提供外部文件给出板件姿态随时间的变化。

组成模型的 Plate 资源集合通过 Spacecraft 的 AddPlates 字段指定到 Spacecraft 对象。每个 Plate 都有一个关联的 AreaCoefficient 参数，表示可在定轨中估计的修正因子。您可以为模型中的每个 Plate 估计单独的修正，也可以使用 Spacecraft 的 NPlateSRPEquateAreaCoefficients 参数选择将单个修正关联到一组板件。

另请参阅：Spacecraft Ballistic/Mass Properties（航天器弹道/质量特性）

## 字段

| 字段 | 描述 |
|------|------|
| **Area** | 板件的表面积。<br>数据类型：Real > 0；允许值：任意正实数；访问：set；默认值：1 m^2；单位：Meters^2；接口：脚本 |
| **AreaCoefficient** | 施加于板件面积的比例因子，通常用于估计板件模型中的误差。<br>数据类型：Real；允许值：Real > 0；访问：set；默认值：1.0；单位：无；接口：脚本 |
| **AreaCoefficientSigma** | AreaCoefficient 的先验不确定度。仅用于约束 AreaCoefficient 参数的估计。<br>数据类型：Real；允许值：Real > 0；访问：set；默认值：1e70；单位：无；接口：脚本 |
| **DiffuseFraction** | 板件的漫反射系数。<br>数据类型：实数；允许值：0 ≤ DiffuseFraction ≤ 1；访问：set；默认值：0；单位：无；接口：脚本 |
| **DiffuseFractionSigma** | DiffuseFraction 的先验不确定度。仅用于约束 DiffuseFraction 参数的估计。<br>数据类型：Real；允许值：Real > 0；访问：set；默认值：1e70；单位：无；接口：脚本 |
| **LitFraction** | 施加于板件面积的比例因子，用于指定板件被照亮（不在阴影中）的比例。此参数可用于建模航天器自遮挡，例如太阳翼在航天器本体侧面投下阴影的情况。<br>数据类型：Real；允许值：0 < LitFraction ≤ 1；访问：set；默认值：1.0；单位：无；接口：脚本 |
| **PlateNormal** | 板件表面法向量。当 Plate.Type 设为 FixedInBody 时，指定板件在航天器本体坐标系中的方向。<br>数据类型：Vector；允许值：非零三维矢量；访问：set；默认值：[1,0,0]；单位：无；接口：脚本 |
| **PlateNormalHistoryFile** | 板件表面法向量历史文件。当 Plate.Type 设为 File 时，指定板件的方向。<br>数据类型：String；允许值：有效的路径和文件名；访问：set；默认值：None；单位：不适用；接口：脚本 |
| **PlateX** | 板件位置在航天器本体坐标系中表达的 X 分量。<br>数据类型：Real；允许值：Real；访问：set、get；默认值：0；单位：Meters；接口：脚本 |
| **PlateY** | 板件位置在航天器本体坐标系中表达的 Y 分量。<br>数据类型：Real；允许值：Real；访问：set、get；默认值：0；单位：Meters；接口：脚本 |
| **PlateZ** | 板件位置在航天器本体坐标系中表达的 Z 分量。<br>数据类型：Real；允许值：Real；访问：set、get；默认值：0；单位：Meters；接口：脚本 |
| **SolveFors** | 板件的待估计参数列表。<br>数据类型：枚举；允许值：AreaCoefficient、DiffuseFraction、SpecularFraction；访问：set；默认值：空；单位：不适用；接口：脚本 |
| **SpecularFraction** | 板件的镜面反射系数。<br>数据类型：Real；允许值：0 ≤ SpecularFraction ≤ 1；访问：set；默认值：1；单位：无；接口：脚本 |
| **SpecularFractionSigma** | SpecularFraction 的先验不确定度。仅用于约束 SpecularFraction 参数的估计。<br>数据类型：Real；允许值：Real > 0；访问：set；默认值：1e70；单位：无；接口：脚本 |
| **Type** | 指定描述板件方向的方法。FixedInBody 板件的方向由 PlateNormal 矢量指定。File 板件的方向由 PlateNormalHistoryFile 指定。<br>SunFacing 板件的方向取为垂直于航天器-太阳矢量。SunFacing 板件的姿态由 GMAT 自动计算，如果板件是 SunFacing 板件，则忽略 PlateNormal 和 PlateNormalHistoryFile 参数。<br>数据类型：枚举；允许值：FixedInBody、SunFacing、File；访问：set；默认值：FixedInBody；单位：不适用；接口：脚本 |

## 备注

每块板件的太阳光压建模包括各板件镜面反射率、漫反射率和吸收的影响。每块板件的镜面、漫反射和吸收比例之和必须等于 1。在 Plate 资源中，用户指定镜面和漫反射系数；吸收比例为 1 减去镜面与漫反射比例之和的剩余部分。

### 板件法向历史文件格式

如果 Plate Type 设为 File，用户必须提供外部姿态历史文件，并在 Plate.PlateNormalHistoryFile 参数上指定。板件法向历史文件给出板件法向量随时间的变化。文件包含如下所述的头部。

| 关键字 | 是否必需 | 描述及支持的值 |
|------|------|------|
| Coordinate_System | 是 | 所含法向量的参考坐标系。可以是任何内置或用户自定义的惯性系，或 'FixedInBody'（使用航天器本体坐标系）。 |
| Interpolation_Method | 否 | 用于法向量的插值方法。目前仅支持线性插值（Linear）。 |
| Start_Epoch | 是 | 法向量表中时间的基准历元。要求的格式为 UTCGregorian 'DD Mon YYYY HH:MM:SS.SSS'。 |

头部之后是一系列记录，每行一条，给出自 Start_Epoch 起的时间（秒），随后是该时刻板件法向量的笛卡尔分量。示例文件如下所示。

```
Start_Epoch = '11 Jun 2019 00:00:00.000'
Coordinate_System = EarthMJ2000Eq
Interpolation_Method = Linear

   0.118      0.71134437  0.59768958  0.36980583
  60.118      0.70844298  0.64262126  0.29179866
 120.117      0.70342991  0.67911896  0.20972316
 180.118      0.69632195  0.70683245  0.12459387
 240.118      0.68720633  0.72550392  0.03730319
 300.118      0.67618273  0.73495324  -0.05119232
 360.118      0.6635059   0.73500373  -0.13974778
 420.118      0.64938672  0.72563809  -0.22747802
 480.117      0.63365791  0.70727707  -0.31342751
 540.118      0.6166704   0.67998056  -0.39666617
 600.118      0.59854485  0.64412315  -0.47628713
 660.118      0.57958926  0.60014396  -0.55127445
 720.118      0.55997495  0.54842962  -0.62100966
 780.117      0.5399806   0.48973174  -0.68453179
 840.117      0.51976556  0.42453172  -0.7413613
 900.117      0.49951296  0.35366998  -0.79082511
 960.117      0.47946796  0.27785984  -0.83240879
1020.118      0.45991923  0.19807528  -0.86558679
1080.118      0.44098414  0.11493292  -0.8901255
1140.118      0.42293817  0.02963382  -0.90567386
1200.117      0.40594474  -0.05701248 -0.91211756
1260.117      0.39029164  -0.14410621 -0.90934363
1320.117      0.37589181  -0.23056147 -0.89752257
1380.117      0.36306455  -0.31566225 -0.87666497
1440.118      0.35205587  -0.39829948 -0.84700306
```

说明：该文件头部指定基准历元为 2019-06-11 00:00:00 UTC，坐标系为 EarthMJ2000Eq，插值方法为线性插值；数据行每行包含自基准历元起的秒数和该时刻板件法向量的三个笛卡尔分量。

## 示例

本示例展示如何创建简单的单板件模型。在本例中，我们对航天器本体 X 面上单块板件的正反两面都进行建模。

```
Create Spacecraft SimSat;

%
%   N-Plate models
%

Create Plate PlusX MinusX;

PlusX.Type             = FixedInBody;
PlusX.PlateNormal      = [1.0, 0.0, 0.0];
PlusX.LitFraction      = 1.0;
PlusX.AreaCoefficient  = 1.0;
PlusX.Area             = 12;
PlusX.SpecularFraction = 1;
PlusX.DiffuseFraction  = 0;

MinusX.Type             = FixedInBody;
MinusX.PlateNormal      = [-1.0, 0.0, 0.0];
MinusX.LitFraction      = 1.0;
MinusX.AreaCoefficient  = 1.0;
MinusX.Area             = 12;
MinusX.SpecularFraction = 0.5;
MinusX.DiffuseFraction  = 0.1;

SimSat.AddPlates  = {PlusX, MinusX};
```

说明：本示例创建航天器 SimSat 和两块板件 PlusX、MinusX（分别代表本体 +X 面和 -X 面，法向分别为 [1,0,0] 和 [-1,0,0]，面积均为 12 m²，全照；PlusX 为纯镜面反射，MinusX 镜面反射 0.5、漫反射 0.1），最后通过 AddPlates 将两块板件挂接到航天器。
