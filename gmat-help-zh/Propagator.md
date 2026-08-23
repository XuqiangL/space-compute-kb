# 传播器（Propagator）
> 译自 GMAT R2026a 帮助文档 Propagator.html

Propagator —— 传播器用于对航天器运动建模。

## 传播器组件概述

Propagator 是 GMAT 中用于对航天器运动建模的组件。GMAT 包含两种类型的传播器：数值积分器类型和星历类型。使用数值积分器类型的 Propagator 时，你可以在一组实现 Runge-Kutta 方法和预测-校正（predictor corrector）方法的数值积分器中进行选择。数值传播器还需要一个力模型（ForceModel）。此外，你可以配置 Propagator 使用 SPICE 内核，以及 Code500、STK 和 CCSDS 星历文件进行传播。本资源不能在任务序列（Mission Sequence）中修改。但是，你可以在任务中将一个 Propagator 整体赋值给另一个 Propagator（即 `myPropagator = yourPropagator`）。

GMAT 关于 Propagator 组件的文档分为以下几节：

- 数值传播器文档参见“数值传播器”一节
- SPICE 传播器文档参见“SPK 配置的传播器”一节
- Code500 星历传播器文档参见“Code500 星历配置的传播器”一节
- STK 星历传播器文档参见“STK 星历配置的传播器”一节
- CCSDS OEM 星历传播器文档参见“CCSDS OEM 星历配置的传播器”一节
- TLE 传播器文档参见“SPICESGP4 TLE 传播器”一节

**另请参阅**：[Spacecraft](Spacecraft.md) 和 [Propagate](Propagate.md)。有关为轨道确定配置传播器的特殊注意事项，请参见[用于轨道确定的传播器配置](NavPropagatorConfiguration.md)。

## 数值传播器（Numerical Propagator）

### 概述

使用数值积分器（而非星历传播器）的 Propagator 对象是 GMAT 中少数几个在脚本中和在 GUI 中配置方式不同的对象之一。在 GUI 中，你在同一个对话框中配置积分器和力模型设置。有关 GMAT 数值积分器的详细讨论以及性能和精度比较、使用建议，请参见下面的“备注”一节。本资源不能在任务序列中修改。但是，你可以在任务中进行整体对象赋值（即 `myPropagator = yourPropagator`）。

在脚本中工作时，你必须独立于 Propagator 单独创建 ForceModel 对象，并使用传播器对象上的“FM”字段指定力模型。详见本节后面的“示例”部分。

### 选项

#### Accuracy
积分步的期望精度阈值。GMAT 使用力模型上 `ErrorControl` 字段中选择的方法来确定积分误差的度量方式。对于每一步，积分器确保误差小于由 `ErrorControl` 度量所定义的精度阈值。

| 项目 | 内容 |
|------|------|
| 数据类型 | Real |
| 允许的值 | Real > 0 且 Real < 1 |
| 默认值 | 1e-11（ABM 积分器为 1e-10） |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### FM
标识积分器使用的力模型。如果未提供力模型，GMAT 使用带 4x4 重力模型的以地球为中心的传播器。

| 项目 | 内容 |
|------|------|
| 数据类型 | Resource reference（资源引用） |
| 允许的值 | ForceModel |
| 默认值 | N/A |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### InitialStepSize
积分器尝试的第一步的大小。

> **警告**：传播器参数的赋值顺序会影响结果。具体来说，必须先指定 `Type`，再指定 `InitialStepSize`，否则 `InitialStepSize` 将重置回默认值。

| 项目 | 内容 |
|------|------|
| 数据类型 | Real |
| 允许的值 | Real > 0.0001 |
| 默认值 | 60 |
| 单位 | 秒 |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### LowerError
积分误差的下界，用于确定何时增大步长。仅适用于 AdamsBashforthMoulton 积分器。

| 项目 | 内容 |
|------|------|
| 数据类型 | Real |
| 允许的值 | Real > 0 且 0 < LowerError < TargetError < Accuracy |
| 默认值 | 1e-13 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### MaxStep
允许的最大步长。

| 项目 | 内容 |
|------|------|
| 数据类型 | Real |
| 允许的值 | Real > 0 且 MinStep <= MaxStep |
| 默认值 | 2700 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### MaxStepAttempts
积分器为满足 `Accuracy` 字段定义的容差所尝试的次数。

| 项目 | 内容 |
|------|------|
| 数据类型 | Integer |
| 允许的值 | Integer >= 1 |
| 默认值 | 50 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### MinStep
允许的最小步长。

| 项目 | 内容 |
|------|------|
| 数据类型 | Real |
| 允许的值 | Real > 0 且 MinStep <= MaxStep |
| 默认值 | 0.001 |
| 单位 | 秒 |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### StopIfAccuracyIsViolated
如果由 `Accuracy` 定义的积分误差值未得到满足，则停止传播的标志。

| 项目 | 内容 |
|------|------|
| 数据类型 | Boolean |
| 允许的值 | true、false |
| 默认值 | true |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### TargetError
积分误差的标称界，用于在调整步长时设置目标积分精度。仅适用于 AdamsBashforthMoulton 积分器。

| 项目 | 内容 |
|------|------|
| 数据类型 | Real |
| 允许的值 | Real > 0 且 0 < LowerError < TargetError < Accuracy |
| 默认值 | 1e-11 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### Type
指定用于对航天器运动的时间演化建模的积分器或解析传播器。

> **警告**：传播器参数的赋值顺序会影响结果。具体来说，必须先指定 `Type`，再指定 `InitialStepSize`，否则 `InitialStepSize` 将重置回默认值。

| 项目 | 内容 |
|------|------|
| 数据类型 | Enumeration（枚举） |
| 允许的值 | PrinceDormand78、PrinceDormand853、PrinceDormand45、RungeKutta89、RungeKutta68、RungeKutta56、AdamsBashforthMoulton、SPK、CCSDS-OEM、Code500、STK |
| 默认值 | RungeKutta89 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

### GUI

> [图：嵌入式 Runge-Kutta 积分器的设置界面]

嵌入式 Runge-Kutta 积分器的设置。从 `Type` 菜单中选择所需的积分器。

> [图：Adams-Bashforth-Moulton 积分器的额外设置界面]

Adams-Bashforth-Moulton 积分器具有如图所示的额外设置。

### 备注

#### 使用数值积分器的最佳实践

后面一节中给出的比较数据表明，PrinceDormand78 积分器是 GMAT 中最好的通用积分器。如有疑问，请使用 PrinceDormand78 积分器，并将 `MinStep` 设置为零，以便积分器的自适应步长算法控制最小积分步长。下面是关于 GMAT 步长控制算法以及使用非零最小积分步长的危险的一些重要说明。AdamsBashforthMoulton 积分器是低阶积分器，我们仅建议在需要预测-校正算法时将其用于低精度分析。我们建议你研究本节后面记录的性能和精度分析，为你的应用选择数值积分器。你可能需要针对你的应用执行进一步的分析和比较。

> **注意**：GMAT 的默认误差计算模式是 `RSSStep`，这是一种比 `RSSState` 更严格的误差控制方法，而 `RSSState` 常被其他软件（如 STK）用作默认值。如果你将 `Accuracy` 设置为非常小的数（例如 1e-13），并将 `ErrorControl` 保持为 `RSSStep`，积分器性能将会很差，而轨道积分精度却几乎没有提高。为了在积分精度和性能之间找到最佳平衡，我们建议你针对所选积分器和应用对精度设置进行试验。你可以从相对较高的 `Accuracy` 设置（例如 1e-9）开始，每次降低一个数量级，并比较最终轨道状态，以确定在何处更小的 `Accuracy` 值会导致更长的传播时间而无法提供更精确的轨道解。

