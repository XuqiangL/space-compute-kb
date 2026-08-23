# 启动文件（StartupFile）

> 译自 GMAT R2026a 帮助文档 StartupFile.html

**Startup File** —— `gmat_startup_file.txt` 配置文件。

## 描述

GMAT 启动文件（`gmat_startup_file.txt`）包含 GMAT 应用程序的基本配置设置，包括数据文件和插件的位置、用户自定义函数的搜索路径，以及控制执行的各种选项。

启动文件必须与 GMAT 可执行文件位于同一位置，且必须命名为 `gmat_startup_file.txt`。GMAT 在程序初始化时加载一次启动文件。

## 文件格式

### 基本语法

启动文件是包含 7 位 US-ASCII 字符集字符的文本文件，且区分大小写。

行由以下任意 ASCII 字符序列终止：

- 换行（十六进制：0A）
- 回车（十六进制：0D）
- 回车后跟换行（十六进制：0D0A）

空白可以出现在任何行的上方或下方，以及任何键或值的前后。以下字符被识别为空白：

- 空格（十六进制：20）
- 水平制表符（十六进制：09）

注释以井号（`#`）开头，且必须独占一行。不允许行内注释。

### 设置属性

属性通过键值对指定，语法如下：

`PROPERTY = VALUE`

属性是一个单词，不含空格。值从等号后的第一个非空白字符延伸到行尾。等号两侧都至少需要一个空白字符。

属性按以下约定命名：

- 接受目录路径的属性以 `_PATH` 结尾。
- 接受文件路径的属性以 `_FILE` 结尾。

重复属性条目的行为取决于各个属性。一般来说：

- 多个 `PLUGIN` 条目会使 GMAT 加载每个指定的插件。
- 多个相同的 `*_FUNCTION_PATH` 条目会把每个路径添加到搜索路径中，从第一个开始。
- 多个相同的 `*_FILE` 条目会被忽略，使用最后一个值。

### 访问属性值

任何以 "_PATH" 结尾的属性（包括自定义的）的值都可以被其他值引用。要引用某个值，把属性名包含在值中即可。重复的斜杠字符会被合并。例如：

```
ROOT_PATH = ../
OUTPUT_PATH = ROOT_PATH/output/
```

会把 `OUTPUT_PATH` 设置为 "`../output/`"。

### 文件路径

正斜杠和反斜杠可以互换使用，也可以在单条路径中混用。以下三条路径被视为相同：

```
data/planetary_ephem/spk/de421.bsp
data\planetary_ephem\spk\de421.bsp
data\planetary_ephem/spk\de421.bsp
```

绝对路径除对斜杠进行规范化外，按原样传递给底层操作系统。

相对路径相对于 GMAT 可执行文件的位置。

## 属性

可用属性如下所示，并酌情给出默认值。

### 系统

- `ROOT_PATH=../` —— GMAT 根目录的路径。

### 插件

- `PLUGIN` —— 插件库的路径，不含扩展名。允许多个 `PLUGIN` 属性，每个插件一个。

### 用户函数

- `GMAT_FUNCTION_PATH` —— GMAT 函数文件（`.gmf` 文件）的搜索路径。可多次出现以添加多个路径。
- `MATLAB_FUNCTION_PATH` —— MATLAB 函数文件（`.m` 文件）的搜索路径。可多次出现以添加多个路径。
- `PYTHON_MODULE_PATH` —— Python 模块的搜索路径。可多次出现以添加多个路径。

### 输出

- `LOG_FILE=OUTPUT_PATH/GmatLog.txt` —— 应用程序日志文件的路径。
- `MEASUREMENT_PATH=OUTPUT_PATH/` —— 仿真测量数据文件的路径。仅与 `libGmatEstimation` 插件一起使用。
- `OUTPUT_PATH=../output/` —— `ReportFile` 资源的输出目录路径。
- `SCREENSHOT_FILE=OUTPUT_PATH/OUTPUT_PATH` —— 屏幕截图的输出路径和基本文件名。基本文件名会追加 "`_###.png`"，其中 "`###`" 是从 `001` 开始的数字序列。如果缺少基本文件名，默认为 "`SCREEN_SHOT`"。
- `VEHICLE_EPHEM_PATH=OUTPUT_PATH/` —— `EphemerisFile` 资源的默认输出目录路径。

### 数据文件

