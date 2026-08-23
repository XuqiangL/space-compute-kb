# 第14章 插件体系（下）：接口、重力、TLE 与工具类插件

> 本章范围：`L:\gmat888\plugins\` 目录下 13 个插件目录的全部文件——`MatlabInterfacePlugin`、`Msise00Plugin`、`NewParameterPlugin`、`OVtoOFI`、`PolyhedronGravityPlugin`、`ProductionPropagatorPlugin`、`PythonInterfacePlugin`、`SaveCommandPlugin`、`ScriptToolsPlugin`、`StationPlugin`、`ThrustFilePlugin`、`TLEPropagatorPlugin`、`YukonOptimizerPlugin`。共约 220 个 C/C++ 代码文件（`.hpp/.cpp/.c/.h/.f/.for`），另有 `.i/.swg/CMakeLists.txt/.gitignore/.script/.rst` 等非代码文件。本章是 [第13章](CH13-plugins-a.md)（接口/测量/估计/传播类 13 个插件）的姊妹篇；插件机制的宿主侧（运行时加载、`Factory` 注册、`GmatPluginFunctions` 三入口）见 [第4章](CH04-executive-factory.md) 与 [第13章](CH13-plugins-a.md) 的通用架构一节，本章不再重复其原理，只讲各插件自身的类。

## 一、本章目录树

```text
plugins/
├── PythonInterfacePlugin/src/base/        # 11 代码：跨语言桥接（Python C-API）
│   ├── command/CallPythonFunction.{hpp,cpp}
│   ├── factory/PythonCommandFactory.{hpp,cpp}
│   ├── function/PythonModule.{hpp,cpp}    # 两个空文件（占位）
│   ├── include/pythoninterface_defs.hpp
│   ├── interface/PythonInterface.{hpp,cpp}
│   └── plugin/GmatPluginFunctions.{hpp,cpp}
├── MatlabInterfacePlugin/                 # 37 代码：跨语言桥接（MATLAB Engine API + .mat 写出）
│   ├── src/base/command/CallMatlabFunction.{hpp,cpp}
│   ├── src/base/factory/  CallMatlabFunctionFactory / MatlabFunctionFactory /
│   │                     MatlabInterfaceFactory / MatlabWorkspaceFactory（各 .hpp/.cpp）
│   ├── src/base/function/MatlabFunction.{hpp,cpp}
│   ├── src/base/include/matlabinterface_defs.hpp
│   ├── src/base/interface/MatlabInterface.{hpp,cpp}
│   ├── src/base/matwriter/  MatData / MatWriter / MatWriterMaker / RealMatData /
│   │                       StringMatData（各 .hpp/.cpp）
│   ├── src/base/plugin/GmatPluginFunctions.{hpp,cpp}
│   ├── src/base/subscriber/MatlabWorkspace.{hpp,cpp}
│   └── src/matlab/gmat_mex/  mex-file/SendGMAT.cpp  src/ipcsetup.h  src/MatlabClient.{hpp,cpp}
│                            src/MatlabConnection.{hpp,cpp}  test/TestDriver.cpp
├── PolyhedronGravityPlugin/src/base/      # 17 代码：多面体重力
│   ├── factory/  GravityParameterFactory / PolyhedronGravityModelFactory（各 .hpp/.cpp）
│   ├── gravitymodel/  PolyhedronBody / PolyhedronGravityModel（各 .hpp/.cpp）
│   ├── include/polyhedrongravitymodel_defs.hpp
│   ├── parameter/  GravData / GravReal / SurfaceHeight（各 .hpp/.cpp）
│   └── plugin/GmatPluginFunctions.{hpp,cpp}
├── TLEPropagatorPlugin/                   # ~23 代码：两行根数传播（SPICE spke10）
│   ├── src/factory/TlePropFactory.{hpp,cpp}
│   ├── src/include/tleprop_defs.hpp
│   ├── src/plugin/GmatPluginFunctions.{hpp,cpp}
│   ├── src/propagator/  SGP4Propagator / SPICEPropagator / TLEData / TLEReader（各 .hpp/.cpp）
│   ├── ValladoCode/SGP4/SGP4/SGP4.{cpp,h}        # Vallado 参考 SGP4（2016-03-09）
│   ├── ValladoCode/SGP4DC/SGP4DC/SGP4DC.{cpp,h}  # 深空 SDP4 变体
│   ├── ValladoCode/TestSGP4/  TestSGP4mod.cpp  TestSGP4/TestSGP4.cpp  TestSGP4/stdafx.{cpp,h}
│   │                        TestSGP4/targetver.h
│   ├── TLE/Active_Nov-09-2019.txt                # 示例 TLE 数据
│   ├── samples/NeedTlePropagator/*.script/.py    # 6 个示例脚本
│   └── doc/source/*.rst  test/TLE/*.txt  test/truth/*.truth  …（数据/文档）
├── Msise00Plugin/src/base/                # 12 代码：NRLMSISE-00 大气
│   ├── atmosphere/  NRLMsise00Atmosphere.{hpp,cpp}  nrlmsise00_sub.{c,h,f,for,_v2.for}
│   ├── factory/NRLMsise00Factory.{hpp,cpp}
│   ├── include/nrlmsise00_defs.hpp
│   └── plugin/GmatPluginFunctions.{hpp,cpp}
├── ProductionPropagatorPlugin/src/base/   # 7 代码：Prince-Dormand 853 积分器
│   ├── factory/ProductionPropagatorFactory.{hpp,cpp}
│   ├── include/ProductionPropagatorDefs.hpp
│   ├── plugin/GmatPluginFunctions.{hpp,cpp}
│   └── propagator/PrinceDormand853.{hpp,cpp}
├── StationPlugin/                         # 11 代码 + SWIG 绑定
│   ├── src/base/factory/StationFactory.{hpp,cpp}
│   ├── src/base/include/StationDefs.hpp
│   ├── src/base/plugin/GmatPluginFunctions.{hpp,cpp}
│   ├── src/base/station/GroundStation.{hpp,cpp}
│   └── swig/  station.i  station.swg  station_py.i  StationAPI.hpp
├── ThrustFilePlugin/src/base/             # 31 代码：推力历史文件（THF）
│   ├── command/  BeginFileThrust / EndFileThrust（各 .hpp/.cpp）
│   ├── datareader/  ThfDataSegment / ThrustHistoryFile / ThrustSegment（各 .hpp/.cpp）
│   ├── factory/  ThrustFileCommandFactory / ThrustFileForceFactory /
│   │             ThrustFileReaderFactory / ThrustSegmentParameterFactory（各 .hpp/.cpp）
│   ├── forcemodel/FileThrust.{hpp,cpp}
│   ├── include/ThrustFileDefs.hpp
│   ├── parameter/  ThrustSegmentData / ThrustSegmentParameters / ThrustSegmentReal /
│   │               ThrustSegmentRvector（各 .hpp/.cpp）
│   └── plugin/GmatPluginFunctions.{hpp,cpp}
├── SaveCommandPlugin/src/base/            # 7 代码
│   ├── command/Save.{hpp,cpp}  factory/SaveCommandFactory.{hpp,cpp}
│   ├── include/SaveCommandDefs.hpp  plugin/GmatPluginFunctions.{hpp,cpp}
├── ScriptToolsPlugin/src/base/            # 7 代码
│   ├── command/CommandEcho.{hpp,cpp}  factory/CommandEchoFactory.{hpp,cpp}
│   ├── include/ScriptToolsDefs.hpp  plugin/GmatPluginFunctions.{hpp,cpp}
├── NewParameterPlugin/src/base/           # 29 代码：力模型/求解器参数
│   ├── factory/NewParameterFactory.{hpp,cpp}
│   ├── include/newparameter_defs.hpp
│   ├── parameter/  AtmosDensity / FMAcceleration / FMDensity / OdeData / OdeReal /
│   │               OdeRvec3 / SolverData / SolverReal / SolverState / SolverStatus /
│   │               SolverString / Torque（各 .hpp/.cpp）
│   └── plugin/GmatPluginFunctions.{hpp,cpp}
├── OVtoOFI/src/base/                      # 9 代码：OrbitView → OpenFramesInterface 映射
│   ├── factory/  InvisOpenFramesViewFactory / OVtoOFIFactory（各 .hpp/.cpp）
│   ├── include/OVtoOFI_defs.hpp
│   ├── plugin/GmatPluginFunctions.{hpp,cpp}
│   └── subscriber/OVtoOFI.{hpp,cpp}
└── YukonOptimizerPlugin/src/base/         # 19 代码：SQP 优化器
    ├── factory/YukonOptimizerFactory.{hpp,cpp}
    ├── include/yukon_defs.hpp
    ├── plugin/GmatPluginFunctions.{hpp,cpp}
    └── solver/  GmatProblemInterface / MinQP / NLPFunctionGenerator / Yukon / Yukonad /
                 YukonOptions.hpp / YukonOutput.hpp / YukonUserProblem（各 .hpp/.cpp）
```

## 二、逐文件/逐类讲解

### 14.1 PythonInterfacePlugin：基于 Python C-API 的跨语言桥接

Python 接口插件把 GMAT 脚本里的 `CallPythonFunction` 命令桥接到 Python 解释器。桥的核心是 `PythonInterface` 单例（包装 CPython C-API），命令层 `CallPythonFunction` 负责 GMAT 参数 ↔ `PyObject` 的双向转换。

#### 14.1.1 `src/base/include/pythoninterface_defs.hpp`

职责：定义 `PYTHON_API` 导入/导出宏（`__declspec(dllexport/dllimport)`，由 `PYTHON_EXPORTS` 开关控制），其余平台留空。这是所有插件共用的 `*_defs.hpp` 模板（与 [第13章](CH13-plugins-a.md) 所述一致），本章后续各插件的 defs 文件均同此模式，不再逐一展开。

#### 14.1.2 `src/base/interface/PythonInterface.hpp` / `.cpp`

职责：Python 解释器的单例门面。类声明于 `PythonInterface.hpp:43`，`class PythonInterface : public Interface`，关键公有接口（`:46-61`）：

```cpp
static PythonInterface* PyInstance();                                   // :46
bool                    PyInitialize();                                 // :47
bool                    PyFinalize();                                   // :48
void                    PyAddModulePath(const StringArray& path);       // :49
PyObject*               PyFunctionWrapper(const std::string &modName,   // :50
                                          const std::string &funcName,
                                          const std::vector<PyObject *> &argIn);
PyObject*               PyExternalFunctionWrapper(const std::string &modName,  // :54
                                                  const std::string &funcName,
                                                  Real *state, Real dt,
                                                  StringArray stateDescription,
                                                  Integer order, Integer dimension,
                                                  UnsignedInt argSz);
```

要点解读：

- **单例**：`PyInstance()`（`PythonInterface.cpp:55`）懒创建唯一实例，构造时 `isPythonInitialized=false`、`numPyCommands=0`、`plF=";"`（`:71-78`）。`Clone`/`Copy` 直接抛 `InterfaceException`（`:107-130`），因为单例不可复制——与 [第13章](CH13-plugins-a.md) 里 `MatlabInterface` 的单例设计呼应。
- **初始化**：`PyInitialize()`（`:144`）只初始化一次，`Py_Initialize()` 失败时检查 `PyErr_Occurred()` 抛 `InterfaceException`；成功则 `numPyCommands++`。`PyFinalize()`（`:252`）用引用计数 `--numPyCommands == 0` 才真正关闭（当前代码里 `Py_Finalize()` 被注释，属已知遗留）。
- **路径注入**：`PyAddModulePath()`（`:315`）逐条执行 `import sys` 与 `sys.path.append("...")`，并把 Windows 反斜杠统一替换为 `/`。
- **函数调用包装**：`PyFunctionWrapper()`（`:364`）是核心：`PyUnicode_FromString`（Py3）→ `PyImport_Import` 导入模块 → 用 `StringIO` 重定向 `sys.stdout`（`:409-416`）→ `PyObject_GetAttrString` 取函数 → `PyTuple_SetItem` 组装参数 → `PyObject_CallObject` 调用 → 捕获 `stdout` 转成 `MessageInterface::ShowMessage` 输出 → 返回 `pyFunc`。所有失败路径走 `PyErrorMsg()`（`:643`，用 `PyErr_Fetch/PyErr_Restore` 取异常文本）。
- **外部函数包装**：`PyExternalFunctionWrapper()`（`:502`）用于把状态向量 `state[dimension]`、时间 `dt`、状态描述 `stateDescription`、阶数 `order` 打包成 Python 列表/浮点元组再调用——这是给 Python 力模型（外部导数）预留的通道，参数布局与 [第6章](CH06-dynamics.md) 的 `PhysicalModel` 接口对齐。
- **模块路径反查**：`PyExternalGetPythonPath()`（`:691`）读模块 `__file__` 属性返回全路径。

#### 14.1.3 `src/base/command/CallPythonFunction.hpp` / `.cpp`

职责：`CallPythonFunction` 命令，继承 `CallFunction`（见 [第5章](CH05-command.md)），把脚本里的输入输出参数映射成 Python 调用。

`CallPythonFunction.hpp:42` 声明类；`PyIfVariant`（`:94`）是桥接的数据变体：

```cpp
typedef std::variant<std::monostate, Real, std::string, Rmatrix> PyIfVariant;  // :94
```

即每个参数只能是"空/实数/字符串/矩阵"之一；`dataInput`/`dataReturn`（`:104-105`）分别缓存输入输出。参数表只有两个字符串字段 `MODULENAME`/`FUNCTIONNAME`（`:116-121`）。

`Execute()`（`CallPythonFunction.cpp:476`）的流程：

```cpp
SendInParam();                                             // 收集输入
for (UnsignedInt i = 0; i < dataInput.size(); ++i)
   argIn.push_back(ConvertToPyObject(dataInput.at(i)));    // GMAT → PyObject
pyRet = pythonIf->PyFunctionWrapper(moduleName, functionName, argIn);  // :495
// 返回值解析（:531-574）：tuple → 逐元素 ConvertFromPyObject；
// memoryview → 忽略；单个值 → 转换
dataReturn.clear();
if (pyRet) {
   if (PyTuple_Check(pyRet)) { /* 逐成员转存 */ }
   else { PyIfVariant curOutput = ConvertFromPyObject(pyRet); /* 非空则收下 */ }
   GetOutParams();                                          // PyObject → GMAT 参数
}
```

要点解读：

- 类型映射规则写在注释里（`:508-530`）：Python float/int → GMAT Variable；str → GMAT string；list → Array；tuple → 一维数组，tuple of tuple → 二维数组。`ConvertToPyObject`（`:773`）与 `ConvertFromPyObject`（`:603`）实现两个方向。
- `Initialize()`（`:399`）解析 `ModuleName`/`FunctionName` 并创建 `PythonInterface::PyInstance()`；`RunComplete()`（`:888`）在命令链结束时调用 `PyFinalize()` 释放解释器。
- `GetOutParams()`（`:1127`）把 `dataReturn` 写回输出参数对象（`Variable`/`Array`/`StringVar`），并对数组做维度校验。

#### 14.1.4 `src/base/factory/PythonCommandFactory.hpp` / `.cpp`

职责：`Gmat::COMMAND` 型工厂，`CreateCommand()`（`.cpp:125`）对 `"CallPythonFunction"` 返回 `new CallPythonFunction()`；`creatables` 只含该命令名（`:47`）。

#### 14.1.5 `src/base/function/PythonModule.hpp` / `.cpp`

职责：**两个空文件**（0 行），是遗留占位——Python 模块的管理实际由 `PythonInterface` 承担。讲解意义在于说明：插件开发中常留空壳避免破坏构建目录结构。

#### 14.1.6 `src/base/plugin/GmatPluginFunctions.cpp` / `.hpp`

职责：插件入口，`GetFactoryCount()` 返回 1，`GetFactoryPointer(0)` 返回 `new PythonCommandFactory`（`:74-76`），`SetMessageReceiver` 转发到 `MessageInterface`。模板与 [第13章](CH13-plugins-a.md) §2.2 完全一致。

### 14.2 MatlabInterfacePlugin：MATLAB Engine 桥接与 .mat 写出

Matlab 插件是 GMAT 历史最悠久的接口插件，提供三条能力线：(1) `MatlabInterface` 单例封装 MATLAB Engine C-API；(2) `CallMatlabFunction`/`MatlabFunction` 让脚本调用 `.m` 函数；(3) `MatWriter`/`MatData` 家族把数据写成 `.mat` 文件（`DataWriter` 体系）；另有 `gmat_mex` 子目录是 MATLAB 侧反向连 GMAT 的 MEX 客户端（wxIPC）。

#### 14.2.1 `src/base/interface/MatlabInterface.hpp` / `.cpp`

职责：MATLAB Engine 门面（单例），被命令、订阅者、GUI 共用。

`MatlabInterface.hpp:50` 声明 `class MatlabInterface : public Interface`，运行模式枚举（`:56-61`，与 `GmatGlobal` 的枚举值一致）：

```cpp
enum MatlabMode
{
   SINGLE_USE = 30,
   SHARED,                 // = 31
   NO_MATLAB,              // = 32：MATLAB 未安装
};
```

核心数据成员：`Engine *enginePtr`、`std::map<std::string, Engine*> matlabEngineMap`（单用模式下按名字管理多个引擎）、`outBuffer[8193]`（`MAX_OUT_SIZE=8192`，`MatlabInterface.cpp:65`）、`accessCount`、`matlabMode`。

逐方法解读（`MatlabInterface.cpp`）：

- `Instance()`（`:91`）懒创建单例；构造（`:753`）默认 `matlabMode = SHARED`，分配输出缓冲。
- `Open()`（`:110`）/`Close()`（`:153`）按模式分派：`SINGLE_USE → OpenSingleEngine/CloseSingleEngine`，`SHARED → OpenSharedEngine/CloseSharedEngine`，Mac 上走 `OpenEngineOnMac`（用 `engOpen("matlab -nosplash -nodesktop")`，`:810`）。
- `PutRealArray()`（`:221`）是"GMAT 行主序 → MATLAB 列主序"的关键转换：构造 `Rmatrix rowMajorMat` 后 `Transpose()` 得列主序，再 `mxCreateDoubleMatrix` + `memcpy` + `engPutVariable`。注释明说"Since MATLAB stores array in column major order, it needs to take transpose"（`:237`）。
- `GetRealArray()`（`:305`）用 `engGetVariable` 取回，`mxIsDouble` 时 `memcpy` 输出，`numRowsReceived/numColsReceived` 由 `mxGetM/mxGetN` 回填；空指针抛 `InterfaceException`（`:352`）；逻辑标量（Bug 2376 修复，`:368-388`）转 1.0/0.0。
- `GetString()`（`:414`）`mxIsChar` 判断后 `mxGetString` 到 `outBuffer`。
- `EvalString()`（`:485`）薄封装 `engEvalString`（0 成功）。
- `RunMatlabString()`（`:602`）是错误处理增强版：先 `IsOpen()` 检查、自动 `Open()`；把 `cd xxx` 转成函数式 `cd('xxx')`（Bug 2032 修复，`:624-634`）；再把求值串包进 `try/catch` + `beep off`，若 MATLAB 报错则从 `errormsg` 变量取回文本抛 `InterfaceException`（`:644-677`）。
- 单用模式：`OpenSingleEngine()`（`:1096`）用 `engOpenSingleUse(NULL,NULL,&retval)`，按名字存 `matlabEngineMap`，自动命名 `matlabEngine_N`；`CloseSingleEngine()`（`:1198`）支持按名字关或全关。
- 参数访问：只有 `MATLAB_MODE` 一个可写参数（`PARAMETER_TEXT` 定义于 `:67-77`），`GetParameterID`（`:1279`）、`Get/SetIntegerParameter`（`:1312`/`:1331`）标准实现，`IsParameterReadOnly` 恒真（`:1298`）。

#### 14.2.2 `src/base/command/CallMatlabFunction.hpp` / `.cpp`

职责：命令 `CallMatlabFunction : public CallFunction`（`.hpp:38`），脚本里调用 `.m` 函数。

`Initialize()`（`.cpp:218`）：先检查 `GmatGlobal::Instance()->IsMatlabAvailable()`（未装 MATLAB 直接抛错，`:228-231`）；开引擎 `matlabIf->Open("GmatMatlab")`；把 `FileManager` 收集的所有 MATLAB 路径用 `path('...', path)` 逆序压栈（`:278-294`）；按名字解析输入/输出 `Parameter` 填入 `mInputList/mOutputList`。

`FormEvalString()`（`:125`）按输出个数组装 MATLAB 左值：`[Out1, Out2] = FuncName(In1, In2);`。`ExecuteMatlabFunction()`（`:451`）依次：`format long`、`clear errormsg`、压函数路径、`SendInParam` 逐个送输入、`FormEvalString`+`EvalMatlabString`、`GetOutParams` 取回输出。

`SendInParam()`（`:536`）按参数类型分派：`Array` 走 `PutRealArray`（`__USE_EVAL_STRING__` 未定义时的默认路径，`:635`）；`Variable` 用 `EvalString` 写 `name = value;`（精度 18 位，`:646-657`）；`String` 写 `name = '...';`；其他 Parameter 先 `EvaluateReal/EvaluateString` 再转字符串，非 REAL/STRING 类型直接拒绝（GMT-3526，`:710-728`）。

#### 14.2.3 `src/base/function/MatlabFunction.hpp` / `.cpp`

职责：`MatlabFunction : public Function`（`.hpp:39`），表示一个 `.m` 文件函数对象。

构造（`.cpp:56`）从 `FileManager::GetMatlabFunctionPath(name)` 取函数目录，失败则退回 `FUNCTION_PATH`；`SetMatlabFunctionPath()`（`:238`）处理相对路径（以 `.` 开头）时先相对 GMAT 工作目录解析，再退回 bin 目录，并把目录注册进 `FileManager::AddMatlabFunctionPath`（`:313`）供嵌套函数查找；`functionName = GmatFileUtil::ParseFileName(functionPath)`（`:316`）去路径取函数名。`FUNCTION_NAME` 的 `SetStringParameter` 是空操作回填（`:209-214`）。

#### 14.2.4 `src/base/subscriber/MatlabWorkspace.hpp` / `.cpp`

职责：`MatlabWorkspace : public Subscriber`（`.hpp:41`），订阅者——把参数按更新频率推送到 MATLAB 工作区（GUI 数据可视化用；`__INCLUDE_MATLAB_WORKSPACE__` 未定义时该工厂不注册，见 14.2.7）。

成员（`.hpp:98-107`）：`mUpdateFrequency`、`mNumParams`、`mDataCount`、`mSendCount`、`mParams`、`mParamNames`、`matlabIf`。参数表 `ADD`/`UPDATE_FREQUENCY`（`:115-120`）。

`Distribute(const Real *dat, Integer len)`（`.cpp:575`）：按 `mDataCount % mUpdateFrequency` 节流；每个参数 `Evaluate()` 后组装 MATLAB 赋值串——`Array` 用 `name(N,:) = [...]` 累积成行（`:621-629`），普通量用 `name(N) = value`，最后 `matlabIf->RunMatlabString(matlabStr)`（`:638`）。空实现 `Distribute(int)`（`:566`）恒 false。

#### 14.2.5 `src/base/matwriter/`：.mat 文件写出体系

这组类实现 GMAT `DataWriter` 接口（见 [第2章](CH02-foundation.md) 的 WriterData/DataWriter），把数据写为 MATLAB v6 `.mat`：

- **`MatData.hpp`**：`MatData : public WriterData`（`:49`），抽象基类，纯虚 `WriteData(MATFile*, obj_name, mxArray* mat_struct, mwIndex)`（`:57`）；保护成员缓存 `pmat/obj_name/mat_struct`。
- **`RealMatData.hpp`**：实数容器（`:45`），`AddData(const Matrix&)` 累积 `realData`/`realData3D`；`WriteData` 用 `mxCreateDoubleMatrix` 构造数组。
- **`StringMatData.hpp`**：字符串容器（`:45`），`AddData(const StringMatrix&)`，内部 `mxArray *pa_string`。
- **`MatWriter.hpp` / `.cpp`**：`MatWriter : public DataWriter`（`.hpp:49`），`GetContainer()`（`.cpp:126`）按类型返回 `RealMatData`/`StringMatData`；`Initialize()`（`:160`）→ `OpenFile()`（`:184`，`matOpen(filename, format)`，格式默认 `"w6"`，非法格式回退）；`DescribeData()`（`:272`）→ `SetMxArray()`（`:289`，`mxCreateStructMatrix` 建结构数组 `mat_struct.variable`）；`WriteData()`（`:223`）遍历 `allData` 调各容器 `WriteData`；`CloseFile()`（`:248`）`matClose`；`ClearData()`（`:330`）清空并 `UnsetMxArray()`。
- **`MatWriterMaker.hpp` / `.cpp`**：`DataWriterMaker` 单例（`.cpp:47`），`CreateDataWriter()` 返回 `new MatWriter`，`GetType()` 返回 `"MatWriter"`。注意它**不是** `Factory` 派生（DataWriter 不可脚本化），而是注册进 `DataWriterInterface`。

#### 14.2.6 `src/matlab/gmat_mex/`：MATLAB 侧 MEX 客户端

方向相反的另一半桥接：让 MATLAB 主动向 GMAT 发命令。基于 wxWidgets IPC（DDE 之外，`ipcsetup.h:37-43` 定义 `IPC_SERVICE="4242"`、`IPC_HOST="localhost"`、`IPC_TOPIC="GMAT-MATLAB"`）：

- **`mex-file/SendGMAT.cpp`**：MEX 入口 `mexFunction`（`:164`）解析两个字符串参数（动作 + 数据），转发给 `SendGMAT()`（`:44`）。动作协议：`"Poke"`+`"Open;"` 建连接并 `mexLock()`；`"Advise"` 订阅；`"Poke"` 推送；`"Request"` 请求返回数据；`"Execute"` 执行；`"Poke"`+`"Close;"` 解锁断开（`:56-140`）。
- **`src/MatlabClient.hpp` / `.cpp`**：`MatlabClient : public wxClient`（`.hpp:39`），`Connect()`/`Disconnect()`/`OnMakeConnection()` 管理 `MatlabConnection* m_connection`。
- **`src/MatlabConnection.hpp` / `.cpp`**：`MatlabConnection : public wxConnection`（`.hpp:42`），重写 `Execute/Request/Poke/OnAdvise/OnDisconnect` 实现 GMAT↔MATLAB 消息语义。
- **`test/TestDriver.cpp`**：独立测试驱动，验证 IPC 往返。

#### 14.2.7 `src/base/factory/` 四个工厂与 `src/base/plugin/GmatPluginFunctions.cpp`

四个工厂均标准 `Factory` 派生：`MatlabInterfaceFactory`（creatable `"MatlabInterface"`，`CreateInterface` 返回 `MatlabInterface::Instance()` 单例，`.cpp:70-71`）、`CallMatlabFunctionFactory`（`"CallMatlabFunction"`）、`MatlabFunctionFactory`（`"MatlabFunction"`）、`MatlabWorkspaceFactory`（`"MatlabWorkspace"`）。

`GmatPluginFunctions.cpp` 的 `GetFactoryCount()`（`:58-69`）在注册 `MatWriter` 时先 `DataWriterInterface::Instance()->RegisterWriterMaker(MatWriterMaker::Instance())`（`:61`），返回 3 或 4 个工厂（`__INCLUDE_MATLAB_WORKSPACE__` 决定是否含 `MatlabWorkspaceFactory`）；`GetFactoryPointer` 按索引 `new` 出对应工厂（`:82-111`）。

### 14.3 PolyhedronGravityPlugin：多面体重力场

对不规则小天体（小行星/彗核），用三角面片多面体模型（Werner-Scheeres 法）计算引力位、加速度、立体角与地表高度。核心是 `PolyhedronGravityModel : public GravityBase`（见 [第6章](CH06-dynamics.md) 的 GravityBase）与几何数据类 `PolyhedronBody`。

#### 14.3.1 `src/base/gravitymodel/PolyhedronBody.hpp` / `.cpp`

职责：多面体几何数据容器与预处理（加载、面法向、内心、边邻接）。非 `GmatBase` 派生，是纯数据+算法类。

`.hpp:30-41` 定义别名与结构：

```cpp
struct Edge { Integer vertex1, vertex2; };                 // :30
typedef std::vector<Integer>       PolygonFace;            // 三角形三个顶点下标
typedef std::vector<Rvector3>      PointsList;             // 顶点表
typedef std::vector<PolygonFace>   FacesList;              // 面表
typedef std::vector<Edge>          EdgesList;
typedef std::map<Integer, Edge>    EdgesMap;
```

类成员（`:43-86`）：`verticesList`、`facesList`、`fn`（面法向）、`ic`（面内心）、`E`（边表）、`attachmentA/attachmentB`（边两侧邻接面）、`edgeMap`、`attachmentAMap/BMap`（哈希加速）。

- `LoadBodyShape()`（`.cpp:141`）：读文本文件——首行顶点数，随后每行 `index x y z`（km）；再读面数，每行 `index ix iy iz`；**下标从 1 转为 0 基**（`:278-280`，注释："GMAT index starts from 0; MatLab index starts from 1"）。数据缺失抛 `UtilityException`。
- `Incenters()`（`.cpp:319`）：逐三角面计算内心。
- `FaceNormals()`：用右手定则算单位外法向（数据文件须保证顶点环绕序）。
- `Edges()` / `EdgeAttachments(i, faceA, faceB)`：由面构造唯一边集，并记录每条边两侧邻接面，供引力求和用。
- `Clone()/Copy()`（`:122-131`）供拷贝。

#### 14.3.2 `src/base/gravitymodel/PolyhedronGravityModel.hpp` / `.cpp`

职责：把多面体引力接入 `GravityBase` 力模型链。

参数表（`.hpp:105-116`）：`CREATE_FORCE_BODY`（引力体名）、`SHAPE_FILENAME`（形状文件）、`BODY_DENSITY`（kg/m³）。成员：`polybody`、`bodyDensity`、`bodyShapeFilename`、`bodyOrientation/bodyState`、`sumWf`（立体角累计，用于"在体内/体外"判定）、`isPHGMInitialized/isShapeLoaded`。

核心算法 `Calculation(Rvector6 x, Rvector6& xdot, Rmatrix66& A)`（`.cpp:424`）：

- 首次调用时预计算 `FaceNormals()/Incenters()/Edges()`（`:446-453`，`firstcalculation` 置位）。
- `CalculateTransformationMatrix()`（`:353`）返回 `[D, Ddot]`：从惯性系（MJ2000Eq）到 BodyFixed 的旋转与旋转率（另有 `_UsingIAUSimplified` 简化版 `:301`，默认走完整版）。`r = D*r; v1 = Ddot*r + D*v`（`:463-464`）把状态转进体固系。
- **边贡献**：对每条边 `i`，取顶点 `P1/P2`、单位方向 `n12`，由 `EdgeAttachments` 取两侧面法向 `na/nb`，用叉积构造面内边法向 `na12 = n12 × na`、`nb21 = n21 × nb`（`:513-518`），再以"面内心指向顶点"的判据修正指向（`:534-541`），最后组装 3×3 边矩阵 `Ee = na*na12ᵀ + nb*nb21ᵀ`（`:548-550`）。
- **面贡献**：对每个面用立体角公式累加 `sumWf`（Werner-Scheeres 的 `w_f` 项），同时累加 `sumEdge`（边）、`sumFace`（面）向量与矩阵，合成引力加速度 `xdot[3..5]` 和状态转移矩阵 `A`。
- **内/外判定**：`sumWf` 在体内时达到 `4π`（相对场点），后续 `GetSolidAngle`（`:1085`）直接复算 `sumWf`：

```cpp
for (Integer i = polybody->facesList.size()-1; i >= 0; --i)
{
   n = polybody->fn[i];
   A = polybody->verticesList[face[0]]; B = ...; C = ...;
   R1 = A-r; R2 = B-r; R3 = C-r;
   r1 = R1.Norm(); r2 = R2.Norm(); r3 = R3.Norm();
   cR23.Set(-R2(2)*R3(1) + R2(1)*R3(2), ...);          // R2×R3
   sumWf = sumWf + 2*atan2(R1*cR23,
         (r1*r2*r3 + r1*R2*R3 + r2*R3*R1 + r3*R1*R2)); // :1146-1147
}
```

这是标准的多面体立体角公式（`2·atan2( r1·(r2×r3), 分母 )` 对每个三角面求和）。

- `GetAltitude(r, time)`（`:1169`）：场点到最近面的有向距离，供 `SurfaceHeight` 参数做"触地/停止"判定。
- `GetDerivatives()`（`:931`）、`SupportsDerivative`（`:1057`）、`SetStart`（`:1018`）实现 `PhysicalModel` 协议；`SetDensity/GetDensity/SetBodyShapeFileName/GetBodyShapeFileName`（`:270-299`）是脚本参数存取；`HasLocalClones()=true`、`IsUserForce()=true`（`:251-256`）。

#### 14.3.3 `src/base/parameter/` GravData / GravReal / SurfaceHeight

- **`GravData.hpp`**：`GravData : public RefData`（`:45`），数据访问层。内部 `enum ModelType {POINT_MASS, HARMONIC, POLYHEDRAL, UNDEFINED}`（`:64-70`），`InitializeRefObjects()` 解析 Spacecraft/SolarSystem/ODEModel，并从力模型里找出中心体引力 `cbForce` 与 `body`、`bodyRadius`。
- **`GravReal.hpp`**：`GravReal : public RealVar, public GravData`，把 `GetGravReal("...")` 接到参数取值。
- **`SurfaceHeight.hpp` / `.cpp`**：`SurfaceHeight : public GravReal`（`.hpp:39`），`Evaluate()` 调 `PolyhedronGravityModel::GetAltitude`，用于任务里"中心体表面高度"监控/停止。

#### 14.3.4 工厂与入口

- `PolyhedronGravityModelFactory`（`Gmat::PHYSICAL_MODEL`）：`CreatePhysicalModel` 对 `"PolyhedronGravityModel"` 返回实例（`.cpp:68-69`）。
- `GravityParameterFactory`（`Gmat::PARAMETER`）：creatable `"SurfaceHeight"`（`.cpp:47`）；`GetListOfCreatableObjects`（`:137`）用"构造即注册"技巧把参数注册进 `ParameterInfo`（与 14.11 的 NewParameterFactory 同法）。
- `GmatPluginFunctions.cpp`：2 个工厂（`:51-86`）。

### 14.4 TLEPropagatorPlugin：两行根数（TLE）传播

把北美防空司令部（NORAD）两行根数文件转成航天器星历。实际传播不重新实现 SGP4，而是调用 **SPICE 库的 `spke10`**（SPICE v66 的 TLE 传播器，内部即 Vallado 2006 版 SGP4），仓库里同时携带 Vallado 参考 C++ 代码 `ValladoCode/` 供比对/许可合规。

#### 14.4.1 `src/propagator/TLEData.hpp` / `.cpp`

职责：单个航天器的 TLE 数据载体（普通类，非 GmatBase）。

```cpp
class TLEData
{
public:
   std::string satName;          // 卫星名
   std::string tleLines[3];      // 原始三行（名称行 + 两行数据）
   double secFromJ2k;            // 根数历元：J2000 起秒（CSPICE 形式）
   double elements[10];          // getelm_c 解析出的 10 元素数组
};
```

构造/拷贝/赋值（`.cpp:23-60`）把三行字符串与 10 元素数组整体复制。

#### 14.4.2 `src/propagator/TLEReader.hpp` / `.cpp`

职责：读 TLE 文件并解析成 CSPICE 元素。

- `GetTLEData(forSatellite)`（`.cpp:46`）：按名字/编号匹配——`line.find(forSatellite)==0`（名字作为行首）或 `==2`（NORAD 编号在第 2 列），也支持 `"SatId"` 通配读取；顺带剥掉 `\r`（Windows 换行，`:61-73`）。未命中返回空 `TLEData`。
- `ParseForSpice(TLEData&)`（`:143`）：把第 1、2 行拼成 `lines[180]`，调 CSPICE `getelm_c(2000, linelen, lines, &secFromJ2k, elements)`（`:150`）得到历元秒与 10 元素（含 `J2/J3/J4/KE/QO/SO/ER/AE` 之后是轨道根数）。

#### 14.4.3 `src/propagator/SPICEPropagator.hpp` / `.cpp`

职责：真正的 TLE 传播器（`SPICESGP4` 类型），`Propagator` 派生，管理每个传播对象的 TLE 状态与步进。

- 嵌套类 `PropObject`（`.hpp:179-211`）：每个传播对象持有 `theSat`（GMAT 航天器）、`satCoords`、`inputs[32]`（SPICE v66 的 `spke10` 输入数组）、`a1epoch`（A.1 修正儒略历元）、`timeOffset`（GMAT 历元与 TLE 历元的秒差）、`tleSettings`、`cconverter/baseCS`。
- 参数表（`.hpp:256-271`）：`STEPSIZE`、`CONFIG_FILENAME`、可覆盖的 `J2/J3/J4/KE/QO/SO/ER/AE` 八个引力/大气常数；`PARAMETER_TEXT` 见 `.cpp:65-80`。构造（`.cpp:359-378`）给出 WGS-72 默认值：

```cpp
params[0] = 1.082616e-3;    // J2
params[1] = -2.53881e-6;    // J3
params[2] = -1.65597e-6;    // J4
params[3] = 7.43669161e-2;  // KE = sqrt(mu) [ER^1.5/min]
params[4] = 120.0;          // QO 大气模型上界 km
params[5] = 78.0;           // SO 大气模型下界 km
params[6] = 6378.135;       // ER 地球赤道半径 km
params[7] = 1.0;            // AE 距离单位/地球半径
```

- `PropObject::Initialize(toTime, params)`（`.cpp:176`）：从航天器取 `EphemerisName`（TLE 文件名）与 `Id`（TLE 中的名字/NORAD 号）；`GmatFileUtil::FindFile` 定位文件；`TLEReader::GetTLEData` 取数据；随后做**一系列 TLE 合法性校验**（`:226-260`：两行必须各 69 字符、倾角 0-180°、RAAN/近地点幅角/平近点角 0-360°、偏心率 0-1、平运动 <99 rev/day）与**校验和检查**（`:263-281`，对每行各位求和 mod 10 对比末位，不符只告警）；`ParseForSpice` 后把 TLE 历元转 A.1MJD，若航天器没设历元则用 TLE 历元（`:292-298`）；组装 `inputs[32]`（`:315-333`：0-7 为物理常数，8-17 与 18-27 两段放 `elements`，28-31 重复 `elements[9]`），调 `spke10_(&et, inputs, iState)`（`:338`）求初始状态并写回航天器 X/Y/Z/VX/VY/VZ（`:345-350`）。
- `Step(dt)`（`:1022`）/`Step()`（`:1056`）：`timeFromEpoch += stepSize`，`propEpoch = initialTleEpoch + timeFromEpoch`，逐对象刷新 `inputs` 后再次 `spke10_` 得到 `j2kState`，`memcpy` 进 `state`，更新 `currentEpoch` 并 `UpdateSpaceObject()`（`:1093-1101`）。`RawStep()`（`:1113`）为未实现空壳。
- `GetParameterID`（`:438`）对 `CentralBody/EpochFormat/StartEpoch` 做"只读拦截"：TLE 传播器不允许覆盖这些来自航天器的设置（`:441-462`）。

#### 14.4.4 `src/propagator/SGP4Propagator.hpp` / `.cpp`

职责：**占位壳**。类名保留（`Propagator("SGP4", ...)`，`.cpp:32-35`），但没有任何实现逻辑——所有传播由 `SPICEPropagator` 承担，历史遗留的命名。讲解意义：插件演进中常见"改名不改壳"。

#### 14.4.5 工厂与入口

- `TlePropFactory`（`Gmat::PROPAGATOR`）：creatable `"SPICESGP4"`（`.cpp:113`），`CreatePropagator` 对 `"SPICESGP4"` 返回 `new SPICEPropagator`（`:88-89`）。
- `GmatPluginFunctions.cpp`：1 个工厂（`:38`）。

#### 14.4.6 `ValladoCode/`：参考 SGP4 实现（非 GMAT 编译产物）

- **`SGP4/SGP4/SGP4.h`**：`#define SGP4Version "SGP4 Version 2016-03-09"`（`:56`）；`gravconsttype {wgs72old, wgs72, wgs84}`（`:59-64`）；核心结构 `elsetrec`（`:66-111`）含近地（`isimp, aycof, con41, cc1...`）与深空（`irez, d2201, d2211...`）两段系数及 `a, altp, alta, epochdays, jdsatepoch...` 根数，还有 `tumin, mu, radiusearthkm, xke, j2, j3, j4, j3oj2` 常量；命名空间 `SGP4Funcs` 声明 `sgp4init`（`:120`）、`sgp4`（`:128`）、`getgravconst`（`:135`）等。
- **`SGP4/SGP4/SGP4.cpp`**：Vallado 的完整 SGP4 实现（3023 行），关键符号：`sgp4init`（`:1358`，由 TLE 初始化 `elsetrec`）、`getgravconst`（`:2068`）、`twoline2rv`（`:2165`，两行根数→`elsetrec`）、`gstime`（`:2461`，格林尼治恒星时）、`sgp4` 主推进。注释 `// sgp4fix` 标注了对原版的修正。
- **`SGP4DC/`**：深空 SGP4 变体（`SGP4DC.cpp`，1631 行）与配套工程文件，含月/日摄动（`irez` 分支）。
- **`TestSGP4/`**：独立验证程序（`TestSGP4mod.cpp`、`TestSGP4/TestSGP4.cpp`），配套 `SGP4-VER.TLE` 与数十个 `.e` 期望文件（`00005.e`…`88888.e`）。

