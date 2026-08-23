# 力模型（ForceModel）

> 译自 GMAT R2026a 帮助文档 ForceModel.html

**ForceModel** —— 用于指定传棒时的力建模选项，如重力、大气阻力、太阳光压和非中心天体引力。

## 描述

**ForceModel**（力模型）是对影响航天器运动的环境力和动力学的建模。GMAT 支持多种力，包括点质量引力和球谐重力模型摄动、大气阻力、太阳光压（SRP）、潮汐模型以及相对论修正。**ForceModel** 配置后挂载到 **Propagator**（传播器）对象上（配置 **Propagator** 时脚本与 GUI 配置方式的差异请参阅 **Propagator** 对象文档）。**Propagator** 与 **Propagate** 命令一起，使用 **ForceModel** 中配置的力来数值求解轨道运动方程（沿时间向前或向后）；在有动力飞行的情况下，还可包含推力项和质量流。有关如何为你的应用配置力模型的详细信息，请参阅下文的讨论。该资源不能在任务序列（Mission Sequence）中被修改。

**另请参阅**：Propagator、FiniteBurn

## 字段

| 选项 | 描述 |
|------|------|
| **CentralBody** | 传棒的中心天体。**CentralBody** 必须是一个天体，不能是 **LibrationPoint**（平动点）、**Barycenter**（质心）、**Spacecraft** 或其他特殊点。<br><br>**数据类型**：资源引用<br>**允许取值**：**CelestialBody**<br>**访问方式**：set<br>**默认值**：**Earth**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **Drag** | 已废弃。该字段已被 **Drag.AtmosphereModel** 取代。 |
| **Drag.AtmosphereModel** | 指定阻力（drag）力中使用的大气密度模型。仅当存在 **PrimaryBody**（主天体）时该字段才激活。<br><br>**数据类型**：枚举<br>**允许取值**：若 **PrimaryBody** 为 **Earth**：**None**、**JacchiaRoberts**、**MSISE86**（需插件）、**MSISE90**、**NRLMSISE00**、**Exponential**<br>若 **PrimaryBody** 为 **Mars**：**None**、**MarsGRAM2005**（需插件）、**Exponential**<br>其他 **PrimaryBody** 设置：**None**、**Exponential**（可通过用户生成的输入文件配置）<br>**访问方式**：set<br>**默认值**：**None**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **Drag.CSSISpaceWeatherFile** | CSSI 空间天气文件的文件名（可含路径信息）。文件格式详情见"备注"。<br><br>**数据类型**：String<br>**允许取值**：包含 CSSI 文件名（可含路径信息）的字符串<br>**访问方式**：set<br>**默认值**：`'SpaceWeather-All-v1.2.txt'`<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **Drag.DensityModel** | 当 **Drag.AtmosphereModel** 为 **MarsGRAM2005** 时启用。指定要使用的 Mars-GRAM 密度模型。**Mean** 为平均密度，叠加输入文件启用的任何可选波动模型扰动。**High** 为 **Mean** 密度加 1 倍标准差。**Low** 为 **Mean** 密度减 1 倍标准差。<br><br>**数据类型**：枚举<br>**允许取值**：**High**、**Low**、**Mean**<br>**访问方式**：set<br>**默认值**：**Mean**<br>**单位**：N/A<br>**接口**：脚本 |
| **Drag.DragModel** | 用户选择的用于阻力计算的航天器面积模型。<br><br>**数据类型**：枚举<br>**允许取值**：**Spherical、SPADFile**<br>**访问方式**：set<br>**默认值**：**Spherical**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **Drag.F107** | 波长 10.7 cm 处太阳通量的瞬时值。仅当存在 **PrimaryBody** 且当前天气来源设为常数值（ConstantFluxAndGeoMag）时该字段才激活。该设置的合理取值范围为 50 <= **Drag.F107** <= 400。<br><br>**数据类型**：Real<br>**允许取值**：**Drag.F107** >= 0<br>**访问方式**：set<br>**默认值**：150<br>**单位**：10^-22 W/m^2/Hz<br>**接口**：GUI、脚本 |
| **Drag.F107A** | 波长 10.7 cm 处太阳通量的 81 天滑动平均值。在脚本中，仅当存在 **PrimaryBody** 且当前天气来源设为常数值（ConstantFluxAndGeoMag）时该字段才激活。该设置的合理取值范围为 50 <= **Drag.F107A** <= 400。<br><br>**数据类型**：Real<br>**允许取值**：**Drag.F107A** >= 0<br>**访问方式**：set<br>**默认值**：150<br>**单位**：10^-22 W/m^2/Hz<br>**接口**：脚本 |
| **Drag.HistoricWeatherSource** | 定义地球密度建模所用历史太阳通量和地磁指数的来源。<br><br>**数据类型**：枚举<br>**允许取值**：**ConstantFluxAndGeoMag**、**CSSISpaceWeatherFile**<br>**访问方式**：set<br>**默认值**：**ConstantFluxAndGeoMag**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **Drag.InputFile** | 当 **Drag.AtmosphereModel** 为 **MarsGRAM2005** 或 **Exponential** 时启用。<br><br>对于 MarsGRAM2005，这是配置模型的 Mars-GRAM 输入 namelist 文件的路径。有关该文件中各项设置及 GMAT 如何使用它们的详情，请参阅 MarsGRAM2005 一节。相对路径相对于 GMAT 的 `bin` 目录。<br><br>对于 Exponential，这是指数阻力参数表文件的路径，用于设置高度分段、参考密度和标高设置。详情见指数阻力一节。<br><br>**数据类型**：String<br>**允许取值**：指向 Mars-GRAM 输入 namelist 文件或逗号分隔指数密度模型文件的有效路径<br>**访问方式**：set<br>**默认值**：`'../data/atmosphere/MarsGRAM2005/inputstd0.txt'`<br>**单位**：N/A<br>**接口**：脚本 |
| **Drag.MagneticIndex** | 密度计算中使用的地磁指数（Kp）。Kp 是行星际 3 小时平均地磁指数，用于度量太阳辐射的磁效应。仅当存在 **PrimaryBody** 且当前天气来源设为常数值（ConstantFluxAndGeoMag）时该字段才激活。<br><br>**数据类型**：Real<br>**允许取值**：0 <= Real <= 9<br>**访问方式**：set<br>**默认值**：3<br>**单位**：N/A<br>**接口**：脚本 |
| **Drag.PredictedWeatherSource** | 定义地球密度建模所用预报太阳通量和地磁指数的来源。<br><br>**数据类型**：枚举<br>**允许取值**：**SchattenFile、ConstantFluxAndGeoMag、CSSISpaceWeatherFile**<br>**访问方式**：set<br>**默认值**：**ConstantFluxAndGeoMag**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **Drag.SchattenErrorModel** | 从 Schatten 文件使用的误差模型。Schatten 预报包含均值、+2 sigma 和 -2 sigma 模型。文件格式详情见"备注"。<br><br>**数据类型**：枚举<br>**允许取值**：**Nominal**、**PlusTwoSigma**、**MinusTwoSigma**<br>**访问方式**：set<br>**默认值**：**Nominal**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **Drag.SchattenFile** | Schatten 文件的文件名（可含路径信息）。文件格式详情见"备注"。<br><br>**数据类型**：String<br>**允许取值**：包含 Schatten 文件名（可含路径信息）的字符串<br>**访问方式**：set<br>**默认值**：`'SchattenPredict.txt'`<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **Drag.SchattenTimingModel** | 从 Schatten 文件使用的时序模型。Schatten 预报包含标称太阳活动周模型、提前模型和滞后模型。文件格式详情见"备注"。<br><br>**数据类型**：枚举<br>**允许取值**：**NominalCycle**、**EarlyCycle**、**LateCycle**<br>**访问方式**：set<br>**默认值**：**NominalCycle**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **ErrorControl** | 控制如何估计当前积分步的误差。当前步的误差按所选的 **ErrorControl** 计算，并与 **Accuracy** 字段中设定的值比较，以确定该步误差可接受还是需要改进。所有误差度量都是相对误差，但相对误差的参考基准随 **ErrorControl** 的选择而变化。**RSSStep** 是相对于当前步测量的均方根和（Root Sum Square, RSS）相对误差。**RSSState** 是相对于当前状态测量的 RSS 相对误差。**LargestStep** 是相对于当前步测量的、相对误差最大的状态向量分量。**LargestState** 是相对于当前状态测量的、相对误差最大的状态向量分量。将 **ErrorControl** 设为 **None** 会关闭误差控制，积分器按数值积分器上 **InitialStepSize** 和 **MaxStep** 中较小者定义的固定步长积分。<br><br>**数据类型**：枚举<br>**允许取值**：**None**、**RSSStep**、**RSSState**、**LargestState**、**LargestStep**<br>**访问方式**：set<br>**默认值**：**RSSStep**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **External** | 指定使用外部力模型时从中获取动力学数据的 Python 脚本。该 Python 脚本可放置在 GMAT 安装目录的 userfunctions/python 文件夹中，或 GMAT 启动文件中由 **PYTHON_MODULE_PATH** 指定的任何文件夹中。名称不应包含 *.py 后缀。此参数若不为空，则表示将使用外部力模型。更多细节见下文"外部力模型"一节。<br><br>**数据类型**：String<br>**允许取值**：包含外部力模型 Python 脚本名的字符串<br>**访问方式**：set<br>**默认值**：**None**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **External.DerivativesFunction** | 指定使用外部力模型时 GMAT 要调用的 **External** Python 脚本中的函数名。更多细节见下文"外部力模型"一节。<br><br>**数据类型**：String<br>**允许取值**：包含 Python 函数名的字符串<br>**访问方式**：set<br>**默认值**：GetDerivatives<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **External.ExcludeOtherForces** | 为 true 时，GMAT 仅使用外部 Python 力模型进行积分，排除 **ForceModel** 中定义的任何 GMAT 力。为 false 时，该力将叠加到 **ForceModel** 中定义的其他任何力之上。更多细节见下文"外部力模型"一节。<br><br>**数据类型**：Boolean<br>**允许取值**：true, false<br>**访问方式**：set<br>**默认值**：false<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **GravityField.<主天体名>.Degree** | 谐波重力场的阶（degree）。仅当存在 **PrimaryBody** 时该字段才激活。<br><br>**数据类型**：Integer<br>**允许取值**：0 <= **Degree** <= 文件中的最大阶数<br>**访问方式**：set<br>**默认值**：4（在 GUI 中加载自定义文件时，GMAT 将 **Degree** 设为文件中的最大值）<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **GravityField.<主天体名>.Order** | 谐波重力场的次（order）。仅当存在 **PrimaryBody** 时该字段才激活。<br><br>**数据类型**：Integer<br>**允许取值**：0 <= **Order** <= 文件中的最大阶数，且 **Degree** <= **Order**<br>**访问方式**：set<br>**默认值**：4（在 GUI 中加载自定义文件时，GMAT 将 **Order** 设为文件中的最大值）<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **GravityField.<主天体名>.PotentialFile** | 重力位（gravity potential）文件。仅当存在 **PrimaryBody** 时该字段才激活。有关支持的文件类型及如何配置重力文件的详细说明，请参阅下文的讨论。<br><br>**数据类型**：String<br>**允许取值**：.cof 或 .grv 文件的路径和文件名<br>**访问方式**：set<br>**默认值**：JGM2.cof<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **GravityField.<主天体名>.StmLimit** | 计算状态转移矩阵（STM）时所用阶/次的上限。STM 不会使用超过 **Degree** 和 **Order** 字段或 **StmLimit** 所指定的阶/次。该字段不影响用于计算状态的阶/次，仅影响 STM。仅当存在 **PrimaryBody** 时该字段才激活。<br><br>**数据类型**：Integer<br>**允许取值**：**Int >= 0**<br>**访问方式**：set<br>**默认值**：100<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **GravityField.<主天体名>.TideFile** | 潮汐文件。仅当存在 **PrimaryBody** 时该字段才激活。有关支持的文件类型及如何配置潮汐文件的详细说明，请参阅下文的讨论。<br><br>**数据类型**：String<br>**允许取值**：.tide 文件的路径和文件名<br>**访问方式**：set<br>**默认值**：（无）<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **GravityField.<主天体名>.TideModel** | 潮汐模型类型的标志。该字段始终激活，但仅当天体具有谐波重力模型时才用于动力学计算。<br><br>**数据类型**：枚举<br>**允许取值**：**None**、**Solid**、**SolidAndPole**<br>**访问方式**：set<br>**默认值**：**None**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **Model** | gmat_startup_file.txt 文件中定义的"已配置"重力文件的 GUI 列表。**Model** 允许你在随 GMAT 分发的重力文件之间快速选择。例如，若 **PrimaryBody** 为地球，你可以在 GMAT 提供的地球重力模型（如 **JGM-2** 和 **EGM-96**）中选择。若选择 **Other**，你可以提供自定义重力文件的路径和文件名。<br><br>**数据类型**：String<br>**允许取值**：**JGM2**、**JGM3**、**EGM96**、**MARS50C**、**MGNP180U**<br>**访问方式**：set, get<br>**默认值**：**JGM2**<br>**单位**：N/A<br>**接口**：GUI |
| **PointMasses** | 在力模型中作为点质量处理的天体列表。一个天体不能同时是 **PrimaryBody** 又在 **PointMasses** 列表中。空列表 "{}" 将从列表中移除所有点质量。<br><br>**数据类型**：资源数组<br>**允许取值**：未选为 **PrimaryBody** 的 **CelestialBodies** 数组<br>**访问方式**：set<br>**默认值**：空列表<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **PrimaryBodies** | 以"复杂"力模型建模的天体。主天体可以拥有大气模型和谐波重力模型。如果你希望对多个天体建模谐波重力，可以指定多个主天体。关于使用多个谐波重力模型的重要注意事项，请参阅下文的备注。力模型的 **CentralBody** 应是主天体之一，且主天体不能包含在 **PointMasses** 字段中。<br><br>**数据类型**：资源引用<br>**允许取值**：未包含在 **PointMasses** 中的 **CelestialBody**<br>**访问方式**：set<br>**默认值**：Earth<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **RelativisticCorrection** | 开启或关闭相对论修正。<br><br>**数据类型**：枚举<br>**允许取值**：**On**、**Off**<br>**访问方式**：set<br>**默认值**：**Off**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **SRP** | 开启或关闭 SRP（太阳光压）力。SRP 配置的详细说明见"备注"一节。所用的 SRP 模型在 SRP.Model 字段中设置。<br><br>**数据类型**：枚举<br>**允许取值**：**On**、**Off**<br>**访问方式**：set<br>**默认值**：Off<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **SRP.ExtraShadowBodies** | SRP 掩食（eclipse）建模要考虑的额外天体。力模型的中心天体始终会被纳入阴影计算，但可以在此列表中添加更多天体。有关多个阴影天体情况下日照百分比如何计算的详情，请参阅下文"SRP 力建模的额外阴影天体"备注。<br><br>**数据类型**：天体列表<br>**允许取值**：**任何已定义的天体**<br>**访问方式**：set<br>**默认值**：空<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **SRP.Flux** | 1 AU 处的 SRP 通量值。在脚本中仅当 **SRP** 开启时该字段才激活。<br><br>**数据类型**：Real<br>**允许取值**：1200 < **SRP.Flux** < 1450<br>**访问方式**：set<br>**默认值**：1367<br>**单位**：W/m^2<br>**接口**：脚本 |
| **SRP.Flux_Pressure** | 1 AU 处的太阳通量除以光速。在脚本中仅当 SRP 开启时该字段才激活。SRP 配置的详细说明见"备注"一节。<br><br>**数据类型**：Real<br>**允许取值**：4.33e-6 < **SRP.Flux_Pressure** < 4.84e-6<br>**访问方式**：set<br>**默认值**：4.55982118135874e-006<br>**单位**：W *s/m^3<br>**接口**：脚本 |
| **SRP.SRPModel** | 用户选择的用于 SRP 计算的航天器面积模型。<br><br>**数据类型**：枚举<br>**允许取值**：**Spherical、SPADFile、NPlate**<br>**访问方式**：set<br>**默认值**：**Spherical**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **SRP.Nominal_Sun** | 用于将 SRP.Flux（1 AU 处的通量）按航天器到太阳的距离进行缩放的一个天文单位（AU）的公里数。在脚本中仅当 SRP 开启时该字段才激活。SRP 配置的详细说明见"备注"一节。<br><br>**数据类型**：Real<br>**允许取值**：135e6 < **Nominal_Sun** < 165e6<br>**访问方式**：set<br>**默认值**：149597870.691<br>**单位**：km<br>**接口**：脚本 |

