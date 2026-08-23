# 循环命令（For）
> 译自 GMAT R2026a 帮助文档 For.html

For —— 按指定次数执行一系列命令。

## 脚本语法

```
For Index = Start:[Increment:]End
    [script statement]
    ...
EndFor
```

## 描述

`For` 命令是一条控制逻辑语句，按指定次数执行一系列命令。命令参数必须采用以下形式之一：

`Index = Start:End`

该语法将 `Index` 从 `Start` 以步长 1 递增到 `End`，重复执行脚本语句，直到 `Index` 大于 `End`。如果 `Start` 大于 `End`，则脚本语句不执行。

`Index = Start:Increment:End`

该语法将 `Index` 从 `Start` 以步长 `Increment` 递增到 `End`：若 `Increment` 为正，重复执行脚本语句直到 `Index` 大于 `End`；若 `Increment` 为负，则直到 `Index` 小于 `End`。如果 `Start` 小于 `End` 且 `Increment` 为负，或者 `Start` 大于 `End` 且 `Increment` 为正，则脚本语句不执行。

**另请参见**：If、While

## 选项

| 选项 | 描述 |
|------|------|
| `Index` | for 循环的自变量。`Index` 按照由 `Start`、`Increment` 和 `End` 的值定义的等差数列计算。<br>接受的数据类型：`Variable`<br>允许的值：-∞ < `Index` < ∞<br>默认值：名为 `I` 的 `Variable`<br>是否必需：是<br>接口：GUI、脚本 |
| `Start` | `Index` 参数的初始值。<br>接受的数据类型：参数（parameter）<br>允许的值：-∞ < `Start` < ∞<br>默认值：1<br>是否必需：是<br>接口：GUI、脚本 |
| `Increment` | `Increment` 参数用于计算循环 Index 的等差数列，使得第 i 次循环的取值为 **Start + i*Increment**，前提是该结果值满足由 `End` 定义的约束。<br>接受的数据类型：参数（parameter）<br>允许的值：-∞ < `Increment` < ∞<br>默认值：1<br>是否必需：否<br>接口：GUI |
| `End` | `End` 参数是 `Index` 的上界（若 `Increment` 为负则为下界）。<br>接受的数据类型：参数（parameter）<br>允许的值：-∞ < `End` < ∞<br>默认值：10<br>是否必需：是<br>接口：GUI、脚本 |

## GUI

> [图：For 命令的 GUI 面板]

`For` 命令的 GUI 面板包含其所有参数的字段：`Index`、`Start`、`Increment` 和 `End`。要编辑这些值，点击你想更改的字段值并输入新值（例如 **5**、**anArray(1,5)** 或 **Spacecraft.X**）。或者，你可以右键点击字段值，或点击字段左侧的省略号（`…`）按钮。这会显示 `ParameterSelectDialog` 窗口，允许你从列表中选择一个参数。

> [图：ParameterSelectDialog 参数选择窗口]

## 备注

`Index`、`Start`、`Increment` 和 `End` 参数的值可以是以下任一类型：

- 字面数值（例如 1、15.2、-6）
- `Variable` 资源
- `Array` 资源元素
- 数值类型的资源参数（例如 `Spacecraft`.`X`、`ChemicalThruster`.`K1`）

并有一条额外要求：如果 `Index` 使用资源参数，该参数必须是可设置的（settable）。

索引规格不能包含数学运算符或括号。`For` 循环执行完毕后，`Index` 的值保留为最后一次循环迭代的值。如果循环没有执行，`Index` 的值保持为遇到循环之前的值。

在 `For` 循环内部对索引变量所做的修改会被 `For` 循环语句覆盖。例如，以下代码片段：

```
For I = 1:1:3
    I = 100
    Report aReport I
EndFor
```

的输出为：

```
100
100
100
```

说明：虽然循环体内把 I 改成 100 并输出（故每次打印 100），但下一次迭代时 For 语句会按等差数列重新设置 I，覆盖循环体内的修改。

在循环内部对 `Start`、`Increment` 和 `End` 参数所做的修改不会影响循环的行为。例如，以下代码片段：

```
J = 2
K = 2
L = 8
For I = J:K:L
    J = 1
    K = 5
    L = 100
    Report aReport I
EndFor
```

的输出为：

```
2
4
6
8
```

说明：循环的 Start/Increment/End 在进入循环时已确定为 2:2:8，循环体内对 J、K、L 的修改不影响本次循环，因此 I 依次取 2、4、6、8。

## 示例

将航天器传播到远地点 3 次：

```
Create Spacecraft aSat
Create Propagator aPropagator
Create Variable I

BeginMissionSequence

For I = 1:1:3
    Propagate aPropagator(aSat, {aSat.Apoapsis})
EndFor
```

说明：循环变量 I 从 1 到 3，每次迭代把 aSat 传播到下一个远地点（Apoapsis），共执行 3 次。

对数组进行索引：

```
Create Variable I J
Create Array anArray[10,5]
BeginMissionSequence

For I = 1:10
    For J = 1:5
        anArray(I,J) = I*J
    EndFor
EndFor
```

说明：嵌套 For 循环遍历 10×5 数组的每个元素，将元素 (I,J) 赋值为 I*J，即生成一个乘法表。
