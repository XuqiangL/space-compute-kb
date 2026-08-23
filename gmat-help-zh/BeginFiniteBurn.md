# 开始有限推力机动（BeginFiniteBurn）

> 译自 GMAT R2026a 帮助文档 BeginFiniteBurn.html

**BeginFiniteBurn** —— 对有限推力机动进行建模。

## 脚本语法

```
BeginFiniteBurn aFiniteBurn(aSpacecraft)

EndFiniteBurn aFiniteBurn(aSpacecraft)
```

其中 `aFiniteBurn` 为有限推力机动对象，`aSpacecraft` 为航天器对象。

## 描述

当施加 `BeginFiniteBurn` 命令时，将打开指定的 `FiniteBurn` 模型中给出的推力器配置。类似地，当施加 `EndFiniteBurn` 命令时，将关闭指定的 `FiniteBurn` 模型中的推力器配置。在 GMAT 执行 `BeginFiniteBurn` 命令之后，受 `FiniteBurn` 对象影响的航天器的所有传播都将在动力学中包含所配置的有限推力，直到对该配置执行 `EndFiniteBurn` 行为止。要施加非零的有限推力机动，必须在 `BeginFiniteBurn` 和 `EndFiniteBurn` 命令之间存在一个 `Propagate` 命令。

要施加 `BeginFiniteBurn` 和 `EndFiniteBurn` 命令，必须配置一个 `FiniteBurn` 对象。该对象需要配置 `ChemicalTank` 和 `ChemicalThruster` 模型。更详细的说明请参阅"备注"部分和下面的示例。

另请参阅：Spacecraft（航天器）、ChemicalThruster（化学推力器）、ChemicalTank（化学推进剂箱）、FiniteBurn（有限推力机动）。

## 选项

| 选项 | 描述 |
|------|------|
| **BeginFiniteBurn - Burn** | 指定由 `BeginFiniteBurn` 命令激活的 `FiniteBurn` 对象。<br>• 接受的数据类型：Reference Array<br>• 允许值：`FiniteBurn` 资源<br>• 默认值：`DefaultFB`<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **BeginFiniteBurn - SpacecraftList** | 指定受 `BeginFiniteBurn` 命令作用的 `Spacecraft`（目前该列表中只能有一个 `Spacecraft`）。`SpacecraftList` 中列出的 `Spacecraft` 将按照由 `Burn` 字段定义的 `FiniteBurn` 对象的配置激活推力器。<br>• 接受的数据类型：Reference Array<br>• 允许值：`Spacecraft` 对象<br>• 默认值：`DefaultSC`<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **EndFiniteBurn - Burn** | 指定由 `EndFiniteBurn` 命令停用的 `FiniteBurn` 对象。<br>• 接受的数据类型：Reference Array<br>• 允许值：`FiniteBurn` 对象<br>• 默认值：`DefaultFB`<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **EndFiniteBurn - SpacecraftList** | 指定受 `EndFiniteBurn` 命令作用的 `Spacecraft`（目前该列表中只能有一个 `Spacecraft`）。`SpacecraftList` 中列出的 `Spacecraft` 将按照由 `Burn` 字段定义的 `FiniteBurn` 对象的配置停用推力器。<br>• 接受的数据类型：`Spacecraft`<br>• 允许值：`Spacecraft` 资源<br>• 默认值：`DefaultSC`<br>• 是否必需：是<br>• 接口：GUI、脚本 |

## GUI

`BeginFiniteBurn` 和 `EndFiniteBurn` 命令对话框允许你通过指定应使用哪个有限推力机动模型以及应将有限推力机动施加到哪艘航天器上来实现有限推力机动。`BeginFiniteBurn` 和 `EndFiniteBurn` 的对话框如下图所示。

> [图：BeginFiniteBurn 命令对话框界面]

> [图：EndFiniteBurn 命令对话框界面]

使用 `Burn` 菜单选择用于机动的 `FiniteBurn` 模型。使用 `Spacecraft` 文本框选择有限推力机动的航天器。你可以在 Spacecraft 文本框中直接输入航天器名称，也可以单击 **Edit** 按钮，使用 `ParameterSelectDialog` 对话框选择航天器。

如果你在没有先创建 `FiniteBurn` 对象的情况下将 `BeginFiniteBurn` 命令或 `EndFiniteBurn` 命令添加到任务序列中，GMAT 将创建一个名为 `DefaultFB` 的默认 `FiniteBurn` 对象。但是，在运行任务之前，你需要配置 `FiniteBurn` 对象所需的 `ChemicalTank` 和 `ChemicalThruster` 对象。详细说明请参阅"备注"部分。
## 备注

### 配置有限推力机动