这些文件仅作参考/合规用途，GMAT 运行期用的是 CSPICE `spke10`；讲解时注意区分。

#### 14.4.7 数据与示例（目录级说明）

- `TLE/Active_Nov-09-2019.txt`：示例 TLE 集合（Starlink、Lightsail2 等），也是测试数据。
- `samples/NeedTlePropagator/*.script`：6 个示例。以 `PropLightsail2.script` 为例：`Create Spacecraft Lightsail2; ... GMAT Lightsail2.EphemerisName = '../TLE/Active_Nov-09-2019.txt'; GMAT Lightsail2.Id = 'LIGHTSAIL 2';`（`:9-13`），再 `Create Propagator TleProp; GMAT TleProp.Type = TLE;`（`:20-22`）——注意脚本里类型写 `TLE`，由工厂/别名映射到 `SPICESGP4`。
- `test/`：回归脚本（`BasicPropagation.script`、`MMS1Propagation.script`、`TdrsPropagation.script`、`TerraPropagation.script`）、TLE 输入与 truth 文件（`test/truth/*.truth`）；`test/generator/orekit/` 用 Orekit（Java）生成参考数据（`OreTleProp.py`、`BuildTlePropData.py`）。
- `doc/`：Sphinx 文档（`source/*.rst`，`Scripting.rst` 目前只有标题占位）、`License-TlePropagator.txt` 说明许可来源（Vallado SGP4 使用条款）。

