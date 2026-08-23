# 第1章 仓库全景与构建系统

本章范围：仓库根目录全部文件（`CMakeLists.txt`、`README.txt`、`License.txt`、`.gitignore`、`.gitmodules`、`.gitbugtraq`、`LinuxPrefs.epf`，共 7 个）以及 `depends/`（12 文件）、`ThirdParty/`（1 文件）、`build/`（23 文件）、`Metrics/`（3 文件）、`moredata/`（184 文件）五个目录，合计 **230 个文件**。本章只讲构建与仓库顶层组织，不涉及 `src/`、`plugins/`、`application/` 等业务源码目录（另见各章）。

## 一、本章目录树

```
L:\gmat888
├── CMakeLists.txt            # 顶级 CMake 构建脚本（586 行，本章核心）
├── README.txt                # 根目录说明（仅 9 行，指向 application/README.txt）
├── License.txt               # Apache License 2.0 全文（176 行）
├── .gitignore                # Git 忽略规则（72 行）
├── .gitmodules               # Git 子模块声明（0 字节，空文件）
├── .gitbugtraq               # BugTraq/JIRA 集成配置（3 行）
├── LinuxPrefs.epf            # Eclipse CDT 工作区偏好导出（351 行）
├── depends/                  # 第三方依赖获取与构建（12 文件）
│   ├── CMakeLists.txt
│   ├── configure.py          # 依赖下载/编译总控脚本（571 行）
│   ├── .gitignore
│   ├── CMakeModules/GmatBoostConfig.cmake
│   └── bin/                  # 7za 解压器、f2c、python、xerces 辅助
├── ThirdParty/               # 预打包第三方依赖（1 文件）
│   └── Gmat3rdPartyLinux64.tar.gz
├── build/                    # 构建/安装/打包脚本（23 文件）
│   ├── .gitignore
│   ├── BuildSystem/windows-32/    # 旧式 Windows 每日构建脚本
│   ├── cmake_modules/             # 自定义 Find/Gmat 模块
│   └── install/                   # install 规则 + NSIS/WiX/mac 打包
├── Metrics/                  # 代码度量报告（SLOCCount 输出，3 文件）
│   └── R2018a/*.txt
└── moredata/                 # 图形/图标/地球定向数据素材（184 文件）
    ├── graphics/             # Logo、图标、外联物料、启动页、模板
    ├── iau_sofa/             # IAU_SOFA.DAT 地球定向参数
    ├── icondeliveries/       # 图标交付集（zip + 解包 PNG）
    └── sourceforge/          # SourceForge 页面说明
```

> 说明：根目录还有 `.git/`、`api-interop/`、`application/`、`doc/`、`plugins/`、`prototype/`、`src/`、`swig/` 等目录，均不在本章范围（分别由其他章节负责）。

## 二、逐文件/逐类讲解

### 2.1 根目录文件

#### 2.1.1 `CMakeLists.txt`（本章核心，逐段解读）

职责一句话：GMAT 的顶级 CMake 脚本，负责声明项目与版本、平台分支、查找全部第三方依赖、以 `add_subdirectory` 串联 `depends/`、`src/`、`swig/`、`plugins/`、`build/install/` 五层，并统一定义编译宏、输出目录与安装规则。

**（1）文件头与最低版本**（`CMakeLists.txt:1-24`）

```cmake
# $Id$
# GMAT: General Mission Analysis Tool.
# CMAKE script file for GMAT Project
# This file must be installed in the main GMAT directory.
# That is, we should have the directory structure:
#   ./src
#   ./plugins
#   ./depends
#   ./application
#   etc...
include(CheckCXXCompilerFlag)
CMAKE_MINIMUM_REQUIRED(VERSION 3.19.0)
```

- 第 7-12 行注释明确约定本文件必须位于 GMAT 主目录，且依赖 `./src`、`./plugins`、`./depends`、`./application` 的固定布局。
- 第 21 行 `include(CheckCXXCompilerFlag)` 引入编译器特性探测模块，后续第 447 行用它探测 `-fPIC`。
- 第 24 行要求 CMake ≥ 3.19.0，是整个构建链的最低版本门槛。

**（2）平台分支：macOS 与 Linux 预处理**（`CMakeLists.txt:26-38`）

```cmake
IF(APPLE)
  SET(CMAKE_OSX_DEPLOYMENT_TARGET 14.5 CACHE STRING ...)
  # [GMT-8340] Enable universal binary support on macOS
  SET(CMAKE_OSX_ARCHITECTURES "arm64;x86_64" CACHE STRING ...)
ENDIF()
IF(UNIX AND NOT APPLE)
   include(CheckCXXCompilerFlag)
ENDIF()
```

- 第 27-33 行：macOS 上把部署目标锁到 14.5，并通过 `CMAKE_OSX_ARCHITECTURES="arm64;x86_64"` 开启通用二进制（Apple Silicon + Intel），对应工单 GMT-8340。
- 第 36-38 行：Linux（`UNIX AND NOT APPLE`）单独引入编译器探测。GMAT 的"三平台分支"实际写法是 `WIN32`、`APPLE`、`UNIX AND NOT APPLE`，而非显式 `LINUX` 变量。

**（3）项目与版本声明**（`CMakeLists.txt:40-53`）

```cmake
PROJECT(GMAT C CXX)
SET(GMAT_RELEASE_NAME "R2026a" CACHE STRING "GMAT version name")
SET(GMAT_VERSION ${GMAT_RELEASE_NAME})
SET_PROPERTY(GLOBAL PROPERTY USE_FOLDERS ON)
SET(GMAT_WXWIDGETS_VERSION "3.2.9" CACHE STRING "GMAT wx version name")
SET(CMAKE_CXX_STANDARD 17 CACHE STRING "C++ Standard used for the build. C++17 is preferred")
SET_PROPERTY(CACHE CMAKE_CXX_STANDARD PROPERTY STRINGS 17 14 11)
SET(CMAKE_CXX_STANDARD_REQUIRED ON)
SET(CMAKE_CXX_EXTENSIONS OFF)
```

- 第 41 行声明项目为 `GMAT`，语言 `C CXX`（纯 C/C++ 工程）。
- 第 42-43 行：发行名 `R2026a` 同时作为 `GMAT_VERSION`，版本号是全局唯一的缓存变量。
- 第 44 行开启 IDE 目录折叠，配合第 533-547 行的 `_ADDSOURCEGROUPS` 宏。
- 第 46 行把 wxWidgets 版本固化为 `3.2.9`（与 `depends/configure.py` 第 13 行一致）。
- 第 50-53 行强制 C++17（首选，下拉可选 17/14/11），并关闭编译器扩展以保证可移植性。

**（4）架构探测与默认构建类型/安装前缀**（`CMakeLists.txt:55-95`）

```cmake
SET(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/build/cmake_modules")
if(CMAKE_CL_64 OR (CMAKE_SIZEOF_VOID_P EQUAL 8))
  SET(GMAT_64_BIT ON)
...
if(NOT CMAKE_CONFIGURATION_TYPES AND NOT CMAKE_BUILD_TYPE)
  SET(CMAKE_BUILD_TYPE Release ... FORCE)
endif()
...
SET(CMAKE_INSTALL_PREFIX "${PROJECT_SOURCE_DIR}/GMAT-${GMAT_RELEASE_NAME}-${CMAKE_SYSTEM_NAME}-${GMAT_RELEASE_TYPE}" ...)
```

