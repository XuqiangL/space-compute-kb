# 航天器轨道状态（Spacecraft Orbit State）
> 译自 GMAT R2026a 帮助文档 SpacecraftOrbitState.html

**Spacecraft Orbit State —— 轨道初始条件**

## 描述

GMAT 支持一整套用于定义轨道状态的状态类型，包括直角坐标（Cartesian）和开普勒根数（Keplerian）等。此外，还可以在不同的坐标系中定义轨道状态，例如 EarthMJ2000Eq 和 EarthFixed。GMAT 提供三种可用于任何坐标系的通用状态类型：`Cartesian`（直角坐标）、`SphericalAZFPA` 和 `SphericalRADEC`（球坐标）。另有三种可用于以天体为中心的坐标系的状态类型：`Keplerian`（开普勒根数）、`ModifiedKeplerian`（修正开普勒根数）和 `Equinoctial`（春分点根数）。

在下文的"备注（Remarks）"一节中，将详细描述每种状态类型，包括状态类型定义、奇点（singularity），以及状态字段如何与 `CoordinateSystem`（坐标系）和 `Epoch`（历元）字段交互。在初始化期间设置轨道状态时存在一些限制，将在"备注"一节中讨论。文中还给出了在常用坐标系中设置各种状态类型的示例。

**另请参阅**：航天器（Spacecraft）、推进器（Propagator）、航天器历元（Spacecraft Epoch）

## 字段

### AltEquinoctialP

轨道定向的度量。`AltEquinoctialP` 与 `AltEquinoctialQ` 共同决定轨道的定向。`AltEquinoctialP` = sin(`INC`/2)*sin(`RAAN`)。

- 数据类型：实数（Real）
- 允许值：-1 ≤ `AltEquinoctialP` ≤ 1
- 访问权限：set, get
- 默认值：0.08982062789020774
- 单位：（无）
- 接口：GUI、脚本

### AltEquinoctialQ

轨道定向的度量。`AltEquinoctialP` 与 `AltEquinoctialQ` 共同决定轨道的定向。`AltEquinoctialQ` = sin(`INC`/2)*cos(`RAAN`)。

- 数据类型：实数（Real）
- 允许值：-1 ≤ `AltEquinoctialQ` ≤ 1
- 访问权限：set, get
- 默认值：0.06674269576352432
- 单位：（无）
- 接口：GUI、脚本

### AOP

轨道近拱点幅角（argument of periapsis），在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：-∞ < `AOP` < ∞
- 访问权限：set, get
- 默认值：314.1905515359921
- 单位：deg.
- 接口：GUI、脚本

### AZI

轨道速度方位角（azimuth），在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：-∞ < `AZI` < ∞
- 访问权限：set, get
- 默认值：82.37742168155043
- 单位：deg.
- 接口：GUI、脚本

### BrouwerLongAOP / BrouwerShortAOP

Brouwer-Lyddane 长周期平均（短周期平均）平近拱点幅角。

- 数据类型：实数（Real）
- 允许值：-∞ < `BrouwerLongAOP`/`BrouwerShortAOP` < ∞
- 访问权限：set, get
- 默认值：由默认直角坐标（Cartesian）状态换算得到
- 单位：deg
- 接口：GUI、脚本

### BrouwerLongECC / BrouwerShortECC

Brouwer-Lyddane 长周期平均（短周期平均）平偏心率。

- 数据类型：实数（Real）
- 允许值：0 ≤ `BrouwerLongECC`/`BrouwerShortECC` ≤ 0.99
- 访问权限：set, get
- 默认值：由默认直角坐标状态换算得到
- 单位：N/A
- 接口：GUI、脚本

### BrouwerLongINC / BrouwerShortINC

Brouwer-Lyddane 长周期平均（短周期平均）平倾角。

- 数据类型：实数（Real）
- 允许值：0 ≤ `BrouwerLongINC`/`BrouwerShortINC` ≤ 180
- 访问权限：set, get
- 默认值：由默认直角坐标状态换算得到
- 单位：deg
- 接口：GUI、脚本

### BrouwerLongMA / BrouwerShortMA

Brouwer-Lyddane 长周期平均（短周期平均）平 MA（平近点角，mean anomaly）。

- 数据类型：实数（Real）
- 允许值：-∞ < `BrouwerLongMA`/`BrouwerShortMA` < ∞
- 访问权限：set, get
- 默认值：由默认直角坐标状态换算得到
- 单位：deg
- 接口：GUI、脚本

### BrouwerLongRAAN / BrouwerShortRAAN

Brouwer-Lyddane 长周期平均（短周期平均）平 RAAN（升交点赤经，right ascension of the ascending node）。

- 数据类型：实数（Real）
- 允许值：-∞ < `BrouwerLongRAAN`/`BrouwerShortRAAN` < ∞
- 访问权限：set, get
- 默认值：由默认直角坐标状态换算得到
- 单位：deg
- 接口：GUI、脚本

### BrouwerLongSMA / BrouwerShortSMA

长周期平均（短周期平均）平半长轴。

- 数据类型：实数（Real）
- 允许值：`Brouwer*SMA` > 3000/(1-`Brouwer*ECC`)
- 访问权限：set, get
- 默认值：由默认直角坐标状态换算得到
- 单位：km
- 接口：GUI、脚本

### CoordinateSystem

定义轨道状态所参考的坐标系。`CoordinateSystem` 字段依赖于 `DisplayStateType` 字段。如果用户选择的坐标系在原点处没有引力体，则不允许使用 `Keplerian`、`ModifiedKeplerian` 和 `Equinoctial` 状态类型。

- 数据类型：字符串（String）
- 允许值：`CoordinateSystem` 资源
- 访问权限：set
- 默认值：`EarthMJ2000Eq`
- 单位：N/A
- 接口：GUI、脚本

### DEC

轨道位置赤纬（declination），在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：-90 ≤ `DEC` ≤ 90
- 访问权限：set, get
- 默认值：10.37584492005105
- 单位：deg
- 接口：GUI、脚本

### DECV

轨道速度赤纬，在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：-90 ≤ `DECV` ≤ 90
- 访问权限：set, get
- 默认值：7.747772036108118
- 单位：deg
- 接口：GUI、脚本

### Delaunayg

Delaunay "g" 元素，与 `AOP`（近拱点幅角）相同，在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：-∞ < `Delaunayg` < ∞
- 访问权限：set, get
- 默认值：314.1905515359921
- 单位：deg
- 接口：GUI、脚本

### DelaunayG

Delaunay "G" 元素，轨道角动量的大小，在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：0 ≤ `DelaunayG` < ∞
- 访问权限：set, get
- 默认值：53525.52895581695
- 单位：km²/s
- 接口：GUI、脚本

### Delaunayh

Delaunay "h" 元素，与 `RAAN`（升交点赤经）相同，在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：-∞ < `Delaunayh` < ∞
- 访问权限：set, get
- 默认值：306.6148021947984
- 单位：deg
- 接口：GUI、脚本

### DelaunayH

Delaunay "H" 元素，轨道角动量矢量的 z 分量，在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：-∞ < `Delaunayl` < ∞（译注：原文如此，应为 `DelaunayH`）
- 访问权限：set, get
- 默认值：52184.99999999999
- 单位：km²/s
- 接口：GUI、脚本

