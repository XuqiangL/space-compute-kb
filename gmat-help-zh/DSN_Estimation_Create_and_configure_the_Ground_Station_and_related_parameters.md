# 创建并配置地面站及相关参数（DSN_Estimation_Create_and_configure_the_Ground_Station_and_related_parameters）

> 译自 GMAT R2026a 帮助文档 DSN_Estimation_Create_and_configure_the_Ground_Station_and_related_parameters.html

## 创建地面站发射机、接收机和天线对象

在创建 `GroundStation` 对象本身之前，如下所示，我们首先创建必须与任何 `GroundStation` 关联的 `Transmitter`、`Receiver` 和 `Antenna` 对象。

```
%  Ground Station electronics. 
Create Transmitter DSNTransmitter;
Create Receiver DSNReceiver;
Create Antenna DSNAntenna;

DSNTransmitter.PrimaryAntenna     = DSNAntenna;
DSNReceiver.PrimaryAntenna        = DSNAntenna;
DSNTransmitter.Frequency          = 7200;   %MHz
```

**中文说明**：创建发射机、接收机、天线三个对象；将发射机和接收机的主天线都设为 DSNAntenna；发射机频率设为 7200 MHz。

在上面的脚本片段中，我们首先创建了 `Transmitter`、`Receiver` 和 `Antenna` 对象。GMAT 脚本行 `DSNTransmitter.PrimaryAntenna = DSNAntenna` 设置 `Transmitter` 资源 `DSNTransmitter` 将使用的主天线。同样，`DSNReceiver.PrimaryAntenna = DSNAntenna` 脚本行设置 `Receiver` 资源 `DSNReceiver` 将使用的主天线。如前所述，`Antenna` 对象目前没有功能，但我们在此包含它，既因为 GMAT 要求，也为了完整性，因为 `Antenna` 资源在未来 GMAT 版本中可能会有功能。最后，我们在上面最后一行 GMAT 脚本中设置发射机频率。此输入频率如何使用的完整描述请参见 `RunEstimator` 帮助。如帮助中所述，由于本例中我们将使用斜坡表，此输入频率不会用于计算测距和多普勒观测的计算值。取而代之的是，斜坡表中的频率值将用于计算测距和多普勒观测的计算值。

对上述陈述有一点澄清。如 `RunEstimator` 帮助中所讨论的，上面讨论的 `DSNTransmitter.Frequency` 值以及先前讨论的 `SatTransponder` `TurnAroundRatio` 值将用于计算确定测距和多普勒测量计算值 C 所需的（通常很小的）介质修正。

## 创建地面站

下面，我们创建并配置 `CAN` `GroundStation` 对象。

```
%   Create ground station and associated error models
Create GroundStation CAN;
CAN.CentralBody           = Earth;
CAN.StateType             = Cartesian;
CAN.HorizonReference      = Ellipsoid;
CAN.Location1             = -4461.083514
CAN.Location2             = 2682.281745
CAN.Location3             = -3674.570392
CAN.Id                    = 22222;
CAN.MinimumElevationAngle = 7.0;
CAN.IonosphereModel       = 'IRI2007';
CAN.TroposphereModel      = 'HopfieldSaastamoinen';
CAN.AddHardware           = {DSNTransmitter, DSNAntenna, ...
                                DSNReceiver};
```

**中文说明**：创建 CAN 地面站（堪培拉），中心天体为地球，以地固笛卡尔坐标给出站址，站 ID 为 22222，最小仰角 7 度，电离层模型 IRI2007，对流层模型 HopfieldSaastamoinen，挂接发射机、天线和接收机。

上面的脚本片段分为五个部分。第一部分创建 `GroundStation` 对象并设置地固笛卡尔坐标。第二部分设置地面站 ID，以便 GMAT 能够识别 GMD 文件中包含的来自此地面站的数据。

第三部分将最小仰角设为 7 度。低于此地面站到航天器仰角时，不使用任何测量数据形成轨道估计。第四部分指定我们希望用于建模射频信号大气折射效应的对流层和电离层模型。最后，第五部分将先前创建的三件必需硬件——发射机、接收机和天线——挂接到地面站。

接下来，我们创建并配置 `GDS` `GroundStation` 资源及关联的 `Transmitter` 资源。

