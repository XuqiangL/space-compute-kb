# 创建并配置力模型和积分器（DSN_Estimation_Create_and_configure_Force_model_and_propagator）

> 译自 GMAT R2026a 帮助文档 DSN_Estimation_Create_and_configure_Force_model_and_propagator.html

我们现在创建并配置将用于仿真的力模型和积分器。对于这条深空漂移远离轨道，我们自然选择太阳作为中心天体。由于我们远离所有行星，我们使用点质量引力模型，并计入太阳、地球、月球和大多数其他行星的影响。此外，我们建模太阳光压（SRP）效应，并计入广义相对论对动力学的影响。完成此配置的脚本片段如下所示。

```
Create ForceModel Fm;
Create Propagator Prop;
Fm.CentralBody             = Sun;
Fm.PointMasses             = {Sun, Earth, Luna, Mars, Saturn, ...
                             Uranus, Mercury, Venus, Jupiter};
Fm.SRP                     = On;
Fm.RelativisticCorrection  = On;
Fm.ErrorControl            = None;
Prop.FM                    = Fm;
Prop.MinStep               = 0;    
```

**中文说明**：创建力模型 Fm 和积分器 Prop；中心天体为太阳，点质量引力包含太阳、地球、月球、火星、土星、天王星、水星、金星、木星；开启太阳光压和相对论修正；ErrorControl 设为 None（定步长）；积分器使用该力模型，最小步长为 0。

我们设置 `ErrorControl = None`，因为对于当前版本的 GMAT，批处理估计要求定步长数值积分。定步长由 `Prop.InitialStepSize` 给出，默认值为 60 秒。对于我们的深空轨道，动力学变化缓慢，此步长不算太大。对于动力学变化更剧烈的力模型，可能需要更小的步长。
