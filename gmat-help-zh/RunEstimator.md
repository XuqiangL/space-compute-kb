# 运行估计器命令（RunEstimator）

> 译自 GMAT R2026a 帮助文档 RunEstimator.html

**RunEstimator** —— 读入导航测量量并生成估计状态向量。

## 脚本语法

```
RunEstimator BatchEstimator_InstanceName [{SolveMode = value}]
RunEstimator ExtendedKalmanFilter_InstanceName
```

## 描述

`RunEstimator` 命令读入导航测量量，并按照输入的 `BatchEstimator` 或 `ExtendedKalmanFilter` 资源的规格生成估计状态向量。

**另请参阅**：BatchEstimator、ExtendedKalmanFilter

## 选项

| 选项 | 描述 |
|------|------|
| **SolveMode** | 指定 `BatchEstimator` 在任务执行期间的行为。当 `SolveMode` 设为 `RunInitialGuess` 时，批处理估计器将执行"观测减计算"（observed-minus-computed）运行。GMAT 将计算并报告相对于初始状态或轨道的残差，但不会尝试微分改正，运行将在第 0 次迭代结束时终止。当 `SolveMode` 设为 `Solve` 时，`BatchEstimator` 将执行微分改正并迭代，直到满足估计器停止条件。<br>`ExtendedKalmanFilter` 估计器忽略此参数。<br>接受的数据类型：引用数组；允许值：`Solve`、`RunInitialGuess`；默认值：`Solve`；是否必需：否；接口：GUI、脚本 |

## 备注

### GMAT 如何生成"计算值 (C)"DSN 数据

作为估计过程的一部分，GMAT 必须计算所谓的观测残差"O-C"，其中"C"是"计算"测量量。如 RunSimulator 帮助中所述，GMAT 按下式计算 DSN 测距"C"测量量：

C = ∫[t1→t3] f_T(t) dt，mod M　　(RU)

其中：

- t1, t3 = 分别为发射历元和接收历元
- f_T = 地面站发射频率
- C = 与发射机有关的常数（X 频段为 221/1498，S 频段为 1/2）
- M = 测距码长度，以 RU（测距单位）计

GMAT 按下式计算 DSN 多普勒测量量：

C = −M2/(t3e − t3s) · ∫[t1s→t1e] f_T(t1) dt1 = −M2·f̄_T·(t1e − t1s)/DCI　　(Hz)

其中：

- t1s, t1e = 分别为发射区间的起点和终点
- f_T = 发射频率
- M2 = 应答机转发比（通常 S 频段为 240/221，X 频段为 880/749）
- DCI = (t3e − t3s) = 多普勒计数区间（Doppler Count Interval）
- f̄_T ≡ ∫[t1s→t1e] f_T(t1) dt1 / (t1e − t1s) = 平均发射频率

用于计算"计算"测距或多普勒测量量的 C 和 M2 的值取决于数据类型，以及所读入的数据是斜坡还是非斜坡数据，如下表所示。用于计算"计算"测量量的发射频率的值取决于所读入的数据是否为斜坡数据。

| 数据类型 | 用于计算"计算"测量量的 C（测距）或 M2（多普勒） | 用于计算"计算"测量量的发射频率 |
|----------|--------------------------------------------------|--------------------------------|
| **估计测距（无斜坡表）** | 根据输入测距 GMD 文件中的上行频段设置。S 频段 C=1/2，X 频段 C=221/1498。 | 使用输入测距 GMD 文件中的频率；不使用通过 Transmitter.Frequency 设置的地面站发射频率。 |
| **估计测距（有斜坡表）** | 根据输入斜坡表中的上行频段设置。S 频段 C=1/2，X 频段 C=221/1498。输入测距测量文件中的上行频段值无影响。 | 使用斜坡表中的频率；不使用输入 GMD 文件中的频率；不使用通过 Transmitter.Frequency 设置的地面站发射频率。 |
| **估计多普勒（无斜坡表）** | M2 = Transponder.TurnAroundRatio。输入测量文件中的上行频段值无影响。 | 使用通过 Transmitter.Frequency 设置的地面站发射频率（注意：多普勒数据的 GMD 文件中没有频率数据）。 |
| **估计多普勒（有斜坡表）** | 根据输入斜坡表中的上行频段设置。S 频段 M2=240/221，X 频段 M2=880/749。输入多普勒 GMD 测量文件中的上行频段值无影响。 | 使用斜坡表中的频率（注意：多普勒数据的 GMD 文件中没有频率数据）；不使用通过 Transmitter.Frequency 设置的地面站发射频率。 |

### 地球章动更新间隔

如果希望估计器精确计算多普勒或测距变率类型测量量（例如 DSN_TCP 和 RangeRate）的残差，需要按如下方式将地球章动更新间隔设为 0。

```
Earth.NutationUpdateInterval = 0
```

对所有测量类型，将地球章动更新间隔设为零都是良好的通用做法。

## 示例

运行批处理估计器。

```
Create BatchEstimator myBatchEstimator

BeginMissionSequence
RunEstimator myBatchEstimator
```

**中文说明**：创建批处理估计器 myBatchEstimator 后，在任务序列中用 RunEstimator 执行估计。

若要查看读入测量量并运行估计器的综合示例，请参见第 14 章《Orbit Estimation using DSN Range and Doppler Data》教程。