## GUI

> [图：ForceModel 资源设置对话框]

**ForceModel** 对象的设置。
## 备注

### 主天体/中心天体与字段交互概述

在 GMAT 中，主天体（primary body）是以复杂力模型建模的天体，可包含球谐重力模型、潮汐或大气阻力。一个天体不能同时出现在 **PrimaryBodies** 和 **PointMasses** 字段中。GMAT 允许力模型中有多个主天体，但在定轨（orbit determination）时限制为单一主天体。

GMAT 目前要求主天体要么与 **CentralBody** 相同，要么在 GUI 中设为 **None**。如果你在 GUI 中更改 **CentralBody**，GMAT 会将主天体改为 **None**，然后你可以在 **None** 和中心天体之间选择。当你在 GUI 中选择主天体时，**Gravity** 和 **Drag** 字段会激活，允许你选择与 **PrimaryBodies** 字段中所选天体一致的模型。例如，如果你选择地球作为主天体，则只能在 **Drag.AtmosphereModel** 字段中选择地球阻力模型。可用模型见上文字段列表。

### 配置重力模型

GMAT 对所有天体支持点质量引力、球谐和潮汐建模。在 **Propagator** 上，所有天体被划分为两个互斥的类别：**PrimaryBodies**（主天体）和 **Point Masses**（点质量）。要将某天体建模为点质量，请将其加入 **PointMasses** 列表。在 GUI 中选择主天体时，**CentralBody** 与主天体必须相同。