要在任务序列中使用 `BeginFiniteBurn` 和 `EndFiniteBurn` 命令，必须按照下面示例所示以及以下步骤配置一个 `FiniteBurn` 对象以及 `ChemicalTank` 和 `ChemicalThruster` 对象：

1. 创建并配置一个 `ChemicalTank` 模型。
2. 创建一个 `ChemicalThruster` 模型：
   a. 设置推力器的参数（方向、推力、比冲等）；
   b. 将 `ChemicalThruster` 配置为使用第 1 步中创建的 `ChemicalTank`。
3. 将前两步中创建的 `ChemicalTank` 和 `ChemicalThruster` 添加到 `Spacecraft`。
4. 创建一个 `FiniteBurn` 模型，并将其配置为使用第 2 步中创建的 `ChemicalThruster`。

### 推力器初始状态

当你配置 `Spacecraft`、`ChemicalTank`、`ChemicalThruster` 和 `FiniteBurn` 对象时，GMAT 会以推力器关闭的状态初始化这些对象，因此没有有限推力机动处于激活状态。如果要在传播期间施加有限推力机动，必须使用 `BeginFiniteBurn` 命令打开推力器。

> **警告**：注意：如果 GMAT 抛出错误消息 "Propagator Exception: MassFlow is not a known propagation parameter on DefaultSC"（传播器异常：MassFlow 不是 DefaultSC 上已知的传播参数），则说明你没有配置执行有限推力机动所需的全部模型。请参阅上面的详细说明和示例，配置 `EndFiniteBurn/BeginFiniteBurn` 命令所需的模型。

### BeginFiniteBurn 和 EndFiniteBurn 命令不是分支命令

`BeginFiniteBurn` 和 `EndFiniteBurn` 命令不是分支命令，这意味着 `BeginFiniteBurn` 命令可以在没有 `EndFiniteBurn` 命令的情况下存在（但是，这可能导致航天器模型中的所有燃料被耗尽）。有限推力机动期间燃料质量完全耗尽时的行为，请参阅 `ChemicalTank` 对象。

类似地，由于 `BeginFiniteBurn` 和 `EndFiniteBurn` 命令用于打开或关闭推力器，在脚本中多次施加同一命令而没有其逆命令，与施加一次的效果相同。换句话说，如果你这样做：

```
BeginFiniteBurn aFiniteBurn(aSat)
BeginFiniteBurn aFiniteBurn(aSat)
BeginFiniteBurn aFiniteBurn(aSat)
```

其效果与只施加一次 `BeginFiniteBurn` 命令相同。`EndFiniteBurn` 命令也是如此。

## 示例

在航天器真近点角介于 300 度和 60 度之间时执行有限推力机动。

```
%  Create objects
Create Spacecraft aSat
Create ChemicalThruster aThruster
Create ChemicalTank aTank
Create FiniteBurn aFiniteBurn
Create Propagator aPropagator

%  Configure the physical objects
aSat.Thrusters        = {aThruster}
aThruster.Tank        = {aTank}
aSat.Tanks            = {aTank}
aFiniteBurn.Thrusters = {aThruster}

BeginMissionSequence

%  Prop to TA = 300 then maneuver until TA = 60
Propagate aPropagator(aSat, {aSat.TA = 300})
BeginFiniteBurn aFiniteBurn(aSat)
Propagate aPropagator(aSat, {aSat.TA = 60})
EndFiniteBurn aFiniteBurn(aSat)
```

上述脚本：创建航天器、推力器、燃料箱、有限推力机动和传播器对象并建立挂载关系；先传播到真近点角 300 度，然后开启有限推力机动，传播到真近点角 60 度时结束机动。

执行一次沿速度方向的机动，推力器点火 2 分钟。

```
%  Create objects
Create Spacecraft aSat
Create ChemicalThruster aThruster
Create ChemicalTank aTank
Create FiniteBurn aFiniteBurn
Create Propagator aPropagator

%  Configure the physical objects
aThruster.CoordinateSystem = Local
aThruster.Origin = Earth
aThruster.Axes   = VNB
aThruster.ThrustDirection1 = 1
aThruster.ThrustDirection2 = 0
aThruster.ThrustDirection3 = 0

%  Configure the physical objects
aSat.Thrusters    = {aThruster}
aThruster.Tank    = {aTank}
aSat.Tanks        = {aTank}
aFiniteBurn.Thrusters = {aThruster}

BeginMissionSequence

%  Fire thruster for 2 minutes
BeginFiniteBurn aFiniteBurn(aSat)
Propagate aPropagator(aSat, {aSat.ElapsedSecs = 120})
EndFiniteBurn aFiniteBurn(aSat)
```

上述脚本：将推力器坐标系设为局部 VNB（原点为地球），推力方向取 X 分量（即沿速度方向）；任务序列中开启有限推力机动并传播 120 秒（2 分钟）后结束机动。