### Delaunayl

Delaunay "ℓ" 元素，与平近点角（mean anomaly）相同，在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：-∞ < `Delaunayl` < ∞
- 访问权限：set, get
- 默认值：97.10782663991999
- 单位：deg
- 接口：GUI、脚本

### DelaunayL

Delaunay "L" 元素，与二体轨道能量相关，在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：0 ≤ `DelaunayL` < ∞
- 访问权限：set, get
- 默认值：53541.66590560955
- 单位：km²/s
- 接口：GUI、脚本

### DisplayStateType

GUI 中显示的轨道状态类型。允许的状态类型取决于 `CoordinateSystem` 的选择。例如，如果坐标系原点处没有天体，则 `Keplerian`、`ModifiedKeplerian` 和 `Equinoctial` 不是 `DisplayStateType` 的允许选项。

- 数据类型：字符串（String）
- 允许值：`Cartesian`、`Keplerian`、`ModifiedKeplerian`、`SphericalAZFPA`、`SphericalRADEC` 或 `Equinoctial`
- 访问权限：set
- 默认值：`Cartesian`
- 单位：N/A
- 接口：GUI、脚本

### ECC

轨道偏心率（eccentricity），在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：`ECC` < 0.9999999 或 `ECC` > 1.0000001。若 `ECC` > 1，则 `SMA` 必须 < 0
- 访问权限：set, get
- 默认值：0.02454974900598137
- 单位：N/A
- 接口：GUI、脚本

### EphemerisName

航天器使用的星历文件路径。该参数可指定 STK、CCSDS-OEM 或 Code500 格式的文件。此文件可与星历推进器（ephemeris propagator）配合使用，以提供航天器轨迹。SPICE BSP/SPK 文件在 `OrbitSpiceKernelName` 参数上设置。关于使用星历文件推进器的详细信息，请参见推进器（Propagator）资源。

- 数据类型：字符串（String）
- 允许值：指向 STK、CCSDS-OEM 或 Code500 星历文件的有效文件路径
- 访问权限：set
- 默认值：未设置（Unset）
- 单位：N/A
- 接口：GUI、脚本

### EquinoctialH

轨道偏心率和近拱点幅角的度量。`EquinoctialH` 与 `EquinoctialK` 共同决定轨道的椭圆程度以及近拱点的位置。`EquinoctialH` = `ECC` * sin(`AOP` + `RAAN`)。

- 数据类型：实数（Real）
- 允许值：-0.99999 < `EquinoctialH` < 0.99999，且 sqrt(`EquinoctialH`² + `EquinoctialK`²) < 0.99999
- 访问权限：set, get
- 默认值：-0.02423431419337062
- 单位：无量纲（dimless）
- 接口：GUI、脚本

### EquinoctialK

轨道偏心率和近拱点幅角的度量。`EquinoctialH` 与 `EquinoctialK` 共同决定轨道的椭圆程度以及近拱点的位置。`EquinoctialK` = `ECC` * cos(`AOP` + `RAAN`)。

- 数据类型：实数（Real）
- 允许值：-0.99999 < `EquinoctialK` < 0.99999，且 sqrt(`EquinoctialH`² + `EquinoctialK`²) < 0.99999
- 访问权限：set, get
- 默认值：-0.003922778585859663
- 单位：无量纲（dimless）
- 接口：GUI、脚本

### EquinoctialP

轨道定向的度量。`EquinoctialP` 与 `EquinoctialQ` 共同决定轨道的定向。`EquinoctialP` = tan(`INC`/2)*sin(`RAAN`)。

- 数据类型：实数（Real）
- 允许值：-∞ < `EquinoctialP` < ∞
- 访问权限：set, get
- 默认值：-0.09038834725719359
- 单位：无量纲（dimless）
- 接口：GUI、脚本

### EquinoctialQ

轨道定向的度量。`EquinoctialP` 与 `EquinoctialQ` 共同决定轨道的定向。`EquinoctialQ` = tan(`INC`/2)*cos(`RAAN`)。

- 数据类型：实数（Real）
- 允许值：-∞ < `EquinoctialQ` < ∞
- 访问权限：set, get
- 默认值：0.06716454898232072
- 单位：无（None）
- 接口：GUI、脚本

### FPA

轨道飞行路径角（flight path angle），在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：0 ≤ `FPA` ≤ 180
- 访问权限：set, get
- 默认值：88.60870365370448
- 单位：Deg.
- 接口：GUI、脚本

### INC

轨道倾角（inclination），在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：0 ≤ `INC` ≤ 180
- 访问权限：set, get
- 默认值：12.85008005658097
- 单位：deg
- 接口：GUI、脚本

### IncomingBVAZI / OutgoingBVAZI

`IncomingBVAZI`/`OutgoingBVAZI` 是进入/离开渐近线在无穷远处的 B 矢量方位角，自南向北逆时针量取。若 `C3Energy` < 0，则以拱线矢量（apsides vector）代替离开/进入渐近线。

- 数据类型：实数（Real）
- 允许值：-∞ < `IncomingBVAZI`/`OutgoingBVAZI` < ∞
- 访问权限：set, get
- 默认值：由默认直角坐标状态换算得到
- 单位：deg
- 接口：GUI、脚本

### IncomingC3Energy / OutgoingC3Energy

C3 能量。`C3Energy` = -mu/`SMA`。`IncomingC3Energy`/`OutgoingC3Energy` 的区别仅在于它们分别与 `IncomingAsymptote`（进入渐近线）和 `OutgoingAsymptote`（离开渐近线）状态表示相关联。

- 数据类型：实数（Real）
- 允许值：`IncomingC3Energy` ≤ -1e-7 或 `IncomingC3Energy` ≥ 1e-7；`OutgoingC3Energy` ≤ -1e-7 或 `OutgoingC3Energy` ≥ 1e-7
- 访问权限：set, get
- 默认值：由默认直角坐标状态换算得到
- 单位：km²/s²
- 接口：GUI、脚本

### IncomingDHA / OutgoingDHA

`IncomingDHA`/`OutgoingDHA` 是进入/离开渐近线的赤纬。若 `C3Energy` < 0，则以拱线矢量代替进入/离开渐近线。

- 数据类型：实数（Real）
- 允许值：-90° ≤ `IncomingDHA`/`OutgoingDHA` < 90°
- 访问权限：set, get
- 默认值：由默认直角坐标状态换算得到
- 单位：deg
- 接口：GUI、脚本

### IncomingRadPer / OutgoingRadPer

轨道近拱点半径。近拱点半径是航天器与位于坐标系原点处天体之间的最小（密切）距离。`IncomingRadPer`/`OutgoingRadPer` 与 `RadPer` 的区别仅在于它们分别与 `IncomingAsymptote` 和 `OutgoingAsymptote` 状态表示相关联。

- 数据类型：实数（Real）
- 允许值：abs(`IncomingRadPer`) ≥ 1 meter；abs(`OutgoingRadPer`) ≥ 1 meter
- 访问权限：set, get
- 默认值：由默认直角坐标状态换算得到
- 单位：km
- 接口：GUI、脚本

### IncomingRHA / OutgoingRHA

`IncomingRHA`/`OutgoingRHA` 是进入/离开渐近线的赤经。若 `C3Energy` < 0，则以拱线矢量代替进入/离开渐近线。