建模为 **PointMasses** 的天体在运动方程中使用天体上定义的引力参数（即 Earth.Mu）。定义为 **PrimaryBodies** 的天体在运动方程中使用位文件（potential file）上定义的常数。GMAT 支持两种重力文件格式：.cof 格式和 STK .grv 格式。只要是受支持的格式，你可以为应用提供自定义位文件。启动文件中定义的位文件可在 GUI 的 **Model** 列表中选择。例如，启动文件中的以下行配置 GMAT，使主天体为地球时 EGM96 成为 GUI 中 **Model** 的可用选项：

```
EARTH_POT_PATH         = DATA_PATH/gravity/earth/
EGM96_FILE             = EARTH_POT_PATH/EGM96.cof 
```

上述启动文件配置定义了地球重力位文件路径，并将 EGM96.cof 注册为可用模型。

下面是配置自定义重力模型的脚本片段示例。

```
Create ForceModel aForceModel

aForceModel.CentralBody = Earth
aForceModel.PrimaryBodies = {Earth}
aForceModel.GravityField.Earth.Degree = 21
aForceModel.GravityField.Earth.Order  = 21
aForceModel.GravityField.Earth.PotentialFile = 'c:\MyData\File.cof'
```

上述脚本创建力模型，中心天体和主天体均为地球，重力场阶/次均设为 21，并使用自定义位文件 `c:\MyData\File.cof`。

### 使用多个谐波重力模型

GMAT 允许同时对多个天体建模非球谐重力场。这是一项高级能力，应谨慎使用，因为很容易在不知情的情况下配置错误并得到不准确的结果。用户应注意，太阳系中极少有需要此能力的情形，应首先考虑其使用是否恰当或必要。该功能的一个关键方面是正确选择力模型的中心天体——通常应选择其引力影响球（sphere of influence）包含轨迹的天体。如果选择使用此功能，用户应仔细选择 **ForceModel** 的 **CentralBody**，并可能希望在不同中心天体假设下检验结果。

在轨道设计与优化中，常见的最佳实践不是使用多个谐波重力模型，而是按引力影响球对轨迹分段，在每个影响球内使用仅含一个主天体的力模型。**Ex_LunarTransfer** 和 **Ex_MarsBPlane** 示例脚本就是很好的例子。

当前版本的 GMAT 允许在轨道设计与任务规划工作中使用多个谐波重力模型，但在执行定轨相关任务时，限制谐波重力模型只能用于单一中心天体设置。

