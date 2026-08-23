# 停止命令（Stop）
> 译自 GMAT R2026a 帮助文档 Stop.html

Stop —— 停止任务执行。

## 描述

`Stop` 命令在遇到该命令的位置停止当前任务的执行，并将控制权返回给 GMAT 界面。其效果类似于 GUI 工具栏上的 `Stop` 按钮。

## GUI

`Stop` 命令可以插入到任务树中或从任务树中删除，但该命令没有自己的 GUI 面板。

## 备注

`Stop` 命令停止的是当前任务的执行，而不是 GMAT 应用程序。在脚本停止点之前显示的所有数据（例如 `OrbitView` 窗口、`GroundTrack` 窗口）仍然可以操作。在循环或求解器结构中使用 `Stop` 命令时，执行将在首次遇到该命令的迭代处停止。

## 示例

在两条命令之间停止脚本的执行：

```
Create Spacecraft aSat
Create ForceModel aForceModel
Create Propagator aProp
aProp.FM = aForceModel

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 30};
Stop
Propagate aProp(aSat) {aSat.ElapsedDays = 30};
```

说明：第一段传播 30 天正常完成后遇到 `Stop`，任务停止，第二条 Propagate 永远不会执行。已显示的图形窗口仍可查看和操作。

停止求解器结构的执行以便进一步检查：

```
Create ChemicalTank aTank
Create ForceModel aForceModel
Create DifferentialCorrector aDC

Create Spacecraft aSat
aSat.Tanks = {aTank}

Create Propagator aProp
aProp.FM = aForceModel

Create ImpulsiveBurn anIB
anIB.DecrementMass = true
anIB.Tanks = {aTank}

BeginMissionSequence

Target aDC
Vary aDC(anIB.Element1 = 0.5)
Maneuver anIB(aSat)
Propagate aProp(aSat) {aSat.Periapsis}
If aSat.aTank.FuelMass < 10
Stop
EndIf
Achieve aDC(aSat.Altitude = 1000)
```

说明：在 Target 差分修正循环中，每次迭代执行机动并传播到近地点；若发现燃料箱剩余燃料小于 10，则执行 `Stop` 在该迭代处停止任务，便于用户检查求解器状态。若燃料充足，则继续执行 `Achieve` 并进入下一次迭代。
