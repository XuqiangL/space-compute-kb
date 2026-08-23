# 太阳系（SolarSystem）

> 译自 GMAT R2026a 帮助文档 SolarSystem.html

**SolarSystem** —— 太阳系模型的高层配置选项。

## 描述

**SolarSystem**（太阳系）资源允许你定义太阳系模型的全局属性，包括内置天体的星历来源，以及在对中等精度建模可接受的应用场景下用于提升性能的若干设置。该资源不能在任务序列（Mission Sequence）中被修改。

> **注意**：自 R2015a 版本起，GMAT 对系统核心部分使用两套独立的太阳系配置。对于传棒（propagation），GMAT 使用由 **SolarSystem**.**EphemerisSource** 指定的星历来源以及每个 **CelestialBody** 资源上配置的属性。对于使用新的 **ContactLocator** 和 **EclipseLocator** 资源进行事件定位时，GMAT 始终使用 SPICE 数据作为 **SolarSystem** 和 **CelestialBody** 的属性来源。详见 ContactLocator、EclipseLocator 和 CelestialBody 文档。

**另请参阅**：CelestialBody、LibrationPoint、Barycenter、CoordinateSystem

## 字段

| 字段 | 描述 |
|------|------|
| **DEFilename** | DE 文件的路径和文件名。<br><br>**数据类型**：String<br>**允许取值**：有效的 DE 文件<br>**访问方式**：set<br>**默认值**：`../data/planetary_ephem/de/leDE1941.405`<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **EphemerisSource** | 内置天体的星历模型。<br><br>**数据类型**：String<br>**允许取值**：**DE405**、**DE421**、**DE424** 或 **SPICE**<br>**访问方式**：set<br>**默认值**：**DE405**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **EphemerisUpdateInterval** | 天体星历的时间更新间隔。例如，若 **EphemerisUpdateInterval** = 60，在时刻 t = 1200 进行了一次星历调用，随后在时刻 t = 1210 又进行了一次调用，则第二次调用将返回与第一次相同的星历。该选项适用于高速、低精度建模，或用于对远离第三体摄动源的轨道进行建模。<br><br>**数据类型**：Real<br>**允许取值**：Real >= 0<br>**访问方式**：set<br>**默认值**：0<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **LSKFilename** | SPK 闰秒内核（leap second kernel）的路径和文件名。<br><br>**数据类型**：String<br>**允许取值**：有效的 SPK 闰秒内核<br>**访问方式**：set<br>**默认值**：`../data/time/naif0011.tls`<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **PCKFilename** | PCK 行星常数内核（planetary constants kernel）的路径和文件名。<br><br>**数据类型**：String<br>**允许取值**：有效的 PCK 行星常数内核路径（`.tpc`）<br>**访问方式**：set<br>**默认值**：`../data/planetary_coeff/pck00010.tpc`<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **SPKFilename** | SPK 轨道星历内核（orbit ephemeris kernel）的路径和文件名。<br><br>**数据类型**：String<br>**允许取值**：有效的 SPK 星历内核（.bsp）<br>**访问方式**：set<br>**默认值**：`../data/planetary_ephem/spk/DE405AllPlanets.bsp`<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **UseTTForEphemeris** | 是否使用地球时（Terrestrial Time, TT）作为轨道星历计算例程输入的标志。设为 false 时使用 TDB（质心动力学时）。<br><br>**数据类型**：String<br>**允许取值**：**true, false**<br>**访问方式**：set<br>**默认值**：**false**<br>**单位**：N/A<br>**接口**：GUI、脚本 |

## GUI

> [图：SolarSystem 对话框（DE 星历配置）]

**SolarSystem** 对话框允许你配置太阳系建模的全局属性。上图展示了默认配置。使用 **Ephemeris Source**（星历来源）可选择内置天体的星历模型。如果你选择 **DE405**、**DE421** 或 **DE424**，对话框如上图所示显示可用选项。

