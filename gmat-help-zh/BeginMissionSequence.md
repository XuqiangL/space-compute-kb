# 任务序列开始命令（BeginMissionSequence）
> 译自 GMAT R2026a 帮助文档 BeginMissionSequence.html

BeginMissionSequence —— 开始脚本的任务序列部分。

## 脚本语法

```
BeginMissionSequence
```

## 描述

`BeginMissionSequence` 命令标志着资源初始化的结束和 GMAT 脚本任务序列部分的开始。它必须作为脚本中的第一条命令出现一次，并且必须位于所有资源创建行之后。

**另请参见**：Script Language

## GUI

使用 GUI 任务树构建任务序列时，`BeginMissionSequence` 命令由 GMAT 自动管理。但是，当直接编辑 GMAT 脚本时（无论使用 GMAT 脚本编辑器还是外部编辑器），你必须手动插入 `BeginMissionSequence` 命令。

## 备注

`BeginMissionSequence` 是一个纯脚本命令，在 GUI 中工作时不需要它。它向 GMAT 表明：该命令以上的脚本部分由静态资源初始化组成，可以按任意顺序执行；该命令以下的部分由任务序列命令组成，必须按顺序执行。这一条以及脚本语言的其他规则在脚本语言参考中有详细讨论。

## 示例

一个传播航天器的最小 GMAT 脚本：

```
Create Spacecraft aSat
Create Propagator aProp

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

说明：先在初始化部分创建航天器和传播器两个资源；`BeginMissionSequence` 之后是任务序列，只有一条命令——把 aSat 传播 1 天。
