# MATLAB 函数资源（MatlabFunction）
> 译自 GMAT R2026a 帮助文档 MatlabFunction.html

MatlabFunction —— 外部 MATLAB 函数的声明。

## 描述

`MatlabFunction` 资源向 GMAT 声明：给定的名称引用一个已存在的 MATLAB 语言外部函数。该函数可以在任务序列中像内置函数一样被调用，但有一些限制。详见 `CallMatlabFunction` 参考文档。用户创建的函数和内置函数（如 cos 或 path）都受支持。

GMAT 支持通过该函数向 MATLAB 传入数据和从 MATLAB 接收数据。它要求系统上存在受支持且配置正确的 MATLAB 版本。关于该接口的一般细节，请参见 MATLAB Interface 文档。

**另请参见**：CallMatlabFunction、MATLAB Interface

## 字段

| 字段 | 描述 |
|------|------|
| `FunctionPath` | 调用关联函数时要添加到 MATLAB 搜索路径中的路径。多个路径用分号（Windows 上）或冒号（其他平台上）分隔。<br>数据类型：字符串<br>允许的值：合法的文件路径<br>访问方式：set、get<br>默认值：启动文件中的 `MATLAB_FUNCTION_PATH` 属性<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

> [图：MatlabFunction 资源的 GUI 窗口]

`MatlabFunction` 的 GUI 窗口非常简单：它只有一个用于输入函数路径的文件输入框，以及一个让你以图形方式选择路径的 Browse（浏览）按钮。

## 备注

### 搜索路径

当调用声明为 `MatlabFunction` 的函数时，GMAT 会在后台以自定义的、可配置的搜索路径启动 MATLAB。然后 MATLAB 在该搜索路径中查找指定名称的函数。搜索区分大小写，因此函数名与 `MatlabFunction` 资源的名称必须完全一致。

搜索路径按顺序由以下部分组成：

1. 关联 `MatlabFunction` 资源的 `FunctionPath` 字段（默认：空）
2. GMAT 启动文件中的 `MATLAB_FUNCTION_PATH` 条目（默认：*GMAT*\userfunctions\matlab）
3. MATLAB 搜索路径（由 MATLAB 的 `path()` 函数返回）

如果在一次运行中调用了多个 MATLAB 函数，每个函数的 `FunctionPath` 字段都会在调用该函数时被添加到搜索路径的最前面。

可以在 `FunctionPath` 字段中用分号（Windows 上）或冒号（macOS 和 Linux 上）分隔来组合多个路径。

### 工作目录

当 MATLAB 在后台启动时，其工作目录被设置为 GMAT 的 `bin` 目录。

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

说明：声明外部 MATLAB 函数 CalcHohmann 并用 FunctionPath 指定其所在目录；把航天器半长轴、目标半长轴和引力常数传入，接收两次霍曼转移的速度增量；依次施加第一次机动、传播到远地点、施加第二次机动。

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

说明：声明 path 和 pwd 两个 MatlabFunction 资源（对应 MATLAB 同名内置命令），调用它们并把返回的字符串写入报告文件。