- 第 56 行把自定义 CMake 模块搜索路径指向 `build/cmake_modules`（`GmatSwigConfig.cmake` 就放在那里）。
- 第 59-65 行用 `CMAKE_CL_64` 或 `CMAKE_SIZEOF_VOID_P` 判定 32/64 位，设置 `GMAT_64_BIT`。
- 第 71-73 行：单配置生成器（make）默认 `Release`。
- 第 77-85 行：默认安装前缀形如 `GMAT-R2026a-Windows-x64` / `...-x86`，可被 `-DCMAKE_INSTALL_PREFIX` 覆盖。
- 第 89-95 行：macOS 上按 Debug/Release 计算 `.app` 包路径 `GMATd-..._Beta.app` / `GMAT-..._Beta.app`。

**（5）Linux 专属链接/消毒器选项**（`CMakeLists.txt:97-112`）

```cmake
IF(UNIX AND NOT APPLE)
  SET(GMAT_RUN_ADDRESS_SANITIZER OFF CACHE BOOL "Check Memory using Address Sanitizer")
  SET_PROPERTY(GLOBAL PROPERTY FIND_LIBRARY_USE_LIB64_PATHS ON)
  SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,--no-undefined")
  IF (GMAT_RUN_ADDRESS_SANITIZER)
    SET(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fno-omit-frame-pointer -fsanitize=address")
    ...
  ENDIF()
ENDIF()
```

- 第 99 行提供 `GMAT_RUN_ADDRESS_SANITIZER` 开关，第 107-111 行在 Debug 下追加 ASan 编译/链接标志。
- 第 102 行让 `find_library` 搜索 lib64 路径（多用于红帽系发行版）。
- 第 106 行强制共享库未定义符号在链接期报错（macOS 默认开启、Linux 需手动加）。

**（6）组件开关选项（`OPTION` 系列）**（`CMakeLists.txt:114-128`）

```cmake
INCLUDE(CMakeDependentOption)

OPTION(GMAT_INCLUDE_GUI "Build the GMAT GUI" ON)
OPTION(GMAT_INCLUDE_CSALT "Build CSALT with GMAT" OFF)
CMAKE_DEPENDENT_OPTION(GMAT_INCLUDE_CSALT_TESTPROGRAM "..." OFF "GMAT_INCLUDE_CSALT" OFF)
CMAKE_DEPENDENT_OPTION(GMAT_INCLUDE_CSALT_INSTALL_SNOPT "..." ON "GMAT_INCLUDE_CSALT" OFF)
OPTION(GMAT_INCLUDE_API "Build the GMAT API" OFF)
CMAKE_DEPENDENT_OPTION(API_GENERATE_PYTHON "GMAT API for Python" ON "GMAT_INCLUDE_API" OFF)
CMAKE_DEPENDENT_OPTION(API_GENERATE_JAVA "GMAT API for Java" ON "GMAT_INCLUDE_API" OFF)
```

这是本章"cmake 参数表"的出处，也是 GMAT 组件化的总开关：

| 缓存变量 | 默认值 | 作用 |
| --- | --- | --- |
| `GMAT_INCLUDE_GUI` | ON | 是否构建 wxWidgets GUI（OFF 即纯控制台 + 插件） |
| `GMAT_INCLUDE_CSALT` | OFF | 是否构建 CSALT（轨迹优化子系统，需 SNOPT） |
| `GMAT_INCLUDE_CSALT_TESTPROGRAM` | OFF | 依赖 `GMAT_INCLUDE_CSALT`，构建 CSALT 测试程序 |
| `GMAT_INCLUDE_CSALT_INSTALL_SNOPT` | ON | 依赖 `GMAT_INCLUDE_CSALT`，安装 SNOPT 库 |
| `GMAT_INCLUDE_API` | OFF | 是否用 SWIG 生成对外 API |
| `API_GENERATE_PYTHON` | ON | 依赖 `GMAT_INCLUDE_API`，生成 Python 绑定 |
| `API_GENERATE_JAVA` | ON | 依赖 `GMAT_INCLUDE_API`，生成 Java 绑定 |

> 注意：任务中提到的 `GMAT_CONSOLE_ONLY` 选项在**本文件的 586 行中并不存在**。当前版本用 `GMAT_INCLUDE_GUI=OFF` 表达"只构建控制台/库"的意图；`GmatConsole` 可执行文件由 `src/console`（见第 3 章相关章节）无条件构建，GUI 则由 `GMAT_INCLUDE_GUI` 门控。另有 `GMAT_RUN_ADDRESS_SANITIZER`（第 99 行）、`GMAT_64_BIT`（第 60 行）、`GMAT_BUILDOUTPUT_DIRECTORY`（第 521 行）等衍生变量。

**（7）Boost 条件依赖**（`CMakeLists.txt:130-157`）

```cmake
if(APPLE AND (CMAKE_OSX_DEPLOYMENT_TARGET VERSION_LESS 10.15))
   SET(GMAT_USE_BOOST_VARIANT ON)
else()
   SET(GMAT_USE_BOOST_VARIANT OFF)
endif()
if(NOT ${CMAKE_CXX_STANDARD} MATCHES "17")
   SET(GMAT_USE_BOOST_VARIANT ON)
endif()
if (GMAT_USE_BOOST_VARIANT OR GMAT_INCLUDE_CSALT)
   SET(GMAT_USE_BOOST ON)
...
```

- `boost::variant` 在 macOS 10.15 前、或非 C++17 模式下被启用（用 Boost 版本替代 `std::variant`），据此决定 `GMAT_USE_BOOST`，最终驱动 `depends/CMakeModules/GmatBoostConfig.cmake` 是否下载 Boost。

**（8）依赖发现段（wxWidgets / CSPICE / F2C / Matlab / Python / Xerces / SWIG）**（`CMakeLists.txt:159-397`）

- 第 161 行 `ADD_SUBDIRECTORY(depends)` **先于**一切源码目录，保证第三方依赖就绪后再编译 GMAT。
- 第 166-197 行 wxWidgets：Windows 用 `wxWidgets_ROOT_DIR` 指向 `depends/wxWidgets/wxWidgets-3.2.9`；Mac/Linux 用 `wx-config`，先把 `depends/wxWidgets/.../cocoa-install|gtk-install/bin` 注入 `PATH`（第 189 行），再 `FIND_PACKAGE(wxWidgets COMPONENTS core base xml net richtext aui xrc qa html adv stc gl)`（第 196 行）。
- 第 200-249 行 CSPICE：按平台/位数拼出 `depends/cspice/{windows|macosx|linux}/cspice{32|64}`，用 `FIND_PATH(CSPICE_DIR NAMES include/SpiceUsr.h ...)` 定位（第 220-226 行），设置 `CSPICE_LIB`/`CSPICE_LIB_DEBUG`（第 238-240 行），找不到则 `MESSAGE(ERROR ...)` 终止（第 245 行），最后第 249 行 `ADD_DEFINITIONS("-D__USE_SPICE__")` 全局开启 SPICE 支持。
- 第 252-272 行 F2C：默认复用 CSPICE 的 include 目录，`FIND_PATH(F2C_DIR NAMES f2c.h ...)`，缺失仅警告。
- 第 275-309 行 Matlab：维护 `MATLAB_ADDITIONAL_VERSIONS` 版本表（第 277-292 行，R2016a=9.0 … R2021b=9.11），`FIND_PACKAGE(Matlab COMPONENTS MAIN_PROGRAM MX_LIBRARY ENG_LIBRARY MAT_LIBRARY)`；第 300-308 行在 macOS 上用 `lipo -info` 探测 Matlab 引擎库架构。
- 第 312-349 行 Python：支持 3.9–3.14（第 314 行），为每个次版本生成 `GMAT_PYTHON3X_ROOT_DIR` 缓存变量，并定义 `_REPORTPYTHONURL`（第 322 行）、`_SETPYTHONROOTDIR`（第 341 行）两个宏。
- 第 352-374 行 Xerces：按平台预置 `depends/xerces/{windows-install|cocoa-install|linux-install}` 路径后 `FIND_PACKAGE(XercesC REQUIRED)`（第 364 行，**强制依赖**），UNIX 下补 CoreFoundation/CoreServices/Threads。
- 第 377-397 行 SWIG：Windows 用预编译 `swigwin`，Linux 把 `swig` 提前加入 `PATH` 以避开系统旧版本，`FIND_PACKAGE(SWIG)`（第 396 行）。

