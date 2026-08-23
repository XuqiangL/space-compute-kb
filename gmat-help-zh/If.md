# 条件命令（If）
> 译自 GMAT R2026a 帮助文档 If.html

If —— 有条件地执行一系列命令。

## 脚本语法

```
If logical expression
    [script statement]
    ...
EndIf
```

```
If logical expression
    [script statement]
    ...
Else
    [script statement]
    ...
EndIf
```

## 描述

`If` 命令是一条控制逻辑语句，当所提供的逻辑表达式的值为真时，执行一系列命令。逻辑表达式的语法在脚本语言参考中描述。

`If` 命令可以选择性地包含一个 `Else` 子句，用于定义当相关逻辑表达式为假时要执行的一系列命令。

**另请参见**：Script Language、For、While

## GUI

> [图：If 命令的 GUI 面板]

`If` 命令的 GUI 面板提供了一个表格，你可以在其中构建复杂的逻辑表达式。表格的行对应复合逻辑表达式中的各个关系表达式（最多 10 个），列对应这些表达式的各个元素。第一行自动包含一条默认语句：

```
If DefaultSC.ElapsedDays < 1.0
```

第一行第一列包含 `If` 命令名的占位符，不可更改。其余每一行第一列包含将该行表达式与上一行连接起来的逻辑运算符（`&`、`|`）。要选择逻辑运算符，在表格中相应的框内双击或右键点击以显示选择窗口，点击正确的运算符并点击 `OK` 即可选中。

> [图：逻辑运算符选择窗口]

`Left Hand Side`（左侧）列包含每个单独表达式的左侧。双击单元格即可输入参数名。若要改为从参数选择列表中设置该值，可以点击要设置的单元格左侧的"…"，或右键点击单元格本身。此时会出现 `ParameterSelectDialog` 窗口，允许你选择一个参数。

> [图：ParameterSelectDialog 参数选择窗口]

`Condition`（条件）列包含连接表达式左右两侧的条件运算符（`==`、`~=`、`<` 等）。要选择关系运算符，在表格中相应的框内双击或右键点击，选择窗口就会出现。点击正确的运算符并点击 `OK` 即可选中。

> [图：关系运算符选择窗口]

最后，`Right Hand Side`（右侧）列包含表达式的右侧。该值的修改方式与 `Left Hand Side` 列相同。

完成后，点击 `Apply` 保存更改，或点击 `OK` 保存更改并关闭窗口。点击任一按钮时，命令都会被验证。

## 示例

一个简单的 `If` 语句：

```
Create Spacecraft aSat
Create ForceModel aForceModel

Create Propagator aProp
aProp.FM = aForceModel

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1, aSat.Altitude = 300}
If aSat.Altitude < 301 & aSat.Altitude > 299
    % propagation stopped on altitude constraint
Else
    % propagation continued for 1 day
EndIf
```

说明：先将航天器 aSat 传播，停止条件为经过 1 天或高度降至 300 km（ whichever 先满足）；随后用 `If` 判断传播停止时的高度是否在 299–301 km 之间：若是，说明传播因高度约束而停止（执行 If 分支）；否则说明传播持续了整整 1 天（执行 Else 分支）。