### 14.5 Msise00Plugin：NRLMSISE-00 大气模型

把 NRL（美国海军研究实验室）MSISE-00 经验大气模型接成 `AtmosphereModel`（见 [第6章](CH06-dynamics.md) 的 AtmosphereModel）。模型核是从 Fortran 用 f2c 翻译的 C 代码 `nrlmsise00_sub.c`。

#### 14.5.1 `src/base/atmosphere/NRLMsise00Atmosphere.hpp` / `.cpp`

职责：`NRLMsise00Atmosphere : public AtmosphereModel`（`.hpp:40`），把大气密度查询接到 Fortran 子程序 `gtd7_`。

`Density(Real *pos, Real *density, Real epoch, Integer count)`（`.cpp:158`）：

- 先检查中心体；`theTimeConverter->Convert(epoch, A1MJD, UTCMJD, ...)` 把 A.1 历元转 UTC（`:176-177`），调基类 `GetInputs(utcEpoch)` 得到年积日 `yd`、日内秒 `sod`、太阳活动指数 `f107/f107a`、地磁指数 `ap[7]`、`geoLat/geoLong/geoHeight`。
- 对每个航天器：`mass = 48`（平均分子量，`:215`）；`alt = CalculateGeodetics(...)` 求大地高度；`lst = sod/3600.0 + geoLong/15.0` 求地方太阳时（`:218`）；把 double 转 float（Fortran 单精度接口要求）后调用：