下面的脚本摘录展示了如何同时为地球和月球（Luna）配置谐波重力建模。

```
Create ForceModel FM

FM.CentralBody                      = Earth;
FM.PrimaryBodies                    = {Earth, Luna};
FM.PointMasses                      = {Sun, Venus, Jupiter, Saturn};
FM.GravityField.Earth.Degree        = 12;
FM.GravityField.Earth.Order         = 12;
FM.GravityField.Earth.TideModel     = 'None';
FM.GravityField.Earth.PotentialFile = 'EGM96.cof';
FM.GravityField.Luna.Degree         = 50;
FM.GravityField.Luna.Order          = 50;
FM.GravityField.Luna.PotentialFile  = 'grgm900c.cof';
FM.GravityField.Luna.TideModel      = 'None';
FM.SRP                              = On
FM.ErrorControl                     = 'None'
```

上述脚本配置力模型 FM：中心天体为地球，主天体为地球和月球（分别使用 EGM96 12×12 和 grgm900c 50×50 谐波重力场），太阳、金星、木星、土星为点质量引力，开启 SRP，并关闭误差控制。
### 力模型设置与 CentralBody 的选择会极大影响结果的精度

> **警告**：**有时，即使你可能不这么认为，也必须在力模型中包含太阳系其他天体的引力。** 当 GMAT 传棒 **Spacecraft** 时，**CentralBody** 参数用作数值积分的基准。具体而言，GMAT 使用卫星相对于 **CentralBody** 的"相对"运动方程。该方程包含来自太阳和太阳系其他行星的项。（参见例如 A. E. Roy 所著《Orbital Motion》第 2 版 6.2 节"相对运动方程"。）如果 GMAT 用户的 **Spacecraft** 处于多体轨道区域，或用户正在切换 **CentralBody**，或正在使用非推荐（如下文所述）的 **CentralBody**，*用户必须在 **ForceModel** 中包含太阳系其他天体的引力*。注意，最佳实践还包括使用与作用在你的 **Spacecraft** 上的主导引力相对应的 **CentralBody**。例如，如果你的 **Spacecraft** 处于月球低轨，月球引力将是主导引力。因此，你应使用月球而非地球作为 **CentralBody**。还可以考虑在传棒过程中，随着 **Spacecraft** 接近不同的引力影响球而切换中心天体。

### 潮汐模型字段交互概述

默认情况下，潮汐数据源设为 **None**，且若未选择潮汐模型，潮汐模型选择器处于禁用状态。要使用潮汐模型，首先必须将潮汐数据源更改为 **Inherited**（继承）或 **Tide File**（潮汐文件），此后潮汐模型选择器才会启用，可从该潮汐数据源支持的潮汐模型中选择。可用模型见上文字段列表。**Inherited** 选项表示潮汐模型的数据由重力位文件提供，或内置于 GMAT 中。重力位文件中包含的潮汐数据优先于任何内置值。**Tide File** 选项启用文件选择器，用于选择包含 Love 数（Love numbers）的文件作为潮汐模型的数据源。潮汐文件中包含的潮汐数据优先于所有其他潮汐数据源。

### 配置潮汐模型

GMAT 对所有中心天体支持固体潮（solid tide）建模，对地球支持固体潮和极潮（pole tide）建模。潮汐模型仅在设置了 **PrimaryBody** 时才能使用。GMAT 内置了地球的固体潮和极潮数值。也可以使用外部文件提供潮汐模型所用的 Love 数——可以来自支持潮汐的重力文件，或单独的潮汐文件。

如果提供了含 Love 数的重力文件，这些 Love 数将用于固体潮模型计算。如果提供了潮汐文件，将使用潮汐文件中的 Love 数。如果同时提供了含 Love 数的重力文件和潮汐文件，两个文件的 Love 数都会被使用，且潮汐文件中的 Love 数优先于重力文件。仅当未提供潮汐文件且重力位文件不含 Love 数时，才使用 GMAT 的地球默认 Love 数。GMAT 的内置值是极潮的唯一数据源。

下面是配置包含月球固体潮的自定义重力模型的脚本片段示例。

```
Create ForceModel aForceModel

aForceModel.CentralBody = Luna
aForceModel.PrimaryBodies = {Luna}
aForceModel.GravityField.Luna.Degree = 21
aForceModel.GravityField.Luna.Order  = 21
aForceModel.GravityField.Luna.PotentialFile = 'c:\MyData\File.cof'
aForceModel.GravityField.Luna.TideFile = 'c:\MyData\File.tide'
aForceModel.GravityField.Luna.TideModel = 'Solid'
```

上述脚本创建以月球为中心天体和主天体的力模型，重力场阶/次为 21，使用自定义位文件和潮汐文件，潮汐模型设为固体潮（Solid）。

潮汐文件使用 .tide 文件扩展名。只要符合受支持的格式，你可以为应用提供自定义潮汐文件。潮汐文件包含用于建模固体潮的 Love 数。潮汐文件可包含 k2、k3 和 k+ 系数。潮汐文件使用的格式为 `k {阶} {次} {值}`，k+ 的格式为 `kplus {次} {值}`。

下面是一个潮汐文件示例，内容为 GMAT 用于地球的内置 Love 数值。

```
k 2 0 0.30190
k 2 1 0.29830
k 2 2 0.30102
k 3 0 0.093
k 3 1 0.093
k 3 2 0.093
k 3 3 0.094
kplus 0 -0.00087
kplus 1 -0.00079
kplus 2 -0.00057
```

上述潮汐文件给出了二阶（k2）、三阶（k3）Love 数及 k+ 修正系数的取值。

### 零潮（Zero Tide）与无潮（Tide Free）模型

潮汐模型的选择与所使用的重力位模型密切相关。某些重力位模型将部分潮汐效应并入了重力位模型中。重力模型处理潮汐力建模的两种常见方式是无潮（tide-free）和零潮（zero-tide）。无潮重力模型的重力位中不含潮汐力效应，而零潮重力模型包含潮汐对重力位的永久（时不变）效应。对于 STK .grv 文件，GMAT 识别 "IncludesPermTides" 关键字以判断重力位模型是否包含永久潮汐效应，但 "TideFreeValues" 和 "ZeroTideValues" 关键字块中的系数目前被忽略。

> **当心**：如果将零潮重力模型与 **Solid** 或 **SolidAndPole** 潮汐选项一起使用，永久潮汐的效应会被重复计算，可能产生不准确的结果。更深入的讨论请参阅《IERS 规范（2010）》（IERS Conventions (2010)）。GMAT 不会在零潮与无潮重力位之间进行转换，因此用户必须注意自己打算使用哪种重力位，尤其是在建模固体潮时。
### 配置阻力模型

GMAT 为地球支持多种密度模型，包括 **Jacchia-Roberts** 和各种 MSISE 模型。非地球天体的密度模型——例如 Mars-GRAM 模型——通过自定义插件组件引入。对于任何密度模型，用户还可以选择使用球形航天器面积模型或 SPAD 文件进行航天器面积计算。航天器面积建模通过 **Drag.DragModel** 参数选择。SPAD 面积建模的更多细节见 Spacecraft Ballistic/Mass Properties 文档。

