# SNOPT 优化器（SNOPTOptimizer）

> 译自 GMAT R2026a 帮助文档 SNOPTOptimizer.html

**SNOPT** —— 序列二次规划（SQP）优化器 SNOPT。

## 描述

`SNOPT` 优化器是由 Stanford Business Software, Inc. 开发的基于 SQP 的非线性规划求解器。它是专有组件，不随 GMAT 分发，必须从供应商处获得。`SNOPT` 执行非线性约束优化，同时支持线性和非线性约束。要使用此求解器，必须配置求解器选项，包括收敛准则、最大迭代次数等选项。在任务序列中，你通过 `Optimize`/`EndOptimize` 序列来实现诸如 SNOPT 之类的优化器。在该序列中，你使用 `Vary` 命令定义优化变量，分别使用 `Minimize` 和 `NonlinearConstraint` 命令定义代价函数和约束。

该资源不能在任务序列中修改。

另请参阅：FminconOptimizer、Optimize（优化）、Vary（优化变量）、NonlinearConstraint（非线性约束）、Minimize（最小化）。

## 字段

| 字段 | 描述 |
|------|------|
| **MajorFeasibilityTolerance** | 指定非线性约束应满足的精度（主可行容差）。<br>• 数据类型：Real<br>• 允许值：Real > 0<br>• 访问权限：set<br>• 默认值：1e-5<br>• 单位：无<br>• 接口：GUI、脚本 |
| **MajorIterationsLimit** | 允许的最大主迭代次数。它用于防止约束的线性化次数过多。<br>• 数据类型：Integer<br>• 允许值：Integer > 0<br>• 访问权限：set<br>• 默认值：1e-5<br>• 单位：无<br>• 接口：GUI、脚本 |
| **MajorOptimalityTolerance** | 指定对偶变量的最终精度（主最优容差）。更多细节请参阅 SNOPT 用户指南。<br>• 数据类型：Real<br>• 允许值：Real > 0<br>• 访问权限：set<br>• 默认值：1e-5<br>• 单位：无<br>• 接口：GUI、脚本 |
| **OutputFileName** | 包含报告文件的路径和文件名。该报告包含由 SNOPT 写入的有关优化进展和信息的数据。<br>• 数据类型：String<br>• 允许值：任何用户定义的文件名<br>• 访问权限：set<br>• 默认值：`SNOPT.out`<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **OverrideSpecsFileValues** | 标志位，指示在 GMAT 脚本/GUI 中可设置的选项是否应覆盖 `SNOPT` Specs 文件中设置的值。注意，如果在初始化期间未找到 specs 文件，即使 `OverrideSpecsFileValues` 字段设置为 `false`，也会应用 GMAT 配置。<br>• 数据类型：Boolean<br>• 允许值：`true`、`false`<br>• 访问权限：set<br>• 默认值：`true`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **ReportFile** | 包含报告文件的路径和文件名。该报告包含由 GMAT 写入的有关优化进展和信息的数据。<br>• 数据类型：String<br>• 允许值：任何用户定义的文件名<br>• 访问权限：set<br>• 默认值：`SNOPTSNOPT1.data`<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **ReportStyle** | 确定求解器每次迭代时写入消息窗口以及写入 `ReportFile` 字段所指定报告的数据量和类型（当 `ShowProgress` 为 true 时）。目前，`Normal`、`Debug` 和 `Concise` 选项包含相同的信息：控制变量的值、约束和目标函数。除这些信息外，`Verbose` 选项还包含经优化器缩放的控制变量的值。<br>• 数据类型：String<br>• 允许值：`Normal`、`Concise`、`Verbose`、`Debug`<br>• 访问权限：set<br>• 默认值：`Normal`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **ShowProgress** | 确定与求解器迭代相关的数据是否既显示在消息窗口中，又写入 `ReportFile` 字段所指定的报告。当 `ShowProgress` 为 true 时，消息窗口中包含的信息量和写入报告的信息量由 `ReportStyle` 字段控制。<br>• 数据类型：Boolean<br>• 允许值：`true`、`false`<br>• 访问权限：set<br>• 默认值：`true`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **SpecsFileName** | 由 SNOPT 读取以配置优化器所有设置的文件。GMAT 脚本/GUI 接口仅支持 SNOPT 配置选项的一小部分。该文件允许你设置 SNOPT 支持的任何选项。该文件仅在初始化期间找到时才加载，且文件中所选的值可以通过 `OverrideSpecsFileValues = true` 被 GMAT 配置覆盖。更多信息请参阅"备注"部分。<br>• 数据类型：String<br>• 允许值：任何用户定义的文件名<br>• 访问权限：set<br>• 默认值：`SNOPT.spec`<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **TotalIterationsLimit** | 允许的最大子迭代次数。<br>• 数据类型：Integer<br>• 允许值：Integer > 0<br>• 访问权限：set<br>• 默认值：100000<br>• 单位：无<br>• 接口：GUI、脚本 |
## GUI

`SNOPT` 对话框允许你指定 `SNOPT` 的属性，例如最大迭代次数、代价函数容差、可行容差、报告选项的选择，以及是否使用中心差分导数方法的选择。