```cpp
#ifndef __SKIP_NRLMSISE00__
   gtd7_((integer*)&xyd,&xsod,&xalt,&xlat,&xlon,&xlst,&xf107a,&xf107,
         &xap[0],(integer*)&xmass, &xden[0], &xtemp[0]);      // :284-285
#endif
```

- 单位换算在收尾（`:322`）：`density[i] = ((double)xden[5] * 1000.0);  // 从 cg/cm^3 到 kg/m^3`。`xden[5]` 是总质量密度，`xden[0..4,6,7]` 是 HE/O/N2/O2/AR/H/N 数密度，`xtemp[0/1]` 是外逸层温度与当地温度。
- `Initialize()`（`:390`）直接转调 `AtmosphereModel::Initialize()`；`Clone/Copy` 标准实现。模型可用开关 `__SKIP_NRLMSISE00__` 编译期禁用（`extern "C"` 的 `gtd7_` 声明在 `:38-45`）。

#### 14.5.2 `src/base/atmosphere/nrlmsise00_sub.*`：模型内核

- **`nrlmsise00_sub.c`**（3260 行）：f2c（20100827 版）自动翻译的 C 代码，文件头注释（`:1-11`）要求链接 `libf2c`。结构：COMMON 块（`gts3c_`、`meso7_`、`lower7_`、`parm7_`、`datim7_`、`csw_` 等，`:20-80`）承载模型系数；主入口 `gtd7_`（`:884`）计算数密度/质量密度/温度；辅助 `gtd7d_`（`:1264`，稠密输出版）、`vtst7_`（`:1542`）、`scalh_`（`:2267`）、`globe7_`（`:2288`）、`glob7s_`（`:2723`）、`densu_`（`:2877`）、`densm_`（`:3009`）、`dnet_`（`:3316`）、`ccor_`（`:3386`）、`ccor2_`（`:3424`）。模型内部按高度分层（mesosphere/thermosphere）与纬度-季节球谐展开。
- **`nrlmsise00_sub.f` / `.for` / `_v2.for`**：原始 Fortran 源（2434/2440 行，`.for` 与 `.f` 同内容，`_v2` 是修订版），供追溯/交叉验证。
- **`nrlmsise00_sub.h`**：仅 include guard 的空头文件（12 行）。

#### 14.5.3 工厂与入口

`NRLMsise00Factory`（`Gmat::ATMOSPHERE`）：`CreateAtmosphereModel` 对 `"NRLMSISE00"` 返回 `new NRLMsise00Atmosphere(ofType, withName)`（`.cpp:69-72`）；`GetListOfCreatableObjects` 仅对 `"Earth"` 返回列表（`:180-195`）。`GmatPluginFunctions.cpp` 注册 1 个工厂。

### 14.6 ProductionPropagatorPlugin：Prince-Dormand 853 积分器

提供核心 Runge-Kutta 积分器的"生产级"变体——DP8(7)13M：8 阶解 + 7 阶误差控制，13 个有效级（表为 16 级，含稠密输出 4 级）。

#### 14.6.1 `src/base/propagator/PrinceDormand853.hpp` / `.cpp`

职责：`PrinceDormand853 : public RungeKutta`（`.hpp:39`），只覆写 `SetCoefficients()`。

构造（`.cpp:44-48`）：

```cpp
PrinceDormand853::PrinceDormand853(const std::string &nomme) :
   RungeKutta      (12, 8, "PrinceDormand853", nomme)   // 12 级、8 阶；16 级时含稠密输出
```

`SetCoefficients()`（`.cpp:117`）填充基类的系数数组 `ai`（节点）、`bij`（Butcher 表）、`cj`（误差权重）、`ee`（稠密输出）：

- `ai[0..11]`（`:124-135`）：`0, 0.0526, 0.0789, 0.1184, 0.2816, 1/3, 0.25, 0.3077, 0.6513, 0.6, 0.8571, 1.0`；`stages==16` 时再补 `ai[12..15]`（`:138-144`）。
- `bij[i][j]`（`:146-284`）：标准 DP853 系数，j 行非零项从 `j-3` 附近开始（相邻级耦合），如 `bij[8]` 一行含 `27.5921`、`-43.4899` 等大系数（`:183-190`），体现 DP 表的"非紧凑"特性。
- `cj[0..11]`（`:286-297`）：误差估计权重，`cj[0]=0.0543`、`cj[5]=4.4503` 等；`ee[0..11]`（`:305-316`）稠密输出插值系数，`stages==16` 时尾部清零。

积分步进/误差控制逻辑全部在基类 `RungeKutta`（见 [第7章](CH07-propagator.md)）。

#### 14.6.2 工厂与入口

`ProductionPropagatorFactory`（`Gmat::PROPAGATOR`）：creatable `"PrinceDormand853"`（`.cpp:90`），`CreatePropagator`（`:68`）对应 `new PrinceDormand853(withName)`。`GmatPluginFunctions.cpp` 注册 1 个工厂。

### 14.7 StationPlugin：地面站

把地面站（GroundStation）从 `SpacePoint` 扩展为带天线硬件、电离层/对流层修正模型、误差模型与仰角可见性判定的跟踪站对象，并提供 SWIG 绑定。

#### 14.7.1 `src/base/station/GroundStation.hpp` / `.cpp`

职责：`GroundStation : public GroundstationInterface`（`.hpp:51`）。`GroundstationInterface` 是 `SpacePoint` 的子类（含 BodyFixedPoint），故地面站本质是"固定在地球上的空间点"。

参数表（`.hpp:174-188`）：

```cpp
enum
{
   STATION_ID = BodyFixedPointParamCount,   // 站 ID
   ADD_HARDWARE,                            // 追加硬件（天线等）
   IONOSPHERE_MODEL,                        // 电离层修正：None/Klobuchar/IRI
   TROPOSPHERE_MODEL,                       // 对流层修正：None/...
   DATA_SOURCE,                             // "Constant" 或 "FromFile"
   TEMPERATURE, PRESSURE, HUMIDITY,         // 对流层修正输入：K / hPa / %
   MINIMUM_ELEVATION_ANGLE,                 // 可见性最低仰角（度）
   ERROR_MODELS,                            // 测量误差模型列表
   MASK_FILENAME,                           // 遮蔽文件 → 生成 CustomFOV
   GroundStationParamCount,
};
```

成员（`:140-170`）：`stationId`、`hardwareNames/hardwareList`、`ionosphereModel/troposphereModel`、`temperature=295.1K / pressure=1013.5hPa / humidity=55%`（`.cpp:121-123` 构造默认值）、`dataSource="Constant"`、`minElevationAngle=7.0°`（`.cpp:125`）、`az_el_visible[3]`、`errorModels/errorModelMap`、`maskFileName`。静态表 `DISALLOWED_ANGLE_PAIRS`（`.cpp:95-102`）禁止"方位/仰角"与"XEast/YNorth/XSouth/YEast"等非法轴组合。

关键方法（`.cpp`）：

- `Initialize()`（`:1293`）：解析硬件与误差模型引用。
- `IsValidElevationAngle(const Rvector6 &state_sez)`（`:1466`）：输入 SEZ（东南天）坐标，按 `MINIMUM_ELEVATION_ANGLE` 判定可见性，返回填充了方位/仰角/可见标志的 `az_el_visible`。
- `IsValidID()`（`:1441`）校验站 ID 格式。
- `CreateErrorModelForSignalPath(spacecraftName, spacecraftId)`（`:1366`）与 `GetErrorModelMap()`（`:134-135`）：为每条上下行信号路径克隆误差模型（GNSS 测量链用，见 [第13章](CH13-plugins-a.md) 的 EstimationPlugin）。
- `VerifyAddHardware()`（`:1184`）与 `VerifyErrorModels()`（`:1499`）做类型/重复性校验；析构（`:151-175`）统一释放硬件、误差模型及其克隆。
- 参数访问：`GetParameterID`（`:304`）、`GetStringParameter/SetStringParameter`（`:433`/`:465`）等全套 GmatBase 覆写；`GetRealParameter`（`:777`）等。

#### 14.7.2 `src/base/factory/StationFactory.hpp` / `.cpp`

`StationFactory`：creatable `"GroundStation"`（`.cpp:54`），且注册新类型 `GmatType::RegisterType(Gmat::GROUND_STATION, "GroundStation")`（`:57`）；`CreateSpacePoint` 对 `"GroundStation"` 返回 `new GroundStation(withName)`（`:155-156`）。`GmatPluginFunctions.cpp` 注册 1 个工厂。

#### 14.7.3 `swig/`：脚本语言绑定

- `station.i`：SWIG 模块入口（`%module station`，import `gmat.i` 与 `station.swg`）。
- `station.swg`：声明 `%apply double[] {double *}`；用宏把 `GetEstimationParameterValue`（返回数组，`:5`）与 `IsValidElevationAngle`（固定 3 元素，`:6`）映射成 Java 数组返回；`%ignore PARAMETER_TEXT/PARAMETER_TYPE`（`:17-18`）；`DOWNCAST(GroundStation,GmatBase)`（`:19`）生成类型降级转换。
- `station_py.i`：Python 版模块（`%module station_py`，import `gmat_py.i`）。
- `StationAPI.hpp`：仅 include `GmatAPI.hpp/StationDefs.hpp/GroundStation.hpp`，供 SWIG 包装器编译。
- 另有 `swig/CMakeLists.txt` 挂载到插件构建。

### 14.8 ThrustFilePlugin：推力历史文件（THF）

用推力历史文件（Thrust History File）驱动有限推力机动。四层结构：THF 数据段（`ThfDataSegment`）→ 段对象（`ThrustSegment`）→ 文件读取器（`ThrustHistoryFile`）→ 力模型（`FileThrust`），外加一对命令（`BeginFileThrust`/`EndFileThrust`）与一套段参数。

#### 14.8.1 `src/base/datareader/ThfDataSegment.hpp` / `.cpp`

职责：纯数据结构（公开成员，"acts as a structure"，`:28-30`），存一个段的头部字段与推力剖面。

```cpp
struct ThrustPoint                                    // :57
{
   Real time;        // 相对段起始的时标（天的小数）
   Real magnitude;   // 推力/加速度幅值（暂未用）
   Real vector[3];   // 瞬时推力（或加速度）三分量
   Real mdot;        // 质量流率
};
enum InterpolationType { NONE, LINEAR, SPLINE };      // :76-81
```

头部字段（`:87-134`）：`segmentName`、`startEpochString/startEpoch(startEpochGT)`、`endEpoch(endEpochGT)`、`hasPrecisionTime`、`csName/cs`（推力数据的坐标系）、`interpolationMethod/accelIntType`（推力插值）、`massFlowInterpolationMethod/massIntType`（质量流插值）、`modelFlag/modelThrust`（"推力"还是"加速度"数据）、`profile`（节点序列）、`isActive`；以及从 `ThrustSegment` 对象传回的比例因子（`thrustScaleFactor/massFlowScaleFactor/includeThrustFactorInMassFlow/tanks`，`:127-134`）。

#### 14.8.2 `src/base/datareader/ThrustSegment.hpp` / `.cpp`

职责：`ThrustSegment : public GmatBase`（`.hpp:41`），脚本可见的段对象，包装一个 `ThfDataSegment segData`（`:190`）并叠加可估计参数。

参数表（`.hpp:235-252`）：`THRUSTSCALEFACTOR`、`TSF_SIGMA`、`TSF_MASSFLOW`、`MASSFLOWSCALEFACTOR`、`MASSSOURCE`（供油箱）、`THRUST_ANGLE_CONSTRAINT`、`THRUST_ANGLE_1/2`、`THRUST_ANGLE_SIGMA_1/2`、`SOLVEFORS`、`TSF_EPSILON`、`START_EPOCH`、`END_EPOCH`。成员含 STM 索引进位（`tsfIndex/ta1Index/ta2Index`，`:222-226`）用于估计器（见 [第13章](CH13-plugins-a.md) 估计框架）。

关键方法：`SetDataSegment()`（`.cpp:1703`）接收解析出的段数据；`DepletesMass()`（`:1721`）；`GetScaleFactors()`（`:1735`）；`GetStmIndex/SetStmIndex`（`:1753`/`:1780`）；`IsEstimationParameterValid`（`:1817`）与 `HasParameterCovariances`（`:1881`）支撑推力比例因子/推力角的解算与协方差；`HadScriptUpdate/ResetScriptUpdate`（`:1934`/`:1939`）标记脚本运行期改写（供 `FileThrust::GetDerivatives` 同步，见下）。

#### 14.8.3 `src/base/datareader/ThrustHistoryFile.hpp` / `.cpp`

