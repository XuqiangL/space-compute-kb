# 第 9 章 基于多重打靶法的最优月球飞掠（Optimal Lunar Flyby using Multiple Shooting）
> 译自 GMAT R2026a 帮助文档 OptimalLunarFlyby.html

| 项目 | 内容 |
| --- | --- |
| 适用读者（Audience） | 高级 |
| 时长（Length） | 90 分钟 |
| 先修要求（Prerequisites） | 完成“轨道仿真”“简单轨道转移”“火星 B 平面目标求解”教程，并参加过 GMAT 基础培训课程或观看过相关视频 |
| 脚本文件（Script File） | `Tut_MultipleShootingTutorial_Step1.script`、`Tut_MultipleShootingTutorial_Step2.script` …… `Tut_MultipleShootingTutorial_Step5.script` |

## 本章目录

- 目标与概述（本节）
- [配置坐标系、航天器、优化器、传播器、机动、变量与图形](ch09s02.md)
- [配置任务序列](ch09s03.md)：任务序列概览；定义初始猜测；初始化变量；Vary 并设置航天器历元；Vary 控制点状态；施加控制点约束；传播各弧段；计算并施加拼接约束；施加拼接点约束；施加任务轨道约束；施加代价函数
- [设计轨道](ch09s04.md)：概述；第 1 步验证配置；第 2 步寻找光滑轨道；第 5 步施加新约束

## 目标与概述（Objective and Overview）

> **注意**
>
> 对于高椭圆地球轨道（HEO），利用月球引力来抬升近地点或进行轨道面改变，往往比使用航天器自身的推进资源更省。然而，要设计同时满足多项特定任务约束的月球飞掠（Lunar Flyby）并非易事，需要借助现代优化技术，在最小化燃料消耗的同时满足轨道约束。在本教程中，你将学习如何通过编写 GMAT 脚本执行多重打靶（Multiple Shooting）优化来设计飞掠轨道。作为分析人员，你的目标是设计一次月球飞掠，使任务轨道的近地点达到 15 倍地球半径，并将任务轨道的倾角改变为 10 度。（注：还有其他任务约束，下文将更详细地讨论。）
>
> 为了高效求解该问题，我们将采用多重打靶法（Multiple Shooting Method），把敏感的边值问题分解为若干更小、更不敏感的子问题。我们将使用三段轨道弧段：第一段从转移轨道进入（Transfer Orbit Insertion，TOI）开始向前传播；第二段以月球近心点（lunar periapsis）为中心，同时向前和向后传播；第三段以任务轨道进入（Mission Orbit Insertion，MOI）为中心，向前和向后传播。见图 1 和图 2，它们展示了最终轨道解以及用于求解该问题的“控制点（Control Points）”和“拼接点（Patch Points）”。

本教程首先从解的若干视图开始，以建立对问题的物理直观理解。在图 1 中展示了一次月球飞掠的示意：轨迹以红色显示，月球轨道以黄色显示，地球位于画面中心。我们要求在 TOI 处满足以下约束：

1. 航天器位于轨道近地点；
2. 航天器高度为 285 km；
3. 转移轨道倾角为 28.5 度。

在月球飞掠处，我们仅要求飞掠高度大于 100 km。该约束是隐式满足的，因此我们不会在脚本中显式写出这一约束。月球飞掠之后，在地球近地点执行一次进入机动，进入任务轨道。MOI 之后必须满足以下约束：

1. 任务轨道近地点为 15 倍地球半径；
2. 任务轨道远地点为 60 倍地球半径；
3. 任务轨道倾角为 10 度。

注：（与月球的相位关系对这类轨道很重要，但月球相位设计考量超出本教程范围。）

> [图 9.1：从地球赤道法线方向看月球飞掠（View of Lunar Flyby from Normal to Earth Equator）]

> [图 9.2：月球飞掠几何视图（View of Lunar Flyby Geometry）]

下图展示了任务时间线以及控制点和拼接点的定义方式。控制点用实心蓝圆表示，定义为将航天器状态作为优化变量处理的位置；拼接点用空心蓝圆表示，定义为强制位置和/或速度连续的位置。在本教程中，我们在 TOI、月球飞掠和 MOI 处放置控制点。在每个控制点处，6 个笛卡尔状态量和历元都作为优化变量，共 18 个优化变量。在 MOI 控制点处，还有一个额外的优化变量——用于进入任务轨道的速度增量 delta V（沿速度方向）。

> [图 9.3：控制点与拼接点的定义（Definition of Control and Patch Points）]

注意，虽然只有 3 个控制点，但我们有 5 段弧段（因此需要 5 个航天器）。定义为控制点的月球飞掠处的状态，会向后传播到一个拼接点、向前传播到一个拼接点；MOI 控制点也是如此。要设计这条轨道，你需要创建以下 GMAT 资源：

1. 创建一个月心坐标系。
2. 创建建模各弧段所需的 5 个航天器。
3. 创建一个地心传播器和一个月心传播器。
4. 创建一个脉冲机动。
5. 创建脚本中使用的众多用户变量。
6. 创建一个 VF13ad 优化器。
7. 创建用于跟踪优化过程的图。

使用脚本片段创建资源之后，你将用 GMAT 脚本构建优化序列。优化序列的伪代码如下所示：

```
Define optimization initial guesses
Initialize variables
Optimize
      Loop initializations
      Vary control point epochs
      Set epochs on spacecraft
      Vary control point state values
      Configure/initialize spacecraft 
      Apply constraints on initial control points (i.e before propagation)
      Propagate spacecraft
      Apply patch point constraints
      Apply constraints on mission orbit
      Apply cost function
EndOptimize
```

**伪代码说明：** 这段伪代码描述了多重打靶优化的整体流程——先定义优化初始猜测值并初始化变量；然后进入 `Optimize`/`EndOptimize` 优化循环：在循环内先做循环初始化，接着用 `Vary` 声明控制点历元与控制点状态为优化变量，并把历元设置到各航天器上、完成航天器配置/初始化；随后对初始控制点（即传播之前）施加约束，传播航天器，再施加拼接点约束（保证弧段间状态连续）、任务轨道约束，最后施加代价函数（cost function），由优化器迭代求解。

构建好基本优化序列之后，我们将执行以下步骤：

1. 运行该序列并分析初始猜测。
2. 运行优化器，仅满足拼接点约束。
3. 打开任务轨道约束，寻找一个可行解。
4. 以可行解作为初始猜测，寻找最优解。
5. 在月球轨道近心点处施加高度约束。
