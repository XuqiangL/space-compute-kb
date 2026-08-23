# 脚本块命令（BeginScript）
> 译自 GMAT R2026a 帮助文档 BeginScript.html

BeginScript —— 执行自由格式的脚本命令。

## 脚本语法

```
BeginScript
    [script statements]
    ...
EndScript
```

## 描述

`BeginScript` 和 `EndScript` 命令（在 GUI 中称为 `ScriptEvent`）允许你在任务序列中编写自由格式的脚本语句，而这些语句不会在 GMAT GUI 中显示为单独的命令。这一特性可用于把复杂的语句序列分组并标记为一个单元，或者在使用 GUI 构建任务序列时编写小段脚本语句。在脚本本身中，`BeginScript`/`EndScript` 块内的语句与块外的语句在执行上没有任何区别。

**另请参见**："脚本编辑器（Script Editor）"一节

## GUI

> [图：ScriptEvent 的 GUI 编辑窗口]

`ScriptEvent` 的 GUI 窗口把命令分为三个部分：开头的注释、固定的 `BeginScript` 和 `EndScript` 命令，以及块本身的内容。该脚本窗口是主脚本编辑器的迷你版，具有行号、语法高亮、代码折叠以及完整编辑器中可用的所有编辑工具。更多信息请参见"脚本编辑器（Script Editor）"文档。`ScriptEvent` 窗口在应用更改时执行脚本语法验证。脚本语言中嵌套的 `BeginScript`/`EndScript` 块在加载到 GUI 时会被折叠为单个 `ScriptEvent`，保存到脚本时也会保存为单个 `BeginScript`/`EndScript` 块。

## 示例

在 `BeginScript`/`EndScript` 块内执行计算。当加载到 GUI 中时，`BeginScript`/`EndScript` 块内的计算会包含在单个 `ScriptEvent` 命令中。

```
Create Spacecraft aSat
Create Propagator aProp
Create ImpulsiveBurn aBurn
Create Variable a_init v_init
Create Variable a_transfer v_transfer_1 v_transfer_2
Create Variable a_target v_final mu
Create Variable dv_1 dv_2
mu = 398600.4415
a_target = 42164

BeginMissionSequence

% calculate Hohmann burns
BeginScript
    a_init = aSat.SMA
    v_init = aSat.VMAG
    a_transfer = (a_init + a_target) / 2
    v_transfer_1 = sqrt(2*mu/a_init - mu/a_transfer)
    v_transfer_2 = sqrt(2*mu/a_target - mu/a_transfer)
    v_final = sqrt(mu/a_target)
    dv_1 = v_transfer_1 - v_init
    dv_2 = v_final - v_transfer_2
EndScript

% perform burn 1
aBurn.Element1 = dv_1
Maneuver aBurn(aSat)

Propagate aProp(aSat) {aSat.Apoapsis}

% perform burn 2
aBurn.Element1 = dv_2
Maneuver aBurn(aSat)

Propagate aProp(aSat) {aSat.ElapsedSecs = aSat.OrbitPeriod}
```

说明：在 BeginScript/EndScript 块内用轨道力学公式计算霍曼转移的两次速度增量：由初始半长轴 a_init、初始速度 v_init 和目标半长轴 a_target 求转移轨道半长轴 a_transfer，再分别计算转移轨道在近地点和远地点的速度 v_transfer_1、v_transfer_2 以及目标圆轨道速度 v_final，最后得到两次机动的速度增量 dv_1、dv_2。块外依次施加第一次机动、传播到远地点、施加第二次机动，并传播一个轨道周期。在 GUI 中，这一整段计算只显示为一个 ScriptEvent 节点。