> **注意**：GMAT 允许你为数值积分器设置最小步长。给定 `MinimumStep` 设置后，可能无法达到所请求的 `Accuracy`。传播器标志 `StopIfAccuracyIsViolated` 决定了当 `Accuracy` 无法满足时的行为。如果 `StopIfAccuracyIsViolated` 为 true，当积分精度不满足时，GMAT 将抛出错误并停止执行。如果 `StopIfAccuracyIsViolated` 为 false，GMAT 只会抛出积分精度未满足的警告，但会继续传播轨道。

#### 数值积分器概述

下表详细描述了每个数值积分器。

| 选项 | 描述 |
|------|------|
| RungeKutta89 | 自适应步长、九阶 Runge-Kutta 积分器，具有八阶误差控制。系数由 J. Verner 推导。Verner 为 89 积分器开发了几组系数，我们选择了最稳健但不一定最高效的系数。 |
| PrinceDormand78 | 自适应步长、八阶 Runge-Kutta 积分器，具有七阶误差控制。系数由 Prince 和 Dormand 推导。 |
| PrinceDormand853 | 自适应步长、八阶 Runge-Kutta 积分器，具有五阶误差控制并包含三阶校正，如 Hairer、Norsett 和 Warner 所著《Solving Ordinary Differential Equations I: Nonstiff Problems》第 II.10 节所述。系数由 Prince 和 Dormand 推导。该积分器在宽松的 Accuracy 设置下表现出奇地好。 |
| PrinceDormand45 | 自适应步长、五阶 Runge-Kutta 积分器，具有四阶误差控制。系数由 Prince 和 Dormand 推导。 |
| RungeKutta68 | 二阶 Runge-Kutta-Nystrom 型积分器，系数由 Dormand、El-Mikkawy 和 Prince 开发。该积分器是 9 级 Nystrom 积分器，对因变量及其导数都进行误差控制。这个二阶实现可以正确积分非保守力，但不推荐用于此用途。数值比较请参见下面的积分器比较。你不能使用此积分器在有限机动期间积分质量，因为质量流率是一阶微分方程，不受此积分器支持。 |
| RungeKutta56 | 自适应步长、六阶 Runge-Kutta 积分器，具有五阶误差控制。系数由 E. Fehlberg 推导。 |
| AdamsBashforthMoulton | 四阶 Adams-Bashford 预测器 / Adams-Moulton 校正器，如 Bate、Mueller 和 White 所著《Fundamentals of Astrodynamics》所述。预测步使用当前状态和变量三个先前状态的导数信息外推变量的下一个状态。校正器使用为此状态评估的导数信息，连同原始状态和两个先前状态的导数信息，来调整此状态，给出最终的校正状态。ABM 积分器使用 RungeKutta89 积分器启动积分过程。ABM 是低阶积分器，不应用于精密应用或高度非线性应用（如天体飞越）。 |

#### 数值积分器的性能和精度比较

下表包含 GMAT 数值积分器的性能比较数据。第一张表显示了比较中包含的每个测试用例的轨道类型、动力学模型和传播时长。比较了五种轨道类型：近地轨道、Molniya（闪电轨道）、火星转移（2 型）、月球转移和有限推力机动（情况 1 为吹除式，情况 2 为压力调节式）。对于每个测试用例，轨道向前传播一段时长，然后向后传播回初始历元。表中的误差值是向前和向后传播到初始位置后最终位置的 RSS 差值。每种轨道类型的运行时间数据以该轨道类型运行时间最快的积分器为基准进行归一化。对于所有测试用例，`ErrorControl` 设置为 `RSSStep`。除 AdamsBashfourthMoulton 设置为 1e-11 外，所有积分器的 `Accuracy` 均设置为 1e-12，因为 AdamsBashfourthMoulton 在 `Accuracy` 设置为 1e-12 时性能较差。

| 轨道 | 动力学模型 | 时长 |
|------|-----------|------|
| LEO | 地球 20x20、太阳、月球、使用 MSISE90 密度的阻力、SRP | 1 天 |
| Molniya | 地球 20x20、太阳、月球、使用 Jacchia Roberts 密度的阻力、SRP | 3 天 |
| 火星转移 | 近地：地球 8x8、太阳、月球、SRP；深空：所有行星作为点质量摄动；近火星：火星 8x8、SRP | 333 天 |
| 月球转移 | 地球为中心天体，所有行星作为点质量摄动 | 5.8 天 |
| 有限推力机动（情况 1 和 2） | 点质量引力 | 7200 秒 |

比较每个积分器的运行时间数据（见下表）我们看到，PrinceDormand78 积分器在 6 个案例中的 4 个中最快，并在 LEO 测试案例中与 RungeKutta89 积分器并列。对于月球飞越案例，RungeKutta89 是最快的积分器，但在这种情况下，给定等效的 `Accuracy` 设置，PrinceDormand78 积分器的精度至少高 2 个数量级。请注意，AdamsBashforthMoulton 积分器对某些轨道有公里级误差，因为它是低阶积分器。

> [图：各积分器在不同轨道类型下的运行时间与精度比较表]

#### AdamsBashforthMoulton 积分器特有的字段

AdamsBashforthMoulton 积分器有两个额外的字段，名为 `TargetError` 和 `LowerError`，仅在 `Type` 设置为 AdamsBashforthMoulton 时才激活。如果你使用其他积分器类型，必须从脚本文件中删除这些字段以避免解析错误。在 GUI 中工作时，这是自动执行的。更多细节请参见下面的示例。

### 示例

使用通用 Runge-Kutta 积分器传播轨道：

```
Create Spacecraft aSat
Create ForceModel aForceModel

Create Propagator aProp
aProp.FM              = aForceModel
aProp.Type            = PrinceDormand78
aProp.InitialStepSize = 60
aProp.Accuracy        = 1e-011
aProp.MinStep         = 0
aProp.MaxStep         = 86400
aProp.MaxStepAttempts = 50
aProp.StopIfAccuracyIsViolated = true

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = .2}
```

使用定步长配置进行传播。通过将 `InitialStepSize` 设置为所需的固定步长并将 `ErrorControl` 设置为 `None` 来实现。本示例以 30 秒的恒定步长传播：

```
Create Spacecraft aSat
Create ForceModel aForceModel
aForceModel.ErrorControl = None

Create Propagator aProp
aProp.FM              = aForceModel
aProp.Type            = PrinceDormand78
aProp.InitialStepSize = 30

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = .2}
```

使用 Adams-Bashforth-Moulton 预测-校正积分器传播轨道：

```
Create Spacecraft aSat
Create ForceModel aForceModel
aForceModel.ErrorControl = RSSStep

Create Propagator aProp
aProp.FM              = aForceModel
aProp.Type            = AdamsBashforthMoulton
aProp.InitialStepSize = 60
aProp.MinStep         = 0
aProp.MaxStep         = 86400
aProp.MaxStepAttempts = 50
%  Note the following fields must be set with decreasing values!
aProp.Accuracy        = 1e-010
aProp.TargetError     = 1e-011
aProp.LowerError      = 1e-013
aProp.StopIfAccuracyIsViolated = true

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = .2}
```

**中文说明**：注意 ABM 积分器的 `Accuracy`、`TargetError`、`LowerError` 三个字段必须以递减的值设置（脚本注释原文：Note the following fields must be set with decreasing values!）。

## SPK 配置的传播器（SPK-Configured Propagator）

### 描述

