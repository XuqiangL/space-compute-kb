# 配置 GMAT（ConfiguringGmat）

> 译自 GMAT R2026a 帮助文档 ConfiguringGmat.html

下面讨论随 GMAT 分发、且为 GMAT 运行所必需的文件和数据。GMAT 使用多种类型的数据文件，包括行星历表文件、地球定向数据、闰秒文件和重力系数文件。本节介绍这些文件的组织方式以及用于自定义它们的控制项。

## 文件结构

GMAT 的默认目录结构分为 12 个主要子目录。这些目录组织了运行 GMAT 所用的文件和数据，包括二进制库、数据文件、纹理贴图和 3D 模型。建议用户查阅安装根目录中的 README 文件。下面各小节概述每个子目录的内容。

> [图：GMAT 根目录结构]

### api

`api` 目录包含帮助用户配置和上手使用 GMAT 应用程序编程接口（API）的脚本。GMAT API 允许用户从 Python 和 MATLAB 等其他编程环境访问 GMAT 功能。该文件夹中提供了 Python 和 MATLAB 的示例脚本。按照 `API_README.txt` 文件中的说明即可开始使用 GMAT API。

### bin

`bin` 目录包含 GMAT 核心功能所需的全部二进制文件。这些库包括可执行文件（Windows 上为 `GMAT.exe`，Mac 上为 `GMAT.app`，Linux 上为 `GMAT`）和平台特定的支持库。`bin` 目录还包含两个文本文件：`gmat_startup_file.txt` 和 `gmat.ini`。启动文件在单独的一节中详细讨论。`gmat.ini` 文件用于配置某些 GUI 面板、设置外部网络链接的路径以及定义 GUI 工具提示消息。

### data

`data` 目录包含运行 GMAT 所需的全部数据文件，并按数据类型组织，如下所述。

> [图：GMAT data 目录结构]

- `api` 目录包含一个帮助文件，GMAT 在 API 交互式会话中用它提供帮助。
- `atmosphere` 目录包含行星大气建模所需的数据文件。特别是，地球大气建模的默认文件存放在 atmosphere/earth 文件夹中。地球大气文件可以在该目录中手动更新，也可以使用 `utilities/python/GMATDataFileManager.py` 工具更新。也可以在你的 GMAT 脚本中指向这些文件的替代路径。
- `emtg` 文件夹包含与将 GMAT 与演化任务轨迹生成器（EMTG）工具结合使用相关的文件和脚本。
- `graphics` 目录包含 GMAT 可视化工具的数据文件，以及应用程序图标和图像。`splash` 目录包含 GMAT 初始化时短暂显示的启动画面。`stars` 目录包含用于在 3D 图形中显示恒星的星表。texture 文件夹包含用于 2D 和 3D 图形资源的纹理贴图。`icons` 目录包含运行时加载的图标和图像的图形文件，如 GMAT 徽标和 GUI 图标。
- `gravity` 目录包含每个具有默认非球形重力模型的天体的重力系数文件。在每个目录内，系数文件按其所表示的模型命名，使用扩展名 `.cof`。
- `gui_config` 目录包含用于配置 GMAT 资源和命令的部分 GUI 对话框的文件。这些文件让你可以轻松为用户提供的插件创建 GUI 面板，也被一些内置 GUI 面板使用。
- `hardware` 文件夹包含一个示例时钟锥角文件。
- `icrf` 文件夹包含 ICRF 坐标转换所需的数据表。
- `IonosphereData` 目录包含 GMAT 轨道确定工具所采用的地球电离层模型所需的文件。该目录中有两个文件需要例行维护：`ap.dat` 文件包含过去和预测的 Ap 指数观测记录；ig_rz.dat 文件包含过去和预测的太阳通量观测记录。使用 IRI 电离层模型进行轨道确定的用户应确保这些文件始终包含足以覆盖处理时间段的数据。这两个文件都可以手动更新，或使用 `utilities/python/GMATDataFileManager.py` 工具更新。该目录中的其余文件不应更新。
- `misc` 目录包含与某些优化器使用相关的文件。
- `planetary_coeff` 目录包含国际地球自转服务（IERS）提供的地球定向参数（EOP）以及不同章动理论的章动系数。
- `planetary_ephem` 目录包含 DE 和 SPK 两种格式的行星历表数据。`de` 目录包含由 JPL 开发和分发的 8 大行星、月球和冥王星的二进制数字历表 DE405 文件。`spk` 目录包含 DE421 SPICE 内核以及选定彗星、小行星和卫星的内核。随 GMAT 分发的所有历表文件均为小端（little-endian）格式。
- `time` 目录包含 JPL 闰秒内核 `SPICELeapSecondKernel.tls` 和 GMAT 闰秒文件 `tai-utc.dat`。
- `vehicle` 目录包含选定航天器的历表数据和 3D 模型。`ephem` 目录包含 SPK 历表文件，包括轨道、姿态、参考架和时间内核。`models` 目录包含 3DS 或 POV 格式的 3D 模型文件，供 GMAT 的 `OrbitView` 可视化资源使用。

