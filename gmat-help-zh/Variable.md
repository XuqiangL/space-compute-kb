# 变量资源（Variable）
> 译自 GMAT R2026a 帮助文档 Variable.html

Variable —— 用户定义的数值变量。

## 描述

`Variable` 资源用于存储单个数值，供任务序列中的命令使用。在大多数命令中，它可以代替字面数值使用。`Variable` 资源在创建时初始化为零，可以使用字面数值赋值，也可以（在任务序列中）使用 `Variable` 资源、`Array` 资源元素、数值类型的资源参数或求值为标量数值的 `Equation` 命令赋值。

**另请参见**：Array、String

## 字段

`Variable` 资源没有字段；取而代之的是直接给资源本身设置所需的值。

| 字段 | 描述 |
|------|------|
| *value* | 变量的值。<br>数据类型：实数<br>允许的值：-∞ < *value* < ∞<br>访问方式：set、get<br>默认值：0.0<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

> [图：Variable 资源的创建窗口]

GMAT GUI 允许你在不离开窗口的情况下一次创建多个 `Variable` 资源。创建 `Variable` 的步骤：

1. 在 **Variable Name** 框中输入所需的变量名称。
2. 在 **Variable Value** 框中输入变量的初始值。此项为必填，且必须是字面数值。
3. 单击 **=>** 按钮创建该变量并将其添加到右侧列表中。

你可以用这种方式创建多个 `Variable` 资源。要在此窗口中编辑已有变量，在右侧列表中单击它并编辑其值。必须再次单击 **=>** 按钮才能保存更改。

> [图：Variable 资源的属性编辑窗口]

你也可以在主 GMAT 窗口的资源树中双击已有的变量。这会打开上面的 `Variable` 属性框，允许你编辑该单个变量的值。

## 备注

GMAT 的 `Variable` 资源存储单个数值。在内部，无论是否存在小数部分，该值都以双精度实数存储。

## 示例

创建一个变量并赋予字面值：

```
Create ReportFile aReport

Create Variable aVar
aVar = 12

BeginMissionSequence

Report aReport aVar
```

说明：创建报告文件和变量 aVar，赋字面值 12，然后在任务序列中把 aVar 写入报告文件。

在任务序列命令中使用变量：

```
Create Spacecraft aSat
Create ForceModel anFM
Create ReportFile aReport

Create Propagator aProp
aProp.FM = anFM

Create Variable i step totalDuration nSteps

BeginMissionSequence

step = 60
totalDuration = 24*60^2     % one day
nSteps = totalDuration / step

% Report Keplerian elements every 60 seconds for one day
For i=1:nSteps
   Propagate aProp(aSat) {aSat.ElapsedSecs = step}
   Report aReport aSat.TAIModJulian aSat.SMA aSat.ECC aSat.INC ...
      aSat.RAAN aSat.AOP aSat.TA
EndFor
```

说明：用变量 step（60 秒）、totalDuration（一天的总秒数）和 nSteps（总步数）控制循环；For 循环中每次传播 60 秒，并报告历元及六个开普勒轨道根数，实现"一天内每 60 秒报告一次开普勒根数"。
