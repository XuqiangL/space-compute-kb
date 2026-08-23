# 创建并配置力模型和积分器（Create_and_configure_Force_model_and_propagator）

> 译自 GMAT R2026a 帮助文档 Create_and_configure_Force_model_and_propagator.html

（本小节属于"第 16 章 仿真与估计航天器间跟踪"教程）

我们现在创建并配置将用于仿真的力模型和积分器。对于此星座，我们使用简化的力建模，仅计入地球引力效应，并禁用太阳光压和大气阻力建模。完成此配置的脚本片段如下所示。

```
%
%   Propagator and force model
%

Create ForceModel FM

FM.CentralBody  = Earth
FM.PointMasses  = {Earth}
FM.Drag         = None
FM.SRP          = Off
FM.ErrorControl = None

Create Propagator Prop

Prop.FM              = FM
Prop.Type            = 'RungeKutta56'
Prop.InitialStepSize = 60
Prop.Accuracy        = 1e-13
Prop.MinStep         = 0
Prop.MaxStep         = 60
Prop.MaxStepAttempts = 50
```

**中文说明**：创建力模型 FM——中心天体为地球，仅计入地球点质量引力，关闭大气阻力和太阳光压，ErrorControl 设为 None（定步长积分，导航估计的要求）；创建积分器 Prop——RungeKutta56 类型，初始步长 60 秒，精度 1e-13，最小步长 0，最大步长 60 秒，最大步尝试次数 50。
