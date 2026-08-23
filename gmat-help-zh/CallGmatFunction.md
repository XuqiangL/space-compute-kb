# 调用 GMAT 函数命令（CallGmatFunction）
> 译自 GMAT R2026a 帮助文档 CallGmatFunction.html

CallGmatFunction —— 调用一个 GMAT 函数。

## 脚本语法

```
GmatFunction()
GmatFunction(input_argument[, input_argument]...)
[output_argument[, output_argument]...] = GmatFunction
[output_argument[, output_argument]...] = ...
    GmatFunction(input_argument[, input_argument]...)
```

## 描述

GMAT 提供了一个特殊命令，允许你调用通过 GMAT 的 `GmatFunction` 资源编写的 GMAT 函数。在 GUI 中，GMAT 函数通过 `CallGmatFunction` 命令调用。

在语法描述中，`GmatFunction` 是一个必须在初始化期间声明的 `GmatFunction` 资源。参数可以作为输入传入函数，也可以作为输出从函数返回。详见"备注"一节。此外，作为输入传入函数或作为输出从函数接收的数据，还可以使用 GMAT 的 `Global` 命令声明为全局。更多细节请参见 `Global` 参考文档。

**另请参见**：GMATFunction、Global

## GUI

> [图：CallGmatFunction 命令的 GUI 面板]

`CallGmatFunction` 的 GUI 提供两个分别用于输入和输出参数的输入框，以及一个用于选择要调用的 GMAT 函数的列表。

`Output`（输出）框列出所有已配置的输出参数。必须通过点击 `Edit` 来选择它们，点击后会显示 `ParameterSelectioDialog` 窗口。关于如何选择参数的详细信息，请参见"计算参数（Calculation Parameters）"参考文档。

`Input`（输入）框的行为与 `Output` 完全相同，但它列出的是函数的所有已配置输入参数。同样必须通过点击 `Edit` 来选择参数。`Function`（函数）列表显示资源（Resources）树中所有已声明为 `GmatFunction` 资源的函数。从列表中选择一个函数即可调用它。

当更改被接受时，GMAT 不会对输入或输出参数执行任何验证。该验证在任务实际运行时执行。

## 备注

GMAT 对象可以作为输入传入 GMAT 函数，也可以作为输出从函数返回。如果某个 GMAT 对象没有在主脚本和 GMAT 函数内部都被声明为全局，那么所有传入函数或作为输出从函数接收的对象都被视为该函数和主脚本的局部对象。

下面列出了可以作为输入传入函数、作为输出从函数接收的允许参数。另请参见 `GmatFunction` 资源的"备注"和"示例"一节，其中包含更多细节和不同的示例，展示如何将对象作为输入传入函数、在函数内执行操作、然后将对象作为输出从函数接收。注意，一个 GMAT 函数文件必须包含且仅包含一个函数定义。

输入参数（语法描述中的 `input_argument` 值）可以是以下任一类型：

- 任何资源对象（例如 `Spacecraft`、`Propagator`、`DC`、`Optimizers`、`Impulsive` 或 `FiniteBurns`）
- 实数类型的资源参数（例如 *Spacecraft*.X）
- 字符串类型的资源参数（例如 *Spacecraft*.UTCGregorian）
- `Array`、`String` 或 `Variable` 资源

输出参数可以是以下任一类型：

- 资源对象，如 `Spacecraft`
- 实数类型的资源参数（例如 *Spacecraft*.X）
- 字符串类型的资源参数（例如 *Spacecraft*.UTCGregorian）
- `Array`、`String` 或 `Variable` 资源

## 示例

调用两个不同的函数。一个函数执行简单的叉积，第二个函数执行点积：