**（9）CSALT/SNOPT 依赖**（`CMakeLists.txt:400-427`）

仅在 `GMAT_INCLUDE_CSALT` 开启时，在 `depends/snopt7` 下 `FIND_LIBRARY` 查找 `snopt7_cpp` 与 `snopt7`（第 410-411 行），缺任一即 `FATAL_ERROR`（第 423 行）。

**（10）通用编译标志与宏定义**（`CMakeLists.txt:430-498`）

```cmake
if(WIN32)
  SET (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -W2")
endif()
if(MSVC)
  SET (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /MP")
endif()
if(UNIX)
  SET (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-strict-aliasing")
endif()
...
ADD_DEFINITIONS(-DNO_GCC_PRAGMA)
ADD_DEFINITIONS(-DUNICODE -D_UNICODE)
...
SET(CMAKE_DEBUG_POSTFIX "d")
...
if(GMAT_64_BIT)
  ADD_DEFINITIONS("-DUSE_64_BIT_LONGS")
endif()
if(UNIX)
  ADD_DEFINITIONS("-DLINUX_MAC")
```

- 第 432-443 行：MSVC 开 `/MP` 并行编译，UNIX 统一 `-fno-strict-aliasing`；第 454-459 行按构建类型设 `-O3`/`-O0 -g`/`-O2 -g`。
- 第 462-463 行全局定义 `NO_GCC_PRAGMA`、`UNICODE`/`_UNICODE`；第 470 行 Debug 库统一加 `d` 后缀；第 480 行 64 位下定义 `USE_64_BIT_LONGS`；第 486 行 UNIX 统一定义 `LINUX_MAC`。
- 第 474-476 行 Windows 下压制 C4430/C4251/C4231/C4996 警告（其中 C4430 在 MatlabInterface 插件中会表现为错误）。

**（11）RPATH 与输出目录/源码分组宏**（`CMakeLists.txt:500-547`）

- 第 503-513 行：macOS 开 `CMAKE_MACOSX_RPATH`；Linux 用 `--enable-new-dtags` 把 RPATH 换成 RUNPATH，使搜索顺序"LD_LIBRARY_PATH 优先、RUNPATH 其次"，与 Mac/Windows 语义一致。
- 第 521 行定义 `GMAT_BUILDOUTPUT_DIRECTORY` 默认指向 `${PROJECT_SOURCE_DIR}/application`，第 523-530 行宏 `_SETOUTPUTDIRECTORY` 把各 target 的 Debug/Release 产物分别落盘到 `application/{bin,plugins,lib}` 与 `application/debug/...`，让开发者免安装即可运行。
- 第 535-547 行宏 `_ADDSOURCEGROUPS` 为 VS/Xcode 生成 Source/Header 分组树。

**（12）目录串联与收尾**（`CMakeLists.txt:549-586`）

```cmake
INCLUDE(build/install/CMake_INSTALL_Setup.cmake)
ADD_SUBDIRECTORY(src)
if(GMAT_INCLUDE_API)
  if(API_GENERATE_JAVA)
    ...
    ADD_SUBDIRECTORY(swig "swig/java")
  endif()
  if(API_GENERATE_PYTHON)
    ...
    foreach(GMATAPI_Python3_Version ${GMAT_PYTHON3_VERSIONS})
      ADD_SUBDIRECTORY(swig "swig/py${GMATAPI_Python3_Version}")
    endforeach()
  endif()
endif()
ADD_SUBDIRECTORY(plugins)
ADD_SUBDIRECTORY(build/install)
```

这是整个构建的**串联骨架**，顺序为：
1. 第 551 行先 include 安装目录结构脚本（定义 install 规则）；
2. 第 555 行 `src`（基础库 base/gmatutil/console/gui 等）；
3. 第 557-578 行 `swig` 仅在 `GMAT_INCLUDE_API` 时进入，且 Java 建一次、Python 按每个支持的版本各建一次二进制目录（`swig/py3.9`…`swig/py3.14`）；
4. 第 582 行 `plugins`（业务插件层）；
5. 第 586 行 `build/install`（把 install 规则作为最后一个子目录加入）。

#### 2.1.2 `README.txt`

职责一句话：根目录级说明的**指针文件**，共 9 行（`README.txt:1-9`）。

- 第 6-8 行明确：安装/配置、源码构建、运行、许可证细节和有用资源都写在 `/application/` 目录下的主 README 里。
- 因此"构建说明"的正文并不在本章范围的根 `README.txt` 中，而是位于 `application/README.txt`（超出本章范围，见应用层章节）。本章的构建参数事实一律以 `CMakeLists.txt` 与 `depends/configure.py` 为准。

#### 2.1.3 `License.txt`

职责一句话：GMAT 的许可证全文，共 176 行。

- 第 1-3 行即标明这是 **Apache License 2.0**（2004 年 1 月版），**不是**任务假设中的"NASA Open Source Agreement（NOSA）"。这说明本仓库版本已完成从 NOSA 到 Apache-2.0 的切换；`LinuxPrefs.epf` 第 226 行附近内嵌的源文件头模板同样引用 "Licensed under the Apache License, Version 2.0"，可交叉印证。
- 要点概述（中文）：第 2 条授予永久、全球、免费、免版税、不可撤销的版权许可（可复制、改作、再分发）；第 3 条授予专利许可，但若你以专利诉讼主张该作品侵权，专利许可即终止；第 4 条规定再分发必须附带本许可证、标记改动、保留版权声明与 NOTICE；第 5 条默认贡献以 Apache-2.0 提交；第 6 条不授予商标使用权；第 7、8 条为"按现状"免责与责任限制。

#### 2.1.4 `.gitignore`

职责一句话：Git 忽略规则，共 72 行，屏蔽构建产物、IDE 元数据与敏感数据。

