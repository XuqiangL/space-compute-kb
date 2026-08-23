# 优化变量（Vary）

> 译自 GMAT R2026a 帮助文档 Vary.html

**Vary** —— 指定求解器使用的变量。

## 脚本语法

```
Vary SolverName(<UserSelectedControl>=InitialGuess, [{[Perturbation=Arg1], [MaxStep=Arg2], [Lower=Arg3], [Upper=Arg4], [AdditiveScalefactor=Arg5], [MultiplicativeScalefactor=Arg6]}])
```

## 描述

`Vary` 命令与 `Target` 或 `Optimize` 命令配合使用。`Vary` 命令定义目标器或优化器使用的控制变量。随后，`Target` 或 `Optimize` 序列会改变这些控制变量，直到满足某些期望的条件。每个 `Target` 或 `Optimize` 序列必须包含至少一个 `Vary` 命令。

另请参阅：DifferentialCorrector（微分修正器）、FminconOptimizer、VF13ad、Target（目标求解）、Optimize（优化）。

## 选项

| 选项 | 描述 |
|------|------|
| **AdditiveScaleFactor** | 用于对自变量进行无量纲化的数。求解器只能看到变量的无量纲形式。无量纲化使用以下方程执行：xn = m (xd + a)。（xn 为无量纲参数，xd 为有量纲参数，a = 加性比例因子，m = 乘性比例因子。）注意，无量纲化过程发生在对控制变量施加摄动之后，因此 xd 表示已摄动的控制变量。<br>• 接受的数据类型：实数、数组元素、变量或任何用户定义的参数<br>• 允许值：实数、数组元素、变量或任何用户定义的参数<br>• 默认值：0<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **InitialGuess** | 指定所选变量的初始猜测值。<br>• 接受的数据类型：实数、数组元素、变量，或任何满足所选变量对象条件的用户定义参数<br>• 允许值：实数、数组元素、变量，或任何满足所选变量对象条件的用户定义参数<br>• 默认值：0.5<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **Lower** | `Lower` 选项用于设置控制变量的下界。`Lower` 必须小于 `Upper`。关于哪些求解器支持此设置，请参阅"Vary 命令选项"部分。<br>• 接受的数据类型：实数、数组元素、变量或任何用户定义的参数<br>• 允许值：实数、数组元素、变量或任何用户定义的参数（Upper > Lower）<br>• 默认值：0<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **MaxStep** | `MaxStep` 选项是求解器单次迭代期间控制变量允许的最大变化量。关于哪些求解器支持此设置，请参阅"Vary 命令选项"部分。<br>• 接受的数据类型：实数、数组元素、变量或任何用户定义的 > 0 的参数<br>• 允许值：实数、数组元素、变量或任何用户定义的 > 0 的参数<br>• 默认值：0.2<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **MultiplicativeScaleFactor** | 用于对自变量进行无量纲化的数。求解器只能看到变量的无量纲形式。无量纲化使用以下方程执行：xn = m (xd + a)。（xn 为无量纲参数，xd 为有量纲参数，a = 加性比例因子，m = 乘性比例因子。）注意，无量纲化过程发生在对控制变量施加摄动之后，因此 xd 表示已摄动的控制变量。<br>• 接受的数据类型：实数、数组元素、变量或任何用户定义的参数<br>• 允许值：实数、数组元素、变量或任何用户定义的 > 0 的参数<br>• 默认值：1<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **Perturbation** | `Perturbation` 选项是用于计算有限差分导数的摄动步长。关于哪些求解器支持此设置，请参阅"Vary 命令选项"部分。<br>• 接受的数据类型：实数、数组元素、变量或任何用户定义的参数<br>• 允许值：实数、数组元素、变量或任何用户定义的 != 0 的参数<br>• 默认值：0.0001<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **SolverName** | 允许你选择指派给 `Vary` 命令的求解器。在 `Target` 序列的上下文中，你将选择一个 `DifferentialCorrector` 对象；在 `Optimize` 序列的上下文中，你将选择 `FminconOptimizer` 或 `VF13ad` 对象。<br>• 接受的数据类型：求解器（优化器或目标器）<br>• 允许值：任何用户定义的优化器或目标器<br>• 默认值：`Target` 序列中为 `DefaultDC`，`Optimize` 序列中为 `DefaultSQP`<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **Upper** | `Upper` 选项用于设置控制变量的上界。`Lower` 必须小于 `Upper`。关于哪些求解器支持此设置，请参阅"Vary 命令选项"部分。<br>• 接受的数据类型：实数、数组元素、变量或任何用户定义的参数<br>• 允许值：实数、数组元素、变量或任何用户定义的参数（Upper > Lower）<br>• 默认值：3.14159<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **UserSelectedControl** | 允许你选择任何单元素的用户定义参数（数字除外）作为变量。例如，`DefaultIB.V`、`DefaultIB.N`、`DefaultIB.Element1`、`DefaultSC.TA`、`Array(1,1)` 和 `Variable` 都是有效值。三元素机动矢量或多维数组不是有效值。<br>• 接受的数据类型：参数、数组元素、`Variable`，或任何其他单元素的用户定义参数（数字除外）。注意，所选变量必须可在任务树中设置。<br>• 允许值：Spacecraft 参数、数组元素、`Variable`，或任何其他单元素的用户定义参数（数字除外）<br>• 默认值：`DefaultIB.Element1`<br>• 是否必需：是<br>• 接口：GUI、脚本 |
## GUI

