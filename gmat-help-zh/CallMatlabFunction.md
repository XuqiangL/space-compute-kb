# 调用 MATLAB 函数命令（CallMatlabFunction）
> 译自 GMAT R2026a 帮助文档 CallMatlabFunction.html

CallMatlabFunction —— 调用一个 MATLAB 函数。

## 脚本语法

```
MatlabFunction()
MatlabFunction(input_argument[, input_argument]...)
[output_argument[, output_argument]...] = MatlabFunction
[output_argument[, output_argument]...] = ...
    MatlabFunction(input_argument[, input_argument]...)
```

## 描述

GMAT 提供了一个特殊命令，允许你调用用 MATLAB 语言编写的函数或 MATLAB 软件自带的函数。在 GUI 中，这就是 `CallMatlabFunction` 命令。

在语法描述中，`MatlabFunction` 是一个必须在初始化期间声明的 `MatlabFunction` 资源。参数可以传入函数并从函数返回，但有一些数据类型限制。详见"备注"一节。

当 MATLAB 函数被调用时，GMAT 会在后台打开一个 MATLAB 命令行窗口。此功能要求在你的系统上正确安装并配置 MATLAB。

**另请参见**：MatlabFunction、MATLAB Interface

## GUI

> [图：CallMatlabFunction 命令的 GUI 面板]

`CallMatlabFunction` 的 GUI 提供两个分别用于输入和输出参数的输入框，以及一个用于选择要调用的函数的列表。

`Output`（输出）框列出所有已配置的输出参数。必须通过点击 `Edit` 来选择它们，点击后会显示参数选择窗口。关于如何选择参数的详细信息，请参见"计算参数（Calculation Parameters）"参考文档。

`Input`（输入）框的行为与 `Output` 完全相同，但它列出的是函数的所有已配置输入参数。同样必须通过点击 `Edit` 来选择参数。`Function`（函数）列表显示资源树中所有已声明为 `MatlabFunction` 资源的函数。从列表中选择一个函数即可调用它。

当更改被接受时，GMAT 不会对输入或输出参数执行任何验证。该验证在任务运行时、MATLAB 启动之后执行。

## 备注

输入参数（语法描述中的 `input_argument` 值）可以是以下任一类型：

- 实数类型的资源参数（例如 *Spacecraft*.X）
- 字符串类型的资源参数（例如 *Spacecraft*.UTCGregorian）
- `Array`、`String` 或 `Variable` 资源
- `Array` 资源元素

输出参数（语法描述中的 `output_argument` 值）可以是以下任一类型：

- 实数类型的资源参数（例如 *Spacecraft*.X）
- 字符串类型的资源参数（例如 *Spacecraft*.UTCGregorian）
- `Array`、`String` 或 `Variable` 资源
- `Array` 资源元素

当值在 MATLAB 与 GMAT 之间传递时，会对以下数据类型执行类型转换。当数据作为输入参数从 GMAT 传入 MATLAB 时，发生以下转换：

| GMAT | MATLAB |
|------|--------|
| 实数（例如 Spacecraft.X、`Variable`、`Array` 元素） | double |
| 字符串（例如 *Spacecraft*.UTCGregorian、`String` 资源） | char 数组 |
| `Array` 资源 | double 数组 |

当数据作为输出参数从 MATLAB 传回 GMAT 时，发生以下转换：

| MATLAB | GMAT |
|--------|------|
| char 数组 | 字符串 |
| double | 实数 |
| double 数组 | Array 资源 |

## 示例

调用一个简单的 MATLAB 内置函数：

```
Create MatlabFunction sinh
Create Variable x y

BeginMissionSequence

x = 1
[y] = sinh(x)
```

说明：声明名为 sinh 的 MatlabFunction 资源（对应 MATLAB 内置双曲正弦函数），把 x=1 传入，接收结果到 y。

调用一个外部的自定义 MATLAB 函数：

```
Create Spacecraft aSat
Create ImpulsiveBurn aBurn
Create Propagator aProp

Create MatlabFunction CalcHohmann
CalcHohmann.FunctionPath = 'C:\path\to\functions'

Create Variable a_target mu dv1 dv2
mu = 398600.4415

BeginMissionSequence

% calculate burns for circular Hohmann transfer (example)
[dv1, dv2] = CalcHohmann(aSat.SMA, a_target, mu)

% perform first maneuver
aBurn.Element1 = dv1
Maneuver aBurn(aSat)

% propagate to apoapsis
Propagate aProp(aSat) {aSat.Apoapsis}

% perform second burn
aBurn.Element1 = dv2
Maneuver aBurn(aSat)
```

说明：声明外部 MATLAB 函数 CalcHohmann 并用 FunctionPath 指定其所在目录；在任务序列中把航天器半长轴、目标半长轴 a_target 和引力常数 mu 传入，接收两次霍曼转移的速度增量 dv1、dv2；然后依次施加第一次机动、传播到远地点、施加第二次机动，完成霍曼转移。

返回 MATLAB 的搜索路径和当前工作目录：

```
Create MatlabFunction path pwd
Create String pathStr pwdStr
Create ReportFile aReport

BeginMissionSequence

[pathStr] = path
[pwdStr] = pwd

Report aReport pathStr
Report aReport pwdStr
```

说明：一条 Create 语句声明 path 和 pwd 两个 MatlabFunction 资源（对应 MATLAB 的同名内置命令）；调用它们并把返回的字符串分别存入 pathStr、pwdStr，最后写入报告文件。