SPK 配置的 Propagator 通过插值用户提供的 SPICE 内核来传播航天器。你通过将 `Type` 字段设置为 `SPK` 来配置 Propagator 使用 SPK 内核。SPK 内核和 `NAIFId` 在 Spacecraft 资源上定义。你使用 Propagate 命令控制传播，包括停止条件。本资源不能在任务序列中修改。但是，你可以在任务中进行整体对象赋值（即 `myPropagator = yourPropagator`）。

**另请参阅**：[Spacecraft](Spacecraft.md)、[Propagate](Propagate.md)

### 字段

#### CentralBody
传播的中央天体。此字段对 SPK、Code500、CCSDS-OEM 或 STK 传播器无效。

| 项目 | 内容 |
|------|------|
| 数据类型 | Resource reference（资源引用） |
| 允许的值 | 天体（Celestial body） |
| 默认值 | Earth |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### EpochFormat
仅用于 SPK、Code500、CCSDS-OEM 或 STK 传播器。`StartEpoch` 字段中包含的历元的格式。

| 项目 | 内容 |
|------|------|
| 数据类型 | Enumeration（枚举） |
| 允许的值 | A1ModJulian、TAIModJulian、UTCModJulian、TTModJulian、TDBModJulian、A1Gregorian、TAIGregorian、TTGregorian、UTCGregorian、TDBGregorian |
| 默认值 | A1ModJulian |
| 单位 | N/A，除非为 Mod Julian，在那种情况下为约化儒略日（Modified Julian Date） |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### StartEpoch
仅用于 SPK、Code500、CCSDS-OEM 或 STK 传播器。传播的初始历元。当提供历元时，该历元用作初始历元。当提供关键字 "FromSpacecraft" 时，起始历元继承自航天器。如果省略此参数或设置为 "EphemStart"，传播将从星历文件的开始处开始。

| 项目 | 内容 |
|------|------|
| 数据类型 | String |
| 允许的值 | "Gregorian：04 Oct 1957 12:00:00.000 <= Epoch <= 28 Feb 2100 00:00:00.000；Modified Julian：6116.0 <= Epoch <= 58127.5"、"EphemStart" 或 "FromSpacecraft" |
| 默认值 | "EphemStart" |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### StepSize
SPK、Code500、CCSDS-OEM 或 STK 传播器的步长。

| 项目 | 内容 |
|------|------|
| 数据类型 | Real |
| 允许的值 | Real > 0 |
| 默认值 | 300 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### Type
指定用于对航天器运动的时间演化建模的积分器或解析传播器。对于 SPK 文件星历传播器，指定 `SPK`。

| 项目 | 内容 |
|------|------|
| 数据类型 | Enumeration（枚举） |
| 允许的值 | PrinceDormand78、PrinceDormand45、RungeKutta89、RungeKutta68、RungeKutta56、BulirschStoer、AdamsBashforthMoulton、SPK、STK、CCSDS-OEM、Code500 |
| 默认值 | RungeKutta89 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

### GUI

> [图：星历传播器（SPK）配置界面]

要配置 Propagator 使用 SPK 文件，在 Propagator 对话框上，在 `Type` 菜单中选择 `SPK`。SPK 传播器有四个可配置字段：`StepSize`、`CentralBody`、`EpochFormat` 和 `StartEpoch`。请注意，更改 `EpochFormat` 设置会将输入历元转换为所选格式。你也可以在 `StartEpoch` 字段中输入 **FromSpacecraft**，Propagator 将使用 Spacecraft 的历元作为初始传播历元。

### 备注

要使用 SPK 配置的 Propagator，你必须在 Spacecraft 上指定 SPK 内核和 `NAIFId`，配置 Propagator 使用 SPK 文件（而非数值方法），并配置 Propagate 命令使用配置好的 SPK 传播器。下面的小节和示例详细讨论了这些内容。

#### 配置航天器 SPK 内核