- 第 2-13 行忽略编译产物（`.o/.obj/.dylib/.so/.dll/.exe/.app/.ilk/.pdb/.jar/.pyd/.tar.gz`）。
- 第 14-15、22-24、30、35 行忽略 Eclipse 元数据（`.project/.cproject/.settings/.metadata/.pydevproject`）与 `KARI/` 合作目录。
- 第 46 行忽略 `depends/boost*`，第 55 行忽略根 `build/` 目录，第 56-57 行忽略已下载的 CSPICE Windows 库（这些目录由 `configure.py` 现场生成，不入库）。
- 第 61-70 行忽略若干样例/输出文件（SAASample、SAA 滤波结果等），第 71-72 行忽略 `.clang-format`、`.clangd`。

#### 2.1.5 `.gitmodules`

职责一句话：Git 子模块清单——**本克隆中为空文件（0 字节）**。

- 这与任务假设"`.gitmodules` 揭示第三方子模块"不符：本 depth-1 克隆的 `.gitmodules` 没有任何 `[submodule "..."]` 条目。
- 结论：GMAT **不通过 git submodule 管理第三方依赖**。外部依赖的获取渠道是（a）`depends/configure.py` 现场 curl 下载 + 编译，（b）CMake `FetchContent`（Boost），（c）`ThirdParty/` 目录的预打包 tarball。

#### 2.1.6 `.gitbugtraq`

职责一句话：Git 客户端（TortoiseGit 等）的 BugTraq 集成配置，共 3 行（`.gitbugtraq:1-3`）。

- 第 1-2 行把问题追踪器指向 JIRA：`https://gmat.atlassian.net/browse/GMT-%BUGID%`，提交信息里的 `GMT-1234` 会被渲染成可点击链接。
- 第 3 行 `logRegex = GMT-(\\d+)` 定义从提交日志提取工单号的正则。该配置解释了仓库内大量 `[GMT-8340]`、`[GMT-6892]` 这类注释的来源。

#### 2.1.7 `LinuxPrefs.epf`

职责一句话：Eclipse CDT 工作区偏好导出文件（351 行，约 68 KB），是遗留的 IDE 配置快照而非构建必需项。

- 第 1 行时间戳 `Wed Sep 18 17:17:01 MST 2013` 表明这是 2013 年的导出，属于历史遗留。
- 主体是 `org.eclipse.cdt.core.formatter.*` 代码风格设置（空格/缩进/大括号位置，如第 37 行 `lineSplit=80`、第 38 行 `tabulation.size=3`），以及 Codan 静态检查的严重级别（第 44 行 `noreturn=Error`、第 222 行 `InvalidTemplateArgumentsProblem=Error`）。
- 第 68 行 `formatter_profile=_ThinkSys` 说明采用名为 `ThinkSys` 的格式化配置（第 332 行有同名 profile 定义）。
- 第 226 行内嵌 C/C++ 文件头模板，含 NASA/GSFC 与 Thinking Systems 联合开发的版权说明及 Apache-2.0 许可头，与 `License.txt` 相互印证。
- 现代 CMake 构建流程**不读取**此文件，仅作为历史 IDE 配置归档。

### 2.2 `depends/` 目录（12 文件）

#### 2.2.1 `depends/CMakeLists.txt`

职责一句话：依赖层的 CMake 入口，共 19 行，本身几乎不含逻辑。

```cmake
SET(GMAT_DEP_BUILD_DIR "${CMAKE_CURRENT_SOURCE_DIR}/build")
INCLUDE(CMakeModules/GmatBoostConfig.cmake)
```

- 第 13 行定义依赖中间产物目录 `depends/build`。
- 第 19 行只 include 了 `GmatBoostConfig.cmake`——因为 Boost 是唯一在 CMake 配置期动态下载的依赖；其余依赖（Xerces/wxWidgets/CSPICE/SWIG/JDK）由 `configure.py` 在 CMake **之前**准备好，再由顶级 `CMakeLists.txt` 用 `FIND_PACKAGE`/`FIND_PATH` 定位。

#### 2.2.2 `depends/configure.py`（依赖获取总控）

职责一句话：跨平台下载并编译 GMAT 全部第三方依赖的 Python 脚本（571 行），是"离线仓库 → 可构建树"的关键一环。

**（1）版本与路径常量**（`configure.py:1-38`）

```python
cspice_version = 'N0067'
swig_version = '4.4.1'
pcre_version = '10.47'
java_version = '11.0.5'
java_update = '10'
wx_build = True
wx_version = '3.2.9'
xerces_version = '3.2.2'
osx_min_version = '14.5'
...
gmat_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
depends_path = gmat_path + '/depends'
```

- 第 7-15 行集中声明各依赖版本：CSPICE N0067、SWIG 4.4.1、PCRE2 10.47、OpenJDK 11.0.5+10、wxWidgets 3.2.9、Xerces-C 3.2.2、macOS 最低版本 14.5。
- 第 25-26 行通过脚本自身位置反推 GMAT 根目录与 `depends/` 路径，脚本必须放在 `depends/` 下。
- 第 30-38 行定义各依赖落点：`depends/{bin,f2c,cspice,swig,java,wxWidgets,xerces,sofa,tsPlot}`。
- 第 40-48 行按 `sys.platform`（darwin/win32/其他）把 cspice、java 子目录进一步分平台。

**（2）Windows 工具链探测**（`configure.py:58-115`）

- `setup_windows()`（第 59 行）定位 Visual Studio（默认 `vs_version = 2022`、`vs_major_version = '17'`、`vc_major_version = '14'`、`vc_minor_version = '1'`，即 VS2022/VC14.1），自动选择 Enterprise/Professional/Community/WDExpress 版本，执行 `vcvarsall.bat x86_amd64` 并把环境变量灌回 Python（第 93-112 行）。

**（3）下载函数 `download_depends()`**（`configure.py:117-255`）

- 第 120-132 行：若 `depends/xerces` 不存在，从 `archive.apache.org` 下载 `xerces-c-3.2.2.tar.gz` 解压并改名。
- 第 135-152 行：下载 wxWidgets 源码（`github.com/wxWidgets/wxWidgets` 的 v3.2.9 tarball）。
- 第 154-191 行：下载 CSPICE。macOS 上区分 Intel（`MacIntel_OSX_AppleC`）与 Apple Silicon（`MacM1_OSX_clang`，第 160-165 行）；按 `struct.calcsize("P")*8` 判定 32/64 位（第 171-176 行）；Windows 用 `depends/bin/7za/7za.exe` 解压（第 182 行），Mac/Linux 用 `gzip/tar`（第 187-190 行）。
- 第 193-217 行：下载 SWIG（Windows 用预编译 `swigwin-4.4.1.zip`，Mac/Linux 用源码包）；第 219-222 行下载 PCRE2 到 SWIG 目录（注释 GMT-6892）。
- 第 224-255 行：下载 AdoptOpenJDK 11（`OpenJDK11U-jdk_x64_<os>_hotspot_11.0.5_10`），仅用于构建 Java API。

**（4）构建函数**（`configure.py:258-553`）

