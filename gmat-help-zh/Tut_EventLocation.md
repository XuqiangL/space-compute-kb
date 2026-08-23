# 第 11 章 查找日食与地面站接触（Finding Eclipses and Station Contacts）
> 译自 GMAT R2026a 帮助文档 Tut_EventLocation.html

| 项目 | 内容 |
| --- | --- |
| 适用读者（Audience） | 初学者 |
| 时长（Length） | 30 分钟 |
| 先修要求（Prerequisites） | 完成[简单轨道转移](SimpleOrbitTransfer.md) |
| 脚本文件（Script File） | `Tut_SimpleOrbitTransfer.script` |

## 本章目录

- 目标与概述（本节）
- [加载任务](ch11s02.md)
- [配置 GMAT 以进行事件定位](ch11s03.md)：验证 SolarSystem 配置；配置 CelestialBody 资源
- [配置并运行日食定位器](ch11s04.md)：创建并配置 EclipseLocator；运行任务
- [配置并运行接触定位器](ch11s05.md)：创建并配置地面站；创建并配置 ContactLocator；运行任务
- [进阶练习](ch11s06.md)

## 目标与概述（Objective and Overview）

在本教程中，我们将修改一个已有任务，使用 `EclipseLocator`（日食定位器）和 `ContactLocator`（接触定位器）资源为其添加日食（eclipse）与地面站接触（station contact）检测。我们将从已完成的“简单轨道转移”任务出发，对其进行修改以添加这些事件报告。

本教程的基本步骤如下：

1. 加载“简单轨道转移”任务。
2. 配置 GMAT 以进行事件定位（Event Location）。
3. 添加并配置一个 `EclipseLocator`，用于报告日食。
4. 运行任务并分析日食报告。
5. 添加并配置一个 `GroundStation`（地面站）和一个 `ContactLocator`，用于报告接触时间。
6. 运行任务并分析接触报告。