职责：`ThrustHistoryFile : public FileReader`（`.hpp:42`），解析 THF 文本文件、产出 `segments`（文件段）与 `scriptSegments`（脚本段），并内建一个 `FileThrust theForce`（`.hpp:135`）。

参数：`FILENAME`、`SEGMENTS`（`.hpp:146-151`）。

- `ReadData()`（`.cpp:724`）：读全文，按关键字切段；`CheckDataStart`（`:1009`）识别段起始（`dataStartKeys` 如 "BEGIN Segment" 之类），`SetHeaderField`（`:1043`）/`MapField`（`:1095`）解析键值对，`ReadThrustProfile`（`:1214`）读节点表，`ValidateSegment`（`:1330`）检查历元/坐标系等必填项（`startEpochFound/coordSystemFound`，`.hpp:127-128`）。
- `ActivateSegments()`（`:915`）/`DeactivateSegments()`（`:964`）：把段激活/停用状态同步给 `theForce`；`AllDataSegmentsLoaded`（`:893`）汇报缺失段。
- `GetForce()`（`:1129`）返回内部 `FileThrust*`，供命令注册为瞬态力。
- `Initialize()`（`:980`）：`FileReader` 打开文件 + `ReadData` + `ActivateSegments`。

#### 14.8.4 `src/base/forcemodel/FileThrust.hpp` / `.cpp`

职责：`FileThrust : public PhysicalModel`（`.hpp:42`），按 THF 剖面为航天器产生推力/加速度导数，是瞬态力模型（`IsTransient()=true`，`.cpp:976`），支持质量消耗（`DepletesMass()`，`.cpp:990`）。

数据成员（`.hpp:163-261`）：`segments/scriptSegments` 指针（由 `SetSegmentList` 注入，`.cpp:1004`）；`dataIsThrust`（数据是推力还是加速度）；`dataBlock[7]`（3 推力分量 + mdot + 插值标志）、`dataSet[5][5]`；插值器 `liner`（LinearInterpolator，暂未用）与 `spliner`（NotAKnotInterpolator）；解算支持 `thrustSF/tsfEpsilon/estimatingTSF/estimatingAngles`；`coordSystem`（段坐标系→惯性转换）。

核心流程 `GetDerivatives(Real* state, Real dt, ...)`（`.cpp:1183`）：

- 先同步脚本改写：遍历 `scriptSegments`，若 `HadScriptUpdate()` 则把 `ThrustScaleFactor/ThrustAngle1/ThrustAngle2` 刷入文件段（`:1247-1268`）。
- 对每个航天器调用 `ComputeAccelerationMassFlow(segmentEpoch, now, burnData)`（`:1775` 双精度版 / `:1925` 精度时间版）：按当前时刻在段内定位（`GetSegmentData`，`:2080` 二分定位索引+偏移），`Interpolate`（`:2113`）→ `LinearInterpolate`（`:2193`）/`SplineInterpolate`（`:2249`）按节点插值出推力与质量流；`ApplyAngleRotations`（`:2326`）按段角 1/2 旋转推力方向，`ApplyAngleDotRotations`（`:2402`）给出对角度导数的旋转（解算/协方差用）。
- 单位换算（`:1285-1297`）：`factor = 0.001`（m/s² → km/s²），`dataIsThrust` 时再 `factor /= mass`（`TotalMass`），`accel[i] += burnData[i]*factor`。
- 质量流：`depleteMass` 时把 `burnData[3]`（kg/s）写进 `mDotIndex` 对应的状态槽（`mloc`，`:1214-1218`）。
- 时间处理：精度时间（`GmatTime`）与非精度双路径，`segmentEpoch = epoch + elapsedTime/SECS_PER_DAY`（`:1280`）。
- 边界查询：`GetForceMaxStep`（`:2800/2832/2899`）按段边界限制步长，`IsEndOfThrust`（`:2954`）供事件/停止判定；`InSegmentInterval`（`:3134`）处理跨午夜区间。
- 参数与 STM：`SetStmIndex`（`:1750`）、`HasParameterCovariances/GetParameterCovariances`（`:2685`/`:2776` 附近）把 TSF/角度估计量纳入状态转移矩阵；`UpdateScriptSegments` 系列（`:3051-3130`）供脚本在运行期改段参数。

#### 14.8.5 `src/base/command/BeginFileThrust.hpp` / `.cpp`、`EndFileThrust.hpp` / `.cpp`

一对命令把 `FileThrust` 挂进瞬态力表：

- `BeginFileThrust : public GmatCommand`（`.hpp:42`）：成员 `burnForce`（`FileThrust*`）、`thrustFile`（`ThrustHistoryFile*`）、`satNames/sats`、`transientForces`（沙箱的瞬态力表指针，`.hpp:84`）。`Initialize()` 解析 THF 对象与航天器名、`SetTransientForces`（`.hpp:74`）注册自身为瞬态力；`Execute()` 激活力并开始机动。
- `EndFileThrust : public GmatCommand`（`.hpp:41`）：对称地结束机动、`DeactivateSegments`、从瞬态力表移除。二者 `DEFAULT_TO_NO_CLONES`。

#### 14.8.6 `src/base/parameter/`：段参数

- **`ThrustSegmentData.hpp`**：`ThrustSegmentData : public RefData`（`:37`），段参数的数据层，`GetReal/SetReal/GetRvector/SetRvector`（`:46-53`）转发到 `mThrustSegment`；未定义返回哨兵 `THRUST_REAL_UNDEFINED`（`:59`）与 `UNDEFINED_RETURN_RVECTOR`（`:70`）。内部枚举（`:73-79`）列出段各字段下标。
- **`ThrustSegmentReal.hpp`**：`ThrustSegmentReal : public RealVar, public ThrustSegmentData`（`:39`），实数段参数基类。
- **`ThrustSegmentRvector.hpp`**：`ThrustSegmentRvector : public RvectorVar, public ThrustSegmentData`（`:39`），向量段参数基类，`IsOptionalField`（`:51`）标记可选字段。
- **`ThrustSegmentParameters.hpp`**：10 个具体参数类——`ThrustSegmentScaleFactor`、`TSFSigma`、`TSFEpsilon`、`StartEpoch`、`EndEpoch`、`MassFlowScaleFactor`（`ThrustSegmentReal` 派生）；`ThrustAngleConstraint`、`ThrustAngle1`、`ThrustAngle2`、`ThrustAngle1Sigma`、`ThrustAngle2Sigma`（`ThrustSegmentRvector` 派生）。各自覆写 `Evaluate()` 与 `SetReal/SetRvector`（写回段对象供解算/命令设置）。

#### 14.8.7 工厂与入口

四个工厂（`GmatPluginFunctions.cpp` 的 `GetFactoryCount()` 返回 4，`:55`）：

- `ThrustFileForceFactory`：**空壳**——creatables 全部注释掉、`CreateCommand` 恒返 NULL（`.cpp:44-51`、`:130-134`），历史遗留。
- `ThrustFileCommandFactory`（`Gmat::COMMAND`）：`"BeginFileThrust"`/`"EndFileThrust"`（`.cpp:51-52`、`:135-138`）。
- `ThrustFileReaderFactory`（`Gmat::DATA_FILE` 类）：`"ThrustHistoryFile"`/`"ThrustSegment"`（`.cpp:46-47`、`:125-127`）。
- `ThrustSegmentParameterFactory`（`Gmat::PARAMETER`）：creatable 只有 `"ThrustScaleFactor"`/`"ThrustAngle1"`/`"ThrustAngle2"` 三个激活（其余注释，`.cpp:138-145`），`CreateParameter` 对应三个类（`:89-103`）。

### 14.9 SaveCommandPlugin：Save 命令

#### 14.9.1 `src/base/command/Save.hpp` / `.cpp`

职责：`Save : public GmatCommand`（`.hpp:42`），把对象按 GmatBase 序列化规则写入 ASCII 文件，用于脚本存档/交接。

参数只有一个 `OBJECT_NAMES`（`STRINGARRAY_TYPE`，`.hpp:96-100`、`.cpp:47-57`）。成员：`fileNameArray`、`appendData`（追加开关）、`wasWritten`（本 run 已写）、`objNameArray/objArray`、`writeVerbose`、`fileArray`（`std::ofstream*`）。

- `SetStringParameter`（`.cpp:206`）：向 `objNameArray` 追加对象名，重复名抛 `CommandException`（`:211-218`）。
- `Execute()`（`:501`）：按 `__USE_SINGLE_FILE__` 宏分支——默认每个对象一个文件，循环 `fileArray[i].open(fileNameArray[i])`（append 与否看 `appendData && wasWritten`，`:517-525`）；`fileArray[i].precision(prec)` 取 `GmatGlobal::GetDataPrecision()`（`:507`）保证输出精度；然后逐个 `WriteObject(i, objArray[i])`（`:554-555`）并关闭。
- `WriteObject(UnsignedInt i, GmatBase *o)`（`:724`）：调 `o->GetGeneratingString(Gmat::SCRIPTING)` 之类的序列化接口写出。
- `Initialize()`（`:391`）：解析对象名→指针，构造文件名（`objectName.objectType` 风格，`UpdateOutputFileNames` 见 `:697`）。
- `TakeAction`（`:648`）支持 `Append`/`Verbose` 等动作；`RunComplete()`（`:575`）清空缓存。

#### 14.9.2 工厂与入口

`SaveCommandFactory`：creatable `"Save"`（`.cpp:49`），`CreateCommand` 对 `"Save"` 返回 `new Save()`（`:132-133`）。`GmatPluginFunctions.cpp` 注册 1 个工厂。`SaveCommandDefs.hpp` 为导出宏模板。

### 14.10 ScriptToolsPlugin：CommandEcho 命令

#### 14.10.1 `src/base/command/CommandEcho.hpp` / `.cpp`

职责：`CommandEcho : public GmatCommand`（`.hpp:43`），运行期切换 GMAT 的"命令回显"模式（每条命令执行时是否打印到消息窗口）。

成员（`.hpp:77-83`）：`echoStatus`（bool）、`echoSetting`（`"On"/"Off"` 字符串）、`initval`（保存初始状态以便 RunComplete 恢复）。

- `SettingInput(eSetting)`（`.cpp:113`）：`"On"→true`、`"Off"→false`，其他值抛 `CommandException`（`:121-123`）。
- `InterpretAction()`（`:188`）：脚本解析——取 `InterpretPreface()` 的第二个 token，剥掉引号（`:194-203`），转 `SettingInput`。
- `Execute()`（`:173`）：`GmatGlobal::Instance()->SetCommandEchoMode(echoStatus)`——一行代码对接全局开关（`GmatGlobal` 见 [第2章](CH02-foundation.md)）。
- `RunComplete()`（`.hpp:55`）：把回显恢复为 `initval` 初始值。

#### 14.10.2 工厂与入口

`CommandEchoFactory`：creatable `"CommandEcho"`（`.cpp:47`），`CreateCommand` 返回 `new CommandEcho()`（`:130-131`）。`GmatPluginFunctions.cpp` 注册 1 个工厂。

### 14.11 NewParameterPlugin：力模型/求解器参数

为脚本补充一批"力模型相关"与"求解器状态"参数：加速度分量、大气密度、各类力矩，以及求解器的数值/状态/字符串字段。设计上全部走"`RefData` 数据层 + 参数基类多重继承"模式。

#### 14.11.1 `src/base/parameter/OdeData.hpp` / `.cpp`

职责：`OdeData : public RefData`（`.hpp:45`），ODE 力模型数据层。成员（`.hpp:69-72`）：`mSpacecraft/mSolarSystem/mModel`、`transients`（瞬态力表）；`GetOdeReal(const std::string&)`（`.cpp:151`）与 `GetOdeRvec3`（`.cpp:294`）是取数入口。

`GetOdeReal` 两分支：

- `"FMDensity"`（`:163`）：从 `ODEModel` 取 `DragForce`（`:170`），`BuildModelState` 构造模型状态后 `df->GetDensity(state, epoch, 1) * 1.0e9`（`:194-196`）——大气力返回 kg/m³，参数约定输出 kg/km³，故乘 1e9。
- `"FMAcceleration"/X/Y/Z`（`:207`）：先临时挂载 `transients` 中与本航天器相关的瞬态力（`:228-247`），再 `mModel->GetDerivativesForSpacecraft(mSpacecraft)` 取 `Rvector6`，其中 `deriv[3..5]` 是加速度三分量（`:250-261`），取模或分量返回，随后卸载瞬态力（`:264-270`）。

`GetOdeRvec3`（`:294`）：`"BurnTorque"/"GravityTorque"/"SRPTorque"/"TotalTorque"` → `((ODEModel*)mModel)->GetTorquesForSpacecraft(mSpacecraft, str)`（`:325`），同样处理瞬态力。`InitializeRefObjects()`（`:384`）解析 Spacecraft/SolarSystem/ODEModel 三个引用对象，缺失抛 `ParameterException`。

#### 14.11.2 `OdeReal.hpp` / `.cpp`、`OdeRvec3.hpp` / `.cpp`

- `OdeReal : public RealVar, public OdeData`（`OdeReal.hpp:40`）：实数参数基类，`EvaluateReal()` 调 `OdeData::GetOdeReal(GetTypeName())`；把 `AddRefObject/SetSolarSystem/SetTransientForces/NeedsForces` 转发给数据层（`:55-75`）。
- `OdeRvec3 : public Rvec3Var, public OdeData`（`OdeRvec3.hpp:40`）：向量参数基类，`EvaluateRvector()` 对应 `GetOdeRvec3`。

#### 14.11.3 具体参数

- **`FMDensity.hpp` / `.cpp`**：`FMDensity : public OdeReal`（`.hpp:45`），`Evaluate()`（`.cpp:120`）取 `"FMDensity"`。
- **`FMAcceleration.hpp` / `.cpp`**：同一文件里四个类（`.hpp:45` 起）——`FMAcceleration`（模）与 `FMAccelerationX/Y/Z`（分量），各自 `Evaluate()`（`FMAcceleration.cpp:123` 等）。
- **`AtmosDensity.hpp` / `.cpp`**：`AtmosDensity : public EnvReal`（`.hpp:46`），大气密度（沿用旧 Env 体系，`Evaluate()` 于 `AtmosDensity.cpp:122`）。
- **`Torque.hpp` / `.cpp`**：四个力矩参数 `BurnTorque/GravityTorque/SRPTorque/TotalTorque : public OdeRvec3`（`.hpp:37/68/99/...`），`Evaluate()` 调 `OdeData::GetOdeRvec3("BurnTorque")` 等（`Torque.cpp:112-120`），并额外暴露 `VectorSize` 参数（`VECTOR_SIZE = OdeDataObjectCount`，`.hpp:60-64`）供脚本访问数组长度。