- 数据类型：实数（Real）
- 允许值：-∞ < `IncomingRHA`/`OutgoingRHA` < ∞
- 访问权限：set, get
- 默认值：由默认直角坐标状态换算得到
- 单位：deg
- 接口：GUI、脚本

### MLONG

航天器在其轨道上位置的度量。`MLONG` = `AOP` + `RAAN` + `MA`。

- 数据类型：实数（Real）
- 允许值：-360 ≤ `MLONG` ≤ 360
- 访问权限：set, get
- 默认值：357.9131803707105
- 单位：deg.
- 接口：GUI、脚本

### ModEquinoctialF

偏心率矢量的分量（与 `ModEquinoctialG` 一起）。偏心率矢量的大小等于偏心率，方向由中心天体指向近地点。`ModEquinoctialF` = `ECC` * cos(`AOP`+`RAAN`)。

- 数据类型：实数（Real）
- 允许值：-∞ < `ModEquinoctialF` < ∞
- 访问权限：set, get
- 默认值：-0.003922778585859663
- 单位：（无）
- 接口：GUI、脚本

### ModEquinoctialG

偏心率矢量的分量（与 `ModEquinoctialF` 一起）。`ModEquinoctialG` = `ECC` * sin(`AOP`+`RAAN`)。

- 数据类型：实数（Real）
- 允许值：-∞ < `ModEquinoctialG` < ∞
- 访问权限：set, get
- 默认值：-0.02423431419337062
- 单位：（无）
- 接口：GUI、脚本

### ModEquinoctialH

与 `EquinoctialQ` 相同。

- 数据类型：实数（Real）
- 允许值：-∞ < `ModEquinoctialH` < ∞
- 访问权限：set, get
- 默认值：0.06716454898232072
- 单位：（无）
- 接口：GUI、脚本

### ModEquinoctialK

与 `EquinoctialP` 相同。

- 数据类型：实数（Real）
- 允许值：-∞ < `ModEquinoctialK` < ∞
- 访问权限：set, get
- 默认值：-0.09038834725719359
- 单位：（无）
- 接口：GUI、脚本

### NAIFId

SPICE 内核中使用的航天器 Id。

- 数据类型：字符串（String）
- 允许值：字符串（String）
- 访问权限：set
- 默认值：-123456789
- 单位：N/A
- 接口：GUI、脚本

### OrbitSpiceKernelName

航天器轨道的 SPK 内核。SPK 轨道内核的扩展名为 ".BSP"。此字段不能在任务序列（Mission Sequence）中设置。

- 数据类型：字符串数组（String array）
- 允许值：路径与文件名的列表
- 访问权限：set
- 默认值：无默认值，该字段为空
- 单位：N/A
- 接口：GUI、脚本

### PlanetodeticAZI

轨道速度方位角，在 `CoordinateSystem` 字段所选坐标系中表示。与 `AZI` 字段不同，`PlanetodeticAZI` 与 `Planetodetic`（行星测地）状态表示相关联，仅对具有 `BodyFixed`（体固）轴的坐标系有效。

- 数据类型：实数（Real）
- 允许值：-∞ < `PlanetodeticAZI` < ∞
- 访问权限：set, get
- 默认值：81.80908019114962
- 单位：deg
- 接口：GUI、脚本

### PlanetodeticHFPA

轨道水平飞行路径角，在 `CoordinateSystem` 字段所选坐标系中表示。`PlanetodeticHFPA` 仅对具有 `BodyFixed` 轴的坐标系有效。

- 数据类型：实数（Real）
- 允许值：-90 ≤ `PlanetodeticHFPA` ≤ 90
- 访问权限：set, get
- 默认值：1.494615814842774
- 单位：deg
- 接口：GUI、脚本

### PlanetodeticLAT

行星测地纬度，在 `CoordinateSystem` 字段所选坐标系中表示。此字段仅对具有 `BodyFixed` 轴的坐标系有效。

- 数据类型：实数（Real）
- 允许值：-90 ≤ `PlanetodeticLAT` ≤ 90
- 访问权限：set, get
- 默认值：10.43478253114861
- 单位：deg
- 接口：GUI、脚本

### PlanetodeticLON

行星测地经度，在 `CoordinateSystem` 字段所选坐标系中表示。此字段仅对具有 `BodyFixed` 轴的坐标系有效。

- 数据类型：实数（Real）
- 允许值：-∞ < `PlanetodeticLON` < ∞
- 访问权限：set, get
- 默认值：79.67188405807977
- 单位：deg
- 接口：GUI、脚本

### PlanetodeticRMAG

轨道位置矢量的大小，在 `CoordinateSystem` 字段所选坐标系中表示。与 `RMAG` 字段不同，`PlanetodeticRMAG` 与 `Planetodetic` 状态表示相关联，仅对具有 `BodyFixed` 轴的坐标系有效。

- 数据类型：实数（Real）
- 允许值：`PlanetodeticRMAG` ≥ 1e-10
- 访问权限：set, get
- 默认值：7218.032973047435
- 单位：km
- 接口：GUI、脚本

### PlanetodeticVMAG

轨道速度矢量的大小，在 `CoordinateSystem` 字段所选坐标系中表示。与 `VMAG` 字段不同，`PlanetodeticVMAG` 与 `Planetodetic` 状态表示相关联，仅对具有 `BodyFixed` 轴的坐标系有效。

- 数据类型：实数（Real）
- 允许值：`PlanetodeticVMAG` ≥ 1e-10
- 访问权限：set, get
- 默认值：6.905049647173787
- 单位：km/s
- 接口：GUI、脚本

### RA

轨道位置赤经（right ascension），在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：-∞ < `RA` < ∞
- 访问权限：set, get
- 默认值：0
- 单位：deg
- 接口：GUI、脚本

### RAAN

轨道升交点赤经（right ascension of the ascending node），在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：-∞ < `RAAN` < ∞
- 访问权限：set, get
- 默认值：306.6148021947984
- 单位：deg
- 接口：GUI、脚本

### RadApo

轨道远拱点半径（radius of apoapsis），在 `CoordinateSystem` 字段所选坐标系中表示。远拱点半径是航天器与位于 `CoordinateSystem` 原点处天体之间的最大（密切）距离。

- 数据类型：实数（Real）
- 允许值：abs(`RadApo`) ≥ 1 meter
- 访问权限：set, get
- 默认值：7368.49911046818
- 单位：km
- 接口：GUI、脚本

### RadPer

轨道近拱点半径（radius of periapsis），在 `CoordinateSystem` 字段所选坐标系中表示。近拱点半径是航天器与位于 `CoordinateSystem` 原点处天体之间的最小（密切）距离。

- 数据类型：实数（Real）
- 允许值：abs(`RadPer`) ≥ 1 meter
- 访问权限：set, get
- 默认值：7015.378524789846
- 单位：km
- 接口：GUI、脚本

### RAV

轨道速度赤经，在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：-∞ < `RAV` < ∞
- 访问权限：set, get
- 默认值：90
- 单位：deg
- 接口：GUI、脚本

### RMAG

轨道位置矢量的大小，在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：`RMAG` ≥ 1e-10
- 访问权限：set, get
- 默认值：7218.032973047435
- 单位：km
- 接口：GUI、脚本

### SemilatusRectum