```
Create ReportFile rf
rf.WriteHeaders = false

Create GmatFunction cross_product
cross_product.FunctionPath = ...
'C:\Users\rqureshi\Desktop\cross_product.gmf'

Create GmatFunction dot_product
dot_product.FunctionPath = ...
'C:\Users\rqureshi\Desktop\dot_product.gmf'      

Create Array v1[3,1] v2[3,1] v3[3,1] ...
v4[3,1] v5[3,1]

Create Variable v6
Create String tempstring


BeginMissionSequence

v1(1,1) = 1
v1(2,1) = 2
v1(3,1) = 3
v2(1,1) = 4
v2(2,1) = 5
v2(3,1) = 6
v4(1,1) = 1
v4(2,1) = 2
v4(3,1) = 3
v5(1,1) = 4
v5(2,1) = -5
v5(3,1) = 6

% Call function. Pass local arrays as input:
% Receive local array as output
[v3] = cross_product(v1, v2)

Report rf v3

% Call function. Pass local arrays as input:
% Receive local variable as output
GMAT [v6] = dot_product(v4, v5)

tempstring = '---------'
Report rf tempstring
Report rf v6


%%%%%% cross_product Function begins below:

function [cross] = cross_product(vec1,vec2)

Create Array cross[3,1]

BeginMissionSequence

cross(1,1) = vec1(2,1)*vec2(3,1) - vec1(3,1)*vec2(2,1)
cross(2,1) = -(vec1(1,1)*vec2(3,1) - vec1(3,1)*vec2(1,1))
cross(3,1) = vec1(1,1)*vec2(2,1) - vec1(2,1)*vec2(1,1)


%%%%%% dot_product Function begins below:

function [c] = dot_product(a1,b1)

Create Variable c

BeginMissionSequence

c = a1(1,1)*b1(1,1) + a1(2,1)*b1(2,1) + a1(3,1)*b1(3,1)
```

逐段说明：

- 初始化部分声明两个 GmatFunction 资源（cross_product 和 dot_product）并指定各自的 .gmf 函数文件路径；创建若干 3×1 数组、一个变量和一个字符串。
- 主脚本任务序列给 v1、v2、v4、v5 赋值后，`[v3] = cross_product(v1, v2)` 把局部数组 v1、v2 作为输入传入函数，接收返回的局部数组 v3（叉积结果）并报告。
- `GMAT [v6] = dot_product(v4, v5)`（带可选 GMAT 前缀）调用点积函数，接收标量结果 v6 并报告。
- 函数定义部分：cross_product 函数内部创建局部数组 cross，按叉积公式逐分量计算；dot_product 函数内部创建局部变量 c，按点积公式计算。每个 .gmf 文件只含一个函数定义。

调用 GMAT 函数：把局部航天器作为输入传入，在函数内执行简单操作，然后把更新后的局部航天器送回主脚本；最后把航天器更新前后的位置矢量报告到局部报告文件订阅器：

```
Create Spacecraft aSat
aSat.DateFormat = UTCGregorian;
aSat.Epoch = '01 Jan 2000 11:59:28.000'
aSat.CoordinateSystem = EarthMJ2000Eq
aSat.DisplayStateType = Cartesian
aSat.X = 7100
aSat.Y = 0
aSat.Z = 1300

Create ReportFile rf
rf.WriteHeaders = false

Create GmatFunction Spacecraft_In_Out
Spacecraft_In_Out.FunctionPath = ...
'C:\Users\rqureshi\Desktop\Spacecraft_In_Out.gmf'


BeginMissionSequence

% Report initial S/C Position to local 'rf':
Report rf aSat.X aSat.Y aSat.Z

% Call function. Pass local S/C as input:
% Receive updated local S/C:
[aSat] = Spacecraft_In_Out(aSat)

% Report updated S/C Position to local 'rf':
Report rf aSat.X aSat.Y aSat.Z



%%%%%%%%%% Function begins below:

function [aSat] = Spacecraft_In_Out(aSat)

BeginMissionSequence

% Update the S/C Position vector:
% Send updated S/C back to main script:
aSat.X = aSat.X + 1000
aSat.Y = aSat.Y + 2000
aSat.Z = aSat.Z + 3000
```

逐段说明：

- 主脚本创建航天器 aSat 并设置初始笛卡尔状态 (7100, 0, 1300)，先报告一次初始位置。
- `[aSat] = Spacecraft_In_Out(aSat)` 把局部航天器作为输入传入函数，并接收更新后的局部航天器作为输出。
- 函数内部对位置三分量分别加 1000、2000、3000，修改随返回值传回主脚本。
- 主脚本再次报告 aSat 的位置，可看到更新后的值 (8100, 2000, 4300)。