```
%   Create GDS transmitter and ground station 
Create GroundStation GDS;  
GDS.CentralBody           = Earth;
GDS.StateType             = Cartesian;
GDS.HorizonReference      = Ellipsoid;
GDS.Location1             = -2353.621251;
GDS.Location2             = -4641.341542;
GDS.Location3             = 3677.052370;
GDS.Id                    = '33333';
GDS.MinimumElevationAngle = 7.0;
GDS.IonosphereModel       = 'IRI2007';
GDS.TroposphereModel      = 'HopfieldSaastamoinen';
GDS.AddHardware           = {DSNTransmitter, DSNAntenna, ...
                                DSNReceiver};
```

**中文说明**：创建 GDS 地面站（戈德斯通），站 ID 33333，其余配置与 CAN 相同。

接下来，我们创建并配置 `MAD` `GroundStation` 资源及关联的 `Transmitter` 资源。

```
%   Create MAD transmitter and ground station 
Create GroundStation MAD;  
MAD.CentralBody           = Earth;
MAD.StateType             = Cartesian;
MAD.HorizonReference      = Ellipsoid;
MAD.Location1             = 4849.519988;
MAD.Location2             = -360.641653;
MAD.Location3             = 4114.504590;
MAD.Id                    = '44444';
MAD.MinimumElevationAngle = 7.0;
MAD.IonosphereModel       = 'IRI2007';
MAD.TroposphereModel      = 'HopfieldSaastamoinen';
MAD.AddHardware           = {DSNTransmitter, DSNAntenna, ...
                                DSNReceiver};
```

**中文说明**：创建 MAD 地面站（马德里），站 ID 44444，其余配置相同。

## 创建地面站误差模型

众所周知，所有测量类型都有与之关联的随机噪声和/或偏差。在 GMAT 中，这些效应用地面站误差模型建模。由于我们已经创建了 `GroundStation` 对象及其相关硬件，现在创建地面站误差模型。由于我们希望使用测距和多普勒数据形成轨道估计，需要创建两个误差模型，如下所示，一个用于测距测量，一个用于多普勒测量。

```
%   Create Ground station error models
Create ErrorModel DSNrange;
DSNrange.Type                   = 'DSN_SeqRange';
DSNrange.NoiseSigma             = 10.63;
DSNrange.Bias                   = 0.0;

Create ErrorModel DSNdoppler;
DSNdoppler.Type                 = 'DSN_TCP';
DSNdoppler.NoiseSigma           = 0.0282;
DSNdoppler.Bias                 = 0.0;

CAN.ErrorModels                 = {DSNrange, DSNdoppler};
GDS.ErrorModels                 = {DSNrange, DSNdoppler};
MAD.ErrorModels                 = {DSNrange, DSNdoppler};
```

**中文说明**：创建两个误差模型——DSNrange（DSN_SeqRange 类型，噪声 sigma 10.63 测距单位，偏差 0）和 DSNdoppler（DSN_TCP 类型，噪声 sigma 0.0282 Hz，偏差 0），并将它们挂接到三个地面站。

上面的脚本片段分为三个部分。第一部分定义名为 `DSNrange` 的 `ErrorModel`。误差模型 Type 为 DSN_SeqRange，表明它是 DSN 序列测距测量的误差模型。高斯白噪声的 1 sigma 标准差设为 10.63 测距单位（RU），测量偏差设为 0 RU。

上面第二部分定义名为 `DSNdoppler` 的 `ErrorModel`。误差模型 `Type` 为 DSN_TCP，表明它是 DSN 总计数相位导出多普勒测量的误差模型。高斯白噪声的 1 sigma 标准差设为 0.0282 Hz，测量偏差设为 0 Hz。上述测距和多普勒 `NoiseSigma` 值将用于形成估计算法使用的测量加权矩阵。

上面第三部分将我们刚创建的两个 `ErrorModel` 资源挂接到 `CAN`、`GDS` 和 `MAD` `GroundStation` 资源。注意，在 GMAT 中，测量噪声或偏差是按地面站定义的。因此，任何涉及 `CAN`、`GDS` 和 `MAD` `GroundStation` 的测距测量误差由 `DSNRange` `ErrorModel` 定义，任何涉及这些地面站的多普勒测量误差由 `DSNdoppler` `ErrorModel` 定义。注意，如果需要，我们也可以创建 6 个不同的 `ErrorModel` 资源——为 3 个地面站各创建代表两种数据类型的两个误差模型。