真近点角为 90 deg 时位置矢量的大小（半通径）。

- 数据类型：实数（Real）
- 允许值：`SemilatusRectum` > 1e-7
- 访问权限：set, get
- 默认值：7187.60430675539
- 单位：km
- 接口：GUI、脚本

### SMA

轨道半长轴（semi-major axis），在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：`SMA` < -0.001 km 或 `SMA` > 0.001 km。若 `SMA` < 0，则 `ECC` 必须 > 1
- 访问权限：set, get
- 默认值：7191.938817629013
- 单位：km
- 接口：GUI、脚本

### TA

轨道真近点角（true anomaly），在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：-∞ < `TA` < ∞
- 访问权限：set, get
- 默认值：99.8877493320488
- 单位：deg.
- 接口：GUI、脚本

### TLONG

密切轨道的真经度。`TLONG` = `RAAN` + `AOP` + `TA`。

- 数据类型：实数（Real）
- 允许值：-∞ < `TLONG` < ∞
- 访问权限：set, get
- 默认值：0.6931030628392251
- 单位：deg
- 接口：GUI、脚本

### VMAG

轨道速度矢量的大小，在 `CoordinateSystem` 字段所选坐标系中表示。

- 数据类型：实数（Real）
- 允许值：`VMAG` ≥ 1e-10
- 访问权限：set, get
- 默认值：7.417715281675348
- 单位：km/s
- 接口：GUI、脚本

### VX

航天器速度相对于航天器 `CoordinateSystem` 字段所选坐标系的 x 分量。

- 数据类型：实数（Real）
- 允许值：-∞ < `VX` < ∞
- 访问权限：set, get
- 默认值：0
- 单位：km/s
- 接口：GUI、脚本

### VY

航天器速度相对于航天器 `CoordinateSystem` 字段所选坐标系的 y 分量。

- 数据类型：实数（Real）
- 允许值：-∞ < `VY` < ∞
- 访问权限：set, get
- 默认值：7.35
- 单位：km/s
- 接口：GUI、脚本

### VZ

航天器速度相对于航天器 `CoordinateSystem` 字段所选坐标系的 z 分量。

- 数据类型：实数（Real）
- 允许值：-∞ < `VZ` < ∞
- 访问权限：set, get
- 默认值：1
- 单位：km/s
- 接口：GUI、脚本

### X

航天器位置相对于航天器 `CoordinateSystem` 字段所选坐标系的 x 分量。

- 数据类型：实数（Real）
- 允许值：-∞ < `X` < ∞
- 访问权限：set, get
- 默认值：7100
- 单位：km
- 接口：GUI、脚本

### Y

航天器位置相对于航天器 `CoordinateSystem` 字段所选坐标系的 y 分量。

- 数据类型：实数（Real）
- 允许值：-∞ < `Y` < ∞
- 访问权限：set, get
- 默认值：0
- 单位：km
- 接口：GUI、脚本

### Z

航天器位置相对于航天器 `CoordinateSystem` 字段所选坐标系的 z 分量。

- 数据类型：实数（Real）
- 允许值：-∞ < `Z` < ∞
- 访问权限：set, get
- 默认值：1300
- 单位：km
- 接口：GUI、脚本

## GUI

> [图：航天器轨道状态/历元对话框（Resource_SpacecraftOrbitEpoch_GUI.png）]

航天器（Spacecraft）轨道状态对话框允许设置航天器轨道状态的历元、坐标系和状态类型。当指定一个轨道状态时，所定义的状态采用 `StateType` 菜单中选择的表示法，相对于 `CoordinateSystem` 菜单中指定的坐标系，并对应于 `Epoch` 菜单中定义的历元。如果所选的 `CoordinateSystem` 是随时间变化的，则坐标系的历元由 `Epoch` 字段定义，更改历元会改变轨道状态的惯性系表示。

更改 `Epoch Format`（历元格式）会使 `Epoch` 立即更新，以反映所选的时间系统和格式。

如果 `CoordinateSystem` 在原点处没有中心天体，或者 `CoordinateSystem` 引用了当前航天器（导致循环引用），则无法计算 `Keplerian`、`ModifiedKeplerian` 和 `Equinoctial` 状态类型。例如，如果选择了 `Keplerian` 状态类型，则无法计算开普勒根数的坐标系不会出现在 `CoordinateSystem` 菜单中。同样，如果选择的 `CoordinateSystem` 在原点处没有天体，基于开普勒根数的状态类型将不会作为选项出现在 `StateType` 菜单中。只有当 `CoordinateSystem` 具有 `BodyFixed` 轴时，才能选择 `Planetodetic` 状态类型。

## 备注（Remarks）

### Cartesian（直角坐标）状态

`Cartesian` 状态由相对于所选 `CoordinateSystem` 表示的位置和速度分量组成。

### Keplerian（开普勒根数）与 Modified Keplerian（修正开普勒根数）状态类型

`Keplerian` 和 `ModifiedKeplerian` 状态类型使用相对于所选 `CoordinateSystem` 的密切开普勒轨道根数。要使用 `Keplerian` 或 `ModifiedKeplerian` 状态类型，航天器的坐标系必须在原点处具有中心天体。两种表示法的区别在于轨道大小和形状的定义方式不同。`Keplerian` 状态类型由以下元素组成：`SMA`（半长轴）、`ECC`（偏心率）、`INC`（倾角）、`RAAN`（升交点赤经）、`AOP`（近拱点幅角）和 `TA`（真近点角）。`ModifiedKeplerian` 状态类型由以下元素组成：`RadApo`（远拱点半径）、`RadPer`（近拱点半径）、`INC`、`RAAN`、`AOP` 和 `TA`。下表和下图详细描述了每个 `Keplerian` 状态元素，包括奇点。

### 开普勒根数的几何意义

| 名称 | 描述 |
|---|---|
| `SMA` | `SMA` 包含轨道类型和大小的信息。若 `SMA` > 0，轨道为椭圆；若 `SMA` < 0，轨道为双曲线（Hyperbolic）；对于抛物线轨道，`SMA` 为无穷大。 |
| `ECC` | `ECC` 包含轨道形状的信息。若 `ECC` = 0，轨道为圆；若 0 < `ECC` < 1，轨道为椭圆；若 `ECC` = 1，轨道为抛物线；若 `ECC` > 1，轨道为双曲线。 |
| `INC` | `INC` 是轨道角动量矢量与 z 轴之间的夹角。若 `INC` < 90 deg.，轨道为顺行（prograde）；若 `INC` > 90 deg，轨道为逆行（retrograde）。 |
| `RAAN` | `RAAN` 定义为 x 轴与交点矢量之间逆时针量取的夹角。交点矢量定义为 z 轴与轨道角动量矢量的叉积。对于赤道轨道，`RAAN` 无定义。 |
| `AOP` | `AOP` 是指向近拱点的矢量与指向交线方向的矢量之间的夹角。对于圆轨道，`AOP` 无定义。 |
| `TA` | `TA` 定义为指向近拱点的矢量与指向航天器的矢量之间的夹角。对于圆轨道，`TA` 无定义。 |

> [图：开普勒根数几何示意图（Resource_SpacecraftOrbitState_Remark_2.png）]

`Keplerian` 和 `ModifiedKeplerian` 状态类型存在若干奇点。下面描述各种奇点以及状态转换算法中对每个奇点的处理方式。

