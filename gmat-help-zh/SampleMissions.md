# 示例任务（Sample Missions）
> 译自 GMAT R2026a 帮助文档 SampleMissions.html

GMAT 发行版包含 30 多个示例任务。这些示例展示了如何将 GMAT 应用于从霍曼转移（Hohmann transfer）到平动点站位保持、再到轨迹优化的各类问题。要找到并运行示例任务：

1. 打开 GMAT。
2. 在工具栏上单击 Open（打开）。
3. 导航到 GMAT 根目录中的 `samples` 文件夹。
4. 双击您选择的脚本文件。
5. 单击 Run（运行）按钮。

> [图：Run（运行任务）工具栏图标]

某些优化任务需要 MATLAB、MATLAB 优化工具箱、VF13 优化器或 Yukon 优化器。其中一些是专有库，不随 GMAT 分发。对于使用了您不可用的优化器的示例任务，您可以尝试改用 GMAT 自带的 Yukon 优化器。MATLAB 的 `fmincon` 优化器目前仅在 Windows 平台上与 GMAT 配合使用。有关配置 MATLAB 优化器的详细信息，请参阅《MATLAB 接口（MATLAB Interface）》（见 MatlabInterface.html）。
