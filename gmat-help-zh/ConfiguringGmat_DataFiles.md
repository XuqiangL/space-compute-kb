# 配置数据文件（ConfiguringGmat_DataFiles）

> 译自 GMAT R2026a 帮助文档 ConfiguringGmat_DataFiles.html

GMAT 使用许多会定期更新的经验数据文件。在某些情况下，文件由其所属机构每三小时就更新一次。GMAT 随附一个 Python 脚本 `\utilities\python\GMATDataFileManager.py`，可自动完成文件更新、记录变更，并可选地归档 GMAT 所用数据文件的旧版本。详细使用说明请参阅该 Python 类中包含的帮助文档。下面介绍 GMAT 使用的经验数据文件，以及用哪些启动文件变量来定义这些文件在你系统上的位置。数据来源和备注说明了文件的获取位置和使用方式。

| 启动文件变量 | 数据来源 | 备注 |
| --- | --- | --- |
| EOP_FILE | ftp://hpiers.obspm.fr/iers/series/opa/eopc04_IAU2000/ | GMAT 天文动力学例程使用的 EOP 文件 |
| PLANETARY_PCK_FILE | https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/ | 包含定向、尺寸和形状数据的 SPICE 行星常数内核。自 R2017a 版本起为 pck00010.pck。版本可能变化，文件会检查新版本 |
| LEAP_SECS_FILE | https://maia.usno.navy.mil/ser7/tai-utc.dat | GMAT 天文动力学例程使用的闰秒文件 |
| LSK_FILE | https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/ | SPICE 天文动力学例程使用的闰秒文件。自 R2017a 版本起为 naif0012.tls。版本可能变化，文件会检查新版本 |
| CSSI_FLUX_FILE | ftp://ftp.agi.com/pub/DynamicEarthData/SpaceWeather-All-v1.2.txt | CSSI 空间天气文件，当传播器配置为使用 CSSI 文件作为空间天气建模来源时，用于阻力建模中的通量和地磁指数 |
| SCHATTEN_FILE | https://iswa.ccmc.gsfc.nasa.gov/iswa_data_tree/model/solar/FDF/SchattenSolarFluxPrediction/ | Schatten 文件目前不由数据文件管理器工具更新。用户可从数据来源手动下载。注意下载后必须按 GMAT 随附的 Schatten 数据文件所示添加 BEGIN_DATA 和 END_DATA 标记 |
| EARTH_LATEST_PCK_FILE | https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/earth_latest_high_prec.bpc | SPICE 天文动力学例程使用的 EOP 文件 |
| EARTH_PCK_PREDICTED_FILE | https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/ | 包含地球预测的岁差、章动、章动修正、UT1-TAI 和极移的 SPICE 内核。用于 SPICE 天文动力学例程 |
| EARTH_PCK_CURRENT_FILE | https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/ | 包含地球历史的岁差、章动、章动修正、UT1-TAI 和极移的 SPICE 内核。用于 SPICE 天文动力学例程 |
| LUNA_PCK_CURRENT_FILE | https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/ | 提供月球主轴（PA）参考架定向的内核。用于 SPICE 天文动力学例程 |
| LUNA_FRAME_KERNEL_FILE | https://naif.jpl.nasa.gov/pub/naif/generic_kernels/fk/satellites/ | 该参考架内核包含实现月球主轴（PA）和平均地球/极轴（ME）参考系的月球参考架最新规范。用于 SPICE 天文动力学例程 |

## 加载自定义插件

自定义插件通过在启动文件（`bin/gmat_startup_file.txt`）中添加一行来加载，该行指定插件文件的名称和位置。要使插件能与 GMAT 配合工作，插件库必须放在启动文件中引用的文件夹中。全部细节请参阅启动文件（Startup File）参考文档。

## 配置 MATLAB 接口

GMAT 包含一个 MATLAB 接口。请参阅 MATLAB Interface 参考文档来配置 MATLAB 接口。

## 配置 Python 接口

GMAT 包含一个 Python 接口。请参阅 Python Interface 参考文档来配置 Python 接口。

## 用户自定义函数路径

如果你创建了自定义 MATLAB 函数，可以提供这些文件的路径，GMAT 会在运行时定位它们。默认启动文件已配置为允许你把 MATLAB 函数（扩展名为 `.m`）放在 `userfunctions/matlab` 目录中，GMAT 会在运行时自动搜索该位置。你可以通过更改启动文件中的下面这些行来更改 MATLAB 函数的搜索路径位置（相对于 GMAT `bin` 文件夹）：

```
MATLAB_FUNCTION_PATH = ../userfunctions/matlab
```

如果你希望把自定义函数组织在多个文件夹中，可以向启动文件添加多个搜索路径。例如：

```
MATLAB_FUNCTION_PATH = ../MyFunctions/utils
MATLAB_FUNCTION_PATH = ../MyFunctions/StateConversion 
MATLAB_FUNCTION_PATH = ../MyFunctions/TimeConversion
```

GMAT 会按启动文件中指定的顺序搜索这些路径，并使用第一个名称匹配的函数。