注意：本节只讨论可通过启动文件设置的路径。关于定期更新的数据文件的内容及如何维护这些文件的讨论，请参阅"配置数据文件"（Configuring Data Files）。

- `CELESTIALBODY_POT_PATH=DATA_PATH/gravity/celestialbody/` —— `CELESTIALBODY` 的重力势文件搜索路径。`CELESTIALBODY` 是给定 GMAT 任务中定义的任何天体的名称。该属性对用户自定义天体没有默认值。
- `ATMOSPHERE_PATH` —— 包含大气模型数据的目录路径。
- `BODY_3D_MODEL_PATH` —— 包含 CelestialBody 3D 模型文件的目录路径。
- `CSSI_FLUX_FILE` —— 默认 CSSI 太阳通量文件的路径。
- `DATA_PATH=ROOT_PATH/data/` —— 包含数据文件的目录路径。
- `DE405_FILE=DE_PATH/leDE1941.405` —— DE405 DE 文件历表文件的路径。
- `DE421_FILE` —— DE421 DE 文件历表文件的路径。
- `DE424_FILE` —— DE424 DE 文件历表文件的路径。
- `EGM96_FILE=EARTH_POT_PATH/EGM96.cof` —— EGM-96 地球重力势文件的路径。
- `EOP_FILE` —— IERS "EOP 08 C04 (IAU1980)" 地球定向参数文件的路径。
- `ICRF_FILE` —— 计算 FK5 到 ICRF 旋转矩阵所需数据（`ICRF_Table.txt`）的路径。
- `JGM2_FILE=EARTH_POT_PATH/JGM2.cof` —— JGM-2 地球重力势文件的路径。
- `JGM3_FILE=EARTH_POT_PATH/JGM3.cof` —— JGM-3 地球重力势文件的路径。
- `LEAP_SECS_FILE=TIME_PATH/tai-utc.dat` —— 来自 http://maia.usno.navy.mil 的累积闰秒文件的路径。
- `LP165P_FILE=LUNA_POT_PATH/LP165P.cof` —— LP165P 月球重力势文件的路径。
- `LSK_FILE` —— SPICE 闰秒内核的路径。
- `MARINI_TROPO_FILE` —— 包含 Marini 对流层模型所需的特定位置大气数据的文件路径。
- `MARS50C_FILE=MARS_POT_PATH/Mars50c.cof` —— Mars50c 火星重力势文件的路径。
- `MGNP180U_FILE=VENUS_POT_PATH/MGNP180U.cof` —— MGNP180U 金星重力势文件的路径。
- `NUTATION_COEFF_FILE=PLANETARY_COEFF_PATH/NUTATION.DAT` —— FK5 归算的章动级数数据（`NUTATION.DAT`）的路径。
- `PLANETARY_COEFF_PATH=DATA_PATH/planetary_coeff/` —— 包含行星系数文件的目录路径。
- `PLANETARY_EPHEM_DE_PATH` —— 包含 DE 历表文件的目录路径。
- `PLANETARY_EPHEM_SPK_PATH` —— 包含 SPICE 行星历表文件的目录路径。
- `PLANETARY_PCK_FILE` —— 默认天体的 SPICE 行星常数内核的路径。
- `PLANETARY_SPK_FILE` —— 默认天体的 SPICE 历表内核的路径。
- `SCHATTEN_FILE` —— 默认 Schatten 太阳通量预测文件的路径。
- `SPACECRAFT_MODEL_FILE` —— 默认航天器 3D 模型文件。
- `SPAD_PATH` —— 包含 SPAD 数据文件的目录路径。
- `SPAD_SRP_FILE` —— 默认 SPAD SRP 模型的路径。
- `TIME_PATH=DATA_PATH/time/` —— 包含闰秒文件的目录路径。
- `VEHICLE_EPHEM_CCSDS_PATH` —— 包含航天器 CCSDS-OEM 历表文件的目录路径。
- `VEHICLE_EPHEM_SPK_PATH` —— 包含航天器 SPK 历表文件的目录路径。
- `VEHICLE_MODEL_PATH` —— 包含 3D 航天器模型的目录路径。

### 应用程序文件