要配置地球密度模型，请选择地球作为主天体。在 GUI 中，这会激活 **AtmosphereModel** 列表。选择大气模型后，你可以使用 **AtmosphereModel** 列表旁的 **Setup** 按钮配置太阳通量值。下面是配置 **NRLMSISE00** 密度模型的脚本片段示例。

```
Create ForceModel aForceModel

aForceModel.PrimaryBodies = {Earth}
aForceModel.Drag.AtmosphereModel = NRLMSISE00
```

上述脚本创建力模型，主天体为地球，大气阻力密度模型选用 NRLMSISE00。

> **当心**：GMAT 使用由 MSISE 模型创建者编写的原始单精度 FORTRAN 代码。在低高度处，单精度密度会在双精度积分器的步长控制中引起数值问题，积分可能慢到不可接受。你可以通过使用定步长积分，或使用相对较高的 **Accuracy** 值（如 1e-8）来避免性能问题。你可能需要试验 **Accuracy** 设置，找到适合你的应用的取值。

注意，当你为 **Drag.AtmosphereModel** 选择 **None** 时，与密度配置关联的字段（如 **Drag.F107**、**Drag.F107A**、**Drag.MagneticIndex** 等）为非激活状态，必须从脚本文件中移除以避免解析错误。在 GUI 中操作时，此过程会自动完成。

下表说明了 GMAT 支持的阻力模型的高度限制。

| 模型 | 理论高度 (h) 限制 | 备注 |
|------|------------------|------|
| **MSISE86** | 90 < h < 1000 | GMAT 不允许在 90 km 高度以下传棒。 |
| **MSISE90** | 0 < h < 1000 | GMAT 允许在 0 km 高度以下传棒，但结果非物理。 |
| **NRLMSISE00** | 0 < h < 1000 | GMAT 允许在 0 km 高度以下传棒，但结果非物理。 |
| **JacchiaRoberts** | h > 100 | GMAT 不允许在 100 km 高度以下传棒。 |
| **Exponential** | h > 0 | 使用指数密度模型传棒无上下高度限制。 |

#### MarsGRAM2005

当 **PrimaryBody** 为 **Mars** 时，你可以选择 Mars-GRAM 2005 作为大气模型。该模型仅在 `libMarsGRAM` 插件可用并在 GMAT 启动文件中启用时可用。

> **警告**：自 R2015a 版本起，一个给定脚本中只能有一种唯一的 Mars-GRAM 力模型配置。如果你包含多个带有不同 Mars-GRAM 配置的 Mars-GRAM 力模型的传播器，不同的配置将不会被采纳，所有传播器将使用相同的 Mars-GRAM 配置。

使用 **MarsGRAM2005** 大气模型时，脚本语言（而非 GUI）中提供三个新字段：

- **Drag.InputFile**
- **Drag.DensityModel**

这些字段的详情见"字段"一节。此外，空间天气字段按如下方式处理：

- **Drag.F107**：1 AU 处 10.7 cm 太阳通量的值，如"字段"一节所述
- **Drag.F107A**：不使用
- **Drag.MagneticIndex**：不使用

Mars-GRAM 2005 输入文件是 FORTRAN namelist 格式的文本文件。该文件中的大多数变量直接传递给 Mars-GRAM 模型并按其本意使用。然而，某些变量会被 GMAT 提供的值内部替换。下表列出了被特殊处理的输入变量。

| 输入变量 | GMAT 的用法 |
|----------|-------------|
| （未列出者） | 直接传递给 Mars-GRAM 2005 模型 |
| `DATADIR` | 始终为 `'../data/atmosphere/MarsGRAM2005/binFiles'` |
| `GCMDIR` | 始终为 `'../data/atmosphere/MarsGRAM2005/binFiles'` |
| `IERT` | 始终为 1（地球接收时间） |
| `IUTC` | 始终为 0（TT 时间） |
| `MONTH` | 由当前传棒历元替换 |
| `MDAY` | 由当前传棒历元替换 |
| `MYEAR` | 由当前传棒历元替换 |
| `NPOS` | 始终为 1 |
| `IHR` | 由当前传棒历元替换 |
| `IMIN` | 由当前传棒历元替换 |
| `ISEC` | 由当前传棒历元替换 |
| `LonEW` | 始终为 1（东经为正） |
| `F107` | 由 **Drag.F107** 的值替换 |
| `FLAT` | 由当前传棒状态替换 |
| `FLON` | 由当前传棒状态替换 |
| `FHGT` | 由当前传棒状态替换 |
| `MOLAhgts` | 始终为 0（参考椭球面） |
| `iup` | 始终为 0（无输出） |
| `ipclat` | 始终为 0（行星中心纬度输入） |
| `requa` | 由 **Mars.EquatorialRadius** 的值替换 |
| `rpole` | 由 GMAT 的火星极半径值替换（由 **Mars.EquatorialRadius** 和 **Mars.Flattening** 计算得出） |

输入文件由 Mars-GRAM 2005 模型代码读取，该代码的错误检查能力有限。如果输入文件或数据文件不正确或缺失，GMAT 可能表现出非预期行为。注意，Mars-GRAM 2005 模型返回的局部风不包含在 GMAT 的阻力模型中。

#### Exponential（指数模型）

对于任何 **PrimaryBody** 设置，GMAT 都可以基于指数大气密度模型建模大气阻力。系统出厂配置支持对 **Earth** 或 **Mars** 使用该模型。

使用 **Exponential** 大气模型时，GMAT 通过脚本语言（而非 GUI）中的以下字段指定的文本文件来配置模型：

- **Drag.InputFile**

该字段的详情见"字段"一节。使用 **Exponential** 模型时，其他空间天气字段被忽略。这些字段是：

- **Drag.F107**：不使用
- **Drag.F107A**：不使用
- **Drag.MagneticIndex**：不使用

指数大气输入文件是一个文本文件，包含三列逗号分隔的数据，按高度定义大气密度，高度以公里为单位、从支持大气的中心天体表面起算。高度被划分为若干分段。每个高度分段的底部由数据文件第一列的值指定。第二列指定该高度处的大气密度，单位为千克每立方米。第三列是标高（scale height）参数（单位公里），用于调整指数曲线形状以匹配期望的密度剖面。

> **注意**：如果输入的指数密度模型文件不包含低至 0 km 高度的记录，GMAT 将使用文件中的第一条记录来计算低于第一条记录高度的密度。

GMAT 中实现的指数模型的细节可参阅 David A. Vallado 所著《Fundamentals of Astrodynamics and Applications》第五版（2022）第 8.6 节。
### JacchiaRoberts 和 MSIS 地球大气密度模型的空间天气数据

