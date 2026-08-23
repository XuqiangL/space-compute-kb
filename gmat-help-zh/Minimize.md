# 最小化（Minimize）

> 译自 GMAT R2026a 帮助文档 Minimize.html

**Minimize** —— 定义要最小化的代价函数。

## 脚本语法

```
Minimize OptimizerName (ObjectiveFunction)
```

## 描述

`Minimize` 命令在 `Optimize`/`EndOptimize` 优化序列内使用，用于定义你想要最小化的目标函数。

另请参阅：Vary（优化变量）、NonlinearConstraint（非线性约束）、Optimize（优化）。

## 选项

| 选项 | 描述 |
|------|------|
| **ObjectiveFunction** | 指定优化器将尝试最小化的目标函数。<br>• 接受的数据类型：String<br>• 允许值：Spacecraft 参数、数组元素、变量，或任何其他单元素的用户定义参数（数字除外）<br>• 默认值：`DefaultSC.Earth.RMAG`<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **OptimizerName** | 指定使用哪个优化器来最小化代价函数。<br>• 接受的数据类型：Reference Array<br>• 允许值：任何 `VF13ad` 或 `fminconOptimizer` 资源<br>• 默认值：`DefaultSQP`<br>• 是否必需：是<br>• 接口：GUI、脚本 |

## GUI

如下图所示，在 `Optimize`/`EndOptimize` 优化序列内使用 `Minimize` 命令来定义你希望最小化的代价函数。

> [图：任务树中 Optimize 序列内的 Minimize 命令]

双击 `Minimize1` 弹出如下图所示的 `Minimize` 命令对话框。

> [图：Minimize 命令对话框界面]

你必须为上面的 `Minimize` 命令对话框提供两个输入：

- 优化器的选择。
- 要最小化的对象（及关联变量）。你可以直接输入对象，也可以单击该字段右侧的 **Edit** 按钮，从三种可能的选择（`Spacecraft`、`Variable` 或 `Array`）中选择对象类型。

## 备注

### 优化序列中 Vary、NonlinearConstraint 和 Minimize 命令的数量

一个优化序列必须包含一个或多个 `Vary` 命令。`Vary` 命令必须出现在任何 `Minimize` 或 `NonlinearConstraint` 命令之前。

一个优化序列中最多允许一个 `Minimize` 命令。

一个 `Optimize`/`EndOptimize` 优化序列可以不含 `Minimize` 命令。在这种情况下，由于每个优化序列必须包含 (a) 一个或多个 `NonlinearConstraint` 命令，和/或 (b) 单个 `Minimize` 命令，因此该优化序列必须包含至少一个 `NonlinearConstraint` 命令。

### 命令交互

`Minimize` 命令仅在 `Optimize`/`EndOptimize` 优化序列内使用。使用 `Minimize` 命令的完整示例请参阅 Optimize（优化）命令文档。

| 命令 | 描述 |
|------|------|
| `Vary` 命令 | 每个优化序列必须包含至少一个 `Vary` 命令。`Vary` 命令用于定义与优化序列关联的控制变量。 |
| `NonlinearConstraint` 命令 | `NonlinearConstraint` 命令用于定义与优化序列关联的约束（即目标）。注意，一个优化序列中允许多个 `NonlinearConstraint` 命令。 |
| `Optimize` 命令 | `Minimize` 命令只能出现在 `Optimize/EndOptimize` 命令序列内。 |

## 示例

```
% Minimize the eccentricity of Sat, using SQP1
Minimize SQP1(Sat.ECC)

% Minimize the Variable DeltaV, using SQP1
Minimize SQP1(DeltaV)

% Minimize the first component of MyArray, using VF13ad1
Minimize VF13ad1(MyArray(1,1))
```

上述脚本：分别演示用 SQP1 优化器最小化航天器 Sat 的偏心率、用 SQP1 最小化变量 DeltaV、用 VF13ad1 优化器最小化数组 MyArray 的第一个分量。

如上所述，`Minimize` 命令只出现在 `Optimize` 序列内。请参阅 Optimize（优化）命令帮助中展示 `Minimize` 命令用法的完整示例。