- `build_xerces()`（第 258 行）：Windows 用 `cmake -G "Visual Studio 17 2022" ... -DBUILD_SHARED_LIBS:BOOL=OFF -Dtranscoder=windows`（第 270 行）静态构建 Debug/Release；Mac/Linux 走 autotools `../configure --disable-shared --disable-netaccessor-curl ...`（第 313 行），并分别编译 debug（`-O0 -g`）与 release（`-O2`）两套静态库（第 316、329 行），release 库装完后重命名 debug 库为 `libxerces-cd.a`（第 322 行）。
- `build_wxWidgets()`（第 341 行）：Windows 用 `nmake -f makefile.vc ... SHARED=1 BUILD=debug|release`（第 365-368 行）；Mac/Linux 用 `../configure --enable-unicode --with-opengl`（第 420 行），macOS 额外 `--enable-universal_binary=x86_64,arm64 --with-osx_cocoa`（第 416 行）。
- `build_cspice()`（第 433 行）：Windows 用 `cl /c ... *.c` + `link -lib /out:cspice.lib`（第 452-453 行）；Mac/Linux 设 `TKCOMPILEOPTIONS` 后跑 `./mkprodct.csh`（第 492-493 行），带 `-DUIOLEN_int` 以整数 uiolen 编译（注释 GMT-5044）。
- `build_swig()`（第 508 行）：仅 Mac/Linux 需要，先跑 SWIG 自带的 `pcre-build.sh`（第 536 行），再 `configure && make && make install`。

**（5）主流程**（`configure.py:555-571`）

```python
if sys.platform == 'win32':
    setup_windows()
download_depends()
build_xerces()
if wx_build:
    build_wxWidgets()
build_cspice()
build_swig()
```

- 顺序固定：Windows 先导环境 → 统一下载 → Xerces → wxWidgets → CSPICE → SWIG。每个步骤通过"探测产物文件是否存在"实现幂等（如第 293 行查 `libxerces-c.a`、第 405 行查 `wx-config`、第 449 行查 `cspiced.lib`），重复运行只补缺失项。

#### 2.2.3 `depends/CMakeModules/GmatBoostConfig.cmake`

职责一句话：按需用 CMake `FetchContent` 下载 Boost 的模块，共 60 行。

```cmake
IF(NOT GMAT_USE_BOOST)
  RETURN()
ENDIF()
INCLUDE(FetchContent)
SET(Boost_VERSION 1.71.0)
...
FetchContent_Populate(boost
  URL https://archives.boost.io/release/${Boost_VERSION}/source/boost_${Boost_SUFFIX}.tar.bz2
  SOURCE_DIR ${BOOST_ROOT}
  BINARY_DIR ${GMAT_DEP_BUILD_DIR}/boost
  ...
)
...
FIND_PACKAGE(Boost ${Boost_VERSION} EXACT REQUIRED)
```

- 第 15-17 行：`GMAT_USE_BOOST` 为假时直接返回（Boost 可选）。
- 第 25 行默认 Boost 1.71.0，第 26-29 行允许 `Boost_VERSION_OVERRIDE` 覆盖。
- 第 33 行把 `1.71.0` 转成 `1_71_0` 后缀拼 URL。
- 第 43-50 行 `FetchContent_Populate` 下载 `.tar.bz2`（注释说明 `.7z` 在 1.71.0 解压有问题）。
- 第 56-59 行关闭 debug/release 库搜索、禁止系统路径——GMAT **只用 Boost 头文件**，不链接 Boost 库。

#### 2.2.4 `depends/.gitignore`

职责一句话：忽略由 `configure.py` 现场生成的依赖目录，共 9 行（`depends/.gitignore:1-9`）。

- 忽略 `/cspice`、`/swig`、`/java`、`/wxWidgets`、`/xerces`、`/logs`、`/snopt*`、`/Boost*`、`/build`，与 `configure.py` 的下载落点一一对应；这解释了为何 `depends/` 在仓库里只有 12 个文件而运行时却会膨胀出多个子目录。

#### 2.2.5 `depends/bin/` 辅助工具（4 个子目录）

- `bin/7za/`：内置 7-Zip 命令行版 `7za.exe`（版本 9.20，`readme.txt:1`）及其 `7-zip.chm` 手册、`license.txt`（LGPL v2.1，`license.txt:8`）、`readme.txt`。Windows 下 `configure.py` 用它解压 CSPICE/SWIG/JDK 的 zip（见 `configure.py:182,208,246`）。
- `bin/f2c/`：`f2c32.zip`、`f2c64.zip` 两个预编译 Fortran→C 转换器归档（二进制，仅列出用途）。注意顶级 `CMakeLists.txt:255` 实际默认复用 CSPICE 自带的 f2c，此目录是独立备用。
- `bin/xerces/XercesLibOverride.prop`：MSBuild 属性表，把 XercesLib 静态库的 `RuntimeLibrary` 从 `MultiThreaded` 覆盖为 `MultiThreadedDLL`（第 15、20、26、31 行），解决 Xerces 默认静态运行时与 GMAT 的 DLL 运行时不匹配导致的链接错误（文件头注释第 3-8 行详述缘由）。
- `bin/python/.gitignore`：仅 1 行 `*.txt`，用于屏蔽该占位目录下的文本文件。

### 2.3 `ThirdParty/` 目录（1 文件）

职责一句话：预打包的 Linux 第三方依赖压缩包，1 个文件 `ThirdParty/Gmat3rdPartyLinux64.tar.gz`（二进制归档，仅列表说明）。

- 从命名可判断是面向 Linux x64 的第三方依赖打包（配合早期基于预编译 tarball 的构建方式），与 `configure.py` 的"现场下载"路线并存，属历史遗留分发物。
- 由于是二进制归档，本章只登记用途，不展开分析（符合规范对二进制文件的处理）。

### 2.4 `build/` 目录（23 文件）

职责一句话：构建辅助与安装/打包脚本集合，分三个子目录——`install/`（正式安装规则与各平台打包）、`cmake_modules/`（自定义 CMake 模块）、`BuildSystem/`（旧式每日构建脚本）。

#### 2.4.1 `build/.gitignore`

职责一句话：忽略 `build/` 下的 `/Linux*` 与 `/windows-cmakebuild/`（`build/.gitignore:1-2`）。

#### 2.4.2 `build/install/`（安装与打包，16 文件）

**（1）`CMake_INSTALL_Setup.cmake`**（112 行）——安装目录结构主规则：

- 第 29-38 行把 `GMAT_BUILDOUTPUT_DIRECTORY`（默认 `application/`）整体 `INSTALL(DIRECTORY ...)` 到 `CMAKE_INSTALL_PREFIX`，但排除 `.*`、`debug`、`bin`、`plugins`、`lib`、`data/atmosphere/Msise86_Data`（后几个目录另有专门规则处理）。
- 第 41-54 行按平台/构建类型安装 `gmat_startup_file.txt`（UNIX 用 `_mac_linux` 变体并改名），Debug 用 `_debuginstall` 变体。
- 第 63-74 行安装 `GMAT.ini`（Release/Debug 各自版本）。
- 第 76-104 行条件安装 Java/Python API 支持文件（`load_gmat.m`、`gmatpy/__init__.py`）。
- 第 106-112 行 macOS 额外安装 `MacConfigure.txt`。

**（2）`install/CMakeLists.txt`**（104 行）——wxWidgets 库安装规则：

- 第 22-38 行 Windows：按 `*u_*.dll`（release）/`*ud_*.dll`（debug）后缀把 wx DLL 装到 `bin`，排除 `msw*`。
- 第 39-69 行 Mac/Linux：把 `libwx_*u[_-]*` 装到 `lib/` 或 app bundle 的 `Frameworks/`。
- 第 74-102 行 macOS 调用 `mac_change_install_names.sh` 修正 wx dylib 的 install name 与 GMAT 各组件的 RPATH（因 wxWidgets 默认用绝对路径 install name，不可移植）。

