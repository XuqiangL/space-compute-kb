# 第13章 插件体系（上）：接口、测量、估计与传播类插件

> 本章范围：`L:\gmat888\plugins\` 目录下的根共享文件（`CMakeLists.txt`、`CMakeLists_PluginTemplate.txt`）以及 13 个插件目录——`CInterfacePlugin`、`DataCallbackPlugin`、`DataInterfacePlugin`、`EphemPropagatorPlugin`、`EstimationPlugin`、`EventLocatorPlugin`、`ExtendedKalmanFilterPlugin`、`ExternalForceModelPlugin`、`ExtraPropagatorsPlugin`、`FminconOptimizerPlugin`、`FormationPlugin`、`GeometricMeasurementPlugin`、`GmatFunctionPlugin`。共 375 个 C/C++ 代码文件（`.hpp/.cpp/.c/.h`），另有 `.m/.script/.i/.swg/Doxyfile/CMakeLists.txt/.gitignore` 等非代码文件若干。插件机制的宿主侧（`PluginManager`/工厂注册的运行时加载）在 core 中，本章与之呼应——见 [第4章](CH04-executive-factory.md)。

## 一、本章目录树

```text
plugins/
├── CMakeLists.txt                      # 插件总控：_SETUPPLUGIN 宏 + 各插件 OPTION/ADD_SUBDIRECTORY
├── CMakeLists_PluginTemplate.txt       # 新插件 CMakeLists 模板
├── CInterfacePlugin/                   # 27 文件：C 接口（11 代码 + MATLAB 脚本等）
│   ├── src/  command/ factory/ include/ plugin/
│   ├── matlab/  build/matlab/          # MATLAB 驱动脚本（11 个 .m + 1 .script）
│   └── tester/                         # C 测试程序（.c/.h）
├── DataCallbackPlugin/src/base/        # 7 代码：factory/ include/ plugin/ subscriber/
├── DataInterfacePlugin/src/base/       # 23 代码：command/ datainterface/ datareader/ factory/ include/ plugin/
├── EphemPropagatorPlugin/src/base/     # 15 代码：factory/ include/ plugin/ propagator/
├── EstimationPlugin/                   # 212 文件（198 代码）：适配器/硬件/信号/测量模型/估计器/文件解析/SWIG
│   ├── src/base/  adapter(52) command(4) datafilter(6) errormodel(2) estimator(12) event(10)
│   │   factory(20) hardware(16) include(1) measurement(26) measurementfile(18)
│   │   measurementmodel(4) plugin(2) propagator(2) reporter(2) signal(12)
│   │   tdmReader(6) trackingfile(4)
│   └── src/base/swig/                  # Python/Java 绑定（navigation.i/.swg/_py.i + NavigationAPI.hpp）
├── EventLocatorPlugin/src/base/        # 23 代码：event/ factory/ include/ locator/ plugin/
├── ExtendedKalmanFilterPlugin/src/base/# 43 代码：EKF/ command/ estimatedparam/ factory/ include/ noise/ plugin/ smoother/
├── ExternalForceModelPlugin/src/base/  # 7 代码：factory/ forcemodel/ include/ plugin/
├── ExtraPropagatorsPlugin/src/base/    # 7 代码：factory/ include/ plugin/ propagator/
├── FminconOptimizerPlugin/src/base/    # 7 代码：factory/ include/ plugin/ solver/
├── FormationPlugin/src/base/           # 7 代码：factory/ formation/ include/ plugin/
├── GeometricMeasurementPlugin/src/base/# 13 代码：factory/ include/ measurement/ plugin/
└── GmatFunctionPlugin/src/base/        # 14 代码：command/ factory/ function/ include/ plugin/
```

## 二、插件通用架构

GMAT 的插件是**运行时动态加载的共享库**，其结构在编译期和运行期各有一条链路。一个插件由四要素构成：

1. **CMake 定义**：插件目录下的 `CMakeLists.txt`（调用总控文件 `plugins/CMakeLists.txt` 中的 `_SETUPPLUGIN` 宏）把源码编译成 `lib<PluginName>` 共享库；
2. **入口点 `GmatPluginFunctions.cpp`**：导出 3 个 C 函数，把插件内的工厂暴露给宿主；
3. **工厂类（派生自 `Factory`）**：把"脚本里的对象类型名"映射到 `new` 出具体对象；
4. **启动文件中的 `PLUGIN =` 条目**：声明该共享库要在启动时加载（注意：GMAT **没有独立的 `.plugin` 描述文件**，插件清单写在 `bin/gmat_startup_file.txt` 中）。

### 2.1 编译期：`_SETUPPLUGIN` 宏与总控 CMakeLists

`plugins/CMakeLists.txt` 是全仓库的插件总控。第 22~104 行定义宏 `_SETUPPLUGIN(TargetName PLUGIN_DIRS PLUGIN_SRCS INSTALL_DIR)`，它统一完成：加 `-D_DYNAMICLINK` 定义（第 24 行）、递归收集头文件、`ADD_LIBRARY(... SHARED ...)` 建共享库（第 36 行）、`TARGET_INCLUDE_DIRECTORIES(... BEFORE ...)`（第 40 行）、链接 `GmatUtil` 与 `GmatBase`（第 63~64 行）、按平台 `INSTALL`（第 70~79 行）以及 macOS 的符号链接（第 82~102 行）。第 55 行强制库前缀 `lib`（Windows 下也如此）。

每个插件通过一个 `OPTION` 决定是否编译。第 111~136 行按字母序声明本章 13 个插件的开关与默认值：

```cmake
OPTION(PLUGIN_CINTERFACE "CInterface Plugin" OFF)          # :111
OPTION(PLUGIN_DATAINTERFACE "DataInterface Plugin" ON)     # :112
OPTION(PLUGIN_DATACALLBACK "DataCallback Plugin" OFF)      # :113
OPTION(PLUGIN_EPHEMPROPAGATOR "EphemPropagator Plugin" ON) # :114
OPTION(PLUGIN_EKF "EKF Plugin" ON)                         # :115
OPTION(PLUGIN_ESTIMATION "Estimation Plugins" ON)          # :116
OPTION(PLUGIN_EVENTLOCATOR "EventLocator Plugin" ON)       # :117
OPTION(PLUGIN_EXTERNALFORCEMODEL "ExternalForceModel Plugin" ON)  # :118
OPTION(PLUGIN_EXTRAPROPAGATORS "ExtraPropagators Plugin" ON)     # :119
OPTION(PLUGIN_FMINCONOPTIMIZER "FminconOptimizer Plugin" OFF)    # :120
OPTION(PLUGIN_FORMATION "Formation Plugin" ON)             # :121
OPTION(PLUGIN_GEOMETRICMEASUREMENT "GeometricMeasurement Plugin" OFF) # :122
OPTION(PLUGIN_GMATFUNCTION "GmatFunction Plugin" ON)       # :123
```

对应每个 `if (PLUGIN_XXX)` 块把插件的 `src/base` 子目录 `ADD_SUBDIRECTORY`，并从该子目录读回 `TargetName` 累加进 `PluginTargets`（例如第 152~158 行 CInterface 块）。第 389 行把全部插件目标归入 IDE 文件夹 "GMAT Plugins"；第 536~543 行统一设库版本与 Win32 链接标志（`/NODEFAULTLIB:libcmt.lib`）。文件尾部还处理了三类"外挂"：SWIG 绑定（第 391~429 行，EstimationPlugin 的 `swig` 子目录在此挂载）、专有插件（第 431~452 行）、以及第三方的 `ListOfAdditionalPlugins.txt`（第 454~512 行）。

模板文件 `CMakeLists_PluginTemplate.txt` 给出了新插件的最小骨架（第 26~56 行）：设 `TargetName`、`ADD_DEFINITIONS("-D<PLUGINNAME>_EXPORTS")`、列出 `PLUGIN_DIRS` 与 `PLUGIN_SRCS`，最后调用 `_SETUPPLUGIN(...)`。

### 2.2 运行期入口：`GmatPluginFunctions.cpp` 的 3 个 C 函数

每个插件的 `src/base/plugin/GmatPluginFunctions.cpp` 用 `extern "C"` 导出宿主可 `dlsym/GetProcAddress` 的符号。以 `plugins/EphemPropagatorPlugin/src/base/plugin/GmatPluginFunctions.cpp` 为例：

```cpp
extern "C"
{
   Integer GetFactoryCount()                    // :49-52
   {
      return 1;
   }
   Factory* GetFactoryPointer(Integer index)    // :69-84
   {
      Factory* factory = NULL;
      switch (index)
      {
         case 0:
            factory = new EphemPropFactory;     // :76
            break;
         default:
            break;
      }
      return factory;
   }
   void SetMessageReceiver(MessageReceiver* mr) // :102-105
   {
      MessageInterface::SetMessageReceiver(mr);
   }
}
```

- `GetFactoryCount()`：告诉宿主本插件有几个工厂（星历插件只返回 1）。
- `GetFactoryPointer(index)`：按索引 `new` 出对应工厂实例——这是"插件 → 工厂"的唯一通道。
- `SetMessageReceiver(mr)`：把全局日志/消息接收器注入插件，保证插件内的 `MessageInterface` 输出走 GMAT 统一通道（第 101~104 行注释标明该方法"可能在未来版本移除"）。

接口契约在 core 的 `src/base/plugin/DynamicLibrary.hpp` 第 44~126 行文档中精确定义。除上述 3 个必选函数外，插件还可选实现：`GetTriggerManagerCount/GetTriggerManager`（沙盒级 TriggerManager，第 67~75 行）、`GetMenuEntryCount/GetMenuEntry`（向资源树注册新节点，第 77~112 行）、`GetGuiToolkitName/GetGuiFactoryCount/GetGuiFactory`（GUI 面板，第 114~125 行）。

### 2.3 工厂基类 `Factory` 与类型专用创建方法

core 的 `src/base/factory/Factory.hpp` 定义工厂基类。其核心是第 85~86 行的泛型创建：

```cpp
virtual GmatBase* CreateObject(const std::string &ofType,
                               const std::string &withName = "");
```

`ofType` 是脚本里写出的类型名（如 `"SPK"`、`"BatchEstimator"`），工厂内部按它分派。为让调用方拿到带类型的指针，`Factory` 还声明了一组 `CreateXxx` 虚函数（第 89~163 行），本章各插件覆盖其中相应者，例如：

| 插件 | 覆盖的 CreateXxx | 返回类型 |
|---|---|---|
| EphemPropagatorPlugin | `CreatePropagator` | `Propagator*` |
| EstimationPlugin | `CreateSolver`、`CreateMeasurementModel`、`CreateErrorModel`、`CreateDataFilter`、`CreateDataFile`、`CreateObType`、`CreateEvent`、`CreateHardware`… | 各对应 |
| EventLocatorPlugin | `CreateEventLocator`、`CreateEvent` | `EventLocator*`、`Event*` |
| GeometricMeasurementPlugin | `CreateMeasurementModel` | `MeasurementModelBase*` |

第 167~168 行的 `GetListOfCreatableObjects(qualifier)` 返回本工厂能创建的类型名清单（`createList`），供脚本解释器构建"可创建对象映射"（见 §2.4）。

### 2.4 运行时加载与注册调用链

加载由 `Moderator` 发起，链路如下（core，`src/base/executive/Moderator.cpp`）：

1. `Moderator::LoadPlugins()`（第 848 行）从 `FileManager::GetPluginList()` 取回启动文件里的 `PLUGIN =` 名单，逐个调 `LoadAPlugin(*i)`（第 863/871 行）。之后第 876~879 行让脚本解释器 `BuildCreatableObjectMaps`，把新类型名接进解析表。
2. `Moderator::LoadAPlugin(name)`（第 896 行）规范化路径后调 `LoadLibrary(pluginName)`（第 945 行）得到 `DynamicLibrary*`。
3. 取工厂：`fc = theLib->GetFactoryCount()`（第 949 行），循环 `newFactory = theLib->GetGmatFactory(i)`（第 964 行）——它内部就是调插件导出的 `GetFactoryPointer`。
4. 注册：`theFactoryManager->RegisterFactory(newFactory)`（第 967 行）；注册失败打印告警（第 968~970 行）。
5. 可选注册 TriggerManager（第 999~1017 行）、资源树菜单项（第 1018~1046 行）、GUI 工厂（第 1048~1054 行）。

`FactoryManager::RegisterFactory`（`src/base/factory/FactoryManager.cpp` 第 84~103 行）把工厂追加进 `factoryList/factoryTypeList`，并按 `GetOverriddenTypes()` 建立覆盖表。之后脚本创建对象走 `FactoryManager::CreateObject(generalType, ofType, withName)`（第 120~129 行）→ `FindFactory` 定位工厂 → `f->CreateObject(ofType, withName)`。

启动文件机制在 `src/gmatutil/util/FileManager.cpp`：解析时遇到 `PLUGIN` 类型就 `mPluginList.push_back(name)`（第 3450~3457 行），写出启动文件时按 `PLUGIN = <name>` 回写（第 1563~1571 行）；启动文件固定名为 `gmat_startup_file.txt`（第 3851 行）。**因此"声明一个插件"的实际动作 = 在 `bin/gmat_startup_file.txt` 加一行 `PLUGIN = libMyPlugin`**（无扩展名，见 `LoadAPlugin` 第 892~893 行注释）。

### 2.5 每个插件的代码骨架与 `*_defs.hpp`

各插件目录高度同构，通常含：`factory/`（工厂）、`include/`（`*_defs.hpp`：API 导出宏 + 参数 ID 枚举 + 常量）、`plugin/GmatPluginFunctions.cpp/.hpp`（入口）、以及承载业务类的子目录（`propagator/`、`estimator/`、`measurement/` 等）。`*_defs.hpp` 里的 `class Xxx_API`（如 `EPHEM_PROPAGATOR_API`）对应 CMake 的 `_EXPORTS` 定义，控制符号的 dllimport/dllexport。参数表统一走 `GmatBase` 的 `PARAMETER_TEXT/PARAMETER_TYPE` 宏 + `GetParameterInfo()`，各插件的参数 ID 从 1 递增，常以 `ParameterCount` 收尾。

## 三、逐插件讲解

以下按目录逐个讲解 13 个插件。每个插件给出：目的、导出类清单、插件注册与工厂、逐文件讲解、关键类深读、参数表、与 core 的扩展点，最后附该插件的「文件清单附录」表。

### 13.1 根目录共享文件（`plugins/`）

| 相对路径 | 职责 | 关键内容 |
|---|---|---|
| `plugins/CMakeLists.txt` | 插件总控脚本，544 行 | `_SETUPPLUGIN` 宏（:22-104）、`OPTION` 开关（:111-136）、各插件 `ADD_SUBDIRECTORY`（:151-385）、SWIG/专有/第三方插件挂载（:391-512）、版本与链接标志（:536-543） |
| `plugins/CMakeLists_PluginTemplate.txt` | 新插件 CMake 模板，56 行 | `TargetName`、`ADD_DEFINITIONS`、`PLUGIN_DIRS/PLUGIN_SRCS`、`_SETUPPLUGIN` 调用（:26-56） |

根目录**没有** `README.md`（已 glob 验证）。全仓库插件清单、默认开关与"如何新增一个插件"的说明都集中写在 `plugins/CMakeLists.txt` 的注释中（第 106~110、142~149 行）。

### 13.2 CInterfacePlugin（C 语言接口）

**目录**：`plugins/CInterfacePlugin/`（`src/command`、`src/factory`、`src/include`、`src/plugin`、`tester/`、`matlab/`、`build/matlab/` 共 27 个文件，其中 11 个 C/C++ 代码）

**构建开关**：`PLUGIN_CINTERFACE`，默认 `OFF`（见 `plugins/CMakeLists.txt` 第 111 行 `OPTION(PLUGIN_CINTERFACE "CInterface Plugin" OFF)`）

**目标库名**：`CInterface`（`src/CMakeLists.txt` 第 17 行 `SET(TargetName CInterface)`），产物为 `libCInterface` 动态库，并 `FORCE` 安装到 `bin`。

**一句话目的**：以纯 C 风格的 `extern "C"` 函数把 GMAT 引擎（启动、加载/运行脚本、访问 ODE 模型、读写传播状态向量、求导数、枚举对象）暴露给外部客户端（如 NASA ODTBX 的 MATLAB 封装），是三个接口类插件中"最早阶段、最低层"的桥接层。

#### 目的与职责

该插件不向 GMAT 内部注册"业务对象"，而是向**进程外客户端**暴露一套稳定的 C ABI。整个模块的核心价值都集中在 `src/plugin/CInterfacePluginFunctions.cpp` 里的一整块 `extern "C"` 代码（第 61~839 行）：它通过 `Moderator` 单例驱动 GMAT 引擎生命周期，通过 `PropSetup`/`ODEModel` 访问当前传播模型，并维护 `odeTable`、`setupTable`、`odeNameTable` 三张内部表（第 53~55 行）在"名字/索引 → 模型指针"之间建立映射。

作为插件它仍遵循 GMAT 的标准加载协议：导出 `GetFactoryCount()`、`GetFactoryPointer(index)`、`SetMessageReceiver(mr)` 三个符号，使 `Moderator` 能以 `PLUGIN = ./libCInterface`（见 `CInterfaceIntro.hpp` 第 32 行）的方式动态加载它。它还附带一个 `PrepareMissionSequence` 命令：这是一个"空操作"命令（no-op），用于把脚本从"立即执行"切换为"只填充并初始化 Sandbox、不真正跑任务序列"的模式，从而避免为接口准备对象时执行整个任务。

#### 导出类清单

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `PrepareMissionSequence` | `GmatCommand`（`src/command/PrepareMissionSequence.hpp` 第 49 行） | 空操作命令，把 GMAT 切到"命令模式"、只初始化 Sandbox 不执行序列 |
| `CCommandFactory` | `Factory`（`src/factory/CCommandFactory.hpp` 第 40 行） | 按类型串创建 `PrepareMissionSequence` 命令对象 |

> 注：本插件没有名为 `CInterface` 的类。对外暴露的是 `CInterfacePluginFunctions.cpp` 中的自由函数（`StartGmat`/`LoadScript`/`RunScript`/`FindOdeModel`/`GetState`/`GetDerivatives` 等），其声明汇总在 `src/plugin/CInterfaceFunctions.h`。

#### 插件注册与工厂

`GmatPluginFunctions.cpp` 的 `extern "C"` 块里实现 GMAT 插件加载协议：

- `GetFactoryCount()`（第 75 行）返回 `1`，表示本模块只有 1 个工厂；
- `GetFactoryPointer(Integer index)`（第 94 行）`case 0` 时 `new CCommandFactory` 返回命令工厂；
- `SetMessageReceiver(MessageReceiver* mr)`（第 120 行）把 GMAT 的全局消息接收器透传给 `MessageInterface`。

`CCommandFactory::CCommandFactory()`（`factory/CCommandFactory.cpp` 第 78~86 行）继承 `Factory(Gmat::COMMAND)`，并向 `creatables` 与 `qualifiedCreatables` 各压入 `"PrepareMissionSequence"`；`CreateCommand()`（第 56 行）按 `ofType == "PrepareMissionSequence"` 实例化命令；`GetListOfCreatableObjects("SequenceStarters")`（第 152 行）把它归入"序列起始命令"分类，供 GUI/脚本解析器识别。

#### 逐文件讲解

##### `src/command/PrepareMissionSequence.hpp` / `.cpp`

命令对象本身，继承 `GmatCommand`。构造时把类型名设为 `"PrepareMissionSequence"` 并推入 `objectTypeNames`（`.cpp` 第 43~47 行）。核心是 `Execute()`（第 111~125 行）：只调用 `BuildCommandSummary(true)` 后返回 `true`，被注释掉的 `PrepareToPropagate` 遍历说明它**故意不触发传播**。`GetGeneratingString()`（第 160 行）把脚本串还原为 `PrepareMissionSequence;`；`Clone()`（第 137 行）做深拷贝；`RenameRefObject()`（第 147 行）恒返回 `true` 表示它不引用任何可改名对象。类尾部 `DEFAULT_TO_NO_CLONES`（`.hpp` 第 71 行）关闭了默认引用对象机制。

##### `src/factory/CCommandFactory.hpp` / `.cpp`

见"插件注册与工厂"一节。`CreateCommand()` 是工厂唯一真正产出物；构造/拷贝构造/赋值三个入口都保证 `creatables` 里至少有一个 `"PrepareMissionSequence"`，避免空列表。

##### `src/include/CInterfaceIntro.hpp`

Doxygen 主页面（`\mainpage`），不是代码。它用文字规定了接口的使用契约：状态向量必须是"笛卡尔、地心、地球赤道坐标系"，历元用 GMAT 的 A.1 修正儒略日格式，时间偏移以秒为单位（第 14~17 行）；并给出运行时加载方式 `PLUGIN = ./libCInterface`（第 32 行）和"启动引擎 → 加载脚本 → 运行脚本建立连接 → 访问内部对象"四步调用顺序（第 36~42 行）。

##### `src/include/GmatCFunc_defs.hpp`

跨平台导出宏定义文件。在 Windows + MSVC + `_DYNAMICLINK` 下根据 `CINTERFACE_EXPORTS` 把 `CINTERFACE_API` 展开为 `__declspec(dllexport/dllimport)`（第 49~53 行），其余平台为空宏（第 72~74 行）。它是 `CInterfaceFunctions.h` 与 `PrepareMissionSequence.hpp` 的公共前置依赖。

##### `src/plugin/CInterfaceFunctions.h`

**纯 C 客户端函数声明清单**（第 44~70 行），被 `CInterfacePluginFunctions.hpp` 的 `extern "C"` 块 `#include`（`.hpp` 第 58 行）。声明包括：`getLastMessage()`、`StartGmat()`、`LoadScript()`、`RunScript()`、`LoadAndRunScript()`、`FindOdeModel()`、`SetModel()`、`SetModelByName()`、`GetStateSize()`、`GetStateDescription()`、`SetState()`、`GetState()`、`GetDerivativesForState()`、`GetDerivatives()`、`CountObjects()`、`GetObjectName()`、`GetRunSummary()`、`GetPluginFunction()`。文件头注释（第 29~36 行）特别说明：该文件会被 MATLAB 解析，用于 `loadlibrary`/`calllib` 生成原型。

##### `src/plugin/CInterfacePluginFunctions.hpp`

`.cpp` 的声明头。`extern "C"` 块内声明三个插件协议函数 + `#include "CInterfaceFunctions.h"` 引入全部客户端函数（第 45~58 行），再声明三个内部辅助函数 `GetODEModel`、`GetFirstPropagator`、`GetPropagator`（第 61~63 行）。模块级全局（`ode`、`pSetup`、`nextOdeIndex`、三张 map）定义在 `.cpp` 第 48~55 行。

##### `src/plugin/CInterfacePluginFunctions.cpp`

本插件 90% 的实质代码（详见"关键类深读"）。除插件协议三函数外，实现了：引擎生命周期 `StartGmat`（第 163 行）、`LoadScript`（第 208 行）、`RunScript`（第 258 行）、未启用的 `LoadAndRunScript`（第 316 行）；ODE 模型访问 `FindOdeModel`（第 350 行）、`SetModel`（第 426 行）、`SetModelByName`（第 459 行）；状态读写 `GetStateSize`（第 480 行）、`GetStateDescription`（第 500 行）、`SetState`（第 534 行）、`GetState`（第 584 行）；求导 `GetDerivativesForState`（第 636 行）、`GetDerivatives`（第 692 行）；对象枚举 `CountObjects`（第 743 行）、`GetObjectName`（第 772 行）、`GetRunSummary`（第 800 行）、动态函数查找 `GetPluginFunction`（第 834 行）。`extern "C"` 块之外是三个内部辅助函数，用于沿任务序列链表查找 `PropSetup`。

##### `tester/CInterfaceTester.h` / `.c`

Unix/Linux 下的独立 C 测试程序（`.c` 第 166 行注释说明 Mac/Linux 可用，Windows 待补）。`main()`（第 157 行）先 `dlopen("libCInterface.so"/"libCInterface.dylib")`（第 169~171 行），然后演示完整调用链：`GetFunction("AintNoSuchFunction")` 验证错误路径 → `StartGmat` → 循环 20 次交替加载 `Ex_ForceModels.script` / `Ex_HohmannTransfer.script` → `RunScript` → `FindOdeModel` → `GetState` → `GetDerivatives`。`GetFunction()`（第 14 行）在 Windows 用 `GetProcAddress`、其余平台用 `dlsym` 解析符号，是手动重建 C ABI 绑定的典型样本。

##### `matlab/` 与 `build/matlab/`（数据/脚本类文件）

`matlab/` 目录是 ODTBX 侧的 MATLAB 封装层，通过 `calllib('libCInterface', ...)` 调用上面的 C 函数；`build/matlab/` 是构建期用 MATLAB `loadlibrary` 从 `CInterfaceFunctions.h` 生成 `interfacewrapper.m` 原型与 thunk 库的脚本。代表性深读：

- **`matlab/startgmat.m`**（第 1~102 行）：对用户暴露的一站式入口。先解析可选参数 `filename`/`odemodelname`（默认 `GmatConfig.script`），用 `CheckForFile` 校验脚本存在（第 76 行），依次调用 `opengmat()`（第 82 行）、`preparescript(filename)`（第 85 行）、`findodemodel(odemodelname)`（第 94~96 行），返回 `odeId`。
- **`matlab/run_gmatinterface.m`**（第 1~237 行）：完整的接口自测脚本。`loadlibrary('libCInterface', @interfacewrapper)`（第 49 行）后逐段演示 `StartGmat`→`LoadScript`/`RunScript`→`FindOdeModel`→`GetStateSize`→`SetState`→`GetDerivatives`/`GetDerivativesForState`，并用 `libpointer`/`setdatatype` 解出返回的 `double*` 与 A 矩阵（第 105~227 行）。
- **`matlab/GmatConfig.script`**（第 1~63 行）：默认 GMAT 配置脚本，创建 1 个 `Spacecraft`、2 个 `ForceModel`（`DefaultProp_ForceModel` 与 `fm`）、2 个 `Propagator`，末尾 `BeginMissionSequence` 后跟两条 `Propagate ... 'AMatrix'`（第 60~63 行）；第 61 行的 `%PrepareMissionSequence;` 注释提示了"用 PrepareMissionSequence 代替 BeginMissionSequence"的用法。

MATLAB/脚本文件清单：

| 文件 | 职责 |
| --- | --- |
| `matlab/CheckForFile.m` | 用 `dir` 判断文件是否在当前目录，返回 0/1 |
| `matlab/findgmatrootpath.m` | 从 `gmat_startup_file.txt` 提取 `ROOT_PATH` 并校验其有效性 |
| `matlab/opengmat.m` | `loadlibrary` + `StartGmat` 启动引擎，失败时清理临时启动文件并报错 |
| `matlab/preparescript.m` | `LoadScript` + `RunScript` 装载并运行配置脚本 |
| `matlab/findodemodel.m` | 包装 `FindOdeModel`，返回模型 ID |
| `matlab/setodemodel.m` | 包装 `SetModel`，约定 ID 从 1000 起（0 代表第一个模型） |
| `matlab/closegmat.m` | `unloadlibrary` 卸载接口库，并清理临时 `gmat_startup_file.txt` |
| `matlab/startgmat.m` | 一站式启动入口（上文深读） |
| `matlab/run_gmatinterface.m` | 接口自测脚本（上文深读） |
| `matlab/GmatConfig.script` | 默认 GMAT 配置脚本（上文深读） |
| `build/matlab/prepareInterface.m` | 从源码树内 `libCInterface` + `CInterfaceFunctions.h` 生成 `interfacewrapper.m` |
| `build/matlab/prepareInterface_cmake.m` | 从已安装 GMAT 的 `bin/libCInterface` 生成原型并拷贝到 `matlab/libCInterface` |

##### 非代码文件

`src/Doxyfile`、`src/Doxyfile2` 为 Doxygen 配置；`src/.gitignore` 为忽略清单；`src/CMakeLists.txt`（第 17 行定义目标名、第 25~29 行列编译源、第 35 行 `_SETUPPLUGIN(... bin FORCE)` 强制装入 `bin`、第 62~113 行处理 MATLAB 脚本安装与 thunk 生成）。

#### 关键类深读：C 接口的暴露方式

本插件通过 **`extern "C"` + `CINTERFACE_API` 导出宏** 把 C++ 内部功能打成无 name-mangling 的 C 符号，供 `dlopen`/`dlsym`（或 MATLAB `loadlibrary`）直接解析。以 `GetFactoryCount` 为例（`CInterfacePluginFunctions.cpp` 第 75~78 行）：

```cpp
extern "C"
{
   Integer GetFactoryCount()
   {
      return 1;
   }
```

调用链的关键是 `Moderator` 单例与 `PropSetup` 的关系：

1. `StartGmat()`（第 163~189 行）取 `Moderator::Instance()`，调用 `Initialize("gmat_startup_file.txt")`，成功后清空三张表并把 `nextOdeIndex` 复位为 1000。
2. `LoadScript(scriptName)`（第 208~237 行）调 `Moderator::InterpretScript`；`RunScript()`（第 258~296 行）调 `Moderator::RunMission` 并翻译返回值（1→成功、-1~-4→不同错误）。
3. `FindOdeModel(modelName)`（第 350~408 行）先查 `odeNameTable` 命中缓存；否则取 `Moderator::GetFirstCommand(1)` 得首命令，交给 `GetODEModel(&current, modelName)` 沿命令链表遍历，遇到 `Propagate` 命令就 `current->Execute()` 建立内部连接，再 `GetRefObject(Gmat::PROP_SETUP, "", 0)` 取 `PropSetup`，从中拿 `ODEModel`，写回 `odeTable`/`setupTable` 并分配递增 ID（`GetODEModel` 第 864~984 行，`GetFirstPropagator` 第 997 行，`GetPropagator` 第 1059 行）。
4. `GetState()`/`SetState()` 通过 `pSetup->GetPropStateManager()->GetState()` 读写 `GmatState`（第 540、590 行）；`GetDerivatives()` 调 `ode->GetDerivatives(state, dt, order)` 后用 `GetDerivativeArray()` 拷贝导数（第 716~727 行）。

`CInterfaceTester.c` 则演示了客户端如何**手动重绑**这些符号：`GetFunction()` 用 `dlsym` 取函数指针并按正确签名强制转换（如 `GetDerivatives` 在第 137 行转成 `double*(*)(double,int,int*)`），随后依次调用，等价于 MATLAB 侧 `calllib` 做的事。

#### 参数表

`PrepareMissionSequence` 未定义任何自有参数（`.hpp` 第 71 行 `DEFAULT_TO_NO_CLONES` 且无 `GetParameterInfo`）；`CInterfacePluginFunctions.cpp` 中的接口函数为自由 C 函数，同样无 `GetParameterInfo` 参数表，故本节省略。

#### 与 core 的扩展点

- `PrepareMissionSequence` 继承 core 的 `GmatCommand`（`src/base/command/GmatCommand.hpp`），需重写 `Execute()`、`Clone()`、`RenameRefObject()`、`GetGeneratingString()`，并借助 `DEFAULT_TO_NO_CLONES` 关闭默认引用对象表。
- `CCommandFactory` 继承 core 的 `Factory`（`src/base/factory/Factory.hpp`），需重写 `CreateCommand()` 与 `GetListOfCreatableObjects()`。
- 插件加载协议（`GetFactoryCount`/`GetFactoryPointer`/`SetMessageReceiver`）由 core 的 `Moderator` 通过动态库符号查找调用，是 GMAT 所有插件的统一入口约定。

#### 文件清单附录

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/CMakeLists.txt` | 构建脚本，目标 `CInterface`，强制装 `bin` | `SET(TargetName CInterface)`、`_SETUPPLUGIN` |
| `src/command/PrepareMissionSequence.hpp` | 空操作命令声明 | `PrepareMissionSequence` |
| `src/command/PrepareMissionSequence.cpp` | 空操作命令实现 | `Execute`、`Clone`、`GetGeneratingString` |
| `src/factory/CCommandFactory.hpp` | 命令工厂声明 | `CCommandFactory` |
| `src/factory/CCommandFactory.cpp` | 命令工厂实现 | `CreateCommand`、`GetListOfCreatableObjects` |
| `src/include/CInterfaceIntro.hpp` | Doxygen 主页面（使用说明） | 文档注释 |
| `src/include/GmatCFunc_defs.hpp` | 导出宏定义 | `CINTERFACE_API` |
| `src/plugin/CInterfaceFunctions.h` | 客户端 C 函数声明清单 | `StartGmat`、`GetDerivatives` 等 |
| `src/plugin/CInterfacePluginFunctions.hpp` | 插件函数声明头 | 协议三函数 + 内部辅助函数声明 |
| `src/plugin/CInterfacePluginFunctions.cpp` | 插件核心实现 | `StartGmat`、`LoadScript`、`FindOdeModel`、`GetState`、`GetDerivatives`、`GetODEModel`、`GetPropagator` |
| `tester/CInterfaceTester.h` | 测试程序声明 | `GetFunction`、`main` |
| `tester/CInterfaceTester.c` | C 测试程序实现 | `GetFunction`、`main`、`dlopen`/`dlsym` |
| `matlab/*.m`（10 个） | ODTBX MATLAB 封装 | `startgmat`、`run_gmatinterface`、`opengmat` 等 |
| `matlab/GmatConfig.script` | 默认配置脚本 | `Create Propagator`、`BeginMissionSequence` |
| `build/matlab/*.m`（2 个） | MATLAB 原型生成脚本 | `prepareInterface`、`prepareInterface_cmake` |
| `src/Doxyfile`、`src/Doxyfile2` | Doxygen 配置 | — |
| `src/.gitignore` | 忽略清单 | — |

### 13.3 DataCallbackPlugin（数据回调订阅器）

**目录**：`plugins/DataCallbackPlugin/src/base/`（`factory`、`include`、`plugin`、`subscriber` 共 8 个文件）

**构建开关**：`PLUGIN_DATACALLBACK`，默认 `OFF`（见 `plugins/CMakeLists.txt` 第 113 行 `OPTION(PLUGIN_DATACALLBACK "DataCallback Plugin" OFF)`）

**目标库名**：`DataCallback`（`src/base/CMakeLists.txt` 第 17 行 `SET(TargetName DataCallback)`），`FORCE` 安装到 `bin`。

**一句话目的**：实现一个 `Subscriber` 子类，把 GMAT 运行时实时发布的传播数据（double 数组）转发给用户提供的 C 回调函数，实现"边算边回调"的原型式数据出口。

#### 目的与职责

`DataCallback` 是一个"只发布、不落盘/不绘图"的订阅器：它与 `ReportFile`、`XyPlot` 等常规 `Subscriber` 同族，但把 `Distribute()` 里收到的数据直接交给用户在 `SetCallback()` 注册的函数指针（`void (*CBFcn)(const double*, int, void*)`），而不是写文件或画图。文件头（`DataCallback.hpp` 第 27~29 行、`DataCallback.cpp` 第 27~29 行）均标注"prototype code（原型代码）"，说明它是为外部客户端（同样面向 ODTBX 一类用户）验证数据回调通道而设的最小实现。

插件层面它仍然走 GMAT 标准动态库协议（`GetFactoryCount`/`GetFactoryPointer`/`SetMessageReceiver`），额外导出一个 `SetCallback(subscriberName, CBFcn, userData)` 自由函数，让 C 客户端在运行前就能把回调挂到某个已创建的 `DataCallback` 订阅器上。工厂注册的订阅器类型名是 `"DataCallback"`。

#### 导出类清单

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `DataCallback` | `Subscriber`（`subscriber/DataCallback.hpp` 第 40 行） | 订阅 `Parameter` 数据，在 `Distribute` 时调用用户回调函数 |
| `DataCallbackFactory` | `Factory`（`factory/DataCallbackFactory.hpp` 第 40 行） | 按类型串 `"DataCallback"` 创建订阅器对象 |

> 基类 `Subscriber` 定义于 core `src/base/subscriber/Subscriber.hpp` 第 54 行（`class GMAT_API Subscriber : public GmatBase`），`Distribute` 的两个虚函数原型见第 258~259 行。

#### 插件注册与工厂

`plugin/GmatPluginFunctions.cpp` 的 `extern "C"` 块：

- `GetFactoryCount()`（第 56 行）返回 `1`；
- `GetFactoryPointer(index)`（第 72 行）`case 0` 返回 `new DataCallbackFactory`；
- `SetMessageReceiver(mr)`（第 98 行）透传 `MessageInterface`；
- `SetCallback(subscriberName, CBFcn, userData)`（第 114~145 行）：从 `Moderator::Instance()` 取订阅器，`dynamic_cast<DataCallback*>` 校验类型后调用 `dc->SetCallback(CBFcn, userData)`，返回 0/-1/-2/-3 区分成功、找不到 Moderator、找不到订阅器、非 DataCallback；
- `getLastMessage()`（第 160 行）返回模块级 `lastMsg` 状态串。

`DataCallbackFactory`（`factory/DataCallbackFactory.cpp`）：构造函数（第 87~94 行）继承 `Factory(Gmat::SUBSCRIBER)` 并向 `creatables` 压入 `"DataCallback"`；`CreateObject()`（第 50 行）转调 `CreateSubscriber()`；`CreateSubscriber()`（第 68 行）在 `ofType == "DataCallback"` 时 `new DataCallback(ofType, withName)`。

#### 逐文件讲解

##### `src/base/CMakeLists.txt`

构建脚本：`TargetName = DataCallback`（第 17 行），编译源 `factory/DataCallbackFactory.cpp`、`plugin/GmatPluginFunctions.cpp`、`subscriber/DataCallback.cpp`（第 25~29 行），`_SETUPPLUGIN(... bin FORCE)`（第 35 行），并重定义导出宏符号 `DATACALLBACK_EXPORTS`（第 38 行）。

##### `src/base/include/datacallback_defs.hpp`

导出宏定义，与 `CInterfacePlugin` 的 `GmatCFunc_defs.hpp` 同构：Windows/MSVC/`_DYNAMICLINK` 下按 `DATACALLBACK_EXPORTS` 展开 `DATACALLBACK_API` 为 `__declspec(dllexport/dllimport)`（第 47~51 行），其它平台为空宏（第 72~74 行）。

##### `src/base/plugin/GmatPluginFunctions.hpp` / `.cpp`

插件协议 + `SetCallback` + `getLastMessage` 的声明与实现（详见"插件注册与工厂"）。

##### `src/base/factory/DataCallbackFactory.hpp` / `.cpp`

订阅器工厂（详见"插件注册与工厂"）。`CreateObject`/`CreateSubscriber` 都是虚函数重写，供 `Factory` 基类多态分派。

##### `src/base/subscriber/DataCallback.hpp` / `.cpp`

订阅器核心。要点：

- **静态参数表**（`.cpp` 第 42~52 行）：`PARAMETER_TEXT = {"DataElements"}`，类型 `Gmat::OBJECTARRAY_TYPE`；枚举 `DATA_ELEMENTS = SubscriberParamCount`（`.hpp` 第 109~113 行）把它挂在 `Subscriber` 参数之后。
- **构造函数**（第 62~77 行）：初始化 `mCallbackFcn(NULL)`、`mUserData(NULL)`，`objectTypes.push_back(Gmat::SUBSCRIBER)`，并 `blockCommandModeAssignment = false`；若传入 `firstParam` 则立即 `AddParameter`。
- **`AddParameter(paramName, index)`**（第 140~158 行）：去重后把参数名压入 `mParamNames`，同步压入一个 `NULL` 到 `mParams` 与 `yParamWrappers` 占位，`mNumParams` 随之递增。
- **`SetCallback(CBFcn, userdata)`**（第 167~171 行）：保存函数指针与用户数据。
- **`Initialize()`**（第 176~213 行）：校验 `mNumParams > 0` 且首参数非空，否则 `active = false` 并返回 false；通过后调用 `Subscriber::Initialize()`。
- **`Distribute(const Real* dat, Integer len)`**（第 515~529 行，重写基类第 259 行虚函数）：核心回调点。当 `mCallbackFcn != NULL` 且 `len > 0` 时，遍历 `yParamWrappers` 逐个 `EvaluateReal()` 得到**按正确参考系换算后的**数据，拷贝进临时数组，再 `mCallbackFcn(convertedData, len, mUserData)`。
- 其余为 `Get/SetStringParameter`（`DATA_ELEMENTS` 走 `AddParameter`）、`SetRefObject`/`GetRefObject`（把 `Gmat::PARAMETER` 引用解析到 `mParams`，并借助 `GmatStringUtil::GetArrayName` 处理数组元素）、`GetWrapperObjectNameArray`（把 `mParamNames` 填进 `yWrapperObjectNames`）等常规 GmatBase 粘合代码。

#### 关键类深读：回调订阅机制

`DataCallback` 复用了 GMAT 成熟的 **Publisher → Subscriber** 数据分发链，自己不发明新通道：

1. **注册**：脚本 `Create DataCallback dc;` 经 `DataCallbackFactory` 建对象；C 客户端随后调 `SetCallback("dc", myCb, userData)` 挂回调（`GmatPluginFunctions.cpp` 第 114 行）。
2. **触发**：任务运行时，core 的 `Publisher::Publish()`（`src/base/executive/Publisher.cpp` 第 360 行注释）遍历订阅器，对每个 `Subscriber` 调 `ReceiveData(stream)` 或 `ReceiveData(data, count)`（第 411、413 行）。
3. **分发**：`Subscriber::ReceiveData(const Real*, len)`（`src/base/subscriber/Subscriber.cpp` 第 435~464 行）先查 `active`，再调虚函数 `Distribute(datastream, len)`（第 458 行）——多态落到 `DataCallback::Distribute`。
4. **回调**：`DataCallback::Distribute`（第 515~529 行）通过 `yParamWrappers[i]->EvaluateReal()` 把原始 `Real*` 数据换算到目标参考系，再交给 `mCallbackFcn`。

因此"何时被 Sandbox 触发"的答案是：**由 Sandbox 内部（如 `Propagate` 命令逐点推进时）把当前状态/参数值经 `Publisher` 广播，最终抵达 `ReceiveData`→`Distribute`→回调函数**。`DataCallback` 只重写了 `Distribute(const Real*, Integer)` 这一层（`Receive`/`Initialize` 均继承自 `Subscriber`，`Initialize` 则重写以做参数非空校验），是最小的 `Subscriber` 定制点。

#### 参数表

`DataCallback` 的 `GetParameterText`/`GetParameterType`（`.cpp` 第 247~278 行）基于静态表返回，其自有参数只有一个：

| 参数文本 | 参数类型 | 说明 |
| --- | --- | --- |
| `DataElements` | `OBJECTARRAY_TYPE`（字符串数组） | 要订阅并回调的 `Parameter` 对象名列表，逐项 `AddParameter` 累积 |

（`SetStringParameter(id==DATA_ELEMENTS)` 第 325~333 行即 `AddParameter`；`IsParameterCommandModeSettable` 第 303 行把 `DATA_ELEMENTS` 设为 command 模式不可设置。）

#### 与 core 的扩展点

- `DataCallback` 继承 `Subscriber`（`src/base/subscriber/Subscriber.hpp`），须重写：`Distribute(const Real*, Integer)`（基类第 259 行）作为数据出口；`Initialize()` 做自校验；`Clone()`/`Copy()` 保持可复制语义；`GetParameterText/ID/Type` 与 `SetStringParameter`/`GetStringArrayParameter` 挂载 `DataElements` 参数；`SetRefObject`/`GetRefObject`/`GetRefObjectTypeArray` 声明对 `Gmat::PARAMETER` 的引用。
- `DataCallbackFactory` 继承 `Factory`（`src/base/factory/Factory.hpp`），须重写 `CreateObject`/`CreateSubscriber`。
- 运行时依赖 core 的 `Publisher`（`src/base/executive/Publisher.cpp`）调用 `ReceiveData` 驱动数据流，`Subscriber` 基类提供的 `yParamWrappers`（`ElementWrapper` 数组，`Subscriber.hpp` 第 237 行）承担"原始数据 → 目标参考系"的换算。

#### 文件清单附录

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/CMakeLists.txt` | 构建脚本，目标 `DataCallback` | `SET(TargetName DataCallback)` |
| `src/base/include/datacallback_defs.hpp` | 导出宏定义 | `DATACALLBACK_API` |
| `src/base/plugin/GmatPluginFunctions.hpp` | 插件协议 + `SetCallback` 声明 | `SetCallback`、`getLastMessage` |
| `src/base/plugin/GmatPluginFunctions.cpp` | 插件协议 + `SetCallback` 实现 | `GetFactoryPointer`、`SetCallback` |
| `src/base/factory/DataCallbackFactory.hpp` | 订阅器工厂声明 | `DataCallbackFactory` |
| `src/base/factory/DataCallbackFactory.cpp` | 订阅器工厂实现 | `CreateSubscriber`、`CreateObject` |
| `src/base/subscriber/DataCallback.hpp` | 订阅器声明 | `DataCallback`、`Distribute`、`DATA_ELEMENTS` |
| `src/base/subscriber/DataCallback.cpp` | 订阅器实现 | `AddParameter`、`SetCallback`、`Initialize`、`Distribute` |

### 13.4 DataInterfacePlugin（数据接口与读取器）

**目录**：`plugins/DataInterfacePlugin/src/base/`（`command`、`datainterface`、`datareader`、`factory`、`include`、`plugin` 共 23 个代码文件，另含 `CMakeLists.txt` 与 2 个 `.gitignore`）

**构建开关**：`PLUGIN_DATAINTERFACE`，默认 `ON`（见 `plugins/CMakeLists.txt` 第 112 行 `OPTION(PLUGIN_DATAINTERFACE "DataInterface Plugin" ON)`）

**目标库名**：`DataInterface`（`src/base/CMakeLists.txt` 第 17 行 `SET(TargetName DataInterface)`），安装到 `plugins` 目录（第 41 行 `_SETUPPLUGIN(... plugins)`，非 `FORCE`）。

**一句话目的**：以 `Interface → DataInterface → FileInterface` 与 `GmatBase → DataReader → FileReader → TcopsVHFData → TcopsVHFAscii` 两条继承链，实现"从外部数据文件读取字段、经坐标/时间换算后 `Set` 到 GMAT 对象"的通用数据导入框架。

#### 目的与职责

该插件把"读外部数据"这件事拆成两层正交的抽象：**接口层**（`Interface`/`DataInterface`/`FileInterface`）负责 GMAT 对象侧的参数管理、文件流打开/关闭、字段→对象参数名映射，是脚本可见的 `Create FileInterface ...` 对象；**读取器层**（`DataReader`/`FileReader`/`TcopsVHFData`/`TcopsVHFAscii`）是纯内部对象，只认 `ifstream` 与"文件格式"，负责逐行解析并把结果塞进 `realData`/`rvector6Data`/`stringData` 三张 map。二者通过 `FileInterface` 持有 `theReader`（`DataInterface.hpp` 第 122 行）并在 `Initialize()` 里用 `ReaderFactory` 按 `Format` 创建具体读取器来衔接。

导入动作由 `Set` 命令驱动（`command/Set.cpp`）：脚本写 `Set <目标对象> <接口名>`，`Execute()` 打开接口→`LoadData()` 读文件→按 `SupportedFields` 逐字段把值写回目标对象（必要时用 `CoordinateConverter`/`TimeSystemConverter` 换算）。目前唯一落地的具体格式是 TCOPS 矢量保持文件（TVHF）的 ASCII 版（`TVHF_ASCII`），对应读取器 `TcopsVHFAscii`。

#### 导出类清单

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `DataInterface` | `Interface`（`datainterface/DataInterface.hpp` 第 42 行） | 数据接口抽象基类，持有一个 `DataReader` 并声明纯虚 `LoadData()` |
| `FileInterface` | `DataInterface`（`datainterface/FileInterface.hpp` 第 42 行） | 基于 `ifstream` 的文件接口，负责开流/建读取器/关流 |
| `DataReader` | `GmatBase`（`datareader/DataReader.hpp` 第 42 行） | 读取器抽象基类，定义 `readerDataType` 枚举与纯虚解析函数 |
| `FileReader` | `DataReader`（`datareader/FileReader.hpp` 第 40 行） | 逐行读文件的读取器基类，提供三种 `Parse*Value` |
| `TcopsVHFData` | `FileReader`（`datareader/TcopsVHFData.hpp` 第 43 行） | 声明 TVHF 支持的字段及坐标/时间/原点语义 |
| `TcopsVHFAscii` | `TcopsVHFData`（`datareader/TcopsVHFAscii.hpp` 第 43 行） | 具体解析 TVHF ASCII（dump 与 Task 9 两种） |
| `Set` | `GmatCommand`（`command/Set.hpp` 第 44 行） | 把接口读到的字段值设置到目标对象 |
| `DataInterfaceFactory` | `Factory` | 创建 `FileInterface`（`Gmat::INTERFACE` 类型） |
| `DataInterfaceCommandFactory` | `Factory` | 创建 `Set` 命令（`Gmat::COMMAND` 类型） |
| `ReaderFactory` | `Factory` | 创建 `TVHF_ASCII` 读取器（内部用，非注册工厂） |

> core `Interface` 定义于 `src/base/interface/Interface.hpp` 第 36 行（`class GMAT_API Interface : public GmatBase`），仅声明 `Open()`/`Close()` 两个虚函数。

#### 插件注册与工厂

`plugin/GmatPluginFunctions.cpp`：

- `GetFactoryCount()`（第 50 行）返回 `2`（接口工厂 + 命令工厂）；
- `GetFactoryPointer(index)`（第 67 行）：`case 0` → `new DataInterfaceFactory`，`case 1` → `new DataInterfaceCommandFactory`；
- `SetMessageReceiver(mr)`（第 100 行）透传 `MessageInterface`（注释标注"deprecated"）。

三个工厂的 `createList`：

- `DataInterfaceFactory`（`factory/DataInterfaceFactory.cpp` 第 47~56 行）：`Factory(Gmat::INTERFACE)`，`creatables` 压入 `"FileInterface"`，并 `GmatType::RegisterType(Gmat::DATAINTERFACE_SOURCE, "DataInterface")` 注册新类型名；`CreateInterface()`（第 117 行）在 `ofType=="FileInterface"` 时 `new FileInterface(withName)`，`CreateObject()`（第 143 行）转调之。
- `DataInterfaceCommandFactory`（`factory/DataInterfaceCommandFactory.cpp` 第 46~53 行）：`Factory(Gmat::COMMAND)`，`creatables` 压入 `"Set"`；`CreateCommand()`（第 131 行）`new Set()`。
- `ReaderFactory`（`factory/ReaderFactory.cpp` 第 46~53 行）：`Factory(Gmat::INTERFACE)`，`creatables` 压入 `"TVHF_ASCII"`；`CreateObject()`（第 130 行）`new TcopsVHFAscii(withName)`，并校验返回对象 `IsOfType("DataReader")`（第 140 行）。该工厂**不在插件 `GetFactoryPointer` 中注册**，只被 `FileInterface::Initialize()` 直接实例化使用（见 `FileInterface.cpp` 第 33~34 行注释）。

#### 逐文件讲解

##### `src/base/CMakeLists.txt`

构建脚本：`TargetName = DataInterface`（第 17 行），编译 11 个 `.cpp`（`command/Set.cpp`、`datainterface/DataInterface.cpp`、`datainterface/FileInterface.cpp`、`datareader/DataReader.cpp`、`datareader/FileReader.cpp`、`datareader/TcopsVHFAscii.cpp`、`datareader/TcopsVHFData.cpp`、三个 `factory/*.cpp`、`plugin/GmatPluginFunctions.cpp`，第 25~37 行），`_SETUPPLUGIN(... plugins)`（第 41 行）。

##### `src/base/include/DataInterfaceDefs.hpp`

导出宏定义，同构于其它两个插件：按 `DATAINTERFACE_EXPORTS` 展开 `DATAINTERFACE_API`（第 50~53 行），非 Windows 为空（第 75~77 行）。

##### `src/base/command/Set.hpp` / `.cpp`

导入命令。声明（`.hpp`）保留 `InterpretAction`/`Execute`/`Initialize`/`TakeAction` 及 `targetName`/`interfaceName`/`loadAll`/`selections` 等成员，参数表代码整段被注释（第 70~87、122~132 行）。实现要点：

- **`InterpretAction()`**（`.cpp` 第 401 行）：手工解析生成串 `Set <target> <interface> (Data={...})`，做括号/空格匹配校验，取出 `targetName`、`interfaceName`，选项交给 `CheckForOptions`。
- **`CheckForOptions()`**（第 1029 行）：解析 `Data={...}`，把所选字段压入 `selections`（`"Epoch"` 恒插到首位，第 1108 行），含 `"All"` 则 `loadAll` 保持 true。
- **`Initialize()`**（第 522 行）：`FindObject` 定位 target 与 interface，`IsOfType("DataInterface")` 校验后转型；非 `loadAll` 时用 `SupportedFields` 告警未识别关键字。
- **`Execute()`**（第 571 行）：`Open()==0` 则 `LoadData()`、`Close()`；随后对 `SupportedFields`（或 `selections`）逐字段调 `SetTargetParameterData(fieldType, field)`。
- **`SetTargetParameterData()`**（第 793 行）：按 `DataReader::readerDataType` 分支——`READER_REAL` 写 `SetRealParameter`；`READER_RVECTOR6` 必要时经 `ConvertToTargetCoordinateSystem`（第 936 行，用 `CoordinateSystem::CreateLocalCoordinateSystem` + `CoordinateConverter`）后逐分量写；`READER_TIMESTRING` 对 `SpaceObject` 经 `ConvertToSystemTime`（第 1010 行，`TimeSystemConverter`）写历元；`READER_STRING`/`READER_SUBTYPE` 目前空转返回 true。
- **`GetGeneratingString()`**（第 696 行）反序列化回 `Set target interface (Data={...});`。

##### `src/base/datainterface/DataInterface.hpp` / `.cpp`

接口抽象层。静态参数表（`.cpp` 第 38~52 行）：`Format`（`ENUMERATION_TYPE`）、`SelectedFields`（`STRINGARRAY_TYPE`）、`SupportedFields`（`STRINGARRAY_TYPE`）。`Open()`（第 620 行）与 `Close()`（第 694 行）在基类里是"返回 -1 的占位"，真正实现留给 `FileInterface`；`LoadData()` 声明为纯虚（`.hpp` 第 100 行 `virtual bool LoadData() = 0`）。`GetRealValue`/`GetReal6Vector`/`GetStringValue`（第 711~752 行）与 `UsesCoordinateSystem`/`GetTimeSystemName` 等（第 765~865 行）都是**非虚的 pass-through**，转调 `theReader` 对应方法；`GetReaderParameterType` 亦然。`SetStringParameter(id==FORMAT)`（第 282 行）校验值必须在 `supportedFormats` 中，否则抛 `InterfaceException`。

##### `src/base/datainterface/FileInterface.hpp` / `.cpp`

文件接口实现。新增参数 `Filename`（`FILENAME_TYPE`，`.hpp` 第 101 行）。构造函数（`.cpp` 第 68~81 行）用 `ReaderFactory` 取 `GetListOfCreatableObjects()` 填充 `supportedFormats` 并取首个作为默认 `readerFormat`。关键流程：

- **`Initialize()`**（第 434~484 行）：校验 `filename` 非空、文件存在（`GmatFileUtil::DoesFileExist`）、`readerFormat` 非空，然后用 `ReaderFactory::CreateObject(readerFormat, "")` 创建 `theReader`（第 464 行）。
- **`Open()`**（第 497~522 行）：开 `theStream`，`theReader->SetStream(&theStream, filename)`。
- **`LoadData()`**（第 533~547 行）：`theReader->ReadData()`。
- **`Close()`**（第 560~576 行）：关 `theStream`。

##### `src/base/datareader/DataReader.hpp` / `.cpp`

读取器抽象层。`readerDataType` 枚举（`.hpp` 第 45~53 行）以 `30000` 起编码 `READER_REAL`/`READER_RVECTOR6`/`READER_STRING`/`READER_TIMESTRING`/`READER_SUBTYPE`/`READER_UNKNOWN`。构造（`.cpp` 第 44~53 行）调 `GmatBase(Gmat::DATAINTERFACE_SOURCE, ...)` 并注册 `"DataReader"` 类型名。声明纯虚：`ReadData()`（第 67 行）与三个 `Parse*Value()`（第 119~122 行）。数据存取走"非虚 public 包装 → 虚 protected 实现"模式：`GetRealValue` 在 `dataReady` 时才调 `GetRData`（第 206~216 行），`GetRData` 查 `realData` map，未命中返回哨兵 `-999999.999999`。`WasDataLoaded` 查 `dataLoaded` map；`ClearData` 只清标志不清数据（第 187 行）。

##### `src/base/datareader/FileReader.hpp` / `.cpp`

逐行文件读取器基类。持有 `theStream`、`dataBuffer`（`StringArray` 行缓冲）。`SetStream()`（第 121 行）绑定流与文件名；`ReadLine()`（第 145 行）用 `GmatFileUtil::GetLine` 读一行。三个 `Parse*Value` 是通用解析器：`ParseRealValue`（第 164 行）在行内找 `fileStringMap[theField]` 关键字、跳过空格、截取到下一个空格，把 FORTRAN 的 `D/d` 指数记号换成 `e`（第 204~206 行），`GmatStringUtil::IsValidReal` 校验后写 `realData`；`ParseRvector6Value`（第 262 行）对 6 个标识符逐个 `ParseRealValue`（允许跨最多 7 行）拼 `Rvector6`，凑齐 6 个分量才写 `rvector6Data`；`ParseStringValue`（第 325 行）截取关键字后到行尾的字符串写 `stringData`。

##### `src/base/datareader/TcopsVHFData.hpp` / `.cpp`

TVHF 字段定义层（注释说明它是为将来二进制 TVHF 预留的中间层，`.hpp` 第 36~42 行）。构造函数（`.cpp` 第 46~138 行）填充 `supportedFields` 及四张 map：`Epoch`（`READER_TIMESTRING`，文件关键字 `EPOCH TIME FOR ELEMENTS`）、`CartesianState`（`READER_RVECTOR6`，关键字 `CARTESIAN COORDINATES`，映射对象参数 `CartesianX`）、`Cr`（`READER_REAL`，关键字 `CSUBR`）、6 个 `READER_SUBTYPE`（`X `/`Y `/`Z `/`XDOT`/`YDOT`/`ZDOT`）、`CoordinateSystem`/`CentralBody`（`READER_STRING`）。`UsesCoordinateSystem`/`GetCoordinateSystemName`（第 217~242 行）只对 `CartesianState` 返回真/`origin+csSuffix`；`UsesTimeSystem` 只对 `Epoch` 返回真、系统名为 `UTCModJulian`。`BuildOriginName()`（第 326 行）把文件里的 `SUN/MOON/...` 翻译成 GMAT 名（`MOON`→`Luna`），未知原点抛 `InterfaceException`；`BuildCSName()`（第 371 行）只接受 `J2000`→`MJ2000Eq`，`TOD`/`1950` 明确抛"不支持"。

##### `src/base/datareader/TcopsVHFAscii.hpp` / `.cpp`

TVHF ASCII 具体解析。`ReadData()`（第 141~233 行）是主循环：先清旧数据，逐行 `ReadLine`；在找到表头前把行暂存进 `dataBuffer`，用 `CheckForHeader`（第 256 行，识别 `TCOPS VECTOR HOLD FILE DUMP PROGRAM` 为 dump、`TVHF ELEMENT SET SUMMARY` 为 Task 9）判定；找到表头后调 `ManageStartData`（第 317 行，Task 9 文件取前 7 行作为 `startVector`），再读到 `CheckForBlockBoundary`（第 289 行，dump 文件按 `LONG REPORT OF THE TCOPS VECTOR HOLD FILE` 分块，当前只保留第一块）。收尾 `ParseDataBlock()`（第 359 行）遍历 `supportedFields`，按 `dataType` 分派到三个 `Parse*Value`（`CartesianState` 用 6 个标识符拼 `Rvector6`，`Epoch` 走 `ParseTime`）。`ParseTime()`（第 429 行）从 `stringData` 解析 `yyyy mm dd hh mm ss`，做两位年份扩展与各分量合法性校验后 `ModifiedJulianDate(...)` 得到修正儒略日，写回 `realData["Epoch"]`。

##### `src/base/plugin/GmatPluginFunctions.hpp` / `.cpp`

插件协议（见"插件注册与工厂"）。

##### `src/base/factory/`（三个工厂）

见"插件注册与工厂"。

##### 非代码文件

`src/.gitignore`、`src/base/.gitignore` 为忽略清单。

#### 关键类深读：数据接口的层次与数据流

**`DataReader` 基类接口**：它刻意采用"public 非虚入口 + protected 虚实现"的 NVI（Non-Virtual Interface）结构——子类只需重写三个纯虚 `ParseRealValue`/`ParseRvector6Value`/`ParseStringValue`（`DataReader.hpp` 第 119~122 行）和一个纯虚 `ReadData()`（第 67 行），把解析结果写进受保护的 `realData`/`rvector6Data`/`stringData` map，而 `GetRealValue`/`GetReal6Vector`/`GetStringValue` 等对外访问入口由基类统一加 `dataReady` 门槛与哨兵值（`DataReader.cpp` 第 206~262 行）。

**`FileReader` 的文件读取**：`ReadLine` 把文件变成 `dataBuffer` 行缓冲，三个 `Parse*Value` 用 `fileStringMap`（字段 → 文件内关键字）在行内定位数据，把 FORTRAN 的 `D` 指数转换成 C++ 能解析的 `e`，再经 `GmatStringUtil::IsValidReal` 校验后入 map——这是"关键字驱动"而非"列位置驱动"的松散格式解析。

**`TcopsVHFAscii`/`TcopsVHFData` 的具体格式解析**：`TcopsVHFData` 在构造期就把 TVHF 的字段语义表（文件关键字、对象参数名、数据类型、是否坐标/时间相关）一次性填好，`TcopsVHFAscii` 只负责"把字节流按表头/块边界切块 → 按字段语义表逐字段 `Parse*Value`"，最后用 `BuildOriginName`/`BuildCSName` 把文件里的 `SUN`/`J2000` 等翻译成 GMAT 内部名。这体现了"格式语义（TcopsVHFData）与文件形态（TcopsVHFAscii）分离"的设计。

**`DataInterface`/`FileInterface` 与 core `Interface` 的关系**：core `Interface` 只定义 `Open`/`Close` 两个虚函数（`Interface.hpp` 第 43~44 行）；`DataInterface` 在此基础上加 `Format`/`SelectedFields`/`SupportedFields` 参数与纯虚 `LoadData`；`FileInterface` 再补 `Filename` 参数并真正实现 `Open`/`LoadData`/`Close` 的流操作，用 `ReaderFactory` 按 `Format` 把 `DataReader` 实例注入。`Set` 命令只面向 `DataInterface` 抽象编程，因此新增格式只需加 `DataReader` 子类 + 在 `ReaderFactory` 登记，命令与接口层无需改动。

**`Set` 命令作用**：它是整个插件对外的"执行入口"，把"接口读到的数据"与"目标对象参数"按 `readerDataType` 逐一对接，并承担坐标系统（`CoordinateConverter`）与时间系统（`TimeSystemConverter`）换算，确保外部文件数据落进 GMAT 对象前符合对象自身约定的参考系与 A.1 历元。

#### 参数表

`DataInterface` 与 `FileInterface` 的 `GetParameterText`/`GetParameterType` 基于静态表（`DataInterface.cpp` 第 38~52 行、`FileInterface.cpp` 第 46~56 行）：

| 参数文本 | 所属类 | 参数类型 | 说明 |
| --- | --- | --- | --- |
| `Format` | `DataInterface` | `ENUMERATION_TYPE` | 读取器格式名（如 `TVHF_ASCII`），枚举值来自 `supportedFormats` |
| `SelectedFields` | `DataInterface` | `STRINGARRAY_TYPE` | 用户选择的字段，只读，透传 `theReader->GetSelectedFieldNames` |
| `SupportedFields` | `DataInterface` | `STRINGARRAY_TYPE` | 读取器支持的字段列表，只读 |
| `Filename` | `FileInterface` | `FILENAME_TYPE` | 要读取的文件路径 |

（`Set` 命令的自有参数表在源码中被注释禁用，无 `GetParameterInfo`；`DataReader`/`FileReader`/`TcopsVHF*` 的参数表段同样被注释，字段语义改用构造期的 map 填充，不通过 `GetParameterInfo` 暴露。）

#### 与 core 的扩展点

- `DataInterface` 继承 `Interface`（`src/base/interface/Interface.hpp` 第 36 行），须实现 `Open()`/`Close()` 并新增纯虚 `LoadData()`；`FileInterface` 进一步实现流操作。
- `DataReader`/`FileReader`/`TcopsVHFData`/`TcopsVHFAscii` 继承 `GmatBase`（`src/base/foundation/GmatBase.hpp`），通过重写 `DataReader` 的三个纯虚 `Parse*Value()` 与 `ReadData()` 完成格式解析；`TcopsVHFData` 重写 `UsesCoordinateSystem`/`GetCoordinateSystemName`/`UsesOrigin`/`GetOriginName`/`UsesTimeSystem`/`GetTimeSystemName` 六个语义查询虚函数。
- `Set` 继承 `GmatCommand`（`src/base/command/GmatCommand.hpp`），须重写 `InterpretAction()`/`Execute()`/`Initialize()`/`Clone()`/`GetGeneratingString()`，并实现 `GetRefObjectName`/`SetRefObjectName`/`TakeAction`/`RenameRefObject`。
- 三个工厂继承 `Factory`（`src/base/factory/Factory.hpp`），分别重写 `CreateInterface`/`CreateObject` 或 `CreateCommand`。

#### 文件清单附录

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/CMakeLists.txt` | 构建脚本，目标 `DataInterface` | `SET(TargetName DataInterface)` |
| `src/base/include/DataInterfaceDefs.hpp` | 导出宏定义 | `DATAINTERFACE_API` |
| `src/base/command/Set.hpp` | Set 命令声明 | `Set` |
| `src/base/command/Set.cpp` | Set 命令实现 | `InterpretAction`、`Execute`、`SetTargetParameterData`、`ConvertToTargetCoordinateSystem`、`ConvertToSystemTime`、`CheckForOptions` |
| `src/base/datainterface/DataInterface.hpp` | 数据接口抽象声明 | `DataInterface`、`LoadData`（纯虚）、`FORMAT` 枚举 |
| `src/base/datainterface/DataInterface.cpp` | 数据接口抽象实现 | `GetRealValue`、`GetStringArrayParameter`、`SetStringParameter(FORMAT)` |
| `src/base/datainterface/FileInterface.hpp` | 文件接口声明 | `FileInterface`、`FILENAME` 枚举 |
| `src/base/datainterface/FileInterface.cpp` | 文件接口实现 | `Initialize`、`Open`、`LoadData`、`Close` |
| `src/base/datareader/DataReader.hpp` | 读取器抽象声明 | `DataReader`、`readerDataType`、纯虚 `ReadData`/`Parse*Value` |
| `src/base/datareader/DataReader.cpp` | 读取器抽象实现 | `GetRealValue`、`WasDataLoaded`、`GetRData` |
| `src/base/datareader/FileReader.hpp` | 文件读取器基类声明 | `FileReader`、`SetStream`、`ReadLine` |
| `src/base/datareader/FileReader.cpp` | 文件读取器基类实现 | `ParseRealValue`、`ParseRvector6Value`、`ParseStringValue` |
| `src/base/datareader/TcopsVHFData.hpp` | TVHF 字段语义声明 | `TcopsVHFData`、`UsesCoordinateSystem` |
| `src/base/datareader/TcopsVHFData.cpp` | TVHF 字段语义实现 | 构造期字段表、`BuildOriginName`、`BuildCSName` |
| `src/base/datareader/TcopsVHFAscii.hpp` | TVHF ASCII 读取器声明 | `TcopsVHFAscii`、`ReadData` |
| `src/base/datareader/TcopsVHFAscii.cpp` | TVHF ASCII 读取器实现 | `ReadData`、`CheckForHeader`、`ParseDataBlock`、`ParseTime` |
| `src/base/factory/DataInterfaceFactory.hpp` / `.cpp` | 接口工厂 | `CreateInterface`、`CreateObject` |
| `src/base/factory/DataInterfaceCommandFactory.hpp` / `.cpp` | 命令工厂 | `CreateCommand` |
| `src/base/factory/ReaderFactory.hpp` / `.cpp` | 读取器工厂（内部用） | `CreateObject` |
| `src/base/plugin/GmatPluginFunctions.hpp` / `.cpp` | 插件协议 | `GetFactoryCount`、`GetFactoryPointer` |
| `src/.gitignore`、`src/base/.gitignore` | 忽略清单 | — |

### 13.5 EphemPropagatorPlugin（星历传播器）

**目录**：`plugins/EphemPropagatorPlugin/src/base/`，子目录 `factory/`、`include/`、`plugin/`、`propagator/`，共 15 个 C++ 文件（7 个 `.cpp`、8 个 `.hpp`，另加 1 个 `CMakeLists.txt`）。

**构建开关**：`PLUGIN_EPHEMPROPAGATOR`，默认 `ON`，见 `plugins/CMakeLists.txt` 第 114 行。

**目标库名**：`EphemPropagator`，由 `plugins/EphemPropagatorPlugin/src/base/CMakeLists.txt` 第 17 行 `SET(TargetName EphemPropagator)` 决定；`PLUGIN_SRCS`（第 25–33 行）列出 7 个源文件。第 40 行 `DEFINE_SYMBOL "EPHEM_PROPAGATOR_EXPORTS"` 为 Windows 导出注入宏。

**一句话目的**：提供一族"读星历文件 → 插值出状态"的 `Propagator` 派生类，用外部星历（CCSDS OEM、NASA Code-500、SPICE SPK、STK `.e`）替代数值积分来驱动航天器状态演化。

#### 目的与职责

该插件把"轨道演化来自星历表插值而非 ODE 积分"这一能力封装为可脚本化的传播器。抽象基类 `EphemerisPropagator` 继承 core 的 `Propagator`，声明 `UsesODEModel()` 恒返回 `false`（`EphemerisPropagator.cpp` 第 1310–1313 行），并保留两个纯虚方法 `Step()` 与 `UpdateState()`（`EphemerisPropagator.hpp` 第 156、261 行）交给派生类实现；四个具体子类各自持有一个不同的星历读取器，在 `UpdateState()` 里"查表 + 插值"出当前历元的状态，再经 `CoordinateConverter` 统一转换到 MJ2000Eq 系。传播器不求解动力学方程，只按星历跨度推进历元，因此天然支持负向传播（`stepDirection`，`EphemerisPropagator.cpp` 第 473–476 行）。

四个子类对应的星历格式不同：`CcsdsEphPropagator` 读 CCSDS OEM（轨道星历消息，`CCSDSEphemerisFile` 读取器）；`Code500Propagator` 读 NASA Code-500 二进制星历（`Code500EphemerisFile`）；`SPKPropagator` 读 SPICE SPK 内核（`SpiceOrbitKernelReader`）；`StkEPropagator` 读 STK `.e` 星历（`STKEphemerisFile`）。基类还负责"跨星历外推"的策略：`TakeAction("RunPastStartEnd")` 关掉 `stopOutsideOfEphem` 标志（第 1291–1294 行），允许 TDRS 类测量模型在星历跨度之外继续运行而不报错。

#### 导出类清单

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `EphemerisPropagator` | `Propagator`（`src/base/propagator/Propagator.hpp`） | 星历传播器抽象基类，管理星历跨度、历元源、状态缓冲 |
| `CcsdsEphPropagator` | `EphemerisPropagator` | 读 CCSDS OEM 星历并插值出状态 |
| `Code500Propagator` | `EphemerisPropagator` | 读 NASA Code-500 星历，用 not-a-knot 样条插值 |
| `SPKPropagator` | `EphemerisPropagator` | 读 SPICE SPK 内核，经 `SpiceOrbitKernelReader` 取状态 |
| `StkEPropagator` | `EphemerisPropagator` | 读 STK `.e` 星历并插值出状态 |
| `EphemPropFactory` | `Factory`（`src/base/factory/Factory.hpp`） | 创建上述传播器对象，类型 `Gmat::PROPAGATOR` |

继承声明行号：`EphemerisPropagator.hpp` 第 44 行 `class EPHEM_PROPAGATOR_API EphemerisPropagator : public Propagator`；`CcsdsEphPropagator.hpp` 第 41 行、`Code500Propagator.hpp` 第 44 行、`SPKPropagator.hpp` 第 43 行、`StkEPropagator.hpp` 第 44 行分别 `: public EphemerisPropagator`；`EphemPropFactory.hpp` 第 47 行 `: public Factory`。

#### 插件注册与工厂

`plugin/GmatPluginFunctions.cpp` 定义插件加载 C 接口：`GetFactoryCount()` 返回 `1`（第 49–52 行），`GetFactoryPointer(index)` 在 `case 0` 时 `new EphemPropFactory`（第 73–77 行），`SetMessageReceiver` 调用 `MessageInterface::SetMessageReceiver(mr)`（第 102–105 行）。头文件在 `extern "C"` 中声明这三个符号（`GmatPluginFunctions.hpp` 第 45–50 行）。

`EphemPropFactory::CreatePropagator` 按脚本类型字符串创建对象（`factory/EphemPropFactory.cpp` 第 71–87 行）：`"SPK"`→`SPKPropagator`、`"Code500"`→`Code500Propagator`、`"STK"`→`StkEPropagator`、`"CCSDS-OEM"`→`CcsdsEphPropagator`；`CreateObject` 直接委托给它（第 52–56 行）。默认构造函数以 `Factory(Gmat::PROPAGATOR)` 初始化并把四种类型压入 `creatables`（第 98–108 行）；拷贝构造（第 135–145 行）沿用同一模式。

#### 逐文件讲解

##### include/ephempropagator_defs.hpp

职责：DLL 导入/导出宏。Windows + MSVC + `_DYNAMICLINK` 下按 `EPHEM_PROPAGATOR_EXPORTS` 定义 `EPHEM_PROPAGATOR_API` 为 `__declspec(dllexport/dllimport)`（第 47–51 行），并处理 STL 模板导出 `DECLSPECIFIER`/`EXPIMP_TEMPLATE`（第 60–66 行）；非 Windows 或未定义宏时置空（第 72–74 行）。`EPHEM_PROPAGATOR_EXPORTS` 由 CMake 第 40 行 `DEFINE_SYMBOL` 注入。

##### factory/EphemPropFactory.hpp

职责：声明工厂类。重写 `CreateObject`（第 50 行）与 `CreatePropagator`（第 52 行），提供默认/列表/拷贝构造与赋值、析构（第 56–64 行）。include `Factory.hpp` 与 `ephempropagator_defs.hpp`（第 39–40 行）。

##### factory/EphemPropFactory.cpp

职责：实现工厂。`CreatePropagator` 的四个分支见上文；`creatables` 依次为 `"SPK"/"Code500"/"STK"/"CCSDS-OEM"`（第 103–106 行）。赋值运算符仅调用 `Factory::operator=`（第 159–163 行）。

##### plugin/GmatPluginFunctions.hpp / .cpp

职责：插件加载 C 接口声明与实现，模式与其它插件一致（详见"插件注册与工厂"）。

##### propagator/EphemerisPropagator.hpp

职责：声明抽象基类。公开大量脚本参数访问方法（`Get/SetRealParameter`、`Get/SetStringParameter`、`GetStringArrayParameter` 等，第 53–119 行）与引用对象接口（`GetRefObjectArray`/`SetRefObject`/`RenameRefObject`，第 121–147 行）；传播入口 `Initialize()`（第 154 行）、`Step(Real)`（第 155 行）、纯虚 `Step()`（第 156 行）、纯虚 `UpdateState()`（第 261 行）。保护成员包含 `Ephemeris *theEphem`（第 183 行）、`ephemStep`（第 185 行）、`PropagationStateManager *psm`（第 214 行）、`state`/`j2kState`（第 217–219 行）、`stopOutsideOfEphem`（第 204 行）等；`StartEpochSource` 枚举 `FROM_SCRIPT/FROM_EPHEM/FROM_SPACECRAFT`（第 174–179 行）描述初始历元来源。参数 ID 枚举从 `PropagatorParamCount` 偏移（第 240–250 行）。

##### propagator/EphemerisPropagator.cpp

职责：实现基类。静态参数表 `PARAMETER_TEXT` = `StepSize/CentralBody/EpochFormat/StartEpoch/EphemStart/EphemEnd/StartOptions`（第 51–61 行），类型为 `REAL/OBJECT/STRING/STRING/REAL/REAL/STRINGARRAY`（第 63–74 行）。构造函数默认 `ephemStep=300.0`、`epochFormat="A1ModJulian"`、`stopOutsideOfEphem=true`、`startEpochSource=FROM_EPHEM`（第 91–112 行），并把 `"EphemStart"` 作为默认起始历元写入 `startOptions`（第 120–124 行）。`GetParameterID` 先查本类表再回退基类（第 264–274 行）；`IsParameterReadOnly` 把 `INITIAL_STEP_SIZE`、`EPHEM_START_OPTIONS`、`EPHEM_START_A1MJD`、`EPHEM_END_A1MJD` 置为只读（第 365–370 行）；`SetRealParameter` 处理 `EPHEM_STEP_SIZE`（第 461–466 行）并在 `INITIAL_STEP_SIZE` 为负时置 `stepDirection=-1`（第 473–476 行）。`Initialize()`（第 1340 行起）按 `psm` 状态维数分配 `state`/`j2kState`（第 1348–1373 行），再按 `startEpochSource` 三分支决定初始历元（`FROM_SPACECRAFT` 第 1392–1440 行、`FROM_EPHEM` 第 1442–1468 行、`FROM_SCRIPT` 第 1471 行起）。`SetSolarSystem` 校验并缓存中心天体/参考系（第 994–1020 行）。

##### propagator/CcsdsEphPropagator.hpp / .cpp

职责：CCSDS OEM 传播器。`.hpp` 成员 `CCSDSEphemerisFile ephem`（第 101 行）、`ephemRecords`（第 105–106 行）、`CoordinateConverter cc`/`CoordinateSystem *ephemCoord/*j2k`（第 119–124 行）；重写 `Initialize/Step/RawStep/GetStepTaken`（第 89–95 行）与 `UpdateState/SetEphemSpan`（第 127–128 行），并声明 `BuildCoordinates`（第 130 行）。`.cpp` 参数表仅一项 `EphemFile`（`FILENAME_TYPE`，第 54、61 行）。`UpdateState()`（第 1023–1058 行）核心是 `theState = ephem.InterpolatePoint(currentEpoch)`（第 1033/1035 行），若 `ephemCoord` 非空则经 `cc.Convert(currentEpoch, ..., ephemCoord, state, j2k)` 转系（第 1046/1051 行），否则 `memcpy` 直拷（第 1057 行）。`CCSDSEphemerisFile` 的 `InterpolatePoint` 最终调用 CCSDS 分段的 Lagrange 插值（core 侧 `src/gmatutil/util/CCSDSOEMSegment.cpp` 第 323 行 `return InterpolateLagrange(atEpoch)`，插值器名强制为 `"Lagrange"`，见 `CCSDSEphemerisFile.cpp` 第 256、405 行）。

##### propagator/Code500Propagator.hpp / .cpp

职责：Code-500 传播器。`.hpp` 成员 `Code500EphemerisFile ephem`（第 104 行）、`Interpolator *interp`（第 106 行）、`ephemRecords`（第 112–113 行）、`startEpochs/timeSteps/timeSpans`（第 119–129 行），并声明 `FindRecord`/`UpdateInterpolator`/`GetState`（第 141–146 行）与单位换算常量 `DUL_TO_KM` 等（第 162–165 行）。`.cpp` 参数表仅 `EphemFile`（第 55、62 行）。初始化时 `interp = new NotAKnotInterpolator("Code500NotAKnot", 6)`（第 871–874 行）——这是唯一显式用 not-a-knot 三次样条的传播器。`FindRecord(GmatEpoch)`（第 1255–1286 行）按 `startEpochs[]` 二分定位数据块 `record`，再用 `secsPastStart/timeSteps[record]` 算块内 `stateIndex`。`UpdateInterpolator`（第 1408 行起）把目标历元落在插值窗口中心，向插值器 `AddPoint` 灌入相邻状态点（第 1496–1549 行）。`UpdateState()`（第 1170–1223 行）直接 `interp->Interpolate(currentEpoch, theState)`（第 1189/1191 行）后转系。

##### propagator/SPKPropagator.hpp / .cpp

职责：SPICE SPK 传播器。`.hpp` 成员 `spkFileNames`（第 101 行）、`naifIds`（第 103 行）、`SpiceOrbitKernelReader *skr`（第 120 行）、`spkCentralBody/spkCentralBodyNaifId`（第 114–116 行）；重写 `Initialize/LoadSpans/Step/RawStep`（第 89–97 行）。`.cpp` 参数表仅 `SPKFiles`（`STRINGARRAY_TYPE`，第 50、57 行）。`UpdateState()`（第 1162 行起）在越界检查后调用 `skr->GetTargetState(scName, id, currentEpochGT, spkCentralBody, spkCentralBodyNaifId)`（第 1219–1220 行）直接由 SPICE 内核取目标状态（插值由 SPICE 内部完成），再 `ReturnFromOriginGT` 回原点（第 1245 行）；异常路径区分"越界"与"内核间隙"（第 1213–1237 行）。

##### propagator/StkEPropagator.hpp / .cpp

职责：STK `.e` 传播器。`.hpp` 成员 `STKEphemerisFile ephem`（第 105 行）、`ephemRecords`（第 109–110 行）、`CoordinateConverter cc`/`ephemCoord`/`j2k`（第 123–128 行）；重写 `Step/StepGT/RawStep`（第 96–98 行）与 `UpdateState/SetEphemSpan/BuildCoordinates`（第 130–134 行）。`.cpp` 参数表仅 `EphemFile`（第 54、61 行）。`UpdateState()`（第 1069–1090 行）`Rvector6 theState = ephem.InterpolatePoint(currentEpoch)`（第 1079 行），随后 `cc.Convert` 到 MJ2000Eq（第 1084–1086 行）。STK 文件读取器同样强制 Lagrange 插值（`src/gmatutil/util/STKEphemerisFile.cpp` 第 1492–1496 行：非 Lagrange 时降级或报错）。

#### 关键类深读：EphemerisPropagator 的插值/外推机制

`EphemerisPropagator` 自身不实现插值，只提供骨架；插值算法分派到各子类的星历读取器：

1. **OEM/STK 路径（Lagrange）**：`CcsdsEphPropagator::UpdateState`（第 1023–1058 行）与 `StkEPropagator::UpdateState`（第 1069–1090 行）调用读取器的 `InterpolatePoint(currentEpoch)`。core 基类 `Ephemeris::InterpolatePoint`（`src/gmatutil/util/Ephemeris.cpp` 第 312 行）先 `FindSegment`/`IndexInSegment` 定位（第 316、327 行），再按阶数 `interp = new LagrangeInterpolator("", 6, maxOrder)`（第 355 行；`useHermite` 时为 `HermiteInterpolator`，第 352–353 行），随后把插值点居中（第 368–372 行）灌点计算。CCSDS OEM 的 Lagrange 插值见 `CCSDSOEMSegment::InterpolateLagrange`。
2. **Code-500 路径（not-a-knot 样条）**：`Code500Propagator` 在 `Initialize` 里 `new NotAKnotInterpolator`（第 874 行），`FindRecord`（第 1255 行）与 `UpdateInterpolator`（第 1408 行）负责把星历记录送入插值器，`UpdateState` 直接 `interp->Interpolate`（第 1189/1191 行）。
3. **SPK 路径（SPICE 内核）**：`SPKPropagator::UpdateState` 不经过通用 `Ephemeris`，而是 `SpiceOrbitKernelReader::GetTargetState`（第 1219 行）向 SPICE 库取状态，插值在 SPICE 内部完成。

外推/边界策略集中在基类：`TakeAction("RunPastStartEnd")`（`EphemerisPropagator.cpp` 第 1291–1294 行）关掉 `stopOutsideOfEphem`；`Initialize` 的 `FROM_SPACECRAFT` 分支在航天器历元早于 `ephemStart` 时夹取到 `ephemStart`（第 1404–1416 行）。

#### 参数表（各传播器脚本参数，行号见对应 `.cpp`）

`EphemerisPropagator` 基类参数（`EphemerisPropagator.cpp` 第 51–74 行）：

| 脚本名 | 类型 | 说明 |
| --- | --- | --- |
| `StepSize` | `REAL_TYPE` | 星历推进步长（默认 300 s，第 94 行） |
| `CentralBody` | `OBJECT_TYPE` | 中心天体（设置功能已关闭，第 740–743 行） |
| `EpochFormat` | `STRING_TYPE` | 历元格式，默认 `A1ModJulian` |
| `StartEpoch` | `STRING_TYPE` | 起始历元，可取值 `FromSpacecraft/EphemStart/脚本值`（第 772–780 行） |
| `EphemStart` | `REAL_TYPE` | 星历起始 A.1 MJD（只读，第 367 行） |
| `EphemEnd` | `REAL_TYPE` | 星历结束 A.1 MJD（只读，第 367 行） |
| `StartOptions` | `STRINGARRAY_TYPE` | 起始历元来源选项（只读，第 367 行） |

子类各追加一项：`CcsdsEphPropagator`/`Code500Propagator`/`StkEPropagator` 为 `EphemFile`（`FILENAME_TYPE`，分别见第 54、55、54 行），`SPKPropagator` 为 `SPKFiles`（`STRINGARRAY_TYPE`，第 50 行）。

#### 与 core 的扩展点

- 继承 `src/base/propagator/Propagator.hpp` 的 `Propagator`，须重写纯虚 `Step()` 与 `UpdateState()`（本插件在 `EphemerisPropagator` 中继续声明为纯虚，由四个子类实现）。
- 继承 `src/base/factory/Factory.hpp` 的 `Factory`，须重写 `CreateObject`（`EphemPropFactory` 另提供 `CreatePropagator`）。
- 星历读取器（`Ephemeris`/`CCSDSEphemerisFile`/`Code500EphemerisFile`/`STKEphemerisFile`/`SpiceOrbitKernelReader`）均来自 core `src/gmatutil/util/`，插值算法（`LagrangeInterpolator`/`HermiteInterpolator`/`NotAKnotInterpolator`）在 `src/gmatutil/util/interpolator/`。

#### 文件清单附录

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `plugins/EphemPropagatorPlugin/src/base/CMakeLists.txt` | 构建脚本 | `SET(TargetName EphemPropagator)`、`PLUGIN_SRCS` |
| `plugins/EphemPropagatorPlugin/src/base/include/ephempropagator_defs.hpp` | DLL 导出宏 | `EPHEM_PROPAGATOR_API` |
| `plugins/EphemPropagatorPlugin/src/base/factory/EphemPropFactory.hpp` | 工厂声明 | `EphemPropFactory` |
| `plugins/EphemPropagatorPlugin/src/base/factory/EphemPropFactory.cpp` | 工厂实现 | `CreatePropagator`、`creatables` |
| `plugins/EphemPropagatorPlugin/src/base/plugin/GmatPluginFunctions.hpp` | 加载接口声明 | `GetFactoryCount` 等 |
| `plugins/EphemPropagatorPlugin/src/base/plugin/GmatPluginFunctions.cpp` | 加载接口实现 | `GetFactoryPointer` |
| `plugins/EphemPropagatorPlugin/src/base/propagator/EphemerisPropagator.hpp` | 基类声明 | `EphemerisPropagator`、`StartEpochSource` |
| `plugins/EphemPropagatorPlugin/src/base/propagator/EphemerisPropagator.cpp` | 基类实现 | `Initialize`、`SetRealParameter`、参数表 |
| `plugins/EphemPropagatorPlugin/src/base/propagator/CcsdsEphPropagator.hpp` | OEM 传播器声明 | `CcsdsEphPropagator` |
| `plugins/EphemPropagatorPlugin/src/base/propagator/CcsdsEphPropagator.cpp` | OEM 传播器实现 | `UpdateState`、`ephem.InterpolatePoint` |
| `plugins/EphemPropagatorPlugin/src/base/propagator/Code500Propagator.hpp` | Code-500 传播器声明 | `Code500Propagator`、`NotAKnotInterpolator *interp` |
| `plugins/EphemPropagatorPlugin/src/base/propagator/Code500Propagator.cpp` | Code-500 传播器实现 | `FindRecord`、`UpdateInterpolator`、`GetState` |
| `plugins/EphemPropagatorPlugin/src/base/propagator/SPKPropagator.hpp` | SPK 传播器声明 | `SPKPropagator`、`SpiceOrbitKernelReader *skr` |
| `plugins/EphemPropagatorPlugin/src/base/propagator/SPKPropagator.cpp` | SPK 传播器实现 | `UpdateState`、`skr->GetTargetState` |
| `plugins/EphemPropagatorPlugin/src/base/propagator/StkEPropagator.hpp` | STK 传播器声明 | `StkEPropagator` |
| `plugins/EphemPropagatorPlugin/src/base/propagator/StkEPropagator.cpp` | STK 传播器实现 | `UpdateState`、`ephem.InterpolatePoint` |

### 13.6 EstimationPlugin（上）：批处理估计器与测量模型

**目录**：`plugins/EstimationPlugin/`
**构建开关**：`PLUGIN_ESTIMATION`（ON，见 `plugins/CMakeLists.txt` 第116行 `OPTION(PLUGIN_ESTIMATION "Estimation Plugins" ON)`）
**目标库名**：`GmatEstimation`（读 `plugins/EstimationPlugin/src/base/CMakeLists.txt` 第29行 `SET(TargetName GmatEstimation)`；第166行把 DLL 导出宏设为 `ESTIMATION_EXPORTS`）
**一句话目的**：本片段覆盖 EstimationPlugin 的“核心估计器 + 测量模型”子系统——批处理加权最小二乘（`BatchEstimator`）、估计状态管理（`EstimationStateManager`）、测量模型/测量数据/测量管理器、数据过滤器、误差模型、事件定位、Nav 专用 RK4 传播器，以及把上述资源注册进 GMAT 对象体系的工厂与命令入口。

> 本章为“上篇”，只覆盖 `src/base` 下 estimator、measurementmodel、measurement（根级，不含 Ionosphere/Troposphere 子目录）、command、reporter、event、propagator、errormodel、datafilter、factory、include、plugin 这些我负责的子目录；adapter、hardware、signal、measurementfile、tdmReader、trackingfile 等子目录由同章其它片段覆盖。

#### 目的与职责

EstimationPlugin 是 GMAT 的轨道确定（Orbit Determination）与测量仿真后端。它把“传播器 + 力模型 + 测量模型 + 观测数据 + 求解参数”组织成两个有限状态机求解器：

1. **`Simulator`**（仿真）：从给定初值用传播器推进轨道，在测量历元处计算测量值并（可选）加噪声写入数据文件，供后续估计使用；
2. **`Estimator`→`BatchEstimatorBase`→`BatchEstimator`**（估计）：沿整条弧段累计信息矩阵与残差，用加权最小二乘迭代修正状态，直至收敛或判定发散。

两类求解器共用一套测量基础设施：`MeasurementManager` 管理观测数据流、ramp 表和测量模型，`MeasureModel`（及其子类 `GPSPointMeasureModel`）经由 `Signal` 路径计算测量值与偏导数，`ErrorModel`/`DataFilter`/`MediaCorrection` 分别提供测量噪声偏置、二级数据编辑与传播介质修正。`EstimationStateManager` 负责把各对象上声明的 SolveFor/Consider 参数组装成估计状态向量、状态转移矩阵（STM）与协方差矩阵。整套资源通过 `plugin/GmatPluginFunctions.cpp` 暴露的工厂注册进 GMAT 的对象工厂系统，并由 `RunEstimator`/`RunSimulator` 两个 Mission Control Sequence 命令驱动。

数据流（估计）：脚本解析 → 工厂创建 `BatchEstimator` 与 `RunEstimator` 命令 → `RunEstimator::PreExecution()` 装载 propagator/事件管理器/solve-for → `BatchEstimatorBase::AdvanceState()` 循环 `PROPAGATING→CALCULATING→(LOCATING)→ACCUMULATING→ESTIMATING→CHECKINGRUN` → 收敛后 `Finalize()` 把协方差写回对象。

#### 导出类清单

基类均为只读源码确认（相对 `plugins/EstimationPlugin/src/base/`）：

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `Estimator` | `Solver`（`src/base/solver/Solver.hpp`） | 估计器抽象基类：持有 `MeasurementManager`/`EstimationStateManager`、信息矩阵、STM、协方差、报告/绘图；声明纯虚 `Estimate()/DataFilter()/IsFinalPass()/IsIterative()`。见 `estimator/Estimator.hpp:54` |
| `BatchEstimatorBase` | `Estimator`（`estimator/Estimator.hpp:54`） | 批估计状态机：`AdvanceState()` 调度、先验协方差、收敛判据（绝对/相对容差、连续发散）。见 `estimator/BatchEstimatorBase.hpp:53` |
| `BatchEstimator` | `BatchEstimatorBase`（`estimator/BatchEstimatorBase.hpp:53`） | 直接求逆的批加权最小二乘：实现 `Accumulate()/Estimate()/SolveNormalEquations()` 与内环（ILSE）/外环（OLSE）σ 编辑。见 `estimator/BatchEstimator.hpp:50` |
| `Simulator` | `Solver`（`src/base/solver/Solver.hpp`） | 测量仿真求解器：`AdvanceState()` 驱动 `SIMULATING` 态写入测量。见 `estimator/Simulator.hpp:47` |
| `EstimationStateManager` | `StateManager`（`src/base/foundation/StateManager.hpp`） | 组装估计状态向量/STM/协方差，坐标换算，SolveFor/Consider 管理。见 `estimator/EstimationStateManager.hpp:50` |
| `EstimatorException` | `BaseException`（`src/base/foundation/BaseException.hpp`） | 估计子系统异常。见 `estimator/EstimatorException.hpp:42` |
| `MeasureModel` | `GmatBase`（`src/base/foundation/GmatBase.hpp`） | 基于 Signal 路径的测量模型基类：计算测量值/偏导数、光时解、介质修正。见 `measurementmodel/MeasureModel.hpp:60` |
| `GPSPointMeasureModel` | `MeasureModel`（`measurementmodel/MeasureModel.hpp:60`） | GPS 单点解测量模型（位置点解 + 状态/参数偏导数）。见 `measurementmodel/GPSPointMeasureModel.hpp:58` |
| `MeasurementModelBase` | `GmatBase`（`src/base/foundation/GmatBase.hpp`） | 测量模型与 TrackingFileSet 的公共工厂基类（很薄）。见 `measurement/MeasurementModelBase.hpp:44` |
| `MeasurementManager` | （无基类，普通类） | 测量/观测数据的中介者。见 `measurement/MeasurementManager.hpp:57` |
| `MeasurementData` | （无基类，结构体式类） | 已计算测量值的载体结构。见 `measurement/MeasurementData.hpp:55` |
| `MeasurementException` | `BaseException`（`src/base/foundation/BaseException.hpp`） | 测量子系统异常（头文件内联实现）。见 `measurement/MeasurementException.hpp:40` |
| `MediaCorrection` | `MediaCorrectionInterface`（`src/base/solarsys/MediaCorrectionInterface.hpp`） | 介质修正模型（电离层/对流层）的插件侧基类。见 `measurement/MediaCorrection.hpp:40` |
| `RunEstimator` | `RunSolver`（`src/base/command/RunSolver.hpp`） | 驱动估计器状态机的 MCS 命令。见 `command/RunEstimator.hpp:51` |
| `RunSimulator` | `RunSolver`（`src/base/command/RunSolver.hpp`） | 驱动仿真器状态机的 MCS 命令。见 `command/RunSimulator.hpp:53` |
| `ProgressReporter` | （无基类，普通类） | Nav 进度报告（写文件或消息接口）。见 `reporter/ProgressReporter.hpp:38` |
| `Event` | `GmatBase`（`src/base/foundation/GmatBase.hpp`） | 事件基类：`Evaluate()` 纯虚，环形缓冲监控临界/极值。见 `event/Event.hpp:67` |
| `EventData` | （无基类，结构体） | 事件参与者的状态/STM 数据。见 `event/EventData.hpp:48` |
| `EventManager` | `TriggerManager`（`src/base/foundation/TriggerManager.hpp`） | 事件管理器/触发器，内含 `EstimationRootFinder`。见 `event/EventManager.hpp:43` |
| `EstimationRootFinder` | （无基类，普通类） | 用传播器定位事件根（历元）。见 `event/EstimationRootFinder.hpp:52` |
| `EventException` | `BaseException`（`src/base/foundation/BaseException.hpp`） | 事件子系统异常。见 `event/EventException.hpp:40` |
| `RungeKutta4` | `RungeKutta`（`src/base/propagator/RungeKutta.hpp`） | 无步长控制的定步 RK4 传播器（Nav 专用）。见 `propagator/RungeKutta4.hpp:37` |
| `ErrorModel` | `GmatBase`（`src/base/foundation/GmatBase.hpp`） | 测量噪声/偏置/pass-bias 误差模型。见 `errormodel/ErrorModel.hpp:38` |
| `DataFilter` | `GmatBase`（`src/base/foundation/GmatBase.hpp`） | 二级数据编辑过滤器基类。见 `datafilter/DataFilter.hpp:41` |
| `AcceptFilter` | `DataFilter`（`datafilter/DataFilter.hpp:41`） | 白名单接受过滤器（记录号/抽稀）。见 `datafilter/AcceptFilter.hpp:40` |
| `RejectFilter` | `DataFilter`（`datafilter/DataFilter.hpp:41`） | 黑名单拒绝过滤器（记录号）。见 `datafilter/RejectFilter.hpp:39` |
| 10 个 `*Factory` | `Factory`（`src/base/factory/Factory.hpp`） | 见下表“插件注册与工厂” |

#### 插件注册与工厂

`plugin/GmatPluginFunctions.cpp` 是插件的 C 导出入口，GMAT 运行时按索引向它索要工厂：

- `GetFactoryCount()`（`plugin/GmatPluginFunctions.cpp:64`）：定义了 `USE_DATAFILE_PLUGIN` 宏时返回 10，否则返回 8（第66–70行）；即 DataFile/ObType 两个工厂仅在未启用独立数据文件插件时由本插件提供。
- `GetFactoryPointer(Integer index)`（`plugin/GmatPluginFunctions.cpp:98`）按索引返回：0=`EstimationCommandFactory`(105行)、1=`EstimatorFactory`(109行)、2=`MeasurementModelFactory`(113行)、3=`EstimatorHardwareFactory`(122行)、4=`EstimationDataFilterFactory`(127行)、5=`ErrorModelFactory`(132行)、6=`NavPropagatorFactory`(137行)、7=`DataFileFactory`(143行)、8=`ObTypeFactory`(148行)。
- `GetTriggerManagerCount()` 返回 1（第84行），`GetTriggerManager(0)` 返回 `EventManager`（第178行）。
- `GetMenuEntryCount()` 返回 3（第215行）：GUI 树上新增 `Simulators`/`Estimators`（挂在 `Solvers` 下）与 `Measurements` 三个资源节点（第236–258行）。

各工厂 `CreateXxx` 的 createList（构造器 `creatables` 字符串，均只读确认）：

| 工厂类 | 构造基类类型 | createList（真实行号） | CreateXxx 分支（真实行号） |
| --- | --- | --- | --- |
| `EstimatorFactory` | `Gmat::SOLVER` | `Simulator`/`BatchEstimator`/`BatchEstimatorInv`（`EstimatorFactory.cpp:166-168`） | `CreateSolver`：`Simulator`、`BatchEstimator`、`BatchEstimatorInv`（废弃，转 `BatchEstimator`）（`EstimatorFactory.cpp:101-120`） |
| `EstimationCommandFactory` | `Gmat::COMMAND` | `RunEstimator`/`RunSimulator`（`EstimationCommandFactory.cpp:89-90`） | `CreateCommand`：`RunSimulator`、`RunEstimator`（`EstimationCommandFactory.cpp:61-64`） |
| `MeasurementModelFactory` | `Gmat::MEASUREMENT_MODEL` | `TrackingFileSet`（`MeasurementModelFactory.cpp:104`） | `CreateMeasurementModel`：`TrackingFileSet`（`MeasurementModelFactory.cpp:84-85`） |
| `EstimatorHardwareFactory` | `Gmat::HARDWARE` | `Antenna`/`Transmitter`/`Receiver`/`Transponder`（`EstimatorHardwareFactory.cpp:53-56`） | `CreateHardware`：同名四类（`EstimatorHardwareFactory.cpp:188-195`） |
| `EstimationDataFilterFactory` | `Gmat::DATA_FILTER` | `AcceptFilter`/`RejectFilter`（`EstimationDataFilterFactory.cpp:163-164`） | `CreateDataFilter`：同名两类（`EstimationDataFilterFactory.cpp:207-211`） |
| `ErrorModelFactory` | `Gmat::ERROR_MODEL` | `ErrorModel`（`ErrorModelFactory.cpp:123`） | `CreateErrorModel`：`ErrorModel`（`ErrorModelFactory.cpp:149-150`） |
| `NavPropagatorFactory` | `Gmat::PROPAGATOR` | `RungeKutta4`（`NavPropagatorFactory.cpp:97`） | `CreatePropagator`：`RungeKutta4`（`NavPropagatorFactory.cpp:76-77`） |
| `DataFileFactory` | `Gmat::DATA_FILE` | `DataFile`（仅 TESTING 模式，`DataFileFactory.cpp:82-85`） | `CreateDataFile`：`DataFile`（仅 TESTING，`DataFileFactory.cpp:176-179`） |
| `ObTypeFactory` | `Gmat::OBTYPE` | `GMATInternal`/`GMAT_RampTable`（+`TDM`，`ObTypeFactory.cpp:100-106`） | `CreateObType`：`GMATInternal`→`GmatObType`、`GMAT_RampTable`→`RampTableType`、`TDM`→`TdmObType`（`ObTypeFactory.cpp:203-213`） |
| `SignalModelFactory` | `Factory`（默认构造） | 无 creatables，仅 `GmatType::RegisterType("Signal")`（`SignalModelFactory.cpp:32-35`） | 无 CreateXxx；未被 `GetFactoryPointer` 导出 |

#### 逐文件讲解

##### #### estimator

###### ##### Estimator.hpp / Estimator.cpp

职责一句话：所有估计器的抽象基类，把 Solver 的有限状态机与测量/状态/协方差/报告基础设施粘合在一起。

- `Estimator` 继承 `Solver`（`Estimator.hpp:54`），成员含 `MeasurementManager measManager` 与 `EstimationStateManager esm`（`Estimator.hpp:233-235`）。
- 估计数学量集中于此：信息矩阵 `information`、其逆 `informationInverse`、残差 `residuals`、先验偏差 `x0bar`、状态转移矩阵 `stm`、协方差 `stateCovariance`、笛卡尔→SolveFor 转换阵 `cart2SolvMatrix`、SolveFor→Keplerian 转换阵 `solv2KeplMatrix`（`Estimator.hpp:276-332`）。
- 纯虚接口强制派生类实现：`IsFinalPass()`（第69行）、`Estimate()`（第546行）、`DataFilter()`（第525行）、`WriteReportFileHeaderPart6()`（第606行）、`WriteReportFileSummaryPart1()`（第621行）、`IsIterative()`（第609行）。
- `Initialize()`（`Estimator.cpp:544`）做运行前校验：至少一个传播器、至少一个测量、多传播器下的 EKF/Smoother 限制（第568–585行）；`CompleteInitialization()`（`Estimator.cpp:917`）从 ESM 取 STM/协方差并禁止 Code500/星历传播器参与估计（第923–970行）。
- `CalculateResiduals()`（`Estimator.cpp:4119`）是每历元测量处理入口：先 `FilteringData()` 做二级编辑，再取有效测量模型、计算 O-C、校验 EOP 与介质修正范围。
- 参数表（`Estimator.cpp:115-149`）见“参数表”小节；静态编辑标志位 `NORMAL_FLAG=0 … EGAP_FLAG=256`（`Estimator.cpp:151-160`）用位掩码记录每条观测被何种规则剔除。
- `GetMeasurementWeight()`（`Estimator.cpp:3552`）从测量协方差取权重（最小二乘的 W 对角元来源）。

###### ##### BatchEstimatorBase.hpp / BatchEstimatorBase.cpp

职责一句话：批估计有限状态机的骨架——初始化、推进状态、收敛判定、先验协方差与报告，不实现具体最小二乘数学（`Accumulate()` 为纯虚）。

- 关键成员：`absoluteTolerance`/`relativeTolerance`（收敛容差）、`oldResidualRMS`/`newResidualRMS`/`bestResidualRMS`（残差 RMS 历史）、`useApriori`、`weights`、`inversionType`、`freezeEditing`/`freezeIteration`、`maxConsDivergences`（`BatchEstimatorBase.hpp:120-162`）。
- 构造默认值（`BatchEstimatorBase.cpp:110-127`）：`absoluteTolerance=1.0e-3`、`relativeTolerance=1.0e-4`、`maxConsDivergences=3`、`freezeIteration=4`、`inversionType="Internal"`。
- `AdvanceState()`（`BatchEstimatorBase.cpp:910`）是状态机调度中枢，`switch(currentState)` 依次调用 `CompleteInitialization()/FindTimeStep()/CalculateData()/ProcessEvent()/Accumulate()/Estimate()/CheckCompletion()/RunComplete()`；任何异常捕获后置 `FINISHED` 并重抛（第1009–1013行）。
- `CompleteInitialization()`（`BatchEstimatorBase.cpp:1074`）把信息矩阵与 `x0bar` 清零（第1193–1205行）、缓冲对象并 `MapObjectsToVector()`、计算状态换算阵 `cart2SolvMatrix`/`solv2KeplMatrix`（第1283–1285行）。
- 收敛判定 `TestForConvergence()`（`BatchEstimatorBase.cpp:2032`）实现四条准则：`newResidualRMS <= absoluteTolerance`（绝对容差，第2046行）、`|predictedRMS-bestResidualRMS|/bestResidualRMS <= relativeTolerance`（相对容差，第2057行）、达到 `maxIterations`（第2074行）、连续发散计数达 `maxConsDivergences`（第2082–2102行）。
- `InvertApriori()`（`BatchEstimatorBase.cpp:2358`）对初始协方差求逆得到先验信息矩阵 `Pdx0⁻¹`，奇异时抛 `EstimatorException`。

###### ##### BatchEstimator.hpp / BatchEstimator.cpp

职责一句话：以直接求逆实现 Tapley《Statistical Orbit Determination》第4章批最小二乘（`BatchEstimator.hpp:42-48` 注释明确算法出处）。

- 参数（`BatchEstimator.cpp:57-79`）：`OLSEInitialRMSSigma`(maxResidualMult=3000)、`OLSEMultiplicativeConstant`(constMult=3)、`OLSEAdditiveConstant`(additiveConst=0)、`OLSEUseRMSP`(chooseRMSP=true)、`UseInnerLoopEditing`(useInnerLoop=false)、`ILSEMultiplicativeConstant`(constMultIL=3)、`ILSEMaximumIterations`(maxIterationsIL=15)。
- `Accumulate()`（`BatchEstimator.cpp:889`）核心累加（详见“关键类深读”）：
  ```cpp
  for (UnsignedInt k = 0; k < measStat.residual.size(); ++k) {
     Real ocDiff = measStat.residual[k];  // residual = O - C
     Real weight = measStat.weight[k];
     if (measStat.editFlag == NORMAL_FLAG) {
        for (UnsignedInt i = 0; i < stateSize; ++i) {
           for (UnsignedInt j = 0; j < stateSize; ++j)
              information(i, j) += hMeas[k][i] * hMeas[k][j] * weight; // AᵀWA
           residuals[i] += hMeas[k][i] * weight * ocDiff;              // AᵀWb
        }
     }
  }
  ```
  （`BatchEstimator.cpp:914-934`）——对每条“正常”观测，把 `H̃ᵀ W H̃` 累进信息矩阵、`H̃ᵀ W (O-C)` 累进残差向量。
- `Estimate()`（`BatchEstimator.cpp:1033`）在求解前检查有效观测数不少于求解参数数（第1067行），按 `useApriori` 决定是否叠加先验项（第1129–1145行），调用 `SolveNormalEquations()` 求协方差，再解出 `dx`（第1194–1200行），`estimationStateS[i] += dx[i]`（第1226行），写回对象（第1231–1233行）。
- `SolveNormalEquations()`（`BatchEstimator.cpp:1651`）先 `MatrixFactorization::CompressNormalMatrix()` 剔除全零行/列（第1684行），再按 `inversionType` 选 `Schur`/`Cholesky`/`Internal`（直接 `Inverse()`）三种求逆（第1736–1790行），最后 `ExpandNormalMatrixInverse()` 还原（第1805行）。
- `InnerLoop()`（`BatchEstimator.cpp:1383`）实现内环 σ 编辑：在 `maxIterationsIL` 内反复用 `predictedRMS` 剔除超限记录直至编辑集不变（第1442–1590行）。
- `DataFilter()`（`BatchEstimator.cpp:1835`）实现初始 RMS 过滤（第0次迭代）与外环 σ 编辑（第1次起）：`sqrt(weight)*|O-C| > constMult*sigma+additiveConst` 即剔除（第1874行）。
- `EstimationPartials()`（`BatchEstimator.cpp:1894`）计算 `H̃`：先在测量时刻求偏导，再乘 STM 映射到先验历元，最后经 `cart2SolvMatrix` 转到 SolveFor 坐标（第1961–2005行）。

###### ##### EstimationStateManager.hpp / EstimationStateManager.cpp

职责一句话：估计状态向量的“装配工”，把散布在各对象上的 SolveFor/Consider 参数排序成状态向量，并维护对应 STM 与协方差。

- 继承 `StateManager`（`EstimationStateManager.hpp:50`），内部委托 `PropagationStateManager *psm` 管理随时间演化的分量（第203行）。
- 核心方法：`BuildState()`（`EstimationStateManager.cpp:1129`）调用 `SortVector()` 定状态维数、初始化 STM 为单位阵、从各对象 `GetCovariance(id)` 拼总协方差（第1149–1218行）；`MapObjectsToVector()`（第1558行）/`MapVectorToObjects()`（第1302行）在对象与向量间搬运状态；`MapObjectsToSTM()`（第1797行）/`MapSTMToObjects()` 搬运 STM；`MapObjectsToCovariances()`/`MapCovariancesToObjects()`（第2068行）搬运协方差。
- 状态表达与坐标换算：`GetEstimationState()`（第3240行）返回 SolveFor 态；`CartToSolveForStateConversionDerivativeMatrix()`（第4182行）给出 `[dX/dS]`，`SolveForStateToKeplConversionDerivativeMatrix()` 给出 `[dS/dK]`，供估计器把笛卡尔偏导转换到实际求解参数坐标。
- `HasElementsOfType()`（`EstimationStateManager.hpp:143`）供 `BatchEstimatorBase` 检查是否混入不支持的 `EstimatedParameter`（`BatchEstimatorBase.cpp:1083`）。
- 参与估计的参数类型由对象自身声明（`SetProperty(obj)` 读取对象 `SolveFors`），常见为 `CartesianState`/`KeplerianState`（含 Cr、Cd）、力模型参数、`Bias`/`PassBiases` 等。

###### ##### EstimatorException.hpp / EstimatorException.cpp

职责一句话：估计器层次抛出的异常，前缀 `"Estimator Exception: "`。

- 继承 `BaseException`（`EstimatorException.hpp:42`）；构造器把前缀与细节交给基类（`EstimatorException.cpp:44-45`）。典型用法见 `BatchEstimatorBase.cpp:387,397,484`。

###### ##### Simulator.hpp / Simulator.cpp

职责一句话：生成仿真测量数据的求解器，走 `INITIALIZING→PROPAGATING→CALCULATING→(LOCATING)→SIMULATING→FINISHED` 状态机。

- 继承 `Solver`（`Simulator.hpp:47`）；成员含 `MeasurementManager measManager`（第237行）、`addNoise`（第224行）、`simulationStep`/`nextSimulationEpochGT`（第196–216行）。
- `AdvanceState()`（`Simulator.cpp:1701`）按状态调度，`SIMULATING` 态调 `SimulateData()`（第1755行）。
- `SimulateData()`（`Simulator.cpp:2085`）校验介质修正后 `measManager.WriteMeasurements()` 写数据文件，再 `FindNextSimulationEpoch()` 决定继续或结束（第2093–2118行）。
- `GetTimeStep()`（`Simulator.cpp:392`）返回当前到下一仿真历元的步长，供命令侧 `Propagate()` 使用。
- 参数（`Simulator.hpp:150-160`）：`Measurements`、`Propagator`、`EpochFormat`、`InitialEpoch`、`FinalEpoch`、`MeasurementTimeStep`、`AddNoise`。

##### #### measurementmodel

###### ##### MeasureModel.hpp / MeasureModel.cpp

职责一句话：基于 `Signal` 路径的测量模型基类，负责沿信号路径计算测量值与偏导数、求解光时、应用介质修正。

- 继承 `GmatBase`（`MeasureModel.hpp:60`）；成员含参与者列表 `participants`、信号路径 `signalPaths`、`SignalData` 结果 `theData`、修正类型/模型列表 `correctionTypeList`/`correctionModelList`（第211–244行）。
- 关键接口：`CalculateMeasurement(...)`（第134行，实现于 `MeasureModel.cpp:1416`）、`CalculateMeasurementDerivatives(...)`（第146行，实现于 `MeasureModel.cpp:2108`）、`Initialize()`（第132行，实现于 `MeasureModel.cpp:960`）。
- `SetCorrection()/AddCorrection()`（第159–162行）挂接相对论、ET-TAI、电离层、对流层等修正；`SetProgressReporter()`（第188行）接入 `ProgressReporter` 记录日志。
- 唯一脚本参数 `SIGNAL_PATH`（第262–266行）。

###### ##### GPSPointMeasureModel.hpp / GPSPointMeasureModel.cpp

职责一句话：GPS 单点解测量模型——用 GPS 观测量做逐历元位置解算并输出对状态/参数（含 Cr、Cd）的偏导数。

- 继承 `MeasureModel`（`GPSPointMeasureModel.hpp:58`）；重写 `Initialize()`（第76行，实现于 `GPSPointMeasureModel.cpp:261`）、`CalculateMeasurement()`（第78行，实现于第517行）、`CalculateMeasurementDerivatives()`（第86行，实现于第740行）。
- 私有辅助 `InitializePointModel()`（`GPSPointMeasureModel.cpp:362`）构建点解所需信号；`ModelPointSignalDerivative()` 与 `GetDerivativeWRTState()/WRTC()/WRTCr()/WRTCd()`（`GPSPointMeasureModel.hpp:114-118`）分别求对状态、光速参数、Cr、Cd 的偏导。

##### #### measurement

###### ##### MeasurementData.hpp / MeasurementData.cpp

职责一句话：承载“已计算测量值”的数据结构（近似 struct）。

- 字段（`MeasurementData.hpp:67-194`）覆盖测量类型/名称/唯一 ID、历元、参与者/传感器 ID、测量值 `value`、修正 `correction`、各信号段距离/距离率矢量、收发时刻与位置、可行性 `isFeasible`/`unfeasibleReason`、协方差、Doppler 计数区间、TDRS 专用字段、介质修正值与 HORP 高度/角。
- `CleanUp()`（`MeasurementData.cpp:109`）释放内部堆指针（range/rate 矢量、收发位置）；拷贝构造与赋值做逐字段浅拷贝（第180–335行）。

###### ##### MeasurementException.hpp

职责一句话：测量子系统异常（仅头文件，内联实现）。

- 继承 `BaseException`，前缀 `"Measurement Exception Thrown: "`（`MeasurementException.hpp:52-53`）。

###### ##### MeasurementManager.hpp / MeasurementManager.cpp

职责一句话：估计器/仿真器与测量模型、观测数据、数据文件之间的中介者。

- 成员：测量模型集 `trackingSets`/`adapters`（第154–158行）、观测数据 `observations` 与当前索引 `obsIndex`（第177–179行）、测量结果 `measurements`（第174行）、数据流 `streamList`/`rampTableDataStreamList`（第186–198行）。
- 关键接口：`PrepareForProcessing()`（第69行）、`CalculateMeasurements()`（第75行）、`CalculateDerivatives()`（第76行）、`LoadObservations()`（第109行）、`AdvanceObservation()`（第127行）、`GetValidMeasurementList()`（第106行）、`GetMeasurement()`/`GetObsData()`（第95/125行）、`ProcessEvent()`（第81行）、`SetStatisticsDataFiltersToDataFiles()`（第140行）。
- 在 `BatchEstimatorBase` 中被大量调用（如 `CompleteInitialization` 里 `PrepareForProcessing(false)`，`BatchEstimatorBase.cpp:1145`）。

###### ##### MeasurementModelBase.hpp / MeasurementModelBase.cpp

职责一句话：测量模型与 TrackingFileSet 的公共“工厂可识别”基类（非常薄）。

- 继承 `GmatBase`（`MeasurementModelBase.hpp:44`），构造时以 `Gmat::MEASUREMENT_MODEL` 类型注册（`MeasurementModelBase.cpp:37`）。
- 唯一实质方法是 `GetParmIdFromEstID(Integer id, GmatBase *obj)`（`MeasurementModelBase.cpp:60-62`）：`return id - obj->GetType()*250;`，用于把估计参数 ID 还原为对象本地参数 ID。注意：真正的“测量模型计算接口”（`CalculateMeasurement`/`CalculateMeasurementDerivatives`）位于 `MeasureModel`，而非本类。

###### ##### MediaCorrection.hpp / MediaCorrection.cpp

职责一句话：测量介质修正（电离层/对流层）的插件侧基类。

- 继承 `MediaCorrectionInterface`（`MediaCorrection.hpp:40`），构造时注册 `Gmat::MEDIA_CORRECTION` 类型（`MediaCorrection.cpp:44`）；本身无额外逻辑，具体模型在 `measurement/Ionosphere` 与 `measurement/Troposphere` 子目录（本章其它片段覆盖）。

###### ##### EstimationDefs.hpp

职责一句话：向 `Gmat` 命名空间扩展测量类型与数据源枚举。

- `Gmat::MeasurementType`（第48–104行）：几何（`GEOMETRIC_RANGE/RANGE_RATE/AZ_EL/RA_DEC`，ID 起 7000）、DSN/USN/SN/TDRSS 双向测距与多普勒、光学、自定义（7700–7999）等分段编号。
- `Gmat::MeasurementSource`（第107–119行）：`GMAT_INTERNAL_DATA=3000`、`UNKNOWN_SOURCE`、自定义 3500–3800。

##### #### command

###### ##### RunEstimator.hpp / RunEstimator.cpp

职责一句话：MCS 命令，克隆并驱动 `Estimator` 的有限状态机，完成命令侧传播、事件定位与状态发布。

- 继承 `RunSolver`（`RunEstimator.hpp:51`）；成员 `Estimator *theEstimator`、`EventManager *eventMan`、`eventList` 等（第89–119行）。
- `Initialize()`（`RunEstimator.cpp:375`）支持延迟初始化（第386–392行）：克隆求解器、设 `SetDelayInitialization(false)`、把数据流/ramp 表对象交给 `MeasurementManager`（第446–488行）。
- `PreExecution()`（`RunEstimator.cpp:736`）是真正的装载点：建 propagator 克隆与 `satPropMap`、装载 solve-for 到 ESM、配置外部 STM（Plate/硬件/瞬态力）、初始化 `RunSolver`（第788–1116行）。
- `LoadSolveForsToESM()`（`RunEstimator.cpp:599`）遍历参与者与力模型，把 `SolveFors` 通过 `esm->SetProperty(...)` 装载（第628/677行）。
- `Execute()`（`RunEstimator.cpp:1140`）按 `theEstimator->GetState()` 分派到 `PrepareToEstimate()/Propagate()/Calculate()/LocateEvent()/Estimate()/Accumulate()/CheckConvergence()/Finalize()`。

###### ##### RunSimulator.hpp / RunSimulator.cpp

职责一句话：MCS 命令，克隆并驱动 `Simulator` 状态机完成测量仿真。

- 继承 `RunSolver`（`RunSimulator.hpp:53`）；成员 `Simulator *theSimulator`、`EventManager *eventMan` 等（第83–104行）。
- `Initialize()`（`RunSimulator.cpp:296`）克隆模拟器、设置数据流/ramp 表、准备 propagator（第315–494行）。
- `Execute()`（`RunSimulator.cpp:555`）按状态分派 `PrepareToSimulate()/Propagate()/Calculate()/LocateEvent()/Simulate()/Finalize()`，最后调用 `theSimulator->AdvanceState()`（第649行）。
- `Propagate()`（`RunSimulator.cpp:991`）用 `theSimulator->GetTimeStep()` 推进；`LocateEvent()`（第1080行）与 `EventManager` 协作定位事件；`Finalize()`（第1340行）调用 `measman->ProcessingComplete()`。

##### #### reporter

###### ##### ProgressReporter.hpp / ProgressReporter.cpp

职责一句话：Nav 子系统进度/日志报告器，把文本写到文件或消息接口。

- 成员：`buffer` 与 `bufferTrigger=16383`（16KB 阈值触发落盘，`ProgressReporter.cpp:37`）、日志级别映射 `levels`（Everything=0/Verbose=1/NotFound=32767，第45–50行）、子系统级 `subsystemLogLevel`（第80行）。
- `Initialize()`（第97行）在无文件名时切到消息接口；`WriteData()`（第123行）/`Flush()`（第265行）缓冲写；`AddLogLevel()`/`SetLogLevel()` 管理日志级别。注意部分重载 `WriteData(label,value,...)`/`WriteDataArray(...)` 目前为未实现占位（第139–162行）。

##### #### event

###### ##### Event.hpp / Event.cpp

职责一句话：事件基类，监控传播轨迹以定位临界/极值时刻。

- 继承 `GmatBase`（`Event.hpp:67`）；`EventStatus` 枚举 `SEEKING/ZERO_BRACKETED/EXTREMA_BRACKETED/ITERATING/LOCATED/UNKNOWN_STATUS`（第44–52行）。
- 纯虚 `Evaluate()`（第78行）由派生类给出事件函数值；`CheckStatus()`（第87行）推进定位状态；环形缓冲 `epoch/value/derivative` 与 `depth`（第108–115行）保存采样以做求根；`FixState()`/`GetFixedEpoch()` 固定事件计算中的状态（第79–81行）。

###### ##### EventData.hpp / EventData.cpp

职责一句话：事件参与者的状态快照结构。

- 字段（`EventData.hpp:56-77`）：`participantName/Index`、`fixedState`、惯性系原点 `cs_origin`、`epoch`、J2000Eq 位置/速度、惯性→体坐标旋转阵 `rInertial2obj`、状态转移矩阵 `stm`。

###### ##### EventManager.hpp / EventManager.cpp

职责一句话：事件触发器/管理器，内含求根器以定位事件历元。

- 继承 `TriggerManager`（`EventManager.hpp:43`）；成员 `ObjectArray events`、`EstimationRootFinder locater`（第72–74行）。
- 接口：`SetObject()/ClearObject()`（第57–58行）、`CheckForTrigger()`/`LocateTrigger()`（第59–60行）、`FindRoot()`/`EvaluateEvent()`（第64–65行）；被 `RunEstimator`/`RunSimulator` 的事件定位流程调用。

###### ##### EstimationRootFinder.hpp / EstimationRootFinder.cpp

职责一句话：用传播器做事件求根，返回事件发生的历元。

- 成员 `PropSetup *propagator`、`maxAttempts`、`startState`、卫星/编队缓冲（`EstimationRootFinder.hpp:69-80`）。
- 接口 `SetPropSetup()`（第63行）、`FixState()`（第64行）、`Locate(ObjectArray&)`（第65行）、内部 `FindRoot()`（第82行）。

###### ##### EventException.hpp / EventException.cpp

职责一句话：事件子系统异常，前缀 `"Event Exception: "`（`EventException.hpp:42` 继承 `BaseException`）。

##### #### propagator

###### ##### RungeKutta4.hpp / RungeKutta4.cpp

职责一句话：无步长控制的经典四阶 Runge-Kutta 传播器，供 Nav 代码做快速定步传播。

- 继承 `RungeKutta`（`RungeKutta4.hpp:37`）；重写 `EstimateError()`/`AdaptStep()`（第45–46行，对定步长 RK4 基本为 no-op）与 `Clone()`（第47行）；`SetCoefficients()`（第50行）填 RK4 系数。

##### #### errormodel

###### ##### ErrorModel.hpp / ErrorModel.cpp

职责一句话：定义测量噪声/偏置与 pass-bias 的误差模型。

- 继承 `GmatBase`（`ErrorModel.hpp:38`）；成员 `noiseSigma`、`bias`、`biasSigma`、`timeGap`、`passBiases`（第159–176行）。
- 估计接口：`IsEstimationParameterValid()`/`GetEstimationParameterSize()`/`GetEstimationParameterValue()`/`HasParameterCovariances()`/`GetParameterCovariances()`（第130–135行），使其可作为 solve-for 来源。
- pass-bias 支持：`GetPassBiasStartEpoches()`/`GetBiasPassNumber()`/`GetPassBias()`（第137–145行），被 `BatchEstimatorBase::GetProgressString()` 用于打印 `PassBiases` 时间范围（`BatchEstimatorBase.cpp:1714-1717`）。
- 参数：`Type`、`NoiseSigma`、`Bias`、`BiasSigma`、`PassBiases`、`SolveFors`、`ModelId`（第183–195行）。

##### #### datafilter

###### ##### DataFilter.hpp / DataFilter.cpp

职责一句话：二级数据编辑过滤器基类。

- 继承 `GmatBase`（`DataFilter.hpp:41`）；过滤维度：`fileNames`/`observers`/`trackers`/`dataTypes`/`epochFormat`+`initialEpoch`/`finalEpoch`/`strands`（第121–149行）。
- 核心 `FilteringData(ObservationData*, Integer& rejectedReason, Integer obDataId)`（第112–113行），由 `Estimator::CalculateResiduals()` 调用（`Estimator.cpp:4133`）。
- 判定辅助：`HasFile()/HasObserver()/HasTracker()/HasDataType()/IsInTimeWindow()`（第191–199行）。
- 参数：`Filenames`、`ObservedObjects`、`Trackers`、`DataTypes`、`EpochFormat`、`InitialEpoch`、`FinalEpoch`、`Strands`（第157–168行）。

###### ##### AcceptFilter.hpp / AcceptFilter.cpp

职责一句话：白名单式接受过滤器，按记录号或抽稀频率保留数据。

- 继承 `DataFilter`（`AcceptFilter.hpp:40`）；额外成员 `recNumbers`/`recNumRanges`/`allRecNumbers`、`thinMode`/`thinningFrequency`（第101–104行）。
- 参数：`ThinMode`、`ThinningFrequency`、`RecordNums`（第127–133行）；`IsThin()`（第121行）判断是否满足抽稀比例。

###### ##### RejectFilter.hpp / RejectFilter.cpp

职责一句话：黑名单式拒绝过滤器，按记录号剔除数据。

- 继承 `DataFilter`（`RejectFilter.hpp:39`）；成员 `recNumbers`/`recNumRanges`/`allRecNumbers`（第84–87行）；参数仅 `RecordNums`（第93–97行）。

##### #### factory

各工厂职责一句话与 createList 见“插件注册与工厂”表格，逐文件补充要点：

- `EstimatorFactory`：`CreateSolver()` 兼容废弃名 `BatchEstimatorInv`（`EstimatorFactory.cpp:105-120`）。
- `EstimationCommandFactory`：`Factory(Gmat::COMMAND)`，产出 `RunSimulator`/`RunEstimator` 命令。
- `MeasurementModelFactory`：`Factory(Gmat::MEASUREMENT_MODEL)`，产出 `TrackingFileSet`（真正的物理测量模型在 adapter 层组装，不在本工厂）。
- `EstimatorHardwareFactory`：`Factory(Gmat::HARDWARE)`，产出 Antenna/Transmitter/Receiver/Transponder，并注册 `Sensor`/`RFHardware` 类型（`EstimatorHardwareFactory.cpp:59-61`）。
- `EstimationDataFilterFactory`：`Factory(Gmat::DATA_FILTER)`，产出 AcceptFilter/RejectFilter。
- `ErrorModelFactory`：`Factory(Gmat::ERROR_MODEL)`，产出 ErrorModel。
- `NavPropagatorFactory`：`Factory(Gmat::PROPAGATOR)`，产出 RungeKutta4。
- `DataFileFactory`：`Factory(Gmat::DATA_FILE)`，仅 TESTING 模式产出 DataFile。
- `ObTypeFactory`：`Factory(Gmat::OBTYPE)`，产出 GMATInternal/GMAT_RampTable/TDM 观测类型。
- `SignalModelFactory`：仅 `GmatType::RegisterType("Signal")`，无 creatables 也未导出（`SignalModelFactory.cpp:32-35`）。

##### #### include

###### ##### estimation_defs.hpp

职责一句话：跨平台 DLL 导入/导出宏。

- 定义 `ESTIMATION_API`：Windows+MSVC+`_DYNAMICLINK` 下按 `ESTIMATION_EXPORTS` 展开为 `__declspec(dllexport/dllimport)`，否则为空（`estimation_defs.hpp:37-76`）。与 `src/base/CMakeLists.txt:166` 的 `DEFINE_SYMBOL "ESTIMATION_EXPORTS"` 对应。

##### #### plugin

###### ##### GmatPluginFunctions.hpp / GmatPluginFunctions.cpp

职责一句话：插件的 C 导出入口与 GUI 资源注册（详见“插件注册与工厂”）。

- 导出 `GetFactoryCount/GetTriggerManagerCount/GetFactoryPointer/GetTriggerManager/SetMessageReceiver/GetMenuEntryCount/GetMenuEntry`（`GmatPluginFunctions.hpp:43-51`）。
- 头文件末尾含 Doxygen `\mainpage`，说明本插件设计文档指向 GMAT 架构规范第2卷（`GmatPluginFunctions.hpp:58-80`）。

#### 关键类深读

##### BatchEstimatorBase / BatchEstimator：批处理最小二乘实现结构

`BatchEstimatorBase` 提供状态机与收敛骨架，`BatchEstimator` 填充最小二乘数学。算法对应 Tapley, Schutz & Born《Statistical Orbit Determination》(2004) 第4章（`BatchEstimator.hpp:42-48`）。

**正规方程与加权最小二乘对应关系**。估计问题为

> **Δx = (Aᵀ W A)⁻¹ Aᵀ W b**，其中 A=H̃（测量对状态的偏导矩阵），W 为测量权重（对角元 = 1/σ²），b = O−C（观测减计算残差）。

代码对应（`BatchEstimator.cpp`）：

1. **AᵀWA（信息矩阵）**：`information(i,j) += hMeas[k][i] * hMeas[k][j] * weight`（第926行）——`hMeas` 是已映射到 SolveFor 坐标、并回推到先验历元的 `H̃` 行向量，`weight` 是第 k 个测量分量的 W 对角元；`information` 即 `Λ = AᵀWA`。
2. **AᵀWb（残差向量）**：`residuals[i] += hMeas[k][i] * weight * ocDiff`（第931行），`ocDiff = O − C`（第916行）。
3. **求逆得协方差**：`SolveNormalEquations(information, informationInverse)`（第1164行）——`informationInverse = Λ⁻¹ = P`（估计误差协方差）。
4. **解出状态增量**：`delta += informationInverse(i,j) * residuals(j)`（第1198行），即 `dx = Λ⁻¹ · N = (AᵀWA)⁻¹AᵀWb`。
5. **状态更新**：`estimationStateS[i] += dx[i]`（第1226行）。

**先验（apriori）项**。若 `UseInitialCovariance=true`，`Estimate()` 先把先验协方差求逆加到信息矩阵并修正残差（`BatchEstimator.cpp:1129-1145`）：

```cpp
Rmatrix Pdx0_inv;
InvertApriori(Pdx0_inv);              // Pdx0⁻¹
information = information + Pdx0_inv; // Λ += P₀⁻¹
for (...) residuals[i] += Pdx0_inv(i,j) * x0bar[j]; // N += P₀⁻¹·(x̄₀−x)
```

`InvertApriori()`（`BatchEstimatorBase.cpp:2358`）即求 `Pdx0⁻¹`；`x0bar` 在每轮迭代前更新为 `initialEstimationStateS[j] − currState[j]`（`BatchEstimatorBase.cpp:1539`），对应 GTDS MathSpec 的 `δX̄` 项。构造默认 `useApriori=false`（`BatchEstimatorBase.cpp:118`）。

**残差累积 / WRMS**。`CalculateWRMS()`（`BatchEstimator.cpp:1309`）按 `sqrt( Σ weight·(O−C−H̃·dx)² / count )` 计算加权 RMS 及其预测值（`predictedRMS`），供收敛判据使用；`CalculateResidualChange()`（第1366行）给出线性化残差变化 `H̃·dx`。

**迭代收敛判据**。`TestForConvergence()`（`BatchEstimatorBase.cpp:2032`）：
- 绝对容差：`newResidualRMS <= absoluteTolerance`（第2046行，默认 1e-3）；
- 相对容差：`|predictedRMS − bestResidualRMS|/bestResidualRMS <= relativeTolerance`（第2057行，默认 1e-4）；
- 最大迭代：`iterationsTaken == maxIterations−1`（第2074行，`Estimator` 默认 `maxIterations=15`，`Estimator.cpp:220-221`）；
- 连续发散：`newResidualRMS > oldResidualRMS` 累计，达 `maxConsDivergences`（默认 3）判发散（第2082–2102行）。

**正规矩阵降阶**。`SolveNormalEquations()`（`BatchEstimator.cpp:1651`）先用 `MatrixFactorization::CompressNormalMatrix(infMatrix, ..., 1e-50)` 剔除全零行/列（第1684行），避免无信息参数（如未观测 Bias）导致求逆奇异，求解后再 `ExpandNormalMatrixInverse()` 还原（第1805行）；被剔除参数会打印 `Performed normal matrix reduction for ...`（第1699行）。

##### EstimationStateManager：状态向量/协方差矩阵组织

`BuildState()`（`EstimationStateManager.cpp:1129`）是装配核心：`stateSize = SortVector()` 排序并确定维数（第1150行，无 solve-for 时抛异常第1156行），按 `stateMap[index]` 逐项设置元素属性（对象全名 + 元素名 + 下标，第1179–1187行），STM 初始化为单位阵（第1189–1195行），协方差从各对象 `GetCovariance(id)` 的子块拼装（第1199–1218行）。`MapObjectsToVector()`/`MapVectorToObjects()`（第1558/1302行）在对象与向量间搬运；`MapObjectsToSTM()`/`MapSTMToObjects()`（第1797行）搬运 STM；`MapObjectsToCovariances()`/`MapCovariancesToObjects()`（第2068行）搬运协方差。参与估计的参数类型由各对象 `SolveFors` 声明（`RunEstimator::LoadSolveForsToESM()` 装载，`RunEstimator.cpp:599`）：航天器状态（Cartesian/Keplerian）、力模型参数（Cr、Cd、AtmosDensity 等）、测量 Bias/PassBiases、Plate/硬件参数、瞬态力参数等。坐标换算由 `CartToSolveForStateConversionDerivativeMatrix()`（第4182行）与 `SolveForStateToKeplConversionDerivativeMatrix()` 提供。

##### MeasurementModelBase：测量模型基类接口

注意 `MeasurementModelBase` 只是工厂用的极薄基类（`MeasurementModelBase.hpp:44` 继承 `GmatBase`，仅有 `GetParmIdFromEstID()`，`MeasurementModelBase.cpp:60-62`）。真正的“测量模型计算接口”在 `MeasureModel`：
- `Initialize()`（`MeasureModel.cpp:960`）准备传播器与信号路径；
- `CalculateMeasurement(withEvents, withMediaCorrection, forObservation, rampTB, forSimulation, atTimeOffset, forStrand)`（`MeasureModel.hpp:134`，实现于 `MeasureModel.cpp:1416`）沿每条 Signal 路径算测量值并写 `MeasurementData`；
- `CalculateMeasurementDerivatives(obj, id, measTime, ...)`（`MeasureModel.hpp:146`，实现于 `MeasureModel.cpp:2108`）返回对状态/参数的偏导 `theDataDerivatives`；
- 参数/参与状态映射：`SIGNAL_PATH` 定义参与测量建模的对象与顺序（`MeasureModel.hpp:262-266`），`participants`/`signalPaths`/`theData` 保存路径与结果（第212–224行）。

##### Estimator / Simulator：Initialize / Estimate 流程

`Estimator` 继承 `Solver`（`Estimator.hpp:54`，`src/base/solver/Solver.hpp`）。`RunEstimator` 命令先 `Clone()` 出求解器并 `SetDelayInitialization(false)`（`RunEstimator.cpp:424-429`），随后 `Initialize()`（`Estimator.cpp:544`）做校验，`CompleteInitialization()`（第917行）取 STM/协方差。进入 `AdvanceState()`（`BatchEstimatorBase.cpp:910`）后，`BatchEstimator::Estimate()`（`BatchEstimator.cpp:1033`）每轮执行：累计 → 求逆 → 解 dx → 更新状态 → `CHECKINGRUN` 判收敛，收敛则 `FINISHED`，`Finalize()`（`BatchEstimatorBase.cpp:1030`）把 `informationInverse` 写回协方差并 `esm.MapCovariancesToObjects()`。

`Simulator` 同样继承 `Solver`（`Simulator.hpp:47`），但状态机多一个 `SIMULATING` 态：`AdvanceState()`（`Simulator.cpp:1701`）在 `SIMULATING` 调 `SimulateData()`（第1755行）→ `measManager.WriteMeasurements()` 写数据，再 `FindNextSimulationEpoch()` 推进或结束。

#### 参数表

**`Estimator`（`Estimator.cpp:115-149`）**：

| 参数名 | 类型 | 单位/默认值 | 说明 |
| --- | --- | --- | --- |
| `Measurements` | OBJECTARRAY | — | 参与估计的测量模型/跟踪文件集 |
| `AddSolveFor` | STRINGARRAY | — | 额外 solve-for 字符串 |
| `Propagator` | OBJECTARRAY | — | 推进轨道的传播器 |
| `EstimationEpochFormat` | STRING | `FromParticipants` | 估计历元格式 |
| `EstimationEpoch` | STRING | `FromParticipants` | 估计历元 |
| `PredictTimeSpan` | REAL | 0.0 | 超出最后测量继续外推时长（秒） |
| `AddPredictToMatlabFile` | BOOLEAN | false | 是否把外推段写入 .mat |
| `ShowAllResiduals` | ON/OFF | true | 是否显示全部残差 |
| `AddResidualsPlot` | STRINGARRAY | — | 追加残差图 |
| `DataFilters` | STRINGARRAY | — | 二级数据过滤器列表 |
| `MatlabFile` | FILENAME | — | MATLAB 输出文件 |
| `DataFile` | FILENAME | — | JSON 输出文件 |
| `DataFileStyle` | STRING | — | 数据文件风格 |

**`BatchEstimatorBase`（`BatchEstimatorBase.cpp:71-97`，默认值见构造 110-127）**：

| 参数名 | 类型 | 单位/默认值 | 说明 |
| --- | --- | --- | --- |
| `AbsoluteTol` | REAL | 1.0e-3 | 绝对收敛容差（对 WRMS） |
| `RelativeTol` | REAL | 1.0e-4 | 相对收敛容差（对 RMS 变化比，取值 (0,1]） |
| `UseInitialCovariance` | BOOLEAN | false | 是否叠加先验协方差项 |
| `InversionAlgorithm` | STRING | `Internal` | 求逆算法：`Internal`/`Schur`/`Cholesky` |
| `MaxConsecutiveDivergences` | INTEGER | 3 | 判定发散的最大连续发散轮数 |
| `ResetBestRMSIfDiverging` | BOOLEAN | false | 发散时是否重置 best RMS（GMT-5711） |
| `FreezeMeasurementEditing` | BOOLEAN | false | 是否冻结测量编辑 |
| `FreezeIteration` | INTEGER | 4 | 冻结编辑的起始迭代号 |
| `ConvergentStatus` | STRING（只读） | — | 收敛状态文本（`IsParameterReadOnly` 见 `BatchEstimatorBase.cpp:337-343`） |

**`BatchEstimator`（`BatchEstimator.cpp:57-79`，默认值见构造 91-101）**：

| 参数名 | 类型 | 单位/默认值 | 说明 |
| --- | --- | --- | --- |
| `OLSEInitialRMSSigma` | REAL | 3000.0 | 初始 RMS σ 过滤阈值（第0轮） |
| `OLSEMultiplicativeConstant` | REAL | 3.0 | 外环 σ 编辑乘性系数 k |
| `OLSEAdditiveConstant` | REAL | 0.0 | 外环 σ 编辑加性常数 K |
| `OLSEUseRMSP` | BOOLEAN | true | 用预测 RMS（true）还是当前 RMS（false） |
| `UseInnerLoopEditing` | BOOLEAN | false | 是否启用内环（ILSE）编辑 |
| `ILSEMultiplicativeConstant` | REAL | 3.0 | 内环 σ 编辑乘性系数 |
| `ILSEMaximumIterations` | INTEGER | 15 | 内环最大迭代数 |

#### 与 core 的扩展点

插件类继承的 core 基类（相对 `src/base/`）与需要重写的虚函数：

| 插件类 | core 基类（相对路径） | 需重写/实现的虚函数 |
| --- | --- | --- |
| `Estimator` | `solver/Solver.hpp` | 纯虚：`IsFinalPass()`、`Estimate()`、`DataFilter()`、`WriteReportFileHeaderPart6()`、`WriteReportFileSummaryPart1()`、`IsIterative()`；常规：`Initialize()`/`CompleteInitialization()`/`Finalize()`/`TakeAction()`/参数访问器 |
| `BatchEstimatorBase` | `estimator/Estimator.hpp` | 纯虚 `Accumulate()`（`BatchEstimatorBase.hpp:206`）；`AdvanceState()`/`Initialize()`/`Finalize()`/`TestForConvergence()`/`InvertApriori()` |
| `Simulator` | `solver/Solver.hpp` | `Initialize()`/`AdvanceState()`/`Finalize()`/`GetTimeStep()`/`SetSolverResults()` |
| `EstimationStateManager` | `foundation/StateManager.hpp` | `BuildState()`/`MapObjectsToVector()`/`MapVectorToObjects()`/`MapObjectsToSTM()`/`MapSTMToObjects()`/`MapObjectsToCovariances()`/`MapCovariancesToObjects()`/`SetProperty()` 等 |
| `MeasurementModelBase` | `foundation/GmatBase.hpp` | 参数/引用对象访问器；计算接口在 `MeasureModel` |
| `MeasureModel` | `foundation/GmatBase.hpp` | `Initialize()`/`CalculateMeasurement()`/`CalculateMeasurementDerivatives()`/`SetCorrection()` 等 |
| `MediaCorrection` | `solarsys/MediaCorrectionInterface.hpp` | 具体介质修正由 Ionosphere/Troposphere 子类实现 |
| `ErrorModel`/`DataFilter` | `foundation/GmatBase.hpp` | `Initialize()`/`Finalize()`、估计参数接口（`IsEstimationParameterValid` 等）、`FilteringData()` |
| `Event` | `foundation/GmatBase.hpp` | 纯虚 `Evaluate()`、`Initialize()`/`CheckStatus()`/`FixState()` |
| `EventManager` | `foundation/TriggerManager.hpp` | `SetObject()`/`ClearObject()`/`CheckForTrigger()`/`LocateTrigger()`/`Clone()` |
| `RungeKutta4` | `propagator/RungeKutta.hpp` | `EstimateError()`/`AdaptStep()`/`Clone()`/`SetCoefficients()` |
| `RunEstimator`/`RunSimulator` | `command/RunSolver.hpp` | `Initialize()`/`Execute()`/`RunComplete()`/`TakeAction()`/`GetNext()`/`SetPropagationProperties()` 等 |
| `*Factory` | `factory/Factory.hpp` | `CreateObject()`/`CreateXxx()`；`EventManager` 额外实现 `TriggerManager` 接口 |

#### 文件清单附录

（相对 `plugins/EstimationPlugin/src/base/`；共 76 个代码文件，全部已读确认）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `estimator/Estimator.hpp/.cpp` | 估计器抽象基类与状态/协方差/报告基础设施 | `Estimator`；`Initialize/CompleteInitialization/Finalize/CalculateResiduals/GetMeasurementWeight` |
| `estimator/BatchEstimatorBase.hpp/.cpp` | 批估计状态机与收敛判据 | `BatchEstimatorBase`；`AdvanceState/CompleteInitialization/TestForConvergence/InvertApriori` |
| `estimator/BatchEstimator.hpp/.cpp` | 直接求逆批最小二乘 | `BatchEstimator`；`Accumulate/Estimate/SolveNormalEquations/InnerLoop/DataFilter/EstimationPartials/CalculateWRMS` |
| `estimator/EstimationStateManager.hpp/.cpp` | 状态向量/STM/协方差装配与坐标换算 | `EstimationStateManager`；`BuildState/MapObjectsToVector/MapVectorToObjects/MapObjectsToSTM/CartToSolveForStateConversionDerivativeMatrix` |
| `estimator/EstimatorException.hpp/.cpp` | 估计异常 | `EstimatorException` |
| `estimator/Simulator.hpp/.cpp` | 测量仿真求解器 | `Simulator`；`Initialize/AdvanceState/SimulateData/GetTimeStep` |
| `measurementmodel/MeasureModel.hpp/.cpp` | 基于 Signal 的测量模型基类 | `MeasureModel`；`Initialize/CalculateMeasurement/CalculateMeasurementDerivatives/SetCorrection` |
| `measurementmodel/GPSPointMeasureModel.hpp/.cpp` | GPS 单点解测量模型 | `GPSPointMeasureModel`；`Initialize/InitializePointModel/CalculateMeasurement/CalculateMeasurementDerivatives` |
| `measurement/MeasurementData.hpp/.cpp` | 已计算测量值结构 | `MeasurementData`；`CleanUp` |
| `measurement/MeasurementException.hpp` | 测量异常（内联） | `MeasurementException` |
| `measurement/MeasurementManager.hpp/.cpp` | 测量/观测中介者 | `MeasurementManager`；`PrepareForProcessing/CalculateMeasurements/CalculateDerivatives/LoadObservations/AdvanceObservation` |
| `measurement/MeasurementModelBase.hpp/.cpp` | 测量模型工厂基类 | `MeasurementModelBase`；`GetParmIdFromEstID` |
| `measurement/MediaCorrection.hpp/.cpp` | 介质修正基类 | `MediaCorrection` |
| `measurement/EstimationDefs.hpp` | 测量类型/数据源枚举 | `Gmat::MeasurementType/MeasurementSource` |
| `command/RunEstimator.hpp/.cpp` | 估计驱动命令 | `RunEstimator`；`Initialize/PreExecution/Execute/LoadSolveForsToESM` |
| `command/RunSimulator.hpp/.cpp` | 仿真驱动命令 | `RunSimulator`；`Initialize/Execute/Propagate/LocateEvent/Simulate` |
| `reporter/ProgressReporter.hpp/.cpp` | Nav 进度报告 | `ProgressReporter`；`Initialize/WriteData/Flush/SetLogLevel` |
| `event/EstimationRootFinder.hpp/.cpp` | 事件求根 | `EstimationRootFinder`；`Locate/FindRoot/FixState` |
| `event/Event.hpp/.cpp` | 事件基类 | `Event`；`Evaluate/CheckStatus/FixState` |
| `event/EventData.hpp/.cpp` | 事件参与者状态快照 | `EventData` |
| `event/EventException.hpp/.cpp` | 事件异常 | `EventException` |
| `event/EventManager.hpp/.cpp` | 事件管理器/触发器 | `EventManager`；`SetObject/CheckForTrigger/LocateTrigger/FindRoot` |
| `propagator/RungeKutta4.hpp/.cpp` | Nav 定步 RK4 传播器 | `RungeKutta4`；`EstimateError/AdaptStep/SetCoefficients` |
| `errormodel/ErrorModel.hpp/.cpp` | 测量误差模型 | `ErrorModel`；`GetPassBias/GetEstimationParameterValue` |
| `datafilter/DataFilter.hpp/.cpp` | 二级数据过滤基类 | `DataFilter`；`FilteringData/HasFile/HasObserver/HasTracker/IsInTimeWindow` |
| `datafilter/AcceptFilter.hpp/.cpp` | 接受过滤器 | `AcceptFilter`；`FilteringData/IsThin` |
| `datafilter/RejectFilter.hpp/.cpp` | 拒绝过滤器 | `RejectFilter`；`FilteringData` |
| `factory/DataFileFactory.hpp/.cpp` | DataFile 工厂 | `DataFileFactory` |
| `factory/ErrorModelFactory.hpp/.cpp` | ErrorModel 工厂 | `ErrorModelFactory` |
| `factory/EstimationCommandFactory.hpp/.cpp` | 命令工厂 | `EstimationCommandFactory` |
| `factory/EstimationDataFilterFactory.hpp/.cpp` | 数据过滤器工厂 | `EstimationDataFilterFactory` |
| `factory/EstimatorFactory.hpp/.cpp` | 求解器工厂 | `EstimatorFactory` |
| `factory/EstimatorHardwareFactory.hpp/.cpp` | 硬件工厂 | `EstimatorHardwareFactory` |
| `factory/MeasurementModelFactory.hpp/.cpp` | 测量模型工厂 | `MeasurementModelFactory` |
| `factory/NavPropagatorFactory.hpp/.cpp` | Nav 传播器工厂 | `NavPropagatorFactory` |
| `factory/ObTypeFactory.hpp/.cpp` | 观测类型工厂 | `ObTypeFactory` |
| `factory/SignalModelFactory.hpp/.cpp` | Signal 类型注册 | `SignalModelFactory` |
| `include/estimation_defs.hpp` | DLL 导入/导出宏 | `ESTIMATION_API` |
| `plugin/GmatPluginFunctions.hpp/.cpp` | 插件 C 导出入口与 GUI 资源 | `GetFactoryCount/GetFactoryPointer/GetTriggerManager/GetMenuEntry` |

### 13.6 EstimationPlugin（下）：测量 I/O、硬件与信号链路

**目录**：`plugins/EstimationPlugin/`（本小节聚焦 `src/base/` 下的 `adapter/`、`hardware/`、`signal/`、`measurement/Ionosphere/`、`measurement/Troposphere/`、`measurementfile/`、`tdmReader/`、`trackingfile/` 以及 `swig/` 绑定，共约 100 个 `.hpp/.cpp` 文件 + 5 个 SWIG 文件）

#### 目的与职责

本小节覆盖 EstimationPlugin 中"测量数据从文件流进 GMAT、经物理模型算成可比较的观测值"的整条链路。数据流大致是：

1. **文件层**（`measurementfile/` + `tdmReader/`）：`DataFile` 是脚本可见的测量数据流容器，它持有 `ObType` 派生流对象；`GmatObType`（GMAT 内部 `.gmd` 格式）、`TdmObType`（CCSDS TDM XML 格式，经 Xerces 解析）、`B3_obtype`（B3 观测格式）、`RampTableType`（频率斜坡表）各自把磁盘记录读成统一的 `ObservationData` / `RampTableData` 结构。
2. **适配层**（`adapter/`）：`TrackingDataAdapter` 及其 25 个派生类把测量模型（`MeasureModel`）算出的原始物理量按观测类型做单位换算、叠加介质修正/硬件延迟/噪声/偏差，产出与观测文件同量纲的 `MeasurementData`（C 值），供估计器与模拟器使用。
3. **物理信号层**（`signal/`）：`SignalBase` 以链表组织"发射→接收"的信号路径，`PhysicalSignal` 在路径上做光时迭代、相对论/ET-TAI 修正、介质修正与硬件延迟；`SignalData`/`SignalDataCache` 是信号路径数据的载体与缓存。
4. **硬件层**（`hardware/`）：`Antenna/Sensor/RFHardware/Transmitter/Receiver/Transponder/Oscillator/Signal` 描述测站与航天器的射频链路，为信号计算提供频率、硬件延迟与误差模型。
5. **介质修正层**（`measurement/Ionosphere/`、`measurement/Troposphere/`）：`Ionosphere`（IRI2007 / TRK-2-23）与 `Troposphere`（HopfieldSaastamoinen / Marini / TRK-2-23）给出距离、仰角、时延三个方向的折射修正。
6. **汇总层**（`trackingfile/`）：`TrackingFileSet` 把脚本里的 `TrackingConfig` 与 `DataFile` 组装成一组 `TrackingDataAdapter`，是估计/模拟的入口对象；`TFSMagicNumbers` 单例负责给每个"信号节点数 + 测量类型"组合分配稳定的整数 magic number（`.gmd` 文件里用它标识测量类型）。

#### 导出类清单

以下基类均经 `read` 确认继承关系（`相对路径:行号` 为类声明行）：

| 类名 | 基类 | 职责 |
|---|---|---|
| `TrackingDataAdapter` | `MeasurementModelBase`（`adapter/TrackingDataAdapter.hpp:63`） | 所有测量适配器的基类，把测量模型原始量换算成观测格式的 C 值 |
| `RangeAdapterKm` | `TrackingDataAdapter`（`adapter/RangeAdapterKm.hpp:39`） | 距离类（km）适配器的共同基类，叠加修正/噪声/偏差 |
| `AngleAdapterDeg` | `TrackingDataAdapter`（`adapter/AngleAdapterDeg.hpp:41`） | 角度类（deg）适配器的共同基类，rad→deg 换算 |
| `GPSAdapter` | `TrackingDataAdapter`（`adapter/GPSAdapter.hpp:42`） | GPS 位置矢量（`GPS_PosVec`）适配器 |
| 其余 22 个 adapter | 见 §13.6.3 表 | 各自处理一种观测类型（距离/多普勒/角度/TDRS） |
| `Hardware` | `GmatBase`（core `src/base/hardware/Hardware.hpp:59`） | core 侧硬件基类（本插件未改动） |
| `Imager` | `Hardware`（core `src/base/hardware/Imager.hpp:38`） | core 侧带视场（FOV）硬件中间类 |
| `Antenna` | `Imager`（`hardware/Antenna.hpp:33`） | 天线：延迟 + 相位中心位置 |
| `Sensor` | `Imager`（`hardware/Sensor.hpp:42`） | 传感器基类：持有 `Signal` 与硬件延迟 |
| `RFHardware` | `Sensor`（`hardware/RFHardware.hpp:44`） | 射频硬件基类：关联主天线 |
| `Transmitter` | `RFHardware`（`hardware/Transmitter.hpp:42`） | 发射机：频率模型/频段/频率多项式 |
| `Receiver` | `RFHardware`（`hardware/Receiver.hpp:35`） | 接收机：中心频率/带宽/误差模型 |
| `Transponder` | `RFHardware`（`hardware/Transponder.hpp:35`） | 转发器：输入/输出频率模型 + 转发比 |
| `Oscillator` | `Transmitter`（`hardware/Oscillator.hpp:39`） | 振荡器：频率漂移 + 频率多项式（Taylor 级数） |
| `Signal` | 无（独立类，`hardware/Signal.hpp:36`） | 传感器信号的最小值对象（epoch + value） |
| `SignalBase` | `GmatBase`（`signal/SignalBase.hpp:57`） | 信号路径链表节点基类 |
| `PhysicalSignal` | `SignalBase`（`signal/PhysicalSignal.hpp:50`） | 瞬时信号：光时/介质/相对论/硬件延迟计算 |
| `PassivePhysicalSignal` | `PhysicalSignal`（`signal/PassivePhysicalSignal.hpp:35`） | 无硬件延迟的被动信号 |
| `SinglePointSignal` | `SignalBase`（`signal/SinglePointSignal.hpp:42`） | 单端点信号（预留，R2014b 未用） |
| `SignalData` / `SignalDataCache` | 无（结构体式，`signal/SignalData.hpp:52` / `SignalDataCache.hpp:47`） | 信号路径数据载体 / 电离层缓存 |
| `Ionosphere` | `MediaCorrection`（`measurement/Ionosphere/Ionosphere.hpp:39`） | IRI2007 / TRK-2-23 电离层修正 |
| `Troposphere` | `MediaCorrection`（`measurement/Troposphere/Troposphere.hpp:35`） | HopfieldSaastamoinen / Marini / TRK-2-23 对流层修正 |
| `MediaCorrection` | `MediaCorrectionInterface`（`measurement/MediaCorrection.hpp:40`） | 介质修正模型基类（本插件实现） |
| `DataFile` | `GmatBase`（`measurementfile/DataFile.hpp:51`） | 测量数据流容器（脚本对象） |
| `ObType` | `GmatBase`（`measurementfile/ObType.hpp:51`） | 观测流抽象基类 |
| `GmatObType` / `B3_obtype` / `RampTableType` / `TdmObType` | `ObType`（各自 `:43/:43/:44/:41`） | 各文件格式的观测流实现 |
| `ObservationData` / `RampTableData` | `GmatData`（`:51` / `:48`） | 观测记录 / 斜坡表记录（结构体式） |
| `GmatData` | 无（`measurementfile/GmatData.hpp:45`） | 数据记录基类 |
| `DataFileAdapter` | 无（`measurementfile/DataFileAdapter.hpp:44`） | `DataFile`/`ObType`/内部结构间的转换器 |
| `TdmReadWriter` | 无（`tdmReader/TdmReadWriter.hpp:48`） | TDM XML 的 Xerces 解析实现 |
| `TdmErrorHandler` | `xercesc::ErrorHandler`（`tdmReader/TdmErrorHandler.hpp:54`） | XML 解析错误处理器 |
| `TrackingFileSet` | `MeasurementModelBase`（`trackingfile/TrackingFileSet.hpp:49`） | 测量配置与数据文件的总容器 |
| `TFSMagicNumbers` | 无（单例，`trackingfile/TFSMagicNumbers.hpp:57`） | 测量类型 magic number 生成器 |

#### 逐文件讲解

##### 13.6.1 `adapter/`：测量数据适配器

适配器是"测量模型原始量 → 观测格式 C 值"的换算层。基类 `TrackingDataAdapter` 定义统一接口，子类按观测类型重写 `Initialize()`、`CalculateMeasurement()`、`CalculateMeasurementDerivatives()` 等。26 个适配器的单位换算与继承关系见下表（类声明行号均已 `read` 确认）：

| 适配器 | 基类（`:行号`） | 观测量 / 单位换算 | 重写要点 |
|---|---|---|---|
| `TrackingDataAdapter` | `MeasurementModelBase`（:63） | 基类，无具体单位 | 定义 `CalculateMeasurement`/`CalculateMeasurementDerivatives` 纯虚接口、参数表（`SIGNAL_PATH/OBS_DATA/RAMPTABLES/MEASUREMENT_TYPE/...`）、`GetTrackingConfig()`、斜坡频率积分 `IntegralRampedFrequency` |
| `RangeAdapterKm` | `TrackingDataAdapter`（:39） | 距离，km；把每段 `rangeVecInertial.GetMagnitude()` 累加 | C 值叠加介质/硬件延迟修正，再乘 `multiplier` 并加噪声/偏差（`RangeAdapterKm.cpp:575/588/716/724/735`） |
| `AngleAdapterDeg` | `TrackingDataAdapter`（:41） | 角度，deg；修正量 rad→deg | 抽象角度适配器，统一角度 C 值与噪声/偏差处理（`AngleAdapterDeg.cpp:708/763`） |
| `AzimuthAdapter` | `AngleAdapterDeg`（:39） | 方位角，deg | 提取方位角观测量 |
| `ElevationAdapter` | `AngleAdapterDeg`（:39） | 仰角，deg | 提取仰角观测量 |
| `DeclinationAdapter` | `AngleAdapterDeg`（:39） | 赤纬，deg | 提取赤纬观测量 |
| `RightAscAdapter` | `AngleAdapterDeg`（:39） | 赤经，deg | 提取赤经观测量 |
| `XEastAdapter` | `AngleAdapterDeg`（:39） | X（东向）角度，deg | 直角坐标角度投影 |
| `XSouthAdapter` | `AngleAdapterDeg`（:39） | X（南向）角度，deg | 直角坐标角度投影 |
| `YEastAdapter` | `AngleAdapterDeg`（:39） | Y（东向）角度，deg | 直角坐标角度投影 |
| `YNorthAdapter` | `AngleAdapterDeg`（:39） | Y（北向）角度，deg | 直角坐标角度投影 |
| `DSNRangeAdapter` | `RangeAdapterKm`（:39） | DSN 距离，km；处理测距模与斜坡频率 | 双程距离 + 斜坡频率积分（`DSNRangeAdapter.cpp:1008`） |
| `DSNPNRangeAdapter` | `RangeAdapterKm`（:39） | DSN 伪噪声测距，km | PN 测距专用修正与斜坡（`DSNPNRangeAdapter.cpp:1063`） |
| `BRTSRangeAdapter` | `RangeAdapterKm`（:44） | BRTS 距离，km | BRTS 测距修正（`BRTSRangeAdapter.cpp:419`） |
| `GNRangeAdapter` | `RangeAdapterKm`（:39） | 地面网络（GN）距离，km | 地面网络测距 |
| `RangeSkinAdapter` | `GNRangeAdapter`（:38） | GN 距离（skin） | GN 距离派生 |
| `TDRSRangeAdapter` | `RangeAdapterKm`（:39） | TDRS 距离，km | TDRS 测距（`TDRSRangeAdapter.cpp:349`） |
| `DopplerAdapter` | `RangeAdapterKm`（:39） | 多普勒（频率），Hz | 由距离/距离率经频率换算多普勒频移（`DopplerAdapter.cpp`） |
| `RangeRateAdapterKps` | `RangeAdapterKm`（:39） | 距离变化率，km/s | 距离率 C 值 |
| `PointRangeRateAdapterKps` | `RangeAdapterKm`（:39） | 点距离变化率，km/s | 点测距率 |
| `GNDopplerAdapter` | `GNRangeAdapter`（:39） | GN 多普勒，km/s | `dtdt/dopplerCountInterval`（`GNDopplerAdapter.cpp:1011`） |
| `BRTSDopplerAdapter` | `BRTSRangeAdapter`（:39） | BRTS 多普勒，Hz | 频率×多普勒计数换算（`BRTSDopplerAdapter.cpp:1237-1240`） |
| `TDRSDopplerAdapter` | `RangeAdapterKm`（:39） | TDRS 多普勒，Hz | 4 支路（EL/SL/ES/SS）叠加，Hz/Km 因子（`TDRSDopplerAdapter.cpp:1222-1240`） |
| `TDRS3LReturnDopplerAdapter` | `RangeAdapterKm`（:39） | TDRS 3L 返程多普勒，Hz | 三支路返程叠加（`TDRS3LReturnDopplerAdapter.cpp:1306-1309`） |
| `TDRSDOWDAdapter` | `TrackingDataAdapter`（:39） | TDRS 单向差多普勒（DOWD），Hz | 两路径频率差分（`TDRSDOWDAdapter.cpp:1325`） |
| `GPSAdapter` | `TrackingDataAdapter`（:42） | GPS 位置矢量 `GPS_PosVec` | GPS 单点解测量（`GPSAdapter.cpp:602` 起离子层修正） |

###### TrackingDataAdapter

- 基类接口（`TrackingDataAdapter.hpp:63-392`）：继承 `MeasurementModelBase`（`measurement/MeasurementModelBase.hpp:44`，最终继承 core `GmatBase`）。核心纯虚接口为 `CalculateMeasurement(...)`（:162-166）与 `CalculateMeasurementDerivatives(obj, id)`（:167-169），派生类必须实现。`Initialize()`（`TrackingDataAdapter.cpp:1363-1423`）先调 `MeasurementModelBase::Initialize()`，再把太阳系/传播器/进度报告器注入 `calcData`（指向 `MeasureModel`），最后给 `cMeasurement` 分配 1×1 单位协方差（:1405-1407）。
- 单位换算模式：基类不直接换算，而是在 `cMeasurement` 中累积测量模型输出的物理量；派生类负责单位（`RangeAdapterKm` 用 km、`AngleAdapterDeg` 用 deg、多普勒类用 Hz）。基类提供 `SetModelTypeID(theID, type, mult)`（:1570-1576）设置 magic number/类型名/乘子，`SetMultiplierFactor`（:1636-1639）设置缩放因子（如双程距离除 2）。
- 把观测文件数值转成内部物理量：基类把 `ObservationData`（`obsData` 成员，:301）、斜坡表（`rampTB`，:304）、参与方 ID 列表（`participantLists`，:234）注入计算流程；`GetTrackingConfig()`（:2481-2532）把参与方 ID 与类型名拼成 `.gmd` 风格的配置串。斜坡频率积分 `IntegralRampedFrequency`（:2251-2401）用梯形法对 `rampFrequency`/`rampRate` 分段积分得到累加相位（:2380 `value1 = ((f0+f1)/2 - basedFreq) * interval_len`）。偏差/噪声/协方差由 `ComputeMeasurementBias`（:1847）、`ComputeMeasurementNoiseSigma`（:1937）、`ComputeMeasurementErrorCovarianceMatrix`（:1975）从 `ErrorModel` 读入（`measurementBias`/`noiseSigma`/`measErrorCovariance` 成员）。

##### 13.6.2 `hardware/`：射频硬件链路

硬件类构成一条继承链：core `Hardware`→`Imager`→（插件）`Antenna`/`Sensor`→`RFHardware`→`Transmitter`/`Receiver`/`Transponder`，`Oscillator` 再派生自 `Transmitter`。

###### Antenna

- 职责：天线硬件模型。继承 core `Imager`（`Antenna.hpp:33`），新增 `antennaDelay`（天线延迟）与 3 个 `phaseCenterLocation`（相位中心在星体坐标系的偏移）成员（:65-68）。参数枚举 `ANTENNA_DELAY/PHASE_CENTER_LOCATION1..3`（:72-78）。

###### Sensor

- 职责：传感器基类。继承 core `Imager`（`Sensor.hpp:42`），持有最多两条 `Signal*`（`signal1/signal2`）、两条硬件延迟（`hardwareDelay1/2`）与 `isTransmitted1/2` 标志（:108-113）。提供 `GetDelay/SetDelay/GetSignal/SetSignal/IsTransmitted/IsFeasible` 等接口（:98-104）。参数 `SENSOR_ID` 与 `HARDWARE_DELAY`（:117-122）。

###### RFHardware

- 职责：射频硬件基类。继承 `Sensor`（`RFHardware.hpp:44`），新增 `primaryAntenna`（主天线指针）与 `primaryAntennaName`（:96-97），参数 `PRIMARY_ANTENNA`（:100-104）。`Initialize()`（`RFHardware.cpp:503`）负责把脚本名解析成实际天线对象并绑定。

###### Transmitter

- 职责：发射机。继承 `RFHardware`（`Transmitter.hpp:42`）。核心成员 `frequencyModel/frequency/frequencyBand`（:150-152）与 `freqPolynomialCoeffs`（Taylor 系数，:156）、`freqPolynomialCoeffSigmas`（:158）。`GetFrequency()`（`Transmitter.cpp:1248`）按多项式算发射频率，`GetFrequencyOscillatorBias()`（:1283）取振荡器频率偏置，`GetOutPutFrequency()`（:1333）取输出频率。参数含 `FREQUENCY_MODEL/FREQUENCY/FREQUENCY_BAND/FREQUENCY_POLYNOMIAL_COEFFICIENTS/...`（:175-186）。

###### Receiver

- 职责：接收机。继承 `RFHardware`（`Receiver.hpp:35`）。成员 `frequencyModel/centerFrequency/bandwidth/receiverId`（:139-143）与 `errorModelNames/errorModels`（:144-145，用于 `TrackingDataAdapter::GetMeasurementErrorModel` 里按测量类型查找误差模型，`TrackingDataAdapter.cpp:1761-1797`）。参数 `FREQUENCY_MODEL/CENTER_FREQUENCY/BANDWIDTH/RECEIVER_ID/ERROR_MODELS`（:148-156）。

###### Transponder

- 职责：转发器。继承 `RFHardware`（`Transponder.hpp:35`）。成员 `inputFrequencyModel/inputCenterFrequency/inputBandwidth/outputFrequencyModel/turnAroundRatio`（:110-114），转发比 `turnAroundRatio` 决定返程频率与上行频率的关系（`GetTurnAroundRatio()`，:105）。参数 `INPUT_FREQUENCY_MODEL/INPUT_CENTER_FREQUENCY/INPUT_BANDWIDTH/OUTPUT_FREQUENCY_MODEL/TURN_AROUND_RATIO`（:117-125）。

###### Oscillator

- 职责：振荡器。继承 `Transmitter`（`Oscillator.hpp:39`），新增频率漂移 `freqDrift`（单位秒）与漂移噪声 `freqDriftSigma`（:140-142），以及自己的频率多项式系数（:144-146）。`GetFrequency()`（`Oscillator.cpp:1158-1169`）按 "Equation 3.3.7"（TDRSS/BRTS Math Spec）做 Taylor 级数求和：`freq = Σ freqPolynomialCoeffs[k]·t^k`，其中 `t = (currentEpoch-initialEpoch).GetMjd() + freqDrift`（:1163）。`GetFrequencyDriftDerivative()`（:1209-1223）给出频率对漂移的导数（乘 `1.0e6` 从 Mhz/s 转 Hz/s）。

###### Signal

- 职责：传感器信号的最小值对象。独立类（`Signal.hpp:36`），只含 `epoch`（`GmatTime`）与 `value`（`Real`），提供 `SetEpoch/GetEpoch/SetValue/GetValue`（:46-50）。它是硬件信号传输的最小数据单元。

##### 13.6.3 `signal/`：信号路径与数据

###### SignalBase

- 职责：信号路径链表节点基类，继承 core `GmatBase`（`SignalBase.hpp:57`）。用 `next/previous` 指针（:133-135）把多个"发射→接收"腿串成完整路径。核心纯虚接口：`ModelSignal(atEpoch, forSimulation, EpochAtReceive)`（:91）、`ModelSignalDerivative(...)`（:94-98）、`SignalFrequencyCalculation(...)`（:101）、`AddCorrection(...)`（:105）、`MediaCorrectionCalculation(...)`（:108）、`HardwareDelayCalculation()`（:110）。成员含发射/接收状态（`tState/rState`，:138-140）、各坐标系（`tcs/rcs/ocs/j2k`，:152-158）、旋转矩阵（:167-181）、HORP 参数（:188-196）。

###### PhysicalSignal

- 职责：瞬时信号实现，继承 `SignalBase`（`PhysicalSignal.hpp:50`）。持有 `Troposphere*` 与 `Ionosphere*` 修正模型（:89-92）、相对论/ET-TAI 修正（`useRelativity/relCorrection/ettaiCorrection`，:94-102）。关键函数：`ModelSignal`（:62）、`RelativityCorrection`（:107）、`ETminusTAI`（:110）、`TroposphereCorrection/IonosphereCorrection/MediaCorrection`（:118-120）、`HardwareDelayCalculation`（:123）。私有成员含 `TestSignalBlockedBetweenTwoParticipants`（:132）、`TestSignalBlockedByBody`（:133）、`TestHeightOfRayPath`（:134）三个遮挡/HORP 判定。

###### PassivePhysicalSignal

- 职责：无硬件延迟的被动信号。继承 `PhysicalSignal`（`PassivePhysicalSignal.hpp:35`），仅重写 `HardwareDelayCalculation()`（:49）以跳过硬件延迟计算。

###### SinglePointSignal

- 职责：单端点信号中间类。继承 `SignalBase`（`SinglePointSignal.hpp:42`），只声明构造/析构/拷贝，注释注明 R2014b 尚不需要（:39-41）。

###### SignalData

- 职责：信号路径数据载体（结构体式，`SignalData.hpp:52`）。字段覆盖：收发节点与传播器（`tNode/rNode/tPropagator/rPropagator`，:67-77）、收发时刻/位置/速度/距离矢量（:82-114）、可行性与仰角（`feasibility/feasibilityReason/feasibilityValue`，:117-119）、状态转移矩阵（`tSTM/rSTM/...`，:123-132）、修正标识（:145-151）、硬件延迟（`tDelay/rDelay`，:156-158）、信号频率（`arriveFreq/transmitFreq/receiveFreq/...`，:162-174），以及链表指针 `next`（:178）。

###### SignalDataCache

- 职责：信号数据缓存（`SignalDataCache.hpp:47`）。核心是 `CacheKey`（strand+频率+两时刻，:55-64）与 `CacheValue`（光时解 + 电离层修正，:67-83），用 `std::unordered_map` 组成 `SimpleSignalDataCache`（:91）。`TrackingFileSet` 与 `TrackingDataAdapter` 用它缓存电离层修正，避免重复计算（`TrackingDataAdapter.hpp:334`、`TrackingFileSet.hpp:318`）。

##### 13.6.4 `measurement/Ionosphere/`：电离层修正

###### Ionosphere

- 职责：IRI 2007 / TRK-2-23 电离层介质修正。继承 `MediaCorrection`（`Ionosphere.hpp:39`）。接口 `TEC(end,start)`（总电子含量，:56）、`BendingAngle(end,start)`（仰角修正，:57）、`Correction()`（:58，按 `modelTypeName` 分派 IRI2007 / TRK-2-23）。IRI2007 的电子密度剖面函数 `xe1..xe6`（:932/967/996/1023/1054/1084）为静态私有，分别给出 F2/E/F1/D/E 层剖面。`CalculateIRI2007`（`Ionosphere.cpp:1268`）与 `CalculateTRK223`（:1886）为两个计算入口。另设单例 `IonosphereCorrectionModel`（:110-122）供全局复用。
- 关键公式：
  - `TEC` 用梯形积分沿路径累加电子密度（`Ionosphere.cpp:1125-1144`）：`tec += electdensity*ds`，`ds` 为相邻采样点间距（m）。
  - `BendingAngle` 用折射率 `n = 1 - 40.3·N_e/f²`（:1178-1191）与 Snell 折射逐段累加 `dtheta`（:1206-1217）。
  - `Correction` 返回三元素数组：距离修正（m）、仰角修正（rad）、时延修正（s）（:1228-1231）。

###### APData

- 职责：从历史文件读 ap 太阳活动指数并按年月日时返回 `rap`（`APData.hpp:34`，`get_rap` 在 :40）。逻辑取自 IRI2007。

###### MagneticField / MagneticHistory

- 职责：地磁场谐波系数模型。`MagneticField`（`MagneticField.hpp:34`）提供 `geomag_lat`（地磁纬度，:39）与 `get_field`（磁倾/modiP，:41）；`MagneticHistory`（`MagneticHistory.hpp:35`）按年份加载历史磁场并 `make_magnetic_field(year,doy)`（:41）。供 IRI2007 计算 modip 用。

###### IonosphereCoefficients / IonosphereCoefficientsFull

- 职责：IRI2007 的 URSI/CCIR 系数表。`IonosphereCoefficients`（`IonosphereCoefficients.hpp:34`）存某一太阳活动（rssn）下的 `m3000f2/fof2` 系数（按 cos(lat)/sin(modip)/经度展开）；`IonosphereCoefficientsFull`（`IonosphereCoefficientsFull.hpp:36`）从数据文件加载全月/全 ig/rz 系数，并 `make_ionosphere_coefficients(year,month,day,hours)`（:41）插值出某时刻的系数。

##### 13.6.5 `measurement/Troposphere/`：对流层修正

###### Troposphere

- 职责：对流层介质修正。继承 `MediaCorrection`（`Troposphere.hpp:35`）。`Correction()`（`Troposphere.cpp:178-210`）按 `modelTypeName` 分派三种模型：`HopfieldSaastamoinen`、`Marini`、`TRK-2-23`。三个计算函数 `CalculateHS`（:323）、`CalculateMarini`（:465）、`CalculateTRK223`（:595）。
- 关键公式（HopfieldSaastamoinen，`Troposphere.cpp:346-443`）：
  - 干湿折射率 `N[0] = 77.624·p/T`（:369）、湿项 `N[1] = 371900·e/T² - 12.92·e/T`（:374），其中水汽压 `e = 6.10·fh·exp(17.15·Tc/(234.7+Tc))`（:373）。
  - 干湿对流层高度 `h[0] = 5·0.002277·p/(N[0]·1e-6)`（:380）、湿高 `h[1]`（:383）。
  - 距离修正 `drho = Σ N[j]·1e-6·sum1`（:434），仰角修正 `dE = Ce·4·cosE·dE/rho`（:438），时延修正 `drho/c`（:443）。

##### 13.6.6 `measurementfile/`：测量文件结构

###### DataFile

- 职责：测量数据流容器（脚本对象），继承 `GmatBase`（`DataFile.hpp:51`）。持有 `ObType* theDatastream`（:128）与数据过滤列表 `filterList`（:137）。接口 `SetStream/OpenStream/ReadObservation/ReadRampTableData/WriteMeasurement`（:107-115）。参数 `StreamName/ObsType/DataThinningRatio/SelectedStationIDs/EpochFormat/StartEpoch/EndEpoch`（:156-166）。`FilteringData`（:120）在读取后做过滤。

###### ObType

- 职责：观测流抽象基类，继承 `GmatBase`（`ObType.hpp:51`）。纯虚接口 `AddMeasurement(md)`（:73）与 `ReadObservation()`（:77-78）、`ReadRampTableData()`（:82-83），由各文件格式派生实现。持有 `streamName/header/openForRead/openForWrite`（:91-97）与时间转换单例 `theTimeConverter`（:100）。

###### GmatObType

- 职责：GMAT 内部 `.gmd` 格式观测流。继承 `ObType`（`GmatObType.hpp:43`），用 `std::fstream theStream` 读写（:71），`ReadObservation` 逐条解析。`ProcessSignals`（:85）解析信号路径串。

###### B3_obtype

- 职责：B3 观测格式扩展。继承 `ObType`（`B3_obtype.hpp:43`）。`b3Type`（:66）编码观测组合（0 距离率、1 方位+仰角、2 距离+方位+仰角、5 赤经赤纬等，注释 :50-61），并带 `securityClassification/satelliteID/sensorID/.../azimuth/elevation/range/rangeRate/ecf_X..Z`（:69-107）。

###### GmatData

- 职责：数据记录基类（`GmatData.hpp:45`），只含 `dataFormat`（"GMATInternal"/"GMAT_OD"/"GMAT_ODDoppler"/"GMAT_RampTable"，:57）与纯虚 `Clear()`（:54）。

###### ObservationData

- 职责：观测记录（结构体式），继承 `GmatData`（`ObservationData.hpp:51`）。字段覆盖：`fileIndex/inUsed/removedReason`（:69-77）、`typeName/type/uniqueID/epochSystem/epoch/epochGT`（:80-90）、`participantIDs/sensorIDs/strands/value/dataMap`（:98-106）、`value_orig/unit/noiseCovariance`（:109-114）、`uplinkBand/downlinkBand/uplinkFreqAtRecei/rangeModulo`（:127-135）、`transmitDelay/receiveDelay/dopplerCountInterval`（:138-143）、TDRS 相关字段（`tdrsServiceID/tdrsNode4Freq/...`，:147-170）。

###### RampTableData

- 职责：斜坡表记录（结构体式），继承 `GmatData`（`RampTableData.hpp:48`）。字段 `typeName/type/epochSystem/epoch/epochGT`（:61-69）、`participantIDs`（:72）、`uplinkBand/rampType/rampFrequency/rampRate`（:74-80）、排序键 `indexkey`（:83）。

###### RampTableType

- 职责：GMAT_RampTable 斜坡表流。继承 `ObType`（`RampTableType.hpp:44`），用 `std::fstream` 读写并缓存 `std::vector<RampTableData> rampTable`（:78-79）。`AddMeasurement/ReadObservation` 空实现（:59-61），只实现 `ReadRampTableData`（:62-63）。

###### DataFileAdapter

- 职责：`DataFile`/`ObType`/内部结构间的转换器（`DataFileAdapter.hpp:44`）。接口 `GetObTypeObject(forFile)`（:52）、`LoadObservation(data, target)`（:53）、`LoadMeasurement(data, target)`（:54）。

##### 13.6.7 `tdmReader/`：TDM XML 解析

###### TdmReadWriter

- 职责：TDM（CCSDS Tracking Data Message）XML 解析实现（`TdmReadWriter.hpp:48`），封装 Xerces DOM 解析器。`Validate`（:58）、`ProcessMetadata`（:61）、`LoadRecord`（:62）读元数据与观测记录。元数据枚举 `MetaData`（`TIME_SYSTEM/PARTICIPANT_1..5/MODE/PATH/TRANSMIT_BAND/...`，:90-112）用 `HashIt`（:115）把 XML 节点名映射为枚举。

###### TdmObType

- 职责：TDM 观测流。继承 `ObType`（`TdmObType.hpp:41`），持有 `TdmReadWriter*`（:62）、模板 `ObservationData*`（:66）与 `TFSMagicNumbers*`（:70）。`Open` 触发验证，`ReadObservation` 逐条读观测。

###### TdmErrorHandler

- 职责：Xerces SAX 错误处理器。继承 `xercesc::ErrorHandler`（`TdmErrorHandler.hpp:54`），重写 `fatalError/error/warning/resetErrors`（:62-65），把解析错误转成 GMAT 消息。

##### 13.6.8 `trackingfile/`：测量集合与 magic number

###### TrackingFileSet

- 职责：测量配置与数据文件的总容器（脚本对象），继承 `MeasurementModelBase`（`TrackingFileSet.hpp:49`）。内部类 `MeasurementDefinition`（:186-203）记录 `strands/sensors/types`；成员 `measurements`（`std::vector<TrackingDataAdapter*>`，:208）、`filenames/rampedTablenames`（:210-212）、HORP/相对论/ET-TAI 标志（:214-250）、数据过滤（:261-262）。核心方法 `BuildAdapter(...)`（:312）按 `strand+sensors+type` 工厂化适配器，`GetAdapters()`（:174）返回全部适配器。参数枚举 `TRACKINGCONFIG/FILENAME/.../HORP_HEIGHT/HORP_CENTRAL_ANGLE/DATA_FILTERS`（:276-303）。

###### TFSMagicNumbers

- 职责：测量类型 magic number 生成器（单例，`TFSMagicNumbers.hpp:57`）。`LookupEntry` 结构（:79-95）记录 `signalPathCount/nodeCount/nodes/type/multFactor/magicNumber`。`GetMagicNumber(nodelist, type)`（:69）按节点数与类型分配整数 ID，`FillMagicNumber(theObs)`（:71）为观测填 ID，`GetMNMultiplier`（:72）取缩放因子。这些 ID 出现在 `.gmd` 文件与估计子系统里标识测量类型。

##### 13.6.9 `swig/`：Python/Java 绑定

- `navigation.i`（5 行）：Java 绑定入口，`%module navigation`，`%import gmat.i` 后 `%include navigation.swg`。
- `navigation.swg`（51 行）：绑定主体。`%apply double[]` 映射双精度数组，`ARRAYRETURN(...)` 为 `ErrorModel::GetEstimationParameterValue` 生成数组返回，`VECTORCONVERT(...)` 为 `RampTableData/TrackingDataAdapter/SignalData/SignalBase` 生成向量转换，`DOWNCAST(...)` + `%include` 逐个暴露本插件类型（`TrackingDataAdapter`/`RangeAdapterKm`/`TrackingFileSet`/硬件类/`PhysicalSignal` 等）。
- `NavigationAPI.hpp`（23 行）：绑定用的聚合头，include 本插件各公开头（`TrackingDataAdapter.hpp`/`RangeAdapterKm.hpp`/硬件/`PhysicalSignal.hpp` 等）。
- `navigation_py.i`（9 行）：Python 绑定入口，`%module navigation_py`，`%ignore TrackingFileSet::MeasurementDefinition`（内部类不暴露）后 `%include navigation.swg`。
- `CMakeLists.txt`（37 行）：SWIG 生成脚本。`_SETUPSWIG(...)` 按 Python/Java 生成绑定，`TARGET_LINK_LIBRARIES(... GmatEstimation)` 链接插件库（:26/:36）。

#### 关键类深读

##### TrackingDataAdapter：基类接口与单位换算模式

- **继承**：`TrackingDataAdapter : MeasurementModelBase`（`TrackingDataAdapter.hpp:63`），`MeasurementModelBase : GmatBase`（`measurement/MeasurementModelBase.hpp:44`）——因此它最终是 core `GmatBase` 的派生，具备脚本参数体系。
- **基类接口**：`Initialize()`（`TrackingDataAdapter.cpp:1363`）把 `solarsys/propagators/navLog/withLighttime` 注入 `calcData`（`MeasureModel`），并初始化 `cMeasurement`；纯虚 `CalculateMeasurement(...)`（hpp:162）与 `CalculateMeasurementDerivatives(...)`（hpp:167）由派生类实现；`GetUnit` 相关换算被下推到派生类（基类只声明 `SetMultiplierFactor/GetMultiplierFactor`，:200-201）。
- **单位换算模式**：派生类在 `CalculateMeasurement` 里把 `calcData->GetSignalData()`/`GetSignalPaths()` 返回的 `SignalData`（含 `rangeVecInertial`、修正、硬件延迟、频率）换算成观测单位——距离类用 km（`RangeAdapterKm.cpp:575/588`），角度类把 rad 修正乘 `DEG_PER_RAD` 转 deg（`AngleAdapterDeg.cpp:584/708`），多普勒类用 `multiplier = freq·1e6/(dopplerCountInterval·c)` 把 km 转 Hz（`TDRSDopplerAdapter.cpp:1222-1226`）。
- **观测文件数值转内部物理量**：基类把 `ObservationData`（:301）、斜坡表（:304）、参与方（:234）作为输入，`GetTrackingConfig`（:2481）把 `participantLists` 中的名字替换成 ID（航天器 `Id`、地面站 `Id`）拼成 `.gmd` 配置串；斜坡频率积分 `IntegralRampedFrequency`（:2251）按 `rampFrequency/rampRate` 梯形积分；偏差/噪声/协方差分别从 `ErrorModel` 读入（:1847/:1937/:1975）。

##### RFHardware 与子类：硬件链路在测量值计算中的角色

- **继承链**（core 侧）：`Hardware : GmatBase`（`src/base/hardware/Hardware.hpp:59`）→ `Imager : Hardware`（`src/base/hardware/Imager.hpp:38`）→（插件侧）`Sensor : Imager`（`Sensor.hpp:42`）→ `RFHardware : Sensor`（`RFHardware.hpp:44`）→ `Transmitter/Receiver/Transponder : RFHardware`，`Oscillator : Transmitter`（`Oscillator.hpp:39`）；`Antenna : Imager`（`Antenna.hpp:33`）独立一支。任务描述中的"RFHardware 继承 Hardware"是指这条间接继承链。
- **在测量值中的角色**：`SignalBase`/`PhysicalSignal` 在算每条信号腿时，从发射机/接收机/转发器/振荡器取频率（`Transmitter::GetFrequency`、`Oscillator::GetFrequency` 的 Taylor 级数），把硬件延迟（`Sensor::GetDelay`、`RFHardware` 主天线）换算成距离/时延修正，并把 `Receiver` 上挂的 `ErrorModel` 用于偏差与噪声（`TrackingDataAdapter::GetMeasurementErrorModel`，`TrackingDataAdapter.cpp:1670-1813`）。因此硬件层决定多普勒/测距的频率基准与误差特性，是"信号层算几何、硬件层定频率与噪声"的分工。

##### DataFile / ObType / TdmReadWriter：测量文件解析结构

- `DataFile` 是脚本可见容器，`ObType` 是具体文件流抽象，`TdmObType`+`TdmReadWriter` 处理 CCSDS TDM XML（Xerces），`GmatObType` 处理 `.gmd`，`B3_obtype` 处理 B3，`RampTableType` 处理斜坡表。它们统一产出 `ObservationData`/`RampTableData`（继承 `GmatData`），`DataFileAdapter` 负责 `DataFile→ObType→内部结构` 的双向转换。`TFSMagicNumbers` 给每个观测补上 magic number，使 `.gmd` 的整数类型 ID 与 `TrackingDataAdapter::SetModelTypeID` 的 `modelTypeID` 一致。

##### Ionosphere / Troposphere：介质修正模型（关键公式行号）

- `Ionosphere::Correction`（`Ionosphere.cpp:1233`）按模型分派；`TEC`（:1103）梯形积分电子密度；`BendingAngle`（:1166）用 `n=1-40.3·N_e/f²`（:1178）做 Snell 折射；IRI2007 剖面 `xe1..xe6`（:932/967/996/1023/1054/1084）；`CalculateIRI2007`（:1268）、`CalculateTRK223`（:1886）。
- `Troposphere::Correction`（`Troposphere.cpp:178`）按模型分派；`CalculateHS`（:323）中干湿折射率 `N[0]=77.624·p/T`（:369）、`N[1]`（:374）、距离修正 `drho`（:434）、仰角修正 `dE`（:438）、时延 `drho/c`（:443）；`CalculateMarini`（:465）、`CalculateTRK223`（:595）。

#### 与 core 的扩展点

- `TrackingDataAdapter` 继承的 core 类为 `GmatBase`（经 `MeasurementModelBase`，`measurement/MeasurementModelBase.hpp:44`）；`MeasureModel`（`adapter` 内 `calcData` 指针指向的类型）亦继承 `GmatBase`。
- `RFHardware` 继承 `Sensor`→core `Imager`→core `Hardware`→core `GmatBase`（`src/base/hardware/Hardware.hpp:59`、`Imager.hpp:38`）。`Hardware.hpp` 第 59 行确认 `class GMAT_API Hardware : public GmatBase`。
- `SignalBase` 继承 core `GmatBase`（`signal/SignalBase.hpp:57`）。
- 工厂注册在 `factory/`（本小节未展开，见 §13.6 其它片段）：`EstimatorHardwareFactory` 负责 `CreateHardware`（Antenna/Transmitter/Receiver/Transponder/Oscillator/Sensor 等），`DataFileFactory`/`ObTypeFactory` 负责测量文件对象，`MeasurementModelFactory` 负责测量模型。

#### 文件清单附录

| 相对路径（相对 `plugins/EstimationPlugin/`） | 职责 | 关键类/函数 |
|---|---|---|
| `src/base/adapter/TrackingDataAdapter.hpp/.cpp` | 适配器基类 | `TrackingDataAdapter`、`Initialize`、`CalculateMeasurement`（纯虚）、`IntegralRampedFrequency`、`ComputeMeasurementBias/NoiseSigma` |
| `src/base/adapter/RangeAdapterKm.hpp/.cpp` | 距离（km）基类 | `CalculateMeasurement`、`GetIonoCorrection/GetTropoCorrection` |
| `src/base/adapter/AngleAdapterDeg.hpp/.cpp` | 角度（deg）基类 | rad→deg 换算 |
| `src/base/adapter/AzimuthAdapter.hpp/.cpp` 等 7 个角度适配器 | 方位/仰角/赤经/赤纬/X·Y 投影 | 各 `CalculateMeasurement` |
| `src/base/adapter/DSNRangeAdapter.hpp/.cpp`、`DSNPNRangeAdapter.hpp/.cpp` | DSN 距离/PN 距离 | 斜坡频率积分 |
| `src/base/adapter/BRTSRangeAdapter.hpp/.cpp`、`BRTSDopplerAdapter.hpp/.cpp` | BRTS 距离/多普勒 | 距离→Hz 换算 |
| `src/base/adapter/GNRangeAdapter.hpp/.cpp`、`GNDopplerAdapter.hpp/.cpp`、`RangeSkinAdapter.hpp/.cpp` | 地面网络距离/多普勒 | km/km·s⁻¹ |
| `src/base/adapter/TDRSRangeAdapter.hpp/.cpp`、`TDRSDopplerAdapter.hpp/.cpp`、`TDRS3LReturnDopplerAdapter.hpp/.cpp`、`TDRSDOWDAdapter.hpp/.cpp` | TDRS 距离/多普勒/DOWD | 4 支路叠加、Hz/Km 因子 |
| `src/base/adapter/DopplerAdapter.hpp/.cpp` | 多普勒基类 | 频率换算 |
| `src/base/adapter/RangeRateAdapterKps.hpp/.cpp`、`PointRangeRateAdapterKps.hpp/.cpp` | 距离率（km/s） | 距离率 C 值 |
| `src/base/adapter/GPSAdapter.hpp/.cpp` | GPS 位置矢量 | `GPS_PosVec` |
| `src/base/hardware/Antenna.hpp/.cpp` | 天线模型 | `Antenna`、延迟/相位中心 |
| `src/base/hardware/Sensor.hpp/.cpp` | 传感器基类 | `Sensor`、`GetDelay/SetDelay` |
| `src/base/hardware/RFHardware.hpp/.cpp` | 射频硬件基类 | `RFHardware`、主天线绑定 |
| `src/base/hardware/Transmitter.hpp/.cpp` | 发射机 | `GetFrequency`、频率多项式 |
| `src/base/hardware/Receiver.hpp/.cpp` | 接收机 | `Receiver`、误差模型列表 |
| `src/base/hardware/Transponder.hpp/.cpp` | 转发器 | `GetTurnAroundRatio` |
| `src/base/hardware/Oscillator.hpp/.cpp` | 振荡器 | `GetFrequency`、`GetFrequencyDriftDerivative` |
| `src/base/hardware/Signal.hpp/.cpp` | 信号值对象 | `Signal` |
| `src/base/signal/SignalBase.hpp/.cpp` | 信号路径基类 | 链表、`ModelSignal` 等纯虚接口 |
| `src/base/signal/PhysicalSignal.hpp/.cpp` | 瞬时信号 | `ModelSignal`、介质/相对论/硬件延迟 |
| `src/base/signal/PassivePhysicalSignal.hpp/.cpp` | 被动信号 | 无硬件延迟 |
| `src/base/signal/SinglePointSignal.hpp/.cpp` | 单端点信号 | 预留 |
| `src/base/signal/SignalData.hpp/.cpp` | 信号数据载体 | `SignalData` |
| `src/base/signal/SignalDataCache.hpp/.cpp` | 信号数据缓存 | `CacheKey/CacheValue`、`SimpleSignalDataCache` |
| `src/base/measurement/Ionosphere/Ionosphere.hpp/.cpp` | 电离层修正 | `TEC`、`BendingAngle`、`Correction`、`xe1..xe6` |
| `src/base/measurement/Ionosphere/APData.hpp/.cpp` | ap 指数数据 | `get_rap` |
| `src/base/measurement/Ionosphere/MagneticField.hpp/.cpp` | 地磁场模型 | `get_field` |
| `src/base/measurement/Ionosphere/MagneticHistory.hpp/.cpp` | 地磁场历史 | `make_magnetic_field` |
| `src/base/measurement/Ionosphere/IonosphereCoefficients.hpp/.cpp` | IRI2007 系数（单时刻） | `get_vals` |
| `src/base/measurement/Ionosphere/IonosphereCoefficientsFull.hpp/.cpp` | IRI2007 系数（全表） | `make_ionosphere_coefficients` |
| `src/base/measurement/Troposphere/Troposphere.hpp/.cpp` | 对流层修正 | `Correction`、`CalculateHS/Marini/TRK223` |
| `src/base/measurementfile/DataFile.hpp/.cpp` | 数据流容器 | `DataFile`、`ReadObservation` |
| `src/base/measurementfile/ObType.hpp/.cpp` | 观测流抽象基类 | `ObType` |
| `src/base/measurementfile/GmatObType.hpp/.cpp` | `.gmd` 观测流 | `GmatObType` |
| `src/base/measurementfile/B3_obtype.hpp/.cpp` | B3 观测格式 | `B3_obtype`、`b3Type` |
| `src/base/measurementfile/GmatData.hpp/.cpp` | 数据记录基类 | `GmatData` |
| `src/base/measurementfile/ObservationData.hpp/.cpp` | 观测记录 | `ObservationData` |
| `src/base/measurementfile/RampTableData.hpp/.cpp` | 斜坡表记录 | `RampTableData` |
| `src/base/measurementfile/RampTableType.hpp/.cpp` | 斜坡表流 | `RampTableType` |
| `src/base/measurementfile/DataFileAdapter.hpp/.cpp` | 文件/流转换器 | `DataFileAdapter` |
| `src/base/tdmReader/TdmReadWriter.hpp/.cpp` | TDM XML 解析 | `TdmReadWriter` |
| `src/base/tdmReader/TdmObType.hpp/.cpp` | TDM 观测流 | `TdmObType` |
| `src/base/tdmReader/TdmErrorHandler.hpp/.cpp` | XML 错误处理 | `TdmErrorHandler` |
| `src/base/trackingfile/TrackingFileSet.hpp/.cpp` | 测量集合容器 | `TrackingFileSet`、`BuildAdapter` |
| `src/base/trackingfile/TFSMagicNumbers.hpp/.cpp` | magic number 单例 | `TFSMagicNumbers`、`GetMagicNumber` |
| `swig/NavigationAPI.hpp` | 绑定聚合头 | include 各公开头 |
| `swig/navigation.i` | Java 绑定入口 | `%module navigation` |
| `swig/navigation.swg` | 绑定主体 | `VECTORCONVERT/DOWNCAST/%include` |
| `swig/navigation_py.i` | Python 绑定入口 | `%module navigation_py` |
| `swig/CMakeLists.txt` | SWIG 生成脚本 | `_SETUPSWIG` |

### 13.7 EventLocatorPlugin（事件定位器）

**目录**：`plugins/EventLocatorPlugin/src/base/`，子目录 `event/`、`factory/`、`include/`、`locator/`、`plugin/`，共 23 个 C++ 文件（11 个 `.cpp`、12 个 `.hpp`，另加 1 个 `CMakeLists.txt`）。

**构建开关**：`PLUGIN_EVENTLOCATOR`，默认 `ON`，见 `plugins/CMakeLists.txt` 第 117 行。

**目标库名**：`EventLocator`，由 `plugins/EventLocatorPlugin/src/base/CMakeLists.txt` 第 17 行 `SET(TargetName EventLocator)` 决定；`PLUGIN_SRCS`（第 25–37 行）列出 11 个源文件。第 44 行 `DEFINE_SYMBOL "LOCATOR_EXPORTS"` 注入导出宏。

**一句话目的**：提供三个 `EventLocator` 派生类（接触/地影/侵入），在给定时间区间内搜索并报告目标航天器与地面站、掩体天体或传感器视场之间的几何事件。

#### 目的与职责

该插件实现 GMAT 的事件定位（event location）能力，属"搜索型"子系统：它不是逐步数值传播，而是在一个时间区间内寻找满足某种几何条件的事件起止时刻与持续时长。三个定位器都继承 core 的抽象基类 `EventLocator`（`src/base/event/EventLocator.hpp`，`GmatBase` 的子类），并各自实现纯虚方法 `FindEvents()`（基类第 287 行声明）：`EclipseLocator` 找航天器进入/离开天体阴影（本影/半影/伪本影）；`ContactLocator` 找航天器与地面站（或带视场的成像仪）的可视接触；`IntrusionLocator` 找侵入天体进入某传感器视场的事件（含掩星/凌星）。

关键设计是"把根求解外包给 SPICE"：三个 `FindEvents()` 都不自己写寻根算法，而是通过 `EphemManager`（core `src/base/subscriber/EphemManager.hpp`）调用 SPICE 的几何查找器（Geometry Finder, GF）子程序——`EclipseLocator` 用 `GetOccultationIntervals`（内部 `gfoclt_c`，`EphemManager.cpp` 第 609 行）、`ContactLocator` 用 `GetContactIntervals`（内部 `gfposc_c` 第 824 行，视线遮挡再叠加 `gfoclt_c` 第 894 行）、`IntrusionLocator` 用 `GetIntrusionIntervals`（内部 `gfoclt_c` 第 1223/1247 行）。SPICE GF 以 `stepSize` 为搜索步长做粗扫描，再用二分/寻根细化穿越时刻，因此 `EventLocator` 基类的 `stepSize`（默认 10 s，`EventLocator.cpp` 第 150 行）直接决定最小可分辨事件时长。

事件结果用"结果容器 + 事件项"两级结构表达：`ContactResult`/`EclipseTotalEvent`/`IntrusionResult` 都是 `LocatedEvent` 的派生类，内部再聚合若干 `ContactEvent`/`EclipseEvent`/`IntrusionEvent`（同样派生自 `LocatedEvent`），便于一次接触/一次侵入内报告多个子事件与逐点采样数据。

#### 导出类清单

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `ContactLocator` | `EventLocator`（`src/base/event/EventLocator.hpp`） | 搜索航天器与观测站（含成像仪）的接触事件 |
| `EclipseLocator` | `EventLocator` | 搜索航天器进入/离开阴影的事件 |
| `IntrusionLocator` | `EventLocator` | 搜索侵入天体进入传感器视场的事件 |
| `ContactEvent` | `LocatedEvent`（`src/base/event/LocatedEvent.hpp`） | 单次接触事件（含 AER 序列） |
| `ContactResult` | `LocatedEvent` | 单观测者的接触事件容器 |
| `EclipseEvent` | `LocatedEvent` | 单次阴影事件（本影/半影/伪本影之一） |
| `EclipseTotalEvent` | `LocatedEvent` | 阴影事件容器（可嵌套合并） |
| `IntrusionEvent` | `LocatedEvent` | 单次侵入事件（含逐点采样） |
| `IntrusionResult` | `LocatedEvent` | 单传感器的侵入事件容器 |
| `EventLocatorFactory` | `Factory`（`src/base/factory/Factory.hpp`） | 创建上述三个定位器，类型 `Gmat::EVENT_LOCATOR` |

继承声明行号：`ContactLocator.hpp` 第 59 行、`EclipseLocator.hpp` 第 46 行、`IntrusionLocator.hpp` 第 57 行分别 `: public EventLocator`；`ContactEvent.hpp` 第 39 行、`ContactResult.hpp` 第 39 行、`EclipseEvent.hpp` 第 39 行、`EclipseTotalEvent.hpp` 第 39 行、`IntrusionEvent.hpp` 第 42 行、`IntrusionResult.hpp` 第 42 行分别 `: public LocatedEvent`；`EventLocatorFactory.hpp` 第 43 行 `: public Factory`。

#### 插件注册与工厂

`plugin/GmatPluginFunctions.cpp` 定义插件加载 C 接口：`GetFactoryCount()` 返回 `1`（第 52–55 行），`GetFactoryPointer(index)` 在 `case 0` 时 `new EventLocatorFactory`（第 72–76 行），`SetMessageReceiver` 调用 `MessageInterface::SetMessageReceiver(mr)`（第 94–97 行）。头文件在 `extern "C"` 中声明这三个符号（`GmatPluginFunctions.hpp` 第 39–44 行）。

`EventLocatorFactory::CreateEventLocator`（`factory/EventLocatorFactory.cpp` 第 162–175 行）按类型字符串创建 `"EclipseLocator"`/`"ContactLocator"`（受 `#define INCLUDE_CONTACT` 保护，第 38 行）/`"IntrusionLocator"`；`CreateObject` 委托给它（第 145 行）。默认构造函数以 `Factory(Gmat::EVENT_LOCATOR)` 初始化，`creatables` 依次压入上述三个名字（第 50–57 行），并额外 `GmatType::RegisterType(Gmat::EVENT_LOCATOR, "EventLocator")`（第 59 行）；拷贝/赋值路径在 `creatables` 为空时补齐同一列表（第 87–95、116–123 行）。

#### 逐文件讲解

##### include/EventLocatorDefs.hpp

职责：DLL 导入/导出宏。Windows + MSVC + `_DYNAMICLINK` 下按 `LOCATOR_EXPORTS` 定义 `LOCATOR_API` 为 `__declspec(dllexport/dllimport)`（第 50–54 行），并处理 STL 模板导出 `DECLSPECIFIER`/`EXPIMP_TEMPLATE`（第 63–69 行）；非 Windows 或未定义宏时置空（第 75–77 行）。`LOCATOR_EXPORTS` 由 CMake 第 44 行 `DEFINE_SYMBOL` 注入。

##### factory/EventLocatorFactory.hpp / .cpp

职责：工厂声明与实现，见"插件注册与工厂"。`.hpp` 重写 `CreateObject` 与 `CreateEventLocator`（第 51–54 行）。

##### plugin/GmatPluginFunctions.hpp / .cpp

职责：插件加载 C 接口声明与实现，模式与其它插件一致。

##### event/LocatedEvent（core，本插件事件类的公共基类）

职责（`src/base/event/LocatedEvent.hpp`）：事件的最小抽象，持有 `start`/`end`（A1Mjd）与计算量 `duration`（第 66–73 行），提供 `GetDuration/GetStart/GetEnd`（第 52–54 行）、`SetStart/SetEnd`（第 62–63 行），并声明纯虚 `GetReportString()`（第 58 行）。本插件所有事件/结果类都继承它，从而统一接入"按起止时刻排序、计算时长、输出报告"的流程。

##### event/ContactEvent.hpp / .cpp

职责：单次接触事件。`.hpp` 公开成员：`eventNumber`、`eventSignalPath`、`eventStation`、`eventPass`（第 51–54 行），以及 AER 采样序列 `eventTimes/eventRanges/eventRangeRates/eventAzimuths/eventElevations` 与 `eventMaxElevation/eventMaxElevationEpoch`（第 55–61 行）；`customReport/leftJustified/columnSpacing`（第 63–65 行）与 `column` 结构体（第 67–77 行）支持自定义报告列。报告方法 `GetReportString/GetReportStringLegacy/GetAERString`（第 83–85 行）。`.cpp` 构造函数按 `startEpoch/endEpoch` 初始化，可带自定义列与对齐标志（第 40–48 行），`GetReportString` 拼装表格行。

##### event/ContactResult.hpp / .cpp

职责：单观测者的接触结果容器。`.hpp` 成员 `theEvents`（`std::vector<ContactEvent*>`）、`numEvents`、`observerName`、`noEvents`（第 75–81 行）；接口 `AddEvent/NumberOfEvents/SetNoEvents/SetObserverName/GetDuration/GetEvent/GetReportString/TakeAction("Clear")`（第 49–71 行）。`.cpp` 的 `AddEvent` 累加 `numEvents` 并更新 `duration`；`TakeAction("Clear","Events")` 清空并释放事件列表（第 114 行注释 "start and end are set by FindEvents" 表明起止时刻由定位器回填）。

##### event/EclipseEvent.hpp / .cpp

职责：单次阴影事件。`.hpp` 成员 `eclipseType`（本影/半影/伪本影）、`occultingBody`（第 58–60 行）；接口 `GetBodyName/GetReportString`（第 51–54 行）。构造函数签名为 `(startEpoch, endEpoch, itsType, theBody)`（第 44 行）。`.cpp` 的 `GetReportString` 输出"事件类型 + 掩体名 + 起止时刻 + 时长"。

##### event/EclipseTotalEvent.hpp / .cpp

职责：阴影事件容器（把多个单次阴影按时间顺序合并成一次"总事件"）。`.hpp` 成员 `theEvents`（`std::vector<EclipseEvent*>`）、`numEvents`、`theIndex`（第 73–77 行）；接口 `AddEvent/SetEvent/NumberOfEvents/GetDuration/SetIndex/GetEvent/GetReportString/TakeAction`（第 49–69 行）。`.cpp` 中 `GetDuration` 取最早开始与最晚结束之差；`TakeAction("Clear")` 释放子事件。

##### event/IntrusionEvent.hpp / .cpp

职责：单次侵入事件，携带逐点采样数据。`.hpp` 成员 `intrudingBody`、`intrusionType`（`Intrusion/Occultation/Transit`），以及逐点数组 `epochs/angDiameter/angLoc1/angLoc2/illmnVals`（第 66–78 行）与 `skipFirstLine/skipLastLine`（第 79–80 行）；接口 `GetNumIndividualEvents/GetIntrusionType/GetReportString/SetSkipFirstLine/SetSkipLastLine`（第 56–62 行）。构造函数接收完整数组（第 47–49 行）。`.cpp` 第 212 行 `GetIntrusionType` 返回侵入类型字符串。

##### event/IntrusionResult.hpp / .cpp

职责：单传感器的侵入结果容器。`.hpp` 成员 `theEvents`（`std::vector<IntrusionEvent*>`）、`coord1Name/coord2Name/scName/sensorName/coordType`（第 84–98 行）；接口 `AddEvent/NumberOfTotalEvents/NumberOfIndividualEvents/SetSpacecraftName/SetSensorName/SetCoordinateType/SetCoordinateNames/GetDuration/GetEvent/GetReportString/TakeAction`（第 52–80 行）。`.cpp` 的 `GetReportString` 按侵入类型（`Occultation`/`Transit`/`Intrusion`）区分输出（第 172–176、352–354 行）。

##### locator/ContactLocator.hpp / .cpp

职责：接触定位器（本插件最复杂的定位器）。`.hpp` 成员 `observerNames/observers`（观测站，第 163–165 行）、`directObserversNames/directObserversHostIndex/directObservers/observedRegions`（第 169–175 行，区分"直接观测者"=带视场成像仪或无 FOV 的地面站）、`lightTimeDirection`（第 178 行）、报告控制 `leftJustified/reportPrecision/reportColumnsInOrder/reportIntervals/intervalStep/reportTimeFormat/reportTemplateFormat`（第 180–192 行）、结果容器 `contactResults`（第 194 行）、SPICE 相关 `spice/spiceInstNames/fkFileName/ikFileName`（第 201–206 行）；参数 ID 枚举 `STATIONS/LIGHT_TIME_DIRECTION/LEFT_JUSTIFIED/REPORT_PRECISION/REPORT_TEMPLATE_FORMAT/INTERVAL_STEP/REPORT_TIME_FORMAT`（第 212–221 行）。`.cpp` 参数表 `Observers/LightTimeDirection/LeftJustified/ReportPrecision/ReportFormat/IntervalStepSize/ReportTimeFormat`（第 63–85 行）。`FindEvents()`（第 2310 行起）对每个观测者取 NAIF ID 与最小仰角（第 2372–2390 行），排除中心天体作为遮挡体（第 2393–2417 行），调用 `em->GetContactIntervals(...)`（第 2437–2439 行）得到接触区间，再用 `reclat_c` 计算每个接触起止/最大仰角时刻的方位角、仰角、距离（第 2482、2516、2542、2577 行）填入 `ContactEvent`。

##### locator/EclipseLocator.hpp / .cpp

职责：阴影定位器。`.hpp` 成员 `eclipseTypes`（第 105 行）、`sun`（第 107 行）、结果 `theEvents`（`std::vector<EclipseTotalEvent*>`）、`maxIndex/maxDuration`（第 109–113 行）、`defaultEclipseTypes`（第 115 行）；参数 ID `ECLIPSE_TYPES`（第 119–123 行）。`.cpp` 参数表仅 `EclipseTypes`（`STRINGARRAY_TYPE`，第 67–77 行），构造函数默认 `Umbra/Penumbra/Antumbra`（第 100–102 行）。`FindEvents()`（第 851 行起）对每个掩体天体与每种阴影类型调用 `em->GetOccultationIntervals(...)`（第 915–919 行），把返回的起止区间包装成 `EclipseEvent` 加入 `rawList`，随后按开始时刻冒泡排序（第 968–981 行），再用 `EclipseTotalEvent` 把重叠事件合并/嵌套（第 997 行起，嵌套逻辑 `GetNestedEvents` 见 `.hpp` 第 133 行）。

##### locator/IntrusionLocator.hpp / .cpp

职责：侵入定位器。`.hpp` 成员 `sensorNames/sensors`（第 151–153 行）、`centralBodyName/centralBody`（第 155–157 行）、`intrudingBodyNames/intrudingBodies`（第 159–161 行）、`minimumPhase`（第 163 行）、`reportCoordinates`（第 165 行）、`spice`（第 167 行）、结果 `intrusionResults`（第 169 行）、`gridFrameFile/instFKFileNames/scFKFileName/ikFileNames`（第 171–177 行）；参数 ID `SENSORS/CENTRAL_BODY/INTRUDING_BODIES/MINIMUM_PHASE/REPORT_COORDINATES/SPICE_GRID_FRAME_FILE`（第 184–192 行）。`.cpp` 参数表同名（第 58–78 行），构造函数默认 `centralBodyName="Earth"`、`reportCoordinates="SensorFrame"`、`stepSize=10`（第 94–99、112 行）。`FindEvents()`（第 1831 行起）对每个传感器构造 `instName = SC_SENSOR`（第 1846–1847 行），计算 `maxPhaseAngle = PI*(1-minimumPhase)`（第 1872 行），调用 `em->GetIntrusionIntervals(...)`（第 1889–1892 行），再对区间内每个中间时刻取目标相对位置 `em->GetTargetPosition`（第 1913–1914 行）并计算角直径与角坐标（第 1917–1943 行）填入 `IntrusionEvent`。`WriteFixedGridSPK`（`.hpp` 第 179 行）与 `spkw08_c`/`spkopn_c` 等调用（`.cpp` 第 2050–2130 行）用于固定网格坐标时写出 SPK 帧内核。

#### 关键类深读：事件定位原理（扫描 + SPICE GF 寻根）

`EventLocator` 基类（core）把"何时定位"与"如何定位"分开。`LocateEvents()`（`src/base/event/EventLocator.cpp` 第 1795 行）先 `ProvideEphemerisData` 让航天器星历可用（第 1798 行注释），随后调用纯虚 `FindEvents()`（第 1913 行），最后 `ReportEventData` 写报告（第 1915 行起）。三个派生类的 `FindEvents()` 都不实现自己的穿越寻根，而是把区间与 `stepSize` 交给 `EphemManager` 的 SPICE GF 封装：

1. **地影（`gfoclt_c` 掩星查找）**：`EclipseLocator::FindEvents`（第 851 行）→ `em->GetOccultationIntervals(eclipseType, ...)`（第 915 行）→ core `EphemManager::GetOccultationIntervals` 内 `gfoclt_c(...)`（`EphemManager.cpp` 第 609 行）。SPICE 按 `stepSize` 粗扫阴影函数变号区间，再细化穿越时刻。
2. **接触（`gfposc_c` 仰角约束 + `gfoclt_c` 视线遮挡）**：`ContactLocator::FindEvents`（第 2310 行）→ `em->GetContactIntervals(...)`（第 2437 行）→ `gfposc_c`（`EphemManager.cpp` 第 824 行，用 `relate=">"` 约束仰角大于最小仰角），若存在掩体则叠加 `gfoclt_c`（第 894 行）排除视线被遮挡的时段。
3. **侵入（`gfoclt_c` 视场掩星）**：`IntrusionLocator::FindEvents`（第 1831 行）→ `em->GetIntrusionIntervals(...)`（第 1889 行）→ `gfoclt_c`（`EphemManager.cpp` 第 1223/1247 行），以传感器视场为"前"、侵入天体为"后"查找掩星区间，并按相位角阈值过滤。

`stepSize`（默认 10 s）作为 SPICE GF 的扫描步长，从基类参数表 `StepSize`（`EventLocator.cpp` 第 78、95 行）传入，直接决定搜索分辨率。运行模式 `RunMode` 枚举 `Automatic/Manual/Disabled`（`EventLocator.cpp` 第 104–109 行）控制是任务结束自动定位、命令触发还是禁用。

**Event 类与 LocatedEvent 的关系**：`LocatedEvent`（core）只提供 `start/end/duration` 与纯虚 `GetReportString()`；本插件的六个 `*Event`/`*Result` 类都继承它，其中 `*Result`（`ContactResult`/`EclipseTotalEvent`/`IntrusionResult`）是"聚合容器"——内部 `std::vector<*Event*>` 持有子事件，`AddEvent` 时扩展总时长，`GetReportString` 递归渲染子事件行。`ContactEvent` 额外携带 AER 采样序列与最大仰角，`IntrusionEvent` 携带逐点角直径/角坐标/照度序列，供报告逐点输出。

#### 参数表（各定位器脚本参数）

`EventLocator` 基类参数（`src/base/event/EventLocator.cpp` 第 70–102 行）：`Spacecraft`(`OBJECT_TYPE`)、`Filename`(`FILENAME_TYPE`)、`OccultingBodies`(`OBJECTARRAY_TYPE`)、`InputEpochFormat`(`STRING_TYPE`)、`InitialEpoch`(`STRING_TYPE`)、`StepSize`(`REAL_TYPE`，默认 10)、`FinalEpoch`(`STRING_TYPE`)、`UseLightTimeDelay`(`BOOLEAN_TYPE`)、`UseStellarAberration`(`BOOLEAN_TYPE`)、`WriteReport`(`BOOLEAN_TYPE`)、`RunMode`(`ENUMERATION_TYPE`)、`UseEntireInterval`(`BOOLEAN_TYPE`)。

| 定位器 | 新增参数 | 类型 | 行号（`.cpp`） |
| --- | --- | --- | --- |
| `ContactLocator` | `Observers` / `LightTimeDirection` / `LeftJustified` / `ReportPrecision` / `ReportFormat` / `IntervalStepSize` / `ReportTimeFormat` | OBJECTARRAY / ENUM(`Transmit`,`Receive`) / BOOLEAN / INTEGER / STRING / REAL / STRING | 第 63–85 行 |
| `EclipseLocator` | `EclipseTypes` | STRINGARRAY（默认 Umbra/Penumbra/Antumbra） | 第 67–77 行 |
| `IntrusionLocator` | `Sensors` / `CentralBody` / `IntrudingBodies` / `MinimumPhase` / `ReportCoordinates` / `SpiceGridFrameFile` | OBJECTARRAY / OBJECT / OBJECTARRAY / REAL / STRING / STRING | 第 58–78 行 |

#### 与 core 的扩展点

- 继承 `src/base/event/EventLocator.hpp` 的 `EventLocator`（`GmatBase` 子类），须重写纯虚 `FindEvents()`（基类第 287 行）与可选的 `Initialize()/ReportEventData()`。
- 继承 `src/base/event/LocatedEvent.hpp` 的 `LocatedEvent`，须重写纯虚 `GetReportString()`（基类第 58 行）。
- 继承 `src/base/factory/Factory.hpp` 的 `Factory`，须重写 `CreateObject`（另提供 `CreateEventLocator`）。
- 实际几何计算经 `src/base/subscriber/EphemManager.hpp` 的 `GetOccultationIntervals/GetContactIntervals/GetIntrusionIntervals` 委托 SPICE GF（`gfoclt_c`/`gfposc_c`），SPICE 接口在 `src/base/util/SpiceInterface.hpp`。

#### 文件清单附录

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `plugins/EventLocatorPlugin/src/base/CMakeLists.txt` | 构建脚本 | `SET(TargetName EventLocator)`、`PLUGIN_SRCS` |
| `plugins/EventLocatorPlugin/src/base/include/EventLocatorDefs.hpp` | DLL 导出宏 | `LOCATOR_API` |
| `plugins/EventLocatorPlugin/src/base/factory/EventLocatorFactory.hpp` | 工厂声明 | `EventLocatorFactory` |
| `plugins/EventLocatorPlugin/src/base/factory/EventLocatorFactory.cpp` | 工厂实现 | `CreateEventLocator`、`creatables` |
| `plugins/EventLocatorPlugin/src/base/plugin/GmatPluginFunctions.hpp` | 加载接口声明 | `GetFactoryCount` 等 |
| `plugins/EventLocatorPlugin/src/base/plugin/GmatPluginFunctions.cpp` | 加载接口实现 | `GetFactoryPointer` |
| `plugins/EventLocatorPlugin/src/base/event/ContactEvent.hpp` | 接触事件声明 | `ContactEvent`、AER 采样成员 |
| `plugins/EventLocatorPlugin/src/base/event/ContactEvent.cpp` | 接触事件实现 | `GetReportString`、`GetAERString` |
| `plugins/EventLocatorPlugin/src/base/event/ContactResult.hpp` | 接触结果容器声明 | `ContactResult` |
| `plugins/EventLocatorPlugin/src/base/event/ContactResult.cpp` | 接触结果容器实现 | `AddEvent`、`GetDuration` |
| `plugins/EventLocatorPlugin/src/base/event/EclipseEvent.hpp` | 阴影事件声明 | `EclipseEvent` |
| `plugins/EventLocatorPlugin/src/base/event/EclipseEvent.cpp` | 阴影事件实现 | `GetReportString` |
| `plugins/EventLocatorPlugin/src/base/event/EclipseTotalEvent.hpp` | 阴影容器声明 | `EclipseTotalEvent` |
| `plugins/EventLocatorPlugin/src/base/event/EclipseTotalEvent.cpp` | 阴影容器实现 | `AddEvent`、`GetDuration` |
| `plugins/EventLocatorPlugin/src/base/event/IntrusionEvent.hpp` | 侵入事件声明 | `IntrusionEvent`、逐点数组成员 |
| `plugins/EventLocatorPlugin/src/base/event/IntrusionEvent.cpp` | 侵入事件实现 | `GetIntrusionType`、`GetReportString` |
| `plugins/EventLocatorPlugin/src/base/event/IntrusionResult.hpp` | 侵入结果容器声明 | `IntrusionResult` |
| `plugins/EventLocatorPlugin/src/base/event/IntrusionResult.cpp` | 侵入结果容器实现 | `AddEvent`、`GetReportString` |
| `plugins/EventLocatorPlugin/src/base/locator/ContactLocator.hpp` | 接触定位器声明 | `ContactLocator`、`FindEvents` |
| `plugins/EventLocatorPlugin/src/base/locator/ContactLocator.cpp` | 接触定位器实现 | `FindEvents`、`GetContactIntervals`、`reclat_c` |
| `plugins/EventLocatorPlugin/src/base/locator/EclipseLocator.hpp` | 阴影定位器声明 | `EclipseLocator`、`GetNestedEvents` |
| `plugins/EventLocatorPlugin/src/base/locator/EclipseLocator.cpp` | 阴影定位器实现 | `FindEvents`、`GetOccultationIntervals` |
| `plugins/EventLocatorPlugin/src/base/locator/IntrusionLocator.hpp` | 侵入定位器声明 | `IntrusionLocator`、`WriteFixedGridSPK` |
| `plugins/EventLocatorPlugin/src/base/locator/IntrusionLocator.cpp` | 侵入定位器实现 | `FindEvents`、`GetIntrusionIntervals`、`spkw08_c` |

### 13.8 ExtendedKalmanFilterPlugin（扩展卡尔曼滤波与平滑器）

**目录**：`plugins/ExtendedKalmanFilterPlugin/`
**构建开关**：`PLUGIN_EKF`（ON，见 `plugins/CMakeLists.txt` 第115行 `OPTION(PLUGIN_EKF "EKF Plugin" ON)`；第189行 `if (PLUGIN_EKF)` 作为分支条件）
**目标库名**：`EKF`（`plugins/ExtendedKalmanFilterPlugin/src/base/CMakeLists.txt` 第30行 `SET(TargetName EKF)`；第74行将 DLL 导出宏重命名为 `KALMAN_EXPORTS`；第78行链接 `GmatEstimation`）
**一句话目的**：提供顺序（序贯）估计基础设施 `SeqEstimator`、扩展卡尔曼滤波器 `ExtendedKalmanFilter`、反向平滑器 `Smoother`/`RunSmoother`，以及与顺序估计配套的过程噪声模型（SNC/Linear）和可估参数模型（一阶高斯-马尔可夫），实现单次遍历（one-pass）的在线轨道确定与事后平滑。

#### 目的与职责

`EstimationPlugin` 的批处理最小二乘（`BatchLeastSquares`）需要对整段测量数据反复迭代求残差偏导数，而顺序估计器（sequential estimator）则按时间顺序只处理一次测量流：在两次测量之间用传播器做**时间更新（预测）**，在每条测量到达时做**量测更新（校正）**，因此天然适合在线/近实时定轨。`ExtendedKalmanFilter` 是这类顺序估计器的一个具体实现——它把非线性动力学 `f(·)` 与非线性量测模型 `h(·)` 在当前状态附近线性化（用状态转移矩阵 Φ 与量测偏导数矩阵 H 近似），套用线性卡尔曼滤波五方程。

本插件与 `EstimationPlugin` 的关系是：`SeqEstimator` 继承自 `EstimationPlugin` 中的 `Estimator`（`plugins/EstimationPlugin/src/base/estimator/Estimator.hpp` 第54行 `class ESTIMATION_API Estimator : public Solver`），因此复用了整套 `EstimationStateManager`（求解向量/协方差/状态映射）、`MeasurementManager`（观测管理、残差计算、sigma 编辑）和报表/Matlab 输出管线；本插件在其上追加了顺序估计特有的**有限状态机**（`SeqEstimator::AdvanceState()`）、**过程噪声 Q 与状态转移矩阵 Φ 的构造**、以及**反向平滑器**（它把同一段数据再反向跑一遍滤波器，然后与正向结果做协方差/状态加权融合，得到整段弧段上精度更高的平滑轨迹）。插件还提供了两个独立的资源类族——`ProcessNoiseBase`（过程噪声模型）与 `EstimatedParameterModel`（被估参数模型），二者分别由 `ProcessNoiseModel` 与 `EstimatedParameter` 作为“容器/资源”对象持有，用于在滤波器中把非轨道量（大气阻力系数 `Cd`、大气密度标度因子等）连同其噪声一并纳入状态向量。

#### 导出类清单

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `SeqEstimator` | `Estimator`（`EKF/SeqEstimator.hpp:48`） | 顺序估计基类：状态机、时间/量测更新、过程噪声 Q 与 STM 管理 |
| `ExtendedKalmanFilter` | `SeqEstimator`（`EKF/ExtendedKalmanFilter.hpp:59`） | EKF 具体实现：量测更新五方程的平方根形式 |
| `SmootherBase` | `Estimator`（`smoother/SmootherBase.hpp:44`） | 平滑器基类：三态（FILTERING/SMOOTHING/PREDICTING）状态机 |
| `Smoother` | `SmootherBase`（`smoother/Smoother.hpp:42`） | 具体平滑器：正反向滤波结果融合 |
| `RunSmoother` | `RunEstimator`（`command/RunSmoother.hpp:46`） | 使命控制序列命令，驱动平滑器状态机 |
| `ProcessNoiseBase` | `GmatBase`（`noise/ProcessNoiseBase.hpp:42`） | 过程噪声模型基类（6×6 航天器噪声 + 坐标转换） |
| `SNCProcessNoise` | `ProcessNoiseBase`（`noise/SNCProcessNoise.hpp:40`） | 状态噪声补偿（State Noise Compensation）过程噪声 |
| `LinearProcessNoise` | `ProcessNoiseBase`（`noise/LinearProcessNoise.hpp:40`） | 线性时间增长的过程噪声 |
| `ProcessNoiseModel` | `GmatBase`（`noise/ProcessNoiseModel.hpp:42`） | 过程噪声的“资源/容器”对象，内嵌一个 `ProcessNoiseBase` |
| `EstimatedParameterModel` | `GmatBase`（`estimatedparam/EstimatedParameterModel.hpp:42`） | 被估参数模型基类（7×7 扩展噪声） |
| `FirstOrderGaussMarkov` | `EstimatedParameterModel`（`estimatedparam/FirstOrderGaussMarkov.hpp:40`） | 一阶高斯-马尔可夫（FOGM）参数模型 |
| `EstimatedParameter` | `GmatBase`（`estimatedparam/EstimatedParameter.hpp:41`） | 被估参数的“资源/容器”对象，内嵌一个 `EstimatedParameterModel` |

继承链完整标注（`ExtendedKalmanFilter → SeqEstimator → Estimator → Solver`）：`Estimator` 定义于 `plugins/EstimationPlugin/src/base/estimator/Estimator.hpp:54`，`Solver` 定义于 `src/base/solver/Solver.hpp`。`RunSmoother → RunEstimator → RunSolver`：`RunEstimator` 定义于 `plugins/EstimationPlugin/src/base/command/RunEstimator.hpp:51`。

#### 插件注册与工厂

`plugin/GmatPluginFunctions.cpp` 实现插件库入口三函数：`GetFactoryCount()`（第57~61行）返回 `7`；`GetFactoryPointer(Integer index)`（第74~108行）按 `switch` 索引依次构造 7 个工厂；`SetMessageReceiver()`（第121~124行）转发到 `MessageInterface`。工厂索引对应关系：

| index | 工厂 | createList（脚本可创建类型） |
| --- | --- | --- |
| 0 | `ExtendedKalmanFilterFactory` | `ExtendedKalmanFilter` |
| 1 | `ProcessNoiseModelFactory` | `ProcessNoiseModel` |
| 2 | `ProcessNoiseFactory` | `StateNoiseCompensation`（测试模式另有 `LinearTime`） |
| 3 | `SmootherFactory` | `Smoother` |
| 4 | `EKFCommandFactory` | `RunSmoother` |
| 5 | `EstimatedParameterFactory` | `EstimatedParameter` |
| 6 | `EstimatedParameterModelFactory` | `FirstOrderGaussMarkov` |

各工厂的 `Create*` 方法均在对应 `.cpp` 中按字符串分派：`ExtendedKalmanFilterFactory::CreateSolver`（`factory/ExtendedKalmanFilterFactory.cpp:74~132`，第102~103行 `if (ofType == "ExtendedKalmanFilter") return new ExtendedKalmanFilter(withName)`）；`ProcessNoiseFactory::CreateProcessNoise`（`factory/ProcessNoiseFactory.cpp:72~81`，第75~78行分派 `LinearTime`/`StateNoiseCompensation`）；`SmootherFactory::CreateSmoother`（`factory/SmootherFactory.cpp:66~72`）；`EKFCommandFactory::CreateCommand`（`factory/EKFCommandFactory.cpp:53~64`）；`EstimatedParameterModelFactory::CreateEstimatedParameterModel`（`factory/EstimatedParameterModelFactory.cpp:71~78`）。

#### 逐文件讲解

##### EKF/SeqEstimator.hpp

顺序估计基类声明（共352行）。关键点：
- 第48行 `class KALMAN_API SeqEstimator: public Estimator` 确立继承；第36~38行引入 `kalman_defs.hpp`、`Estimator.hpp`、`ProcessNoiseModel.hpp`。
- 第48~59行声明 `Initialize()`、`AdvanceState()`、`StateCleanUp()`、`Finalize()`、`IsFinalPass()` 等核心虚函数。
- 第93~130行定义 `FilterMeasurementInfoType`（继承 `MeasurementInfoType`，追加 `state`/`cov`/`sqrtCov`/`covVNB`/`scaledResid`/`kalmanGain`）；第133~158行定义 `UpdateInfoType`（时间/量测更新点的快照：`epoch`/`isObs`/`measStat`/`state`/`cov`/`sqrtCov`/`covVNB`/`processNoise`/`stm`），这两个结构是滤波器与平滑器之间传递“逐历元状态/协方差/增益”的核心数据载体。
- 第160~165行声明平滑器接口：`GetUpdateStats()`、`GetObjectBuffer()`、`SetAnchorEpoch()`、`SetCovariance()`、`UpdateInitialConditions()`。
- 第215~221行是时间更新协方差 `pBar`、过程噪声 `Q`、量测矩阵 `H`、单位阵 `I` 等关键矩阵成员；第229~230行 `std::map<GmatBase*, ProcessNoiseModel*> processNoiseModels` 保存每个航天器关联的过程噪声模型。
- 第250~263行枚举本类新增参数（`PROCESS_NOISE_TIME_STEP` 等 9 项，见“参数表”）；第275~349行声明状态机各阶段虚方法（`CompleteInitialization`/`FindTimeStep`/`CalculateData`/`ProcessEvent`/`CheckCompletion`/`RunComplete`/`PrepareForStep`/`FilterUpdate`/`UpdateProcessNoise`/`TimeUpdate`）。

##### EKF/SeqEstimator.cpp

顺序估计基类实现（共3573行）。关键点：
- 第83~95行静态参数文本 `PARAMETER_TEXT[]`、第97~109行 `PARAMETER_TYPE[]`。
- 第674~741行 `AdvanceState()`：顺序估计有限状态机。`switch(currentState)` 依次在 `INITIALIZING→CompleteInitialization()`、`PROPAGATING→FindTimeStep()`、`CALCULATING→CalculateData()`、`LOCATING→ProcessEvent()`、`ESTIMATING→Estimate()`、`CHECKINGRUN→CheckCompletion()`、`FINISHED→RunComplete()` 之间迁移；默认分支抛 `EstimatorException`。这是顺序估计区别于批处理的骨架——每推进一“步”就沿状态机走一段。
- 第1084~1378行 `CompleteInitialization()`：初始化核心。第1095~1096行取 `esm.GetState()` 并记录 `stateSize`；第1119~1120行用首航天器历元设 `estimationEpochGT`/`currentEpochGT`；第1122~1134行禁用 `KeplerianState`/`PassBiases` 求解；第1143~1148行禁用 SN 类测量模型；第1174~1189行从每个航天器读入关联的 `ProcessNoiseModel`（`processNoiseModels[sat] = noiseModel`）；第1253~1258行给 `pBar`/`Q`/`residuals`/`x0bar`/`dx` 设置尺寸；第1331~1348行按“下一测量历元 vs 下一噪声历元”选择进入 `CALCULATING` 或 `PROPAGATING`。
- 第1389~1456行 `FindTimeStep()`：PROPAGATING 状态核心。第1392~1398行若已到测量历元则转 `CALCULATING` 并调 `FilterUpdate()`；第1413~1433行在噪声更新历元调 `UpdateProcessNoise()`+`FilterUpdate()` 并推进 `nextNoiseUpdateGT`；第1438~1446行计算 `timeStep = min(至测量, 至噪声更新)`。
- 第1469~1527行 `UpdateProcessNoise()`：第1476行先清零 `Q`；第1478~1479行 `dt = |currentEpochGT - prevUpdateEpochGT|`；第1494行 `scNoise = noiseModel->GetProcessNoise(dt, currentEpochGT)`；第1513~1519行把 6×6 `scNoise` 累加进 `Q` 的对应位置子块。
- 第1540~1625行 `AddEstimatedParameterNoise()`：把 `EstimatedParameter`（如 `Cd`、密度标度因子）的 7×7 噪声（6 状态 + 1 参数）通过 `estParam->GetProcessNoise(dt, accelVector)`（第1606行）嵌入 `Q` 的对应行列（第1609~1622行）。
- 第1637~1685行 `TimeUpdate()`（基类版本，注释第1633行引用 Tapley eq. 4.7.1(b)）：第1649行注释 `// phi * P * phi^T + Q`；第1651~1655行计算坐标转换后的 `Q_S = dS_dX*Q*dS_dXᵀ` 与 `stm_S = dS_dX*(*stm)*dX_dS`；第1670行 `pBar = stm_S * P * stm_Sᵀ + Q_S`；第1684行 `Symmetrize(pBar)` 显式对称化。
- 第1880~1890行 `PrepareForStep()`：第1882行 `ResetSTM()`（每次传播步前把 STM 重置为单位阵）并回映射。
- 第1901~1938行 `FilterUpdate()`：顺序估计的“时间更新”动作——第1904~1907行映射 STM 后调 `UpdateProcessNoise()`+`TimeUpdate()`，第1909行 `(*stateCovariance->GetCovariance()) = pBar` 把时间更新协方差写回；第1912~1937行若非 `CALCULATING` 则记录 `UpdateInfoType` 快照（供平滑器使用）并 `PrepareForStep()` 重置 STM。
- 第2375~2407行 `DataFilter()`：sigma 编辑。第2381行 `Rbar = H*pBar*Hᵀ + R`，第2397~2399行若 `|O−C| ≥ constMult*σ` 则标记 `inUsed=false`、`removedReason="SIG"`。
- 第2355~2364行 `EstimationPartials()`：第2360~2362行把量测偏导数 `hMeas` 填入 `H`。

##### EKF/ExtendedKalmanFilter.hpp

EKF 类声明（共112行）。关键点：
- 第40~58行头部注释说明：实现遵循 Tapley, Schutz & Born (2004) 第212页流程图，加入两处 R. Carpenter 建议的改进——(1) 状态噪声协方差与时间更新协方差都显式强制对称；(2) 协方差更新可在简单形式 `P=(I−KH̃)P̄` 与 Bucy-Joseph 形式（4.7.19）之间选择（编译期，默认 Joseph）。
- 第72~74行成员：`Rvector yi`（O−C 残差）、`Rmatrix kalman`（卡尔曼增益）；第77~78行 `sqrtP`/`sqrtPupdate`（协方差的平方根/Cholesky 因子，EKF 采用**平方根滤波**数值格式）。
- 第80~96行私有方法 `SetupMeas()`/`ComputeObs()`/`ComputeGain()`/`UpdateElements()`/`AdvanceEpoch()`/`UpdateCovarianceSimple()`/`UpdateCovarianceJoseph()`，对应量测更新的各个步骤。

##### EKF/ExtendedKalmanFilter.cpp

EKF 具体实现（共1394行），是本插件最核心的文件。关键点：
- 第58~69行构造：`SeqEstimator("ExtendedKalmanFilter", name)`，第63行 `objectTypeNames.push_back("ExtendedKalmanFilter")`。
- 第165~202行 `CompleteInitialization()`：第173~178行校验协方差维度；第180行 `I = Rmatrix::Identity(stateSize)`；第183~188行若非平方根已存在则对先验协方差做 Cholesky 分解 `cf.Factor(...)` 得到 `sqrtP` 并转置（得到“上三角→下三角”约定）。
- 第212~328行 `Estimate()`（量测更新的总调度）：第243行 `SetupMeas()`，第257行 `ComputeObs(updateStat)`，第271行 `ComputeGain(updateStat)`，第285行 `UpdateElements(updateStat)`；第301行 `updateStats.push_back(updateStat)` 把本测量更新点快照入栈（平滑器依赖它）；第327行 `AdvanceEpoch()`。
- 第396~595行 `TimeUpdate()`（覆盖基类，用平方根 QR 形式做协方差预测，注释第392~393行指向 Brown & Hwang 4e 5.7 节）：第419~422行坐标转换后 `Q_S = dS_dX*Q*dS_dXᵀ`；第460行 `stm_S = dS_dX*(*stm)*dX_dS`；第477~521行对 `Q_S` 做 Cholesky（处理零对角行/列的压缩/扩张）；第523行 `stmP = stm_S*sqrtP`；第555行 `sqrtP = thinQR(stmP, sqrtQ)`；第579行 `pBar = sqrtP*sqrtPᵀ`；第582行 `Symmetrize(pBar)`。
- 第604~646行 `SetupMeas()`：第610行取有效测量列表，第615~616行 `measCount`/`calculatedMeas`，第629~631行由 `sqrtP` 还原 `pBar`，第634~638行按测量维度给 `measSize`/`H`/`yi`/`kalman` 定尺寸。
- 第656~741行 `ComputeObs()`：第664~665行 `CalculateResiduals(measStat)` 计算 O−C；第681~685行把残差写入 `yi(k)`；第688行取量测噪声协方差 `R`；第695~701行逐元素计算标度残差 `Rbar = H*pBar*Hᵀ+R`、`σ=√Rbar(k,k)`、`scaledResid = residual[k]/σ`。
- 第759~816行 `ComputeGain()`：第767~781行 Lear 方法量测欠权；第784~788行对 `R` 做 Cholesky；第790~792行 `Sw = thinQR(sqrtScale*H*Spbar, Sr)`；第810行 `kalman = Spbar*Spbarᵀ*Hᵀ*(Sw*Swᵀ)⁻¹`（即 `K=P⁻Hᵀ(HP⁻Hᵀ+R)⁻¹` 的平方根形式）；第811行 `sqrtPupdate = thinQR((I−kalman*H)*Spbar, kalman*Sr)`。
- 第829~896行 `UpdateElements()`：第835行判断 `editFlag == NORMAL_FLAG`；第837行 `dx = kalman*yi`；第839~862行无状态偏移时直接 `estimationStateS[i] += dx[i]` 并回映射；第875~888行 `P2 = sqrtPupdate*sqrtPupdateᵀ`，`sqrtP = sqrtPupdate`，再写回 `stateCovariance`（即默认使用平方根更新结果，而非 Simple/Joseph 全矩阵式）。
- 第906~915行 `UpdateCovarianceSimple()`：第914行 `P = (I − K*H)*Pbar`。
- 第927~952行 `UpdateCovarianceJoseph()`：第937~939行 `P = (I−KH)P̄(I−KH)ᵀ + KRKᵀ`（Bucy-Joseph，数值上更稳健）。
- 第954~1048行 `AdvanceEpoch()`：第972行 `measManager.AdvanceObservation()` 推进到下一条测量，第979行取 `nextMeasurementEpochGT`；第982~1017行处理 `DelayRectifyTimeSpan` 的延迟整流（把状态偏移并入标称状态并清零偏移）；第1029行 `FindTimeStep()`。
- 第1385~1392行 `UpdateCov()`：仅推进协方差（不更新状态、不发布），供平滑器/预测阶段使用。

##### command/RunSmoother.hpp / command/RunSmoother.cpp

平滑器驱动命令。`RunSmoother` 继承 `RunEstimator`（`command/RunSmoother.hpp:46`），因此复用了 `RunEstimator` 对 Solver 状态机的命令侧动作；`RunSmoother.hpp` 第59~66行覆盖 `PrepareToEstimate()`/`Propagate()`/`Calculate()`/`IsSmootherPredicting()`。

`RunSmoother.cpp` 关键点：
- 第126~170行 `Initialize()`：第136行取平滑器内嵌 `SeqEstimator` 的名字，第139~163行向前遍历使命控制序列中前一个 `RunEstimator` 命令，找到使用该 `SeqEstimator` 的正向滤波器后，第152行 `forwardFilterInfo = ((SeqEstimator*)obj)->GetUpdateStats()`、第153行 `SetForwardFilterInfo(forwardFilterInfo)`、第156~157行 `GetObjectBuffer`/`SetObjectBuffer`——把正向滤波的逐历元统计快照与对象缓冲区传递给平滑器。
- 第181~242行 `LoadSolveForsToFilterESM()`：把求解向量/力模型求解参数装入平滑器内部滤波器的 `EstimationStateManager`。
- 第256~337行 `PrepareToEstimate()`：装配求解对象后第329行 `((Smoother*)theEstimator)->PrepareFilter()`，再调基类。
- 第350~385行 `Propagate()`：`FILTERING`/`PREDICTING` 态走 `RunEstimator::Propagate()`（真实传播）；`SMOOTHING` 态不积分，而是第373行 `MoveToNext(false)` 直接跳到下一平滑点。
- 第395~451行 `Calculate()`：`FILTERING` 态缓存 PSM 状态到 `measStates`；`SMOOTHING` 态按历元回填 PSM 状态并 `MapVectorToObjects()`。

##### estimatedparam/EstimatedParameter.hpp / .cpp

被估参数“资源”对象（共133/758行）。它继承 `GmatBase`，内嵌一个 `EstimatedParameterModel *estimatedParameterModel`（默认构造为 `FirstOrderGaussMarkov`，`EstimatedParameter.cpp:82`）。参数枚举 `EST_PARAM_TYPE`/`SOLVE_FOR`/`VALUE`/`SIGMA`/`HALF_LIFE`（`EstimatedParameter.hpp:107~117`），其中 `SOLVE_FOR`/`VALUE`/`SIGMA`/`HALF_LIFE` 是“owned 参数”，`Get/Set*Parameter` 都通过 `GetOwnedObjectId()` 转发到内嵌模型（`EstimatedParameter.cpp:556~598`）。第164~171行 `GetProcessNoise()` 转发到模型；第183~187行 `SetConversionFactor()` 转发。第199~219行 `SetEstimatedParameterModel()` 用 `Clone()` 替换内嵌模型。第666~713行 `SetStringParameter(SOLVE_FOR)` 校验求解变量名不与自身同名、且在允许列表内。

##### estimatedparam/EstimatedParameterModel.hpp / .cpp

被估参数模型基类（共110/322行）。继承 `GmatBase`；成员 `shortName`（脚本短名）、`solveFor`（求解变量名）、`allowedSolveFors`（允许的求解变量列表）、`convFactor`（epsilon↔标称转换因子，默认 1.0）。第55~56行声明纯虚 `GetProcessNoise(GmatEpoch, const Real accelVector[3])`；第58行 `SetConversionFactor()`。`EstimatedParameterModel.cpp:264~293` 的 `SetStringParameter(SOLVE_FOR)` 在 `allowedSolveFors` 中查找并校验。

##### estimatedparam/FirstOrderGaussMarkov.hpp / .cpp

一阶高斯-马尔可夫参数模型（共97/414行），实现为 `EstimatedParameterModel`。成员 `steadyStateValue`/`steadyStateSigma`/`halfLife`（默认 1.0/0.1/7200 s，见 `FirstOrderGaussMarkov.cpp:67~72`）；`allowedSolveFors` 为 `{"Cd","AtmosDensityScaleFactor"}`（第75~76行）。核心在第147~234行 `GetProcessNoise()`：第156行 `tau = halfLife/ln(2)`；第163~164行计算指数项；第166~167行 `sigma2 = 2*σ_ss²/(convFactor²*tau)`；第169~172行加速度外积 `accelOuterMatrix`；第177~210行按 `|dt/tau|` 阈值选择解析式或泰勒级数式（避免小 `dt` 下的指数精度损失）计算 `gamma_pp/pv/pa/vv/va/aa` 六个系数；第213~231行组装 7×7 噪声矩阵（前 6 维是位置/速度受加速度过程驱动，第 7 维是 FOGM 参数自相关），第231行 `result(6,6)=sigma2*gamma_aa`。

##### estimatedparam/EstimatedParameterException.hpp

极简异常类（共42行）：第36~41行 `EstimatedParameterException : public BaseException`，前缀 `"EstimatedParameter Exception: "`。

##### factory/*（7 个工厂，14 个文件）

见“插件注册与工厂”一节。每个工厂 `.hpp` 声明 `Factory` 派生类与 `Create*` 方法，`.cpp` 实现字符串分派与 `creatables` 列表。`ExtendedKalmanFilterFactory` 额外实现 `DoesObjectTypeMatchSubtype()`（`factory/ExtendedKalmanFilterFactory.cpp:270~282`）与 `CreateSolver()`；其余工厂（`ProcessNoiseModelFactory`/`EstimatedParameterFactory`/`ProcessNoiseFactory`/`SmootherFactory`/`EstimatedParameterModelFactory`/`EKFCommandFactory`）结构对称。

##### include/kalman_defs.hpp

导入/导出宏（共78行）。第37~72行针对 Windows/`_MSC_VER` 定义 `WIN32_LEAN_AND_MEAN` 与 `_USE_MATH_DEFINES`，并在 `_DYNAMICLINK`+`KALMAN_EXPORTS` 时定义 `KALMAN_API=__declspec(dllexport)`（否则 `dllimport`）；第74~76行非 Windows 平台把 `KALMAN_API` 置空。`KALMAN_EXPORTS` 由 `src/base/CMakeLists.txt:74` 的 `DEFINE_SYMBOL "KALMAN_EXPORTS"` 提供。

##### noise/ProcessNoiseBase.hpp / .cpp

过程噪声模型基类（共126/630行）。继承 `GmatBase`；第57行声明纯虚 `GetProcessNoise(const GmatEpoch, const GmatTime&)`（返回 `Rmatrix66`）。成员 `shortName`、`solarSystem`、`coordinateSystem`/`j2k`。参数仅 `COORD_SYS`（`ProcessNoiseBase.hpp:110~114`）。`ProcessNoiseBase.cpp:181~201` `Initialize()` 用 `coordinateSystem->GetJ2000Body()` 创建 J2000 惯性系 `j2k`；第214~271行与第286~343行两个 `ConvertMatrix()` 重载（`GmatTime`/`Real`）把输入系下的协方差 `mat = T*mat*Tᵀ` 旋转到惯性系（第242~253行把 3×3 旋转矩阵扩展成 6×6 分块对角变换，位置/速度同转）。第45行参数 `"CoordinateSystem"`，默认 `"EarthMJ2000Eq"`。

##### noise/SNCProcessNoise.hpp / .cpp

状态噪声补偿（State Noise Compensation）模型（共136/712行）。脚本短名 `"StateNoiseCompensation"`（`SNCProcessNoise.cpp:74`）。参数 `ACCEL_SIGMA_VECTOR`（加速度噪声 σ，默认 `{1e-8,1e-8,1e-8}`，第80行）与只读的 `ELAPSED_TIME`/`CURRENT_EPOCH`/`CURRENT_EPOCH_GT`/`CURRENT_NOISE_MAT`。核心在第180~219行 `GetProcessNoise()`：第185~186行 `dt2=dt²`、`dt3=dt³`；第188~194行按连续加速度随机游走模型填充 6×6 分块——
```
Q_pp = σ_a²·dt³/3,  Q_pv = Q_vp = σ_a²·dt²/2,  Q_vv = σ_a²·dt
```
——第207行 `ConvertMatrix(result, epoch)` 把结果旋转到惯性系。第233~278行为 `Real` 重载，额外把结果存入 `currentProcessNoise`。

##### noise/LinearProcessNoise.hpp / .cpp

线性时间增长模型（共103/374行）。脚本短名 `"LinearTime"`（`LinearProcessNoise.cpp:63`）。参数 `RATE_VECTOR`（6 维速率，默认全 0）。第133~142行 `GetProcessNoise()`：`result(ii,ii) = (rateVec(ii)*dt)²`（纯对角），第140行坐标转换。仅在测试运行模式下加入 `creatables`（`factory/ProcessNoiseFactory.cpp:99~103`）。

##### noise/ProcessNoiseModel.hpp / .cpp

过程噪声“资源/容器”对象（共161/938行）。继承 `GmatBase`，内嵌 `ProcessNoiseBase *noiseModel`（默认 `new SNCProcessNoise("")`，`ProcessNoiseModel.cpp:90`）。参数 `NOISE_TYPE`/`UPDATE_TIME_STEP`（自有）+ `COORD_SYS`/`RATE_VECTOR`/`ACCEL_SIGMA_VECTOR`（owned，转发给内嵌模型，`ProcessNoiseModel.hpp:135~144`）。`GetProcessNoise()`（第191~199行）转发到 `noiseModel->GetProcessNoise()`；`SetNoiseModel()`（第211~231行）用 `Clone()` 替换。`GetOwnedObjectId()`（第917~938行）把 owned 参数 id 映射到内嵌对象的真实参数 id。`UpdateTimeStep` 为负时抛 `NoiseException`（第646~650行）。

##### noise/NoiseException.hpp

异常类（共42行）：第36~41行 `NoiseException : public BaseException`，前缀 `"Noise Exception: "`。

##### plugin/GmatPluginFunctions.hpp / .cpp

见“插件注册与工厂”。

##### smoother/SmootherBase.hpp / .cpp

平滑器基类（共286/2917行）。继承 `Estimator`。第48~54行枚举三态 `SmootherState { FILTERING, SMOOTHING, PREDICTING, UNDEFINED_STATE }`。第141~147行成员 `SeqEstimator *filter`（内嵌的正向/反向滤波器）、`forwardFilterInfo`/`backwardFilterInfo`（正/反向逐历元快照）、`filterIndex`。第174~180行参数 `FILTER`/`DELAY_FILTER_RECTIFY_TIME`/`MEAS_DEWEIGHT_THRESHOLD_FILTER`/`MEAS_DEWEIGHT_COEFF_FILTER`。第256行声明纯虚 `SmoothState(...)`。

`SmootherBase.cpp` 关键点：
- 第738~800行 `AdvanceState()`：与 `SeqEstimator` 同构的状态机，但第740行先 `filter->UpdateCurrentEpoch(currentEpochGT)`。
- 第1443~1631行 `CompleteInitialization()`：第1506~1510/1596~1598行对内部滤波器 `TakeAction("RunBackwards")`、`TakeAction("UseProvidedFlags")`；第1602~1623行把正向滤波的编辑标志复制给反向滤波器；第1626行 `filter->CompleteInitialization()`、第1627行 `filter->SetAnchorEpoch(forwardFilterInfo[0].epoch, true)`。
- 第1369~1410行 `UpdateInitialConditions()`：第1382~1388行取正向滤波末端协方差并放大 `1e10` 作为反向滤波初始协方差（第1388行），第1395~1402行对非轨道状态元素再放大 `1e4`——即反向滤波的“信息先验接近零”，避免双计数。
- 第1782~1880行 `Estimate()`：`FILTERING` 态调 `filter->Estimate()`（反向滤波）；`SMOOTHING` 态第1799~1848行计算残差后第1847行 `SmoothState(smootherStat, true)` 融合正反向结果。
- 第1892~1958行 `CheckCompletion()`：反向滤波 `FINISHED` 后第1925行 `backwardFilterInfo = filter->GetUpdateStats()`，第1929行 `MoveToNext(false)`，第1931行 `smootherState = SMOOTHING`。
- 第2032~2059行 `SmootherUpdate()`、第2069~2087行 `AdvanceEpoch()`（第2071行 `filterIndex++`，第2074~2077行到达末尾转 `CHECKINGRUN`）。

##### smoother/Smoother.hpp / .cpp

具体平滑器（共67/451行），实现纯虚 `SmoothState()`。核心：
- 第159~229行 `SmoothState()`：第161~162行用 `FindIndex()` 对齐正反向快照索引；第164~171行取正/反向状态与协方差平方根；第187~201行分别组合“后验/先验”两对（测量更新点用 forward 后验 × backward 先验，或 forward 先验 × backward 后验）；第216~219行对非测量点直接 `SmoothCovState(forwardSqrtCov, backwardSqrtCov, ...)`。
- 第300~315行 `SmoothCovState()`：平方根形式的两滤波器信息融合。第302行 `Rd = thinQR(Ra, Rb)`（合并平方根），第303行 `Sd = Rd.Inverse()`，第304~305行 `Ua=Sd*Ra`、`Ub=Sd*Rb`，第306行 `Mc = thinQR(Rb*Ubᵀ*Ua, Ra*Uaᵀ*Ub)`，第308~310行 `cov = Mc*Mcᵀ` 并对称化，第312~314行 `state = Xa + Ra*Uaᵀ*(Sd*(Xb−Xa))`。
- 第326~372行 `FindIndex()`：先在按历元排序的向量上做二分查找（第337~351行），漏配时退化为线性扫描（第355~365行）。
- 第383~402行 `ObsMatch()`：靠 `isObs` 与 `recNum` 判两条快照是否为同一测量。

#### 关键类深读

##### SeqEstimator：顺序估计器结构

`SeqEstimator` 通过 `AdvanceState()`（`SeqEstimator.cpp:674~741`）实现顺序估计有限状态机，状态迁移见下表：

| 状态 | 进入动作 | 迁移去向 |
| --- | --- | --- |
| `INITIALIZING` | `CompleteInitialization()` | 由末历元决定 `CALCULATING` 或 `PROPAGATING` |
| `PROPAGATING` | `FindTimeStep()` | 到测量→`CALCULATING`；到噪声更新→先 `FilterUpdate()` 再继续传播；到末尾→`CHECKINGRUN` |
| `CALCULATING` | `CalculateData()` | 有事件→`LOCATING`，否则→`ESTIMATING` |
| `LOCATING` | `ProcessEvent()` | 事件全部定位→`ESTIMATING` |
| `ESTIMATING` | `Estimate()`（EKF 覆盖） | →`PROPAGATING`（`AdvanceEpoch()`） |
| `CHECKINGRUN` | `CheckCompletion()` | →`FINISHED` |
| `FINISHED` | `RunComplete()` | 结束 |

**预测（Propagate）流程**：传播由 `PropSetup`/传播器在 PROPAGATING 状态完成（`RunEstimator` 命令读 `GetTimeStep()` 驱动积分）；估计器一侧的责任是维护协方差与 STM。每个传播步前 `PrepareForStep()`（`SeqEstimator.cpp:1880~1890`）把 STM 重置为单位阵；到达噪声更新历元时 `FilterUpdate()`（`SeqEstimator.cpp:1901~1938`）依次做 `MapObjectsToSTM()`→`UpdateProcessNoise()`（构造 `Q`）→`TimeUpdate()`（`pBar = ΦPΦᵀ + Q`）→把 `pBar` 写回 `stateCovariance`。

**更新（Update）流程**（EKF 覆盖，见下）。

**状态向量与协方差**：状态向量由 `EstimationStateManager`（`esm`）管理，`CompleteInitialization()` 第1095行 `estimationState = esm.GetState()`、第1096行 `stateSize = estimationState->GetSize()`；协方差通过 `stateCovariance->GetCovariance()` 访问。EKF 额外维护平方根因子 `sqrtP`（`ExtendedKalmanFilter.cpp:183~188`、`SetCovariance()` 第1368~1375行）。

##### ExtendedKalmanFilter：EKF 五方程在代码中的实现

EKF 的五个递推方程与代码对应如下（除状态传播外均位于 `ExtendedKalmanFilter.cpp`）：

1. **状态预测** x̂ₖ⁻ = f(x̂ₖ₋₁)。状态的非线性传播 `f(·)` 由传播器（ODE 积分）在 PROPAGATING 状态完成，EKF 本身不重复积分；EKF 只负责协方差的线性化传播（下一条）。状态在量测更新时才显式修正（见第 4 条 `dx` 累加）。

2. **协方差预测** Pₖ⁻ = ΦₖPₖ₋₁Φₖᵀ + Q。`ExtendedKalmanFilter::TimeUpdate()`（第396~595行）用平方根 QR 形式实现同一方程：第419~422行 `Q_S = dS_dX*Q*dS_dXᵀ`，第460行 `stm_S = dS_dX*(*stm)*dX_dS`，第523行 `stmP = stm_S*sqrtP`，第555行 `sqrtP = thinQR(stmP, sqrtQ)`，第579行 `pBar = sqrtP*sqrtPᵀ`，第582行 `Symmetrize(pBar)`。基类等价写法在 `SeqEstimator.cpp:1670`：`pBar = stm_S * P * stm_Sᵀ + Q_S`。其中 Φ 即状态转移矩阵 `*stm`，由 `EstimationStateManager` 在传播时累积。

3. **卡尔曼增益** K = Pₖ⁻Hᵀ(HPₖ⁻Hᵀ+R)⁻¹。`ComputeGain()`（第759~816行）：第788行 `cf.Factor(R, sqrtR_T)`，第790~792行 `Spbar=sqrtP`、`Sr=sqrtR_Tᵀ`、`Sw = thinQR(sqrtScale*H*Spbar, Sr)`，第810行 `kalman = Spbar*Spbarᵀ*Hᵀ*(Sw*Swᵀ)⁻¹`。`Sw*Swᵀ = H P⁻ Hᵀ + R`（第792行的 thinQR 保证），故第810行等价于 `K=P⁻Hᵀ(HP⁻Hᵀ+R)⁻¹`；`H` 在 `EstimationPartials()`（`SeqEstimator.cpp:2360~2362`）填入。

4. **状态更新** x̂ₖ = x̂ₖ⁻ + K(z−h(x̂ₖ⁻))。`UpdateElements()`（第829~896行）：残差/创新 `yi = z−h(x̂ₖ⁻)` 由 `ComputeObs()` 第681~685行填入（`yi(k) = measStat.residual[k]`）；第837行 `dx = kalman * yi`；第852~862行无偏移时 `estimationStateS[i] += dx[i]` 再 `esm.SetEstimationState(...)`/`MapVectorToObjects()` 写回。

5. **协方差更新** Pₖ = (I−KH)Pₖ⁻。默认在 `UpdateElements()` 第875~888行使用平方根结果 `P2 = sqrtPupdate*sqrtPupdateᵀ`（`sqrtPupdate` 在第811行由 `thinQR((I−kalman*H)*Spbar, kalman*Sr)` 得到，已内含 Joseph 的数值修正项）。两个显式全矩阵版本供编译期切换：`UpdateCovarianceSimple()` 第914行 `P=(I−K*H)*Pbar`；`UpdateCovarianceJoseph()` 第937~939行 `P=(I−KH)P̄(I−KH)ᵀ + KRKᵀ`。

##### 过程噪声模型与状态转移矩阵 Φ 的构造

- `ProcessNoiseBase`（`noise/ProcessNoiseBase.cpp`）负责坐标系：`Initialize()`（第181~201行）建立 J2000 惯性系 `j2k`，`ConvertMatrix()`（第214~271/286~343行）用 6×6 分块对角旋转把给定系下的 `Q` 变换到惯性系。
- `SNCProcessNoise::GetProcessNoise()`（`SNCProcessNoise.cpp:180~219`）按连续加速度随机游走给出 `Q_pp=σₐ²dt³/3`、`Q_pv=Q_vp=σₐ²dt²/2`、`Q_vv=σₐ²dt`。
- `LinearProcessNoise::GetProcessNoise()`（`LinearProcessNoise.cpp:133~142`）给对角元 `(r_i·dt)²`。
- `ProcessNoiseModel` 作为容器把上述模型暴露给脚本（`Type`/`UpdateTimeStep`/`CoordinateSystem`/`RateVector`/`AccelNoiseSigma`），`GetProcessNoise()` 转发（`ProcessNoiseModel.cpp:191~199`）。
- **Φ 的构造不在本插件**：状态转移矩阵 `stm` 由 `EstimationStateManager` 在传播过程中通过传播器对状态偏导数的数值积分累积（`SeqEstimator` 第1701行 `esm.MapObjectsToSTM()` 只是把对象侧 STM 汇总成全局 `*stm`），本插件负责在 `TimeUpdate()` 里把它与坐标转换矩阵 `dX_dS`/`dS_dX` 一起用于协方差传播（`ExtendedKalmanFilter.cpp:419~460`）。

##### EstimatedParameter / EstimatedParameterModel / FirstOrderGaussMarkov

三者构成“容器→抽象模型→具体模型”的委托链。`EstimatedParameter` 暴露 `Model`（类型）、`SolveFor`、`SteadyStateValue`、`SteadyStateSigma`、`HalfLife` 参数，实际存取全部委托给内嵌的 `FirstOrderGaussMarkov`（`EstimatedParameter.cpp:556~598`）。`FirstOrderGaussMarkov::GetProcessNoise()`（`FirstOrderGaussMarkov.cpp:147~234`）输出 7×7 矩阵：前 6×6 块把加速度过程噪声（含位置/速度交叉项）投影到被估参数对应的力方向，第 7 行/列与 `(6,6)` 元素是 FOGM 参数自相关（`gamma_aa`），从而把 `Cd` 等参数的时间演化噪声并入滤波器 `Q`（见 `SeqEstimator::AddEstimatedParameterNoise()`，`SeqEstimator.cpp:1540~1625`）。

##### Smoother / SmootherBase / RunSmoother：反向滤波平滑

平滑器整体流程：`RunSmoother` 先取得正向滤波的逐历元快照 `forwardFilterInfo`（`RunSmoother.cpp:152~153`），`SmootherBase` 三态状态机先以 `FILTERING` 态对同一段数据**反向**跑一遍内嵌滤波器（`CompleteInitialization()` 第1596行 `RunBackwards`，`Estimate()` 第1788行 `filter->Estimate()`），得到 `backwardFilterInfo`（第1925行）；随后进入 `SMOOTHING` 态，从正向滤波起始历元起沿 `forwardFilterInfo` 逐点调用 `SmoothState()`，用 `SmoothCovState()`（`Smoother.cpp:300~315`）把正反向的协方差平方根 `Ra`/`Rb` 与状态 `Xa`/`Xb` 做平方根信息融合，得到平滑状态与协方差；`PREDICTING` 态则把平滑结果外推到指定预测时段（`SmootherBase.cpp:809~857` `StateCleanUp()`）。反向滤波的初始协方差被放大 `1e10`/`1e4`（`UpdateInitialConditions()`，`SmootherBase.cpp:1382~1402`），以保证最终融合不被反向先验污染。

#### 参数表

**SeqEstimator**（`SeqEstimator.cpp:83~109` 的 `PARAMETER_TEXT`/`PARAMETER_TYPE`，9 个新增参数，其余继承 `Estimator`）：

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| `ProcessNoiseTimeStep` | REAL | 过程噪声更新时间间隔（已弃用，建议用 `ProcessNoiseModel.UpdateTimeStep`；第432~434行输出弃用警告） |
| `ScaledResidualThreshold` | REAL | sigma 编辑的标度系数（`constMult`，默认 3.0） |
| `DelayRectifyTimeSpan` | REAL | 延迟整流参考轨道的时长 |
| `MeasDeweightingSigmaThreshold` | REAL | 测量欠权的位置 σ 阈值（km） |
| `MeasDeweightingCoefficient` | REAL | 测量欠权系数 β（Lear 方法） |
| `InputWarmStartFile` | STRING | 热启动输入数据文件 |
| `WarmStartEpochFormat` | STRING | 热启动历元格式 |
| `WarmStartEpoch` | STRING | 热启动历元（`FirstMeasurement`/`LastWarmStartRecord`/具体历元） |
| `OutputWarmStartFile` | STRING | 热启动输出数据文件 |

**ExtendedKalmanFilter**：`ExtendedKalmanFilter.cpp` 未定义任何 `PARAMETER_TEXT`/`GetParameterText` 覆盖，因此不新增参数，全部继承 `SeqEstimator` 的参数表（EKF 的 `ProcessNoiseTimeStep`/`ScaledResidualThreshold` 等均来自基类）。该文件第74~96行仅新增了成员矩阵与私有量测更新方法，不新增脚本参数。

#### 与 core 的扩展点

- **继承 `Estimator`**：`SeqEstimator`（`EKF/SeqEstimator.hpp:48`）与 `SmootherBase`（`smoother/SmootherBase.hpp:44`）都继承 `Estimator`。`Estimator` 头文件位于 `plugins/EstimationPlugin/src/base/estimator/Estimator.hpp`（第54行 `class ESTIMATION_API Estimator : public Solver`），`Solver` 位于 `src/base/solver/Solver.hpp`。因此顺序估计器与平滑器都作为 GMAT 的 `Solver` 接入求解框架，由 `RunEstimator`/`RunSmoother` 命令驱动其 `AdvanceState()` 状态机。
- **继承 `RunEstimator`**：`RunSmoother`（`command/RunSmoother.hpp:46`）继承 `RunEstimator`（`plugins/EstimationPlugin/src/base/command/RunEstimator.hpp:51` `class ESTIMATION_API RunEstimator : public RunSolver`），复用 `RunEstimator` 对 Solver 状态机的命令侧动作（初始化/传播/计算/发布状态），仅覆盖 `PrepareToEstimate`/`Propagate`/`Calculate`/`IsSmootherPredicting` 以处理反向滤波与平滑点的非积分步进。
- 其余资源类（`ProcessNoiseBase`/`ProcessNoiseModel`/`SNCProcessNoise`/`LinearProcessNoise`/`EstimatedParameter`/`EstimatedParameterModel`/`FirstOrderGaussMarkov`）继承 `GmatBase`，作为普通 GMAT 资源对象注册；`SmootherBase` 与 `SeqEstimator` 之间通过 `friend class SmootherBase`（`SeqEstimator.hpp:169`）建立私有访问关系。

#### 文件清单附录

本插件共有 43 个代码文件（`.hpp`/`.cpp`），外加 `CMakeLists.txt`、`Doxyfile`、`.gitignore` 等非代码文件。

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `EKF/SeqEstimator.hpp` | 顺序估计基类声明 | `SeqEstimator`、`FilterMeasurementInfoType`、`UpdateInfoType` |
| `EKF/SeqEstimator.cpp` | 顺序估计状态机与协方差/噪声 | `AdvanceState`、`CompleteInitialization`、`FindTimeStep`、`UpdateProcessNoise`、`TimeUpdate`、`FilterUpdate`、`DataFilter` |
| `EKF/ExtendedKalmanFilter.hpp` | EKF 类声明 | `ExtendedKalmanFilter`、`sqrtP`/`sqrtPupdate` |
| `EKF/ExtendedKalmanFilter.cpp` | EKF 量测更新实现 | `Estimate`、`TimeUpdate`、`SetupMeas`、`ComputeObs`、`ComputeGain`、`UpdateElements`、`UpdateCovarianceSimple`、`UpdateCovarianceJoseph` |
| `command/RunSmoother.hpp` | 平滑命令声明 | `RunSmoother` |
| `command/RunSmoother.cpp` | 平滑命令实现 | `Initialize`、`LoadSolveForsToFilterESM`、`PrepareToEstimate`、`Propagate`、`Calculate` |
| `estimatedparam/EstimatedParameter.hpp` | 被估参数资源声明 | `EstimatedParameter` |
| `estimatedparam/EstimatedParameter.cpp` | 被估参数委托实现 | `GetProcessNoise`、`SetEstimatedParameterModel`、`GetOwnedObjectId` |
| `estimatedparam/EstimatedParameterException.hpp` | 被估参数异常 | `EstimatedParameterException` |
| `estimatedparam/EstimatedParameterModel.hpp` | 参数模型基类声明 | `EstimatedParameterModel` |
| `estimatedparam/EstimatedParameterModel.cpp` | 参数模型基类实现 | `SetStringParameter`、`SetConversionFactor` |
| `estimatedparam/FirstOrderGaussMarkov.hpp` | FOGM 模型声明 | `FirstOrderGaussMarkov` |
| `estimatedparam/FirstOrderGaussMarkov.cpp` | FOGM 噪声矩阵构造 | `GetProcessNoise` |
| `factory/EKFCommandFactory.hpp/.cpp` | RunSmoother 命令工厂 | `EKFCommandFactory`、`CreateCommand` |
| `factory/ExtendedKalmanFilterFactory.hpp/.cpp` | EKF 工厂 | `ExtendedKalmanFilterFactory`、`CreateSolver` |
| `factory/EstimatedParameterFactory.hpp/.cpp` | EstimatedParameter 工厂 | `EstimatedParameterFactory` |
| `factory/EstimatedParameterModelFactory.hpp/.cpp` | FOGM 模型工厂 | `EstimatedParameterModelFactory` |
| `factory/ProcessNoiseFactory.hpp/.cpp` | 过程噪声工厂 | `ProcessNoiseFactory`、`CreateProcessNoise` |
| `factory/ProcessNoiseModelFactory.hpp/.cpp` | ProcessNoiseModel 工厂 | `ProcessNoiseModelFactory` |
| `factory/SmootherFactory.hpp/.cpp` | Smoother 工厂 | `SmootherFactory`、`CreateSmoother` |
| `include/kalman_defs.hpp` | DLL 导入/导出宏 | `KALMAN_API` |
| `noise/LinearProcessNoise.hpp/.cpp` | 线性过程噪声 | `LinearProcessNoise`、`GetProcessNoise` |
| `noise/NoiseException.hpp` | 噪声异常 | `NoiseException` |
| `noise/ProcessNoiseBase.hpp/.cpp` | 过程噪声基类与坐标转换 | `ProcessNoiseBase`、`ConvertMatrix` |
| `noise/ProcessNoiseModel.hpp/.cpp` | 过程噪声容器 | `ProcessNoiseModel`、`SetNoiseModel` |
| `noise/SNCProcessNoise.hpp/.cpp` | SNC 过程噪声 | `SNCProcessNoise`、`GetProcessNoise` |
| `plugin/GmatPluginFunctions.hpp/.cpp` | 插件库入口 | `GetFactoryCount`、`GetFactoryPointer`、`SetMessageReceiver` |
| `smoother/Smoother.hpp/.cpp` | 平滑器实现 | `Smoother`、`SmoothState`、`SmoothCovState`、`FindIndex` |
| `smoother/SmootherBase.hpp/.cpp` | 平滑器基类状态机 | `SmootherBase`、`AdvanceState`、`CompleteInitialization`、`Estimate`、`CheckCompletion`、`SmootherUpdate` |

### 13.9 ExternalForceModelPlugin（外部力模型）

**目录**：`plugins/ExternalForceModelPlugin/src/base/`，子目录 `factory/`、`include/`、`plugin/`、`forcemodel/`，共 7 个 C++ 文件（3 个 `.cpp`、4 个 `.hpp`，另有 2 个 `.gitignore` 不计入代码）。

**构建开关**：`PLUGIN_EXTERNALFORCEMODEL`，默认 `ON`，见 `plugins/CMakeLists.txt` 第 118 行。

**目标库名**：`ExternalForceModel${TargetPySuffix}`（即 `ExternalForceModel_py<主><次>`），由 `plugins/ExternalForceModelPlugin/src/base/CMakeLists.txt` 第 30 行 `SET(TargetName "ExternalForceModel${TargetPySuffix}")` 决定，后缀来自第 29 行 `SET(TargetPySuffix "_py${Python3_VERSION_MAJOR}${Python3_VERSION_MINOR}")`。构建前强制 `FIND_PACKAGE(Python3 ... EXACT)`（第 22 行），找不到 Python 开发库则 `RETURN()` 跳过（第 23–27 行）；链接 `Python3::Python`（第 53 行）与 `PythonInterface${TargetPySuffix}`（第 54 行）。

**一句话目的**：向 GMAT 的力模型体系注入一个由 Python 脚本提供加速度（和力矩）的 `PhysicalModel` 派生类，使外部自定义力通过 Python 回调参与 ODEModel 的数值积分。

#### 目的与职责

该插件把"外部程序提供受力"的能力做成一个标准力模型。`ExternalModel` 继承 `PhysicalModel`，但自身不计算任何力——它把当前状态向量、历元、状态描述字符串打包，通过 `PythonInterface` 单例调用用户 Python 脚本中的入口函数（默认 `GetDerivatives`），把返回的 Python 列表解码为导数（加速度）向量写回 `deriv`。这样 ODEModel / 传播器（Integrator）完全无需关心力来自哪里，与内置力模型（重力、大气阻力等）使用同一套 `GetDerivatives` 接口。

与之配套的还有 `GetTorquesForSpacecraft`，通过独立入口（`torqueEntryPoint`）调用 Python 返回 3 元素力矩；该路径当前标记为 "Work in Progress"（`ExternalModel.cpp` 第 665 行注释）。`ExternalModel` 还声明支持状态转移矩阵（STM）与 A 矩阵导数（`SupportsDerivative`，第 580–587 行），以便在轨道确定/协方差传播中使用。

#### 导出类清单

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `ExternalModel` | `PhysicalModel`（`src/base/forcemodel/PhysicalModel.hpp`） | 通过 Python 接口计算加速度/力矩的力模型 |
| `ExternalModelFactory` | `Factory`（`src/base/factory/Factory.hpp`） | 创建 `ExternalModel` 对象，类型 `Gmat::PHYSICAL_MODEL` |

`ExternalModel.hpp` 第 38 行 `class EXTERNALMODEL_API ExternalModel : public PhysicalModel`；`ExternalModelFactory.hpp` 第 38 行 `class EXTERNALMODEL_API ExternalModelFactory : public Factory`。

#### 插件注册与工厂

`plugin/GmatPluginFunctions.cpp` 定义插件加载的 C 接口：`GetFactoryCount()` 返回 `1`（第 53 行），`GetFactoryPointer(index)` 在 `index==0` 时 `new ExternalModelFactory()`（第 74–75 行）。

`ExternalModelFactory::CreatePhysicalModel` 只在 `ofType == "ExternalModel"` 时 `new ExternalModel(withName)`（`factory/ExternalModelFactory.cpp` 第 68–69 行），`CreateObject` 委托给它（第 50 行）。默认构造函数把 `"ExternalModel"` 压入 `creatables`（第 86–89 行），工厂类型为 `Gmat::PHYSICAL_MODEL`（第 84 行）。

#### 逐文件讲解

##### ##### include/externalmodel_defs.hpp

职责：DLL 导入/导出宏。Windows + MSVC + `_DYNAMICLINK` 下按 `EXTERNALMODEL_EXPORTS` 定义 `EXTERNALMODEL_API` 为 `__declspec(dllexport/dllimport)`（第 45–50 行），并处理 STL 模板导出 `DECLSPECIFIER`/`EXPIMP_TEMPLATE`（第 59–65 行）；非 Windows 或未定义宏时置空（第 71–73 行）。`EXTERNALMODEL_EXPORTS` 由 CMake 第 49 行 `DEFINE_SYMBOL` 注入。

##### ##### factory/ExternalModelFactory.hpp

职责：声明工厂类。重写 `CreateObject` 与 `CreatePhysicalModel`（第 41–44 行），提供默认/列表/拷贝构造、赋值运算符与析构。头文件 include `PhysicalModel.hpp` 与 `ExternalModel.hpp`（第 35–36 行）。

##### ##### factory/ExternalModelFactory.cpp

职责：实现工厂。`CreateObject` 转发 `CreatePhysicalModel`（第 50 行）；`CreatePhysicalModel` 按类型字符串创建 `ExternalModel`（第 65–72 行）。默认构造 `Factory(Gmat::PHYSICAL_MODEL)` 并 `creatables.push_back("ExternalModel")`（第 83–90 行）；列表构造（第 103–106 行）、拷贝构造（第 119–126 行）、赋值（第 140–153 行）沿用同一模式，拷贝路径下若 `creatables` 为空也补齐 `"ExternalModel"`。

##### ##### forcemodel/ExternalModel.hpp

职责：声明 `ExternalModel`。重写 `Initialize()`、`GetDerivatives()`、`PythonDerivatives()`、`GetDerivativesForSpacecraft()`（第 48–53 行），以及 `SupportsDerivative`/`SetStart`（第 80–82 行）与 `GetTorquesForSpacecraft`（第 84 行）。成员：`scriptFilename`、`fullFilePath`、`excludeForces`、`entryPoint`、`torqueEntryPoint`、`pythonIf`、`satCount`（第 95–107 行）。私有枚举参数 ID `SCRIPT_FILENAME`/`EXCLUDE_OTHER_FORCES`/`ENTRY_POINT`（第 117–119 行），并以 `PhysicalModelParamCount` 为偏移（第 123–124 行）。

##### ##### forcemodel/ExternalModel.cpp

职责：实现 `ExternalModel`。静态参数表：`PARAMETER_TEXT` = `ScriptFileName`/`ExcludeOtherForces`/`DerivativesFunction`（第 45–50 行），类型为 `FILENAME_TYPE`/`BOOLEAN_TYPE`/`STRING_TYPE`（第 52–58 行）。构造函数以 `PhysicalModel(Gmat::PHYSICAL_MODEL, "ExternalModel", name)` 初始化，默认 `entryPoint="GetDerivatives"`，`derivativeIds.push_back(Gmat::CARTESIAN_STATE)`，`isConservative=false`、`hasMassJacobian=true`（第 73–91 行）。参数访问方法（`GetParameterText`/`GetParameterID`/`GetParameterType`/`GetBooleanParameter`/`GetStringParameter` 等，第 181–369 行）按 ID 分派到本地成员或基类。

##### ##### plugin/GmatPluginFunctions.hpp / .cpp

职责：插件加载 C 接口声明与实现。`.hpp` 在 `extern "C"` 中声明 `GetFactoryCount`、`GetFactoryPointer`、`SetMessageReceiver`（第 42–44 行）。`.cpp` 实现 `SetMessageReceiver` 调用 `MessageInterface::SetMessageReceiver(mr)`（第 98 行），并 include `ExternalModelFactory.hpp`（第 37 行）。

#### 关键类深读：ExternalModel

外部加速度的完整调用链如下（行号均见 `forcemodel/ExternalModel.cpp`）：

1. **初始化** `Initialize()`（第 379–415 行）：先调 `PhysicalModel::Initialize()`，随后 `pythonIf = PythonInterface::PyInstance()`（第 389 行），`pythonIf->PyInitialize()`（第 396 行），从 `FileManager` 取全部 Python 模块路径并 `PyAddModulePath(paths)`（第 398–403 行）。任何异常统一包装为 `InterfaceException`（第 405–409 行）。
2. **ODEModel 入口** `GetDerivatives(Real *state, Real dt, Integer order, Integer id)`（第 429–451 行）：`stateDescription = GetStateDateTypes()`（第 432 行），计算 `now = epoch + (elapsedTime + dt) / GmatTimeConstants::SECS_PER_DAY`（第 434 行），对每个航天器拷贝状态后调用 `PythonDerivatives(st, now, stateDescription, order)`，把返回 `dv` 用 `memcpy` 写入 `deriv`（第 436–447 行）。
3. **Python 调用** `PythonDerivatives(...)`（第 467–506 行）：首次调用时 `pythonIf->PyExternalGetPythonPath(scriptFilename)` 解析完整路径并打印初始化消息（第 470–479 行）；核心调用 `pyRet = pythonIf->PyExternalFunctionWrapper(scriptFilename, entryPoint, state, now, stateDescription, order, dimension, 4)`（第 485 行），参数末尾的 `4` 表示返回值元素个数期望；随后逐项 `PyList_GetItem` + `PyFloat_AsDouble` 解码成 `Real` 数组（第 497–503 行）。
4. **按航天器取导数** `GetDerivativesForSpacecraft(Spacecraft *sc)`（第 520–541 行）：取 J2000 状态 `sc->GetState().GetState()`，按 `hasPrecisionTime` 走 `BuildModelStateGT`/`BuildModelState` 构造 6 元素状态，再交给 `PythonDerivatives`。
5. **力矩** `GetTorquesForSpacecraft(sc)`（第 663–709 行）：`torqueEntryPoint` 非空时用同样的 wrapper，但期望返回 3 个元素（第 681、686 行末尾的 `3`）。
6. **状态描述** `GetStateDateTypes()`（第 724–834 行）：遍历 `psm->GetStateMap()`，把 `CartesianState` 映射为 `X/Y/Z/Vx/Vy/Vz`，把 `Covariance`/`STM` 映射为 `Covariance.XY` 等可读名，`MassFlow` 映射为 `TotalMass`，供 Python 脚本按名字取数（作者在注释中标注该实现每次调用都重建字符串、开销较大，第 718–720 行 `@TODO`）。

与 ODEModel/PhysicalModel 的对接体现在：`SupportsDerivative` 声明支持 `CARTESIAN_STATE`、`ORBIT_STATE_TRANSITION_MATRIX`、`ORBIT_A_MATRIX`（第 580–587 行）；`SetStart` 在 `CARTESIAN_STATE` 分支记录 `satCount`、`cartesianStart` 等（第 623–629 行），在 STM/A 矩阵分支记录 `stmStart`/`aMatrixStart` 与 `totalSTMSize`（第 631–645 行）；`IsUnique` 恒返回 `true`（第 555–558 行），表示一个力模型集合中只允许一个 ExternalModel。

#### 参数表（ExternalModel::GetParameterInfo，见 .cpp 静态表）

| 脚本名 | ID（枚举） | 类型 | 说明 |
| --- | --- | --- | --- |
| `ScriptFileName` | `SCRIPT_FILENAME` | `FILENAME_TYPE` | Python 脚本文件名（第 47、55 行） |
| `ExcludeOtherForces` | `EXCLUDE_OTHER_FORCES` | `BOOLEAN_TYPE` | 是否排除其它力、仅用脚本力（第 48、56 行；getter/setter 第 259–283 行） |
| `DerivativesFunction` | `ENTRY_POINT` | `STRING_TYPE` | Python 入口函数名，默认 `GetDerivatives`（第 49、57 行） |

注意 `IsParameterReadOnly` 恒返回 `true`（第 247–250 行）：这些参数对用户界面只读。

#### 与 core 的扩展点

| core 基类 | 相对路径 | 需重写的虚函数（本插件已实现） |
| --- | --- | --- |
| `PhysicalModel` | `src/base/forcemodel/PhysicalModel.hpp` | `Initialize()`、`GetDerivatives()`、`GetDerivativesForSpacecraft()`、`SupportsDerivative()`、`SetStart()`、`GetTorquesForSpacecraft()`、`IsUnique()` |
| `GmatBase`（经由 PhysicalModel） | `src/base/foundation/GmatBase.hpp` | `Clone()`、`GetParameterText/ID/Type/TypeString`、`IsParameterReadOnly`、`Get/SetBooleanParameter`、`Get/SetStringParameter` |
| `Factory` | `src/base/factory/Factory.hpp` | `CreateObject()`、`CreatePhysicalModel()` |

#### 文件清单附录

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/include/externalmodel_defs.hpp` | DLL 导入导出宏 | `EXTERNALMODEL_API` |
| `src/base/factory/ExternalModelFactory.hpp` | 工厂声明 | `ExternalModelFactory` |
| `src/base/factory/ExternalModelFactory.cpp` | 工厂实现 | `CreateObject`、`CreatePhysicalModel` |
| `src/base/forcemodel/ExternalModel.hpp` | 力模型声明 | `ExternalModel`、参数枚举 |
| `src/base/forcemodel/ExternalModel.cpp` | 力模型实现 | `Initialize`、`GetDerivatives`、`PythonDerivatives`、`GetStateDateTypes` |
| `src/base/plugin/GmatPluginFunctions.hpp` | 插件接口声明 | `GetFactoryCount`、`GetFactoryPointer` |
| `src/base/plugin/GmatPluginFunctions.cpp` | 插件接口实现 | `GetFactoryPointer`（`new ExternalModelFactory`）、`SetMessageReceiver` |

### 13.10 ExtraPropagatorsPlugin（附加传播器：Bulirsch-Stoer）

**目录**：`plugins/ExtraPropagatorsPlugin/src/base/`，子目录 `factory/`、`include/`、`plugin/`、`propagator/`，共 7 个 C++ 文件（3 个 `.cpp`、4 个 `.hpp`，另有 1 个 `.gitignore`）。

**构建开关**：`PLUGIN_EXTRAPROPAGATORS`，默认 `ON`，见 `plugins/CMakeLists.txt` 第 119 行。

**目标库名**：`ExtraPropagators`，由 `plugins/ExtraPropagatorsPlugin/src/base/CMakeLists.txt` 第 17 行 `SET(TargetName ExtraPropagators)` 决定；`DEFINE_SYMBOL` 设为 `PROPAGATOR_EXPORTS`（第 36 行）。

**一句话目的**：把 Numerical Recipes 的 Gragg-Bulirsch-Stoer 外推积分器作为 `Integrator` 派生类接入 GMAT 传播子系统。

#### 目的与职责

该插件是 GMAT 官方提供的"插件示例"之一（`ExtraPropagatorFactory.cpp` 头注释称其为 sample code，第 26–28 行）。它演示如何为传播子系统新增一个积分器：`BulirschStoer` 继承 `Integrator`（进而继承 `Propagator`），实现自适应步长的 Gragg-Bulirsch-Stoer 方法——在区间内用修正中点法（modified midpoint）取多个子步数进行外推，再对不同子步长的结果做 Richardson 多项式外推（Neville 算法），把步长外推到零以估计下一状态，并以逐层误差估计做步长/深度自适应。

由于积分器只依赖 `PhysicalModel::GetDerivatives`/`GetDerivativeArray`/`EstimateError` 等基类接口，`BulirschStoer` 与任何 `PhysicalModel`/`ODEModel` 组合都可以工作，是"传播器工厂 + 积分器虚函数重写"扩展点的标准示范。

#### 导出类清单

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `BulirschStoer` | `Integrator`（`src/base/propagator/Integrator.hpp`） | Bulirsch-Stoer 外推积分器 |
| `ExtraPropagatorFactory` | `Factory`（`src/base/factory/Factory.hpp`） | 创建 `BulirschStoer` 对象，类型 `Gmat::PROPAGATOR` |

`BulirschStoer.hpp` 第 75 行 `class PROPAGATOR_API BulirschStoer : public Integrator`；`ExtraPropagatorFactory.hpp` 第 45 行 `class PROPAGATOR_API ExtraPropagatorFactory : public Factory`。注意 `Integrator` 本身继承 `Propagator`（`src/base/propagator/Propagator.hpp`）。

#### 插件注册与工厂

`plugin/GmatPluginFunctions.cpp`：`GetFactoryCount()` 返回 `1`（第 51 行），`GetFactoryPointer(0)` 返回 `new ExtraPropagatorFactory`（第 75–76 行）。

`ExtraPropagatorFactory::CreatePropagator` 在 `ofType == "BulirschStoer"` 时 `new BulirschStoer(withName)`（`factory/ExtraPropagatorFactory.cpp` 第 71–72 行），`CreateObject` 委托（第 52 行）。默认构造 `Factory(Gmat::PROPAGATOR)` 并 `creatables.push_back("BulirschStoer")`（第 85–92 行）；列表/拷贝构造与赋值同样补齐 `creatables`（第 104–106、119–126、140–148 行）。

#### 逐文件讲解

##### ##### include/ExtraPropagatorDefs.hpp

职责：DLL 导入导出宏。与其它插件 defs 同构：`PROPAGATOR_EXPORTS` 决定 `PROPAGATOR_API` 为 `dllexport/dllimport`（第 51–55 行），含 STL 模板导出宏（第 64–69 行），非 Windows 置空（第 76–78 行）。

##### ##### factory/ExtraPropagatorFactory.hpp

职责：声明工厂。重写 `CreateObject` 与 `CreatePropagator`（第 48–51 行），提供默认/列表/拷贝构造、赋值、析构。

##### ##### factory/ExtraPropagatorFactory.cpp

职责：实现工厂。`CreateObject` 转发 `CreatePropagator`（第 52 行）；`CreatePropagator` 按类型创建 `BulirschStoer`（第 68–74 行）。构造/拷贝/赋值沿用 `creatables` 补齐模式（第 85–148 行）。

##### ##### propagator/BulirschStoer.hpp

职责：声明积分器。重写 `Initialize()`、`Step(dt)`、`Step()`、`RawStep()` 以及算法私有步骤 `MidpointMethod()`、`PolyExtrapolate()`、`EstimateError()`、`AdaptStep()`、`SetMaximumDepth()`（第 85–93 行）。参数枚举 `MINIMUM_REDUCTION`/`MAXIMUM_REDUCTION`/`MIN_TOLERANCE`（第 111–113 行）。私有数据含外推深度 `depth`、各层误差 `levelError`、系数 `ai`/`alpha`、中间状态 `intermediates`、多项式系数 `coeffC`、子步尺寸平方 `intervals`、中点法状态 `mstate`/`nstate`/`estimates`/`estimatedState`、每层子区间数 `subinterval`、安全因子 `bs_safety1=0.25`/`bs_safety2=0.70`、步长缩放 `scale_dt` 等（第 120–167 行）。头注释明确算法来自 Numerical Recipes in C，并修正了 NR 原书中 `d[depth][depth]` 数组尺寸错误（第 65–74、269–276 行）。

##### ##### propagator/BulirschStoer.cpp

职责：实现积分器。静态参数表 `PARAMETER_TEXT` = `MinimumReduction`/`MaximumReduction`/`MinimumTolerance`（第 66–71 行），均为 `REAL_TYPE`（第 74–79 行）。构造函数 `Integrator("BulirschStoer", nomme)`，`depth=8`，默认 `minimumReduction=0.7`、`maximumReduction=1.0e-5`、`scale_dt=0.1`（第 92–117 行）。算法主体见"关键类深读"。

##### ##### plugin/GmatPluginFunctions.hpp / .cpp

职责：插件接口声明与实现。`.hpp` 声明 `GetFactoryCount`/`GetFactoryPointer`/`SetMessageReceiver`（第 47–49 行）；`.cpp` 实现 `SetMessageReceiver` 调用 `MessageInterface::SetMessageReceiver`（第 104 行）。

#### 关键类深读：BulirschStoer

积分器运行按 `Step(dt)` → `Step()` 两层驱动，内部逐步构建外推表（行号见 `propagator/BulirschStoer.cpp`）：

1. **初始化** `Initialize()`（第 279–467 行）：先做步长上下限约束（第 283–287 行），调 `Propagator::Initialize()`；若未初始化深度则 `SetMaximumDepth(depth)`（第 293–295 行）；从 `physicalModel->GetDimension()` 取得状态维数，释放并重建一维数组 `errorEstimates`/`coeffC`/`estimatedState`/`mstate`/`nstate`（第 351–399 行）和二维数组 `intermediates[depth][dimension]`/`estimates[depth][dimension]`（第 402–456 行），最后 `ddt = physicalModel->GetDerivativeArray()`（第 457 行）。
2. **深度与系数准备** `SetMaximumDepth(d)`（第 482–695 行）：释放旧数组后，`subinterval[i] = i*2`（第 567–568 行，即 0,2,4,6,…）；累加 `ai[i+1] = ai[i] + subinterval[i+1]`（第 671–673 行）；按 `alpha[j][i] = pow(tolerance*bs_safety1, (ai[j+2]-ai[i+2])/((ai[i+2]-ai[1]+1.0)*(2.0*j+3.0)))` 预计算外推系数（第 681–682 行）；确定最优收敛行 `kopt` 与 `kmax`（第 686–690 行）。
3. **外步长驱动** `Step(dt)`（第 707–724 行）：把总步长 `dt` 拆成若干内部步，循环 `stepSize = stepleft; Step(); stepleft -= stepTaken`，直到走完。
4. **主循环** `Step()`（第 759–809 行）：`for (kused=0; kused<kmax; ++kused)` 逐层做 `MidpointMethod(subinterval[kused+1])`、`PolyExtrapolate()`、`EstimateError()`（第 776–784 行）；当 `kused>1 && eEstimate<tolerance` 收敛则 `AdaptStep` 后跳出（第 785–791 行）；否则继续加深或 `AdaptStep` 缩步（第 794–798 行）。成功后 `memcpy(outState, estimatedState, ...)` 并 `physicalModel->IncrementTime(stepTaken)`（第 805–806 行）。
5. **修正中点法** `MidpointMethod(substeps)`（第 882–917 行）：首步 `nstate[j] = mstate[j] + substepsize*ddt[j]`（第 896 行）；中间各步中心差分 `swap = mstate[j] + h2*ddt[j]`（`h2 = 2.0*substepsize`，第 904 行）；末步合成 `estimates[level][j] = 0.5*(mstate[j]+nstate[j]+substepsize*ddt[j])`（第 914 行）。文档注释给出完整公式（第 845–876 行）。
6. **多项式外推** `PolyExtrapolate()`（第 963–998 行）：`intervals[level] = stepSize²/subinterval[level+1]²`（第 969–970 行）；用 Neville 算法对每一分量在 `intervals` 上做 Richardson 外推，更新 `estimatedState` 与 `errorEstimates`（第 975–995 行）。
7. **误差估计** `EstimateError()`（第 1014–1017 行）：直接委托 `physicalModel->EstimateError(errorEstimates, estimatedState)`。
8. **步长/深度自适应** `AdaptStep(maxerror)`（第 1055–1144 行）：误差过大时按 `errkm = pow(maxerror/(bs_safety1*tolerance), 1.0/(2*kused+1))` 计算缩减因子（第 1080 行），用 `bs_safety2`、`alpha` 等调整 `factor` 并夹在 `minimumReduction`/`maximumReduction` 之间（第 1082–1092 行），`stepSize *= factor`（第 1094 行）；成功时反推更大步长/更深 `kopt`（第 1097–1128 行），并处理固定步长模式（第 1136–1138 行）。

继承 `Integrator` 需重写的虚函数：`Initialize()`、`Step(Real dt)`、`Step()`、`RawStep()`（本实现让 `RawStep` 直接调 `Step()`，第 828–831 行，注释说明 BS 的误差控制与表遍历交织，无法做真正的"无控步"）。参数访问重写 `GetParameterText/ID/Type/TypeString`、`IsParameterReadOnly`、`Get/SetRealParameter`（第 1160–1340 行）。

#### 参数表（BulirschStoer，见 .cpp 第 66–79 行静态表）

| 脚本名 | ID | 类型 | 说明 |
| --- | --- | --- | --- |
| `MinimumReduction` | `MINIMUM_REDUCTION` | `REAL_TYPE` | 缩减步长时的最小（下限）因子，默认 0.7 |
| `MaximumReduction` | `MAXIMUM_REDUCTION` | `REAL_TYPE` | 缩减步长时的最大（上限）因子，默认 1.0e-5 |
| `MinimumTolerance` | `MIN_TOLERANCE` | `REAL_TYPE` | 已废弃；`IsParameterReadOnly` 返回 `true`（第 1230 行），setter 只打警告（第 1310–1317 行） |

此外还继承 `Integrator` 的 `ErrorControl`、`Tolerance`、步长上下限等参数。

#### 与 core 的扩展点

| core 基类 | 相对路径 | 需重写的虚函数（本插件已实现） |
| --- | --- | --- |
| `Integrator` | `src/base/propagator/Integrator.hpp` | `Initialize()`、`Step(Real dt)`、`Step()`、`RawStep()` |
| `Propagator`（Integrator 的基类） | `src/base/propagator/Propagator.hpp` | 通过 `Integrator` 间接继承 `Initialize`/`Step` 接口 |
| `GmatBase` | `src/base/foundation/GmatBase.hpp` | `Clone()`、参数访问方法（`Get/SetRealParameter` 等） |
| `Factory` | `src/base/factory/Factory.hpp` | `CreateObject()`、`CreatePropagator()` |

#### 文件清单附录

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/include/ExtraPropagatorDefs.hpp` | DLL 导入导出宏 | `PROPAGATOR_API` |
| `src/base/factory/ExtraPropagatorFactory.hpp` | 工厂声明 | `ExtraPropagatorFactory` |
| `src/base/factory/ExtraPropagatorFactory.cpp` | 工厂实现 | `CreateObject`、`CreatePropagator` |
| `src/base/propagator/BulirschStoer.hpp` | 积分器声明 | `BulirschStoer`、参数枚举 |
| `src/base/propagator/BulirschStoer.cpp` | 积分器实现 | `Initialize`、`Step`、`MidpointMethod`、`PolyExtrapolate`、`EstimateError`、`AdaptStep`、`SetMaximumDepth` |
| `src/base/plugin/GmatPluginFunctions.hpp` | 插件接口声明 | `GetFactoryCount`、`GetFactoryPointer` |
| `src/base/plugin/GmatPluginFunctions.cpp` | 插件接口实现 | `GetFactoryPointer`（`new ExtraPropagatorFactory`）、`SetMessageReceiver` |

### 13.11 FminconOptimizerPlugin（fmincon 数值优化器）

**目录**：`plugins/FminconOptimizerPlugin/src/base/`，子目录 `factory/`、`include/`、`plugin/`、`solver/`，共 7 个 C++ 文件（3 个 `.cpp`、4 个 `.hpp`）。

**构建开关**：`PLUGIN_FMINCONOPTIMIZER`，默认 `OFF`，见 `plugins/CMakeLists.txt` 第 120 行。`src/base/CMakeLists.txt` 还要求 `WIN32`（第 20–23 行）、`PLUGIN_MATLABINTERFACE` 开启（第 25–28 行）、`Matlab_FOUND`（第 30–33 行），任一不满足即跳过构建。

**目标库名**：`FminconOptimizer`，由 `plugins/FminconOptimizerPlugin/src/base/CMakeLists.txt` 第 37 行 `SET(TargetName FminconOptimizer)` 决定；`DEFINE_SYMBOL` 为 `FMINCON_EXPORTS`（第 56 行）。附加包含 `Matlab_INCLUDE_DIRS`（第 60 行），链接 `MatlabInterface` 与 `${Matlab_LIBRARIES}`（第 64–65 行）。

**一句话目的**：把 MATLAB Optimization Toolbox 的 `fmincon` 求解器包装成 GMAT 的 `ExternalOptimizer`，供 `Optimize`/`Vary`/`Minimize`/`NonlinearConstraint` 命令使用。

#### 目的与职责

该插件是 GMAT 与 MATLAB 引擎桥接的典型优化器实现。`FminconOptimizer` 继承 `ExternalOptimizer`（`src/base/solver/ExternalOptimizer.hpp`，本身是 `Solver` 派生类），它不在 C++ 里实现 SQP 算法，而是把 GMAT 的变量（`variable`）、下界（`variableMinimum`）、上界（`variableMaximum`）、目标函数与约束数据组织成 MATLAB 字符串，通过 `MatlabInterface` 送入 MATLAB 执行 `fmincon`，再读回 `exitFlag` 判断收敛。

分工：GMAT 侧负责状态机驱动、变量/约束数据整理与结果回写；MATLAB 侧（`GmatFminconOptimizationDriver.m` 及其配套 `EvaluateGMATObjective.m`、`EvaluateGMATConstraints.m`、`CallGMATfminconSolver.m`）负责真正调用 `fmincon` 并在每次求值目标/约束时通过 MATLAB↔GMAT 服务器回调回 GMAT 计算代价与约束残差。`FminconOptimizer.cpp` 的 `AdvanceNestedState` 就是这种"MATLAB 回调 → GMAT 求值"的服务器端入口。

#### 导出类清单

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `FminconOptimizer` | `ExternalOptimizer`（`src/base/solver/ExternalOptimizer.hpp`） | MATLAB fmincon 包装优化器 |
| `FminconOptimizerFactory` | `Factory`（`src/base/factory/Factory.hpp`） | 创建 `FminconOptimizer`，类型 `Gmat::SOLVER` |

`FminconOptimizer.hpp` 第 48 行 `class FMINCON_API FminconOptimizer : public ExternalOptimizer`；`FminconOptimizerFactory.hpp` 第 39 行 `class FMINCON_API FminconOptimizerFactory : public Factory`。

#### 插件注册与工厂

`plugin/GmatPluginFunctions.cpp`：`GetFactoryCount()` 返回 `1`（第 52 行），`GetFactoryPointer(0)` 返回 `new FminconOptimizerFactory`（第 72–73 行）。

`FminconOptimizerFactory::CreateSolver` 在 `ofType == "FminconOptimizer"` 时 `new FminconOptimizer(withName)`（`factory/FminconOptimizerFactory.cpp` 第 68–69 行），`CreateObject` 委托（第 50 行）。默认构造 `Factory(Gmat::SOLVER)` 并 `creatables.push_back("FminconOptimizer")`（第 83–90 行）。

#### 逐文件讲解

##### ##### include/fmincon_defs.hpp

职责：DLL 导入导出宏。`FMINCON_EXPORTS` 决定 `FMINCON_API`（第 48–52 行），含 STL 模板导出宏（第 61–67 行），非 Windows 置空（第 73–75 行）。

##### ##### factory/FminconOptimizerFactory.hpp

职责：声明工厂。重写 `CreateObject` 与 `CreateSolver`（第 42–45 行），含默认/列表/拷贝构造、赋值、析构。

##### ##### factory/FminconOptimizerFactory.cpp

职责：实现工厂。`CreateObject` 转发 `CreateSolver`（第 50 行）；`CreateSolver` 创建 `FminconOptimizer`（第 65–72 行）。构造/拷贝补齐 `creatables`（第 83–126 行）。

##### ##### solver/FminconOptimizer.hpp

职责：声明优化器。重写 `Initialize()`、`AdvanceState()`、`AdvanceNestedState()`、`Optimize()`（第 56–59 行）与 `Clone`/`Copy`（第 62–63 行），以及大量字符串参数访问方法（第 67–92 行）与 `WriteParameters`（第 94–95 行）。成员 `options`/`optionValues`（fmincon 选项名与值）、`fminconExitFlag`、`matlabIf`（第 101–108 行）；静态 `ALLOWED_OPTIONS[6]`/`DEFAULT_OPTION_VALUES[6]`/`NUM_MATLAB_OPTIONS`/`MATLAB_OPTIONS_OFFSET`（第 110–117 行）。受保护的 Solver 钩子 `CompleteInitialization`/`RunExternal`/`RunNominal`/`CalculateParameters`/`RunComplete`/`FreeArrays`/`WriteToTextFile`/`GetProgressString`/`OpenConnection`/`CloseConnection`/`IsAllowedOption`/`IsAllowedValue`（第 120–135 行）以及 MATLAB 辅助函数 `RunCdCommand`/`WriteSearchPath`/`EvalMatlabString`（第 137–139 行）。参数 ID `OPTIONS`/`OPTION_VALUES`（第 145–147 行）。

##### ##### solver/FminconOptimizer.cpp

职责：实现优化器。静态参数表 `PARAMETER_TEXT` = `Options`/`OptionValues`（第 56–61 行），`STRINGARRAY_TYPE`（第 63–69 行）；`ALLOWED_OPTIONS` = `DiffMaxChange`/`DiffMinChange`/`MaxFunEvals`/`TolX`/`TolFun`/`TolCon`（第 76–84 行），默认值 `0.1000`/`1.0000e-08`/`1000`/`1.0000e-04`/`1.0000e-04`/`1.0000e-04`（第 86–94 行），`NUM_MATLAB_OPTIONS=6`、`MATLAB_OPTIONS_OFFSET=1000`（第 96–97 行）。构造函数 `ExternalOptimizer("FminconOptimizer", name)`，把 6 个选项与默认值填入两个数组，`AllowStepsizeLimit=false`、`AllowIndependentPerts=false`、`matlabIf=NULL`（第 106–140 行）。算法主体见"关键类深读"。

##### ##### plugin/GmatPluginFunctions.hpp / .cpp

职责：插件接口声明与实现。`.hpp` 声明 `GetFactoryCount`/`GetFactoryPointer`/`SetMessageReceiver`（第 44–46 行）；`.cpp` 实现 `SetMessageReceiver`（第 94 行）。

#### 关键类深读：FminconOptimizer

优化采用"GMAT 状态机 + MATLAB fmincon + 回调服务器"三段式（行号见 `solver/FminconOptimizer.cpp`）：

1. **初始化** `Initialize()`（第 206–220 行）：调 `ExternalOptimizer::Initialize()` 后 `OpenConnection()`。
2. **建立 MATLAB 连接** `OpenConnection()`（第 1426–1646 行）：检查 `GmatGlobal::IsMatlabAvailable()`（第 1435 行），`matlabIf = MatlabInterface::Instance()` 并 `Open("GmatMatlab")`（第 1442–1451 行）；`RunCdCommand` 切到当前目录（第 1465 行），逆序把 `FileManager::GetAllMatlabFunctionPaths()` 加入 MATLAB 路径（第 1470–1487 行）；用 `exist('fmincon')` 确认 Optimization Toolbox（第 1507–1512 行），再用 `exist('gmat_startup')` 找到并运行 `gmat_startup.m`（第 1524–1564 行）；最后校验四个 MATLAB 支撑文件 `GmatFminconOptimizationDriver`/`EvaluateGMATObjective`/`EvaluateGMATConstraints`/`CallGMATfminconSolver` 都在路径上（第 1566–1607 行），并 `inSource = GmatInterface::Instance()`（第 1608 行）——`inSource` 就是 MATLAB 回调 GMAT 的服务器。
3. **状态机** `AdvanceState()`（第 226–272 行）：`INITIALIZING` 写文本报告后 `CompleteInitialization()` 转入 `RUNEXTERNAL`（第 230–247 行）；`RUNEXTERNAL` 调 `RunExternal()`（第 249–257 行）；`FINISHED` 调 `RunComplete()`（第 259–266 行）。`RunExternal()` 实际只做 `Optimize()` 然后置 `currentState = FINISHED`（第 930–935 行）。
4. **嵌套状态机（MATLAB 回调入口）** `AdvanceNestedState(vars)`（第 278–390 行）：`NOMINAL` 态把 MATLAB 传来的 `vars` 写回 `variable` 并 `RunNominal()`（第 292–312 行）；`CALCULATING` 态调 `CalculateParameters()` 后把 `cost`、`gradient`、`eqConstraintValues`、`ineqConstraintValues` 组装成返回给 MATLAB 的字符串数组：`F = <cost>;`（第 330 行）、`GradF = [<gradient>];`（第 341 行）、`NonLinearEqCon = [<eq残差>];`（第 352 行）、`NonLinearIneqCon = [<ineq残差>];`（第 363 行），以及占位的 `JacNonLinearEqCon = [];`/`JacNonLinearIneqCon = [];`（第 371、377 行，Jacobian 留作未来扩展）。
5. **真正调用 fmincon** `Optimize()`（第 396–535 行）：`matlabIf->EvalString("format long")` 防止字符串传输丢精度（第 405 行）；构造 `optimset` 选项串，把 `MaxIter` 追加进选项（第 411–455 行）；分别把 `variable`、`variableMinimum`、`variableMaximum` 组成 MATLAB 列向量 `X0`、`Lower`、`Upper`（第 467–506 行）；执行 `GmatFminconOptimizationDriver;`（第 513–514 行）；读回 `exitFlag`（第 521–525 行），`exitFlag > 0` 视为收敛（第 527–531 行）。
6. **收敛语义** `WriteToTextFile(FINISHED)`（第 1311–1388 行）：把 `fminconExitFlag` 映射为人类可读信息——1=一阶最优条件满足、2=变量逼近最优点、3=目标函数变化小于阈值、4=搜索方向过小、5=目标函数变化小于收敛准则（均收敛），0=函数/迭代次数超限，-1=被输出函数中止，-2=无可行点，-3=无界（第 1316–1362 行）。

目标函数与约束的组织：目标值 `cost`、梯度 `gradient`、等式约束残差 `eqConstraintValues`（对应 `h(x)=0`）、不等式约束残差 `ineqConstraintValues`（对应 `g(x)≤0`）都来自基类 `Solver`/`ExternalOptimizer` 的成员，由 GMAT 的 `Minimize`/`NonlinearConstraint` 命令填充；MATLAB 侧 driver 把 `NonLinearEqCon`/`NonLinearIneqCon` 作为 `fmincon` 的 `ceq`/`c` 传入。边界约束则直接通过 `Lower`/`Upper` 列向量交给 fmincon 的 `lb`/`ub` 参数。也就是说，"公式化"发生在 MATLAB 的 m 文件与 GMAT 的 Optimize/Constraint 命令之间，本 C++ 类只负责搬运这些数值。

#### 参数表（FminconOptimizer，见 .cpp 第 56–97 行静态表）

| 脚本名 | ID | 类型 | 说明 |
| --- | --- | --- | --- |
| `Options` | `OPTIONS` | `STRINGARRAY_TYPE` | fmincon 选项名数组（第 59 行） |
| `OptionValues` | `OPTION_VALUES` | `STRINGARRAY_TYPE` | 与 Options 对应的值数组（第 60 行） |
| `DiffMaxChange` | `MATLAB_OPTIONS_OFFSET+0`（1000） | `STRING_TYPE` | 有限差分最大步长，默认 0.1000 |
| `DiffMinChange` | `1001` | `STRING_TYPE` | 有限差分最小步长，默认 1.0e-08 |
| `MaxFunEvals` | `1002` | `STRING_TYPE` | 最大函数求值次数，默认 1000 |
| `TolX` | `1003` | `STRING_TYPE` | 变量容差，默认 1.0e-04 |
| `TolFun` | `1004` | `STRING_TYPE` | 函数容差，默认 1.0e-04 |
| `TolCon` | `1005` | `STRING_TYPE` | 约束容差，默认 1.0e-04 |

选项合法性由 `IsAllowedOption`（第 1800–1805 行）与 `IsAllowedValue`（第 1811–1833 行，数值型须 >0、`MaxFunEvals` 须正整数）校验；`GetParameterText` 对 1000–1005 区间直接返回 `ALLOWED_OPTIONS[id-1000]`（第 583–587 行）。`IsParameterReadOnly` 把 `OPTIMIZER_TOLERANCE` 与 `SOURCE_TYPE` 置只读（第 664–670 行）。

#### 与 core 的扩展点

| core 基类 | 相对路径 | 需重写的虚函数（本插件已实现） |
| --- | --- | --- |
| `ExternalOptimizer` | `src/base/solver/ExternalOptimizer.hpp` | `Initialize()`、`AdvanceState()`、`AdvanceNestedState()`、`Optimize()`、`OpenConnection()`、`CloseConnection()`、`RunExternal()`、`RunNominal()`、`CalculateParameters()`、`RunComplete()`、`WriteToTextFile()`、`GetProgressString()` |
| `GmatBase` | `src/base/foundation/GmatBase.hpp` | `Clone()`、`Copy()`、参数访问方法（`Get/SetStringParameter`、`GetStringArrayParameter` 等） |
| `Factory` | `src/base/factory/Factory.hpp` | `CreateObject()`、`CreateSolver()` |

#### 文件清单附录

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/include/fmincon_defs.hpp` | DLL 导入导出宏 | `FMINCON_API` |
| `src/base/factory/FminconOptimizerFactory.hpp` | 工厂声明 | `FminconOptimizerFactory` |
| `src/base/factory/FminconOptimizerFactory.cpp` | 工厂实现 | `CreateObject`、`CreateSolver` |
| `src/base/solver/FminconOptimizer.hpp` | 优化器声明 | `FminconOptimizer`、选项静态表 |
| `src/base/solver/FminconOptimizer.cpp` | 优化器实现 | `Initialize`、`AdvanceState`、`AdvanceNestedState`、`Optimize`、`OpenConnection`、`IsAllowedOption/Value`、`EvalMatlabString` |
| `src/base/plugin/GmatPluginFunctions.hpp` | 插件接口声明 | `GetFactoryCount`、`GetFactoryPointer` |
| `src/base/plugin/GmatPluginFunctions.cpp` | 插件接口实现 | `GetFactoryPointer`（`new FminconOptimizerFactory`）、`SetMessageReceiver` |

> 注：fmincon 的真正求解与目标/约束求值依赖 MATLAB 侧脚本 `GmatFminconOptimizationDriver.m`、`EvaluateGMATObjective.m`、`EvaluateGMATConstraints.m`、`CallGMATfminconSolver.m`（`OpenConnection` 第 1566–1607 行校验），这些文件不属于本插件的 C++ 源清单。

### 13.12 FormationPlugin（编队对象）

**目录**：`plugins/FormationPlugin/src/base/`，子目录 `factory/`、`formation/`、`include/`、`plugin/`，共 7 个 C++ 文件（3 个 `.cpp`、4 个 `.hpp`，另有 2 个 `.gitignore`）。

**构建开关**：`PLUGIN_FORMATION`，默认 `ON`，见 `plugins/CMakeLists.txt` 第 121 行。

**目标库名**：`Formation`，由 `plugins/FormationPlugin/src/base/CMakeLists.txt` 第 17 行 `SET(TargetName Formation)` 决定；`DEFINE_SYMBOL` 为 `FORMATION_EXPORTS`（第 36 行）。

**一句话目的**：提供 `Formation` 这种复合 `SpaceObject`，把多个成员航天器的状态拼接成一个可整体传播的编队状态。

#### 目的与职责

`Formation` 继承 `FormationInterface`（`src/base/spacecraft/FormationInterface.hpp`，本身是 `SpaceObject` 派生类），代表一组航天器组成的编队。它维护成员名单 `componentNames`（StringArray）与成员指针 `components`（`std::vector<SpaceObject*>`），把编队建模为一个"复合状态对象"：`dimension` 是所有成员状态尺寸之和，`BuildState()` 将各成员状态顺序拼接为一个 `GmatState`，`UpdateState()`/`UpdateElements()` 在编队状态与成员状态之间双向同步。这样编队可作为一个整体交给传播器积分，同时每个成员又能单独读取。

需澄清一点：本插件的 `Formation` **不是**"参考航天器 + 相对状态"的差分建模。它的编队状态是成员绝对状态的简单拼接（见 `BuildState`，第 1103–1116 行），编队的 MJ2000 状态取各成员状态的**几何中心**（`GetMJ2000State`，第 215–220 行），并没有显式的相对状态变量或参考星。相对状态的语义留给上层坐标系/测量体系处理。

#### 导出类清单

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `Formation` | `FormationInterface`（`src/base/spacecraft/FormationInterface.hpp`） | 由多个 SpaceObject 成员组成的编队对象 |
| `FormationFactory` | `Factory`（`src/base/factory/Factory.hpp`） | 创建 `Formation`，类型 `Gmat::FORMATION` |

`Formation.hpp` 第 38 行 `class FORMATION_API Formation : public FormationInterface`；`FormationFactory.hpp` 第 42 行 `class FORMATION_API FormationFactory : public Factory`。

#### 插件注册与工厂

`plugin/GmatPluginFunctions.cpp`：`GetFactoryCount()` 返回 `1`（第 51 行），`GetFactoryPointer(0)` 返回 `new FormationFactory`（第 72–73 行）。

`FormationFactory::CreateFormation` 在 `ofType == "Formation"` 时 `new Formation(Gmat::FORMATION, ofType, withName)`（`factory/FormationFactory.cpp` 第 152–153 行），`CreateObject` 委托（第 133 行）。默认构造 `Factory(Gmat::FORMATION)` 并 `creatables.push_back("Formation")`（第 46–51 行），额外 `GmatType::RegisterType(Gmat::FORMATION, "Formation")` 注册类型名（第 54 行）。与其它插件工厂不同，此工厂无列表构造，但有拷贝构造/赋值（第 79–114 行）。

#### 逐文件讲解

##### ##### include/FormationDefs.hpp

职责：DLL 导入导出宏。`FORMATION_EXPORTS` 决定 `FORMATION_API`（第 49–53 行），含 STL 模板导出宏（第 62–67 行），非 Windows 置空（第 74–76 行）。文件名仍是模板遗留的 `SampleDefs`（第 33 行注释），但实现与其它插件一致。

##### ##### factory/FormationFactory.hpp

职责：声明工厂。重写 `CreateObject` 与 `CreateFormation`（第 50–53 行），提供默认/拷贝构造、赋值、析构（第 45–48 行）。

##### ##### factory/FormationFactory.cpp

职责：实现工厂。`CreateFormation` 创建 `Formation`（第 149–156 行）。默认构造注册 `Gmat::FORMATION` 类型（第 45–55 行）。

##### ##### formation/Formation.hpp

职责：声明编队类。重写 `GetMJ2000State`（A1Mjd/GmatTime 两个重载，第 47–48 行）、`RenameRefObject`/`Clone`/`Copy`/`ParametersHaveChanged`（第 50–55 行），参数访问方法（第 58–89 行），引用对象方法 `GetRefObjectTypeArray`/`GetRefObjectNameArray`/`Get/SetRefObject`/`GetRefObjectArray`（第 91–104 行），状态同步 `BuildState`/`UpdateElements`/`UpdateState`（第 106–108 行），机动检查 `IsManeuvering`/`GetManeuveringMembers`（第 109–111 行），动作 `TakeAction`/`ClearLastStopTriggered`（第 113–115 行），传播项 `SetPropItem`/`GetDefaultPropItems`/`GetPropItem`/`GetPropItemSize`（第 120–123 行）。成员 `componentNames`/`components`/`dimension`/`satCount`（第 128–135 行）。参数枚举 `ADDED_SPACECRAFT`/`REMOVED_SPACECRAFT`/`CLEAR_NAMES`/`FORMATION_STM`/`FORMATION_CARTESIAN_STATE`（第 139–145 行）。私有辅助 `ClearSpacecraftList`/`RemoveSpacecraft`（第 155–156 行）。

##### ##### formation/Formation.cpp

职责：实现编队类。静态参数表 `PARAMETER_TEXT` = `Add`/`Remove`/`Clear`/`STM`/`CartesianState`（第 53–60 行），类型 `OBJECTARRAY_TYPE`/`OBJECT_TYPE`/`BOOLEAN_TYPE`/`RMATRIX_TYPE`/`REAL_TYPE`（第 64–71 行）。构造函数 `FormationInterface(typeId, typeStr, instName)`，`dimension=0`、`satCount=0`（第 90–100 行）。状态拼接/同步/中心计算见"关键类深读"。

##### ##### plugin/GmatPluginFunctions.hpp / .cpp

职责：插件接口声明与实现。`.hpp` 声明 `GetFactoryCount`/`GetFactoryPointer`/`SetMessageReceiver`（第 40–42 行）；`.cpp` 实现 `SetMessageReceiver`（第 96 行）。

#### 关键类深读：Formation

编队的状态模型围绕 `components` 成员指针展开（行号见 `formation/Formation.cpp`）：

1. **加入成员** `SetRefObject(obj, Gmat::SPACECRAFT, name)`（第 929–983 行）：把 `obj` 转成 `SpaceObject*`，去重后累加 `dimension += ps->GetSize()`（第 945–947 行）；第一个成员时把编队历元/精度时间标志对齐到该成员（第 950–955 行），后续成员历元不一致则抛 `SpaceObjectException`（第 956–965 行）；随后 `components.push_back(so)`（第 966 行）。若 `type == Gmat::FORMATION`，明确禁止"编队的编队"（第 968–973 行）。
2. **拼接状态** `BuildState()`（第 1083–1145 行）：`dimension <= 0` 抛异常；分配 `data[dimension]`，按成员顺序把每个成员的 `GmatState` 逐段拷贝（第 1103–1116 行），`state.SetState(data, dimension)` 后释放临时数组（第 1136–1144 行）。
3. **双向同步**：`UpdateState()`（第 1179–1220 行）把各成员当前状态 `memcpy` 回编队状态并校验成员历元同步；`UpdateElements()`（第 1155–1169 行）反向把编队状态切片写回各成员（若成员本身是 Formation 则递归，第 1166–1167 行）。
4. **几何中心** `GetMJ2000State(atTime)`（第 191–233 行，GmatTime 重载第 249–291 行）：`satCount = components.size()`，对前 `6*satCount` 个元素求和并 `centerState /= satCount`（第 215–220 行），再减去 `j2000Body` 与 `origin` 的 MJ2000 状态（第 223–232 行），得到编队中心的惯性状态。
5. **参数驱动的增删**：`SetStringParameter(ADDED_SPACECRAFT, value)` 在 `componentNames` 里查重后追加（第 615–633 行）；带 index 的重载支持按位替换或追加（第 728–757 行）；`REMOVED_SPACECRAFT` 调 `RemoveSpacecraft`（第 634–636 行）；`CLEAR_NAMES` 布尔参数调 `ClearSpacecraftList`（第 546–552 行）。`RemoveSpacecraft`/`ClearSpacecraftList` 分别删除名字与指针（第 1316–1394 行）。
6. **机动与动作**：`IsManeuvering` 遍历成员（第 1231–1240 行），`GetManeuveringMembers` 返回正在机动的成员名（第 1251–1260 行）；`TakeAction` 支持 `"Clear"`/`"Remove"` 动作（第 1275–1288 行）。
7. **传播项**：`SetPropItem` 把 `"CartesianState"`/`"STM"` 映射为 `Gmat::CARTESIAN_STATE`/`Gmat::ORBIT_STATE_TRANSITION_MATRIX`（第 1397–1405 行）；`GetPropItem` 对 CARTESIAN_STATE 返回 `state.GetState()`（第 1421–1423 行）；`GetPropItemSize` 对 STM 返回 `36 * satCount`（第 1450–1452 行）。

继承 `FormationInterface`（进而 `SpaceObject`）需重写的虚函数：`GetMJ2000State`、`BuildState`、`UpdateElements`、`UpdateState`、`IsManeuvering`、`GetManeuveringMembers`、`TakeAction`，以及引用对象与参数访问方法。

#### 参数表（Formation，见 .cpp 第 53–71 行静态表）

| 脚本名 | ID | 类型 | 说明 |
| --- | --- | --- | --- |
| `Add` | `ADDED_SPACECRAFT` | `OBJECTARRAY_TYPE` | 追加成员航天器名（第 55、66 行） |
| `Remove` | `REMOVED_SPACECRAFT` | `OBJECT_TYPE` | 移除成员（第 56、67 行；只读，第 474 行） |
| `Clear` | `CLEAR_NAMES` | `BOOLEAN_TYPE` | 清空成员列表（第 57、68 行；只读，第 474 行） |
| `STM` | `FORMATION_STM` | `RMATRIX_TYPE` | 编队状态转移矩阵（第 58、69 行） |
| `CartesianState` | `FORMATION_CARTESIAN_STATE` | `REAL_TYPE` | 编队拼接后的笛卡尔状态（第 59、70 行；`GetRealParameter` 第 1499–1500 行按 `id-FORMATION_CARTESIAN_STATE` 索引） |

`IsParameterReadOnly` 额外把 `EPOCH_PARAM`、`ORBIT_COLOR`、`TARGET_COLOR` 及 `FORMATION_CARTESIAN_STATE` 区间置只读（第 469–485 行）。

#### 与 core 的扩展点

| core 基类 | 相对路径 | 需重写的虚函数（本插件已实现） |
| --- | --- | --- |
| `FormationInterface` | `src/base/spacecraft/FormationInterface.hpp` | `GetMJ2000State`、`BuildState`、`UpdateElements`、`UpdateState`、`IsManeuvering`、`GetManeuveringMembers`、`TakeAction`、`SetPropItem`、`GetPropItem` 等 |
| `SpaceObject`（FormationInterface 的基类） | `src/base/spacecraft/SpaceObject.hpp` | 参数访问、`GetRefObject*`/`SetRefObject` 系列 |
| `GmatBase` | `src/base/foundation/GmatBase.hpp` | `Clone()`、`Copy()`、`RenameRefObject()`、`GetParameterText/ID/Type` 等 |
| `Factory` | `src/base/factory/Factory.hpp` | `CreateObject()`、`CreateFormation()` |

#### 文件清单附录

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/include/FormationDefs.hpp` | DLL 导入导出宏 | `FORMATION_API` |
| `src/base/factory/FormationFactory.hpp` | 工厂声明 | `FormationFactory` |
| `src/base/factory/FormationFactory.cpp` | 工厂实现 | `CreateObject`、`CreateFormation`、`GmatType::RegisterType` |
| `src/base/formation/Formation.hpp` | 编队类声明 | `Formation`、参数枚举、成员 `componentNames`/`components` |
| `src/base/formation/Formation.cpp` | 编队类实现 | `GetMJ2000State`、`BuildState`、`UpdateElements`、`UpdateState`、`SetRefObject`、`RemoveSpacecraft`、`SetPropItem` |
| `src/base/plugin/GmatPluginFunctions.hpp` | 插件接口声明 | `GetFactoryCount`、`GetFactoryPointer` |
| `src/base/plugin/GmatPluginFunctions.cpp` | 插件接口实现 | `GetFactoryPointer`（`new FormationFactory`）、`SetMessageReceiver` |

### 13.13 GeometricMeasurementPlugin（几何测量模型）

**目录**：`plugins/GeometricMeasurementPlugin/src/base/`，子目录 `factory/`、`include/`、`measurement/`、`plugin/`，共 13 个 C++ 文件（6 个 `.cpp`、7 个 `.hpp`，另加 1 个 `CMakeLists.txt`）。

**构建开关**：`PLUGIN_GEOMETRICMEASUREMENT`，默认 `OFF`，见 `plugins/CMakeLists.txt` 第 122 行。

**目标库名**：`GeometricMeasurements`，由 `plugins/GeometricMeasurementPlugin/src/base/CMakeLists.txt` 第 17 行 `SET(TargetName GeometricMeasurements)` 决定；`PLUGIN_SRCS`（第 25–32 行）列出 6 个源文件。第 39 行 `DEFINE_SYMBOL "GEOMETRICMEAS_EXPORTS"` 注入导出宏；第 43 行 `TARGET_LINK_LIBRARIES(... GmatEstimation)` 额外链接估计库（几何测量依赖其中的 `CoreMeasurement`/`SignalBase` 计算辅助方法）。

**一句话目的**：提供四个瞬时几何测量模型（测距、测距率、方位俯仰、赤经赤纬），用两参与体（航天器/地面站）的相对位置速度直接算出观测量，供 GMAT 仿真与估计（OD）使用。

#### 目的与职责

该插件把"几何测量"实现为四个 `CoreMeasurement` 派生类。与携带光时修正、介质修正等复杂信号链路的测量模型不同，几何测量是**瞬时**的：它不传播光行时间、不做大气折射修正（`GeometricRange.hpp` 第 42–45 行注释明确"不计算光行时间、不做路径修正"），而是用接收/发射两参与体在同一历元的相对位置（速度）直接求出标量观测量。`Evaluate(bool withEvents)` 是每个类的核心（`GeometricRange.cpp` 第 203 行、`GeometricRangeRate.cpp` 第 139 行、`GeometricAzEl.cpp` 第 155 行、`GeometricRADec.cpp` 第 153 行），它先调用继承自 `CoreMeasurement`/`SignalBase` 的 `CalculateRangeVectorInertial()` 或 `CalculateRangeRateVectorObs()` 得到惯性系/观测系相对矢量，再做求模、点积或反三角运算。

四个模型的观测量维度：`GeometricRange` 与 `GeometricRangeRate` 各 1 维；`GeometricAzEl` 与 `GeometricRADec` 各 2 维（`measurementSize = 2`，见 `GeometricAzEl.cpp` 第 64 行、`GeometricRADec.cpp` 第 60 行），并配置 2×2 协方差矩阵（`covariance.SetDimension(2)`）。`GeometricAzEl` 在观测系（站心/地面站参考系）中算方位俯仰，`GeometricRADec` 在惯性系（J2000）中算赤经赤纬——二者代码几乎相同，仅观测坐标系不同。

> 注：本插件 `#include "CoreMeasurement.hpp"`（如 `GeometricRange.hpp` 第 37 行），但该头文件不在当前 depth-1 克隆中；本 checkout 内 EstimationPlugin 的测量基类头文件为 `plugins/EstimationPlugin/src/base/measurement/MeasurementModelBase.hpp`（第 44 行 `class ESTIMATION_API MeasurementModelBase : public GmatBase`）。插件默认 `OFF` 与此依赖缺失（以及计算辅助方法实际位于 `SignalBase`）有关。

#### 导出类清单

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `GeometricRange` | `CoreMeasurement`（`#include "CoreMeasurement.hpp"`） | 瞬时测距 ρ=\|r\| |
| `GeometricRangeRate` | `CoreMeasurement` | 瞬时测距率 ρ̇=ṙ·û |
| `GeometricAzEl` | `CoreMeasurement` | 瞬时方位角/俯仰角 |
| `GeometricRADec` | `CoreMeasurement` | 瞬时赤经/赤纬 |
| `MeasurementFactory` | `Factory`（`src/base/factory/Factory.hpp`） | 创建上述测量对象，类型 `Gmat::CORE_MEASUREMENT` |

继承声明行号：`GeometricRange.hpp` 第 47 行、`GeometricRangeRate.hpp` 第 43 行、`GeometricAzEl.hpp` 第 42 行、`GeometricRADec.hpp` 第 39 行分别 `: public CoreMeasurement`；`MeasurementFactory.hpp` 第 41 行 `: public Factory`。

#### 插件注册与工厂

`plugin/GmatPluginFunctions.cpp` 定义插件加载 C 接口：`GetFactoryCount()` 返回 `1`（第 50–53 行），`GetFactoryPointer(index)` 在 `case 0` 时 `new MeasurementFactory`（第 70–74 行），`SetMessageReceiver` 调用 `MessageInterface::SetMessageReceiver(mr)`（第 93–96 行）。头文件在 `extern "C"` 中声明这三个符号（`GmatPluginFunctions.hpp` 第 41–46 行）。

`MeasurementFactory::CreateMeasurement`（`factory/MeasurementFactory.cpp` 第 68–80 行）按类型字符串创建 `"GeometricRange"`/`"GeometricRangeRate"`/`"GeometricAzEl"`/`"GeometricRADec"`；`CreateObject` 委托给它（第 49–53 行）。默认构造函数以 `Factory(Gmat::CORE_MEASUREMENT)` 初始化并压入四个 `creatables`（第 91–101 行）；列表构造（第 153–163 行）、拷贝构造（第 176–186 行）、赋值（第 127–141 行）沿用同一模式。

#### 逐文件讲解

##### include/geometricmeasurement_defs.hpp

职责：DLL 导入/导出宏。Windows + MSVC + `_DYNAMICLINK` 下按 `GEOMETRICMEAS_EXPORTS` 定义 `GEOMETRICMEAS_API` 为 `__declspec(dllexport/dllimport)`（第 52–55 行），并处理 STL 模板导出 `DECLSPECIFIER`/`EXPIMP_TEMPLATE`（第 65–71 行）；非 Windows 或未定义宏时置空（第 77–79 行）。`GEOMETRICMEAS_EXPORTS` 由 CMake 第 39 行 `DEFINE_SYMBOL` 注入。

##### factory/MeasurementFactory.hpp / .cpp

职责：工厂声明与实现，见"插件注册与工厂"。`.hpp` 重写 `CreateObject` 与 `CreateMeasurement`（第 50–53 行），include `CoreMeasurement.hpp`（第 38 行）。

##### plugin/GmatPluginFunctions.hpp / .cpp

职责：插件加载 C 接口声明与实现，模式与其它插件一致。`.hpp` 末尾附 Doxygen `\mainpage`（第 52–58 行）。

##### measurement/GeometricRange.hpp / .cpp

职责：瞬时测距。`.hpp` 重写 `Clone/Initialize/CalculateMeasurementDerivatives`（第 55–59 行）与保护 `Evaluate`（第 62 行）。`.cpp` 构造函数 `CoreMeasurement("GeometricRange", name)` 并设 `currentMeasurement.type = Gmat::GEOMETRIC_RANGE`、1×1 协方差（第 55–67 行）。`Evaluate(bool withEvents)`（第 203–283 行）：取地面站最小仰角（第 213–218 行），`CalculateRangeVectorInertial()`（第 220 行），以 `R_o_j2k * rangeVecInertial` 的单位矢量 z 分量反算仰角作可行性判据（第 223–224 行），观测量 `currentMeasurement.value[0] = rangeVecInertial.GetMagnitude()`（第 232/239/244 行，三条分支对应无事件/可行/不可行，不可行时 `unfeasibleReason="B1"` 第 245 行）。

##### measurement/GeometricRangeRate.hpp / .cpp

职责：瞬时测距率。`.hpp` 结构同 `GeometricRange`（`Evaluate` 第 57 行）。`.cpp` 构造函数设 `Gmat::GEOMETRIC_RANGE_RATE`（第 62 行）。`Evaluate`（第 139–158 行）：`CalculateRangeRateVectorObs()`（第 149 行），可行性判据 `rangeVecInertial * p1Loc`（第 152 行，即相对矢量与站位置矢量的点积）；可行时 `rangeUnit = rangeVecObs.GetUnitVector()`（第 156 行），观测量 `currentMeasurement.value[0] = rangeRateVecObs * rangeUnit`（第 157 行），不可行时置 0（第 162 行）。

##### measurement/GeometricAzEl.hpp / .cpp

职责：瞬时方位/俯仰。`.hpp` 结构同前（`Evaluate` 第 56 行）。`.cpp` 构造函数设 `Gmat::GEOMETRIC_AZ_EL`、`measurementSize=2`（第 62–64 行）。`Evaluate`（第 155–195 行）：`CalculateRangeRateVectorObs()`（第 166 行，顺带更新旋转矩阵得到 `rangeVecObs`），可行性闸门 `(feasibilityValue>0) && Abs(rangeVecObs[0])>=1e-8`（第 176 行）；`range = rangeVecObs.GetMagnitude()`（第 180 行），俯仰 `value[1] = ASin(rangeVecObs[2]/range)`（第 181 行），方位 `value[0] = ATan(rangeVecObs[1], -rangeVecObs[0])`（第 188 行）；俯仰等于 90° 时抛 `MeasurementException`（第 183–187 行）。

##### measurement/GeometricRADec.hpp / .cpp

职责：瞬时赤经/赤纬。`.hpp` 额外声明 `InitializeMeasurement()`（第 55 行）。`.cpp` 构造函数设 `Gmat::GEOMETRIC_RA_DEC`、`measurementSize=2`（第 58–60 行）。`Evaluate`（第 153–194 行）与 `GeometricAzEl` 逐行同构：赤纬 `value[1] = ASin(rangeVecObs[2]/range)`（第 180 行）、赤经 `value[0] = ATan(rangeVecObs[1], -rangeVecObs[0])`（第 187 行），差别仅在 `rangeVecObs` 所在坐标系（RA/Dec 用惯性 J2000 系）。

#### 关键类深读：几何测距/测距率/方位俯仰/赤经赤纬的计算公式

相对矢量的构造由 EstimationPlugin 的 `SignalBase` 提供（几何测量通过 `CoreMeasurement` 继承链调用，行号均见 `plugins/EstimationPlugin/src/base/signal/SignalBase.cpp`）：

- **惯性系相对位置** `CalculateRangeVectorInertial()`（第 1190–1212 行）：`theData.rangeVecInertial = theData.rLoc + theData.j2kOriginSep - theData.tLoc`（第 1212 行，注释标注 GMAT MathSpec 式 6.12），即 ρ = **r**₂ − **r**₁（接收点相对发射点）。
- **观测系相对速度** `CalculateRangeRateVectorObs()`（第 1324–1352 行）：`rangeRateVecInertial = rVel - j2kOriginVel - tVel`（第 1339 行），有地面站参与时 `rangeRateVecObs = RDot_Obs_j2k*rangeVecInertial + R_Obs_j2k*rangeRateVecInertial`（第 1348 行），否则直取惯性系值（第 1350 行）。

四个 `Evaluate` 据此给出观测量（行号见各 `.cpp`）：

| 模型 | 公式（代码对应） | 关键行 |
| --- | --- | --- |
| `GeometricRange` | ρ = \|rangeVecInertial\| = \|**r**₂−**r**₁\| | `GeometricRange.cpp` 第 232/239/244 行 |
| `GeometricRangeRate` | ρ̇ = rangeRateVecObs · û，û = rangeVecObs/\|rangeVecObs\| | `GeometricRangeRate.cpp` 第 156–157 行 |
| `GeometricAzEl` | el = asin(z/ρ)，az = atan2(y, −x)（站心观测系） | `GeometricAzEl.cpp` 第 180–188 行 |
| `GeometricRADec` | dec = asin(z/ρ)，RA = atan2(y, −x)（惯性 J2000 系） | `GeometricRADec.cpp` 第 179–187 行 |

其中 ρ = \|rangeVecObs\|，z/x/y 为相对矢量在观测系的三分量；方位角用双参数 `ATan(y, -x)`（第 188/187 行）保证象限正确。`CalculateMeasurementDerivatives`（如 `GeometricRange.cpp` 第 375–504 行）用单位矢量 û（`rangeVecInertial.GetUnitVector()`）给出解析偏导：对发射点位置偏导为 −û、对接收点为 +û（第 385、396、466、477 行），供 OD 的状态雅可比使用。

#### 参数表

四个几何测量类**不新增**脚本参数——它们不覆盖 `GetParameterText`/`GetParameterID` 等（无 `PARAMETER_TEXT`/`PARAMETER_TYPE` 静态表），全部参数（如参与体 `Participants`、历元等）继承自 `CoreMeasurement`。构造函数仅写入内部标识：

| 类 | `currentMeasurement.type` | `measurementSize` | 行号 |
| --- | --- | --- | --- |
| `GeometricRange` | `Gmat::GEOMETRIC_RANGE` | 1（默认） | `GeometricRange.cpp` 第 63 行 |
| `GeometricRangeRate` | `Gmat::GEOMETRIC_RANGE_RATE` | 1（默认） | `GeometricRangeRate.cpp` 第 62 行 |
| `GeometricAzEl` | `Gmat::GEOMETRIC_AZ_EL` | 2 | `GeometricAzEl.cpp` 第 62–64 行 |
| `GeometricRADec` | `Gmat::GEOMETRIC_RA_DEC` | 2 | `GeometricRADec.cpp` 第 58–60 行 |

#### 与 core 的扩展点

- 继承 `CoreMeasurement`（`#include "CoreMeasurement.hpp"`；本 checkout 中该头文件缺失，EstimationPlugin 现行测量基类为 `plugins/EstimationPlugin/src/base/measurement/MeasurementModelBase.hpp`，第 44 行 `: public GmatBase`），须重写 `Initialize()` 与保护方法 `Evaluate(bool withEvents)`。
- 计算辅助方法 `CalculateRangeVectorInertial()`/`CalculateRangeRateVectorObs()` 为 `SignalBase` 的虚方法（声明于 `plugins/EstimationPlugin/src/base/signal/SignalBase.hpp` 第 234、236 行，实现于 `SignalBase.cpp` 第 1190、1324 行），几何测量通过继承链复用。
- 继承 `src/base/factory/Factory.hpp` 的 `Factory`，须重写 `CreateObject`（另提供 `CreateMeasurement`）。
- 链接依赖 `GmatEstimation`（`CMakeLists.txt` 第 43 行），故 `GeometricMeasurement` 与估计子系统共用 `MeasurementData`/`SignalBase` 等类型。

#### 文件清单附录

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `plugins/GeometricMeasurementPlugin/src/base/CMakeLists.txt` | 构建脚本 | `SET(TargetName GeometricMeasurements)`、`GmatEstimation` |
| `plugins/GeometricMeasurementPlugin/src/base/include/geometricmeasurement_defs.hpp` | DLL 导出宏 | `GEOMETRICMEAS_API` |
| `plugins/GeometricMeasurementPlugin/src/base/factory/MeasurementFactory.hpp` | 工厂声明 | `MeasurementFactory` |
| `plugins/GeometricMeasurementPlugin/src/base/factory/MeasurementFactory.cpp` | 工厂实现 | `CreateMeasurement`、`creatables` |
| `plugins/GeometricMeasurementPlugin/src/base/plugin/GmatPluginFunctions.hpp` | 加载接口声明 | `GetFactoryCount` 等 |
| `plugins/GeometricMeasurementPlugin/src/base/plugin/GmatPluginFunctions.cpp` | 加载接口实现 | `GetFactoryPointer` |
| `plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricRange.hpp` | 测距声明 | `GeometricRange` |
| `plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricRange.cpp` | 测距实现 | `Evaluate`、`CalculateMeasurementDerivatives` |
| `plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricRangeRate.hpp` | 测距率声明 | `GeometricRangeRate` |
| `plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricRangeRate.cpp` | 测距率实现 | `Evaluate` |
| `plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricAzEl.hpp` | 方位俯仰声明 | `GeometricAzEl` |
| `plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricAzEl.cpp` | 方位俯仰实现 | `Evaluate` |
| `plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricRADec.hpp` | 赤经赤纬声明 | `GeometricRADec` |
| `plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricRADec.cpp` | 赤经赤纬实现 | `Evaluate`、`InitializeMeasurement` |

### 13.14 GmatFunctionPlugin（GMAT 脚本函数）

**目录**：`plugins/GmatFunctionPlugin/src/base/`，子目录 `command/`、`factory/`、`function/`、`include/`、`plugin/`，共 14 个 C++ 文件（6 个 `.cpp`、8 个 `.hpp`，另有 1 个 `.gitignore`）。

**构建开关**：`PLUGIN_GMATFUNCTION`，默认 `ON`，见 `plugins/CMakeLists.txt` 第 123 行。

**目标库名**：`GmatFunction`，由 `plugins/GmatFunctionPlugin/src/base/CMakeLists.txt` 第 17 行 `SET(TargetName GmatFunction)` 决定；`DEFINE_SYMBOL` 为 `GMATFUNCTION_EXPORTS`（第 39 行）。`PLUGIN_SRCS` 含 6 个源：`CallGmatFunction.cpp`、`Global.cpp`、`GmatFunctionCommandFactory.cpp`、`GmatFunctionFactory.cpp`、`GmatFunction.cpp`、`GmatPluginFunctions.cpp`（第 25–32 行）。

**一句话目的**：把 GMAT 脚本函数（`.gmf`）作为 `UserDefinedFunction` 派生类及其配套命令（`CallGmatFunction`、`Global`）从核心系统迁出为插件，实现可被主脚本反复调用的子脚本执行。

#### 目的与职责

`GmatFunctionIntro.hpp` 说明本插件是 R2013a 起从 `libGmatBase` 迁移出的功能模块（第 38–42 行）：`GmatFunction` 表示一个 `.gmf` 文件（一个可复用子脚本），内部持有一条解析好的命令序列 `fcs`（Function Command Sequence，来自基类），`Initialize()` 负责把函数内部对象克隆进函数对象存储 `objectStore`、校验命令、初始化命令；`Execute()` 逐条执行 `fcs` 并把输出包装成 `ElementWrapper` 回写调用方。

配套两条命令：`CallGmatFunction`（继承 `CallFunction`）在主脚本里调用某个 `GmatFunction`，通过 `FunctionManager`（`fm`）完成进入/退出函数的上下文切换；`Global`（继承 `ManageObject`）把若干对象标记为全局（`SetIsGlobal(true)`）并搬入全局对象存储 GOS，使函数内外共享这些对象。插件同时导出两个工厂：`GmatFunctionFactory` 创建函数对象，`GmatFunctionCommandFactory` 创建两条命令。

#### 导出类清单

| 类名 | 基类 | 职责 |
| --- | --- | --- |
| `GmatFunction` | `UserDefinedFunction`（`src/base/function/UserDefinedFunction.hpp`） | 表示并执行一个 `.gmf` 脚本函数 |
| `CallGmatFunction` | `CallFunction`（`src/base/command/CallFunction.hpp`） | 调用 GMAT 函数的命令 |
| `Global` | `ManageObject`（`src/base/command/ManageObject.hpp`） | 把对象声明为全局对象 |
| `GmatFunctionFactory` | `Factory`（`src/base/factory/Factory.hpp`） | 创建 `GmatFunction`，类型 `Gmat::FUNCTION` |
| `GmatFunctionCommandFactory` | `Factory`（`src/base/factory/Factory.hpp`） | 创建 `CallGmatFunction`/`Global`，类型 `Gmat::COMMAND` |

基类确认：`GmatFunction.hpp` 第 40 行 `class ... GmatFunction : public UserDefinedFunction`；`CallGmatFunction.hpp` 第 37 行 `... : public CallFunction`；`Global.hpp` 第 43 行 `... : public ManageObject`；`GmatFunctionFactory.hpp` 第 44 行、`GmatFunctionCommandFactory.hpp` 第 40 行均继承 `Factory`。

#### 插件注册与工厂

`plugin/GmatPluginFunctions.cpp`：`GetFactoryCount()` 返回 `2`（第 51 行），`GetFactoryPointer(0)` 返回 `new GmatFunctionFactory`（第 76 行），`GetFactoryPointer(1)` 返回 `new GmatFunctionCommandFactory`（第 80 行）。

`GmatFunctionFactory::CreateFunction` 在 `ofType == "GmatFunction"` 时 `new GmatFunction(withName)`（`factory/GmatFunctionFactory.cpp` 第 78–79 行），`CreateObject` 委托（第 59 行）；默认构造 `Factory(Gmat::FUNCTION)` 并 `creatables.push_back("GmatFunction")`（第 96–103 行）。`GmatFunctionCommandFactory::CreateCommand` 分别创建 `CallGmatFunction` 与 `Global`（`factory/GmatFunctionCommandFactory.cpp` 第 132–136 行），默认构造 `Factory(Gmat::COMMAND)` 并 `creatables` 压入两条命令名（第 44–50 行）。

#### 逐文件讲解

##### ##### include/GmatFunction_defs.hpp

职责：DLL 导入导出宏。`GMATFUNCTION_EXPORTS` 决定 `GMATFUNCTION_API`（第 48–52 行），非 Windows 直接置空（第 71–72 行）；`IMPEXP_STDSTRING` 下导出 `std::basic_string`/`allocator` 模板实例（第 75–78 行）。

##### ##### include/GmatFunctionIntro.hpp

职责：Doxygen 主页面。说明模块来源与用途（第 32–43 行），给出加载方式 `PLUGIN = ./libGmatFunction`（第 50 行）。纯文档头，无代码。

##### ##### command/CallGmatFunction.hpp

职责：声明调用命令。重写 `Initialize()`、`Execute()`、`RunComplete()`、`Clone()`（第 47–52 行），无新增成员（第 54–56 行空保护段）。

##### ##### command/CallGmatFunction.cpp

职责：实现调用命令。构造函数 `CallFunction("CallGmatFunction")` 并 `objectTypeNames.push_back("CallGmatFunction")`（第 65–69 行）。`Initialize()` 先 `CallFunction::Initialize()`，当 `isGmatFunction` 为真时把 `solarSys`/`forces`/`globalObjectMap` 传给函数管理器 `fm`（第 133–146 行）；`Execute()` 校验 `mFunction` 非空，`isGmatFunction` 分支调 `fm.Execute(callingFunction)`，否则抛内部错误（第 163–203 行），随后 `BuildCommandSummary(true)`（第 210 行）；`RunComplete()` 在 `fm` 未 finalized 时 `fm.Finalize()`（第 243–248 行）。

##### ##### command/Global.hpp

职责：声明全局声明命令。重写 `Clone`、`Initialize`、`Execute`、`RenameRefObject`、`GetRefObjectNameArray`（第 51–60 行），参数枚举 `GlobalParamCount = ManageObjectParamCount`（第 67 行，无新增参数）。

##### ##### command/Global.cpp

职责：实现全局声明命令。构造函数 `ManageObject("Global")`（第 61 行）。`Initialize()` 先 `ManageObject::Initialize()`，遍历 `objectNames` `FindObject` 并 `obj->SetIsGlobal(true)`（第 151–166 行，注释说明提前在 Initialize 里打全局标记，使 `GmatFunction` 在 `Global` 命令执行前就能搜到全局对象）；`Execute()` 遍历 `objectNames`，若对象在局部对象存储 `objectMap`（LOS）则 `InsertIntoGOS` 搬入全局对象存储并 `objectMap->erase`（第 193–202 行），若已在 `globalObjectMap` 则确保类型匹配（第 204–213 行），找不到则抛 `CommandException`（第 214–219 行）；`RenameRefObject` 同步改 `objectNames`，并对 `PROP_SETUP` 类型处理 `_ForceModel` 后缀（第 246–289 行）。

##### ##### function/GmatFunction.hpp

职责：声明函数类。重写 `IsNewFunction`/`SetNewFunction`（第 50–51 行）、`Initialize`/`Execute`/`Finalize`（第 54–58 行）、`Clone`/`Copy`（第 61–62 行）、`SetStringParameter` 两个重载（第 64–67 行）。成员 `mIsNewFunction`、`unusedGlobalObjectList`（第 70–71 行）；保护方法 `InitializeLocalObjects`/`CreateSubscriberWrappers`/`SetGmatFunctionPath`/`BuildUnusedGlobalObjectList`/`ShowTrace`（第 73–82 行）。参数枚举 `GmatFunctionParamCount = FunctionParamCount`（第 86 行，无新增参数，静态参数表被注释掉）。

##### ##### function/GmatFunction.cpp

职责：实现函数类。构造函数 `UserDefinedFunction("GmatFunction", name)`，通过 `FileManager::GetGmatFunctionPath(name + ".gmf")` 解析函数路径（第 91–172 行）；析构用 `GmatCommandUtil::ClearCommandSeq(fcs, false)` 释放命令序列（第 191–192 行）。`Initialize`/`Execute`/`Finalize` 主体见"关键类深读"；`SetGmatFunctionPath` 处理相对/绝对路径拼装并 `AddGmatFunctionPath`（第 1339–1454 行）；`BuildUnusedGlobalObjectList` 找出未被函数使用、但以航天器为 origin/primary/secondary 的全局坐标系，供 `ObjectInitializer` 忽略未定义引用（第 1468–1518 行）。

##### ##### factory/GmatFunctionFactory.hpp / .cpp

职责：函数工厂。`.hpp` 重写 `CreateObject`/`CreateFunction`（第 48–51 行）；`.cpp` `CreateFunction` 创建 `GmatFunction`（第 75–85 行），构造/拷贝补齐 `creatables`（第 96–136 行）。

##### ##### factory/GmatFunctionCommandFactory.hpp / .cpp

职责：命令工厂。`.hpp` 只重写 `CreateCommand`（第 48–49 行）；`.cpp` `CreateCommand` 按类型创建 `CallGmatFunction`/`Global`（第 129–139 行），构造/拷贝补齐两条命令名（第 43–113 行）。

##### ##### plugin/GmatPluginFunctions.hpp / .cpp

职责：插件接口声明与实现。`.hpp` 声明 `GetFactoryCount`/`GetFactoryPointer`/`SetMessageReceiver`（第 46–48 行）；`.cpp` 实现两个工厂指针（第 69–88 行）与 `SetMessageReceiver`（第 108 行）。

#### 关键类深读：GmatFunction

函数对象的生命周期由三条核心方法驱动（行号见 `function/GmatFunction.cpp`）：

1. **解析（构造函数）** `GmatFunction(name)`（第 91–172 行）：`UserDefinedFunction("GmatFunction", name)` 基类负责类型注册；构造函数向 `FileManager` 查询 `name.gmf` 的路径 `GetGmatFunctionPath`，拼成完整 `functionPath` 并剥离出 `functionName`（第 109–129 行）；找不到时回退 `GMAT_FUNCTION_PATH`/`FUNCTION_PATH`（第 137–158 行）。脚本文本本身的词法/语法解析由核心 `Interpreter` 在函数创建时完成，本插件只持有解析出的 `fcs`。
2. **初始化** `Initialize(objInit, reinitialize, resetLocalObjects)`（第 271–684 行）：`!fcs` 直接返回 false；调 `UserDefinedFunction::Initialize`（第 299 行）；把 `validator` 绑定到本函数并设 `solarSys`（第 302–303 行）；遍历 `functionObjectMap` 把函数内创建的对象克隆进 `objectStore` 并 `SetIsLocal(true)`（第 313–401 行，含形参重定义类型检查第 379–393 行）；遍历 `automaticObjectMap` 处理自动对象（如 `sat.X`）的全局/局部归属并克隆（第 404–489 行）；把 `IsGlobal() && !IsLocal()` 的对象搬入 `globalObjectStore`（第 501–537 行）；构建 `validatorStore` 并 `validator->SetObjectMap`（第 547–555 行）；`CreateSubscriberWrappers()` 为订阅者创建 wrapper（第 562 行）；首次或重初始化时 `validator->HandleCcsdsEphemerisFile` 与 `InitializeLocalObjects(objInit, current, true)`（第 566–576 行）；随后沿 `fcs` 逐条 `current->SetObjectMap/SetGlobalObjectMap/SetSolarSystem/SetInternalCoordSystem/SetTransientForces`，未校验时 `validator->ValidateCommand(current, false, 2)` 再 `current->Initialize()`（第 580–661 行）；最后 `BuildUnusedGlobalObjectList()`（第 668 行）。
3. **执行** `Execute(objInit, reinitialize)`（第 690–974 行）：若 `objectsInitialized` 则先重初始化坐标系、计算点、航天器、Burns、求解器、参数等对象（第 741–758 行）；沿 `fcs` 循环，遇到非 `NoOp`/`Create`/`Global` 的真实命令时惰性 `InitializeLocalObjects`（第 783–822 行），然后 `current->Execute()`（第 833 行）；分支命令仍在执行则 `continue`（第 878–887 行）；结束后为每个输出名创建 `ElementWrapper` 并写入 `outputArgMap`（第 918–962 行）。
4. **收尾** `Finalize(cleanUp)`（第 980–1033 行）：未 finalized 时沿 `fcs` 对每条命令 `RunComplete()`（第 998–1017 行），再 `UserDefinedFunction::Finalize(cleanUp)`。

`InitializeLocalObjects(objInit, current, ignoreException)`（第 1175–1249 行）设置内部坐标系后调 `objInit->InitializeObjects(true, Gmat::UNKNOWN_OBJECT, unusedGlobalObjectList)`，并对"对象在创建前被引用"这种非致命异常按 `ignoreException` 选择忽略或重抛。

#### 关键类深读：CallGmatFunction 与 Global

- `CallGmatFunction` 是"调用点"：它不直接执行函数体，而是通过基类 `CallFunction` 持有的 `FunctionManager fm` 进出函数上下文。`Initialize()` 在函数首次进入前把 `solarSys`/`forces`/`globalObjectMap` 注入 `fm`（`command/CallGmatFunction.cpp` 第 143–145 行）；`Execute()` 调 `fm.Execute(callingFunction)`（第 193 行），由 `FunctionManager` 内部负责保存调用方对象映射、切换函数本地 `objectStore`、执行后恢复。
- `Global` 是"作用域声明"：`Initialize()` 提前把目标对象 `SetIsGlobal(true)`（`command/Global.cpp` 第 161 行），使函数解析期即可发现；`Execute()` 把对象从 LOS（`objectMap`）搬入 GOS（`InsertIntoGOS` + `erase`，第 201–202 行），从而让主脚本与函数共享同一对象实例。

#### 参数表

`GmatFunction`、`CallGmatFunction`、`Global` 均**无新增参数**：三者的 `PARAMETER_TEXT`/`PARAMETER_TYPE` 静态表都被注释掉（`GmatFunction.cpp` 第 69–77 行、`Global.cpp` 第 43–51 行；`GmatFunction.hpp` 第 89–92 行、`Global.hpp` 第 69–71 行）。它们继承的参数来自基类——`GmatFunction` 继承 `Function`/`UserDefinedFunction` 的 `FunctionPath`/`FunctionName`/输入输出形参（`SetStringParameter` 第 1079–1116 行处理 `FUNCTION_PATH`/`FUNCTION_NAME` 并委托基类）；`CallGmatFunction` 继承 `CallFunction` 的 `Function`（被调函数名）；`Global` 继承 `ManageObject` 的对象列表（`objectNames`）。

#### 与 core 的扩展点

| core 基类 | 相对路径 | 需重写的虚函数（本插件已实现） |
| --- | --- | --- |
| `UserDefinedFunction` | `src/base/function/UserDefinedFunction.hpp` | `Initialize()`、`Execute()`、`Finalize()` |
| `Function`（UserDefinedFunction 的基类） | `src/base/function/Function.hpp` | `IsNewFunction`/`SetNewFunction`、`SetStringParameter` |
| `CallFunction` | `src/base/command/CallFunction.hpp` | `Initialize()`、`Execute()`、`RunComplete()` |
| `ManageObject` | `src/base/command/ManageObject.hpp` | `Initialize()`、`Execute()`、`RenameRefObject()` |
| `GmatBase` | `src/base/foundation/GmatBase.hpp` | `Clone()`、`Copy()`、`GetRefObjectNameArray()` |
| `Factory` | `src/base/factory/Factory.hpp` | `CreateObject()`、`CreateFunction()` / `CreateCommand()` |

#### 文件清单附录

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/include/GmatFunction_defs.hpp` | DLL 导入导出宏 | `GMATFUNCTION_API` |
| `src/base/include/GmatFunctionIntro.hpp` | Doxygen 模块说明 | —（文档） |
| `src/base/command/CallGmatFunction.hpp` | 调用命令声明 | `CallGmatFunction` |
| `src/base/command/CallGmatFunction.cpp` | 调用命令实现 | `Initialize`、`Execute`、`RunComplete` |
| `src/base/command/Global.hpp` | 全局声明命令声明 | `Global` |
| `src/base/command/Global.cpp` | 全局声明命令实现 | `Initialize`、`Execute`、`RenameRefObject` |
| `src/base/function/GmatFunction.hpp` | 函数类声明 | `GmatFunction` |
| `src/base/function/GmatFunction.cpp` | 函数类实现 | `Initialize`、`Execute`、`Finalize`、`InitializeLocalObjects`、`SetGmatFunctionPath`、`BuildUnusedGlobalObjectList` |
| `src/base/factory/GmatFunctionFactory.hpp` | 函数工厂声明 | `GmatFunctionFactory` |
| `src/base/factory/GmatFunctionFactory.cpp` | 函数工厂实现 | `CreateObject`、`CreateFunction` |
| `src/base/factory/GmatFunctionCommandFactory.hpp` | 命令工厂声明 | `GmatFunctionCommandFactory` |
| `src/base/factory/GmatFunctionCommandFactory.cpp` | 命令工厂实现 | `CreateCommand`（`CallGmatFunction`/`Global`） |
| `src/base/plugin/GmatPluginFunctions.hpp` | 插件接口声明 | `GetFactoryCount`、`GetFactoryPointer` |
| `src/base/plugin/GmatPluginFunctions.cpp` | 插件接口实现 | `GetFactoryPointer`（两个工厂）、`SetMessageReceiver` |

## 四、关键设计模式与数据流

### 4.1 统一继承树：所有插件对象都挂在 core 扩展点之下

本章 13 个插件没有引入任何"插件私有基类"，每个业务类都继承自 core 中按领域划分的 base 类。继承图（括号内为 `read` 确认的头文件与行号）如下：

**传播类**
- `EphemerisPropagator` → `Propagator`（`plugins/EphemPropagatorPlugin/src/base/propagator/EphemerisPropagator.hpp:44`；`Propagator` 见 `src/base/propagator/Propagator.hpp:88`，其 → `GmatBase`）
- `CcsdsEphPropagator / SPKPropagator / Code500Propagator / StkEPropagator` → `EphemerisPropagator`（各 `.hpp:41~44`）
- `BulirschStoer` → `Integrator`（`plugins/ExtraPropagatorsPlugin/.../BulirschStoer.hpp:75`；`Integrator` 见 `src/base/propagator/Integrator.hpp:128`，其 → `Propagator`）
- `RungeKutta4` → `RungeKutta`（`plugins/EstimationPlugin/.../RungeKutta4.hpp:37`；`RungeKutta` 见 `src/base/propagator/RungeKutta.hpp:151` → `Integrator`）——即 EstimationPlugin 自带一个导航用 RK4 积分器。

**求解/估计类**
- `Estimator` → `Solver`（`plugins/EstimationPlugin/.../Estimator.hpp:54`；`Solver` 见 `src/base/solver/Solver.hpp:57`）
- `BatchEstimatorBase` → `Estimator`（`:53`）；`BatchEstimator` → `BatchEstimatorBase`（`:50`）；`Simulator` → `Solver`（`Simulator.hpp:47`）
- `SeqEstimator` → `Estimator`（`SeqEstimator.hpp:48`）；`ExtendedKalmanFilter` → `SeqEstimator`（`:59`）
- `SmootherBase` → `Estimator`（`SmootherBase.hpp:44`）；`Smoother` → `SmootherBase`（`:42`）
- `FminconOptimizer` → `ExternalOptimizer`（`FminconOptimizer.hpp:48`；`ExternalOptimizer` 见 `src/base/solver/ExternalOptimizer.hpp:43` → `Optimizer` → `Solver`）

**测量类**
- `MeasurementModelBase` → `GmatBase`（`measurement/MeasurementModelBase.hpp:44`）
- `TrackingDataAdapter` → `MeasurementModelBase`（`adapter/TrackingDataAdapter.hpp:63`）；`TrackingFileSet` → `MeasurementModelBase`（`trackingfile/TrackingFileSet.hpp:49`）
- `MeasureModel` → `GmatBase`（`measurementmodel/MeasureModel.hpp:60`）；`GPSPointMeasureModel` → `MeasureModel`（`:58`）
- `GeometricRange / GeometricAzEl / GeometricRADec / GeometricRangeRate` → `CoreMeasurement`（各 `.hpp:39~47`）。**注意**：`CoreMeasurement.hpp` 在本 depth-1 克隆中**不存在**（core 中仅残留注释掉的 `Factory.hpp:70,144` 前向声明），该插件默认 OFF，属未完成的遗留接口。
- `MediaCorrection` → `MediaCorrectionInterface`（`measurement/MediaCorrection.hpp:40`；接口见 `src/base/solarsys/MediaCorrectionInterface.hpp:38`）

**事件类**
- `ContactLocator / EclipseLocator / IntrusionLocator` → `EventLocator`（`src/base/event/EventLocator.hpp:64`）
- `ContactEvent / EclipseEvent / EclipseTotalEvent / IntrusionEvent / ContactResult / IntrusionResult` → `LocatedEvent`（`src/base/event/LocatedEvent.hpp:41`）
- EstimationPlugin 内的 `EventManager` → `TriggerManager`（`EventManager.hpp:43`）——对应 §2.2 中 `DynamicLibrary` 的可选 `GetTriggerManager` 通道。

**硬件/信号类**（EstimationPlugin）
- `Sensor` → `Imager`、`Antenna` → `Imager`（`hardware/Sensor.hpp:42`、`Antenna.hpp:33`）；`RFHardware` → `Sensor`（`:44`）；`Receiver / Transmitter / Transponder` → `RFHardware`；`Oscillator` → `Transmitter`（`Oscillator.hpp:39`）
- `SignalBase` → `GmatBase`（`signal/SignalBase.hpp:57`）；`PhysicalSignal` → `SignalBase`；`PassivePhysicalSignal` → `PhysicalSignal`；`SinglePointSignal` → `SignalBase`

**数据/接口/订阅类**
- `DataReader` → `GmatBase`（`DataReader.hpp:42`）；`FileReader` → `DataReader`（`:40`）
- `DataInterface` → `Interface`（`DataInterface.hpp:42`；`src/base/interface/Interface.hpp:36`）；`FileInterface` → `DataInterface`
- `DataCallback` → `Subscriber`（`DataCallback.hpp:40`；`src/base/subscriber/Subscriber.hpp:54`）

**命令/函数/力模型/编队类**
- `Set` → `GmatCommand`（`DataInterfacePlugin/.../Set.hpp:44`）；`RunEstimator` → `RunSolver`（`RunEstimator.hpp:51` → `PropagationEnabledCommand`，`src/base/command/PropagationEnabledCommand.hpp:59`）；`RunSmoother` → `RunEstimator`；`Global` → `ManageObject`（`Global.hpp:43`，`src/base/command/ManageObject.hpp:43`）；`CallGmatFunction` → `CallFunction`（`CallGmatFunction.hpp:37`，`src/base/command/CallFunction.hpp:44`）
- `ExternalModel` → `PhysicalModel`（`ExternalModel.hpp:38`，`src/base/forcemodel/PhysicalModel.hpp:143`）
- `Formation` → `FormationInterface`（`Formation.hpp:38`，`src/base/spacecraft/FormationInterface.hpp:40` → `SpaceObject`）
- `GmatFunction` → `UserDefinedFunction`（`GmatFunction.hpp:40`，`src/base/function/UserDefinedFunction.hpp:38` → `ObjectManagedFunction` → `Function`）
- `EstimationStateManager` → `StateManager`（`EstimationStateManager.hpp:50`，`src/base/foundation/StateManager.hpp:118`）

### 4.2 工厂方法模式：脚本类型名 → 对象实例

三处协作实现了"脚本写 `Create Spacecraft sat;` 就能 new 出对象"的机制：

1. 插件工厂在构造时把 `createList`（如 `{"SPK","Code500","STK","CCSDS"}`）交给 `Factory` 基类，`GetListOfCreatableObjects()`（`src/base/factory/Factory.hpp:167`）返回它；
2. `Factory::CreateObject(ofType, withName)` 依据 `ofType` 字符串分派到 `new`；
3. `FactoryManager`（单例，`src/base/factory/FactoryManager.hpp:84`）在 `RegisterFactory`（`.cpp:84`）时把工厂按 `GetFactoryType()` 归档，`CreateObject(generalType, ofType, withName)`（`.cpp:120`）先 `FindFactory` 再委托。

第 4 章详述了 Moderator/Interpreter/Sandbox 如何消费这套机制——[第4章](CH04-executive-factory.md)。

### 4.3 估计链路数据流（Estimation / EKF / Fmincon 共享）

```
观测文件(.tdm/.gmd/.trk)
   │  DataFile / TdmReadWriter / ObType 解析          (measurementfile/ tdmReader/)
   ▼
TrackingDataAdapter（单位换算：deg/km → 内部量纲）      (adapter/)
   │  MeasurementModelBase::Compute(计算值) / ComputeDerivative(偏导)
   ▼
MeasurementManager（按观测量组织测量模型）
   │
   ▼
Estimator（Solver 子类）─────────────────────┬──────────
   │ BatchEstimator: 批处理最小二乘           │ SeqEstimator→EKF: 顺序递推
   │  EstimationStateManager: 状态向量+协方差  │  过程噪声 ProcessNoise*
   │  （先验 apriori、正规方程、迭代收敛）      │  预测/更新 五方程
   ▼                                          ▼
FminconOptimizer（外部数值优化，目标/约束）
   ▼
ProgressReporter（报告）+ 协方差/残差输出
```

### 4.4 事件定位数据流

`EventLocator`（接触/地影/侵入）被注册为 `TriggerManager`（`Moderator::LoadAPlugin` 第 999~1017 行取 `GetTriggerManager`）。传播循环中，定位器对事件函数寻根，产出 `LocatedEvent`（含进入/退出时刻），供 Mission Control Sequence 在事件时刻插入动作。

### 4.5 生命周期与可逆性

所有插件对象都是 `GmatBase` 后代，遵循同一生命周期契约：工厂 `CreateObject` 构造 → 脚本 `SetField` 设参数（走 `GetParameterInfo` 的参数表）→ `Initialize()` 分配资源/构建状态 → `Execute()`/`Estimate()` 运行 → `Copy()/Clone()` 复制 → 由 Sandbox 持有并析构。插件本身无独立生命周期：其共享库仅在 `Moderator::LoadAPlugin` 时 `dlopen` 并常驻进程，工厂对象由 `FactoryManager` 持有直到进程退出。

## 五、文件清单附录

本章 13 个插件共 375 个 C/C++ 代码文件（`.hpp/.cpp/.c/.h`）。**每个插件小节末尾的 `#### 文件清单附录` 表已逐文件列出 `相对路径 | 职责 | 关键类/函数`**，合计覆盖本章全部代码文件；下表为按插件的索引（文件数均已 glob 计数验证）：

| 小节 | 插件 | 代码文件数 | 主要导出类 | 扩展点（core base） |
|---|---|---|---|---|
| 13.1 | 根目录共享文件 | 0（2 个 CMake 文件） | `_SETUPPLUGIN` 宏 | CMake 构建层 |
| 13.2 | CInterfacePlugin | 11 | `CInterfaceFunctions`（C ABI）、`PrepareMissionSequence`、`CCommandFactory` | `GmatCommand` |
| 13.3 | DataCallbackPlugin | 7 | `DataCallback` | `Subscriber` |
| 13.4 | DataInterfacePlugin | 23 | `DataReader`/`FileReader`、`DataInterface`/`FileInterface`、`Set` | `GmatBase`/`Interface`/`GmatCommand` |
| 13.5 | EphemPropagatorPlugin | 15 | `EphemerisPropagator`、`SPK/Code500/StkE/CcsdsEphPropagator` | `Propagator` |
| 13.6 | EstimationPlugin | 198 | `BatchEstimator`、`Estimator`、`MeasurementModelBase`、`TrackingDataAdapter`、`RFHardware`、`SignalBase`、`DataFile`、`ObType` 等 | `Solver`/`GmatBase`/`StateManager`/`TriggerManager`/`MediaCorrectionInterface` |
| 13.7 | EventLocatorPlugin | 23 | `ContactLocator`/`EclipseLocator`/`IntrusionLocator`、`*Event`/`*Result` | `EventLocator`/`LocatedEvent` |
| 13.8 | ExtendedKalmanFilterPlugin | 43 | `ExtendedKalmanFilter`、`SeqEstimator`、`Smoother`、`ProcessNoise*`、`EstimatedParameter*` | `Estimator`(→`Solver`) |
| 13.9 | ExternalForceModelPlugin | 7 | `ExternalModel` | `PhysicalModel` |
| 13.10 | ExtraPropagatorsPlugin | 7 | `BulirschStoer` | `Integrator`(→`Propagator`) |
| 13.11 | FminconOptimizerPlugin | 7 | `FminconOptimizer` | `ExternalOptimizer`(→`Optimizer`→`Solver`) |
| 13.12 | FormationPlugin | 7 | `Formation` | `FormationInterface`(→`SpaceObject`) |
| 13.13 | GeometricMeasurementPlugin | 13 | `GeometricRange`/`GeometricRangeRate`/`GeometricAzEl`/`GeometricRADec` | `CoreMeasurement`（头文件缺失，见 §4.1） |
| 13.14 | GmatFunctionPlugin | 14 | `GmatFunction`、`CallGmatFunction`、`Global` | `UserDefinedFunction`/`CallFunction`/`ManageObject` |

> 说明：根目录无 `README.md`（glob 已核实）；插件清单与新增插件步骤写在 `plugins/CMakeLists.txt` 注释中。各插件非代码文件（`.m/.script/.i/.swg/Doxyfile/.gitignore/CMakeLists.txt`）已在对应小节的附录表中另行说明。