> **奇点：`ECC` = 1**
>
> `SMA` 为无穷大，无法用于定义轨道大小。GMAT 要求在设置 `ECC` 或执行转换时满足 `ECC` < 0.9999999 或 `ECC` > 1.0000001。对于在接近这些限值时执行的转换，可能会损失精度。

> **奇点：`ECC` = 0**
>
> `AOP` 无定义。若 `ECC` <= 1e-11，GMAT 在从 `Cartesian` 到 `Keplerian`/`ModKeplerian` 的转换中将 `AOP` 置为零，并将轨道面内的全部角位移计入真近点角。

> **奇点：`SMA` = 0**
>
> 导致奇异的圆锥曲线。GMAT 要求输入 `SMA` 时满足 |`SMA`| > 1 meter。

> **奇点：`SMA` = INF（无穷大）**
>
> `SMA` 为无穷大，需要另一个参数来刻画轨道大小。不支持 `Keplerian` 根数。

> **奇点：`INC` = 0**
>
> `RAAN` 无定义。若 `INC` < 6e-10，GMAT 在从 `Cartesian` 到 `Keplerian`/`ModKeplerian` 的转换中将 `RAAN` 置为 0。此时，若 `ECC` < 1e-11，则 `AOP` 置为 0，GMAT 将 x 轴与航天器之间的全部角位移计入真近点角；若 `ECC` ≥ 1e-11，则 `AOP` 按偏心率矢量与 x 轴之间的夹角计算。

> **奇点：`INC` = 180**
>
> `RAAN` 无定义。若 `INC` > (180 - 6e-10)，GMAT 在从 `Cartesian` 到 `Keplerian`/`ModKeplerian` 的转换中将 `RAAN` 置为 0。此时，若 `ECC` < 1e-11，则 `AOP` 置为 0，GMAT 将 x 轴与航天器之间的全部角位移计入真近点角；若 `ECC` ≥ 1e-11，则 `AOP` 按偏心率矢量与 x 轴之间的夹角计算。

> **奇点：`RadPer` = 0**
>
> 奇异的圆锥曲线。GMAT 要求在状态转换中 `RadPer` > 1 meter。

> **奇点：`RadApo` = 0**
>
> 奇异的圆锥曲线。GMAT 要求在状态转换中 abs(`RadApo`) > 1 meter。

### Delaunay 状态类型

`Delaunay` 与 `Cartesian` 之间的转换经由经典 `Keplerian` 状态进行。因此，`Delaunay` 状态无法表示抛物线轨道。此外，由于 `DelaunayL` 的定义在 `SMA` 为负时不是实数，`Delaunay` 状态也无法表示双曲线轨道。下表描述 `Delaunay` 状态的各元素。

| 元素 | 描述 |
|---|---|
| `Delaunayl` | 平近点角（mean anomaly）。它与半径为 `SMA` 的圆上的均匀角运动相关。 |
| `Delaunayg` | 参见"开普勒根数状态"一节中的 `AOP`。 |
| `Delaunayh` | 参见"开普勒根数状态"一节中的 `RAAN`。 |
| `DelaunayL` | 与二体轨道能量相关。`DelaunayL` = sqrt(mu*`SMA`)。 |
| `DelaunayG` | 轨道角动量矢量的大小。`DelaunayG` = `DelaunayL`*sqrt(1-`ECC`²)。 |
| `DelaunayH` | 轨道角动量的 K 分量。`DelaunayH` = `DelaunayG` * cos(`INC`)。 |

### Delaunay 根数的奇点

`Delaunay` 根数的奇点与 `Keplerian` 根数相同，因为转换过程中使用了 `Keplerian` 根数，参见"开普勒根数状态"一节。下表给出 `Delaunay` 状态类型特有的附加奇点。

> **奇点：`ECC` > 1**
>
> 按照定义，对于双曲线轨道 `DelaunayL` 不是实数。

### Brouwer-Lyddane 平均状态类型

`BrouwerMeanShort` 状态表示在低阶带谐项（即 J2–J5）下的短周期平均平运动。类似地，`BrouwerMeanLong` 状态表示在低阶带谐项（即 J2–J5）下的长周期平均平运动。GMAT 在 Brouwer 平均状态算法中使用 JGM-2 带谐系数。两者对近抛物线或双曲线轨道均为奇异。要在 GMAT 中使用 `BrouwerMeanShort`/`BrouwerMeanLong` 状态类型，中心天体必须是地球。若中心天体为地球，GMAT 可以由密切状态（`Cartesian`、`Keplerian` 等）计算 `BrouwerMeanShort`/`BrouwerMeanLong` 状态，反之亦然。

| 元素 | 描述 |
|---|---|
| `BrouwerLongAOP` / `BrouwerShortAOP` | Brouwer-Lyddane 长周期平均（短周期平均）平近拱点幅角。 |
| `BrouwerLongMA` / `BrouwerShortMA` | Brouwer-Lyddane 长周期平均（短周期平均）平 MA（平近点角）。 |
| `BrouwerLongECC` / `BrouwerShortECC` | Brouwer-Lyddane 长周期平均（短周期平均）平偏心率。 |
| `BrouwerLongINC` / `BrouwerShortINC` | Brouwer-Lyddane 长周期平均（短周期平均）平倾角。 |
| `BrouwerLongRAAN` / `BrouwerShortRAAN` | Brouwer-Lyddane 长周期平均（短周期平均）平 RAAN（升交点赤经）。 |
| `BrouwerLongSMA` / `BrouwerShortSMA` | 长周期平均（短周期平均）平半长轴。 |

### Brouwer-Lyddane 平均根数的奇点

下面说明 `BrouwerMeanShort`/`BrouwerMeanLong` 状态奇点的特性，以及 GMAT 状态转换算法中实现的奇点处理方法。请注意，由于 Brouwer-Lyddane 平均根数涉及迭代求解，在奇点附近可能会损失精度。

> **奇点：`BrouwerSMA` < 3000/(1-`BrouwerECC`)**
>
> 由于 Brouwer 的公式基于地球带谐项，`BrouwerMeanShort` 和 `BrouwerMeanLong` 无法处理平均近地点距离小于地球半径 3000 km 的轨道，因为存在数值不稳定性。

> **奇点：`BrouwerLongINC` = 63，`BrouwerLongINC` = 117**
>
> 如果给定的 `BrouwerLongINC`（仅长周期平均 INC）接近临界倾角 i_c = 63 deg. 或 117 deg.，算法会因奇异项（非零虚部分量）而不稳定。因此 GMAT 无法计算密切根数。

> **奇点：`BrouwerLongECC` = 0，`BrouwerLongECC` ≥ 1**
>
> 据报告，若 `BrouwerECC` 大于 0.9 或小于 1E-7，从直角坐标到 `BrouwerMeanLong` 状态的转换在统计上不收敛。对于这些情形，GMAT 会给出包含当前转换误差的警告信息。

### Spherical（球坐标）状态类型

`SphericalAZFPA` 和 `SphericalRADEC` 状态类型由航天器状态相对于所选 `CoordinateSystem` 的极坐标组成。两种球坐标表示法的区别在于速度的定义方式不同。`SphericalRADEC` 状态类型由以下元素组成：`RMAG`、`RA`、`DEC`、`VMAG`、`RAV` 和 `DECV`。`SphericalAZFPA` 状态类型由以下元素组成：`RMAG`、`RA`、`DEC`、`VMAG`、`AZI` 和 `FPA`。下表和下图详细描述每个球坐标状态元素，包括奇点。