> **警告**：GMAT 允许你提供用户自行创建的 DE 或 SPK 内核文件，但我们建议使用随 GMAT 分发的文件。随 GMAT 提供的文件已经过广泛测试，确保与 JPL 提供的原始数据以及 GMAT 中的其他模型保持一致性和准确性。使用不一致的星历文件或用户生成的文件，如果文件生成不正确，可能导致不稳定或数值问题。
>
> 为应用程序更改星历来源等同于对太阳系模型做出根本性更改。我们建议在分析过程的早期选定 **EphemerisSource**，并始终一致地使用该模型。如果确实需要更改星历模型，我们建议你在脚本文件中更改，而不是通过 GUI 更改。我们允许通过 GUI 更改 **EphemerisSource**，是为了在早期设计阶段（此时对建模一致性的严格要求不那么重要）提供便利。
>
> 此外，当使用 DE 作为 **EphemerisSource** 时，建模是相对于行星系统质心（barycenter）进行的，但地球（Earth）和月球（Moon）除外——它们是相对于各自天体中心建模的。当使用 SPICE 作为 **EphemerisSource** 时，建模是相对于天体上定义的 NaifId 进行的。

> [图：SolarSystem 对话框（SPICE 星历配置）]

如果你为 **Ephemeris Source** 选择了 **SPICE**，**SolarSystem** 对话框会重新配置，禁用 **Ephemeris Filename**（星历文件名）选项，表示该选项在此任务中不再使用。

## 备注

GMAT 对所有内置天体使用 **EphemerisSource** 字段中选定的星历文件。对于用户自定义天体，星历模型在 **CelestialBody** 对象上指定。

- 有关 JPL 提供的 DE 文件的更多信息，请参阅 [JPL IAU 委员会 README](http://iau-comm4.jpl.nasa.gov/README)。
- 有关 SPICE 星历文件的一般信息，请参阅 [JPL NAIF 站点](http://naif.jpl.nasa.gov/naif/toolkit.html)。
- 有关随 GMAT 分发的名为 `DE???AllPlanets.bsp` 的 SPK 内核的信息，请参阅 GMAT 发行版中 `\data\planetary_ephem\spk` 目录下的 `Readme-DE???AllPlanets.txt` 文件。

注意：**SolarSystem** 和内置 **CelestialBody** 资源的完整配置需要数百个字段。GMAT 仅将 **SolarSystem** 和 **CelestialBody** 的非默认值保存到脚本中，以避免脚本被数百个默认设置填满。

### GMAT 对 ICRF 太阳系星历文件的支持

DE400 及之后的 JPL 行星星历文件以国际天球参考架（International Celestial Reference Frame, ICRF）为基准，而 ICRF 与 J2000 参考架并不精确等价。对于大多数轨道——尤其是近地区域的轨道——ICRF 与 J2000 之间的差别无关紧要。然而，用户应当注意：GMAT 目前将 ICRF 太阳系星历状态量当作 J2000 处理，因此用户可能会发现 GMAT 与其他执行太阳系星历 ICRF 到 J2000 转换的系统之间存在不一致。

### 建模额外的太阳系天体

随 GMAT 交付的行星星历文件包含大多数太阳系行星，但不包含行星的天然卫星。在 GMAT 中可以建模木星、土星及其他行星的卫星，但用户必须从外部来源获取这些天体的星历数据。最便捷的方法是从 JPL NAIF 网站获取合适的 SPICE 星历文件（查找 "Generic Kernels"），然后将该 SPICE 文件用作新建 **CelestialBody** 实例的 **OrbitSpiceKernelName**。CelestialBody 文档的示例部分展示了以土星的卫星 Titan（土卫六）为例的完整过程。

## 示例

使用 **DE421** 作为星历。

```
GMAT SolarSystem.EphemerisSource = 'DE421'

Create Spacecraft aSpacecraft
Create Propagator aPropagator
aPropagator.FM = aForceModel
Create ForceModel aForceModel
aForceModel.PointMasses = {Luna, Sun}

BeginMissionSequence

Propagate aPropagator(aSpacecraft) {aSpacecraft.ElapsedSecs = 12000.0}
```

上述脚本将太阳系星历来源设为 DE421，创建一艘航天器和一个传播器，力模型中包含月球（Luna）和太阳（Sun）的点质量引力，然后传棒 12000 秒。

使用 **SPICE** 作为星历。

```
GMAT SolarSystem.EphemerisSource = 'SPICE'

Create Spacecraft aSpacecraft
Create Propagator aPropagator
aPropagator.FM = aForceModel
Create ForceModel aForceModel
aForceModel.PointMasses = {Luna, Sun}

BeginMissionSequence

Propagate aPropagator(aSpacecraft) {aSpacecraft.ElapsedSecs = 12000.0}
```

上述脚本与前一示例相同，但将星历来源设为 SPICE。
