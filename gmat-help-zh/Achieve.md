# 目标达成（Achieve）

> 译自 GMAT R2026a 帮助文档 Achieve.html

**Achieve** —— 为 `Target`（目标求解）序列指定目标。

## 脚本语法

```
Achieve SolverName (Goal = Arg1, [{Tolerance = Arg2}])
```

## 描述

`Achieve` 命令与 `Target` 命令配合使用，作为 `Target` 序列的一部分。`Achieve` 命令的目的是为目标器定义一个要达成的目标（目前，微分修正器是 `Target` 序列中唯一可用的目标器）。要配置 `Achieve` 命令，你需要指定目标对象、其对应的期望值以及可选的容差，以便微分修正器能够找到解。`Achieve` 命令必须伴随一个 `Vary` 命令且位于其后，以协助目标求解过程。

另请参阅：DifferentialCorrector（微分修正器）、Target（目标求解）、Vary（优化变量）。

## 选项

| 选项 | 描述 |
|------|------|
| **Arg1** | 指定 `DifferentialCorrector` 收敛后 `Goal` 的期望值。<br>• 接受的数据类型：Array、ArrayElement、Variable、String<br>• 允许值：实数、数组元素或变量<br>• 默认值：42165<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **Arg2** | `Goal` 等于 `Arg1` 的收敛容差（即二者接近程度）。<br>• 接受的数据类型：实数、数组元素、变量或任何用户定义的 > 0 的参数<br>• 允许值：实数、数组元素、变量或任何用户定义的 > 0 的参数<br>• 默认值：0.1<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **Goal** | 允许你选择任何单元素的用户定义参数（数字除外）作为目标器的目标。<br>• 接受的数据类型：对象参数、ArrayElement、Variable<br>• 允许值：`Spacecraft` 参数、`Array` 元素、`Variable`，或任何其他单元素的用户定义参数（数字除外）<br>• 默认值：`DefaultSC.Earth.RMAG`<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **SolverName** | 指定 `Target` 序列中使用的 `DifferentialCorrector`。<br>• 接受的数据类型：String<br>• 允许值：任何用户定义的 `DifferentialCorrector`<br>• 默认值：`DefaultDC`<br>• 是否必需：是<br>• 接口：GUI、脚本 |

## GUI

`Achieve` 命令仅在 `Target` 序列内有效，用于定义你期望的目标。在一个 `Target` 命令序列中可以使用多个 `Achieve` 命令。`Achieve` 命令对话框如下图所示，它允许你指定目标器、目标对象、目标值和收敛容差。

> [图：Achieve 命令对话框界面]

## 备注

### 命令交互

一个 `Target` 序列必须包含至少一个 `Vary` 命令和一个 `Achieve` 命令。

| 命令 | 描述 |
|------|------|
| `Target` 命令 | `Achieve` 命令只出现在 `Target` 序列内。 |
| `Vary` 命令 | 与任何 `Achieve` 命令相关联的至少有一个 `Vary` 命令。`Vary` 命令标识目标器使用的控制变量。`Achieve` 命令指定的目标通过改变控制变量来实现。 |

## 示例

如上所述，`Achieve` 命令只出现在 `Target` 序列内。请参阅 Target（目标求解）命令帮助中展示 `Achieve` 命令用法的示例。