#### 14.11.4 求解器参数家族

- **`SolverData.hpp` / `.cpp`**：`SolverData : public RefData`（`.hpp:43`），`mSolver` 引用。`GetSolverReal`（`.cpp:127-175` 附近）：把 `IntegerSolverStatus` 映射为数值（`CONVERGED→1.0`、`EXCEEDED_ITERATIONS→-1.0`、`FAILED→-2.0`、运行中 `0.0`，`.cpp:144-168`）；`GetSolverString`（`.cpp:188`）：映射字符串（`"Ready"/"Initialized"/"Running"/"Converged"/"ExceededIterations"/"DidNotConverge"`，`:205-235`），未找到求解器返回 `"SolverNotFound"`（`:240`）。
- **`SolverReal.hpp` / `.cpp`**：`SolverReal : public RealVar, public SolverData`（`.hpp:40`），`EvaluateReal()` 走 `GetSolverReal`，并实现 `GetExternalCloneName/SetExternalClone`（`.hpp:74-75`）供求解器克隆机制用。
- **`SolverString.hpp` / `.cpp`**：`SolverString : public StringVar, public SolverData`（`.hpp:40`），`EvaluateString()` 走 `GetSolverString`；`GetGeneratingString`（`.hpp:73-76`）支持脚本序列化。
- **`SolverState.hpp` / `.cpp`**：`SolverState : public SolverReal`（`.hpp:36`），`Evaluate()`（`SolverState.cpp:105`）取求解器数值状态。
- **`SolverStatus.hpp` / `.cpp`**：`SolverStatus : public SolverString`（`.hpp:36`），`Evaluate()`（`SolverStatus.cpp:104`）取求解器字符串状态。

#### 14.11.5 `src/base/factory/NewParameterFactory.cpp`

`NewParameterFactory`（`Gmat::PARAMETER`）：creatable 11 项（`.cpp:134-147`：`Acceleration/AccelerationX/Y/Z/AtmosDensity/SolverStatus/SolverState/BurnTorque/GravityTorque/SRPTorque/TotalTorque`）；`CreateParameter`（`:82`）按名 `new` 对应类。`GetListOfCreatableObjects`（`:264`）里有一段"构造即注册"hack（`:275-328`）：为让参数在 GUI 上先于使用出现，用 `"DefaultSC.DefaultFM.Acceleration"` 等假名各构造一次再删除，触发构造器里的 `ParameterInfo` 注册（`registrationComplete` 标志防重复）。

### 14.12 OVtoOFI：OrbitView → OpenFramesInterface 映射

用 OpenFrames 渲染器（OpenFramesInterface，见 [第8章](CH08-base-subsystems.md)）替换传统 OrbitView，以提升性能与稳定性。做法是"工厂覆写"：脚本请求 `OrbitView` 时，本插件工厂返回 `OVtoOFI` 对象。

#### 14.12.1 `src/base/subscriber/OVtoOFI.hpp` / `.cpp`

两个类：

- **`InvisOpenFramesView : public OpenFramesView`**（`.hpp:37`）：不可见视图壳。`GetGeneratingString` 返回空串（`:165-168`，注释："This because the object is automatically regenerated when the script is loaded"）——OVtoOFI 内部自动创建的视图不应写入脚本。
- **`OVtoOFI : public OpenFramesInterface`**（`.hpp:54`）：核心映射类。参数表（`.hpp:141-175`）覆盖 OrbitView 的全部视觉参数：`ORBIT_COLOR/TARGET_COLOR/DATA_COLLECT_FREQUENCY/UPDATE_PLOT_FREQUENCY/NUM_POINTS_TO_REDRAW/MAX_DATA/SHOW_LABELS/VIEWPOINT_*(REF/REFERENCE/REF_TYPE/REF_VECTOR/VECTOR/VECTOR_TYPE/VECTOR_VECTOR)/VIEW_DIRECTION_*/VIEW_SCALE_FACTOR/VIEW_UP_*/CELESTIAL_PLANE/WIRE_FRAME/GRID/EARTH_SUN_LINES/SUN_LINE/OVERLAP_PLOT/USE_INITIAL_VIEW/ENABLE_CONSTELLATIONS/MIN_FOV/MAX_FOV/INITIAL_FOV`。

构造（`.cpp:176-209`）：

```cpp
OVtoOFI::OVtoOFI(const std::string& type, const std::string& name) :
   OpenFramesInterface(type, name),
   defaultUp(0.0, 0.0, 1.0), viewPoint(30000.0, 0.0, 0.0),
   viewUp("Z"), addCount(0), showLabels(true),
   drawGrid(false), viewScaleFactor(1.0)
{
   std::string ofvName = name + "_View";
   UnsignedInt viewType = GmatType::GetTypeId("OpenFramesView");
   theView = (OpenFramesView*)(Moderator::Instance()->CreateObject(
         viewType, "OpenFramesView", ofvName));        // :193-194 自动建视图
   theView->SetStringParameter("ViewFrame", "CoordinateSystem");
   theView->SetOnOffParameter("SetDefaultLocation", "On");
   ...
   OpenFramesInterface::SetStringParameter(OpenFramesInterface::VIEW, ofvName, 0);  // :208
}
```

要点：通过 `Moderator` 自动创建配套 `OpenFramesView`，把 OrbitView 的默认取景（`setupDefaultEye` `:1396`、`DefaultCenter`、`DefaultUp`）灌进去，再把视图名绑到 OFI 的 `VIEW` 参数。

参数转发策略：`SetIntegerParameter/SetRealParameter/SetRvectorParameter/SetStringParameter/SetOnOffParameter/SetBooleanParameter/SetBooleanArrayParameter` 等（`:466` 起）全部做"ID 平移"：本地 ID 段直接处理（更新 `showLabels/drawGrid/addCount` 等成员），基类 ID 段通过 `FALL_THROUGH_OFFSET` 偏移后转 `OpenFramesInterface`（如 `SetBooleanArrayParameter` `:1292-1298`）。`GetGeneratingString`（`:1351`）转调 OFI 序列化器；辅助 `setupGrid()`（`:1366`）把网格开关批量写进 `DRAW_GRID` 数组。

#### 14.12.2 工厂与入口

- `OVtoOFIFactory`：**覆写工厂**——creatables 与 overrides 均含 `OrbitView/Enhanced3DView/OpenGLPlot`（`.cpp:94-106`）；`CreateSubscriber` 对这三个类型统一返回 `new OVtoOFI("OpenFramesInterface", withName)` 并打印转换提示（`:65-80`）。覆写机制见 [第4章](CH04-executive-factory.md)。
- `InvisOpenFramesViewFactory`：creatable/override `"OpenFramesView"`（`.cpp:62-74`），`CreateObject` 返回 `new InvisOpenFramesView`（`:42-51`），注册类型 `GmatType::RegisterType("OpenFramesView")`（`:63`）。
- `GmatPluginFunctions.cpp`：2 个工厂（`:39-42`）。

### 14.13 YukonOptimizerPlugin：SQP 优化器

Yukon 是 GMAT 的新型序列二次规划（SQP）优化器（源自 NASA 的 Yukon 算法，作者 S. Hughes）。四层：`Yukonad`（InternalOptimizer 适配器，状态机）→ `Yukon`（SQP 主循环）→ `MinQP`（活动集 QP 子问题求解器）→ `YukonUserProblem`/`NLPFunctionGenerator`（问题接口与弹性模式封装）。

#### 14.13.1 `src/base/solver/YukonUserProblem.hpp` / `.cpp`

职责：用户问题抽象基类（`YukonUserProblem`，`.hpp:41`），纯虚接口即 NLP 定义：

```cpp
virtual void GetNLPInfo(Integer &totalNumVars, Integer &totalNumCons) = 0;  // :46
virtual Rvector GetStartingPoint() = 0;                                     // :47
virtual void GetBoundsInfo(...) = 0;                                        // :48
virtual Real EvaluateCostFunc(Integer numVars, Rvector decVector, bool isNewX) = 0; // :49
virtual Rvector EvaluateCostJac(...) = 0;                                   // :50
virtual Rvector EvaluateConFunc(...) = 0;                                   // :51
virtual Rmatrix EvaluateConJac(...) = 0;                                    // :52
virtual void EvaluateConJacDimensions(...) = 0;                             // :53
virtual std::vector<Real> GetMaxVarStepSize() = 0;                          // :54
```

保护成员（`:60-127`）：界约束矩阵 `AVarBound/bVarBound`、约束类型向量 `conType`、四类约束计数与起始下标（`numNonLinIneqCon/nonLinIneqConStartIdx` 等，`:89-110`）、`conFunctions/conJacobian/costJacobian`。`HandleOneSidedVarBounds`（`.cpp:58`）把单侧界（`±inf`）转成双侧不等式约束。

#### 14.13.2 `src/base/solver/NLPFunctionGenerator.hpp` / `.cpp`

职责：NLP 函数生成器——把用户问题包装成"含界约束 + 弹性模式"的完整 NLP，供 `Yukon` 调用。

- `EvaluateCostAndJac/EvaluateConAndJac/EvaluateAllFunJac/EvaluateFuncsOnly/EvaluateDerivsOnly`（`.hpp:53-67`）：组合调用用户问题接口并计数（`numFunEvals/numGEvals`）。
- `GetNLPInfo/GetNLPStartingPoint/GetNLPBoundsInfo/EvaluateNLP*`（`.hpp:71-84`）：扩展后的 NLP 视图，把变量界转成额外线性约束（`boundAMatrix`，`.hpp:133`）。
- 弹性模式（`PrepareElasticMode` `.hpp:49`、`GetElasticV/GetElasticW` `.hpp:91-92`、`UpdateElasticCostJacobian` `.hpp:87`）：当原始问题不可行时，给每个约束引入弹性变量（V/W），把硬约束松弛成罚函数——`maxElasticWeight` 控制罚权重。

#### 14.13.3 `src/base/solver/MinQP.hpp` / `.cpp`

职责：QP 子问题求解器，活动集方法（Nocedal & Wright 算法 16.1 + Gill-Murray-Wright Phase I）。

头文件注释（`.hpp:9-35`）给出问题形式与退出码约定：

```text
min 0.5*x'*G*x + x'*d
subject to b_lower <= A*x <= b_upper
exitFlag:  1 Converged / 0 无效问题 / -1 不可行 / -2 迭代超限 /
          -3 奇异QP / -4 零空间求解失败 / -5 拉格朗日乘子求解失败
```

构造（`.hpp:94-96`）收 `initGuess, G, d, A, conLB, conUB, W, PhaseNum, checkForDuplicateCons`。成员含三个分解器对象（`LUFactorization lu/luPivot`、`QRFactorization qr`，`.hpp:109-113`，见 [第3章](CH03-math.md)）。

- `Optimize(Rvector &sol, Real &q, Rvector &lagMult, Integer &Converged, Integer &iter, Rvector &activeIS)`（`.cpp:180`）：主入口，KKT 条件用零空间法求解；支持活动集 Hot Start（`GetActiveSet`，`.cpp:159`）。
- `SetUpPhaseI`（`.cpp:1630`）：构造 Phase I 最小化"约束违犯的 ∞ 范数"的简化问题，递归调用自身；不可行则 `exitFlag=-1`。
- `TestForLinearlyDependentCons`（`.cpp:1880`）、`ComputeDistanceToInactiveCons`（`:1489`）、`GetModifiedCons`（`:1192`，返回被合并的约束下标，供 SQP 层剔除冗余约束）等支撑活动集维护。

#### 14.13.4 `src/base/solver/Yukon.hpp` / `.cpp`

职责：SQP 主循环（纯算法类，不依赖 GMAT 对象，除 `MessageInterface`）。构造（`.hpp:49-52`）接收用户问题、Hessian 更新方法（`DampedBFGS/SelfScaledBFGS`）、最大迭代/函数评估数、三容差（可行性/最优性/函数）与最大弹性权重。

主流程 `Optimize()`（`.cpp:586`）：

```cpp
void Yukon::Optimize(Rvector &decVector, Real &costOut, Integer &exitFlag,
                     OutputData &output)
{
   PrepareToOptimize();                     // 初始化：NLP 信息、初值、约束类型
   isFinished = false;
   while (!isFinished)
   {
      PrepareLineSearch();                  // 迭代计数、检查最大迭代
      if (qpExitFlag <= 0) { PrepareFailedRunOutput(...); return; }
      while (!foundStep && srchCount < 10)
         TakeStep();                        // 线搜索：α 缩减
      PrepareForNextIteration();            // Hessian 更新、乘子更新
      CheckIfFinished();                    // 收敛/失败判定
   }
   PrepareOutput(decVector, costOut, exitFlag, output);
}
```

- `ComputeSearchDirection`（`:1216`）：组装 QP 子问题（目标 `0.5 px' H px + gradLag' px`、线性化约束），调 `MinQP::Optimize` 得搜索方向 `px` 与乘子 `plam`。
- `UpdateHessian`（`:1375`）：BFGS 族更新（`DampedBFGS` 默认）。
- `CalcMeritFunction`（`:1566`）/`CalcConViolations`（`:1595`）：`l1` 罚函数 `f + Σ μᵢ·violᵢ` 形式。
- `CheckConvergence`（`:1657`）：KKT 残差 + 步长 + 函数下降多准则。
- `RemoveLinearlyDependentCons`（`:1816`）用 `MinQP::GetModifiedCons` 结果剔除冗余约束。
- 弹性模式：`PrepareElasticMode`（`:1328`）在 QP 不可行时给约束加弹性变量。

#### 14.13.5 `src/base/solver/GmatProblemInterface.hpp` / `.cpp`

职责：`GmatProblemInterface : public YukonUserProblem`（`.hpp:40`），把 GMAT 求解器数据（`Yukonad`）适配成 `YukonUserProblem`。

