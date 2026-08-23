# 运行平滑器命令（RunSmoother）

> 译自 GMAT R2026a 帮助文档 RunSmoother.html

**RunSmoother** —— 运行序贯平滑估计器。

## 脚本语法

```
RunSmoother Smoother_InstanceName
```

## 描述

`RunSmoother` 命令读入导航测量量，并按照输入 `Smoother` 资源的规格生成估计状态向量。

**另请参阅**：ExtendedKalmanFilter、Smoother

## 备注

GMAT 目前仅实现了一种平滑器，采用 Fraser-Potter 算法。该算法从前向 `ExtendedKalmanFilter` 估计器处理的最后一个测量量开始运行反向滤波器，然后通过对前向和反向序贯滤波器进行加权平均，生成改进的状态估计。

在运行平滑器之前，必须先运行 `ExtendedKalmanFilter` 估计器（使用 `RunEstimator` 命令）。

## 示例

运行滤波器和平滑器估计器。

```
Create ExtendedKalmanFilter myEKF
Create Smoother myFPSmoother

BeginMissionSequence

RunEstimator myEKF
RunSmoother myFPSmoother
```

**中文说明**：先创建扩展卡尔曼滤波器 myEKF 和平滑器 myFPSmoother，在任务序列中先运行估计器（前向滤波），再运行平滑器（反向滤波+融合）。