`Vary` 命令仅在 `Target` 或 `Optimize` 序列内有效，用于定义将用于求解问题的控制变量。`Vary` 命令对话框如下图所示。

> [图：Vary 命令对话框界面]

`Vary` 命令对话框允许你指定：

- 求解器（Solver）的选择（如果使用 `Target` 序列则为微分修正器，如果使用 `Optimize` 序列则为优化器）。
- 控制变量（Variable）对象。要定义 `Vary` 命令中使用的控制变量，单击 **Edit** 按钮弹出 `ParameterSelectDialog` 对话框（如下图所示），使用箭头选择所需对象，然后单击 **OK**。
- 控制变量对象的初始值（Initial Value）。
- 摄动（Perturbation）步长，用作有限差分算法的一部分。如"备注"部分所述，仅当所选求解器为微分修正器或 VF13AD 优化器时才使用此字段。
- 收敛后控制变量对象允许的下限（Lower）。如"备注"部分所述，仅当所选求解器为微分修正器或 fmincon 优化器时才使用此字段。
- 收敛后控制变量对象允许的上限（Upper）。如"备注"部分所述，仅当所选求解器为微分修正器或 fmincon 优化器时才使用此字段。
- 控制变量对象每次迭代的最大步长（Max Step）。如"备注"部分所述，仅当所选求解器为微分修正器或 VF13AD 优化器时才使用此字段。
- 用于缩放控制变量对象的加性比例因子（Additive Scale Factor）。
- 用于缩放控制变量对象的乘性比例因子（Multiplicative Scale Factor）。

## 备注

### Vary 命令选项

`Vary` 命令设计为可与 GMAT 的全部三种目标器和优化器（Differential Corrector、fmincon 和 VF13AD）配合使用。这些求解器由不同的开发者开发，工作方式都略有不同，因此有不同的需求。下表显示了给定求解器可用的命令选项。

| 选项 | Differential Corrector | fmincon | VF13AD | SNOPT | Yukon |
|------|:---:|:---:|:---:|:---:|:---:|
| **SolverName** | X | X | X | X | X |
| **Variable** | X | X | X | X | X |
| **InitialGuess** | X | X | X | X | X |
| **AdditiveScaleFactor** | X | X | X | X | X |
| **MultiplicativeScaleFactor** | X | X | X | X | X |
| **Lower** | X | X |  | X | X |
| **Upper** | X | X |  | X | X |
| **Perturbation** | X |  | X |  | X |
| **MaxStep** | X |  | X |  | X |

`Vary` 语法允许你为某个选项指定值，即使特定的求解器不会使用该信息。

#### Vary 命令接受重复参数

如下例所示，`Vary` 命令接受重复的参数。

```
Vary DefaultDC(ImpulsiveBurn1.Element1 = 2, ...
{Perturbation = 1e99, Perturbation = .001})
```

公认的最佳实践是在任何给定命令中不重复参数。但是，对于 `Vary` 命令，如果你不小心多次设置了同一参数，则以最后一次设置为准。因此，在上面的示例中，摄动步长被设置为 0.001。

#### 在 Vary 命令中使用推力器参数

如果你希望在 `Vary` 命令中使用推力器参数（例如推力方向），则必须直接引用克隆的（子）对象。在下面的示例中，我们首先展示使用父对象的语法（不起作用），然后展示使用克隆（子）对象的正确语法。

```
%Referencing the parent object, thruster1, does not work.
Vary DC1(thruster1.ThrustDirection1 = 0.4)
Vary DC1(thruster1.ThrustDirection2 = 0.5)

%Referencing the cloned (child) object, Sc.thruster1, does work.
Vary DC1(Sc.thruster1.ThrustDirection1 = 0.4)
Vary DC1(Sc.thruster1.ThrustDirection2 = 0.5)
```

上述脚本：引用父对象 thruster1 不起作用；必须引用挂载到航天器 Sc 上的克隆（子）对象 Sc.thruster1 才能正确改变推力方向参数。

#### 命令交互

| 命令 | 描述 |
|------|------|
| `Target` 命令 | `Vary` 命令只出现在 `Target` 或 `Optimize` 序列内。 |
| `Optimize` 命令 | `Vary` 命令只出现在 `Target` 或 `Optimize` 序列内。 |
| `Achieve` 命令 | `Achieve` 命令作为 `Target` 序列的一部分，指定期望的结果或目标（通过使用 `Vary` 命令改变控制变量来实现）。 |
| `NonlinearConstraint` 命令 | `NonlinearConstraint` 命令作为 `Optimize` 序列的一部分，指定期望的结果或目标（通过使用 `Vary` 命令改变控制变量来实现）。 |
| `Minimize` 命令 | `Minimize` 命令作为 `Optimize` 序列的一部分，指定要最小化的期望量（通过使用 `Vary` 命令改变控制变量来实现）。 |

## 示例

如上所述，`Vary` 命令只出现在 `Target` 或 `Optimize` 序列内。请参阅 Target（目标求解）和 Optimize（优化）命令帮助中展示 `Vary` 命令用法的示例。