GMAT 为 **JacchiaRoberts** 和 MSIS 地球大气密度建模支持多种空间天气输入类型，包括常数通量和地磁指数值、历史数据文件以及预报数据文件。你可以分别配置历史数据和预报数据所用的数据。对于历史数据，你可以在常数值和 CSSI 空间天气文件之间选择。对于预报数据，你可以在常数值、CSSI 空间天气文件和 Schatten 预报文件之间选择。下面对每种来源进行详细讨论。

数据源的优先级由当前传棒历元（即密度求值时的历元）和数据文件包含的历元决定。应用以下规则：

- 如果历史数据和预报数据源都设为 **ConstantFluxAndGeoMag**，则始终使用常数值。
- 如果你选择 CSSI 文件作为历史数据源，且当前传棒历元早于 CSSI 文件观测数据块的最后一行数据，则使用 CSSI 数据。如果当前传棒历元晚于 CSSI 观测数据块的最后一条记录，则使用指定的预报数据源。如果传棒历元早于第一条观测数据记录，则使用文件中的第一条记录。
- 如果你选择 Schatten 文件作为预报数据源、CSSI 文件作为历史源，GMAT 将在 CSSI 数据文件观测数据块结束时切换到 Schatten 文件。
- 如果你选择 Schatten 文件作为预报数据源、**ConstantFluxAndGeoMag** 作为历史源，GMAT 将在 Schatten 数据记录开始时切换到 Schatten 数据文件。
- Schatten 文件选项不能用作历史空间天气源。

### 常数值

GMAT 为 **JacchiaRoberts** 和 MSIS 地球密度模型支持常数通量和地磁指数值。下面以 NRLMSISE00 为例，展示如何配置 GMAT 对历史和预报数据使用这些值。

```
Create ForceModel aForceModel

aForceModel.Drag.AtmosphereModel = NRLMSISE00
aForceModel.Drag.HistoricWeatherSource = 'ConstantFluxAndGeoMag'
aForceModel.Drag.PredictedWeatherSource = 'ConstantFluxAndGeoMag'
aForceModel.Drag.F107 = 150
aForceModel.Drag.F107A = 150
aForceModel.Drag.MagneticIndex = 3
```

上述脚本将大气模型设为 NRLMSISE00，历史和预报天气源均设为常数值，并指定 F107、F107A 太阳通量和 Kp 地磁指数的取值。

### CSSI 空间天气数据