### docs

`docs` 目录包含最终用户文档，包括数学规范、体系结构规范和估计规范的 PDF 草案版本。GMAT 用户指南在 `help` 目录中以 PDF 和 HTML 格式以及 Windows HTML Help 文件形式提供。

### extras

`extras` 目录包含各种有助于使用 GMAT 但不属于核心代码库的额外便利文件。目前这里唯一的文件是 Notepad++ 文本编辑器中 GMAT 脚本语言的语法着色文件。

### matlab

`matlab` 目录包含 GMAT 的 MATLAB 接口所需的 M 文件，包括与 fmincon 优化器的接口。要使 MATLAB 接口正常工作，`matlab` 目录及其子目录中的所有文件都必须包含在你的 MATLAB 路径中。

### output

`output` 目录是星历文件和报告文件等文件输出的默认位置。如果在 GMAT 会话期间创建的报告或星历文件没有提供路径信息，这些文件将被写入 output 文件夹。

### plugins

`plugins` 目录包含使用 GMAT 时并非必需的可选插件。`proprietary` 目录用于不能自由分发的第三方库，在开源发行版中是一个空文件夹。

### samples

`samples` 目录包含示例任务和脚本，范围从霍曼转移到天平动点保持再到火星 B 平面瞄准。示例文件以 "Ex_" 开头，与 GMAT 教程对应的文件以 "Tut_" 开头。这些文件旨在演示 GMAT 的能力，并为你针对自己的应用和飞行领域构建常见任务类型提供潜在的起点。具有特定要求的示例位于 `NeedMatlab` 和 `NeedVF13ad` 等子目录中。

### userfunctions

`userfunctions` 目录包含 GMAT 发行版中包含的 MATLAB、Python 和 GMAT 函数。你也可以把自己的自定义函数存放在名为 GMAT、Python 和 MATLAB 的子目录中。GMAT 会把这些子目录包含在其搜索路径中，以定位 GMAT 脚本和 GMAT 函数中引用的函数。

### userincludes

`userincludes` 目录提供了一个位置，GMAT 默认会自动在其中搜索使用 `#Include` 宏导入脚本的代码文件。用户可以通过修改启动文件中的 GMAT_INCLUDE_PATH 变量，或在启动文件中添加额外的 GMAT_INCLUDE_PATH 赋值来更改包含文件的搜索路径。如果存在多个赋值，GMAT 按赋值顺序搜索以查找任何 `#Include` 文件。

### utilities

`utilities` 目录包含一些有用的 Python 工具。该目录包括 GMAT 数据文件管理器（GMATDataFileManager.py），运行它可以更新 GMAT 所需的许多环境数据文件（如空间天气、EOP 和闰秒文件）。

`navigation` 子目录包含一些有助于分析扩展卡尔曼滤波运行输出的工具，但这些脚本需要使用 GMAT MATLAB 接口。这些脚本是为配合 GPS_PosVec 滤波/平滑教程脚本使用而构建的，目前仅适用于 GPS_PosVec 数据类型。

`navigation` 子目录还包含将 CCSDS 跟踪数据消息（TDM）、深空网 TRK-2-34 和通用跟踪数据格式（UTDF）二进制文件转换为 GMAT GMD 格式的脚本。目前，这些脚本只转换一小部分数据类型，仅作为示例，不用于通用或业务用途。