**（3）macOS 打包脚本（4 个）**：

- `mac_change_install_names.sh`（30 行）：用 `install_name_tool` 批量把 dylib 的 install name 从绝对路径改为 `@rpath`（第 11-30 行）。
- `mac_makeuniversalbinary.sh`（90 行）：用 `lipo -create` 把 Intel 与 Apple Silicon 两份 MatlabInterface 插件合并成通用二进制（第 79 行），配套 GMT-8560。
- `mac_notarizeGMAT.sh`（173 行）：打包 `.dmg` → 逐类 `codesign`（dylib/so/py/jnilib/jar/可执行文件）→ `hdiutil create` → `xcrun notarytool submit` → `stapler staple` 完成苹果公证；第 73 行硬编码 NASA 的签名身份 `Developer ID Application: NASA (82A95CK2HC)`。
- `mac_GMAT.entitlements`（10 行）：签名授权文件，允许 `allow-dyld-environment-variables` 与 `disable-library-validation`（第 5-8 行），供插件动态加载。

**（4）`windows-nsis/`（8 文件）**——Windows NSIS 安装器与 zip 包构建：

- `README.txt`（53 行）：说明这是当前活跃的安装器方案（基于 NSIS），并指明 MSI/WiX 是长期目标（第 1-3 行）。
- `Makefile`（91 行）：`VERSION = dev`（第 6 行）为版本变量；`all` 同时产 internal/public 的 `.exe` 与 `.zip`（第 12 行）；`installer-internal/public`（第 39、53 行）先跑 `genfilelists.sh` 再用 `makensis /DVERSION=... [/DPUBLIC]` 生成安装器，并用 `sed` 注释掉 `libMatlabInterface`、`libFminconOptimizer` 插件（第 43-46、57-60 行）；`zip-internal/public`（第 69-71 行）调 `zip -r9`。
- `assemblegmat.sh`（93 行）：从 `//mesa-file.gsfc.nasa.gov/595/GMAT/.../LatestCompleteVersion` 网络共享抓取最新构建（第 46-47 行），按 `-t public|public-release|full|full-release` 过滤专有插件与 Mars-GRAM 数据（第 77-90 行）。
- `genfilelists.sh`（30 行）：`find` 目标目录生成 `uninstall.nsh`（Delete/RMDir 语句），供 NSIS 卸载段使用。
- `gmat.nsi`（213 行）：NSIS 安装脚本，含多用户模式（第 23-27 行 `MULTIUSER_INSTALLMODE_INSTALLDIR "GMAT\${VERSION}"`）、开始菜单快捷方式、卸载注册表（第 85-108 行）与"启用 MATLAB 接口"可选段（第 113-117 行）。
- `addcovers.sh`（17 行）/`CreateInstall.bat`（59 行）：前者用 sejda-console 给用户手册 PDF 加封面；后者是完整打包流水线（`make clean → make assemble → sejda 合并 PDF → 删除专有 DLL → make VERSION=...`）。
- `WelcomeImage.bmp`：安装器欢迎页位图（二进制，仅列表）。

**（5）`windows-wix/`（2 文件）**——WiX/MSI 安装器（未完成）：

- `README.txt`（3 行）：明确标注"WiX 安装器是未完成的进行中工作，活跃安装器是 NSIS"。
- `gmat.wxs`（80 行）：WiX 源码，仅定义 `GMAT.exe` 一个组件与开始菜单/桌面快捷方式（第 30-47 行），`Version="0.9.0"`（第 11 行）可见其早期草稿状态。

#### 2.4.3 `build/cmake_modules/`（2 文件）

- `GmatSwigConfig.cmake`（297 行）：SWIG/API 绑定核心宏。定义 `_SETUPSWIG`（第 76 行）宏：按语言拼接 target 名（Java 加 `_java` 后缀、Python 加 `_py3X` 后缀，第 82-91 行）；设置 `CPLUSPLUS`、`-doxygen`/`-package;gmat` 的 SWIG 标志（第 103-108 行）；`SWIG_ADD_LIBRARY` 并链接 `GmatUtil GmatBase`（第 125-126 行）；Python 加链接 `Python3::Module`（第 129 行）；Java 生成 `.jar`、Python 复制 `.py`（第 154-197 行）；按平台设置 INSTALL_RPATH（第 208-232 行）与安装目录（第 235-295 行）。同时负责 JNI/Python3 的 `FIND_PACKAGE`（第 37、51 行）。
- `README_FindMatlab.txt`（12 行）：说明 CMake ≥ 3.3 起内置 `FindMatlab.cmake` 已重构，GMAT 不再自带该模块，故从本目录移除（历史说明文件）。

#### 2.4.4 `build/BuildSystem/windows-32/`（4 文件，旧式每日构建）

- `Makefile`（120 行）：针对 `C:/GMAT` 目录布局的每日构建/分发 Makefile，目标 `all`（cmake 生成 + `cmake --build ... -- //m //fl` + INSTALL，第 40-43 行）、`checkout`（git 拉取主仓库与内部插件、OpenFramesInterface，第 54-57 行）、`dist`（拷贝到网络共享的按日构建目录，第 60-99 行）、`devdocs`（doxygen，第 116-119 行）。
- `GmatBuild.cmd`（65 行）：Windows 批处理流水线，依次 `make clean → checkout → all → userdocs → devdocs → dist → dist-devdocs`，每步写独立日志（第 18-50 行）。
- `GmatBuildandSend.cmd`（12 行）：在 `GmatBuild.cmd` 前后用 `blat` 邮件通知 NASA 内部 SMTP（`ndc-relay.ndc.nasa.gov`，第 6 行）发送开始/结束报告。
- `start.txt`（1 行）：邮件正文模板"GMAT 64-bit Build has started…"。

> 说明：该子目录是面向 2013 年前后 MinGW/MSYS + VS2012 环境的旧式自动化脚本（`GmatBuild.cmd` 引用了 `VS120COMNTOOLS`），与现行 `depends/configure.py` + 顶级 CMake 流程并存，主要供 NASA 内部每日构建机使用。

### 2.5 `Metrics/` 目录（3 文件）

职责一句话：**SLOCCount 代码度量报告的输出**，并非度量脚本本身。

- 三个文件 `GmatSrcSlocCount.txt`、`GmatPluginsSlocCount.txt`、`GmatInternalPluginsSlocCount.txt` 均位于 `Metrics/R2018a/`，是 David A. Wheeler 的 `SLOCCount` 工具（GPL 许可）运行后的 stdout 存档（文件尾第 41-46 行有完整版权声明）。
- 关键结论（可直接引用的真实数字）：

| 文件 | 统计范围 | 总 SLOC | 主要语言占比 |
| --- | --- | --- | --- |
| `GmatSrcSlocCount.txt` | `src/`（base/gui/gmatutil/UnitTests/TestDrivers/console） | 380,161（第 33 行） | C++ 99.32% |
| `GmatPluginsSlocCount.txt` | `plugins/` 22 个插件 | 211,102（第 67 行） | C++ 43.14%、Fortran 32.46%、C 24.40% |
| `GmatInternalPluginsSlocCount.txt` | 内部插件（code/missionfiles/doc） | 219,391（第 27 行） | C 57.77%、Fortran 24.80%、C++ 15.61% |