要创建 `SNOPT` 资源，导航到资源（Resources）树，展开 `Solvers` 文件夹，选中并右键单击 `Optimizers` 子文件夹，指向 **Add**，然后选择 **SNOPT**。这将创建一个新的 `SNOPT` 资源 `SNOPT1`。双击 `SNOPT1` 弹出如下图所示的 `SNOPT` 对话框。

> [图：SNOPT 对话框界面]

## 备注

### SNOPT 优化器版本与可用性

GMAT 目前使用 SNOPT 7.2-12.2。此优化器不包含在 GMAT 的标称安装中，仅在你创建并安装了 SNOPT 插件或从供应商处获得 SNOPT 后可用。

### SPECS 文件配置

Specs 文件包含一个选项和值的列表，其一般形式如下：

```
Begin options
   Iterations limit 500
   Minor feasibility tolerance 1.0e-7
   Solution Yes
End options
```

该文件以关键字 Begin 开始，以 End 结束。文件采用自由格式。每行指定一个选项，使用以下一项或多项：

1. 一个关键字（所有选项都需要）。
2. 一个修饰关键字的短语（一个或多个单词）（仅用于某些选项）。
3. 一个指定整数或实数值的数字（仅用于某些选项）。此类数字最多可为 16 个连续字符，采用 Fortran 77 的 I、F、E 或 D 格式，以空格或换行符结尾。

这些项可以用大写、小写或大小写混合输入。某些关键字有同义词，并且允许某些缩写，只要没有歧义即可。可以使用空行和注释来提高可读性。注释以行中任意位置的星号（*）开始，该行后续所有字符均被忽略。Begin 行会回显到 Summary 文件中。

SNOPT 选项的完整列表请参阅 SNOPT 用户指南。

### 配置 SNOPT 以实现有效优化

使用 `SNOPT` 时，`Vary` 命令中的 `Upper`（上界）和 `Lower`（下界）是必填字段。通过为你的问题适当设置这些值，可以降低 `SNOPT` 尝试非物理值或导致物理模型出现数值奇异值的可能性。使用 `SNOPT` 时，仔细设置边界非常重要。

此外，`SNOPT` 对缩放相当敏感，必须注意在 `Vary` 命令中提供可接受的 `AdditiveScaleFactor`（加性比例因子）和 `MultiplicativeScaleFactor`（乘性比例因子）值。使用 `SNOPT` 时，导数由 `SNOPT` 通过优化器内置的有限差分计算。如果优化问题缩放不当，优化可能失败，或耗费不必要的时间。注意，SNOPT 具有内置的缩放选项，可通过 Specs 文件设置，SNOPT 用户指南中有更详细的描述。

### 资源与命令交互

> **警告**：GMAT 的 `Vary` 命令是一个通用接口，设计用于支持许多优化器，`Vary` 命令支持的并非所有设置都被 `SNOPT` 支持。关于哪些 `Vary` 命令设置被 `SNOPT` 支持的详细信息，请参阅 Vary（优化变量）命令文档。

`SNOPT` 资源只能在优化类命令的上下文中使用。更多信息和完整示例请参阅 Optimize（优化）、Vary（优化变量）、NonlinearConstraint（非线性约束）和 Minimize（最小化）的文档。

## 示例

使用 SNOPT 求解一个简单的数学优化问题。

```
Create SNOPT NLP
NLP.ShowProgress              = true
NLP.ReportStyle               = Normal
NLP.ReportFile                = output.report
NLP.MajorOptimalityTolerance  = 0.001
NLP.MajorFeasibilityTolerance = 0.0001
NLP.MajorIterationsLimit      = 456
NLP.TotalIterationsLimit      = 789012
NLP.OutputFileName            = 'SNOPTName123.out'
NLP.SpecsFileName             = 'SNOPT.spec'
NLP.OverrideSpecsFileValues   = true

Create Variable X1 X2 J G

BeginMissionSequence

Optimize NLP {SolveMode = Solve, ExitMode = DiscardAndContinue}
   
   %  Vary the independent variables
   Vary 'Vary X1' NLP(X1 = 0, {Perturbation = 0.0000001, Upper = 10, ...
   Lower = -10, AdditiveScaleFactor = 0.0, ...
   MultiplicativeScaleFactor = 1.0})
   Vary 'Vary X2' NLP(X2 = 0, {Perturbation = 0.0000001, Upper = 10, ...
   Lower = -10, AdditiveScaleFactor = 0.0, ...
   MultiplicativeScaleFactor = 1.0})
   
   %  The cost function and Minimize command
   J = ( X1 - 2 )^2 + ( X2 - 2 )^2
   Minimize 'Minimize Cost (J)' NLP(J)
   
   %  Calculate constraint and use NonLinearConstraint command
   G = X2 + X1
   NonlinearConstraint NLP(G<=8)

EndOptimize
```

上述脚本：创建 SNOPT 优化器 NLP 并配置其报告、容差、迭代限制、输出文件和 specs 文件选项；创建变量 X1、X2、J、G；在 Optimize 序列中以 X1、X2 为控制变量（初值 0，上下界 ±10），最小化代价函数 J = (X1-2)² + (X2-2)²，并施加约束 G = X1+X2 ≤ 8。
