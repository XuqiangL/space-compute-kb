# OpenFrames 可视化接口（OpenFramesInterface）

> 译自 GMAT R2026a 帮助文档 OpenFramesInterface.html

**OpenFramesInterface** —— 用户自定义资源，为 GMAT 任务提供高性能的 3D 交互式可视化。

## 描述

> **注意**：`OpenFramesInterface` 的主要文档见其在线 GitLab Wiki（https://gitlab.com/EmergentSpaceTechnologies/OpenFramesInterface/wikis/home）。你可以按任意 GUI 面板上的 **Help（帮助）** 按钮直接访问相关的 Wiki 章节。

`OpenFramesInterface`（**OFI**）资源允许你使用高性能、可定制且易于使用的交互式 3D 图形来可视化 GMAT 任务。OFI 是作为 `OrbitView`（轨道视图）的替代品而开发的，因此它在保留相似 GUI 和脚本格式的同时提供了更强的功能和性能。无论你对 `OrbitView` 的熟悉程度如何，都能轻松使用 `OpenFramesInterface`！

OFI 的特性和优势包括：

- 每个窗口可创建多个交互式视图。每个视图可以跟随航天器或其他天体，甚至可以自动旋转以跟踪另一个对象。
- 控制仿真时间，以任何所需速率（包括实时和倒退时间）播放场景动画，并在多个窗口之间同步时间。
- 许多可视化更改会立即生效，无需重新运行任务。
- 为航天器和天体使用各种 3D 模型格式：3ds、lwo、obj 等。
- 使用 Oculus Rift 或 HTC Vive 等头显在虚拟现实中查看任何 GMAT 任务。VR 能提供关于非平面轨迹的信息，而这些信息在传统显示器上难以获得。

> **提示**：GMAT 的 `samples/NeedOpenFramesInterface` 文件夹中有基于同名 `OrbitView` 示例脚本使用 OFI 的示例。

**另请参阅**：`OrbitView`