### 球坐标元素的几何意义

| 名称 | 描述 |
|---|---|
| `RMAG` | 位置矢量的大小。 |
| `RA` | 赤经，即位置矢量在 xy 平面内的投影与 x 轴之间逆时针量取的夹角。 |
| `DEC` | 赤纬，即位置矢量与 xy 平面之间的夹角。 |
| `VMAG` | 速度矢量的大小。 |
| `FPA` | 垂直飞行路径角。在由位置矢量和速度矢量构成的平面内，从垂直于位置矢量的平面量到速度矢量的角度。 |
| `AZI` | 飞行路径方位角。从垂直于位置矢量并指北的矢量，量到速度矢量在垂直于位置矢量的平面内的投影的角度。 |
| `RAV` | 速度赤经。速度矢量在 xy 平面内的投影与 x 轴之间逆时针量取的夹角。 |
| `DECV` | 速度赤纬。速度矢量与 xy 平面之间的夹角。 |

> [图：球坐标元素几何示意图（Resource_SpacecraftOrbitState_Remark_4.png）]

### 球坐标元素的奇点

> **奇点：`RMAG` = 0**
>
> 导致奇异的圆锥曲线：赤纬和飞行路径角无定义。若 `RMAG` < 1e-10，GMAT 将不允许转换。对于大于但接近 1e-10 的 `RMAG` 值，转换中可能会损失精度。

> **奇点：`VMAG` = 0**
>
> 导致奇异的圆锥曲线：速度赤纬和飞行路径角无定义。若 `VMAG` < 1e-10，GMAT 将不允许转换。对于大于但接近 1e-10 的 `VMAG` 值，转换中可能会损失精度。

### Planetodetic（行星测地）状态类型

`Planetodetic` 状态类型适用于指定相对于中心天体表面的状态。它与球坐标状态类型非常相似，但在其定义中使用了中心天体的扁率。要使用 `Planetodetic` 状态类型，航天器的坐标系必须在原点处具有天体，并且必须具有 `BodyFixed`（体固）轴。

| 元素 | 描述 |
|---|---|
| `PlanetodeticRMAG` | 轨道半径矢量的大小。 |
| `PlanetodeticLON` | 行星测地经度。 |
| `PlanetodeticLAT` | 行星测地纬度，使用中心天体的 `Flattening`（扁率）。 |
| `PlanetodeticVMAG` | 固定坐标系中轨道速度矢量的大小。 |
| `PlanetodeticAZI` | 固定坐标系中的轨道速度方位角。 |
| `PlanetodeticHFPA` | 水平飞行路径角。`HFPA` = 90 - `VFPA`。 |

### 行星测地元素的奇点

> **奇点：`PlanetodeticRMAG` = 0**
>
> 导致奇异的圆锥曲线：赤纬和飞行路径角无定义。若 `PlanetodeticRMAG` < 1e-10，GMAT 将不允许转换。对于大于但接近 1e-10 的 `PlanetodeticRMAG` 值，转换中可能会损失精度。

> **奇点：`PlanetodeticVMAG` = 0**
>
> 导致奇异的圆锥曲线：速度赤纬和飞行路径角无定义。若 `PlanetodeticVMAG` < 1e-10，GMAT 将不允许转换。对于大于但接近 1e-10 的 `PlanetodeticVMAG` 值，转换中可能会损失精度。

### Equinoctial（春分点根数）状态类型

GMAT 支持 `Equinoctial` 状态表示，对于倾角小于 180 度的椭圆轨道它是非奇异的。要使用 `Equinoctial` 状态类型，航天器的坐标系必须在原点处具有中心天体。

| 元素 | 描述 |
|---|---|
| `SMA` | 参见开普勒根数一节。 |
| `EquinoctialH` | 轨道偏心率和近拱点幅角的度量。`EquinoctialH` 与 `EquinoctialK` 共同决定轨道的椭圆程度以及近拱点的位置。`EquinoctialH` = `ECC` * sin(`AOP`)。 |
| `EquinoctialK` | 轨道偏心率和近拱点幅角的度量。`EquinoctialH` 与 `EquinoctialK` 共同决定轨道的椭圆程度以及近拱点的位置。`EquinoctialK` = `ECC` * cos(`AOP`)。 |
| `EquinoctialP` | 轨道定向的度量。`EquinoctialP` 与 `EquinoctialQ` 共同决定轨道的定向。`EquinoctialP` = tan(`INC`/2)*sin(`RAAN`)。 |
| `EquinoctialQ` | 轨道定向的度量。`EquinoctialP` 与 `EquinoctialQ` 共同决定轨道的定向。`EquinoctialQ` = tan(`INC`/2)*cos(`RAAN`)。 |
| `MLONG` | 航天器在其轨道上平位置的度量。`MLONG` = `AOP` + `RAAN` + `MA`。 |

### 春分点根数的奇点

> **奇点：`INC` = 180**
>
> `RAAN` 无定义。若 `INC` > 180 - 1.0e-11，GMAT 将 `RAAN` 置为 0 度。GMAT 不支持真正逆行轨道的 `Equinoctial` 根数。

> **奇点：`ECC` > 0.9999999**
>
> `Equinoctial` 根数对抛物线或双曲线轨道无定义。

### Alternate Equinoctial（另类春分点根数）状态类型

`AlternateEquinoctial` 状态类型是 `Equinoctial` 根数的一个微小变体，在 "P" 和 "Q" 元素中使用 sin(`INC`/2) 代替 tan(`INC`/2)。两种表示法具有相同的奇点。

| 元素 | 描述 |
|---|---|
| `SMA` | 参见开普勒根数一节。 |
| `EquinoctialH` | 参见春分点根数一节。 |
| `EquinoctialK` | 参见春分点根数一节。 |
| `AltEquinoctialP` | 轨道定向的度量。`AltEquinoctialP` 与 `AltEquinoctialQ` 共同决定轨道的定向。`AltEquinoctialP` = sin(`INC`/2)*sin(`RAAN`)。 |
| `AltEquinoctialQ` | 轨道定向的度量。`AltEquinoctialP` 与 `AltEquinoctialQ` 共同决定轨道的定向。`AltEquinoctialP` = sin(`INC`/2)*cos(`RAAN`)。（译注：原文如此，应为 `AltEquinoctialQ` = sin(`INC`/2)*cos(`RAAN`)） |
| `MLONG` | 参见春分点根数一节。 |

### Modified Equinoctial（修正春分点根数）状态类型

`ModifiedEquinoctial` 状态表示对圆轨道、椭圆轨道、抛物线轨道和双曲线轨道均非奇异。唯一的奇点出现在逆行赤道轨道，因为与 `Equinoctial` 一样，GMAT 不支持逆行因子（retrograde factor）。