- `GetNLPInfo`（`.cpp:58`）：`totalNumVars = optimizerData->registeredVariableCount`、`totalNumCons = optimizerData->registeredComponentCount`。
- `GetBoundsInfo`（`:94`）：从 `variableMinimum/Maximum` 取变量界；等式约束取 `eqConstraintDesiredValues`（上下界相同），不等式按 `ineqConstraintOp`（`+1` 下界 / `-1` 上界）展开成 `[值, ±inf]`（`:107-131`）。
- `EvaluateCostFunc`（`:151`）直接返回 `optimizerData->cost`；`EvaluateCostJac` 返回 `costJacobian`；`EvaluateConFunc/EvaluateConJac` 返回约束值与 Jacobian（由 `SetConFunction`（`.hpp:57`）在每次轨迹评估时注入）。
- `SetPointerToOptimizer(Yukonad*)`（`.hpp:56`）建立反向指针。

#### 14.13.6 `src/base/solver/Yukonad.hpp` / `.cpp`

职责：`Yukonad : public InternalOptimizer`（`.hpp:54`，见 [第8章](CH08-base-subsystems.md) 的 Optimizer 体系），把 Yukon 接进 GMAT 求解器状态机（`RunNominal → RunPerturbation → CalculateParameters → CheckCompletion → RunComplete`）。

- 参数表（`.hpp:136-147`）：`goalNameID/useCentralDifferencesID/feasibilityToleranceID/hessianUpdateMethodID/maximumFunctionEvalsID/optimalityToleranceID/functionToleranceID/maximumElasticWeightID`；`Hessian_Update_Method` 枚举 `{DampedBFGS, SelfScaledBFGS, MaxUpdateMethod}`（`:149-154`）。
- 状态机方法：`AdvanceState()`（`.cpp:907`）、`RunNominal()`（`:1234`，驱动一次完整轨迹评估并收集 cost/约束）、`RunPerturbation()`（`:1251`，用 `Gradient/Jacobian` 工具做中心差分/前向差分求导，`useCentralDifferences` 开关）、`CalculateParameters()`（`:1344`，把梯度/雅可比喂给 `Yukon`）、`CheckCompletion()`（`:1377`，收 `Yukon` 的收敛判定并写回求解器状态）、`RunComplete()`（`:1470`，释放数组）。
- `Optimize()`（`:1016`）是空壳（恒 true）——优化实际发生在 `AdvanceState` 的状态机里；`SetSolverResults`（`:1035`）把 `"Objective"` 型结果识别为目标函数。
- 内部持 `Yukon *runOptimizer` 与 `GmatProblemInterface *gmatProblem`（`.hpp:216-218`）。

#### 14.13.7 辅助头文件、工厂与入口

- **`YukonOptions.hpp`**：`OptionsList` 结构（`:41-69`）——`hessUpdateMethod/meritFunction/finiteDiffVector/derivativeMethod/maxIter/maxFunEvals/tolCon/tolF/tolGrad/maxVarStepSize/QPMethod/display/maxElasticWeight`，即 Yukon 的全部运行选项。
- **`YukonOutput.hpp`**：`OutputData { Integer iter; Integer fevals; }`（`:38-44`）。
- **`YukonOptimizerFactory`**：`Gmat::SOLVER` 工厂，creatable `"Yukon"`（`.cpp:88`），`CreateSolver` 对 `"Yukon"` 返回 `new Yukonad(withName)`（`:68-69`）。
- **`GmatPluginFunctions.cpp`**：注册 1 个工厂。

## 三、关键设计模式与数据流

### 3.1 插件四要素的统一骨架

本章 13 个插件与 [第13章](CH13-plugins-a.md) 共用同一骨架：`*_defs.hpp`（导出宏）→ `GmatPluginFunctions.cpp`（`GetFactoryCount`/`GetFactoryPointer`/`SetMessageReceiver` 三 C 函数）→ 若干 `Factory` 派生（creatables 列表 + `CreateXxx` 分派）→ 业务类。差异只在业务层：

| 插件 | Factory 数 | creatable 对象 | 宿主对象类型 |
|------|-----------|----------------|--------------|
| PythonInterface | 1 | `CallPythonFunction` | `Gmat::COMMAND` |
| MatlabInterface | 3~4 | `MatlabInterface`/`CallMatlabFunction`/`MatlabFunction`/（`MatlabWorkspace`）+ `MatWriterMaker` | INTERFACE/COMMAND/FUNCTION/SUBSCRIBER + DataWriter |
| PolyhedronGravity | 2 | `PolyhedronGravityModel`/`SurfaceHeight` | PHYSICAL_MODEL/PARAMETER |
| TLEPropagator | 1 | `SPICESGP4` | PROPAGATOR |
| Msise00 | 1 | `NRLMSISE00` | ATMOSPHERE |
| ProductionPropagator | 1 | `PrinceDormand853` | PROPAGATOR |
| Station | 1 | `GroundStation`（注册新类型） | SPACE_POINT |
| ThrustFile | 4 | 命令 2 + 读者 2 + 参数 3 + 空壳 | COMMAND/DATA_FILE/PARAMETER |
| SaveCommand | 1 | `Save` | COMMAND |
| ScriptTools | 1 | `CommandEcho` | COMMAND |
| NewParameter | 1 | 11 个参数 | PARAMETER |
| OVtoOFI | 2 | `OrbitView`(覆写)/`OpenFramesView`(覆写) | SUBSCRIBER |
| YukonOptimizer | 1 | `Yukon` | SOLVER |

### 3.2 跨语言桥接：两种范式对比

**MATLAB（Engine API）**：GMAT 进程内嵌 MATLAB 引擎（`engOpen/engEvalString/engPutVariable/engGetVariable`），数据以 `mxArray` 共享，`PutRealArray` 显式做行主序→列主序转置；错误经 `try/catch` + `lasterr` 捕获。反向通道用 wxIPC（`gmat_mex`）让 MATLAB 主动连 GMAT。**Python（C-API）**：GMAT 进程内嵌 CPython（`Py_Initialize/PyImport_Import/PyObject_CallObject`），参数用 `std::variant<monostate, Real, string, Rmatrix>` 桥接，tuple/list 递归转换；stdout 用 `StringIO` 重定向回 GMAT 消息窗。两者共同点：解释器都是单例、引用计数管理 `Py_DECREF/mxDestroyArray`、错误信息回传 GMAT 异常体系。

### 3.3 多面体重力：Werner-Scheeres 公式的数据流

```
bodyShapeFilename（.txt: 顶点表+面表）
        │ LoadBodyShape()（下标 1→0 基）
        ▼
PolyhedronBody: verticesList / facesList
        │ FaceNormals() / Incenters() / Edges() / EdgeAttachments()
        ▼
PolyhedronGravityModel::Calculation():
    r_惯 = D·r_体（CalculateTransformationMatrix，含 Ddot）
    边项: Ee = na·na12ᵀ + nb·nb21ᵀ,  Le = ln((r1+r2+e)/(r1+r2-e))
    面项: Ff = nf·nfᵀ,  ωf = 2·atan2(...)（立体角，sumWf）
    xdot = -Gρ·(ΣEe·re·Le − ΣFf·rf·ωf)
    A   = 状态转移矩阵（数值/解析）
        │
        ▼
GetDerivatives → ODEModel 加速度；GetSolidAngle/GetAltitude → SurfaceHeight 参数
```

### 3.4 TLE 传播：文件 → CSPICE → 航天器

```
TLE 文件（EphemerisName） + 航天器 Id
        │ TLEReader::GetTLEData（按名/NORAD 号匹配，剥 \r）
        ▼
TLEData（tleLines[3]）
        │ TLEReader::ParseForSpice → getelm_c → secFromJ2k + elements[10]
        ▼
SPICEPropagator::PropObject::Initialize：
    校验 69 字符/根数范围/校验和 → 历元转换（UTCMJD→A1MJD）→ inputs[32]
        │ spke10_（SPICE v66，内部 Vallado 2006 SGP4）
        ▼
初始/后续状态 → Spacecraft X/Y/Z/VX/VY/VZ；Step() 用 timeFromEpoch 累积推进
```

### 3.5 瞬态力注册：BeginFileThrust / EndFileThrust 的运行时装配

```
脚本: BeginFileThrust THFObject {satNames}
        │ Initialize(): 解析 ThrustHistoryFile → GetForce() 得 FileThrust
        │ SetTransientForces(transientForces)  → 把 FileThrust 加入沙箱瞬态力表
        ▼
Propagate: ODEModel 每个导数调用 → FileThrust::GetDerivatives
        （段定位 → 插值 → 角旋转 → 单位换算 → 质量流）
        ▼
脚本: EndFileThrust → DeactivateSegments + 从瞬态力表移除
```

### 3.6 参数插件的"RefData + 参数基类"多重继承

`NewParameterPlugin`/`ThrustFilePlugin`/`PolyhedronGravityPlugin` 共用同一模式：参数类多重继承"GMAT 参数基类（`RealVar`/`StringVar`/`Rvec3Var`）+ 数据层（`RefData` 派生）"。数据层负责解析引用对象（Spacecraft/ODEModel/Solver/ThrustSegment）并在运行时取数；参数基类负责脚本序列化与求值入口（`Evaluate()` → `EvaluateReal()` → `DataLayer::GetXxx(typeName)`）。工厂的 `GetListOfCreatableObjects` 用"构造即注册"让参数提前进入 `ParameterInfo`，供 GUI 使用。

### 3.7 SQP 优化器的四层结构

```
Yukonad（InternalOptimizer 状态机）── 参数/目标/约束/容差
        │ AdvanceState: RunNominal → RunPerturbation（Gradient/Jacobian）
        ▼
GmatProblemInterface（YukonUserProblem 实现）── 从 GMAT 数据取 cost/约束/梯度
        ▼
Yukon（SQP 主循环）：ComputeSearchDirection → MinQP → 线搜索 → BFGS → 收敛判定
        │（不可行时 PrepareElasticMode 加弹性变量）
        ▼
MinQP（活动集 QP）：Phase I 求可行点 → 零空间法解 KKT → Hot Start 活动集
```

### 3.8 工厂覆写（OVtoOFI）与 DataWriter 注册（MatWriter）

`OVtoOFIFactory` 的 `overrides` 列表让它在 `OrbitView`/`Enhanced3DView`/`OpenGLPlot` 的类型名下"截胡"创建请求（[第4章](CH04-executive-factory.md) 的覆写机制）；`MatWriterMaker` 则走独立的 `DataWriterInterface::RegisterWriterMaker` 注册（DataWriter 不可脚本化，不属 `Factory` 体系）。两者都是"插件扩展宿主能力"的旁路通道。

## 四、文件清单附录

### 表 14-1 MatlabInterfacePlugin（37 代码文件）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/base/command/CallMatlabFunction.hpp/.cpp | 调用 .m 函数的命令 | `CallMatlabFunction::FormEvalString/ExecuteMatlabFunction/SendInParam` |
| src/base/factory/CallMatlabFunctionFactory.hpp/.cpp | 命令工厂 | `CreateCommand`→`CallMatlabFunction` |
| src/base/factory/MatlabFunctionFactory.hpp/.cpp | 函数工厂 | `CreateFunction`→`MatlabFunction` |
| src/base/factory/MatlabInterfaceFactory.hpp/.cpp | 接口工厂（单例） | `CreateInterface`→`MatlabInterface::Instance()` |
| src/base/factory/MatlabWorkspaceFactory.hpp/.cpp | 订阅者工厂 | `CreateSubscriber`→`MatlabWorkspace` |
| src/base/function/MatlabFunction.hpp/.cpp | .m 函数对象 | `SetMatlabFunctionPath`（相对路径解析） |
| src/base/include/matlabinterface_defs.hpp | 导出宏 | `MATLAB_API` |
| src/base/interface/MatlabInterface.hpp/.cpp | MATLAB Engine 单例门面 | `Open/Close/PutRealArray/GetRealArray/RunMatlabString` |
| src/base/matwriter/MatData.hpp/.cpp | .mat 数据抽象基类 | `WriteData`（纯虚） |
| src/base/matwriter/MatWriter.hpp/.cpp | .mat 写出器 | `OpenFile/WriteData/SetMxArray` |
| src/base/matwriter/MatWriterMaker.hpp/.cpp | DataWriter 制造器单例 | `CreateDataWriter`→`MatWriter` |
| src/base/matwriter/RealMatData.hpp/.cpp | 实数容器 | `AddData/WriteData` |
| src/base/matwriter/StringMatData.hpp/.cpp | 字符串容器 | `AddData/WriteData` |
| src/base/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | `GetFactoryCount/GetFactoryPointer/SetMessageReceiver` |
| src/base/subscriber/MatlabWorkspace.hpp/.cpp | 参数推送订阅者 | `Distribute(const Real*, len)` |
| src/matlab/gmat_mex/mex-file/SendGMAT.cpp | MEX 客户端入口 | `mexFunction/SendGMAT`（Poke/Advise/Request/Execute） |
| src/matlab/gmat_mex/src/ipcsetup.h | IPC 常量 | `IPC_SERVICE="4242"`、`IPC_TOPIC` |
| src/matlab/gmat_mex/src/MatlabClient.hpp/.cpp | wxClient 客户端 | `Connect/Disconnect/OnMakeConnection` |
| src/matlab/gmat_mex/src/MatlabConnection.hpp/.cpp | wxConnection 消息语义 | `Execute/Request/Poke/OnAdvise` |
| src/matlab/gmat_mex/test/TestDriver.cpp | IPC 测试驱动 | `main` |

非代码：src/.gitignore、src/base/CMakeLists.txt（`_SETUPPLUGIN` 装配）。

### 表 14-2 Msise00Plugin（12 代码文件）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/base/atmosphere/NRLMsise00Atmosphere.hpp/.cpp | MSISE-00 大气模型适配 | `Density()`（调 `gtd7_`，cg/cm³→kg/m³） |
| src/base/atmosphere/nrlmsise00_sub.c | 模型内核（f2c 翻译） | `gtd7_`(:884)、`gtd7d_`(:1264)、`densu_`(:2877)、`globe7_`(:2288) |
| src/base/atmosphere/nrlmsise00_sub.f/.for | Fortran 原始源 | `gtd7` 等 |
| src/base/atmosphere/nrlmsise00_sub_v2.for | Fortran 修订版源 | `gtd7` 等 |
| src/base/atmosphere/nrlmsise00_sub.h | 空头文件（guard） | — |
| src/base/factory/NRLMsise00Factory.hpp/.cpp | 大气工厂 | `CreateAtmosphereModel`→`NRLMSISE00` |
| src/base/include/nrlmsise00_defs.hpp | 导出宏 | `NRLMSISE00_API` |
| src/base/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | 1 个工厂 |

非代码：src/.gitignore、src/base/CMakeLists.txt。

