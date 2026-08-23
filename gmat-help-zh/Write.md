# 写出命令（Write）
> 译自 GMAT R2026a 帮助文档 Write.html

Write —— 将数据写入以下三个目的地中的一个或多个：消息窗口、日志文件或 `ReportFile` 资源。

## 脚本语法

```
Write ResourceList [{ MessageWindow = true, LogFile = false,  
                    Style = Concise, ReportFile = myReport }]
```

## 描述

`Write` 命令允许你在执行期间有选择地将信息写入 GMAT 的输出目的地。`Write` 命令可以辅助自动化质量保证（QA）：把数据写入 GMAT 日志文件或 `ReportFile` 资源，供独立的 QA 系统处理；也可以把数据写入消息窗口，以帮助排查和调试脚本配置。该命令还可用于写出附属资源上的信息，以便观察参数在整个任务过程中的变化。

## 选项

| 选项 | 描述 |
|------|------|
| `LogFile` | 指定是否将输出写入日志文件的标志。<br>接受的数据类型：布尔值<br>允许的值：{True, False}<br>默认值：False<br>是否必需：否<br>接口：GUI、脚本 |
| `MessageWindow` | 指定是否将输出显示在消息窗口中的标志。<br>接受的数据类型：布尔值<br>允许的值：{True, False}<br>默认值：True<br>是否必需：否<br>接口：GUI、脚本 |
| `ReportFile` | 输出数据将写入的 `ReportFile` 资源名称。如果未设置此字段，则不会写入任何 `ReportFile` 资源。用户可以在 `ReportFile` 上设置 `Precision` 和 `ColumnWidth` 等格式选项；但使用 `Write` 命令写数据时，这些设置不会被使用。<br>接受的数据类型：`ReportFile` 资源<br>允许的值：任何用户定义的 `ReportFile` 资源<br>默认值：无<br>是否必需：否<br>接口：GUI、脚本 |
| `ResourceList` | 一个或多个希望输出其值的 GMAT 资源和/或资源字段的列表。<br>接受的数据类型：GMAT 资源和/或资源字段的列表<br>允许的值：任何 GMAT 资源名或 资源.字段 名<br>默认值：无<br>是否必需：否<br>接口：GUI、脚本 |
| `Style` | 指定输出格式的参数。Concise 表示在适当情况下输出仅包含值，不包含对象名；例外情况是输出带字段的对象（如 `Spacecraft`）时，会输出对象和字段。Verbose 表示始终输出对象名和字段。Script 表示生成可被脚本解析的输出（即把输出粘贴到现有 GMAT 脚本中时能通过语法检查）。<br>接受的数据类型：字符串<br>允许的值：{Concise, Verbose, Script}<br>默认值：Concise<br>是否必需：否<br>接口：GUI、脚本 |

## GUI

在下例中，`myVar` 的值将只写入消息窗口。

> [图：Write 命令的 GUI 面板，仅勾选消息窗口输出 myVar]

## 示例

下面是一些使用 `Write` 命令的示例脚本，输出以加粗字体显示。

```
Create ChemicalTank ChemicalTank1
Create Spacecraft Sat
Create String myString1 myString2
Create Variable myVar
Create Array myArray[2,2]

myVar        = 3.1415
myString1    = 'This is my string'
myArray(1,1) = 1
myArray(2,2) = 1

BeginMissionSequence

Write ChemicalTank1 {Style =  Script}
```

**Create ChemicalTank ChemicalTank1;**

**ChemicalTank1.AllowNegativeFuelMass = false;**

**ChemicalTank1.FuelMass = 756;**

**ChemicalTank1.Pressure = 1500;**

**ChemicalTank1.Temperature = 20;**

**ChemicalTank1.RefTemperature = 20;**

**ChemicalTank1.Volume = 0.75;**

**ChemicalTank1.FuelDensity = 1260;**

**ChemicalTank1.PressureModel = PressureRegulated;**

说明：以 Script 样式输出整个 ChemicalTank1 资源，输出内容本身即为可粘贴回脚本的合法 GMAT 语句（Create 语句加各字段赋值）。

```
Write Sat.X Sat.VZ
```

**7100**

**1**

说明：以默认的 Concise 样式输出两个资源参数的值，只显示数值，不显示参数名。

```
Write myVar myString1
```

**3.1415**

**'This is my string'**

说明：Concise 样式下输出变量与字符串的值，字符串带单引号。

```
Write myArray
```

**1 0**

**0 1**

说明：输出整个 2×2 数组，按矩阵形式分行显示（初始化时只设置了 (1,1) 和 (2,2) 为 1，其余为 0）。

```
Write myArray(2,2)
```

**1**

说明：输出单个数组元素。

```
myString2 = sprintf('%10.7f',Sat.X)  
Write myString2 {Style = Script}
```

**Create String myString2;**

**myString2 = '7100.0000000';**

说明：先用 `sprintf` 把 Sat.X 按格式 '%10.7f' 格式化为字符串存入 myString2，再以 Script 样式输出，得到可直接用于脚本的 Create 与赋值语句。

```
Write myString2
```

**'7100.0000000'**

说明：以默认 Concise 样式输出同一字符串，只显示带引号的值。

下面的示例写出一份报告，该报告可通过 `#Include` 功能读入 GMAT 脚本：

```
Create Spacecraft Sat;
Create ReportFile rf;
rf.Filename = 'GMAT.script';
Create Variable myVar;
myVar = 11;

BeginMissionSequence;

Write Sat {Style = Script, MessageWindow = false, ReportFile = rf}
```

说明：以 Script 样式把航天器 Sat 的完整定义写入文件 GMAT.script（通过 ReportFile rf），并关闭消息窗口输出。生成的文件是合法的 GMAT 脚本片段，之后可用 `#Include` 宏包含进其他脚本。

下面的示例在机动完成后写出燃料箱（附着在航天器上的附属资源）的参数。输出显示在脚本下方；注意，燃料质量的减少就是通过这种方式用 `Write` 命令写出来的：

```
Create Spacecraft Sat;
Create ChemicalTank ChemicalTank1;
Sat.Tanks = {ChemicalTank1};

BeginMissionSequence;
Maneuver ImpulsiveBurn1(Sat);
Propagate DefaultProp(Sat) {Sat.ElapsedSecs = 12000};
Write Sat.ChemicalTank1
```

**ChemicalTank1.AllowNegativeFuelMass = true;**

**ChemicalTank1.FuelMass = 386.9462121211856;**

**ChemicalTank1.Pressure = 1500;**

**ChemicalTank1.Temperature = 20;**

**ChemicalTank1.RefTemperature = 20;**

**ChemicalTank1.Volume = 0.75;**

**ChemicalTank1.FuelDensity = 1260;**

**ChemicalTank1.PressureModel = 'PressureRegulated';**

说明：把燃料箱 ChemicalTank1 挂到航天器上，执行脉冲机动并传播 12000 秒后，用 `Write Sat.ChemicalTank1` 输出该附属资源的当前状态；输出中的 FuelMass 已因机动消耗而下降。
