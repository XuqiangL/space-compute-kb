# 调用 Python 函数命令（CallPythonFunction）
> 译自 GMAT R2026a 帮助文档 CallPythonFunction.html

CallPythonFunction —— 调用一个 Python 函数。

## 脚本语法

```
Python.PythonModule.PythonFunction()
Python.PythonModule.PythonFunction(input_argument[, input_argument]...)
[output_argument[, output_argument]...] = Python.PythonModule.PythonFunction
[output_argument[, output_argument]...] = Python.PythonModule.PythonFunction(input_argument[, input_argument]...)
```

## 描述

GMAT 提供了一个特殊命令，允许你调用用 Python 语言编写的函数。在 GUI 中，这就是 `CallPythonFunction` 命令。

在语法描述中，前缀 `Python` 是一个关键字，用于告诉 GMAT 该脚本正在调用 Python 系统。`PythonModule` 标识一个 Python 文件（名为 PythonModule.py），其中包含要调用的函数。`PythonFunction` 是该文件内部被调用的函数。参数可以按照下述准则传入函数并从函数返回。详见"备注"一节。

当 Python 函数被调用时，GMAT 会在后台加载 Python 引擎。此功能要求在你的系统上正确安装并配置兼容版本的 Python。一旦 GMAT 加载了该引擎，它会一直驻留在内存中，直到 GMAT 关闭。

## GUI

> [图：CallPythonFunction 命令的 GUI 面板]

`CallPythonFunction` 的 GUI 提供一个单行文本输入框，用于以一行脚本的形式输入 Python 函数调用。

CallPythonFunction 的语法如上文"脚本语法"一节所述。GMAT 的 Python 接口接受变量（Variable）、字符串（String）、数值型对象参数和一维数组作为输入参数；它返回变量、数组和字符串，可以是单个值或一组值。该接口调用由 PythonModule 字段标识的 Python 脚本，脚本中定义了要访问的函数。接收函数负责根据下文"备注"中描述的类型转换来验证输入。

当用户接受面板上的输入时，GMAT 不会对输入或输出参数执行任何验证。该验证在任务运行时、Python 启动之后执行。

## 备注

输入参数（语法描述中的 `input_argument` 值）可以是以下任一类型：

- 实数类型的资源参数（例如 *Spacecraft*.X）
- 字符串类型的资源参数（例如 *Spacecraft*.UTCGregorian）
- 一维 `Array`、`String` 或 `Variable` 资源
- `Array` 资源元素

输出参数（语法描述中的 `output_argument` 值）可以是以下任一类型：

- `Array`、`String` 或 `Variable` 资源

当值在 Python 与 GMAT 之间传递时，会对以下数据类型执行类型转换。当数据作为输入参数从 GMAT 传入 Python 时，发生以下转换：

| GMAT | Python |
|------|--------|
| 实数（例如 Spacecraft.X、`Variable`、`Array` 元素） | float |
| 字符串（例如 *Spacecraft*.UTCGregorian、`String` 资源） | str |
| `Array` 资源 | memoryview |

当数据作为输出参数从 Python 传回 GMAT 时，发生以下转换：

| Python | GMAT |
|--------|------|
| str | String |
| float | 实数 |
| float 数组 | Array 资源 |

## 示例

调用一个简单的 Python 函数：

```
Create Variable x y

BeginMissionSequence

x = 1
y = Python.MyMath.sinh(x)
```

说明：调用 MyMath.py 模块中的 sinh 函数，把 x=1 传入，结果赋给 y。

调用一个多输入多输出的 Python 函数：

```
Create Spacecraft aSat
Create ImpulsiveBurn aBurn
Create Propagator aProp

Create Variable a_target mu dv1 dv2
mu = 398600.4415

BeginMissionSequence

% calculate burns for circular Hohmann transfer (example)
[dv1, dv2] = Python.MyOrbitFunctions.CalcHohmann(aSat.SMA, a_target, mu)

% perform first maneuver
aBurn.Element1 = dv1
Maneuver aBurn(aSat)

% propagate to apoapsis
Propagate aProp(aSat) {aSat.Apoapsis}

% perform second burn
aBurn.Element1 = dv2
Maneuver aBurn(aSat)
```

说明：调用 MyOrbitFunctions.py 模块中的 CalcHohmann 函数，传入航天器半长轴、目标半长轴 a_target 和引力常数 mu，接收两次霍曼转移的速度增量 dv1、dv2；然后依次施加第一次机动、传播到远地点、施加第二次机动，完成霍曼转移。