### 表 14-3 NewParameterPlugin（29 代码文件）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/base/factory/NewParameterFactory.hpp/.cpp | 参数工厂 | `CreateParameter`（11 类）、构造即注册 |
| src/base/include/newparameter_defs.hpp | 导出宏 | `NEW_PARAMETER_API` |
| src/base/parameter/AtmosDensity.hpp/.cpp | 大气密度参数 | `AtmosDensity::Evaluate`(:122) |
| src/base/parameter/FMAcceleration.hpp/.cpp | 加速度模/分量参数 | `FMAcceleration::Evaluate`(:123)、`FMAccelerationX/Y/Z` |
| src/base/parameter/FMDensity.hpp/.cpp | 力模型密度参数 | `FMDensity::Evaluate`(:120) |
| src/base/parameter/OdeData.hpp/.cpp | ODE 数据层 | `GetOdeReal/GetOdeRvec3/InitializeRefObjects` |
| src/base/parameter/OdeReal.hpp/.cpp | 实数 ODE 参数基类 | `EvaluateReal()` |
| src/base/parameter/OdeRvec3.hpp/.cpp | 向量 ODE 参数基类 | `EvaluateRvector()` |
| src/base/parameter/SolverData.hpp/.cpp | 求解器数据层 | `GetSolverReal/GetSolverString`（状态映射） |
| src/base/parameter/SolverReal.hpp/.cpp | 求解器实数参数 | `EvaluateReal()`、外部克隆 |
| src/base/parameter/SolverState.hpp/.cpp | 求解器数值状态 | `SolverState::Evaluate`(:105) |
| src/base/parameter/SolverStatus.hpp/.cpp | 求解器字符串状态 | `SolverStatus::Evaluate`(:104) |
| src/base/parameter/SolverString.hpp/.cpp | 求解器字符串参数 | `EvaluateString()` |
| src/base/parameter/Torque.hpp/.cpp | 四种力矩参数 | `BurnTorque/GravityTorque/SRPTorque/TotalTorque` |
| src/base/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | 1 个工厂 |

非代码：src/.gitignore、src/base/CMakeLists.txt。

### 表 14-4 OVtoOFI（9 代码文件）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/base/factory/InvisOpenFramesViewFactory.hpp/.cpp | 覆写 `OpenFramesView` | `CreateObject`→`InvisOpenFramesView` |
| src/base/factory/OVtoOFIFactory.hpp/.cpp | 覆写 OrbitView 系 | `CreateSubscriber`→`OVtoOFI` |
| src/base/include/OVtoOFI_defs.hpp | 导出宏 | `OVTOOFI_API` |
| src/base/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | 2 个工厂 |
| src/base/subscriber/OVtoOFI.hpp/.cpp | 映射主类 | `OVtoOFI`（参数转发）、`InvisOpenFramesView`（无脚本输出） |

非代码：src/.gitginore（文件名拼写即如此）、src/base/CMakeLists.txt。

### 表 14-5 PolyhedronGravityPlugin（17 代码文件）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/base/factory/GravityParameterFactory.hpp/.cpp | 参数工厂 | `SurfaceHeight`、构造即注册 |
| src/base/factory/PolyhedronGravityModelFactory.hpp/.cpp | 力模型工厂 | `CreatePhysicalModel`→`PolyhedronGravityModel` |
| src/base/gravitymodel/PolyhedronBody.hpp/.cpp | 多面体几何 | `LoadBodyShape/Incenters/Edges/EdgeAttachments` |
| src/base/gravitymodel/PolyhedronGravityModel.hpp/.cpp | 多面体引力 | `Calculation`(:424)、`GetSolidAngle`(:1085)、`GetAltitude`(:1169) |
| src/base/include/polyhedrongravitymodel_defs.hpp | 导出宏 | `POLYHEDRONGRAVITYMODEL_API` |
| src/base/parameter/GravData.hpp/.cpp | 重力数据层 | `GetGravReal/InitializeRefObjects`、`ModelType` |
| src/base/parameter/GravReal.hpp/.cpp | 实数重力参数 | `EvaluateReal()` |
| src/base/parameter/SurfaceHeight.hpp/.cpp | 表面高度参数 | `SurfaceHeight::Evaluate` |
| src/base/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | 2 个工厂 |

非代码：src/.gitignore、src/base/CMakeLists.txt。

### 表 14-6 ProductionPropagatorPlugin（7 代码文件）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/base/factory/ProductionPropagatorFactory.hpp/.cpp | 传播器工厂 | `CreatePropagator`→`PrinceDormand853` |
| src/base/include/ProductionPropagatorDefs.hpp | 导出宏 | `PRODUCTIONPROPAGATOR_API` |
| src/base/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | 1 个工厂 |
| src/base/propagator/PrinceDormand853.hpp/.cpp | DP8(7) 积分器 | `SetCoefficients()`（ai/bij/cj/ee） |

非代码：src/.gitignore、src/base/CMakeLists.txt。

### 表 14-7 PythonInterfacePlugin（11 代码文件）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/base/command/CallPythonFunction.hpp/.cpp | Python 调用命令 | `Execute`(:476)、`ConvertToPyObject/ConvertFromPyObject`、`PyIfVariant` |
| src/base/factory/PythonCommandFactory.hpp/.cpp | 命令工厂 | `CreateCommand`→`CallPythonFunction` |
| src/base/function/PythonModule.hpp/.cpp | 占位（空文件） | — |
| src/base/include/pythoninterface_defs.hpp | 导出宏 | `PYTHON_API` |
| src/base/interface/PythonInterface.hpp/.cpp | Python 解释器单例 | `PyInitialize/PyFunctionWrapper/PyExternalFunctionWrapper` |
| src/base/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | 1 个工厂 |

非代码：src/.gitignore、src/base/.gitignore、src/base/CMakeLists.txt。

### 表 14-8 SaveCommandPlugin（7 代码文件）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/base/command/Save.hpp/.cpp | 对象存档命令 | `Save::Execute`(:501)、`WriteObject`(:724)、`OBJECT_NAMES` |
| src/base/factory/SaveCommandFactory.hpp/.cpp | 命令工厂 | `CreateCommand`→`Save` |
| src/base/include/SaveCommandDefs.hpp | 导出宏 | `SAVECOMMAND_API` |
| src/base/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | 1 个工厂 |

非代码：src/.gitignore、src/base/.gitignore、src/base/CMakeLists.txt。

### 表 14-9 ScriptToolsPlugin（7 代码文件）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/base/command/CommandEcho.hpp/.cpp | 命令回显开关 | `Execute`(:173)→`SetCommandEchoMode`、`InterpretAction`(:188) |
| src/base/factory/CommandEchoFactory.hpp/.cpp | 命令工厂 | `CreateCommand`→`CommandEcho` |
| src/base/include/ScriptToolsDefs.hpp | 导出宏 | `ScriptTools_API` |
| src/base/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | 1 个工厂 |

非代码：src/base/CMakeLists.txt。

### 表 14-10 StationPlugin（11 代码文件）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/base/factory/StationFactory.hpp/.cpp | 地面站工厂 | `RegisterType(GROUND_STATION)`、`CreateSpacePoint` |
| src/base/include/StationDefs.hpp | 导出宏 | `STATION_API` |
| src/base/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | 1 个工厂 |
| src/base/station/GroundStation.hpp/.cpp | 地面站对象 | `Initialize`(:1293)、`IsValidElevationAngle`(:1466)、误差模型/硬件管理 |
| swig/station.i | SWIG 模块 | `%module station` |
| swig/station.swg | SWIG 映射 | `ARRAYRETURN`、`DOWNCAST(GroundStation,GmatBase)` |
| swig/station_py.i | Python 绑定 | `%module station_py` |
| swig/StationAPI.hpp | 包装头 | include 汇总 |

非代码：src/.gitignore、src/base/CMakeLists.txt、swig/CMakeLists.txt。

### 表 14-11 ThrustFilePlugin（31 代码文件）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/base/command/BeginFileThrust.hpp/.cpp | 开始文件推力 | `SetTransientForces/Initialize/Execute` |
| src/base/command/EndFileThrust.hpp/.cpp | 结束文件推力 | `Execute`（停用段、移除瞬态力） |
| src/base/datareader/ThfDataSegment.hpp/.cpp | 段数据结构 | `ThrustPoint`、`InterpolationType`、profile |
| src/base/datareader/ThrustHistoryFile.hpp/.cpp | THF 文件读取器 | `ReadData`(:724)、`ActivateSegments`(:915)、`ReadThrustProfile`(:1214) |
| src/base/datareader/ThrustSegment.hpp/.cpp | 段对象（可估计） | `SetDataSegment`(:1703)、`GetStmIndex`(:1753) |
| src/base/factory/ThrustFileCommandFactory.hpp/.cpp | 命令工厂 | `BeginFileThrust/EndFileThrust` |
| src/base/factory/ThrustFileForceFactory.hpp/.cpp | 空壳工厂 | 恒 NULL |
| src/base/factory/ThrustFileReaderFactory.hpp/.cpp | 数据文件工厂 | `ThrustHistoryFile/ThrustSegment` |
| src/base/factory/ThrustSegmentParameterFactory.hpp/.cpp | 参数工厂 | `ThrustScaleFactor/ThrustAngle1/2` |
| src/base/forcemodel/FileThrust.hpp/.cpp | 文件推力力模型 | `GetDerivatives`(:1183)、`ComputeAccelerationMassFlow`、插值/角旋转 |
| src/base/include/ThrustFileDefs.hpp | 导出宏 | `THRUSTFILE_API` |
| src/base/parameter/ThrustSegmentData.hpp/.cpp | 段参数数据层 | `GetReal/SetReal/GetRvector` |
| src/base/parameter/ThrustSegmentParameters.hpp/.cpp | 10 个段参数类 | `ThrustSegmentScaleFactor/TSFEpsilon/ThrustAngle1/2`… |
| src/base/parameter/ThrustSegmentReal.hpp/.cpp | 实数段参数基类 | `EvaluateReal()` |
| src/base/parameter/ThrustSegmentRvector.hpp/.cpp | 向量段参数基类 | `EvaluateRvector()`、`IsOptionalField` |
| src/base/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | 4 个工厂 |

非代码：src/base/CMakeLists.txt。

### 表 14-12 TLEPropagatorPlugin（主要代码文件，数据/文档见说明）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/factory/TlePropFactory.hpp/.cpp | 传播器工厂 | `CreatePropagator`→`SPICESGP4` |
| src/include/tleprop_defs.hpp | 导出宏 | `TLE_PROPAGATOR_API` |
| src/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | 1 个工厂 |
| src/propagator/SGP4Propagator.hpp/.cpp | 占位壳 | `Propagator("SGP4")` |
| src/propagator/SPICEPropagator.hpp/.cpp | TLE 传播器（spke10） | `PropObject::Initialize`(:176)、`Step`(:1056)、参数 J2…AE |
| src/propagator/TLEData.hpp/.cpp | TLE 数据载体 | `tleLines[3]/secFromJ2k/elements[10]` |
| src/propagator/TLEReader.hpp/.cpp | TLE 解析 | `GetTLEData`(:46)、`ParseForSpice`(:143，`getelm_c`) |
| ValladoCode/SGP4/SGP4/SGP4.cpp/.h | Vallado 参考 SGP4 | `sgp4init`(:1358)、`getgravconst`(:2068)、`twoline2rv`(:2165)、`gstime`(:2461) |
| ValladoCode/SGP4DC/SGP4DC/SGP4DC.cpp/.h | 深空 SGP4 变体 | `SGP4DC`（irez 深空分支） |
| ValladoCode/TestSGP4/TestSGP4mod.cpp | 参考验证程序 | `TestSGP4mod` |
| ValladoCode/TestSGP4/TestSGP4/TestSGP4.cpp | 参考验证程序 | `TestSGP4` |
| ValladoCode/TestSGP4/TestSGP4/stdafx.cpp/.h | 预编译头 | — |
| ValladoCode/TestSGP4/TestSGP4/targetver.h | 目标版本宏 | — |

数据/文档类（目录级覆盖）：`TLE/Active_Nov-09-2019.txt`（示例 TLE）；`samples/NeedTlePropagator/`（6 个示例脚本，含 `PropLightsail2.script`，脚本类型名 `TLE` 映射到 `SPICESGP4`）；`test/`（4 个回归脚本、TLE 输入、truth 输出、Orekit 生成器 py）；`doc/`（Sphinx rst + License）；`ValladoCode/*.sln/.vcxproj/.suo/.rc/.ico`（Windows 工程与资源，不分析）；`test/truth/*.truth`、`TestSGP4/*.e`（参考输出，不分析）。

### 表 14-13 YukonOptimizerPlugin（19 代码文件）

| 相对路径 | 职责 | 关键类/函数 |
|----------|------|-------------|
| src/base/factory/YukonOptimizerFactory.hpp/.cpp | 求解器工厂 | `CreateSolver`→`Yukon`（`Yukonad`） |
| src/base/include/yukon_defs.hpp | 导出宏 | `YUKON_API` |
| src/base/plugin/GmatPluginFunctions.hpp/.cpp | 插件入口 | 1 个工厂 |
| src/base/solver/GmatProblemInterface.hpp/.cpp | GMAT→NLP 适配 | `GetNLPInfo`(:58)、`GetBoundsInfo`(:94)、`EvaluateCostFunc`(:151) |
| src/base/solver/MinQP.hpp/.cpp | 活动集 QP 求解器 | `Optimize`(:180)、`SetUpPhaseI`(:1630)、退出码约定 |
| src/base/solver/NLPFunctionGenerator.hpp/.cpp | NLP 函数封装 | `EvaluateAllNLPFuncJac`、弹性模式 V/W |
| src/base/solver/Yukon.hpp/.cpp | SQP 主循环 | `Optimize`(:586)、`ComputeSearchDirection`(:1216)、`UpdateHessian`(:1375) |
| src/base/solver/Yukonad.hpp/.cpp | 求解器状态机适配 | `AdvanceState`(:907)、`RunNominal`(:1234)、`RunPerturbation`(:1251) |
| src/base/solver/YukonOptions.hpp | 选项结构 | `OptionsList` |
| src/base/solver/YukonOutput.hpp | 输出结构 | `OutputData{iter,fevals}` |
| src/base/solver/YukonUserProblem.hpp/.cpp | 用户问题抽象 | 9 个纯虚接口、`HandleOneSidedVarBounds`(:58) |

非代码：src/base/CMakeLists.txt。