要使用 SPK 配置的 Propagator，你必须将 SPK 内核添加到 Spacecraft 并定义航天器的 `NAIFId`。选定航天器的 SPK 内核可在[此处](http://naif.jpl.nasa.gov/naif/data_archived.html)获得。GMAT 随附了两个示例航天器 SPK 内核（GEOSat.bsp 和 MoonTransfer.bsp）用于示例目的。下面显示了如何通过脚本接口添加航天器内核的示例。

```
Create Spacecraft aSpacecraft
aSpacecraft.NAIFId               = -123456789
aSpacecraft.OrbitSpiceKernelName = {...
                                    '..\data\vehicle\ephem\spk\GEOSat.bsp'}
```

要通过 GUI 添加 Spacecraft SPK 内核：

1. 在 Spacecraft 对话框上，点击 SPICE 选项卡。
2. 在 SPK Files 列表下，点击 Add。
3. 浏览以找到并选择所需的 SPK 文件。
4. 重复以添加所有必要的 SPK 内核。
5. 在 NAIF ID 字段中，输入航天器整数 NAIF id 编号。注意：对于给定任务，如果航天器使用 SPK 传播器传播，每个航天器应具有唯一的 NAIF ID。

> [图：在 Spacecraft 对话框的 SPICE 选项卡中添加 SPK 内核]

你可以通过脚本向航天器添加多个内核，如下所示，其中文件 GEOSat1.bsp 和 GEOSat2.bsp 是仅用于示例目的的虚拟文件名，不随 GMAT 分发。在脚本中，你可以使用相对路径或绝对路径来定义 SPK 文件的位置。相对路径是相对于你本地安装的 GMAT bin 目录定义的。

```
Create Spacecraft aSpacecraft
aSpacecraft.OrbitSpiceKernelName ={'C:\MyDataFiles\GEOSat1.bsp',...
                                   'C:\MyDataFiles\GEOSat2.bsp'}
```

#### 配置 SPK 传播器

你可以在 Propagator 资源上定义 SPK 配置的 Propagator 的传播 `StartEpoch`，或从 Spacecraft 继承 `StartEpoch`。下面是一个脚本片段，显示如何从 Spacecraft 继承 `StartEpoch`。要使用 GUI 从 Spacecraft 继承 `StartEpoch`：

1. 打开 SPK 传播器对话框，
2. 在 `StartEpoch` 字段中，输入 **FromSpacecraft** 或从下拉菜单中选择 **FromSpacecraft**。

要在 Propagator 资源上显式定义 `StartEpoch`，请使用以下语法：

```
Create Propagator spkProp
spkProp.EpochFormat = 'UTCGregorian'
spkProp.StartEpoch  = '22 Jul 2014 11:29:10.811'

Create Propagator spkProp2
spkProp2.EpochFormat = 'TAIModJulian'
spkProp2.StartEpoch  = '23466.5'
```

如果省略 `StartEpoch`，传播将从星历文件的开始时间开始。要配置步长，请使用 `StepSize` 字段。

```
Create Propagator spkProp
spkProp.Type     = SPK
spkProp.StepSize = 300
```

#### 与 Propagate 命令的交互

SPK 配置的 Propagator 与 Propagate 命令的配合方式与数值传播器与 Propagate 命令的配合方式相同，但以下情况例外：

- 如果 Propagate 命令使用 SPK 传播器，那么你只能使用该传播器传播一个航天器。但是，你可以在单个 Propagate 命令中混合 SPK 传播器和数值传播器。
- SPK 配置的 Propagator 不会传播 STM 或计算轨道雅可比矩阵（A 矩阵）。

在下面的示例中，我们假定已预先配置了名为 `aSpacecraft` 的 Spacecraft 和名为 `spkProp` 的 Propagator。下面显示了使用 `spkProp` 将 `aSpacecraft` 传播到地球近拱点的示例命令。

```
Propagate spkProp(aSpacecraft) {aSpacecraft.Earth.Periapsis}
```

下面是一个演示如何使用 SPK 传播器向后传播的脚本片段。

```
Propagate BackProp spkProp(aSpacecraft) {aSpacecraft.ElapsedDays = -1.5}
```

#### 星历边界附近的行为

一般来说，星历插值在星历文件边界附近精度较低，出于这个和其他原因，我们建议提供超出你应用初始和最终历元的相当长时段的星历。在星历文件的开始或结束附近传播时，使用双精度算术可能会影响结果。例如，如果星历文件的初始历元为 TDBModJulian = 21545.00037249916，而你以 UTC Gregorian 指定 `StartEpoch`，则时间转换中的舍入误差和/或使用 Gregorian 格式（仅精确到毫秒）截断时间可能会导致请求的历元略微超出星历文件提供的范围。最好的解决方案是提供额外的星历数据，以避免边界处的时间问题以及更微妙的插值不良问题。

> **警告**：为了定位请求的停止条件，GMAT 需要包围停止条件函数的根。然后，GMAT 使用标准求根技术将停止条件定位到请求的精度。如果请求的停止条件位于星历数据的开始或结束处或附近，那么在不步出星历文件的情况下可能无法包围停止条件，这将抛出错误并停止执行。在这种情况下，你必须提供更多星历数据以定位所需的停止条件。

### 示例

使用 SPK 配置的 Propagator 传播 GEO 航天器。从航天器定义 `StartEpoch`。注意：SPK 内核 GEOSat.bsp 随 GMAT 分发。

```
Create Spacecraft aSpacecraft;
aSpacecraft.UTCGregorian = '02 Jun 2004 12:00:00.000'
aSpacecraft.NAIFId       = -123456789
aSpacecraft.OrbitSpiceKernelName = {'..\data\vehicle\ephem\spk\GEOSat.bsp'}

Create Propagator spkProp
spkProp.Type        = SPK
spkProp.StepSize    = 300
spkProp.CentralBody = Earth
spkProp.StartEpoch  = FromSpacecraft

Create OrbitView EarthView
EarthView.Add             = {aSpacecraft, Earth, Luna}
EarthView.ViewPointVector = [ 30000 -20000 10000 ]
EarthView.ViewScaleFactor = 2.5

BeginMissionSequence
Propagate spkProp(aSpacecraft) {aSpacecraft.TA = 90}
Propagate spkProp(aSpacecraft) {aSpacecraft.ElapsedDays = 2.4}
```

使用 SPK 配置的 Propagator 模拟月球转移。在 Propagator 上定义 `StartEpoch`。注意：SPK 内核 MoonTransfer.bsp 随 GMAT 分发。

```
Create Spacecraft aSpacecraft
aSpacecraft.NAIFId = -123456789
aSpacecraft.OrbitSpiceKernelName = {...
                          '..\data\vehicle\ephem\spk\MoonTransfer.bsp'}

Create Propagator spkProp
spkProp.Type = SPK
spkProp.StepSize = 300
spkProp.CentralBody = Earth
spkProp.EpochFormat = 'UTCGregorian'
spkProp.StartEpoch = '22 Jul 2014 11:29:10.811'

Create OrbitView EarthView
EarthView.Add = {aSpacecraft, Earth, Luna}
EarthView.ViewPointVector = [ 30000 -20000 10000 ]
EarthView.ViewScaleFactor = 30

BeginMissionSequence
Propagate spkProp(aSpacecraft) {aSpacecraft.ElapsedDays = 12}
```

## Code500 星历配置的传播器（Code500 Ephemeris-Configured Propagator）

### 描述

Code500 星历配置的 Propagator 通过插值或沿用户提供的 Code500 格式二进制星历文件步进来传播航天器。你通过将 `Type` 字段设置为 `Code500` 来配置 Propagator 使用 Code500 星历。Code500 星历文件在 `Spacecraft.EphemerisName` 资源上指定。用户使用 Propagate 命令控制传播，包括停止条件。本资源不能在任务序列中修改。但是，你可以在任务序列中进行整体对象赋值（即 `myPropagator = yourPropagator`）。

Propagator 的 `CentralBody` 选项不适用于 Code500 传播器，不应与 Code500 传播器类型一起使用。GMAT 将自动检测并使用星历文件的中央天体。应使用 Propagate 命令遍历星历文件。当尝试在星历文件边界之外传播时，GMAT 将抛出错误消息并终止。

Code500 星历文件是二进制格式文件。如 [EphemerisFile](EphemerisFile.md) 帮助中所述，GMAT 可以生成小端（little-endian）和大端（big-endian）二进制格式的 Code500 星历文件（通过 `EphemerisFile.OutputFormat`）。星历传播器可以读取任一端序格式的 Code500 星历文件。星历文件的端序格式将由 GMAT 自动检测。

**另请参阅**：[Spacecraft](Spacecraft.md)、[Propagate](Propagate.md)、[EphemerisFile](EphemerisFile.md)

### 字段

唯一适用于 Code500 星历传播器的 Propagator 字段是 `EpochFormat`、`StartEpoch`、`StepSize` 和 `Type`。

#### EpochFormat
仅用于 SPK、Code500、CCSDS-OEM 或 STK 传播器。指定 `StartEpoch` 字段中包含的历元的格式。

| 项目 | 内容 |
|------|------|
| 数据类型 | Enumeration（枚举） |
| 允许的值 | A1ModJulian、TAIModJulian、UTCModJulian、TTModJulian、TDBModJulian、A1Gregorian、TAIGregorian、TTGregorian、UTCGregorian、TDBGregorian |
| 默认值 | A1ModJulian |
| 单位 | N/A，除非为 Mod Julian，在那种情况下为约化儒略日（Modified Julian Date） |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### StartEpoch
仅用于 SPK、Code500、CCSDS-OEM 或 STK 传播器。指定传播的初始历元。当提供历元时，该历元用作初始历元。当提供关键字 **FromSpacecraft** 时，起始历元继承自航天器。如果省略此参数或设置为 "EphemStart"，传播将从星历文件的开始处开始。

| 项目 | 内容 |
|------|------|
| 数据类型 | String |
| 允许的值 | "Gregorian：04 Oct 1957 12:00:00.000 <= Epoch <= 28 Feb 2100 00:00:00.000；Modified Julian：6116.0 <= Epoch <= 58127.5"、"EphemStart" 或 "FromSpacecraft" |
| 默认值 | "EphemStart" |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### StepSize
Code500 传播器的步长。GMAT 在遍历星历文件时将使用此步长，无论星历的内部步长如何。GMAT 将根据需要在文件上的矢量之间执行插值。

| 项目 | 内容 |
|------|------|
| 数据类型 | Real |
| 允许的值 | Real > 0 |
| 默认值 | 300 |
| 单位 | 秒 |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### Type
指定用于对航天器运动的时间演化建模的积分器或解析传播器。对于 Code500 星历传播器，指定 `Code500`。

| 项目 | 内容 |
|------|------|
| 数据类型 | Enumeration（枚举） |
| 允许的值 | PrinceDormand78、PrinceDormand45、RungeKutta89、RungeKutta68、RungeKutta56、BulirschStoer、AdamsBashforthMoulton、SPK、CCSDS-OEM、Code500 |
| 默认值 | RungeKutta89 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

### GUI

> [图：Code500 星历传播器配置界面]

要从 GMAT GUI 配置 Propagator 使用 Code500 星历文件，请从资源树中选择并打开一个 Propagator。在 Integrator 类别中，从 `Type` 下拉框中选择 `Code500`。这将显示 Code500 传播器选项对话框。Code500 传播器显示四个字段——`StepSize`、`CentralBody`、`EpochFormat` 和 `StartEpoch`。请注意，更改 `EpochFormat` 设置会将输入历元转换为所选格式。你也可以在 `StartEpoch` 字段中输入 **FromSpacecraft**，Propagator 将使用 Spacecraft 的历元作为初始传播历元。`CentralBody` 字段显示给用户，但在积分器类型为 Code500 时未使用。

### 备注

目前没有 GUI 选项可将 Code500 星历文件分配给 Spacecraft 资源。你必须通过脚本在 `Spacecraft.EphemerisName` 参数上指定 Code500 星历文件。下面的小节提供了如何执行此操作的示例。

#### 配置航天器星历文件

一个航天器只能分配一个 Code500 星历。目前没有 GUI 选项可将 Code500 星历文件添加到航天器。要使用 Code500 星历配置的 Propagator，你必须在脚本中使用 `EphemerisName` 参数将 Code500 星历文件添加到 Spacecraft。GMAT 随附了一个示例航天器 Code500 星历（`sat_leo.ephem`，在 `data/vehicle/ephem/code500` 目录中）。此示例文件的跨度为 4/20/2015 00:00:00 到 4/30/2015 00:00:00。下面显示了如何将此星历分配给航天器的示例。相对路径是相对于你本地安装的 GMAT `bin` 目录定义的。

```
Create Spacecraft aSpacecraft

aSpacecraft.EphemerisName = '../data/vehicle/ephem/code500/sat_leo.ephem'

BeginMissionSequence
```

#### 配置 Code500 星历传播器

如果你已将星历文件分配给航天器，则配置传播器只需要在 Propagator 资源上分配 `Code500` 类型和所需的步长。传播的中央天体将是星历文件的中央天体。如果需要，你也可以在传播器上指定 `EpochFormat` 和 `StartEpoch`，以指定开始传播的初始历元。使用独立的 Propagate 命令（参见 [Propagate](Propagate.md)）传播到所需的起始历元也可以达到同样的效果。

```
Create Propagator Code500Prop

Code500Prop.Type     = 'Code500'
Code500Prop.StepSize = 60.

BeginMissionSequence
```

前面关于 SPK 传播器一节中关于与 Propagate 命令的交互以及星历边界附近的行为的相同备注也适用于 Code500 星历传播器。

### 示例

本示例使用 Code500 星历传播航天器，从航天器定义 `StartEpoch`。本示例中使用的星历文件包含在 GMAT 发行版中的所示位置。如果你将下面的代码复制并粘贴到新的 GMAT 脚本中，它将运行。

```
Create Spacecraft aSpacecraft

% Ephem file span is 4/20/2015 - 4/30/2015

aSpacecraft.EphemerisName = '../data/vehicle/ephem/code500/sat_leo.ephem'
aSpacecraft.DateFormat    = UTCGregorian
aSpacecraft.Epoch         = '22 Apr 2015 00:00:00.000'

Create Propagator Code500Prop

Code500Prop.Type       = 'Code500'
Code500Prop.StepSize   = 60.
Code500Prop.StartEpoch = 'FromSpacecraft'

Create ReportFile PropReport

PropReport.Filename     = 'EphemPropagator_Code500_ForwardProp.txt'
PropReport.WriteHeaders = True

BeginMissionSequence

While aSpacecraft.ElapsedDays <= 1

    Propagate Code500Prop(aSpacecraft)

    Report PropReport aSpacecraft.UTCGregorian aSpacecraft.TAIModJulian ...
        aSpacecraft.X aSpacecraft.Y aSpacecraft.Z ...
        aSpacecraft.VX aSpacecraft.VY aSpacecraft.VZ

EndWhile
```

**中文说明**：上述脚本将 Code500 星历文件 `sat_leo.ephem` 赋给航天器，配置 60 秒步长的 Code500 传播器，并在 While 循环中逐步传播，同时将状态写入报告文件。

另一个更详细的 Code500 星历传播器使用示例显示在 `samples\Navigation` 目录中提供的 `Ex_Code500_EphemerisCompare.script` 文件中。此脚本生成一份报告，显示两个不同的以地球为中心的 Code500 星历文件中轨道之间的差异（以 RIC 坐标表示）。

## STK 星历配置的传播器（STK Ephemeris-Configured Propagator）

### 描述

STK 星历配置的 Propagator 通过插值或沿用户提供的 STK 格式星历文件步进来传播航天器。你通过将 `Type` 字段设置为 `STK` 来配置 Propagator 使用 STK 星历。STK 星历文件使用 `Spacecraft.EphemerisName` 字段在 Spacecraft 资源上指定。用户使用 Propagate 命令控制传播，包括停止条件。本资源不能在任务序列中修改。但是，你可以在任务序列中进行整体对象赋值（即 `myPropagator = yourPropagator`）。

Propagator 的 `CentralBody` 选项不适用于 STK 传播器，不应与 STK 传播器类型一起使用。GMAT 将自动检测并使用星历文件的中央天体。应使用 Propagate 命令遍历星历文件。当尝试在星历文件边界之外传播时，GMAT 将抛出错误消息并终止。STK 传播器包含在步出文件跨度之前将航天器步进到星历边界的代码。

STK 星历文件是符合 Systems Tool Kit 星历 TimePosVel 规范的 ASCII 文件。如 [EphemerisFile](EphemerisFile.md) 帮助中所述，GMAT 可以使用 `EphemerisFile.OutputFormat` 字段生成 STK 星历文件。STK 传播器适用于 STK 格式的文件，从 STK 4.0 开始，或 GMAT STK 星历。

**另请参阅**：[Spacecraft](Spacecraft.md)、[Propagate](Propagate.md)、[EphemerisFile](EphemerisFile.md)

### 字段

唯一适用于 STK 星历传播器的 Propagator 字段是 `EpochFormat`、`StartEpoch`、`StepSize` 和 `Type`。

#### EpochFormat
仅用于 SPK、Code500、CCSDS-OEM 或 STK 传播器。指定 `StartEpoch` 字段中包含的历元的格式。

| 项目 | 内容 |
|------|------|
| 数据类型 | Enumeration（枚举） |
| 允许的值 | A1ModJulian、TAIModJulian、UTCModJulian、TTModJulian、TDBModJulian、A1Gregorian、TAIGregorian、TTGregorian、UTCGregorian、TDBGregorian |
| 默认值 | A1ModJulian |
| 单位 | N/A，除非为 Mod Julian，在那种情况下为约化儒略日（Modified Julian Date） |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### StartEpoch
仅用于 SPK、Code500、CCSDS-OEM 或 STK 传播器。指定传播的初始历元。当提供历元时，该历元用作初始历元。当提供关键字 **FromSpacecraft** 时，起始历元继承自航天器。如果省略此参数或设置为 "EphemStart"，传播将从星历文件的开始处开始。

| 项目 | 内容 |
|------|------|
| 数据类型 | String |
| 允许的值 | "Gregorian：04 Oct 1957 12:00:00.000 <= Epoch <= 28 Feb 2100 00:00:00.000；Modified Julian：6116.0 <= Epoch <= 58127.5"、"EphemStart" 或 "FromSpacecraft" |
| 默认值 | "EphemStart" |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### StepSize
传播器的步长。GMAT 在遍历星历文件时将使用此步长，无论星历的内部步长如何。GMAT 将根据需要在文件上的矢量之间执行插值。

| 项目 | 内容 |
|------|------|
| 数据类型 | Real |
| 允许的值 | Real > 0 |
| 默认值 | 300 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### Type
指定用于对航天器运动的时间演化建模的积分器或解析传播器。对于 STK 星历传播器，指定 `STK`。

| 项目 | 内容 |
|------|------|
| 数据类型 | Enumeration（枚举） |
| 允许的值 | PrinceDormand78、PrinceDormand45、RungeKutta89、RungeKutta68、RungeKutta56、BulirschStoer、AdamsBashforthMoulton、SPK、CCSDS-OEM、Code500、STK |
| 默认值 | RungeKutta89 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

### GUI

> [图：STK 星历传播器配置界面]

要从 GMAT GUI 配置 Propagator 使用 STK 星历文件，请从资源树中选择并打开一个 Propagator。在 Integrator 类别中，从 `Type` 下拉框中选择 `STK`。这将显示 STK 传播器选项对话框。STK 传播器显示四个影响传播的字段——`StepSize`、`CentralBody`、`EpochFormat` 和 `StartEpoch`。请注意，更改 `EpochFormat` 设置会将输入历元转换为所选格式。你也可以在 `StartEpoch` 字段中输入 **FromSpacecraft**，Propagator 将使用 Spacecraft 的历元作为初始传播历元。`CentralBody` 字段显示给用户，但在积分器类型为 STK 时未使用。

### 实现说明

默认情况下，位置插值使用 7 阶 Hermite-Newton 均差插值器执行，仅使用函数值数据（即位置插值的位置数据）。速度插值使用位置多项式的导数来生成插值。

对于分段星历，插值器在段边界处重新启动。如果星历段的点数少于 8 个，插值器通过包含用于插值的速度数据来激活位置插值的导数信息。插值器的阶数发生变化以匹配段中的点数（对于 n 个数据点，位置的阶数 = 2n - 1，速度的阶数 = n - 1）。第一次发生这种情况时，会在消息窗口中发布警告通知，指示速度插值的阶数。后续更改不会报告，但插值阶数将适应后续段中的点数。

使用停止条件传播可能会显示亚毫秒级的相关差异。

STK 星历文件可以通过设置时间上遥远的 Scenario Epoch，并使用文件中每个星历点的时间偏移进行补偿，来设置与文件中数据非常不同的星历历元。这可能会在传播中导致舍入问题，特别是在传播到星历末尾（或向后传播到开始）时。

### 备注

一个航天器只能分配一个 STK 星历。目前没有 GUI 选项可将 STK 星历文件分配给 Spacecraft 资源。你必须通过脚本在 `Spacecraft.EphemerisName` 参数上指定 STK 星历文件。下面的小节提供了如何执行此操作的示例。

GMAT 支持读取多种 STK 星历参考系，但有一些限制需要注意。下表显示了 GMAT 对读取 STK 星历参考系的支持状态，以及 STK 参考系与 GMAT 等效 CoordinateSystem Axes 之间的映射。下面未特别提及的任何 STK 参考系都不支持用于 STK 星历传播器。

| STK 参考系 | GMAT 轴 | 状态 |
|-----------|---------|------|
| J2000 | J2000 | 支持所有中央天体 |
| J2000_Ecliptic | MJ2000Ec | 仅支持太阳 |
| ICRF | ICRF | 支持所有中央天体 |
| TrueOfDate | TODEq | 仅支持地球 |
| Fixed | BodyFixed | 支持所有中央天体。月球固连系解释为月球主轴（PA）坐标系。目前不支持月球固连的平均地球/极轴（ME）坐标系。有关地球和其他中央天体的固连系解释的详细信息，请参见 [CelestialBody](CelestialBody.md) 备注。 |

#### 配置航天器星历文件

要使用 STK 星历配置的 Propagator，你必须将 STK 星历文件添加到 Spacecraft。GMAT 随附了一个示例航天器 STK 星历（`SampleSTKEphem.e`，在 `data/vehicle/ephem/stk` 目录中）。此示例文件的跨度为 1 Jan 2000 11:59:28.000 到 4 Jan 2000 11:59:28.000。下面显示了如何将此星历分配给航天器的示例。相对路径是相对于你本地安装的 GMAT `bin` 目录定义的。

```
Create Spacecraft aSpacecraft;

aSpacecraft.EphemerisName = '../data/vehicle/ephem/stk/SampleSTKEphem.e';

BeginMissionSequence;
```

#### 配置 STK 星历传播器

如果你已将星历文件分配给航天器，则配置传播器只需要在 Propagator 资源上分配 `STK` 类型和所需的步长。传播的中央天体将是星历文件的中央天体。如果需要，你也可以在传播器上指定 `EpochFormat` 和 `StartEpoch`，以指定开始传播的初始历元。使用独立的 Propagate 命令（参见 [Propagate](Propagate.md)）将航天器推进到所需的起始历元也可以达到同样的效果。

```
Create Propagator STKProp;

STKProp.Type     = 'STK';
STKProp.StepSize = 60;

BeginMissionSequence;
```

前面关于 SPK 传播器一节中关于与 Propagate 命令的交互以及星历边界附近的行为的相同备注也适用于 STK 星历传播器。

### 示例

本示例使用 STK 星历传播航天器，从航天器定义 `StartEpoch`。本示例中使用的星历文件包含在 GMAT 发行版中的所示位置。如果你将下面的代码复制并粘贴到新的 GMAT 脚本中，它将运行。

```
%----------------------------------------
%   Spacecraft
%----------------------------------------
Create Spacecraft STKSat;

STKSat.DateFormat    = UTCGregorian;
STKSat.Epoch         = '01 Jan 2000 12:00:00.000';
STKSat.EphemerisName = '../data/vehicle/ephem/stk/SampleSTKEphem.e';

%----------------------------------------
%   Propagator
%----------------------------------------

Create Propagator STKProp;

STKProp.Type        = STK;
STKProp.StepSize    = 60;
STKProp.CentralBody = Earth;
STKProp.EpochFormat = 'A1ModJulian';
STKProp.StartEpoch  = 'FromSpacecraft';

%----------------------------------------
%   Output 
%----------------------------------------

Create OpenFrameInterface OFI_View1;

OFI_View1.SolverIterations = Current;
OFI_View1.UpperLeft        = [ 0 0 ];
OFI_View1.Size             = [ 0 0 ];
OFI_View1.RelativeZOrder   = 0;
OFI_View1.Maximized        = false;
OFI_View1.Add              = {STKSat, Earth};


%----------------------------------------
%---------- Arrays, Variables, Strings
%----------------------------------------

Create Array initialState[6,1] finalState[6,1];

%----------------------------------------
% Miscellaneous variables.
%----------------------------------------

Create String initialEpoch finalEpoch;

%
%   Mission Sequence
%

BeginMissionSequence;

[initialEpoch, initialState, finalEpoch, finalState] = ...
   GetEphemStates('STK', STKSat, 'UTCGregorian', EarthMJ2000Eq);

STKSat.Epoch = initialEpoch;

While STKSat.ElapsedDays <= 1
      
   Propagate STKProp(STKSat);

EndWhile;
```

**中文说明**：上述脚本使用 `GetEphemStates` 函数读取 STK 星历的初始/最终历元和状态，将航天器历元设为星历初始历元，然后在 While 循环中用 STK 传播器逐步传播 1 天。本示例在 samples 目录中的 `Ex_STKEphemPropagation` 脚本中提供。

## CCSDS OEM 星历配置的传播器（CCSDS OEM Ephemeris-Configured Propagator）

### 描述

CCSDS-OEM 星历配置的 Propagator 通过插值或沿用户提供的 CCSDS OEM 格式星历文件步进来传播航天器。你通过将 `Type` 字段设置为 `CCSDS-OEM` 来配置 Propagator 使用 OEM 星历。OEM 星历文件使用 `Spacecraft.EphemerisName` 字段在 Spacecraft 资源上指定。用户使用 Propagate 命令控制传播，包括停止条件。本资源不能在任务序列中修改。但是，你可以在任务序列中进行整体对象赋值（即 `myPropagator = yourPropagator`）。

Propagator 的 `CentralBody` 选项不适用于 OEM 传播器，不应与 OEM 传播器类型一起使用。GMAT 将自动检测并使用星历文件的中央天体。应使用 Propagate 命令遍历星历文件。当尝试在星历文件边界之外传播时，GMAT 将抛出错误消息并终止。OEM 传播器包含在步出文件跨度之前将航天器步进到星历边界的代码。

OEM 星历文件是符合空间数据系统咨询委员会轨道数据消息标准（CCSDS 502.0-B-2）的 ASCII 文件。如 [EphemerisFile](EphemerisFile.md) 帮助中所述，GMAT 可以使用 `EphemerisFile.OutputFormat` 字段生成 OEM 星历文件。GMAT 目前仅支持 Version 1.0 OEM 星历文件。

**另请参阅**：[Spacecraft](Spacecraft.md)、[Propagate](Propagate.md)、[EphemerisFile](EphemerisFile.md)

### 字段

唯一适用于 OEM 星历传播器的 Propagator 字段是 `EpochFormat`、`StartEpoch`、`StepSize` 和 `Type`。

#### EpochFormat
仅用于 SPK、Code500、CCSDS-OEM 或 STK 传播器。指定 `StartEpoch` 字段中包含的历元的格式。

| 项目 | 内容 |
|------|------|
| 数据类型 | Enumeration（枚举） |
| 允许的值 | A1ModJulian、TAIModJulian、UTCModJulian、TTModJulian、TDBModJulian、A1Gregorian、TAIGregorian、TTGregorian、UTCGregorian、TDBGregorian |
| 默认值 | A1ModJulian |
| 单位 | N/A，除非为 Mod Julian，在那种情况下为约化儒略日（Modified Julian Date） |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### StartEpoch
仅用于 SPK、Code500、CCSDS-OEM 或 STK 传播器。指定传播的初始历元。当提供历元时，该历元用作初始历元。当提供关键字 **FromSpacecraft** 时，起始历元继承自航天器。如果省略此参数或设置为 "EphemStart"，传播将从星历文件的开始处开始。

| 项目 | 内容 |
|------|------|
| 数据类型 | String |
| 允许的值 | "Gregorian：04 Oct 1957 12:00:00.000 <= Epoch <= 28 Feb 2100 00:00:00.000；Modified Julian：6116.0 <= Epoch <= 58127.5"、"EphemStart" 或 "FromSpacecraft" |
| 默认值 | "EphemStart" |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### StepSize
传播器的步长。GMAT 在遍历星历文件时将使用此步长，无论星历的内部步长如何。GMAT 将根据需要在文件上的矢量之间执行插值。

| 项目 | 内容 |
|------|------|
| 数据类型 | Real |
| 允许的值 | Real > 0 |
| 默认值 | 300 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### Type
指定用于对航天器运动的时间演化建模的积分器或解析传播器。对于 OEM 星历传播器，指定 `CCSDS-OEM`。

| 项目 | 内容 |
|------|------|
| 数据类型 | Enumeration（枚举） |
| 允许的值 | PrinceDormand78、PrinceDormand45、RungeKutta89、RungeKutta68、RungeKutta56、BulirschStoer、AdamsBashforthMoulton、SPK、CCSDS-OEM、Code500、STK |
| 默认值 | RungeKutta89 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

### GUI

> [图：CCSDS OEM 星历传播器配置界面]

要从 GMAT GUI 配置 Propagator 使用 CCSDS OEM 星历文件，请从资源树中选择并打开一个 Propagator。在 Integrator 类别中，从 `Type` 下拉框中选择 `CCSDS-OEM`。这将显示 OEM 传播器选项对话框。OEM 传播器显示四个影响传播的字段——`StepSize`、`CentralBody`、`EpochFormat` 和 `StartEpoch`。请注意，更改 `EpochFormat` 设置会将输入历元转换为所选格式。你也可以在 `StartEpoch` 字段中输入 **FromSpacecraft**，Propagator 将使用 Spacecraft 的历元作为初始传播历元。`CentralBody` 字段显示给用户，但在积分器类型为 CCSDS-OEM 时未使用。

### 实现说明

默认情况下，位置插值使用 7 阶 Hermite-Newton 均差插值器执行，仅使用函数值数据（即位置插值的位置数据）。速度插值使用位置多项式的导数来生成插值。

对于分段星历，插值器在段边界处重新启动。如果星历段的点数少于 8 个，插值器通过包含用于插值的速度数据来激活位置插值的导数信息。插值器的阶数发生变化以匹配段中的点数（对于 n 个数据点，位置的阶数 = 2n - 1，速度的阶数 = n - 1）。第一次发生这种情况时，会在消息窗口中发布警告通知，指示速度插值的阶数。后续更改不会报告，但插值阶数将适应后续段中的点数。

使用停止条件传播可能会显示亚毫秒级的相关差异。

### 备注

目前没有 GUI 选项可将 OEM 星历文件分配给 Spacecraft 资源。你必须通过脚本在 `Spacecraft.EphemerisName` 参数上分配 OEM 星历文件。下面的小节提供了如何执行此操作的示例。

GMAT 支持读取多种 OEM 星历参考系。下表显示了 GMAT 对读取 OEM 星历参考系的支持状态，以及 OEM 参考系与 GMAT 等效 CoordinateSystem Axes 之间的映射。下面未特别提及的任何 OEM 参考系都不支持用于 OEM 星历传播器。

| OEM 参考系 | GMAT 轴 | 状态 |
|-----------|---------|------|
| EME2000 | MJ2000Eq | 支持所有中央天体 |
| TOD | TODEq | 仅支持地球 |
| GRC 或 TDR | BodyFixed | 仅支持地球 |

#### 配置航天器星历文件

一个航天器只能分配一个 OEM 星历。要使用 OEM 星历配置的 Propagator，你必须在脚本中使用 `EphemerisName` 参数将 CCSDS OEM 星历文件添加到 Spacecraft。GMAT 随附了一个示例航天器 CCSDS-OEM 星历（`SampleOEMEphem.oem`，在 `data/vehicle/ephem/ccsds` 目录中）。此示例文件的跨度为 1 Jan 2000 12:00:00.000 到 3 Jan 2000 12:00:00.000。下面显示了如何将此星历分配给航天器的示例。相对路径是相对于你本地安装的 GMAT `bin` 目录定义的。

```
Create Spacecraft aSpacecraft;

aSpacecraft.EphemerisName = '../data/vehicle/ephem/ccsds/SampleOEMEphem.oem';

BeginMissionSequence;
```

#### 配置 OEM 星历传播器

如果你已将星历文件分配给航天器，则配置传播器只需要在 Propagator 资源上分配 `CCSDS-OEM` 类型。传播的中央天体将是星历文件的中央天体。如果需要，你也可以在传播器上指定 `EpochFormat` 和 `StartEpoch`，以指定开始传播的初始历元。使用独立的 Propagate 命令（参见 [Propagate](Propagate.md)）将航天器推进到所需的起始历元也可以达到同样的效果。

```
Create Propagator OEMProp;

OEMProp.Type     = 'CCSDS-OEM';
OEMProp.StepSize = 60;

BeginMissionSequence;
```

前面关于 SPK 传播器一节中关于与 Propagate 命令的交互以及星历边界附近的行为的相同备注也适用于 OEM 星历传播器。

### 示例

本示例使用 OEM 星历传播航天器，从星历文件的开始处开始。本示例中使用的星历文件包含在 GMAT 发行版中的所示位置。如果你将下面的代码复制并粘贴到新的 GMAT 脚本中，它将运行。

```
%----------------------------------------
%   Spacecraft
%----------------------------------------

Create Spacecraft OEMSat;

OEMSat.EphemerisName = '../data/vehicle/ephem/ccsds/SampleOEMEphem.oem';

%----------------------------------------
%   Propagator
%----------------------------------------

Create Propagator OEMProp;

OEMProp.Type = 'CCSDS-OEM';

%----------------------------------------
%   Output 
%----------------------------------------

Create OpenFramesInterface OFI_View1;

OFI_View1.SolverIterations = Current;
OFI_View1.UpperLeft        = [ 0 0 ];
OFI_View1.Size             = [ 0 0 ];
OFI_View1.RelativeZOrder   = 0;
OFI_View1.Maximized        = False;
OFI_View1.Add              = {OEMSat, Earth};

%----------------------------------------
%   Mission Sequence
%----------------------------------------

BeginMissionSequence;

While OEMSat.ElapsedDays <= 1
      
   Propagate OEMProp(OEMSat);

EndWhile;
```

**中文说明**：上述脚本将 CCSDS OEM 星历文件赋给航天器，配置 OEM 传播器，并在 While 循环中逐步传播 1 天，同时使用 OpenFramesInterface 进行可视化。

## SPICESGP4 TLE 传播器（SPICESGP4 TLE Propagator）

### 描述

SPICESGP4 Propagator 通过使用 SPICE 对 SGP4 算法的实现来处理标准两行根数（Two-Line Element，TLE）中的数据，从而传播航天器。你通过将 `Type` 字段设置为 `SPICESGP4` 来配置 Propagator 使用 TLE 数据文件。TLE 数据使用 `Spacecraft.EphemerisName` 字段在 Spacecraft 资源上指定，且 `Spacecraft.Id` 字段匹配 TLE 中航天器的名称或匹配卫星目录编号。用户使用 Propagate 命令控制传播，包括停止条件。本资源可以在任务序列中修改，但在开始任务序列之前必须提供初始 TLE。但是，一旦任务序列开始，你可以更改 TLE 值。

Propagator 的 `CentralBody` 选项不适用于 TLE 传播器，不应与 TLE 传播器类型一起使用。TLE 格式按定义以地球为中央天体。

**另请参阅**：[Spacecraft](Spacecraft.md)、[Propagate](Propagate.md)

### 字段

唯一适用于 SPICESGP4 星历传播器的 Propagator 字段是 `StepSize` 和 `Type`。

#### StepSize
传播器的步长。GMAT 在传播 TLE 时将使用此步长。

| 项目 | 内容 |
|------|------|
| 数据类型 | Real |
| 允许的值 | Real > 0 |
| 默认值 | 300 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

#### Type
指定用于对航天器运动的时间演化建模的积分器或解析传播器。对于 TLE 传播器，指定 `SPICESGP4`。（译注：原文此处为 "Specify CCSDS-OEM for an OEM ephemeris propagator"，系原文档的笔误，此处应为 SPICESGP4。）

| 项目 | 内容 |
|------|------|
| 数据类型 | Enumeration（枚举） |
| 允许的值 | PrinceDormand78、PrinceDormand45、RungeKutta89、RungeKutta68、RungeKutta56、BulirschStoer、AdamsBashforthMoulton、SPK、CCSDS-OEM、Code500、STK、SPICESGP4 |
| 默认值 | RungeKutta89 |
| 单位 | N/A |
| 接口 | GUI、脚本 |
| 访问权限 | set |

### 实现说明

SPICESGP4 传播器由 SPICE 对 SGP4 算法的实现驱动。该方法基于 Vallado 等人在 2006 年论文《Revisiting Spacetrack Report #3》中发表的算法。

### 备注

目前没有 GUI 选项可将 TLE 分配给 Spacecraft 资源。你必须通过脚本在 `Spacecraft.EphemerisName` 参数上分配 TLE 文件。下面的小节提供了如何执行此操作的示例。默认情况下，航天器的初始历元将设置为 TLE 的初始值，但这可以通过定义 `Spacecraft.Epoch` 参数来更改。

#### 配置航天器星历文件

一个航天器只能分配一个 TLE 文件。要使用 SPICESGP4 类型的 Propagator，你必须在脚本中使用 `EphemerisName` 参数将 TLE 文件添加到 Spacecraft。GMAT 随附了一个示例航天器 TLE（`Ex_TLEPropagationTLE.otxt`，在 `samples/SupportFiles` 目录中）。TLE 中对象的名称应与使用 `Spacecraft.Id` 参数在脚本中设置的值相同。下面显示了如何将此 TLE 分配给航天器的示例。相对路径是相对于你本地安装的 GMAT `bin` 目录定义的。

```
Create Spacecraft aSpacecraft;

aSpacecraft.EphemerisName = '../samples/SupportFiles/Ex_TLEPropagationTLE.txt';
aSpacecraft.Id            = 'ExampleSat';

BeginMissionSequence;
```

#### 配置 SPICESPG4 星历传播器

如果你已将星历文件分配给航天器，则配置传播器只需要在 Propagator 资源上分配 `SPICESGP4` 类型。下面是一个脚本示例，演示如何创建步长为 60 秒的 `SPICESGP4` 类型 Propagator。

```
Create Propagator SPICESGP4Propagator;

SPICESGP4Propagator.Type     = 'SPICESGP4';
SPICESGP4Propagator.StepSize = 60;

BeginMissionSequence;
```

### 示例

本示例使用来自 TLE 的数据传播航天器，并将状态信息记录到报告文件。本示例中使用的文件包含在 GMAT 发行版中的所示位置。如果你将下面的代码复制并粘贴到新的 GMAT 脚本中，它将运行。

```
%----------------------------------------
%---------- Spacecraft
%----------------------------------------

Create Spacecraft ExampleSat;
ExampleSat.DateFormat    = UTCGregorian;
ExampleSat.EphemerisName = '../samples/SupportFiles/Ex_TLEPropagationTLE.txt';
ExampleSat.Id            = 'ExampleSat';

%----------------------------------------
%---------- Propagators
%----------------------------------------

Create Propagator TLEProp;
TLEProp.Type     = SPICESGP4;
TLEProp.StepSize = 300;

%----------------------------------------
%---------- Subscribers
%----------------------------------------

Create ReportFile rf;
rf.Filename = BasicPropagation.txt
rf.Add      = {ExampleSat.UTCGregorian, ExampleSat.X, ExampleSat.Y, ExampleSat.Z, ExampleSat.VX, ExampleSat.VY, ExampleSat.VZ}

%----------------------------------------
%---------- Mission Sequence
%----------------------------------------

BeginMissionSequence;

Propagate TLEProp(ExampleSat) {ExampleSat.ElapsedDays = 1.0};
```

**中文说明**：上述脚本将 TLE 文件赋给航天器并设置 `Id` 与 TLE 中对象名一致，配置 300 秒步长的 SPICESGP4 传播器，然后将航天器传播 1 天并把位置/速度状态写入报告文件。