你可以为 **JacchiaRoberts** 和 MSIS 地球大气密度模型提供空间标准与创新中心（Center for Space Standards and Innovation, CSSI）文件作为历史和预报空间天气数据。CSSI 文件格式在 [Celestrak](https://celestrak.com/SpaceData/) 网站有详细说明，文件可在该站点及[此处](ftp://ftp.agi.com/pub/DynamicEarthData/)下载。你可以按如下方式配置 GMAT 对历史和预报数据使用 CSSI 文件。此文件仅用于 JacchiaRoberts 和 MSIS 模型选项。

```
Create ForceModel aForceModel

aForceModel.Drag.AtmosphereModel = NRLMSISE00
aForceModel.Drag.HistoricWeatherSource = 'CSSISpaceWeatherFile'
aForceModel.Drag.PredictedWeatherSource = 'CSSISpaceWeatherFile'
aForceModel.Drag.CSSISpaceWeatherFile = 'SpaceWeather-All-v1.2.txt'
```

上述脚本将大气模型设为 NRLMSISE00，历史和预报天气源均设为 CSSI 空间天气文件，并指定文件名 `SpaceWeather-All-v1.2.txt`。

你可以提供文件的完整路径或相对路径，或将文件放入 GMAT 启动文件帮助中所述的数据文件夹中。

### Schatten 空间天气数据

你可以按如下方式配置 GMAT 使用 Schatten 预报数据。Schatten 数据文件只能用作预报空间天气数据，且仅与 **JacchiaRoberts** 和 MSIS 密度模型一起使用。

```
Create ForceModel aForceModel

aForceModel.Drag.AtmosphereModel = NRLMSISE00
aForceModel.Drag.PredictedWeatherSource = 'SchattenFile'
aForceModel.Drag.SchattenFile = 'SchattenPredict.txt'
aForceModel.Drag.SchattenErrorModel = 'Nominal'
aForceModel.Drag.SchattenTimingModel = 'NominalCycle'
```

上述脚本将大气模型设为 NRLMSISE00，预报天气源设为 Schatten 文件，并指定文件名、误差模型（Nominal）和时序模型（NominalCycle）。

Schatten 文件由戈达德航天飞行中心（Goddard Space Flight Center）的飞行动力学设施（Flight Dynamics Facility, FDF）分发，并在社区协调建模中心（Community Coordinated Modeling Center, CCMC）网站上提供。你可以在 https://iswa.ccmc.gsfc.nasa.gov/iswa_data_tree/model/solar/FDF/SchattenSolarFluxPrediction 网址访问当前和历史的 Schatten 数据文件。注意，从 CCMC 下载 Schatten 文件时，必须手动添加 BEGIN_DATA 和 END_DATA 标记，如下例所示。

你可以提供文件的完整路径或相对路径，或将文件放入 GMAT 启动文件帮助中所述的数据文件夹中。此外，你可以在 **SchattenErrorModel** 的 **Nominal**、**PlusTwoSigma** 和 **MinusTwoSigma** 之间选择，在 **SchattenTimingModel** 的 **NominalCycle**、**EarlyCycle** 和 **LateCycle** 之间选择。注意，GMAT 读取的原始文件包含均值、+2 sigma、-2 sigma 与标称、提前、滞后太阳活动周的全部组合。来自 FDF 的文件必须经过修改，加入指示数据起止的关键字，如下所示：

```
           NOMINAL TIMING      EARLY TIMING        LATE TIMING      
 mo. yr.  mean +2sig -2sig ap mean +2sig -2sig ap mean +2sig -2sig ap
BEGIN_DATA 
  2 2011    92  107   76    9  105  125   85   10   77   87   66    8
  3 2011    93  110   77    9  106  128   86   10   79   89   67    8
  4 2011    95  112   78    9  108  129   87   10   80   92   69    8
END_DATA
```

上述 Schatten 文件示例包含标称/提前/滞后三种时序下各自的均值、+2σ、-2σ 太阳通量预报和 ap 地磁指数。

数据必须按 FORMAT(I3,I5,I6,11I5) 格式化，且 BEGIN_DATA 和 END_DATA 关键字之间不能出现注释或空行。
### 配置 SRP 模型

GMAT 支持球形 SRP 模型，以及用于高精度 SRP 建模的 SPAD 文件。两种模型都使用双锥（dual cone）模型来描述中心天体对航天器的遮挡。有关为航天器配置 SPAD 文件，请参阅 Spacecraft Ballistic/Mass Properties 文档。下面的脚本片段展示了如何配置两个 **ForceModel**，一个使用 **Spherical** 面积建模（默认），一个使用 **SPADFile**。

```
% A spherical SRP model
Create ForceModel aForceModel_1

aForceModel_1.PrimaryBodies = {Earth}
aForceModel_1.SRP = On
aForceModel_1.SRP.SRPModel = Spherical

% A SPAD SRP model
Create ForceModel aForceModel_2

aForceModel_2.PrimaryBodies = {Earth}
aForceModel_2.SRP = On
aForceModel_2.SRP.SRPModel = SPADFile
```

上述脚本创建两个力模型：第一个使用球形 SRP 面积模型，第二个使用 SPAD 文件进行高精度 SRP 建模。

你可以用两种方法定义太阳通量，目前仅在脚本接口中支持。一种方法是使用 **SRP.Flux** 字段定义通量值，并使用 **Nominal_Sun** 字段定义天文单位（以 km 计），如下例所示。

```
Create ForceModel aForceModel

aForceModel.PrimaryBodies = {Earth}
aForceModel.SRP = On
aForceModel.SRP.Flux = 1367
aForceModel.SRP.Nominal_Sun = 149597870.691
```

上述脚本开启 SRP，用 SRP.Flux 指定 1 AU 处太阳通量（1367 W/m^2），并用 Nominal_Sun 指定天文单位长度。

另一种方法是使用 **Flux_Pressure** 字段定义 1 个天文单位处的通量压强，如下所示。

```
Create ForceModel aForceModel

aForceModel.PrimaryBodies = {Earth}
aForceModel.SRP = On
aForceModel.SRP.Flux_Pressure = 4.53443218374393e-006
aForceModel.SRP.Nominal_Sun = 149597870.691
```

上述脚本改用 SRP.Flux_Pressure 直接指定 1 AU 处的光压通量（单位 W·s/m^3）。

如果你混用通量设置（如下例所示），GMAT 将使用脚本中最后出现的方法。此处，GMAT 将使用 **Flux_Pressure** 设置。

```
Create ForceModel aForceModel

aForceModel.PrimaryBodies = {Earth}
aForceModel.SRP = On
aForceModel.SRP.Flux = 1370
aForceModel.SRP.Nominal_Sun = 149597870
aForceModel.SRP.Flux_Pressure = 4.53443218374393e-006
```

> **当心**：GMAT 配置 SRP 模型太阳通量的默认选项是使用 **SRP.Flux** 和 **Nominal_Sun** 字段。如果你最初配置的是 **Flux_Pressure** 字段，当你通过工具栏保存按钮保存任务时，GMAT 会写出与你的 **Flux_Pressure** 设置相一致的 **SRP.Flux** 和 **Nominal_Sun** 值。

### SRP 力建模的额外阴影天体

除了轨道中心天体外，GMAT 还可以建模额外阴影天体的影响。例如，绕地球运行的航天器有时会遭遇月球掩食，绕月球运行的航天器有时会遭遇地球掩食。

> **注意**：建议所有建模 SRP 的地球轨道航天器在 SRP **ExtraShadowBodies** 列表中包含 Luna，所有绕月航天器在 **ExtraShadowBodies** 列表中包含地球。

太阳光压力取决于航天器暴露于阳光的百分比。如果航天器处于全日照，日照百分比因子为 1；当航天器处于本影（全阴影）时，日照百分比因子为 0，即 SRP 力为零。当 GMAT 检测到多个天体同时遮挡航天器时，将分别计算每个遮挡天体的总日照百分比因子，然后应用以下规则：

- 如果任一天体的日照百分比为 0，则该天体完全遮挡太阳，整体日照百分比为零。
- 如果太阳被两个天体部分遮挡，且这两个天体在太阳圆面上不重叠，则日照百分比为太阳圆面未被两个天体遮蔽的部分。
- 如果太阳被两个以上天体部分遮挡，或被两个相互重叠的天体遮挡，则 SRP 的整体日照百分比取各遮挡天体中的最小值。

### 变分方程与 STM

GMAT 可以选择性地传棒轨道状态转移矩阵（State Transition Matrix, STM）。有关如何配置 GMAT 计算 STM 的更多信息，请参阅 Propagate 命令文档。

> **当心**：GMAT 允许你将状态转移矩阵（STM）与轨道状态一起传棒。然而，并非所有变分项都已实现用于 STM 传棒。已实现的有：点质量摄动、球谐（含潮汐模型）、大气阻力和太阳光压。未实现的有：相对论项和有限推力（finite burns）。此外，SRP 变分项不包含阴影百分比对轨道状态的偏导数。对于半影持续时间较短的轨道，此近似是可接受的；但对于在半影中停留时间相对较长的轨道，此近似不准确。

### 外部力模型

此功能扩展了 GMAT **ForceModel** 的能力，允许在 GMAT 积分器中使用外部的、由 Python 定义的力模型。Python 脚本可添加到 Python userfunctions 文件夹，或 GMAT 启动文件中由 **PYTHON_MODULE_PATH** 指定的任何其他文件夹。此外，必须配置 GMAT 的 Python 接口。要使用外部力模型，请创建一个包含 GMAT 在轨道积分期间将调用的函数的 Python 脚本。默认情况下，该函数应命名为 GetDerivatives()，但可以使用 **ForceModel.External.DerivativesFunction** 参数更改函数名。该函数必须按下述顺序接收四个参数。这些参数的 Python 名称可由用户在 Python 函数定义内更改：

- state：列表，传棒状态向量。该向量的大小和内容可变，取决于用户的 **ForceModel** 和 **Propagator** 配置。仅包含浮点值。
- epoch：浮点数，当前历元，**A1ModJulian** 格式。
- description：列表，描述每个状态向量项的字符串列表。该列表的大小和顺序与状态向量一致。
- order：整数（1 或 2），ExternalForceModel 要计算的导数阶数。若 order 为 1，返回值为状态向量的一阶导数。若 order 为 2，返回值为二阶导数。大多数 GMAT 积分器仅使用一阶导数。目前唯一使用二阶导数的积分器是 RungeKutta68。

导数函数必须返回与状态向量大小匹配的浮点数列表。使用下表帮助你确定 GMAT 期望从导数函数接收到什么。请确保导数函数返回的列表顺序与传入函数的状态参数列表描述中指定的顺序一致。任何要返回的矩阵（如 **A** 矩阵）必须先重塑为线性数组，并按正确顺序附加到状态导数之后。

| 状态分量 | GMAT 提供的内容 | 导数函数应返回的内容 | 备注 |
|----------|----------------|---------------------|------|
| CartesianState | 中心天体惯性系（J2000 轴）中的位置和速度 | 对于一阶积分器，返回 [vx, vy, vz, ax, ay, az]，其中 [ax, ay, az] 是惯性坐标系中外力的加速度分量。对于二阶积分器，返回 [ax, ay, az, 0, 0, 0]。 | 返回列表中的速度分量被忽略；GMAT 会自动用状态向量中的速度替换。速度分量可以返回零。大多数 GMAT 积分器是一阶积分器。RungeKutta68 是目前唯一实现的二阶积分器。 |
| TotalMass | 当前航天器质量（kg） | 质量流率 dm/dt | 单位为 kg/sec。 |
| STM（状态转移矩阵） | 从 **t_(i-1)** 到 **t_i** 的状态转移矩阵 Φ_i，即 Φ_i = Φ(t_(i-1), t_i) | **A** 矩阵 | A 矩阵的定义见 GMAT 数学规范（Math Specification）第 4.1.3 节和式 4.14。 |
| Covariance（协方差） | 一个 6x6 占位矩阵。 | 一个 6x6 占位矩阵。这些值可以是任意值（建议为零），必须由用户在偏导数向量的适当位置返回，但它们对协方差传棒没有影响。 | 外部力模型目前对协方差传棒没有影响。如果使用外部力模型并传棒协方差，状态中会包含一个标记为 "Covariance" 的额外 6x6 矩阵。该矩阵应被忽略。但是，用户必须用 36 个占位元素填充返回的偏导数向量。 |

> **注意**：返回一阶导数时，GMAT 将忽略前三个值。这些值对应状态向量中第一个 **Spacecraft** 的笛卡尔速度。GMAT 内部会从当前状态向量中获取这些值。建议用户为这三个值返回 [0.0, 0.0, 0.0]。

> **注意**：由于外部力模型需要使用外部 Python 脚本，用户可以将此脚本连接到 GMAT 的 Python API。这带来了多种功能，包括让用户能够在导数函数内部访问各种航天器参数。需要注意：在外部力模型函数内通过 API 访问的航天器参数可能并不总是最新的。内部航天器对象并非每一步都更新，因为各种积分器会执行子步，其间状态数据可能发生变化。GMAT 航天器对象仅在完成一个完整步后才更新。凡包含在状态向量参数中的数据，都应只从直接传入外部力模型导数函数的状态向量参数中访问。然而，任何未直接传入导数函数的数据都可以安全地从 API 访问。
## 示例

用于点质量传棒的 **ForceModel**。

```
Create Spacecraft aSat
Create ForceModel aForceModel

aForceModel.CentralBody = Earth
aForceModel.PointMasses = {Earth}

Create Propagator aProp

aProp.FM = aForceModel

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = .2}
```

上述脚本创建航天器和力模型，中心天体为地球，仅将地球作为点质量引力，然后传棒 0.2 天。

用于高精度低地球轨道传棒的 **ForceModel**。

```
Create Spacecraft aSat
Create ForceModel aForceModel

aForceModel.CentralBody = Earth
aForceModel.PrimaryBodies = {Earth}
aForceModel.PointMasses = {Sun, Luna}
aForceModel.SRP = On
aForceModel.RelativisticCorrection = On
aForceModel.ErrorControl = RSSStep
aForceModel.GravityField.Earth.Degree = 20
aForceModel.GravityField.Earth.Order = 20
aForceModel.GravityField.Earth.PotentialFile = 'EGM96.cof'
aForceModel.GravityField.Earth.TideModel = 'None'
aForceModel.Drag.AtmosphereModel = MSISE90
aForceModel.Drag.F107 = 150
aForceModel.Drag.F107A = 150
aForceModel.Drag.MagneticIndex = 3
aForceModel.SRP.Flux = 1359.388569998901
aForceModel.SRP.SRPModel = Spherical;
aForceModel.SRP.Nominal_Sun = 149597870.691

Create Propagator aProp

aProp.FM = aForceModel

BeginMissionSequence

Propagate aProp(aSat){aSat.ElapsedDays = .2}
```

上述脚本配置高精度低地球轨道力模型：地球 EGM96 20×20 谐波重力场，太阳和月球点质量引力，开启 SRP（球形模型）和相对论修正，MSISE90 大气阻力模型（常数空间天气），误差控制为 RSSStep，传棒 0.2 天。

使用 SPAD SRP 文件的 **ForceModel**。

```
Create Spacecraft aSpacecraft

aSpacecraft.DryMass   = 2000
aSpacecraft.SPADSRPFile = '..\data\vehicle\spad\SphericalModel.spo'
aSpacecraft.SPADSRPScaleFactor = 1

Create ForceModel aFM

aFM.SRP = On
aFM.SRP.SRPModel = SPADFile

Create Propagator aProp

aProp.FM = aFM

BeginMissionSequence

Propagate aProp(aSpacecraft) {aSpacecraft.ElapsedDays = 0.2}
```

上述脚本为航天器指定 SPAD SRP 文件（干质量 2000 kg，缩放因子 1），力模型开启 SRP 并选用 SPADFile 面积模型，传棒 0.2 天。

用于高精度月球轨道传棒的 **ForceModel**。

```
Create Spacecraft moonSat

moonSat.DateFormat       = UTCGregorian
moonSat.UTCGregorian     = '01 Jun 2004 12:00:00.000'
moonSat.CoordinateSystem = MoonMJ2000Eq
moonSat.DisplayStateType = Cartesian

moonSat.X  = -1486.792117191545200
moonSat.Y  = 0.0
moonSat.Z  = 1486.792117191543000
moonSat.VX = -0.142927729144255
moonSat.VY = -1.631407624437537
moonSat.VZ = 0.142927729144255

Create CoordinateSystem MoonMJ2000Eq

MoonMJ2000Eq.Origin = Luna
MoonMJ2000Eq.Axes   = MJ2000Eq

Create ForceModel MoonLP165P

MoonLP165P.CentralBody                = Luna
MoonLP165P.PrimaryBodies              = {Luna}
MoonLP165P.SRP                        = On
MoonLP165P.SRP.Flux                   = 1367
MoonLP165P.SRP.Nominal_Sun            = 149597870.691
MoonLP165P.Gravity.Luna.PotentialFile = ../data/gravity/luna/LP165P.cof
MoonLP165P.Gravity.Luna.Degree        = 20
MoonLP165P.Gravity.Luna.Order         = 20

Create Propagator RKV89

RKV89.FM = MoonLP165P

BeginMissionSequence

Propagate RKV89(moonSat) {moonSat.ElapsedSecs = 300}
```

上述脚本创建月球轨道航天器（以月球为中心的 MJ2000Eq 坐标系中给出笛卡尔初值），力模型以月球为中心天体和主天体，使用 LP165P 重力位文件 20×20 阶次并开启 SRP，用 RKV89 传播器传棒 300 秒。

使用 **ExternalForceModel**（外部力模型）的 **ForceModel**。

```
Create Spacecraft aSat

Create ForceModel ExternalForceModel
ExternalForceModel.External = SimpleExternalForceModel;
ExternalForceModel.External.ExcludeOtherForces = true;

Create Propagator aProp
aProp.FM = ExternalForceModel

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = .2}
```

上述脚本创建名为 ExternalForceModel 的力模型，指定外部 Python 脚本 `SimpleExternalForceModel` 提供动力学，并排除 GMAT 内置的其他力，然后传棒 0.2 天。
