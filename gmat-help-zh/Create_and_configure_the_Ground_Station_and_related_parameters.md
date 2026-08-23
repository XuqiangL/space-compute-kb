# 创建并配置地面站及相关参数（Create_and_configure_the_Ground_Station_and_related_parameters）

> 译自 GMAT R2026a 帮助文档 Create_and_configure_the_Ground_Station_and_related_parameters.html

（本小节属于"第 13 章 仿真 DSN 测距与多普勒数据"教程）

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

**中文说明**：创建发射机、接收机、天线三个对象；发射机和接收机的主天线均设为 DSNAntenna；发射机频率设为 7200 MHz。

在上面的脚本片段中，我们首先创建了 `Transmitter`、`Receiver` 和 `Antenna` 对象。GMAT 脚本行 `DSNTransmitter.PrimaryAntenna = DSNAntenna` 设置 `Transmitter` 对象将使用的主天线。同样，`DSNReceiver.PrimaryAntenna = DSNAntenna` 脚本行设置 `Receiver` 对象将使用的主天线。如前所述，`Antenna` 对象目前没有功能，但我们在此包含它，既因为 GMAT 要求，也为了完整性，因为 `Antenna` 资源在未来 GMAT 版本中可能会有功能。最后，我们在上面最后一行 GMAT 脚本中设置发射机频率。此输入频率如何使用的完整描述请参见 `RunSimulator` 帮助。如帮助中所述，由于本例中我们不使用斜坡表，此输入频率将用于计算测距和多普勒观测的仿真值。此外，此输入频率还将输出到 `RunSimulator` 命令创建的测距数据文件中。

## 创建地面站

下面，我们创建并配置一个 `GroundStation` 对象。

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

**中文说明**：创建 CAN 地面站（堪培拉），中心天体为地球，以地固笛卡尔坐标给出站址，站 ID 22222（将写入 GMD 文件），最小仰角 7 度，电离层模型 IRI2007，对流层模型 HopfieldSaastamoinen，挂接发射机、天线和接收机。

上面的脚本片段分为五个部分。第一部分创建 `GroundStation` 对象并设置地固笛卡尔坐标。第二部分设置地面站 ID，该 ID 将输出到 `RunSimulator` 命令创建的 GMD 文件。第三部分将最小仰角设为 7 度。低于此地面站到航天器仰角时，不会创建仿真数据。第四部分指定我们希望用于建模射频信号大气折射效应的对流层和电离层模型。最后，第五部分将先前创建的三件必需硬件——发射机、接收机和天线——挂接到地面站。

## 创建地面站误差模型

众所周知，所有测量类型都有与之关联的随机噪声和/或偏差。在 GMAT 中，这些效应用地面站误差模型建模。由于我们已经创建了 `GroundStation` 对象及其相关硬件，现在创建地面站误差模型。由于我们希望仿真测距和多普勒数据，需要创建两个误差模型，如下所示，一个用于测距测量，一个用于多普勒测量。

```
%   Create Ground station error models
Create ErrorModel DSNrange;
DSNrange.Type                  = 'DSN_SeqRange';
DSNrange.NoiseSigma            = 10.63;
DSNrange.Bias                  = 0.0;

Create ErrorModel DSNdoppler;
DSNdoppler.Type                = 'DSN_TCP';
DSNdoppler.NoiseSigma          = 0.0282;
DSNdoppler.Bias                = 0.0;

CAN.ErrorModels                = {DSNrange, DSNdoppler};
```

**中文说明**：创建两个误差模型——DSNrange（DSN_SeqRange 类型，噪声 sigma 10.63 测距单位，偏差 0）和 DSNdoppler（DSN_TCP 类型，噪声 sigma 0.0282 Hz，偏差 0），并挂接到 CAN 地面站。

上面的脚本片段分为三个部分。第一部分定义名为 `DSNrange` 的 `ErrorModel`。误差模型 Type 为 DSN_SeqRange，表明它是 DSN 序列测距测量的误差模型。高斯白噪声的 1 sigma 标准差设为 10.63 测距单位（RU），测量偏差设为 0 RU。

上面第二部分定义名为 `DSNdoppler` 的 `ErrorModel`。误差模型 Type 为 DSN_TCP，表明它是 DSN 总计数相位导出多普勒测量的误差模型。高斯白噪声的 1 sigma 标准差设为 0.0282 Hz，测量偏差设为 0 Hz。

上面第三部分将我们刚创建的两个 `ErrorModel` 资源挂接到 `CAN` `GroundStation`。注意，在 GMAT 中，测量噪声或偏差是按地面站定义的。因此，任何涉及 CAN 地面站的测距测量误差由 `DSNRange` `ErrorModel` 定义，任何涉及 `CAN` `GroundStation` 的多普勒测量误差由 `DSNdoppler` `ErrorModel` 定义。注意，由于 GMAT 目前只建模发射和接收地面站相同的双向测量，我们不必考虑发射和接收地面站不同的情况。假设我们要向此仿真添加额外的 `GroundStation`，涉及此新 `GroundStation` 的观测的测量误差将由挂接到它的 `ErrorModel` 资源定义。

关于我们如何确定所创建的两个 `ErrorModel` 资源的 NoiseSigma 值，请参见"附录 A —— 测量噪声值的确定"中的讨论。