- `CELESTIALBODY_TEXTURE_FILE=TEXTURE_PATH/DefaultTextureFile.jpg` —— CELESTIALBODY 的纹理文件路径。CELESTIALBODY 是 GMAT 中任何内置天体的名称，DefaultTextureFile 是为该天体定义的默认纹理文件。
- `BORDER_FILE` —— 星座边界星表的路径。
- `CONSTELLATION_FILE=STAR_PATH/inp_Constellation.txt` —— 星座星表的路径。
- `GUI_CONFIG_PATH=DATA_PATH/gui_config/` —— 包含 GUI 配置文件的目录路径。
- `HELP_PATH` —— 包含用户指南帮助文件的目录路径。
- `HELP_DIRECTORY_FILE` —— CHM 帮助文件的路径，用于通过 GMAT GUI 浏览用户指南内容。
- `HELP_HTML_FILE` —— HTML 帮助文件的路径，用于在浏览器中打开整个用户指南。
- `ICON_PATH=DATA_PATH/graphics/icons/` —— 包含应用程序图标的目录路径。
- `MAIN_ICON_FILE` —— GUI 图标的路径。
- `PERSONALIZATION_FILE=DATA_PATH/gui_config/MyGmat.ini` —— GUI 配置和历史文件的路径。
- `SPACECRAFT_MODEL_FILE=MODEL_PATH/aura.3ds` —— 默认 Spacecraft 3D 模型文件的路径。
- `SPLASH_FILE=SPLASH_PATH/GMATSplashScreen.tif` —— GUI 启动图像的路径。
- `SPLASH_PATH=DATA_PATH/graphics/splash/` —— 包含启动画面文件的目录路径。
- `STAR_FILE=STAR_PATH/inp_StarCatalog.txt` —— 星表的路径。
- `STAR_PATH=DATA_PATH/graphics/stars/` —— 包含恒星和星座星表的目录路径。
- `TEXTURE_PATH=DATA_PATH/graphics/texture/` —— 包含天体纹理文件的目录路径。

### 程序设置

- `MATLAB_APP_PATH` —— [仅 macOS] MATLAB 应用（`.app`）的路径。
- `MATLAB_MODE=SHARED` —— MATLAB 接口连接模式。可用选项：
  - `NO_MATLAB` —— 禁用 MATLAB 接口。
  - `SHARED` —— 每个 GMAT 实例共享单个 MATLAB 连接。默认。
  - `SINGLE` —— 每个 GMAT 实例使用自己的 MATLAB 连接。
- `WRITE_GMAT_KEYWORD=ON` —— 保存 GMAT 脚本文件时，在赋值行前写 "`GMAT `" 前缀。可接受的值为 `ON` 和 `OFF`。
- `WRITE_PERSONALIZATION_FILE=ON` —— 把窗口位置和其他本地配置设置写入 GMAT.ini 文件。设为 OFF 可避免多个 GMAT 实例同时写用户配置文件时遇到的系统错误。可接受的值为 `ON` 和 `OFF`。

### 调试设置

- `DEBUG_FILE_PATH=OFF` —— 调试文件路径处理。可接受的值为 `ON` 和 `OFF`。
- `DEBUG_MATLAB=OFF` —— 调试 MATLAB 接口连接。可接受的值为 `ON` 和 `OFF`。
- `DEBUG_PARAMETERS=OFF` —— 启动时把可用参数表写入日志文件。可接受的值为 `ON` 和 `OFF`。
- `HIDE_SAVEMISSION=TRUE` —— 在 GUI 中隐藏 `SaveMission` 命令。可接受的值为 `TRUE` 和 `FALSE`。
- `PLOT_MODE` —— `XYPlot` 窗口放置模式。唯一可接受的值是 `TILE`，它会使 GMAT 忽略绘图窗口放置字段并平铺窗口。
- `RUN_MODE` —— GMAT 执行模式。可用选项：
  - `EXIT_AFTER_RUN` —— 当 GMAT 以 `-r` 或 `--run` 命令行参数调用时，运行完成后自动退出。
  - `TESTING` —— 在 GUI 中显示测试选项。
  - `TESTING_NO_PLOTS` —— 与 `TESTING` 相同，但同时禁用 GUI 中的所有图形输出。
- `ECHO_COMMANDS` —— 命令执行时将其写入日志文件。可接受的值为 TRUE 和 `FALSE`。
- `NO_SPLASH` —— GMAT 启动时跳过显示启动画面。可接受的值为 TRUE 和 `FALSE`。