# 非线性约束（NonlinearConstraint）

> 译自 GMAT R2026a 帮助文档 NonlinearConstraint.html

**NonlinearConstraint** —— 指定优化期间使用的约束，并可选择性地指定检查物理约束值时使用的容差。

## 脚本语法

```
NonlinearConstraint OptimizerName ({逻辑表达式})
或
NonlinearConstraint OptimizerName ({逻辑表达式}, {Tolerance=Arg})
```

## 描述

`NonlinearConstraint` 命令在 `Optimize`/`EndOptimize` 优化序列内使用，用于施加线性或非线性约束。

当支持的优化器通过 `CheckPhysicalTolerances` 设置开启物理约束值检查时，`NonlinearConstraint` 上的 `Tolerance` 设置会为该特定约束设定所用的容差，在物理约束检查期间覆盖优化器的 `FeasibilityTolerance` 设置。如果未指定 `Tolerance`，则对该约束使用 `FeasibilityTolerance`。

物理容差检查在优化器数学计算之外执行；约束的优化使用为优化器定义的算法执行。

注意：`Tolerance` 设置与实现了 `CheckPhysicalTolerances` 设置且该设置为 true 的优化器配合使用。VF13ad 和 SNOPT 优化器实现了此设置。

另请参阅：Vary（优化变量）、Optimize（优化）、Minimize（最小化）。

## 选项

| 选项 | 描述 |
|------|------|
| **LHS** | 允许你选择任何单元素的用户定义参数（数字除外）来定义约束变量。约束函数的形式为 LHS Operator RHS（左端 运算符 右端）。<br>• 接受的数据类型：String<br>• 允许值：Spacecraft 参数、数组元素、变量，或任何其他单元素的用户定义参数（数字除外）<br>• 默认值：`DefaultSC.SMA`<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **Operator** | 用于指定约束函数的逻辑运算符。约束函数的形式为 LHS Operator RHS。<br>• 接受的数据类型：Reference Array<br>• 允许值：`>=`、`<=`、`=`<br>• 默认值：`=`<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **OptimizerName** | 指定用于施加约束的求解器/优化器对象。<br>• 接受的数据类型：Reference Array<br>• 允许值：任何 `VF13ad` 或 `fminconOptimizer` 对象<br>• 默认值：`DefaultSQP`<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **RHS** | 允许你选择任何单元素的用户定义参数（包括数字）来指定约束变量的期望值。约束函数的形式为 LHS Operator RHS。<br>• 接受的数据类型：String<br>• 允许值：Spacecraft 参数、数组元素、变量，或任何其他单元素的用户定义参数（包括数字）<br>• 默认值：7000<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **Tolerance** | 指定约束的物理容差设置，覆盖优化器的 `FeasibilityTolerance` 设置。<br>• 接受的数据类型：String<br>• 允许值：Spacecraft 参数、数组元素、变量，或任何其他单元素的用户定义参数（包括数字）<br>• 默认值：1.0e-3<br>• 是否必需：否<br>• 接口：脚本 |

## GUI

如下图所示，在 Optimize/EndOptimize 序列内使用 `NonlinearConstraint` 命令来定义你希望在优化过程结束时满足的等式或不等式约束。

> [图：任务树中 Optimize 序列内的 NonlinearConstraint 命令]

双击 `NonlinearConstraint1` 弹出如下图所示的 `NonlinearConstraint` 命令对话框。

> [图：NonlinearConstraint 命令对话框界面]

你必须为上面的 `NonlinearConstraint` 命令对话框提供四个输入：

- 优化器（Optimizer）的选择。
- 约束（Constraint）对象。单击该字段右侧的 **Edit** 按钮，从三种可能的选择（`Spacecraft`、`Variable` 或 `Array`）中选择约束对象类型。
- 逻辑运算符。从三个选择 =、<= 或 >= 中选择一个。
- 约束值（Constraint Value）。

注意，输入 2-4 定义了一个逻辑表达式。在上面的示例中，我们有：`DefaultSC.SMA = 7000`。

## 备注

### 优化序列中 Vary、NonlinearConstraint 和 Minimize 命令的数量

一个优化序列必须包含一个或多个 `Vary` 命令。`Vary` 命令必须出现在任何 `Minimize` 或 `NonlinearConstraint` 命令之前。

允许多个 `NonlinearConstraint` 命令。每个约束恰好对应一个 `NonlinearConstraint` 命令。

一个 `Optimize/EndOptimize` 优化序列可以不含 `NonlinearConstraint` 命令。在这种情况下，由于每个优化序列必须包含 (a) 一个或多个 `NonlinearConstraint` 命令，和/或 (b) 单个 `Minimize` 命令，因此该优化序列必须包含单个 `Minimize` 命令。

### 命令交互

`Minimize` 命令仅在 `Optimize/EndOptimize` 优化序列内使用。使用 `NonlinearConstraint` 命令的完整示例请参阅 Optimize（优化）命令文档。

| 命令 | 描述 |
|------|------|
| `Optimize` 命令 | `NonlinearConstraint` 命令只能出现在 `Optimize/EndOptimize` 命令序列内。 |
| `Vary` 命令 | 每个优化序列必须包含至少一个 `Vary` 命令。`Vary` 命令用于定义与优化序列关联的控制变量。 |
| `Minimize` 命令 | `Minimize` 命令在优化序列内使用，用于定义将被最小化的目标函数。注意，一个优化序列最多允许包含一个 `Minimize` 命令。（优化序列不要求必须包含 `Minimize` 命令。） |

## 示例

```
% Constrain SMA of Sat to be 7000 km, using SQP1
NonlinearConstraint SQP1( Sat.SMA = 7000 )

% Constrain SMA of Sat to be less than or equal to 7000 km,
% using SQP1
NonlinearConstraint SQP1( Sat.SMA <= 7000 )

% Constrain the SMA of Sat to be greater than or equal to 7000 km,
% using VF13ad1
NonlinearConstraint VF13ad1( Sat.SMA >= 7000 )

% Constrain SMA of Sat to be within 10 km of 7000 km, using SNOPT1
NonlinearConstraint SNOPT1( Sat.SMA = 7000, {Tolerance = 10.0} )
```

上述脚本：分别演示用 SQP1 将 Sat 的半长轴约束为 7000 km、用 SQP1 约束半长轴不超过 7000 km、用 VF13ad1 约束半长轴不小于 7000 km，以及用 SNOPT1 约束半长轴在 7000 km 附近 10 km 容差范围内。

如上所述，`NonlinearConstraint` 命令只出现在 `Optimize` 序列内。请参阅 Optimize（优化）命令帮助中展示 `NonlinearConstraint` 命令用法的完整示例。