| 元素 | 描述 |
|---|---|
| `SemilatusRectum` | 真近点角为 90 deg 时位置矢量的大小。`SemilatusRectum` = `SMA`*(1-`ECC`²)。 |
| `ModEquinoctialF` | 偏心率矢量的分量（与 `ModEquinoctialG` 一起）。偏心率矢量在 x 上的投影。`ModEquinoctialF` = `ECC` * cos(`AOP`+`RAAN`)。 |
| `ModEquinoctialG` | 偏心率矢量的分量（与 `ModEquinoctialF` 一起）。偏心率矢量在 y 上的投影。`ModEquinoctialG` = `ECC` * sin(`AOP`+`RAAN`)。 |
| `ModEquinoctialH` | 与 `EquinoctialQ` 相同。 |
| `ModEquinoctialK` | 与 `EquinoctialP` 相同。 |
| `TLONG` | 航天器在其轨道上真实位置的度量。`TLONG` = `AOP` + `RAAN` + `TA`。 |

### 修正春分点根数的奇点

> **奇点：`INC` = 180**
>
> 与 `Equinoctial` 根数类似，在 `INC` = 180 deg 处存在奇点。GMAT 不支持逆行赤道轨道的 `ModifiedEquinoctial` 根数。

### Hyperbolic Asymptote（双曲线渐近线）状态类型

GMAT 支持两种相关的双曲线渐近线状态类型：`IncomingAsymptote` 用于定义进入双曲线渐近线，`OutgoingAsymptote` 用于定义离开双曲线渐近线。两种表示法都适用于定义飞越（flyby）。

| 元素 | 描述 |
|---|---|
| `IncomingRadPer` / `OutgoingRadPer` | 轨道近拱点半径。近拱点半径是航天器与坐标系原点处天体之间的最小（密切）距离。`IncomingRadPer`/`OutgoingRadPer` 与 `RadPer` 的区别仅在于它们分别与 `IncomingAsymptote` 和 `OutgoingAsymptote` 状态表示相关联。 |
| `IncomingC3Energy` / `OutgoingC3Energy` | C3 能量。`C3Energy` = -mu/`SMA`。`IncomingC3Energy`/`OutgoingC3Energy` 的区别仅在于它们分别与 `IncomingAsymptote` 和 `OutgoingAsymptote` 状态表示相关联。 |
| `IncomingRHA` / `OutgoingRHA` | 进入/离开渐近线的赤经。若 `C3Energy` < 0，则以拱线矢量代替进入/离开渐近线。 |
| `IncomingDHA` / `OutgoingDHA` | 进入/离开渐近线的赤纬。若 `C3Energy` < 0，则以拱线矢量代替进入/离开渐近线。 |
| `IncomingBVAZI` / `OutgoingBVAZI` | 进入/离开渐近线在无穷远处的 B 矢量方位角，自南向北逆时针量取。若 `C3Energy` < 0，则以拱线矢量代替离开/进入渐近线。 |
| `TA` | 参见 `Keplerian`。 |

### 双曲线渐近线元素的奇点

> **奇点：`IncomingC3Energy`/`OutgoingC3Energy` = 0**
>
> 若 `IncomingC3Energy`/`OutgoingC3Energy` = 0，则航天器处于抛物线轨道。双曲线渐近线状态不支持抛物线轨道。必须通过选择一组合适的元素来避免 -1E-7 ≤ `IncomingC3Energy`/`OutgoingC3Energy` ≤ 1E-7。

> **奇点：`ECC` = 0**
>
> 对于圆轨道的情形，`TA` 无定义。必须通过选择一组合适的元素来避免 `ECC` ≤ 1E-7。GMAT 不支持真正圆轨道的双曲线渐近线表示。

> **奇点：渐近线矢量平行于 z 轴**
>
> 如果渐近线矢量与坐标系的 z 方向平行或反平行，则 B 平面无定义。必须通过选择合适的坐标系或元素组来避免这种情形。

### 状态分量与航天器 CoordinateSystem 字段的相互作用

当定义航天器的状态元素（例如 `SMA`、`X` 或 `DEC`）时，这些值是在航天器 `CoordinateSystem` 字段所定义的坐标系中设置的。例如，以下各行使 `MySat` 的 `Cartesian` 状态的 X 分量在 `EarthFixed` 坐标系中被设为 `1000`。

```
aSpacecraft.CoordinateSystem = EarthFixed
aSpacecraft.X = 1000
```

当上述脚本行在脚本中执行时，GMAT 将状态转换到指定的坐标系（此处为 `EarthFixed`），将 `X` 分量设为 `1000`，然后将状态转换回内部的惯性系表示。

下面的示例先在 `EarthMJ2000Eq` 坐标系中将 `SMA` 设为 `8000`，然后在地球固定坐标系中将 `X` 设为 `6000`。（注意：这在初始化模式下是不允许的；详见后文备注。）

```
aSpacecraft.CoordinateSystem = EarthMJ2000Eq
aSpacecraft.SMA = 8000
aSpacecraft.CoordinateSystem = EarthFixed
aSpacecraft.X = 6000
```

### 状态分量与航天器 Epoch 字段的相互作用

当指定航天器的历元时，所定义的是航天器在指定坐标系中的初始历元。如果为航天器选择的坐标系是随时间变化的系统（例如 `EarthFixed` 系统），那么所定义的状态就是该历元时刻 `EarthFixed` 系统中的状态。例如，以下各行会将 `MySat` 的直角坐标状态在 UTC 时间 `01 Dec 2000 12:00:00.000` 的 `EarthFixed` 系统中设为 `[7000 0 1300 0 7.35 1]`。

```
Create Spacecraft MySat
MySat.UTCGregorian     = '01 Dec 2000 12:00:00.000'
MySat.CoordinateSystem = EarthFixed

MySat.X  = 7000
MySat.Y  = 0
MySat.Z  = 1300
MySat.VX = 0
MySat.VY = 7.35
MySat.VZ = 1
```

对应的 `EarthMJ2000Eq` 表示为：

```
X  = -2320.30266
Y  = -6604.25075
Z  =  1300.02599
VX =  7.41609
VY = -2.60562
VZ =  0.99953
```

可以在任务序列中使用如下脚本行更改航天器的历元：

```
MySat.TAIGregorian = '02 Dec 2000 12:00:00.000'
```

当上述行在任务序列中执行时，GMAT 将状态转换到指定的坐标系，再转换到指定的状态类型——此处分别为 `EarthFixed` 和 `Cartesian`——将历元设为 `02 Dec 2000 12:00:00.000`，然后将状态转换回内部表示。此行为与 GUI 中航天器轨道对话框的行为相同。由于此例中的坐标系是随时间变化的，更改航天器历元导致航天器惯性状态表示发生了变化。历元更改为 `02 Dec 2000 12:00:00.000` 之后，`EarthMJ2000Eq` 状态表示现在为：

```
X  = -2206.35771
Y  = -6643.18687
Z  =  1300.02073
VX =  7.45981
VY = -2.47767
VZ =  0.99953
```

### 初始化期间的脚本限制

在脚本中设置航天器轨道状态时，需要注意一些限制。在脚本的初始化部分（`BeginMissionSequence` 命令之前），历元和坐标系只应设置一次；对这些参数的多次定义会导致错误或警告信息，并可能产生意料之外的结果。

