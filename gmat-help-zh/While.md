# 循环命令（While）
> 译自 GMAT R2026a 帮助文档 While.html

While —— 当条件满足时重复执行一系列命令。

## 脚本语法

```
While logical expression
    [script statement]
    ...
EndWhile
```

## 描述

`While` 命令是一条控制逻辑语句，只要所提供的逻辑表达式的值为真，就重复执行一系列命令。逻辑表达式在每次循环迭代之前求值。如果表达式一开始即为假，循环永远不会执行。如果 while 循环为空，它会被跳过，并向用户发出一条警告消息。表达式的语法在脚本语言参考中描述。

**另请参见**：Script Language、For、If

## GUI

> [图：While 命令的 GUI 面板]

`While` 命令的 GUI 面板提供了一个表格，你可以在其中构建复杂的逻辑表达式。表格的行对应复合逻辑表达式中的各个关系表达式，列对应这些表达式的各个元素。第一行自动包含一条默认语句：

```
While DefaultSC.ElapsedDays < 1.0
```

第一行第一列包含 `While` 命令名的占位符，不可更改。其余每一行第一列包含将该行表达式与上一行连接起来的逻辑运算符（`&`、`|`）。要选择逻辑运算符，在表格中相应的框内双击或右键点击，选择窗口就会出现。点击正确的运算符并点击 `OK` 即可选中。

> [图：逻辑运算符选择窗口]

`Left Hand Side`（左侧）列包含每个单独关系表达式的左侧。双击单元格即可输入参数名。若要改为从参数选择列表中设置该值，可以点击要设置的单元格左侧的"…"，或右键点击单元格本身。此时会出现 `ParameterSelectDialog` 窗口，允许你选择一个参数。

> [图：ParameterSelectDialog 参数选择窗口]

`Condition`（条件）列包含连接表达式左右两侧的条件运算符（`==`、`~=`、`<` 等）。要选择关系运算符，在表格中相应的框内双击或右键点击，选择窗口就会出现。点击正确的运算符并点击 `OK` 即可选中。

> [图：关系运算符选择窗口]

最后，`Right Hand Side`（右侧）列包含表达式的右侧。该值的修改方式与 `Left Hand Side` 列相同。

完成后，点击 `Apply` 保存更改，或点击 `OK` 保存更改并关闭窗口。点击任一按钮时，命令都会被验证。

## 示例

传播航天器直到其达到预定高度，并在每次经过近地点时报告数据：

```
Create Spacecraft aSat
aSat.SMA = 6800
aSat.ECC = 0

Create ForceModel aForceModel
aForceModel.Drag.AtmosphereModel = MSISE90

Create Propagator aProp
aProp.FM = aForceModel

Create ReportFile aReport

BeginMissionSequence

While aSat.Altitude > 300
    Propagate aProp(aSat) {aSat.Periapsis}
    Report aReport aSat.TAIGregorian aSat.Altitude
EndWhile
```

说明：创建一颗圆轨道（SMA = 6800 km、ECC = 0）航天器，力模型使用 MSISE90 大气模型以模拟大气阻力衰减。`While` 循环在高度大于 300 km 时重复执行：每次迭代传播到下一个近地点，并向报告文件输出当前 TAI 公历时间和高度。随着大气阻力使轨道衰减，当高度降至 300 km 及以下时循环结束。