- 每个文件还附 COCOMO 成本估算：如 `GmatSrcSlocCount.txt:34-39` 给出开发工作量 102.33 人年、约 1,382 万美元、预估 32.91 名开发者。`GmatPluginsSlocCount.txt:34` 显示 EstimationPlugin（17.2 万行）是体量最大的插件。这些数字可作第 2/3 章源码规模讨论的旁证。

### 2.6 `moredata/` 目录（184 文件）

职责一句话：GMAT 的**图形/图标/地球定向数据素材仓库**，不含源码，均为设计源文件、位图与数据文件。

- `graphics/`（42 文件）：`Logo/`（1 个 PSD 分层 Logo）、`icons/`（17 个 PSD，含 GMATMainIcon、AboutDialogImage、YouTube 系列等）、`outreach/`（4 个外联物料：DownloadCards.pptx、GMAT Flyer.zip、GMAT_Flyer_Final.pdf、Signboard.pdf）、`splash/`（19 个启动页 AI/PSD/TIF/PNG，含 R2022a 版）、`templates/`（1 个 GMAT_Template.pptx）。
- `iau_sofa/`（1 文件）：`IAU_SOFA.DAT`，地球定向参数（EOP）数据表，每行四列 `JD_UTC  x  y  UT1-UTC`（实测首行 `2436115.5  -842.15419404161 ...`），供 IAU/SOFA 天文算法做地球自转改正（UTC→UT1/TT 换算）。
- `icondeliveries/`（140 文件）：根目录 15 个交付包（`FirstSet.zip`、`IconSet3.zip`、`planets.zip` 等 zip 与 4 张 mockup 图、`IconTrackingSpreadsheet.xls` 追踪表）；`AllIcons/`（111 个 PNG，GUI 各类资源图标，如 Propagate/ImpulsiveBurn/CoordinateSystem 等）；`images3/`（14 个 PNG）。
- `sourceforge/`（1 文件）：`README.rst.txt`，SourceForge 项目页面的 reStructuredText 说明。

## 三、关键设计模式与数据流

### 3.1 依赖获取的两阶段模型

GMAT 把"第三方依赖"与"自身源码"解耦为**两阶段**：

1. **预构建阶段**（`depends/configure.py`）：curl 下载 Xerces/wxWidgets/CSPICE/SWIG/OpenJDK/PCRE2，并各自编译到 `depends/<name>/<platform>-install` 固定位置；Boost 则延后到 CMake 配置期由 `GmatBoostConfig.cmake` 的 `FetchContent` 下载。所有产物被 `depends/.gitignore` 屏蔽，仓库只保留"配方"而非"产物"。
2. **CMake 配置阶段**（顶级 `CMakeLists.txt`）：用 `FIND_PACKAGE`/`FIND_PATH` 到上述固定位置定位依赖，把绝对路径转成 `CSPICE_DIR`、`wxWidgets_ROOT_DIR`、`XercesC` 等变量，供下游 target 使用。

调用链：`configure.py`（离线准备）→ `cmake -S . -B build`（读顶级 `CMakeLists.txt`）→ `add_subdirectory(depends)` 拉取 Boost → `find_package` 定位其余依赖 → 编译 `src`/`plugins`/`swig`。

### 3.2 目录串联的分层拓扑

顶级 `CMakeLists.txt:161,555,557-578,582,586` 的 `add_subdirectory` 顺序体现了 GMAT 的**依赖分层**：

```
depends  →  src(基础库)  →  swig(API，可选)  →  plugins(插件)  →  build/install(安装)
```

下层先定义、上层再引用：`src` 产出 `GmatBase`/`GmatUtil` 等基础库；`swig` 的 `_SETUPSWIG` 宏链接 `GmatUtil GmatBase`（`GmatSwigConfig.cmake:126`）；`plugins` 再依赖基础库；最后的 `build/install` 统一收集所有 target 做安装。Boost 通过 `GMAT_USE_BOOST` 变量从顶层（第 148-157 行）传导到 depends 层，是跨目录配置下传的典型。

### 3.3 平台分支的统一模式

三平台（Windows/macOS/Linux）差异全部收口在**判断式 + 路径变量**里，而非分叉目录：

- `WIN32` / `APPLE` / `UNIX AND NOT APPLE` 三分支贯穿 `CMakeLists.txt`（第 27/36/98/169/203/355/383 行）与 `configure.py`（第 40/160/179/193/232 行）。
- 依赖路径按平台拼装：`depends/cspice/{windows|macosx|linux}/cspice{32|64}`（`CMakeLists.txt:204-216`）、`depends/xerces/{windows-install|cocoa-install|linux-install}`（`CMakeLists.txt:356-361`）。
- 统一宏定义让上层代码无需感知平台：`__USE_SPICE__`（第 249 行）、`LINUX_MAC`（第 486 行）、`USE_64_BIT_LONGS`（第 480 行）。

### 3.4 构建 → 安装 → 打包流水线

- **构建**：产物统一落 `application/`（`GMAT_BUILDOUTPUT_DIRECTORY`，第 521 行），Debug 版进 `application/debug/`，实现"免安装即运行"。
- **安装**：`build/install/CMake_INSTALL_Setup.cmake` 把 `application/` 内容按平台过滤后装到 `CMAKE_INSTALL_PREFIX`，`build/install/CMakeLists.txt` 补装 wxWidgets 运行库。
- **打包**：Windows 走 NSIS（`windows-nsis/Makefile` + `gmat.nsi` + `assemblegmat.sh` + `genfilelists.sh`）；macOS 走 `mac_notarizeGMAT.sh` 的 dmg + 签名 + 公证；旧式每日构建走 `BuildSystem/windows-32/` 的 Makefile/cmd 链。

## 四、文件清单附录

### 4.1 根目录（7 文件）

| 相对路径 | 职责 | 关键类/函数/内容 |
| --- | --- | --- |
| `CMakeLists.txt` | 顶级构建脚本：项目声明、依赖查找、目录串联、安装 | `PROJECT(GMAT C CXX)`、`OPTION(GMAT_INCLUDE_GUI/CSALT/API)`、`ADD_SUBDIRECTORY(depends/src/swig/plugins/build/install)`、`_SETOUTPUTDIRECTORY`、`_ADDSOURCEGROUPS` |
| `README.txt` | 根说明指针 | 指向 `application/README.txt`（第 6-8 行） |
| `License.txt` | 许可证全文 | Apache License 2.0（第 1-3 行） |
| `.gitignore` | Git 忽略规则 | 编译产物/IDE 元数据/`depends/boost*`/`/build` 等 |
| `.gitmodules` | Git 子模块清单 | 空文件（无任何 submodule） |
| `.gitbugtraq` | BugTraq/JIRA 集成 | `GMT-%BUGID%`、`logRegex=GMT-(\\d+)` |
| `LinuxPrefs.epf` | Eclipse CDT 偏好导出 | formatter/Codan 设置、`ThinkSys` profile、Apache-2.0 文件头模板 |

