# 创建并配置批处理估计器对象（DSN_Estimation_Create_and_configure_BatchEstimator_object）

> 译自 GMAT R2026a 帮助文档 DSN_Estimation_Create_and_configure_BatchEstimator_object.html

如下所示，我们创建并配置用于定义估计过程的 `BatchEstimator` 对象。

```
Create BatchEstimator bat
bat.ShowProgress               = true;
bat.ReportStyle                = Normal;
bat.ReportFile                 =  ...
         'Orbit Estimation using DSN Range and Doppler Data.report';
bat.Measurements               = {DSNsimData} 
bat.AbsoluteTol                = 0.001;
bat.RelativeTol                = 0.0001;
bat.MaximumIterations          = 10
bat.MaxConsecutiveDivergences  = 3;
bat.Propagator                 = Prop;
bat.ShowAllResiduals           = On;
bat.OLSEInitialRMSSigma        = 10000;
bat.OLSEMultiplicativeConstant = 3;
bat.OLSEAdditiveConstant       = 0;
bat.EstimationEpochFormat      = 'FromParticipants'; 
bat.InversionAlgorithm         = 'Internal';    
bat.MatlabFile                 =  ...
           'Orbit Estimation using DSN Range and Doppler Data.mat'
```

**中文说明**：创建名为 bat 的批处理估计器，配置报告输出、测量数据、收敛准则、积分器、外循环 sigma 编辑和 MATLAB 输出文件。

上述所有字段在 `BatchEstimator` 帮助中都有描述，但我们在此也简要说明。在上面第一行脚本中，我们创建了 `BatchEstimator` 对象 `bat`。在下一行，我们将 `ShowProgress` 字段设为 true，以便在消息窗口中显示批处理估计器的详细输出。

在第三行，我们将 `ReportStyle` 设为 Normal。如果我们想查看测量偏导数等额外数据，可以通过在 GMAT 启动文件中设置 RUN_MODE = Testing 来使用 Verbose 样式。在下一行，我们将 `ReportFile` 字段设为所需输出文件的名称，默认写入 GMAT 的 'output' 目录。

我们将 Measurements 字段设为希望使用的 `TrackingFileSet` 资源名称。回想一下，我们在"定义要处理的测量类型"一节中创建的 `TrackingFileSet` `DSNsimData` 定义了我们希望处理的测量类型。在本例中，我们希望处理与 `CAN`、`GDS` 和 `MAD` 地面站关联的 DSN 测距和多普勒数据。

接下来四个字段 `AbsoluteTol`、`RelativeTol`、`MaximumIterations` 和 `MaxConsecutiveDivergences` 定义批处理估计器的收敛准则。完整细节请参见 `BatchEstimator` 帮助中的"收敛准则的行为"（Behavior of Convergence Criteria）讨论。

下一行脚本设置 Propagator 字段，指定估计过程中应使用哪个 `Propagator` 对象。我们将此字段设为在"定义要处理的测量类型"一节中创建的 `Prop` `Propagator` 对象。

在第 11 行脚本中，我们将 `ShowAllResiduals` 字段设为 true，以显示与各地面站关联的观测残差图。

接下来三行脚本设置与 GMAT 外循环 sigma 编辑（OLSE）能力相关的字段 `OLSEInitialRMSSigma`、`OLSEMultiplicativeConstant` 和 `OLSEAdditiveConstant`，OLSE 用于编辑（即移除）某些测量量，使其不用于计算轨道估计。完整细节请参见 `BatchEstimator` 帮助中的"外循环 sigma 编辑（OLSE）的行为"讨论。

接下来，我们将 `EstimationEpochFormat` 字段设为 'FromParticipants'，这告诉 GMAT 与求解变量（本例中为 `Sat` 的笛卡尔状态）关联的历元来自 `Sat.Epoch` 的值，我们已将其设为 "19 Aug 2015 00:00:00.000 UTCG"。

接下来，我们将 `InversionAlgorithm` 字段设为 'Internal'，指定 GMAT 用于求逆法方程的算法。还有另外两种求逆算法 'Cholesky' 或 'Schur' 可供选择。

最后，我们设置 `MatlabFile` 的值。这是将创建的 MATLAB 输出文件的名称，默认写入 GMAT 的 'output' 目录。此文件可读入 MATLAB 进行详细计算和分析。只有在安装了 MATLAB 并正确配置与 GMAT 的接口时，才能创建 MATLAB 文件。
