# 第 10 章 使用 GMAT 函数进行火星 B 平面目标求解（Mars B-Plane Targeting Using GMAT Functions）
> 译自 GMAT R2026a 帮助文档 Tut_UsingGMATFunctions.html

| 项目 | 内容 |
| --- | --- |
| 适用读者（Audience） | 高级 |
| 时长（Length） | 75 分钟 |
| 先修要求（Prerequisites） | 完成[轨道仿真](SimulatingAnOrbit.md)、[简单轨道转移](SimpleOrbitTransfer.md)、[火星 B 平面目标求解](Mars_B_Plane_Targeting.md)，并对 B 平面及其在目标求解中的用法有基本了解 |
| 脚本与函数文件（Script and function Files） | `Tut_UsingGMATFunctions.script`、`TargeterInsideFunction.gmf` |

## 本章目录

- 目标与概述（本节）
- [配置贮箱、航天器属性、机动、传播器、微分修正器、坐标系与图形](ch10s02.md)：另含创建单个报告文件（ReportFile）与创建 GMAT 函数（GmatFunction）
- [配置任务序列](ch10s03.md)：创建启动第一个 Target 序列的命令；配置任务树以运行第一个 Target 序列；配置 Make Objects Global 命令；配置 Target Desired B-Plane Coord. From Inside Function 命令；配置 Report Parameters 命令
- [运行含第一个 Target 序列的任务](ch10s04.md)：创建并配置第二个 Target 序列（Mars Capture、Vary MOI.V、Apply MOI、Prop to Mars Apoapsis、Achieve RMAG）
- [运行含第一、第二个 Target 序列的任务](ch10s05.md)

## 目标与概述（Objective and Overview）

> **注意**
>
> 空间任务设计中最具挑战性的问题之一，是设计一条能让航天器进入目标行星极近邻域的行星际转移轨道。让航天器接近目标行星的一种可行方法是瞄准该行星的 B 平面（B-Plane）。B 平面是一个平面坐标系，可在引力辅助过程中用于目标求解。它可以被想象成一个附着在辅助天体上的靶标；此外，它必须与逼近双曲线的入射渐近线垂直。图 10.1“从垂直于 B 平面的视角看 **B 平面的几何**”和图 10.2“从垂直于轨道面的视角看 **B 矢量**”展示了从垂直于轨道面的视角看到的 B 平面与 B 矢量的几何关系。要深入了解 B 平面，请查阅 GMATMathSpec 文档。火星任务是使用 B 平面目标求解的一个很好的例子：通过执行一次瞄准火星 B 平面的轨道修正机动（TCM）即可将航天器送往火星；当航天器接近火星后，再执行一次轨道进入机动，即可被火星轨道捕获。

> [图 10.1：从垂直于 B 平面的视角看 B 平面的几何（Geometry of the B-Plane）]

> [图 10.2：从垂直于轨道面的视角看 B 矢量（The B-vector）]

在本教程中，我们将使用 GMAT 对一次火星任务进行建模，重点是如何使用 GMAT 函数（GMAT functions）。从一条相对于地球的外飞双曲线轨道出发，我们将执行一次 TCM 来瞄准火星 B 平面。接近火星后，我们将调整机动的大小，执行火星轨道进入（MOI），以获得一条倾角为 90 度的最终椭圆轨道。要达成这些任务目标，需要创建两个独立的目标求解序列。为了聚焦于这两个目标求解器的配置，我们将大量使用航天器、传播器和机动的默认配置。

第一个目标求解序列采用基于地球的速度（V）、法向（N）和副法向（B）方向的机动，并包含四段传播序列。VNB 方向机动的目的是瞄准 B 矢量的 BdotT 与 BdotR 分量：BdotT 的目标值为 0 km；BdotR 瞄准一个非零值，以生成倾角为 90 度的极轨道。BdotR 的目标值设为 -7000 km，以避免轨道与火星相交（火星半径约为 3396 km）。**整个第一个目标求解序列将在一个 GMAT 函数内部创建。** 在 `Mission`（任务）树中，该函数将通过 GMAT 的 `CallGmatFunction` 命令来调用。此外，我们还会在主脚本和函数内部，通过 GMAT 的 `Global` 命令将相关对象（如航天器、力模型、订阅器（subscribers）、脉冲机动等）声明为全局（global）。

第二个目标求解序列采用一次基于火星的反速度方向（-V）机动，并包含一段传播序列。这次反速度方向机动将在近火点处执行，其目的是通过瞄准远火点处位置矢量模长 12,000 km 来实现 MOI。与第一个目标求解序列不同，第二个目标求解序列不会在函数内部创建。

本教程的目的是演示如何创建、填充、调用 GMAT 函数，并将其作为实际任务设计的一部分来使用。在本教程中，我们刻意将整个第一个目标求解序列放进一个 GMAT 函数中；然后在任务树中调用并执行该函数，再在函数之外继续设计第二个目标求解序列。航天器、力模型、订阅器等关键对象将被声明为全局，以确保数据能够持续地绘制并报告给所有订阅器。

本教程的基本步骤如下：

1. 修改 `DefaultSC` 以定义航天器的初始状态。初始状态是一条相对于地球的外飞双曲线轨道。
2. 创建并配置一个 `Fuel Tank`（贮箱）资源。
3. 使用默认设置创建两个 `ImpulsiveBurn`（脉冲机动）资源。
4. 创建并配置三个 `Propagator`（传播器）：NearEarth、DeepSpace 和 NearMars。
5. 创建并配置 `DifferentialCorrector`（微分修正器）资源。
6. 创建并配置三个 `DefaultOrbitView`（轨道视图）资源，分别用于可视化地心、日心和火心轨迹。
7. 创建并配置单个 `ReportFile`（报告文件）资源，用于数据报告输出。
8. 创建并配置三个 `CoordinateSystem`（坐标系）：地心、日心和火心。
9. 创建并配置单个 `GmatFunction` 资源，该函数将在 `Mission`（任务）树中被调用和执行。
10. 在 GMAT 函数内部创建第一个 `Target` 序列，用于瞄准 B 矢量的 BdotT 与 BdotR 分量。
11. 创建第二个 `Target` 序列，通过瞄准远火点位置模长来实现 MOI。
12. 运行任务并分析结果。