此外，在初始化期间设置状态时，必须在对应于单一状态类型的一组字段中设置轨道状态。例如，使用 `X`、`Y`、`Z`、`VX`、`VY`、`VZ` 字段（`Cartesian` 状态类型）或 `SMA`、`ECC`、`INC`、`RAAN`、`AOP`、`TA` 字段（`Keplerian` 状态类型）设置轨道状态，但不能混合使用两者。如果需要混合使用状态类型、坐标系或历元来定义航天器的状态，必须在任务序列中（`BeginMissionSequence` 命令之后）通过脚本来设置状态。

### 共享状态分量

某些状态分量（例如 `SMA`）在多种状态表示之间共享。在任务序列中，GMAT 不要求指定正在设置的状态表示；相反，可以指定来自不同表示的元素组合。

对于这些共享分量，GMAT 为每个分量定义了默认表示，并在设置或读取共享分量的值时使用该表示。这通常是透明的，但如果默认表示存在奇点，或者因所设置或读取的值导致数值精度损失，则可能产生副作用。下表列出每个共享状态分量及其默认表示。

| 字段 | 共享于 | 默认表示 |
|---|---|---|
| `AOP` | Keplerian、ModifiedKeplerian | Keplerian |
| `DEC` | SphericalAZFPA、SphericalRADEC | SphericalAZFPA |
| `EquinoctialH` | AlternateEquinoctial、Equinoctial | Equinoctial |
| `EquinoctialK` | AlternateEquinoctial、Equinoctial | Equinoctial |
| `INC` | Keplerian、ModifiedKeplerian | Keplerian |
| `RA` | SphericalAZFPA、SphericalRADEC | SphericalAZFPA |
| `RAAN` | Keplerian、ModifiedKeplerian | Keplerian |
| `RMAG` | SphericalAZFPA、SphericalRADEC | SphericalAZFPA |
| `SMA` | AlternateEquinoctial、Equinoctial、Keplerian | Keplerian |
| `TA` | IncomingAsymptote、OutgoingAsymptote、Keplerian、ModifiedKeplerian | Keplerian |
| `VMAG` | SphericalAZFPA、SphericalRADEC | SphericalAZFPA |

举例来说，考虑以下任务序列。由于 GMAT 按顺序执行每条命令，它会使用所赋值的状态表示来计算每个分量。对于共享分量，则使用各自的默认表示。

```
BeginMissionSequence
aSpacecraft.SMA = 20000      % conversion goes through Keplerian
aSpacecraft.RA = 30          % conversion goes through SphericalAZFPA
aSpacecraft.OutgoingDHA = 90 % conversion goes through OutgoingAsymptote
aSpacecraft.TA = 45          % conversion goes through Keplerian
```

上述脚本中：`SMA` 的转换经由 Keplerian 表示；`RA` 经由 SphericalAZFPA；`OutgoingDHA` 经由 OutgoingAsymptote；`TA` 经由 Keplerian。

> **警告**
>
> 当使用非默认依赖关系设置状态参数时（尤其是在基于开普勒根数的表示中），请注意中间轨道的大幅转换可能导致精度损失。

## 示例

以 `Keplerian`（开普勒根数）表示法定义航天器的 Earth MJ2000Eq 坐标：

```
Create Spacecraft aSpacecraft
aSpacecraft.CoordinateSystem = EarthMJ2000Eq
aSpacecraft.SMA  = 7100
aSpacecraft.ECC  = 0.01
aSpacecraft.INC  = 30
aSpacecraft.RAAN = 45
aSpacecraft.AOP  = 90
aSpacecraft.TA   = 270
```

上述脚本在 EarthMJ2000Eq 坐标系中用开普勒根数设置轨道状态。

以 `Cartesian`（直角坐标）表示法定义航天器的地球固定坐标：

```
Create Spacecraft aSpacecraft
aSpacecraft.CoordinateSystem = EarthFixed
aSpacecraft.X = 7100
aSpacecraft.Y = 0
aSpacecraft.Z = 1300
aSpacecraft.VX = 0
aSpacecraft.VY = 7.35
aSpacecraft.VZ = 1
```

上述脚本在 EarthFixed 坐标系中用直角坐标设置轨道状态。

以 `ModifiedKeplerian`（修正开普勒根数）表示法定义航天器的月心坐标：

```
Create CoordinateSystem MoonInertial
MoonInertial.Origin = Luna
MoonInertial.Axes = BodyInertial

Create Spacecraft aSpacecraft
aSpacecraft.CoordinateSystem = MoonInertial
aSpacecraft.RadPer = 2100
aSpacecraft.RadApo = 2200
aSpacecraft.INC = 90
aSpacecraft.RAAN = 45
aSpacecraft.AOP = 45
aSpacecraft.TA = 180
```

上述脚本先创建以月球（Luna）为原点、BodyInertial 为轴的坐标系，再用修正开普勒根数设置轨道状态。

以 `SphericalAZFPA` 表示法定义航天器的旋转天平动点（Rotating Libration Point）坐标：

```
Create LibrationPoint ESL1
ESL1.Primary = Sun
ESL1.Secondary = Earth
ESL1.Point = L1

Create CoordinateSystem EarthSunL1CS
EarthSunL1CS.Origin = ESL1 
EarthSunL1CS.Axes = ObjectReferenced
EarthSunL1CS.XAxis = R
EarthSunL1CS.ZAxis = N
EarthSunL1CS.Primary = Sun
EarthSunL1CS.Secondary = Earth

Create Spacecraft aSpacecraft
aSpacecraft.CoordinateSystem = EarthSunL1CS
aSpacecraft.DateFormat = UTCGregorian
aSpacecraft.Epoch = '09 Dec 2005 13:00:00.000'
aSpacecraft.RMAG = 1520834.130720907
aSpacecraft.RA = -111.7450242065574
aSpacecraft.DEC = -20.23326432189756
aSpacecraft.VMAG = 0.2519453702907011
aSpacecraft.AZI = 85.22478175803107
aSpacecraft.FPA = 97.97050698644287
```

上述脚本创建日地 L1 天平动点及相应的 ObjectReferenced 坐标系，并用 SphericalAZFPA 球坐标设置轨道状态。

以 `Planetodetic`（行星测地）表示法定义航天器的地球固定坐标：

```
Create Spacecraft aSpacecraft
aSpacecraft.CoordinateSystem = EarthFixed
aSpacecraft.PlanetodeticRMAG = 7218.032973047435
aSpacecraft.PlanetodeticLON = 79.67188405817301
aSpacecraft.PlanetodeticLAT = 10.43478253417053
aSpacecraft.PlanetodeticVMAG = 6.905049647178043
aSpacecraft.PlanetodeticAZI = 81.80908019170981
aSpacecraft.PlanetodeticHFPA = 1.494615714741736
```

上述脚本在 EarthFixed 坐标系中用行星测地元素设置轨道状态。

以 `Equinoctial`（春分点根数）表示法设置航天器的 Earth MJ2000 黄道坐标：

```
Create Spacecraft aSpacecraft
aSpacecraft.CoordinateSystem = EarthMJ2000Ec
aSpacecraft.SMA = 9100
aSpacecraft.EquinoctialH = 0.00905
aSpacecraft.EquinoctialK = 0.00424
aSpacecraft.EquinoctialP = -0.1059
aSpacecraft.EquinoctialQ = 0.14949
aSpacecraft.MLONG = 247.4528
```

上述脚本在 EarthMJ2000Ec（黄道）坐标系中用春分点根数设置轨道状态。
