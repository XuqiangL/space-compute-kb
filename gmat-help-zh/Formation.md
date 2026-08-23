# 编队（Formation）

> 译自 GMAT R2026a 帮助文档 Formation.html

**Formation** —— 一组航天器的集合。

## 描述

**Formation**（编队）资源允许你将多艘航天器组合到一个"容器"对象中，随后 GMAT 的传棒子系统会把这组航天器作为一个耦合动力系统来建模。你只能使用数值积分器类型的传播器来传棒 **Formation** 资源。该资源不能在任务序列（Mission Sequence）中被修改。

**另请参阅**：Propagate、Color

## 字段

| 字段 | 描述 |
|------|------|
| **Add** | 向 **Formation** 中添加一组 **Spacecraft**（航天器）。该列表不能为空。<br><br>**数据类型**：资源数组（Resource array）<br>**允许取值**：航天器组成的数组<br>**访问方式**：set（仅可设置）<br>**默认值**：空列表<br>**单位**：N/A<br>**接口**：GUI、脚本 |

## GUI

要创建一个简单的 **Formation** 并配置其中的 **Spacecraft**，请在**资源树（Resource Tree）**中执行以下操作：

1. 右键单击 **Spacecraft** 文件夹，选择 **Add Spacecraft**。
2. 右键单击 **Formations** 文件夹，选择 **Add Formation**。
3. 双击 **Formation1** 打开其对话框。
4. 单击右箭头按钮两次，将 **DefaultSC** 和 **Spacecraft1** 添加到 **Formation1** 中。
5. 单击 **Ok**。

> [图：Formation 资源的 GUI 配置对话框]

> **注意**：一艘 **Spacecraft** 只能被加入到一个 Formation 中。

## 备注

**Formation** 是一种容器对象，允许你将一组 **Spacecraft** 作为耦合系统来建模。你可以使用 **Add** 字段将 **Spacecraft** 添加到 **Formation** 中，如下面的脚本示例或上面的 GUI 示例所示。使用 **Formation** 资源的主要原因有两个：(1) 简化多航天器的传棒；(2) 提高性能。你只能将一艘航天器加入到一个编队中，并且不能将一个编队加入另一个编队。GMAT 的传棒子系统将 **Formation** 建模为耦合动力系统。一旦航天器被加入到 **Formation** 中，你只需在 **Propagate** 命令语句中包含该编队，即可轻松传棒其中的所有航天器，如下所示：

```
Propagate aPropagator(aFormation) {aSat1.ElapsedSecs = 12000.0}
```

上述脚本使用传播器 `aPropagator` 对编队 `aFormation` 进行传棒，直到 `aSat1` 的已流逝秒数达到 12000.0 秒。

你只能使用数值积分器类型的传播器来传棒 **Formation** 资源。GMAT 不支持在传棒编队时传棒轨道状态转移矩阵（orbit state transition matrix）。

传棒 **Formation** 时，编队中所有航天器的历元（epoch）必须一致。GMAT 允许你单独传棒一艘已被加入到 **Formation** 中的 **Spacecraft**，如下所示：

```
aFormation.Add = {aSat1, aSat2}
Propagate aPropagator(aSat1) {aSat1.ElapsedSecs = 12000.0}
```

上述脚本先将 `aSat1` 和 `aSat2` 加入编队，然后单独传棒 `aSat1`。

然而，当传棒某个 **Formation** 时，如果编队中所有 **Spacecraft** 的历元不一致（容差为几微秒），**GMAT** 将抛出错误并停止执行。

### 设置编队资源中航天器的颜色

如果你想为嵌套在 **Formation** 资源中的航天器轨迹设置独特的颜色，请通过 **Spacecraft** 资源或 **Propagate** 命令来更改颜色。关于如何为 **Spacecraft** 资源和 **Propagate** 命令设置独特颜色的讨论和示例，请参阅 Color 文档。

## 示例

创建两艘 **Spacecraft**，将它们加入到一个 **Formation** 中，并传棒该 **Formation**。

```
Create Spacecraft aSat1 aSat2

Create Formation aFormation
aFormation.Add = {aSat1, aSat2}

Create Propagator aPropagator

BeginMissionSequence

Propagate aPropagator(aFormation) {aSat1.ElapsedSecs = 12000.0}
```

上述脚本创建两艘航天器 `aSat1` 和 `aSat2`，将它们加入编队 `aFormation`，然后使用传播器 `aPropagator` 对整个编队进行传棒，直到 `aSat1` 的已流逝时间达到 12000 秒。