### 4.2 `depends/`（12 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `depends/CMakeLists.txt` | 依赖层 CMake 入口 | `INCLUDE(CMakeModules/GmatBoostConfig.cmake)` |
| `depends/configure.py` | 下载并编译全部第三方依赖 | `setup_windows()`、`download_depends()`、`build_xerces()`、`build_wxWidgets()`、`build_cspice()`、`build_swig()` |
| `depends/.gitignore` | 忽略现场生成的依赖目录 | `/cspice`、`/swig`、`/java`、`/wxWidgets`、`/xerces` 等 |
| `depends/CMakeModules/GmatBoostConfig.cmake` | CMake 期下载 Boost | `FetchContent_Populate(boost ...)`、`FIND_PACKAGE(Boost 1.71.0 EXACT REQUIRED)` |
| `depends/bin/7za/7za.exe` | 7-Zip 命令行解压器（二进制） | 供 Windows 解压 CSPICE/SWIG/JDK |
| `depends/bin/7za/7-zip.chm` | 7-Zip 手册（二进制） | — |
| `depends/bin/7za/license.txt` | 7za 许可证 | GNU LGPL v2.1 |
| `depends/bin/7za/readme.txt` | 7za 说明 | 7-Zip 9.20 特性与格式支持 |
| `depends/bin/f2c/f2c32.zip` | Fortran→C 转换器 32 位（二进制） | 备用 f2c |
| `depends/bin/f2c/f2c64.zip` | Fortran→C 转换器 64 位（二进制） | 备用 f2c |
| `depends/bin/python/.gitignore` | 占位目录忽略规则 | `*.txt` |
| `depends/bin/xerces/XercesLibOverride.prop` | 覆盖 XercesLib 运行时库类型 | `RuntimeLibrary=MultiThreadedDLL` |

### 4.3 `ThirdParty/`（1 文件）

| 相对路径 | 职责 | 关键内容 |
| --- | --- | --- |
| `ThirdParty/Gmat3rdPartyLinux64.tar.gz` | 预打包 Linux x64 第三方依赖（二进制归档） | 历史分发物 |

### 4.4 `build/`（23 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `build/.gitignore` | 忽略本目录临时产物 | `/Linux*`、`/windows-cmakebuild/` |
| `build/install/CMakeLists.txt` | wxWidgets 库安装规则 | `INSTALL(DIRECTORY ... PATTERN "libwx_*u[_-]*")` |
| `build/install/CMake_INSTALL_Setup.cmake` | 安装目录结构主规则 | `INSTALL(DIRECTORY GMAT_BUILDOUTPUT_DIRECTORY ...)`、startup file/GMAT.ini/API 支持文件安装 |
| `build/install/mac_change_install_names.sh` | 修正 macOS dylib install name | `install_name_tool -change ... -id @rpath/...` |
| `build/install/mac_GMAT.entitlements` | 代码签名授权 | `allow-dyld-environment-variables`、`disable-library-validation` |
| `build/install/mac_makeuniversalbinary.sh` | 合并 Intel+Silicon 通用二进制 | `lipo -create` |
| `build/install/mac_notarizeGMAT.sh` | macOS 打包/签名/公证 | `codesign`、`hdiutil create`、`xcrun notarytool submit`、`stapler staple` |
| `build/install/windows-nsis/addcovers.sh` | 给用户手册 PDF 加封面 | `sejda-console merge` |
| `build/install/windows-nsis/assemblegmat.sh` | 从网络共享组装发行文件 | `-t public/public-release/full/full-release` |
| `build/install/windows-nsis/CreateInstall.bat` | Windows 打包流水线 | `make assemble/clean/... VERSION=...` |
| `build/install/windows-nsis/genfilelists.sh` | 生成 NSIS 卸载文件清单 | `find ... → uninstall.nsh` |
| `build/install/windows-nsis/gmat.nsi` | NSIS 安装脚本 | `MULTIUSER_*`、`Section "!GMAT"`、卸载注册表 |
| `build/install/windows-nsis/Makefile` | NSIS/zip 构建 Makefile | `installer-internal/public`、`zip-internal/public` |
| `build/install/windows-nsis/README.txt` | NSIS 打包说明 | 前置条件与 make 目标 |
| `build/install/windows-nsis/WelcomeImage.bmp` | 安装器欢迎位图（二进制） | — |
| `build/install/windows-wix/gmat.wxs` | WiX/MSI 源码（未完成） | `<Product Name="GMAT" Version="0.9.0">` |
| `build/install/windows-wix/README.txt` | 说明 WiX 为进行中工作 | 指向 NSIS |
| `build/cmake_modules/GmatSwigConfig.cmake` | SWIG/API 绑定核心宏 | `_SETUPSWIG` 宏、`SWIG_ADD_LIBRARY`、JNI/Python3 查找 |
| `build/cmake_modules/README_FindMatlab.txt` | 说明移除自带 FindMatlab 的原因 | CMake ≥3.3 内置模块已足够 |
| `build/BuildSystem/windows-32/GmatBuild.cmd` | 旧式每日构建批处理 | `make clean/checkout/all/userdocs/devdocs/dist` |
| `build/BuildSystem/windows-32/GmatBuildandSend.cmd` | 构建 + blat 邮件通知 | `blat start.txt/results.txt` |
| `build/BuildSystem/windows-32/Makefile` | 旧式每日构建 Makefile | `all/clean/checkout/dist/devdocs` |
| `build/BuildSystem/windows-32/start.txt` | 构建开始邮件正文 | "GMAT 64-bit Build has started…" |

### 4.5 `Metrics/`（3 文件）

| 相对路径 | 职责 | 关键数据 |
| --- | --- | --- |
| `Metrics/R2018a/GmatSrcSlocCount.txt` | `src/` SLOC 报告 | 总 380,161 SLOC，C++ 99.32% |
| `Metrics/R2018a/GmatPluginsSlocCount.txt` | `plugins/` SLOC 报告 | 总 211,102 SLOC，EstimationPlugin 最大（172,881） |
| `Metrics/R2018a/GmatInternalPluginsSlocCount.txt` | 内部插件 SLOC 报告 | 总 219,391 SLOC，C 57.77% |

### 4.6 `moredata/`（184 文件，按目录分组）

| 相对路径 | 职责 | 文件数 | 代表性文件 |
| --- | --- | --- | --- |
| `moredata/graphics/Logo/` | Logo 分层设计源文件 | 1 | `GMAT Logo_2014_Layered.psd` |
| `moredata/graphics/icons/` | 图标 PSD 源文件 | 17 | `GMATMainIcon.psd`、`AboutDialogImage.psd` |
| `moredata/graphics/outreach/` | 外联物料 | 4 | `GMAT_Flyer_Final.pdf`、`DownloadCards.pptx` |
| `moredata/graphics/splash/` | 启动页设计源文件 | 19 | `GMAT_Splash_R2022a.png/.ai/.tif` |
| `moredata/graphics/templates/` | 演示模板 | 1 | `GMAT_Template.pptx` |
| `moredata/iau_sofa/` | 地球定向参数数据 | 1 | `IAU_SOFA.DAT` |
| `moredata/icondeliveries/` | 图标交付包（zip + mockup） | 15 | `IconSet3.zip`、`IconTrackingSpreadsheet.xls` |
| `moredata/icondeliveries/AllIcons/` | GUI 资源图标 PNG | 111 | `ImpulsiveBurn.png`、`CoordinateSystem.png` |
| `moredata/icondeliveries/images3/` | 图标 PNG 集 | 14 | `Propagator_a.png`、`Thruster.png` |
| `moredata/sourceforge/` | SourceForge 页面说明 | 1 | `README.rst.txt` |
