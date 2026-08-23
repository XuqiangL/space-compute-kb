# 第8章 参数、函数、求解器、订阅者与其余 base 子系统

本章负责 `src/base/` 下十个子目录的全部 `.hpp/.cpp` 源码文件（以 glob 实测清单为准）：`parameter`（153 个）、`function`（40 个）、`solver`（21 个）、`subscriber`（46 个）、`coordsystem`（76 个）、`interface`（8 个）、`api`（10 个）、`spice`（18 个）、`asset`（6 个）、`configs`（8 个），共 **386 个代码文件**。这些子系统共同构成 GMAT 引擎的"数据面"：参数系统把「对象.字段」抽象为可求值的 `Parameter`；函数系统提供脚本函数（`GmatFunction`/内建函数）的执行框架；求解器以状态机驱动微分改正/优化迭代；订阅者消费 `Publisher` 发布的数据流并输出报告文件、历表与图形；坐标系系统完成状态向量在任意轴系间的旋转+平移；`interface`/`api`/`spice`/`asset`/`configs` 分别提供外部接口、API 层、SPICE 内核桥接、地面站资产与配置管理。依赖的底层基类（`GmatBase`、`ElementWrapper`、`SpacePoint`、`GmatState` 等）见 [第2章](CH02-foundation.md)，工厂与执行层见 [第4章](CH04-executive-factory.md)，命令层见 [第5章](CH05-command.md)。

> 三个需要提前澄清的"名实不符"（已用 glob/grep 全库确认）：
> 1. **`CalculatedParameter` 在本代码库中不存在**：全库仅 `src/base/factory/Factory.cpp:312-336` 有一处被注释掉的 `CreateCalculatedParameter` 声明，无任何实现文件与派生类。本章按实际代码讲解参数族，不再展开该符号。
> 2. **`GmatFunction` 没有独立文件**：`src/base/function/` 下无 `GmatFunction.hpp/.cpp`；脚本函数由 `UserDefinedFunction` 承载（其头注释明确 "All user defined function classes such as GmatFunction are derived from this class"，`UserDefinedFunction.hpp:30`），工厂以类型串 `"GmatFunction"` 创建它（`FunctionManager.cpp:298` 等按 `GetTypeName() == "GmatFunction"` 分支处理）。
> 3. **`ElementWrapper` 基类位于 `src/base/foundation/`**（[第2章](CH02-foundation.md) 已讲），本章 `parameter` 目录只含它的 11 个具体子类，`interface` 目录与"文本转换链"无直接关系（那是 MATLAB/Socket 接口）。

## 一、本章目录树

```
src/base/
├── parameter/                        （153 个文件，本章第一大目录）
│   ├── Parameter.hpp / .cpp          参数抽象基类（Evaluate 虚函数族）
│   ├── paramdefs.hpp                 参数 typedef（ParameterPtrArray / StringParamPtrMap）
│   ├── ParameterInfo.hpp / .cpp      参数注册表单例（类型名 → 属性）
│   ├── ParameterDatabase.hpp / .cpp  参数数据库（名字 → Parameter* 映射）
│   ├── ParameterException.hpp        异常（仅头文件）
│   ├── ParameterDatabaseException.hpp 异常（仅头文件）
│   ├── RealVar.hpp / .cpp            Real 参数中间基类（USER_PARAM 数值变量之祖）
│   ├── Variable.hpp / .cpp           脚本变量 Variable
│   ├── StringVar.hpp / .cpp          字符串变量
│   ├── Array.hpp / .cpp              二维数组变量 Array
│   ├── RvectorVar / Rmat33Var / Rmat66Var / Rvec3Var / Rvec6Var  向量/矩阵变量
│   ├── RefData.hpp / .cpp            引用数据基类（解析对象引用，纯虚 ValidateRefObjects）
│   ├── OrbitData / SpacecraftData / TimeData / AttitudeData /
│   │   BplaneData / BurnData / EnvData / PlanetData              八大数据实现
│   ├── OrbitReal / OrbitRvec6 / OrbitRmat33 / OrbitRmat66 / OrbitTime
│   │   RealVar 与 OrbitData 多继承的轨道参数装配层
│   ├── AttitudeReal / BallisticMassReal / BurnReal / BplaneReal /
│   │   EnvReal / HardwareReal / HardwareRvector / HardwareString /
│   │   PlanetReal / TimeReal / TimeString                        按对象域装配层
│   ├── KeplerianParameters / CartesianParameters / SphericalParameters /
│   │   EquinoctialParameters / ModEquinoctialParameters / AlternateEquinoctialParameters /
│   │   DelaunayParameters / BrouwerMeanLongParameters / BrouwerMeanShortParameters /
│   │   PlanetodeticParameters / AngularParameters / OrbitalParameters /
│   │   BplaneParameters / IncomingAsymptoteParameters / OutgoingAsymptoteParameters /
│   │   TimeParameters / AttitudeParameters / PlanetParameters /
│   │   BallisticMassParameters / HardwareParameters / BurnParameters /
│   │   OrbitStmParameters / OrbitCovarianceParameters               23 个叶子参数族
│   ├── NumberWrapper / StringWrapper / BooleanWrapper / OnOffWrapper /
│   │   ObjectWrapper / ParameterWrapper / VariableWrapper /
│   │   ArrayWrapper / ArrayElementWrapper / StringObjectWrapper /
│   │   ObjectPropertyWrapper                                        11 个 ElementWrapper 子类
│   └── ExpressionParser.hpp / .cpp  简单数学表达式解析器（仅旧 Variable 用）
├── function/                        （40 个文件）
│   ├── Function.hpp / .cpp          函数抽象基类
│   ├── ObjectManagedFunction.hpp / .cpp  对象管理函数中间基类
│   ├── BuiltinGmatFunction.hpp / .cpp    内建函数基类
│   ├── UserDefinedFunction.hpp / .cpp    用户脚本函数（GmatFunction 载体）
│   ├── FunctionManager.hpp / .cpp   函数调用管理器（FOS/LOS/GOS 与调用栈）
│   ├── FunctionException.hpp / .cpp 异常
│   └── Angle / ConvertTime / GetEphemStates / GetLastState / Num2str /
│       Pause / QuaternionProduct / QuaternionRotation / QuaternionToDCM /
│       RotationMatrix / SetSeed / Sign / Str2num / SystemTime      14 个内建函数
├── solver/                          （21 个文件）
│   ├── Solver.hpp / .cpp            求解器基类（状态机 SolverState/MachineMode）
│   ├── DifferentialCorrector.hpp / .cpp  微分改正器（Newton-Raphson/Broyden）
│   ├── Optimizer.hpp / .cpp         优化器基类（纯虚 Optimize）
│   ├── InternalOptimizer.hpp / .cpp 内嵌优化器接口
│   ├── ExternalOptimizer.hpp / .cpp 外部优化器接口（MATLAB）
│   ├── DerivativeModel.hpp / .cpp   导数模型基类（前向/中心/后向差分）
│   ├── Jacobian.hpp / .cpp          雅可比计算
│   ├── Gradient.hpp / .cpp          梯度计算
│   ├── LineSearch.hpp / .cpp        线搜索（未实现占位）
│   ├── ISolverListener.hpp / .cpp   求解器进度监听接口
│   └── SolverException.hpp          异常（仅头文件）
├── subscriber/                      （46 个文件）
│   ├── Subscriber.hpp / .cpp        订阅者基类（ReceiveData/Distribute 管道）
│   ├── ReportFile.hpp / .cpp        报告文件
│   ├── TextEphemFile.hpp / .cpp     文本历表文件（ReportFile 子类）
│   ├── EphemerisFile.hpp / .cpp     历表文件基类（子类选择 Writer）
│   ├── EphemerisWriter.hpp / .cpp   历表写入器基类
│   ├── EphemWriterWithInterpolator.hpp / .cpp  带插值的写入器中间类
│   ├── EphemWriterCCSDS / EphemWriterCode500 / EphemWriterSPK /
│   │   EphemWriterSTK / AttitudeWriterCK                          5 个具体写入器
│   ├── EphemManager.hpp / .cpp      历表管理器（GroundStation 用）
│   ├── XyPlot.hpp / .cpp            XY 曲线图
│   ├── OrbitPlot.hpp / .cpp         轨道图中间基类
│   ├── OrbitView.hpp / .cpp         3D 轨道视图
│   ├── GroundTrackPlot.hpp / .cpp   地面轨迹图
│   ├── OpenGlPlot.hpp / .cpp        OpenGL 图（旧版 OrbitView）
│   ├── GroundTrack.hpp / .cpp       地面轨迹数据订阅者
│   ├── OwnedPlot.hpp / .cpp         求解器自绘图
│   ├── MessageWindow.hpp / .cpp     消息窗口
│   ├── DynamicDataDisplay.hpp / .cpp / DynamicDataInterface.hpp/.cpp / DynamicDataStruct.hpp
│   │   动态数据显示（Interface 两文件为 0 字节占位）
│   └── SubscriberException.hpp      异常（仅头文件）
├── coordsystem/                     （76 个文件）
│   ├── CoordinateBase.hpp / .cpp    坐标系/轴系公共基类
│   ├── CoordinateSystem.hpp / .cpp  坐标系（Origin + AxisSystem 组合）
│   ├── AxisSystem.hpp / .cpp        轴系基类（FK5 归算：岁差/章动/恒星时/极移）
│   ├── InertialAxes.hpp / .cpp      惯性轴系基类
│   ├── MJ2000EqAxes / MJ2000EcAxes / ICRFAxes / TOEEqAxes / TOEEcAxes /
│   │   MOEEqAxes / MOEEcAxes / BodyInertialAxes                     8 个惯性叶子
│   ├── DynamicAxes.hpp / .cpp       动力轴系基类
│   ├── MeanOfDateAxes.hpp/.cpp + MODEqAxes + MODEcAxes              平赤道/平黄道
│   ├── TrueOfDateAxes.hpp/.cpp + TODEqAxes + TODEcAxes + TEMEAxes   真赤道/真黄道/真赤道平春分点
│   ├── BodyFixedAxes / EquatorAxes / TopocentricAxes /
│   │   ObjectReferencedAxes / LocalAlignedConstrainedAxes           动力轴叶子
│   ├── BodySpinSunAxes / GeocentricSolarEclipticAxes /
│   │   GeocentricSolarMagneticAxes                                  三轴参考类动力轴
│   ├── ITRFAxes / SpiceAxes                                         地固/SPICE 轴
│   ├── IAUFile / ICRFFile / ItrfCoefficientsFile                    数据文件读取（单例）
│   ├── CoordinateConverter / CoordinateTransformation /
│   │   CoordinateTranslation / TransformUtil                         转换工具
│   └── CoordinateSystemException.hpp / .cpp                          异常
├── interface/                      （8 个文件）
│   ├── Interface.hpp / .cpp        外部接口基类（Open/Close）
│   ├── GmatInterface.hpp / .cpp    MATLAB 接口单例（字符串流 + 回调）
│   ├── SocketServer.hpp / .cpp     套接字服务器（3000 端口）
│   └── InterfaceException.hpp / .cpp 异常
├── api/                            （10 个文件）
│   ├── APIFunctions.hpp / .cpp     顶层 API 函数（Help/Construct/Execute/RunScript…）
│   ├── ApiClass.hpp / .cpp         API 基类（近空）
│   ├── APIMessageReceiver.hpp / .cpp  消息接收器单例（日志/队列）
│   ├── HelpSystem.hpp / .cpp       帮助系统单例
│   └── APIException.hpp / .cpp     异常
├── spice/                          （18 个文件，需 __USE_SPICE__ 编译）
│   ├── SpiceInterface.hpp / .cpp   CSPICE 桥接基类（加载/卸载内核、时间换算）
│   ├── SpiceKernelReader.hpp / .cpp  内核读取基类
│   ├── SpiceOrbitKernelReader / SpiceAttitudeKernelReader           读取器
│   ├── SpiceKernelWriter.hpp / .cpp  内核写入基类
│   ├── SpiceOrbitKernelWriter / SpiceAttitudeKernelWriter /
│   │   SpiceFrameKernelWriter / SpiceSCClockKernelWriter            写入器
├── asset/                          （6 个文件）
│   ├── BodyFixedPoint.hpp / .cpp   体固连点基类（GroundStation 之祖）
│   ├── GroundstationInterface.hpp / .cpp  地面站接口（纯虚）
│   └── AssetException.hpp / .cpp   异常
└── configs/                        （8 个文件）
    ├── ConfigManager.hpp / .cpp    配置管理器单例（对象注册/克隆/重命名）
    ├── ItemManager.hpp / .cpp      条目管理器基类（纯虚析构）
    ├── PluginItemManager.hpp / .cpp 插件条目管理器单例
    └── ConfigManagerException.hpp / .cpp  异常
```

## 二、逐文件/逐类讲解

### 8.1 parameter 目录（153 个文件）

#### 8.1.1 Parameter —— 参数抽象基类（本章核心之一）

`class GMAT_API Parameter : public GmatBase`（`src/base/parameter/Parameter.hpp:76`）。它是所有「可求值参数」的根：系统参数（如 `Sat.EarthMJ2000Eq.X`）与用户参数（`Variable`、`Array`）都派生自它。与普通 `GmatBase` 对象不同，`Parameter` 的价值不在「脚本可配置字段」，而在**按需求值**：`Evaluate*()` 虚函数族把「当前时刻的对象状态」折算成参数值。

**(1) 构造与参数表。** 构造函数 13 个形参（`Parameter.cpp:102-107`）：

```cpp
// Parameter.cpp:102-107（签名）
Parameter::Parameter(const std::string &name, const std::string &typeStr,
                     GmatParam::ParameterKey key, GmatBase *owner,
                     const std::string &desc, const std::string &unit,
                     GmatParam::DepObject depObj, UnsignedInt ownerType,
                     bool isTimeParam, bool isSettable, bool isPlottable,
                     bool isReportable, UnsignedInt ownedObjType)
```

逐参数解释：`key` 区分系统参数/用户参数（`GmatParam::ParameterKey`，`Parameter.hpp:45-50`）；`owner` 是被求值对象（Spacecraft 等）；`depObj` 声明参数依赖什么对象（坐标系 `COORD_SYS`、原点 `ORIGIN`、被拥有对象 `OWNED_OBJ` 等，`Parameter.hpp:52-61`）；`isTimeParam/isSettable/isPlottable/isReportable` 供 GUI/报告/绘图系统查询能力。构造体（`Parameter.cpp:109-186`）做三件关键事：把 `Gmat::PARAMETER` 推入 `objectTypes`（类型树登记，`Parameter.cpp:110-111`）；把空格替换成下划线后作为 `instanceName`（`Parameter.cpp:126-132`）；调用 `ParameterInfo::Instance()->Add(...)` 把参数类型注册进全局注册表（`Parameter.cpp:179-181`）。末尾 `parameterCount = ParameterParamCount`（`Parameter.cpp:184`），参数 ID 从 `GmatBaseParamCount` 续接：

```cpp
// Parameter.hpp:244-254
enum
{
   OBJECT = GmatBaseParamCount,
   INITIAL_VALUE,
   EXPRESSION,
   DESCRIPTION,
   UNIT,
   DEP_OBJECT,
   COLOR,
   ParameterParamCount
};
```

`PARAMETER_TEXT`/`PARAMETER_TYPE` 静态表（`Parameter.cpp:51-73`）给出这 7 个参数的名与型（`Object` 为 OBJECT_TYPE，其余多为 STRING_TYPE，`Color` 为 UNSIGNED_INT_TYPE）。

**(2) Evaluate 虚函数族。** 这是 Parameter 最核心的协议。`Parameter.hpp:146-152` 声明按返回类型分派的求值族，基类实现全部**抛异常**（`EvaluateReal` 见 `Parameter.cpp:927-933`）：

```cpp
// Parameter.cpp:927-933
Real Parameter::EvaluateReal()
{
   throw ParameterException
      ("Parameter: EvaluateReal(): " + this->GetTypeName() + " has no "
       "implementation of EvaluateReal().\nMay be an invalid call to this "
       "function.\n");
}
```

逐行解释：这是典型的「默认拒绝」虚函数设计——基类不知道如何从 owner 求值，因此抛出 `ParameterException` 提示「无效调用」；每个叶子参数类只重写自己支持的那一个 `Evaluate*`（如 `KepSMA::Evaluate()` 只填 `mRealValue`），其余求值入口保持抛异常，把「类型与算法不匹配」的错误提前到运行期显式暴露。配套的 `GetReal/SetReal/GetRvector6/SetRvector6/...`（`Parameter.hpp:131-144`）同样是默认拒绝的取值/设值族。另有统一入口 `bool Evaluate()`（`Parameter.cpp:1087-1094`）：对 `SYSTEM_PARAM` 抛异常（要求叶子实现），对 `USER_PARAM` 返回 `false`——这是旧式无类型入口，新代码走类型化入口。

**(3) 能力查询与生命周期。** `IsSystemParameter/IsAngleParameter/IsTimeParameter/IsPlottable/IsReportable/IsSettable`（`Parameter.cpp:378-457`）、`IsCoordSysDependent/IsOriginDependent/IsOwnedObjectDependent`（`Parameter.cpp:459-494`）、`NeedCoordSystem/NeedExternalClone`（`Parameter.cpp:508-567`）构成「参数需要什么环境」的声明层：需要坐标系/太阳系/外力模型的参数重写 `SetInternalCoordSystem/SetSolarSystem/SetTransientForces`（`Parameter.cpp:1063-1074`、`1578-1593`）。引用对象协议 `AddRefObject/GetNumRefObjects/Validate`（`Parameter.cpp:1103-1146`）与 `RenameRefObject`（`Parameter.cpp:1180`）使系统参数在对象改名后能更新内部指针。`ToString()`（`Parameter.cpp:677`）输出 `名字 = 值` 文本。

**(4) 子系统参数。** `Parameter` 自身无 `Clone()`（`DEFAULT_TO_NO_CLONES`，`Parameter.hpp:205`），因为系统参数由沙箱/工厂按类型串创建，不做脚本克隆。

#### 8.1.2 注册与元数据：paramdefs / ParameterInfo / ParameterDatabase / 异常

- **`paramdefs.hpp`**（40 行）：纯 typedef 头。`ParameterPtrArray = std::vector<Parameter*>`、`StringParamPtrMap = std::map<std::string, Parameter*>`、`StringParamPtrPair = std::pair<...>`（`paramdefs.hpp:36-38`），是参数容器与 `ParameterDatabase` 的公共类型。
- **`ParameterInfo`**（`class GMAT_API ParameterInfo`，`ParameterInfo.hpp:38`）：**单例注册表**（`Instance()` 见 `ParameterInfo.hpp:43`，`theInstance` 静态成员在 `ParameterInfo.hpp:73`）。`Parameter` 构造时调用 `Add(type, ownerType, ownedObjType, name, depType, isPlottable, isReportable, isSettable, isTimeParam, desc)`（`ParameterInfo.hpp:60-64`，实现存于 8 张 map：`mDepObjMap/mOwnerTypeMap/mOwnedObjTypeMap/mIsPlottableMap/...`，`ParameterInfo.hpp:75-85`）。查询接口 `IsPlottable/IsReportable/IsSettable/IsTimeParameter/RequiresBodyFixedCS/...`（`ParameterInfo.hpp:51-58`）供 GUI 属性页、报告面板按类型名查能力，避免遍历对象。这是「类型串 → 能力位」的集中索引，与 [第2章](CH02-foundation.md) 的 `GmatBase` 参数表互补。
- **`ParameterDatabase`**（`class GMAT_API ParameterDatabase`，`ParameterDatabase.hpp:38`）：非单例容器，持有 `StringParamPtrMap *mStringParamPtrMap`（`ParameterDatabase.hpp:68`）。`Add/GetParameter/Remove/RenameParameter`（`ParameterDatabase.cpp:388/338/439/271`）按名管理 `Parameter*`。它是旧版 `Variable` 做简单表达式时的变量表（见 8.1.3），现在主要被 `ExpressionParser` 与脚本变量管理使用。
- **`ParameterException.hpp` / `ParameterDatabaseException.hpp`**：两个纯头文件，各定义一个 `class ... : public BaseException`（`ParameterException.hpp:36`、`ParameterDatabaseException.hpp:36`），无 .cpp——异常构造全部走 `BaseException` 的默认路径。

#### 8.1.3 用户变量族：RealVar / Variable / StringVar / Array / 向量矩阵变量

- **`RealVar`**（`class GMAT_API RealVar : public Parameter`，`RealVar.hpp:37`）：所有返回 Real 的参数的中间基类，也是用户数值变量之祖。构造默认 `key = USER_PARAM`、`typeStr = "RealVar"`（`RealVar.hpp:41-50`）。新增参数 `VALUE`（`RealVar.hpp:81-85`）与成员 `mRealValue/mValueSet/mIsNumber`（`RealVar.hpp:92-94`）；`GetReal/SetReal`（`RealVar.cpp` 实现）直接读写 `mRealValue`。`PARAMETER_TEXT` 静态表（`RealVar.cpp:44-45` 起）含 `"Value"`。`Variable`、`OrbitReal`、`AttitudeReal`、`BurnReal`、`BplaneReal`、`EnvReal`、`HardwareReal`、`BallisticMassReal`、`PlanetReal`、`TimeReal` 全部派生自它。
- **`Variable`**（`class GMAT_API Variable : public RealVar`，`Variable.hpp:39`）：脚本里的 `Variable` 对象。构造函数（`Variable.cpp:71`）把 `valStr` 解析成初始值；`EvaluateReal()`（`Variable.cpp:193`）返回当前 `mRealValue`；`SetStringParameter`（`Variable.cpp:301`）处理 `Value = 数值或变量名` 的脚本赋值，把 RHS 解析为实数或引用另一个 Variable（`RenameRefObject`/`GetRefObject` 链，`Variable.cpp:368/477`）。头文件里 `#ifdef __ALLOW_SIMPLE_VAR_EXP__` 包裹的 `ExpressionParser`/`ParameterDatabase` 字段（`Variable.hpp:85-92`）表明「变量内嵌简单表达式」已被关闭——注释（`Variable.hpp:82-84`）说明数学表达式只允许在命令模式下（`Math` 节点），对象模式下 Variable 只存字面值。
- **`StringVar`**（`StringVar.hpp:38`）：字符串变量基类，`mStringValue`（`StringVar.hpp:93`）承载值，`EvaluateString()` 返回之；`GetGeneratingString`（`StringVar.cpp`）回写 `name = "value"` 脚本。
- **`Array`**（`class GMAT_API Array : public Parameter`，`Array.hpp:39`）：一/二维数组变量。关键方法是 `SetSize(row, col, zeroElements)`（`Array.hpp:53`）与 `SetRmatrix/GetRmatrix`（`Array.hpp:59-60`）；内部以 `Rmatrix mRmatValue`（`Array.hpp:134`）存值，`EvaluateRmatrix()` 直接返回它（`Array.hpp:61`，注释 "assumes it has only numbers"）。参数表（`Array.cpp:48-49` 起）含 `NumRows/NumCols/RmatValue/SingleValue/RowValue/ColValue/InitialValue/InitialValueType`（枚举见 `Array.hpp:140-151`），其中 `InitialValueType` 区分「数字初值」与「Variable/其他 Array 引用初值」（`Array.hpp:132`）；`GetRealParameter(id, row, col)` 等重载（`Array.hpp:89-102`）让脚本能以 `Array(i,j)` 形式读写元素。
- **`RvectorVar` / `Rmat33Var` / `Rmat66Var` / `Rvec3Var` / `Rvec6Var`**：`class ... : public Parameter`（`RvectorVar.hpp:38`、`Rmat33Var.hpp:37`、`Rmat66Var.hpp:37`、`Rvec3Var.hpp:38`、`Rvec6Var.hpp:38`）。分别是 `Rvector`/`Rmatrix33`/`Rmatrix66`/`Rvector3`/`Rvector6` 类型的用户变量中间基类；`RvectorVar` 带 `VECTOR_SIZE` 参数（`RvectorVar.hpp:78-82`）与 `mRvectorValue`（`RvectorVar.hpp:76`），`EvaluateRvector()` 返回之。它们同时是系统参数装配层（`OrbitRvec6`、`OrbitRmat33`、`OrbitRmat66` 等）的"值载体"半边。

#### 8.1.4 RefData —— 引用数据层（系统参数的"求值引擎"半边）

`class GMAT_API RefData`（`RefData.hpp:80`）**不派生自 GmatBase**，而是系统参数的另一半继承来源：它负责「解析参数名引用的对象（Spacecraft、CoordinateSystem、SolarSystem）并完成状态换算」。核心成员是 `std::vector<RefObjType> mRefObjList`（`RefData.hpp:129`），`RefObjType` 结构体（`RefData.hpp:41-65`）以 `{objType, objName, obj}` 三元组记录一个引用对象。纯虚接口 `ValidateRefObjects(GmatBase *param)`（`RefData.hpp:116`）与 `IsValidObjectType(UnsignedInt type)`（`RefData.hpp:153`）由各 Data 实现；`InitializeRefObjects()`（`RefData.hpp:152`）在求值前把名字解析为指针。

- **`OrbitData`**（`class GMAT_API OrbitData : public RefData`，`OrbitData.hpp:46`）：轨道参数求值核心。它持有 `mSpacecraft/mSolarSystem/mInternalCoordSystem` 等指针（`OrbitData.hpp` 后半部）与引力常数 `mGravConst`。对外提供**成族的状态获取**：`GetCartState/GetKepState/GetModKepState/GetSphRaDecState/GetSphAzFpaState/GetEquinState/GetModEquinState/GetAltEquinState/GetDelaState/GetPlanetodeticState/GetIncAsymState/GetOutAsymState/GetBLshortState/GetBLlongState`（`OrbitData.hpp:58-72`）以及对应的逐分量 `GetKepReal(item)/GetCartReal(item)/...`（`OrbitData.hpp:77-129`）。实现模式如：

```cpp
// OrbitData.cpp:722-743（节选，省略 DEBUG_ORBITDATA_KEP_STATE 调试块）
Rvector6 OrbitData::GetKepState()
{
   if (mSpacecraft == NULL || mSolarSystem == NULL)
      InitializeRefObjects();

   // Call GetCartState() to convert to parameter coord system first
   Rvector6 state = GetCartState();
   Rvector6 kepState = StateConversionUtil::CartesianToKeplerian(mGravConst, state);

   return kepState;
}
```

逐行解释：先确保引用对象已解析（懒初始化）；`GetCartState()`（`OrbitData.cpp:496`）负责把 Spacecraft 状态从内部坐标系经 `CoordinateConverter` 转换到参数声明坐标系（含原点平移）；再用 `StateConversionUtil`（gmatutil 层，见 [第3章](CH03-math.md)）做元素集转换。`GetKepReal(KEP_SMA)`（`OrbitData.cpp:1168`）则按 `item` 索引从 `GetKepState()` 取分量并做角度/单位规范化。`SetReal/SetRvector6`（`OrbitData.hpp:74-75`）支持可设参数（如 `KepSMA` 是可设的）反向写回 Spacecraft 状态。
- **`SpacecraftData`**（`SpacecraftData.hpp:38`）：航天器质量特性/硬件参数数据层，`mSpacecraft`（`SpacecraftData.hpp:69`）指向被求值航天器；枚举从 `DRY_MASS` 到 `FUEL_MOI_ZZ_BCS`、`PRESSURE/TEMPERATURE/VOLUME/FUEL_DENSITY`、`HW_R_SB_11...`（`SpacecraftData.hpp:74-140`）覆盖干质量、干/系统质心、惯量、阻力/反射系数、燃油箱（含体坐标系 BCS 量）、硬件属性（太阳能板、推力器、天线等）全部量。`GetReal/SetReal/GetString/SetString/GetRvector/SetRvector`（`SpacecraftData.hpp:47-54`）是统一入口，内部按 item 分派到 `Spacecraft`/`Tank`/`Hardware` 的 `GetRealParameter` 等接口；`BALLISTIC_REAL_UNDEFINED`（`SpacecraftData.hpp:60`）作为未定义哨兵。
- **`TimeData`**（`TimeData.hpp:42`）：时间参数数据层。依赖 `TimeSystemConverter` 单例（`TimeData.hpp:95`），枚举 `A1, TAI, TT, TDB, UTC, YEARS, MONTHS, DAYS, HOURS, MINS, SECS`（`TimeData.hpp:100-104`）。`GetTimeReal/GetTimeString/GetElapsedTimeReal`（`TimeData.hpp:57-63`）做历元换算；`GetInitialEpoch/SetInitialEpoch`（`TimeData.hpp:52-55`）为 `ElapsedDays/ElapsedSecs` 类参数提供「起始历元」锚点（从 `A1Epoch` 或 `Propagate` 起点而来）。
- **`AttitudeData`**（`AttitudeData.hpp:44`）：姿态参数数据层，枚举覆盖 DCM 9 元、四元数、欧拉角、MRP、角速度、角速率、体对齐/约束向量、姿态参考体等（`AttitudeData.hpp:75-113`）；从 `Spacecraft` 的 `Attitude` 对象取数（`AttitudeData.hpp:72`）。
- **`BplaneData`**（`BplaneData.hpp:42`）、**`BurnData`**（`BurnData.hpp:43`）、**`EnvData`**（`EnvData.hpp:41`）、**`PlanetData`**（`PlanetData.hpp:42`）：分别服务 B 平面参数（`BdotT/BdotR/BVectorMag/BVectorAngle`）、点火参数（`ImpBurnElements/TotalThrust/...`）、环境参数（`EnvReal`）、行星参数（`MHA/Longitude/Altitude/Latitude/LST`）。

#### 8.1.5 系统参数装配层（RealVar/OrbitData 多继承）

- **`OrbitReal`**（`class GMAT_API OrbitReal : public RealVar, public OrbitData`，`OrbitReal.hpp:40`）：**C++ 多继承的经典用例**——从 `RealVar` 继承「参数身份」（名字/类型/求值入口），从 `OrbitData` 继承「求值引擎」。构造（`OrbitReal.cpp:66-82`）把 `RealVar` 与 `OrbitData` 两半都初始化，记录 `mItemId`（本参数在 OrbitData 中的分量索引），并 `AddRefObject(obj)` 把 owner 登记为引用对象。`EvaluateReal()`（`OrbitReal.cpp` 实现）按 `mItemId` 调 `OrbitData::GetXxxReal(mItemId)`。同模式的还有 `OrbitRvec6`（`OrbitRvec6.hpp:40`，6 元状态如 `KepElem`）、`OrbitRmat33`/`OrbitRmat66`（`OrbitRmat33.hpp:38`/`OrbitRmat66.hpp:38`，STM/协方差块）、`OrbitTime`（`OrbitTime.hpp:38`，轨道周期类）。
- 按对象域装配层：`AttitudeReal`（`AttitudeReal.hpp:39`，RealVar+AttitudeData）、`BallisticMassReal`（`BallisticMassReal.hpp:38`，RealVar+SpacecraftData）、`BurnReal`（`BurnReal.hpp:40`）、`BplaneReal`（`BplaneReal.hpp:40`）、`EnvReal`（`EnvReal.hpp:40`）、`HardwareReal`/`HardwareRvector`/`HardwareString`（`HardwareReal.hpp:38`/`HardwareRvector.hpp:41`/`HardwareString.hpp:39`，RealVar/RvectorVar/StringVar+SpacecraftData）、`PlanetReal`（`PlanetReal.hpp:40`）、`TimeReal`/`TimeString`（`TimeReal.hpp:40`/`TimeString.hpp:40`，RealVar/StringVar+TimeData）、`AttitudeRmat33`/`AttitudeRvector`/`AttitudeString`（`AttitudeRmat33.hpp:36`/`AttitudeRvector.hpp:39`/`AttitudeString.hpp:40`）。

#### 8.1.6 叶子参数族（*Parameters.hpp / .cpp，23 个文件对）

每个文件批量声明一组**极薄叶子类**：每个类只重写 `Evaluate()`（把 `mRealValue` 从 `OrbitData` 取来）与 `Clone()`。以 `KepSMA` 为例：

```cpp
// KeplerianParameters.cpp:54-60（构造）
KepSMA::KepSMA(const std::string &name, GmatBase *obj)
   : OrbitReal(name, "SMA", obj, "Orbit Semi-Major Axis", "Km", GmatParam::ORIGIN, KEP_SMA, true)
{
   mDepObjectName = "Earth";
   SetRefObjectName(Gmat::SPACE_POINT, "Earth");
   SetRefObjectName(Gmat::COORDINATE_SYSTEM, "EarthMJ2000Eq");
}
// KeplerianParameters.cpp:121-129（求值）
bool KepSMA::Evaluate()
{
   mRealValue = OrbitData::GetKepReal(KEP_SMA);

   if (mRealValue == GmatOrbitConstants::ORBIT_REAL_UNDEFINED)
      return false;
   else
      return true;
}
```

逐行解释：构造把类型串 `"SMA"`、单位 `"Km"`、依赖对象 `GmatParam::ORIGIN`、分量 ID `KEP_SMA`、可设标志 `true` 一次性传给 `OrbitReal`，并声明默认引用 `Earth` 与 `EarthMJ2000Eq`（后续被沙箱替换为实际对象）；`Evaluate()` 只有一行真正的计算——所有元素集换算逻辑都沉在 `OrbitData`——随后用 `GmatOrbitConstants::ORBIT_REAL_UNDEFINED` 哨兵判定取值是否有效（如状态未初始化时返回 false 而非污染数据）。这正是「**薄叶子 + 厚数据层**」的参数实现策略：146 个系统参数叶子共享同一套换算代码，每个叶子只有 ~40 行。23 个文件对的类清单（行号取自各 .hpp，均为 `class GMAT_API Xxx : public OrbitReal/OrbitRvec6/...`）：

- **KeplerianParameters**（`KeplerianParameters.hpp`）：`KepSMA`(:48)、`KepEcc`(:75)、`KepInc`(:103)、`KepAOP`(:130)、`KepRAAN`(:157)、`KepRADN`(:185)、`KepTA`(:213)、`KepMA`(:241)、`KepEA`(:269)、`KepHA`(:297)、`KepMM`(:325)、`KepElem`(:354，OrbitRvec6)、`ModKepRadApo`(:382)、`ModKepRadPer`(:409)、`ModKepElem`(:439，OrbitRvec6)。求值实现均调 `OrbitData::GetKepReal(KEP_*)`（`KeplerianParameters.cpp:123/236/351/467/583/696/811/926/1041/1156`），`KepElem` 调 `GetKepState()`（`KeplerianParameters.cpp:1383`）。
- **CartesianParameters**（`CartesianParameters.hpp`）：`CartX`(:47)、`CartY`(:74)、`CartZ`(:101)、`CartVx`(:128)、`CartVy`(:155)、`CartVz`(:182)、`CartState`(:210，OrbitRvec6)。单位 km / km/s，`depObj = ORIGIN`，坐标依赖（`CartX` 构造在 .cpp 中 `SetRefObjectName(Gmat::COORDINATE_SYSTEM, ...)` 并 `mNeedCoordSystem = true`）。
- **SphericalParameters**（`SphericalParameters.hpp`）：`SphRMag`(:48)、`SphRA`(:75)、`SphDec`(:102)、`SphVMag`(:130)、`SphRAV`(:157)、`SphDecV`(:184)、`SphAzi`(:212)、`SphFPA`(:240)、`SphRaDecElem`(:269，OrbitRvec6)、`SphAzFpaElem`(:298，OrbitRvec6)。
- **EquinoctialParameters**（`EquinoctialParameters.hpp`）：`EquinSma`(:39)、`SMADot`(:59)、`EquinEy`(:79)、`EquinEyDot`(:99)、`EquinEx`(:119)、`EquinExDot`(:139)、`EquinNy`(:159)、`EquinNyDot`(:179)、`EquinNx`(:199)、`EquinNxDot`(:219)、`EquinMlong`(:239)、`EquinTlongDot`(:259)、`EquinState`(:279，OrbitRvec6)。带 `Dot` 的类求 `GetEquinDot()`（由位置速度与 rMag 计算）。
- **ModEquinoctialParameters**（`ModEquinoctialParameters.hpp`）：`ModEquinP`(:39)、`ModEquinF`(:59)、`ModEquinG`(:79)、`ModEquinH`(:99)、`ModEquinK`(:119)、`ModEquinTLONG`(:139)、`ModEquinState`(:159，OrbitRvec6)。
- **AlternateEquinoctialParameters**（`AlternateEquinoctialParameters.hpp`，作者标注 HYKim）：`AltEquinP`(:39)、`AltEquinQ`(:59)、`AltEquinState`(:79，OrbitRvec6)。
- **DelaunayParameters**（`DelaunayParameters.hpp`）：`Dela_l`(:39)、`Dela_g`(:59)、`Dela_h`(:79)、`DelaL`(:99)、`DelaG`(:119)、`DelaH`(:139)、`DelaState`(:159，OrbitRvec6)。
- **BrouwerMeanLongParameters**（`BrouwerMeanLongParameters.hpp`，作者 MH）：`BLlongSMADP`(:37)、`BLlongECCDP`(:56)、`BLlongINCDP`(:74)、`BLlongRAANDP`(:93)、`BLlongAOPDP`(:111)、`BLlongMADP`(:130)、`BLlongState`(:148，OrbitRvec6)。调 `OrbitData::GetBLlongState()`（Brouwer 平均长周期元素）。
- **BrouwerMeanShortParameters**（`BrouwerMeanShortParameters.hpp`）：`BLshortSMAP`(:37)、`BLshortECCP`(:56)、`BLshortINCP`(:74)、`BLshortRAANP`(:93)、`BLshortAOPP`(:111)、`BLshortMAP`(:130)、`BLshortState`(:148，OrbitRvec6)。
- **PlanetodeticParameters**（`PlanetodeticParameters.hpp`）：`PldRMAG`(:39)、`PldLON`(:59)、`PldLAT`(:79)、`PldVMAG`(:99)、`PldAZI`(:119)、`PldHFPA`(:139)、`PldState`(:159，OrbitRvec6)。需要扁率/赤道半径（`mFlattening/mEqRadius`，来自 origin 天体）。
- **AngularParameters**（`AngularParameters.hpp`）：`SemilatusRectum`(:46)、`AngularMomentumMag`(:73)、`AngularMomentumX/Y/Z`(:101/129/157)、`BetaAngle`(:186)、`RLA`(:214)、`DLA`(:242)。
- **OrbitalParameters**（`OrbitalParameters.hpp`）：`VelApoapsis`(:48)、`VelPeriapsis`(:75)、`Apoapsis`(:102)、`Periapsis`(:129)、`OrbitPeriod`(:156)、`C3Energy`(:183)、`Energy`(:211)。
- **BplaneParameters**（`BplaneParameters.hpp`）：`BdotT`(:47)、`BdotR`(:75)、`BVectorMag`(:103)、`BVectorAngle`(:131)。求值经 `BplaneData`（入射/出射渐近线、B 平面坐标系）。
- **IncomingAsymptoteParameters / OutgoingAsymptoteParameters**（`IncomingAsymptoteParameters.hpp`、`OutgoingAsymptoteParameters.hpp`）：`IncAsymRadPer`(:41)/`OutAsymRadPer`(:41)、`IncAsymC3Energy`(:64)/`OutAsymC3Energy`(:64)、`IncAsymRHA`(:87)/`OutAsymRHA`(:87)、`IncAsymDHA`(:110)/`OutAsymDHA`(:110)、`IncAsymBVAZI`(:133)/`OutAsymBVAZI`(:133)、`IncAsymState`(:156)/`OutAsymState`(:156，OrbitRvec6)。
- **TimeParameters**（`TimeParameters.hpp`）：`CurrA1MJD`(:46)、`A1ModJulian`(:72)、`A1Gregorian`(:98，TimeString)、`TAIModJulian`(:124)、`TAIGregorian`(:150)、`TTModJulian`(:176)、`TTGregorian`(:202)、`TDBModJulian`(:228)、`TDBGregorian`(:254)、`UTCModJulian`(:281)、`UTCGregorian`(:307)、`ElapsedDays`(:333)、`ElapsedDaysFromStart`(:380)、`ElapsedSecs`(:426)、`ElapsedSecsFromStart`(:473)。后四个的 `PARAMETER_TEXT` 静态表在 `TimeParameters.cpp:1290/1595/1889/2184` 起。`CurrA1MJD` 是唯一不依赖具体 Spacecraft 的时间参数（取当前 A1MJD）。
- **AttitudeParameters**（`AttitudeParameters.hpp`）：`DCM11..DCM33`(:56-216)、`DirectionCosineMatrix`(:239，AttitudeRmat33)、`Quat1..Quat4`(:263-323)、`Quaternion`(:345，AttitudeRvector)、`EulerAngle1..3`(:370-410)、`MRP1..3`(:434-474)、`AngularVelocityX/Y/Z`(:498-538)、`EulerAngleRate1..3`(:562-602)、`BodyAlignmentVectorX/Y/Z`(:625-665)、`BodyConstraintVectorX/Y/Z`(:688-728)、`AttitudeParam`(:751，AttitudeString)、`AttitudeReferenceBody`(:771)、`AttitudeConstraintType`(:790)。
- **PlanetParameters**（`PlanetParameters.hpp`）：`MHA`(:48)、`Longitude`(:76)、`Altitude`(:104)、`Latitude`(:132)、`LST`(:160)。
- **BallisticMassParameters**（`BallisticMassParameters.hpp`）：`DryMass`(:46)、`DryCenterOfMassX/Y/Z`(:65/84/103)、`DryMomentOfInertiaXX..ZZ`(:122-217)、`DragCoeff`(:236)、`ReflectCoeff`(:255)、`DragArea`(:274)、`SRPArea`(:293)、`TotalMass`(:312)、`SystemCenterOfMassX/Y/Z`(:331-369)、`SystemMomentOfInertiaXX..ZZ`(:388-483)、`SpadSRPScaleFactor`(:522)、`AtmosDensityScaleFactor`(:541)、`DragCoeffSigma`(:560)、`ReflectCoeffSigma`(:579)、`SpadSRPScaleFactorSigma`(:617)、`AtmosDensityScaleFactorSigma`(:636)。
- **HardwareParameters**（`HardwareParameters.hpp`）：燃油箱 `FuelMass`(:52)、`FuelCenterOfMassX/Y/Z`(:72-112)、`FuelMomentOfInertiaXX..ZZ`(:132-232)、体坐标系版 `FuelCenterOfMass*_BCS`(:252-412)、`Pressure/Temperature/RefTemperature/Volume/FuelDensity`(:432-512)、太阳能板 `R_SB11..R_SB33`(:532-692)、`DutyCycle/ThrustScaleFactor/GravitationalAccel`(:712-752)、推力器 `ThrustCoefficients/ImpulseCoefficients/ThrustDirections/ThrustMagnitude/Isp/MassFlowRate`(:772-884)、电源 `TotalPowerAvailable/RequiredBusPower/ThrustPowerAvailable`(:905-949)、太阳帆/天线 `AreaCoefficient/SpecularFraction/DiffuseFraction/Area/Type/PlateNormal/LitFraction/PlateNormalHistoryFile`(:972-1116)、`AreaCoefficientSigma/SpecularFractionSigma/DiffuseFractionSigma`(:1137-1178)、`PlateX/Y/Z`(:1198-1238)。注意 `ThrustCoefficients/ImpulseCoefficients/ThrustDirections` 用 `HardwareReal` 是因为它们按索引取值（`GetRealParameter(id, index)`）。
- **BurnParameters**（`BurnParameters.hpp`）：`ImpBurnElements`(:48)、`TotalMassFlowRate`(:80)、`TotalAcceleration`(:112)、`TotalThrust`(:144)。依赖瞬态力（有限点火），经 `BurnData` 从 `PhysicalModel` 取数。
- **OrbitStmParameters**（`OrbitStmParameters.hpp`）：`OrbitStm`(:42，OrbitRmat66)、`OrbitStmA/B/C/D`(:65/88/111/134，OrbitRmat33)——状态转移矩阵的四个 3×3 分块，数据来自 Spacecraft 的 STM 缓冲。
- **OrbitCovarianceParameters**（`OrbitCovarianceParameters.hpp`）：`OrbitErrorCovariance`(:39，OrbitRmat66)——轨道误差协方差，来自 `Spacecraft::GetCovariance`。
- **`OrbitTime`**（`OrbitTime.hpp:38`）：`OrbitPeriod` 与 `OrbitTime` 的差值参数（`OrbitTime` 自身是 `OrbitReal`，求值 `mRealValue = OrbitData::GetOtherKepReal(...)` 计算轨道周期）。

#### 8.1.7 ElementWrapper 具体子类（11 个）

`ElementWrapper` 基类（`src/base/foundation/ElementWrapper.hpp`，见 [第2章](CH02-foundation.md)）定义 `EvaluateReal/SetReal/SetupWrapper` 等纯虚与静态赋值核心 `SetValue(lhsWrapper, rhsWrapper, ...)`（`ElementWrapper.cpp:553`）。本章目录下的 11 个子类把「一段文本描述」绑定为「可求值、可赋值的元素」，构成脚本赋值 `lhs = rhs` 的两端：

- **`NumberWrapper`**（`NumberWrapper.hpp:41`）：数字字面量（RHS 用）。成员仅 `Real value`（`NumberWrapper.hpp:65`）；`SetupWrapper` 把描述串 `ToReal` 解析；`EvaluateReal` 返回之。没有引用对象。
- **`StringWrapper`**（`StringWrapper.hpp:36`）：字符串字面量，`EvaluateString/EvaluateReal`（`StringWrapper.hpp:49-53`，Real 版做 `ToReal` 转换）。
- **`BooleanWrapper`**（`BooleanWrapper.hpp:36`）、**`OnOffWrapper`**（`OnOffWrapper.hpp:36`）：布尔/开关字面量，`EvaluateBoolean/EvaluateOnOff`（.cpp 实现把 `"true/false"`、`"On/Off"` 解析）。
- **`ObjectWrapper`**（`ObjectWrapper.hpp:36`）：整对象引用（如 `Sat` 本身），`EvaluateObject()` 返回 `GmatBase*`。
- **`VariableWrapper`**（`VariableWrapper.hpp:42`）：绑定一个 `Variable*`（成员 `var`，`VariableWrapper.hpp:70`）；`EvaluateReal()` 转调 `var->EvaluateReal()`，`SetReal` 写回——脚本里 `x = 5` 的 LHS 包装器。
- **`ParameterWrapper`**（`ParameterWrapper.hpp:42`）：绑定一个 `Parameter*`（成员 `param`，`ParameterWrapper.hpp:82`）；`EvaluateReal/EvaluateString/EvaluateArray/EvaluateRvector/EvaluateObject` 全套（`ParameterWrapper.hpp:64-77`）按参数返回类型分派——报告/绘图/方程中 `Sat.X` 的通用包装器。
- **`ArrayWrapper`**（`ArrayWrapper.hpp:42`）：绑定 `Array*` 整体；`EvaluateArray()` 返回其 Rmatrix。
- **`ArrayElementWrapper`**（`ArrayElementWrapper.hpp:42`）：绑定**数组单元素** `Array(i,j)`。关键设计是行/列各持一个子包装器：成员 `row`、`column`（`ArrayElementWrapper.hpp:84-85`），`GetRowName/GetColumnName/SetRow/SetColumn`（`ArrayElementWrapper.hpp:71-77`）——这样 `Array(i+1, 2)` 里的 `i+1` 也能作为表达式求值；`EvaluateReal` 先求行/列值再索引 `array->GetRealParameter(...)`。
- **`StringObjectWrapper`**（`StringObjectWrapper.hpp:42`）：绑定 `StringVar` 或返回字符串的对象字段；`EvaluateString` 转调 `Parameter::EvaluateString` 或 `GmatBase::GetStringParameter`。
- **`ObjectPropertyWrapper`**（`ObjectPropertyWrapper.hpp:41`）：**最通用的对象字段包装器**。成员 `object`（`ObjectPropertyWrapper.hpp:93`）+ `propID`（`ObjectPropertyWrapper.hpp:97`）；`SetupWrapper` 把 `ObjectName.PropertyName` 解析成 `object` 与参数 ID；`EvaluateReal/EvaluateString/EvaluateOnOff/EvaluateBoolean/EvaluateInteger/EvaluateArray/EvaluateRvector` 全套（`ObjectPropertyWrapper.hpp:66-80`）经 `object->GetXxxParameter(propID)` 取数，`SetReal/SetString/...` 写回；`TakeRequiredAction`（`ObjectPropertyWrapper.hpp:88`）在设值前触发 `TakeAction`（如硬件对象的准备动作）。它是 `Achieve`、`Vary`、`Report` 等命令处理 `Sat.XXX` 时使用最频繁的包装器。

**文本转换链小结**：脚本字符串 → `Interpreter`（非本章）识别 `lhs = rhs` → 各自调 `ElementWrapper::SetValue(lhsWrapper, rhsWrapper, solarSys, objMap, globalObjMap, setRefObj)`（`ElementWrapper.cpp:553`，[第2章](CH02-foundation.md) 2.2.7）→ 按 RHS `GetDataType()` 求值、按 LHS 类型写入。本章 11 个子类负责「描述串 → 求值/赋值」的具体绑定，命令层的调用见 [第5章](CH05-command.md)。

#### 8.1.8 ExpressionParser

`class GMAT_API ExpressionParser`（`ExpressionParser.hpp:52`）：小型递归下降解析器（参考 Herbert Schildt《C++ 完全参考》）。`EvalExp(const char *exp)`（`ExpressionParser.hpp:58`）支持数字、`+ - / * ^`、括号、单字母变量（26 个，`mVars[NUM_VARS]`，`ExpressionParser.hpp:86`）；内部方法 `EvalTwoTerms/EvalTwoFactors/EvalExponent/EvalUnary/EvalParenExp`（`ExpressionParser.hpp:90-94`）按优先级逐层下降。`SetParameterDatabase`（`ExpressionParser.hpp:59`）注入变量表。**当前仅被 `Variable` 的 `__ALLOW_SIMPLE_VAR_EXP__` 编译分支使用**（`Variable.hpp:85-92`），默认关闭，属遗留代码。

### 8.2 function 目录（40 个文件）

#### 8.2.1 Function —— 函数抽象基类

`class GMAT_API Function : public GmatBase`（`src/base/function/Function.hpp:43`）。脚本函数、内建函数、MATLAB 函数的共同基类。成员：`callDescription/functionPath/functionName/inputNames/outputNames/outputWrapperTypes/outputRowCounts/outputColCounts`（`Function.hpp:108-123`）与注入的 `solarSys/internalCoordSys/forces`（`Function.hpp:126-130`）。生命周期三件套：

```cpp
// Function.hpp:68-70
virtual bool         Initialize(ObjectInitializer *objInit, bool reinitialize = false);
virtual bool         Execute(ObjectInitializer *objInit, bool reinitialize = false);
virtual void         Finalize(bool cleanUp = false);
```

基类实现均为空/返回 true（`Function.cpp:248/257/266`），由 `ObjectManagedFunction`/`UserDefinedFunction`/内建函数重写。参数表 `FUNCTION_PATH/FUNCTION_NAME/FUNCTION_INPUT/FUNCTION_OUTPUT`（`Function.hpp:135-142`）供脚本 `BeginMissionSequence` 前声明函数时填充；`GetOutputTypes/SetOutputTypes`（`Function.hpp:53-58`）描述输出包装器类型与行列数（供 `FunctionManager` 创建输出对象）。`IsNewFunction`（`Function.cpp:221`）区分「脚本首次声明」与「调用点引用」。

#### 8.2.2 ObjectManagedFunction / BuiltinGmatFunction / UserDefinedFunction

- **`ObjectManagedFunction`**（`class GMAT_API ObjectManagedFunction : public Function`，`ObjectManagedFunction.hpp:44`）：为 Builtin 与 UserDefined 两类函数提供「函数对象存储（FOS）管理」。成员 `inputArgMap/outputArgMap`（`WrapperMap`，`ObjectManagedFunction.hpp:91-93`）、`objectStore/globalObjectStore`（`ObjectMap*`，`ObjectManagedFunction.hpp:95-97`）。`SetInputElementWrapper(forName, wrapper)`（`ObjectManagedFunction.cpp:203`）把调用点传入的实参包装器按形参名登记；`GetOutputArgument`（`ObjectManagedFunction.cpp:246/262`）取输出包装器；`SetChangingInputType`（`ObjectManagedFunction.cpp:377`）标记「输入类型每次调用可变」（如数组元素实参），驱动 `FunctionManager` 每次重新初始化。
- **`BuiltinGmatFunction`**（`BuiltinGmatFunction.hpp:36`）：内建函数（`Angle`、`ConvertTime` 等）基类。只重写 `Initialize`（`BuiltinGmatFunction.cpp:114`）与 `SetStringParameter`（`BuiltinGmatFunction.cpp:152`）；`.cpp:58` 把 `"BuiltinGmatFunction"` 追加进类型名表。它不解析函数文件——内建函数的输入/输出由脚本调用点直接给出。
- **`UserDefinedFunction`**（`class GMAT_API UserDefinedFunction : public ObjectManagedFunction`，`UserDefinedFunction.hpp:38`）：**用户脚本函数（即 `GmatFunction` 类型的载体）**。从函数文件解析出的命令序列保存在 `fcs`（函数控制序列 `GmatCommand*`，`UserDefinedFunction.hpp:77`），配套 `fcsInitialized/fcsFinalized` 标志与 `SetFunctionControlSequence/GetFunctionControlSequence`（`UserDefinedFunction.cpp:323/...`）。对象管理：`functionObjectMap`（函数内 `Create` 的对象）、`automaticObjectMap`（解析期自动创建、稍后绑定引用的对象）、`validator/validatorStore`（用 `Validator` 生成 ElementWrapper 的校验环境）（`UserDefinedFunction.hpp:86-94`）。`Initialize`（`UserDefinedFunction.cpp:156-163`）取 `Validator::Instance()` 后转调父类；`Finalize`（`UserDefinedFunction.cpp:178-301`）做一件关键收尾：把函数内创建的 Parameter 引用复位回全局 ReportFile/XYPlot（`UserDefinedFunction.cpp:246-292`，遍历 globalObjectStore 中的 ReportFile/XYPlot 调 `SetRefObject`），保证函数返回后全局订阅者仍指向沙箱对象。
- **`FunctionManager`**（`class GMAT_API FunctionManager`，`FunctionManager.hpp:58`）：**函数调用的运行时管理器**（每个 `CallFunction`/`FunctionRunner` 配一个）。核心数据：`functionObjectStore`（FOS，函数局部对象）、`localObjectStore`（LOS，调用者局部）、`globalObjectStore`（GOS，全局）、`combinedObjectStore`（LOS+GOS 合并，喂给 Validator）、`callStack/losStack`（嵌套/递归调用栈）、`callers`（`std::stack<FunctionManager*>`，`FunctionManager.hpp:181`）、`currentFunction`（`ObjectManagedFunction*`，`FunctionManager.hpp:131`）。执行流：

```cpp
// FunctionManager.cpp:913-956（Execute 主干，节选）
PrepareObjectMap();
PrepareExecution(callingFM);

if (firstExecution || currentFunction->HasChangingInputType())
{
   Initialize();                       // 首次执行：校验并创建包装器
}
else
{
   RefreshFormalInputObjects();        // 后续执行：只刷新形参对象
}
```

逐行解释：`PrepareObjectMap`（`FunctionManager.cpp:776-835`）在首次执行时把 LOS+GOS 合并进 `combinedObjectStore` 并交给 `Validator`（`FunctionManager.cpp:808-816`）；随后把 GOS/太阳系/瞬态力注入函数（`FunctionManager.cpp:967-969`），把每个实参包装器 `SetInputElementWrapper`（`FunctionManager.cpp:973-981`），重建 `ObjectInitializer`（`FunctionManager.cpp:991-998`）后调 `currentFunction->Initialize/Execute`。`Evaluate/MatrixEvaluate/EvaluateObject`（`FunctionManager.cpp:1146/1177/1215`）是数学表达式内联调用函数的三态入口；`PushToStack/PopFromStack`（`FunctionManager.cpp:2514/2534`）与 `CloneObjectMap`（`FunctionManager.cpp:3207`）实现嵌套/递归时的对象存储快照；`AssignResult/SaveLastResult`（`FunctionManager.cpp:2296/2452`）把函数返回值送到调用点。

#### 8.2.3 内建函数（14 个文件对）

每个内建函数都是 `class Xxx : public BuiltinGmatFunction`（各 .hpp 行号：`Angle.hpp:37`、`ConvertTime.hpp:38`、`GetEphemStates.hpp:38`、`GetLastState.hpp:37`、`Num2str.hpp:37`、`Pause.hpp:40`、`QuaternionProduct.hpp:36`、`QuaternionRotation.hpp:36`、`QuaternionToDCM.hpp:36`、`RotationMatrix.hpp:38`、`SetSeed.hpp:37`、`Sign.hpp:39`、`Str2num.hpp:37`、`SystemTime.hpp:36`），重写 `GetOutputTypes/SetOutputTypes/Initialize/Execute/Finalize/Clone/Copy`（以 `Angle.hpp:45-57` 为模板）。`Execute` 的模式（以 `Angle::Execute` 为例，`Angle.cpp:187` 起）：先校验 `inputArgMap.size()==3`、`outputArgMap.size()==1`（`Angle.cpp:193-228`），再从 `objectStore` 按 `inputNames` 取三个 `SpacePoint*`，计算夹角，最后把结果写进输出包装器（`Angle.cpp` 后半部分调用 `CreateOutputVariableWrapper` 建输出 Variable 包装器）。各函数语义：

- **`Angle`**：三输入（顶点、两端点 SpacePoint），输出顶点处两矢量夹角（弧度/度），`Angle.cpp:61` 的 `CreateOutputVariableWrapper` 负责把 `Real` 结果包装成输出 Variable。
- **`ConvertTime`**：`ConvertTime(fromTimeSystem, toTimeSystem, inputTime)` 三输入；经 `TimeSystemConverter` 做 A1/TAI/TT/TDB/UTC 换算。
- **`GetEphemStates`**：`[initialEpoch, initialState, finalEpoch, finalState] = GetEphemStates(ephemType, sat, epochFormat, coordSystem)`（`GetEphemStates.hpp:29-31`）；按 `inEphemType` 分派 `ReadSpiceEphemerisFile/ReadCode500EphemerisFile/ReadSTKEphemerisFile/ReadCCSDSEphemerisFile`（`GetEphemStates.hpp:73-76`），并用 `CreateLocalCoordSystem`（`GetEphemStates.hpp:78-81`）建临时坐标系做状态转换。
- **`GetLastState`**：返回指定对象最后一次发布的状态（`Rvector6`），由 `Publisher` 的 last 状态缓冲提供。
- **`Num2str`**：数字转字符串（精度/宽度参数），`Str2num` 反向解析（内部用 `GmatStringUtil::ToReal`）。
- **`Pause`**：暂停运行（`Pause.cpp:68` 构造；内部 Sleep）。
- **`QuaternionProduct` / `QuaternionRotation` / `QuaternionToDCM` / `RotationMatrix`**：四元数乘法、用四元数旋转矢量、四元数→DCM、旋转矩阵构造（输入轴/角）。`RotationMatrix.hpp:38`。
- **`SetSeed`**：设置随机数种子（`GmatGlobal` 的随机源）。
- **`Sign`**：符号函数（`Sign.hpp:39`）。
- **`SystemTime`**：返回当前系统时间字符串（`SystemTime.cpp:68` 构造）。

`FunctionException.hpp/.cpp`：`class FunctionException : public BaseException`（`FunctionException.hpp` 声明），各函数/管理器抛出的异常类型。

### 8.3 solver 目录（21 个文件）

#### 8.3.1 Solver —— 求解器基类与状态机

`class GMAT_API Solver : public GmatBase`（`src/base/solver/Solver.hpp:57`）。头注释（`Solver.hpp:47-56`）明确：求解器子系统是**数值引擎**，调整输入参数（"variables"）并度量扰动结果，整体是一个**状态机**。三个关键枚举：

```cpp
// Solver.hpp:61-107（节选）
enum SolverState
{
   INITIALIZING = 10001, NOMINAL, PERTURBING, ITERATING, CALCULATING,
   ACCUMULATING, ESTIMATING, SIMULATING, PROPAGATING, LOCATING,
   CHECKINGRUN, RUNEXTERNAL, RUNSPECIAL, FINISHED, UNDEFINED_STATE
};
enum MachineMode { SOLVE = 7000, INITIAL_GUESS, RUN_CORRECTED, UNKNOWN_MACHINE_MODE };
enum ExitMode    { DISCARD = 8000, RETAIN, HALT, UNKNOWN_EXIT_MODE };
```

状态机驱动器是 `AdvanceState()`（`Solver.cpp:657-700`）：按 `currentState` 分派到 `CompleteInitialization/RunNominal/RunPerturbation/RunIteration/CalculateParameters/CheckCompletion/RunExternal/RunComplete`（默认实现 `Solver.cpp:1409-1532`），每个虚函数默认只推进状态，由派生类重写实际算法。数据成员：`variable/variableInitialValues/unscaledVariable`（`Solver.hpp:259-263`）、`perturbation/variableMinimum/variableMaximum/variableMaximumStep/pertDirection`（`Solver.hpp:270-285`）、`iterationsTaken/maxIterations`（`Solver.hpp:265-267`）；报告设施：`solverTextFile/textFile`（`Solver.hpp:289-296`）与 `ReportProgress` 三态（`Solver.hpp:181-183`，经 `ISolverListener` 列表派发）。`SetSolverVariables/RefreshSolverVariables/GetSolverVariable/SetUnscaledVariable`（`Solver.hpp:190-196`）是 `Vary` 命令与求解器之间的变量通道；纯虚 `SetSolverResults`（`Solver.hpp:215-217`）与 `SetResultValue`（`Solver.hpp:229-230`）是 `Achieve`/`Minimize` 命令登记目标/约束结果的通道。

#### 8.3.2 DifferentialCorrector —— 微分改正器

`class GMAT_API DifferentialCorrector : public Solver`（`DifferentialCorrector.hpp:48`）。核心数值数据：`goal/tolerance/nominal/achieved/backAchieved`（`DifferentialCorrector.hpp:124-133`）、`jacobian/inverseJacobian`（`DifferentialCorrector.hpp:135-137`）、`indx/b`（LU 分解用，`DifferentialCorrector.hpp:140-142`）、`dcType/dcTypeId`（算法选择，`DifferentialCorrector.hpp:106-108`，合法值 `"NewtonRaphson"/"Broyden"/"ModifiedBroyden"` 见 `DifferentialCorrector.cpp:530-544`）。

**(1) 状态机。** 重写 `AdvanceState()`（`DifferentialCorrector.cpp:853-1001`）：按 `currentMode`（`INITIAL_GUESS` 或 `SOLVE`）分别走 `INITIALIZING → NOMINAL → PERTURBING → CALCULATING → CHECKINGRUN → FINISHED`（`DifferentialCorrector.cpp:900-997`），其中 `CHECKINGRUN` 后 `++iterationsTaken` 并与 `maxIterations` 比较（`DifferentialCorrector.cpp:968-976`）。

**(2) 雅可比与求逆。** `CalculateJacobian()`（`DifferentialCorrector.cpp:1539-1565`）：

```cpp
// DifferentialCorrector.cpp:1543-1564（节选）
if (diffMode != 0)                      // 前向/后向差分
{
   for (i = 0; i < variableCount; ++i)
      for (j = 0; j < goalCount; ++j)
      {
          jacobian[i][j] = achieved[i][j] - nominal[j];
          jacobian[i][j] /= (pertDirection.at(i) * perturbation.at(i));
      }
}
else        // Central differencing
{
   for (i = 0; i < variableCount; ++i)
      for (j = 0; j < goalCount; ++j)
      {
          jacobian[i][j] = achieved[i][j] - backAchieved[i][j];
          jacobian[i][j] /= (2.0 * perturbation.at(i));
      }
}
```

逐行解释：前向/后向差分用「扰动运行结果 − 名义运行结果」除以步长；中心差分用「正扰动 − 负扰动」除以 `2*步长`。`InvertJacobian()`（`DifferentialCorrector.cpp:1576-1633`）把 C 数组拷入 `Rmatrix`，方阵用 `jac.Inverse()`、矩形用 `jac.Pseudoinverse()`（`DifferentialCorrector.cpp:1596-1599`），奇异时抛 `SolverException` 提示「Vary 变量不影响 Achieve 目标」（`DifferentialCorrector.cpp:1603-1605`）。

**(3) 迭代修正（CalculateParameters）。** `DifferentialCorrector.cpp:1126-1358` 按 `dcTypeId` 三路：
- **Newton-Raphson**（case 1）：`CalculateJacobian(); InvertJacobian();`（`:1134-1138`）。
- **Broyden**（case 2）：首次迭代仍走数值雅可比（`:1142-1147`），后续用秩一更新 `jacobian[j][i] = savedJacobian[j][i] + numerator[i]*s[j]/denom`（`:1180-1183`），其中 `s = variable - savedVariable`、`y = nominal - savedNominal`（`:1163-1171`），省去每次重跑全部扰动。
- **Modified Broyden**（case 3）：直接更新**逆**雅可比（`:1189-1245`，用 `savedInverseJacobian` 与 `v_k` 构造）。
最后统一做修正量：`delta[i] += inverseJacobian[j][i] * (goal[j] - nominal[j])`（`:1299`），受 `variableMaximumStep` 步长限制（`:1307-1328`）后 `variable.at(i) += delta.at(i) * multiplier`（`:1330`），并通过 `ISolverListener::VariabledChanged` 通知 GUI（`:1452` 等）。

#### 8.3.3 Optimizer 家族

- **`Optimizer`**（`class GMAT_API Optimizer : public Solver`，`Optimizer.hpp:38`）：优化器基类。新增参数 `OBJECTIVE_FUNCTION/OPTIMIZER_TOLERANCE/EQUALITY_CONSTRAINT_NAMES/INEQUALITY_CONSTRAINT_NAMES/PLOT_COST_FUNCTION/SOURCE_TYPE/CHECK_PHYSICAL_TOLERANCES`（`Optimizer.hpp:145-155`）；数据：`cost/oldCost/tolerance/converged`（`Optimizer.hpp:164-175`）、等/不等约束的 desired/achieved/tolerance/op 四元组向量（`Optimizer.hpp:187-206`）、`gradient/jacobian/eqConstraintJacobian/ineqConstraintJacobian`（`Optimizer.hpp:209-214`）。**纯虚 `bool Optimize() = 0`**（`Optimizer.hpp:141`）由具体优化器实现；`SetConstraintValues`（`Optimizer.hpp:57-58`）由 `NonlinearConstraint` 命令调用；`PerformToleranceCheck`（`Optimizer.hpp:228`）做"物理容差"检查。
- **`InternalOptimizer`**（`InternalOptimizer.hpp:41`）：内嵌优化器接口（参数计数即 `OptimizerParamCount`，`InternalOptimizer.hpp:54-57`），具体内嵌算法（如 NLPQLP）在插件层实现。
- **`ExternalOptimizer`**（`ExternalOptimizer.hpp:43`）：外部优化器接口（如 MATLAB/SNOPT），新增 `FUNCTION_PATH` 参数（`ExternalOptimizer.hpp:104-108`），持有 `GmatInterface` 单例（`ExternalOptimizer.hpp:38`）与 `GmatServer` 前向引用（`ExternalOptimizer.hpp:40`）；`needsServerStartup` 标志（`Solver.hpp:240-241`）表明外部优化器需启动 GMAT 服务器（见 8.6.2）。

#### 8.3.4 导数模型与监听

- **`DerivativeModel`**（`class GMAT_API DerivativeModel`，`DerivativeModel.hpp:40`）：导数计算基类（不派生 GmatBase）。枚举 `FORWARD_DIFFERENCE/CENTRAL_DIFFERENCE/BACKWARD_DIFFERENCE/USER_SUPPLIED`（`DerivativeModel.hpp:44-49`）；`SetDifferenceMode`（`DerivativeModel.hpp:57`）选差分模式；`Initialize(varCount, componentCount)`（`DerivativeModel.hpp:58-59`）分配 `pert/plusPertEffect/minusPertEffect`（`DerivativeModel.hpp:75-79`）；`Achieved(pertNumber, componentId, dx, value, plusEffect)`（`DerivativeModel.hpp:60-61`）收集每次扰动运行的结果；**纯虚 `Calculate(vector<Real>&) = 0`**（`DerivativeModel.hpp:62`）。
- **`Jacobian`**（`Jacobian.hpp:41`）：`Initialize(varCount, componentCount)` 后按差分模式组装 `numComponents × varCount` 雅可比（成员 `nominal/jacobian`，`Jacobian.hpp:59-61`）；`Calculate` 做差分除法。
- **`Gradient`**（`Gradient.hpp:41`）：一列分量（`componentCount=1`）的导数，`nominal` 标量 + `gradient` 向量（`Gradient.hpp:57-59`）。
- **`LineSearch`**（`LineSearch.hpp:39`）：**未实现的占位类**——头注释明确 "This class is not yet implemented"（`LineSearch.hpp:37`），只有构造/析构。
- **`ISolverListener`**（`ISolverListener.hpp`）：求解器进度监听接口，`Solver::ReportProgress(listeners, state)` 遍历派发；`DifferentialCorrector.cpp:1452/1473/1490` 用其 `VariabledChanged` 回调把变量新值推给 GUI 的 Vary 面板。
- **`SolverException.hpp`**：`class SolverException : public BaseException`（仅头文件）。

### 8.4 subscriber 目录（46 个文件）

#### 8.4.1 Subscriber —— 订阅者基类与数据管道

`class GMAT_API Subscriber : public GmatBase`（`src/base/subscriber/Subscriber.hpp:54`）。订阅者从全局 `Publisher` 接收数据流（发布/订阅关系由 [第2章](CH02-foundation.md) 的 `ObjectInitializer` 建立）。数据管道核心：

```cpp
// Subscriber.cpp:435-464（节选，省略 DEBUG_RECEIVE_DATA 调试块）
bool Subscriber::ReceiveData(const Real *datastream, const int len)
{
   if (!active)        // Not currently processing data
      return true;
   if (len == 0)
      return true;
   if (!Distribute(datastream, len))
      return false;
   return true;
}
```

逐行解释：`ReceiveData` 是 `Publisher` 在每次传播/求解步后调用的入口；未激活（`active==false`）或空数据直接返回；真正处理在**虚函数 `Distribute`**（`Subscriber.hpp:258-259`，派生类重写）中。配套 `FlushData/SetEndOfRun`（`Subscriber.cpp:470/485`）以 `Distribute(0)/Distribute(NULL,0)` 双调用通知数据块/运行结束；`SetProvider/SetDataLabels/SetInternalCoordSystem/SetDataCoordSystem/SetSolarSystem`（`Subscriber.cpp:762/770/816/831/855`）配置数据来源环境。**ElementWrapper 机制**是订阅者的求值通道：`xWrapperObjectNames/yWrapperObjectNames/allWrapperObjectNames` 与 `xParamWrappers/yParamWrappers`（`Subscriber.hpp:231-237`），`SetElementWrapper`（`Subscriber.cpp:873`）、`ShouldDataBeSkipped`（`Subscriber.cpp:1950`，按 `SOLVER_ITERATIONS` 选项决定求解迭代数据是否跳过）配合实现「只记录用户选定参数」。`HandleManeuvering/HandleSpacecraftPropertyChange`（`Subscriber.hpp:260-267`）让报告/历表在点火机动或属性变更处做特殊处理。参数表 `SOLVER_ITERATIONS/TARGET_STATUS/UPPER_LEFT/SIZE/RELATIVE_Z_ORDER/MINIMIZED/MAXIMIZED`（`Subscriber.hpp:274-284`）。

#### 8.4.2 ReportFile 与 TextEphemFile

- **`ReportFile`**（`class GMAT_API ReportFile : public Subscriber`，`ReportFile.hpp:47`）：最常用的订阅者，把选定参数写成列式文本。关键方法：`AddParameter(paramName, index)`（`ReportFile.cpp:327`）、`WriteData(WrapperArray, parsable)`（`ReportFile.cpp:370`）、`Initialize`（`ReportFile.cpp:680`）、`Distribute`（`ReportFile.cpp:1802/1870`）。`WriteData` 是格式化核心：为每个包装器计算列宽（`ReportFile.cpp:421-440`，Gregorian 字段最小 24 宽），然后按 `WrapperType` 分派取值——`VARIABLE_WT/ARRAY_ELEMENT_WT/OBJECT_PROPERTY_WT` 走 `EvaluateReal()` 后 `GmatStringUtil::ToString(rval, precision, zeroFill)`（`ReportFile.cpp:442-483`），`NaN` 哨兵处理见 `ReportFile.cpp:459-461`。参数表 `FILENAME/FULLPATH_FILENAME/PRECISION/ADD/WRITE_HEADERS/LEFT_JUSTIFY/ZERO_FILL/FIXED_WIDTH/DELIMITER/COL_WIDTH/WRITE_REPORT/APPEND_TO_EXISTING_FILE`（`ReportFile.hpp:197-212`）。`OpenReportFile`（`ReportFile.cpp:1589`）、`WriteHeaders`（`ReportFile.cpp:1666`）管理文件生命周期；`parsable=true` 时输出 `Create` 关键字脚本（`ReportFile.cpp:446-455`）。
- **`TextEphemFile`**（`class GMAT_API TextEphemFile : public ReportFile`，`TextEphemFile.hpp:39`）：报告文件风格的文本历表（已由 `EphemerisFile` 体系取代，保留为兼容）。

#### 8.4.3 EphemerisFile 与 EphemerisWriter 家族

- **`EphemerisFile`**（`class GMAT_API EphemerisFile : public Subscriber`，`EphemerisFile.hpp:39`）：历表文件订阅者基类。文件类型枚举 `CCSDS_OEM/CCSDS_AEM/SPK_ORBIT/SPK_ATTITUDE/CK_ATTITUDE/CODE500_EPHEM/STK_TIMEPOSVEL`（`EphemerisFile.hpp:120-124`）；持有 `spacecraft/outCoordSystem/ephemWriter`（`EphemerisFile.hpp:126-128`）。`Initialize`（`EphemerisFile.cpp:629`）→ `CreateEphemerisWriter()`（`EphemerisFile.cpp:2023`）按 `fileFormat` 从 `EphemManager` 拿具体 Writer；`Distribute`（`EphemerisFile.cpp:2965/2981`）把 `currState[6]/currCov[21]/currAccel[3]/currQuat[4]`（`EphemerisFile.hpp:173-177`）交给 writer；`HandleOrbitData`（`EphemerisFile.cpp:2121`）、`StartNewSegment`（`EphemerisFile.cpp:2155`）处理段切换；`HandlePropDirectionChange/HandleManeuvering/HandlePropagatorChange`（`EphemerisFile.cpp:2422/3250/3421`）处理反向传播、机动与传播器更换。参数表覆盖 `SPACECRAFT/FILENAME/FILE_FORMAT/FILE_FORMAT_VERSION/EPOCH_FORMAT/INITIAL_EPOCH/FINAL_EPOCH/STEP_SIZE/INTERPOLATOR/INTERPOLATION_ORDER/STATE_TYPE/COORDINATE_SYSTEM/OUTPUT_FORMAT/WRITE_EPHEMERIS/DISTANCE_UNIT/INCLUDE_EVENT_BOUNDARIES` 等（`EphemerisFile.hpp:278-304`）。
- **`EphemerisWriter`**（`class GMAT_API EphemerisWriter`，`EphemerisWriter.hpp:37`）：**不派生 GmatBase** 的写入器基类（由 EphemerisFile 拥有）。数据缓冲：`a1MjdArray/stateArray/covArray/accelArray/quatArray`（`EphemerisWriter.hpp:169-174`）；纯虚 `HandleOrbitData/StartNewSegment/FinishUpWriting/Clone/BufferOrbitData`（`EphemerisWriter.hpp:105-139, 260`）；公共工具 `ConvertState`（`EphemerisWriter.hpp:298-301`，经 `CoordinateConverter coordConverter` 成员 `EphemerisWriter.hpp:246` 从数据坐标系转输出坐标系）、`WriteOrbit/WriteOrbitAt/FindNextOutputEpoch`（`EphemerisWriter.hpp:268-295`，按固定步长在 `nextOutEpochInSecs` 处插值写出）、`WriteHeader/WriteMetaData/WriteDataComments`（`EphemerisWriter.hpp:282-285`）。
- **`EphemWriterWithInterpolator`**（`EphemWriterWithInterpolator.hpp:35`）：中间类，持有 `Interpolator *interpolator`（`EphemWriterWithInterpolator.hpp:50`）与 `epochsOnWaiting` 缓冲（`EphemWriterWithInterpolator.hpp:56`）；`FindNextOutputEpoch`（`EphemWriterWithInterpolator.hpp:73-74`）、`IsTimeToWrite`（`...:83`）、`ProcessEpochsOnWaiting`（`...:88-89`）实现「攒够阶数 → 插值到输出时刻」的流式写出。
- **具体写入器**：
  - `EphemWriterCCSDS`（`EphemWriterCCSDS.hpp:38`）：CCSDS OEM/AEM 文本格式。
  - `EphemWriterCode500`（`EphemWriterCode500.hpp:35`）：NASA Code 500 格式。
  - `EphemWriterSPK`（`EphemWriterSPK.hpp:35`）：SPK 二进制（经 `SpiceOrbitKernelWriter`，见 8.8）；支持后台生成与追加（`CloseEphemerisFile` 语义见 `EphemerisFile.hpp:57`）。
  - `EphemWriterSTK`（`EphemWriterSTK.hpp:35`）：STK TimePosVel 文本。
  - `AttitudeWriterCK`（`AttitudeWriterCK.hpp:38`）：CK 姿态内核（经 `SpiceAttitudeKernelWriter`）。
- **`EphemManager`**（`class GMAT_API EphemManager`，`EphemManager.hpp:53`）：历表管理器（GroundStation 等资产用），枚举 `SPK/FK/CK/CCSDS`（`EphemManager.hpp:57-63`）；`RecordEphemerisData/ProvideEphemerisData/StopRecording`（`EphemManager.hpp:74-79`）控制"写一段→加载回来供查询"；`GetOccultationIntervals/GetContactIntervals/GetIntrusionIntervals`（`EphemManager.hpp:82-130`）经 SPICE 做掩星/可见/侵入区间扫描（用于接触分析）。

#### 8.4.4 绘图类：XyPlot / OrbitPlot / OrbitView / GroundTrackPlot / OpenGlPlot / GroundTrack / OwnedPlot

- **`XyPlot`**（`class GMAT_API XyPlot : public Subscriber`，`XyPlot.hpp:41`）：XY 曲线图订阅者（驱动 GUI 曲线组件）。`mXParam/mYParams`（`XyPlot.hpp:155-156`）保存横/纵参数；`SetXParameter/AddYParameter`（`XyPlot.cpp:251/282`）在初始化阶段解析参数名；`Initialize`（`XyPlot.cpp:323`）建曲线；`Distribute`（`XyPlot.cpp:1758`）按 `mDataCollectFrequency` 抽点、`mUpdatePlotFrequency` 刷屏；`PenUp/PenDown/MarkPoint/MarkBreak`（`XyPlot.cpp:1636-1727`）把不连续数据（如传播段切换）分成曲线段。参数表 `XVARIABLE/YVARIABLES/SHOW_GRID/DATA_COLLECT_FREQUENCY/UPDATE_PLOT_FREQUENCY/SHOW_PLOT/DRAWING`（`XyPlot.hpp:190-210`）。
- **`OrbitPlot`**（`class GMAT_API OrbitPlot : public Subscriber`，`OrbitPlot.hpp:39`）：3D 轨道图中间基类（`OrbitView`/`GroundTrackPlot` 之祖）。持有视图坐标系 `mViewCoordSystem`（`OrbitPlot.hpp:152`）、对象数组 `mObjectArray/mAllSpArray`（`OrbitPlot.hpp:158-159`）与显隐标志 `mDrawOrbitArray/mDrawObjectArray`（`OrbitPlot.hpp:160-161`）；`GetSpacePointList/GetSpacecraftList/GetNonSpacecraftList`（`OrbitPlot.hpp:47-49`）供 GUI 列出可选对象；`SetOrbitColorChanged/SetSegmentOrbitColor`（`OrbitPlot.hpp:134-145`）处理颜色变更通知。
- **`OrbitView`**（`class GMAT_API OrbitView : public OrbitPlot`，`OrbitView.hpp:39`）：当前主力的 3D 轨道视图。新增视点控制：`mViewPointRefObj/mViewPointObj/mViewDirectionObj/mViewUpCoordSystem`（`OrbitView.hpp:153-156`）、`mViewPointRefVector/mViewPointVecVector/mViewDirectionVector`（`OrbitView.hpp:175-177`）与 `mViewScaleFactor`（`OrbitView.hpp:179`）；`GetViewVector/SetVector`（`OrbitView.hpp:47-48`）。显示选项 `mEclipticPlane/mXYPlane/mWireFrame/mOverlapPlot/mUseInitialView/mAxes/mGrid/mSunLine/mEnableStars/mEnableConstellations/mStarCount`（`OrbitView.hpp:157-184`）对应参数表 `SHOW_LABELS/VIEWPOINT_REF/VIEWPOINT_VECTOR/VIEW_DIRECTION/VIEW_SCALE_FACTOR/VIEW_UP_COORD_SYSTEM/VIEW_UP_AXIS/CELESTIAL_PLANE/ECLIPTIC_PLANE/XY_PLANE/WIRE_FRAME/AXES/GRID/EARTH_SUN_LINES/SUN_LINE/OVERLAP_PLOT/STAR_COUNT/ENABLE_STARS/ENABLE_CONSTELLATIONS/MIN_FOV/MAX_FOV/INITIAL_FOV`（`OrbitView.hpp:191-224`）。`Distribute`（`OrbitView.hpp:231-232`）每步把航天器位置加入绘图缓冲，`UpdateSolverData`（`OrbitView.hpp:146`）在求解迭代时刷新。
- **`GroundTrackPlot`**（`GroundTrackPlot.hpp:36`）：地面轨迹图（经纬度图），同样基于 OrbitPlot。
- **`OpenGlPlot`**（`class GMAT_API OpenGlPlot : public Subscriber`，`OpenGlPlot.hpp:39`）：早期 OpenGL 轨道图（已被 OrbitView 取代，保留兼容）；提供 `GetColor/SetColor`（`OpenGlPlot.hpp:51-53`）等颜色管理。
- **`GroundTrack`**（`class GMAT_API GroundTrack : public Subscriber`，`GroundTrack.hpp:43`）：地面轨迹**数据**订阅者（非绘图），计算星下点经纬度供 GUI 或 API 使用。
- **`OwnedPlot`**（`class GMAT_API OwnedPlot : public Subscriber`，`OwnedPlot.hpp:54`）：求解器自有的进度图（Solver 成员 `plotter` 的类型，`Solver.hpp:328`），用于目标函数/约束收敛过程可视化。

#### 8.4.5 其余订阅者

- **`MessageWindow`**（`MessageWindow.hpp:37`）：消息窗口订阅者（把 `MessageInterface` 输出送到 GUI 窗口）。
- **`DynamicDataDisplay`**（`DynamicDataDisplay.hpp:43`）：动态数据显示（GUI 的数值面板），配合 `DynamicDataStruct.hpp` 的 `struct DDD`（`DynamicDataStruct.hpp:30-44`，含 `paramName/refObjectName/paramWrapper/paramValue/warnLowerBound/critLowerBound/...`）。
- **`DynamicDataInterface.hpp/.cpp`**：**两个 0 字节空文件**（pwsh 实测 `Length = 0`），占位遗留。
- **`SubscriberException.hpp`**：`class SubscriberException : public BaseException`（仅头文件）。

### 8.5 coordsystem 目录（76 个文件）

#### 8.5.1 CoordinateBase / CoordinateSystem / AxisSystem

- **`CoordinateBase`**（`class GMAT_API CoordinateBase : public GmatBase`，`CoordinateBase.hpp:56`）：坐标系与轴系的公共基类。定义 `GmatCoordinate::ParameterUsage` 枚举 `NOT_USED/OPTIONAL_USE/REQUIRED/REQUIRED_UNMODIFIABLE`（`CoordinateBase.hpp:47-53`）——每个轴系通过 `UsesEopFile/UsesItrfFile/UsesEpoch/UsesPrimary/UsesSecondary/UsesXAxis/...` 虚函数（`CoordinateBase.hpp:95-104`，全部纯虚）声明「我依赖哪些参数」；`SetOrigin/SetJ2000Body/SetSolarSystem`（`CoordinateBase.hpp:70-86`）管理原点与 J2000 天体。
- **`AxisSystem`**（`class GMAT_API AxisSystem : public CoordinateBase`，`AxisSystem.hpp:46`）：轴系基类，**本章数值最重的文件之一**。核心纯虚 `CalculateRotationMatrix(const A1Mjd &atEpoch)`（`AxisSystem.hpp:205-207`）由每个轴系实现，计算从本轴系到 MJ2000Eq 基系的 `rotMatrix` 与 `rotDotMatrix`（`AxisSystem.hpp:219-222`）。FK5 归算的公共骨架（供需要它的轴系用）：`InitializeFK5`（`AxisSystem.hpp:324`）、`ComputePrecessionMatrix`（`:326`）、`ComputeNutationMatrix`（`:327-331`）、`ComputeSiderealTimeRotation`（`:332-338`）、`ComputeSiderealTimeDotRotation`（`:339-342`）、`ComputePolarMotionRotation`（`:343-344`），中间量缓存 `lastPREC/lastNUT/lastST/lastPM/lastDPsi`（`:270-291`）与性能缓存 `PREC/NUT/ST/STderiv/PM`（`:287-291`）——同一历元重复求值不重算。数据源文件指针 `eop/itrf/icrfFile`（`:255-256, 316`）与章动/行星项表 `a/ap/A..F/Ap..Fp`（`:280-284`）。`RotateToBaseSystem/RotateFromBaseSystem`（`AxisSystem.hpp:119-143`）是坐标变换的旋转半边（含 GmatTime 重载）。
- **`CoordinateSystem`**（`class GMAT_API CoordinateSystem : public CoordinateBase`，`CoordinateSystem.hpp:44`）：**Origin + AxisSystem 的组合**。成员 `AxisSystem *axes`（`CoordinateSystem.hpp:261`）；所有 `UsesXxx` 查询转发给 `axes`（`CoordinateSystem.hpp:63-73`）。`Initialize`（`CoordinateSystem.cpp:1084-1117`）把 `solar/originName/j2000BodyName` 灌入 axes 并 `axes->Initialize()`；`ToBaseSystem/FromBaseSystem`（`CoordinateSystem.cpp:1158/1417`）是核心换算：**先旋转后平移**——`axes->RotateToBaseSystem(epoch, inState, internalState)` 得基系方向，再 `TranslateToBaseSystem(epoch, internalState, finalState)` 把原点从本系原点平移到基系原点（`CoordinateSystem.cpp:1172-1192`）；`coincident=true` 时跳过平移（两系原点重合）。`CreateLocalCoordinateSystem`（`CoordinateSystem.hpp:211-215`）静态工厂：按 `axesType` 建局部坐标系。参数 `AXES/UPDATE_INTERVAL/OVERRIDE_ORIGIN_INTERVAL/SPICE_FRAME_ID/EPOCH`（`CoordinateSystem.hpp:223-232`）；`SetSpiceFrameId` 供 SpiceAxes 使用。

#### 8.5.2 惯性轴系（InertialAxes 家族）

- **`InertialAxes`**（`class GMAT_API InertialAxes : public AxisSystem`，`InertialAxes.hpp:41`）：惯性轴系基类——`rotMatrix` 与历元无关（或只含固定偏置）。
- **`MJ2000EqAxes`**（`MJ2000EqAxes.hpp:41`）：**基系本身**，`CalculateRotationMatrix` 置恒等（`MJ2000EqAxes.cpp`）；`MJ2000EcAxes`（`:41`）：J2000 黄道系，含黄赤交角固定旋转。
- **`ICRFAxes`**（`ICRFAxes.hpp:42`）：ICRF 系，与 FK5 的差异经 `ICRFFile` 的 Euler 旋转向量补（`AxisSystem.hpp:316-320` 的 `icrfFile/icrfToFK5`）。
- **`TOEEqAxes`/`TOEEcAxes`**（`TOEEqAxes.hpp:41`/`TOEEcAxes.hpp:41`）：真赤道/真黄道（历元 2000 定向，含岁差章动到 J2000 的净旋转，作者 Kenton Gee）。
- **`MOEEqAxes`/`MOEEcAxes`**（`MOEEqAxes.hpp:41`/`MOEEcAxes.hpp:41`）：平赤道/平黄道。
- **`BodyInertialAxes`**（`BodyInertialAxes.hpp:41`）：天体惯性系（如火星惯性系，基于天体的固定指向）。

#### 8.5.3 动力轴系（DynamicAxes 家族）

- **`DynamicAxes`**（`class GMAT_API DynamicAxes : public AxisSystem`，`DynamicAxes.hpp:42`）：动力轴系基类——`rotMatrix` 随历元变化，纯标记/公共层（参数计数即 `AxisSystemParamCount`，`DynamicAxes.hpp:66-69`）。
- **`MeanOfDateAxes`**（`MeanOfDateAxes.hpp:42`）：平赤道/平黄道系；`MODEqAxes`（`:41`）/`MODEcAxes`（`:41`）叶子。
- **`TrueOfDateAxes`**（`TrueOfDateAxes.hpp:42`）：真赤道/真黄道系；`TODEqAxes`（`:41`）/`TODEcAxes`（`:41`）叶子；`TEMEAxes`（`TEMEAxes.hpp:39`）：真赤道**平春分点**系（True Equator Mean Equinox）。
- **`BodyFixedAxes`**（`class GMAT_API BodyFixedAxes : public DynamicAxes`，`BodyFixedAxes.hpp:48`）：**体固连系**（地球/月球/火星固定系），数值最重的轴系。`CalculateRotationMatrix`（`BodyFixedAxes.cpp:423-1020`）分两大分支：
  - 原点是 Spacecraft：取 `sc->GetAttitude(epoch)` 的惯性→体 DCM，`rotMatrix = dcm.Transpose()`（体→惯性，`BodyFixedAxes.cpp:464-470`）；角速度经 `skew` 矩阵构造 `Rdot`（`BodyFixedAxes.cpp:504-512`）；姿态模型不提供速率时按 `allowNoRates` 置零矩阵或抛异常（`BodyFixedAxes.cpp:473-488`）。
  - 原点是天体：走 FK5 归算 + SPICE 分支——`spiceIdSet || RotationDataSource()==SPICE_KERNEL` 时用 `CalculateSpiceFrameRotationMatrix`（`BodyFixedAxes.cpp:550-552`），否则 `ComputePrecessionMatrix → ComputeNutationMatrix → ComputeSiderealTimeRotation → ComputeSiderealTimeDotRotation → ComputePolarMotionRotation`（`BodyFixedAxes.cpp:664-671`），最后校验行列式（`BodyFixedAxes.cpp:738`）。
- **`EquatorAxes`**（`EquatorAxes.hpp:42`）：某天体赤道面系（含 `DeFile *theDeFile`，`EquatorAxes.hpp:76`，用 DE 星历定赤道）。
- **`TopocentricAxes`**（`TopocentricAxes.hpp:48`）：站心系（以 GroundStation/体固连点为原点，X 朝东或由 X/Y 轴定义）。
- **`ObjectReferencedAxes`**（`ObjectReferencedAxes.hpp:41`）：**以两个对象定义轴系**——由 `SetPrimaryObject/SetSecondaryObject/SetXAxis/SetYAxis/SetZAxis`（`ObjectReferencedAxes.hpp:59-63`）确定坐标轴的指向。三个叶子：
  - `BodySpinSunAxes`（`BodySpinSunAxes.hpp:42`）：天体自旋轴—太阳方向系。
  - `GeocentricSolarEclipticAxes`（`GeocentricSolarEclipticAxes.hpp:42`）：地心太阳黄道系（GSE）。
  - `GeocentricSolarMagneticAxes`（`GeocentricSolarMagneticAxes.hpp:42`）：地心太阳磁系（GSM）。
- **`LocalAlignedConstrainedAxes`**（`LocalAlignedConstrainedAxes.hpp:41`）：局部对齐约束系——X/Y/Z 轴由用户相对 primary/secondary/reference 对象指定（`LocalAlignedConstrainedAxes.hpp:67-72` 重写 `UsesReferenceObject/SetReferenceObject`）。
- **`ITRFAxes`**（`ITRFAxes.hpp:43`）：ITRF 地固系（IERS 2010 约定，走 FK5 归算+极移）。
- **`SpiceAxes`**（`class GMAT_API SpiceAxes : public AxisSystem`，`SpiceAxes.hpp:45`）：**任意 SPICE 帧轴系**——`SetSpiceFrameId`（`SpiceAxes.hpp:77`）指定 NAIF 帧名，`CalculateRotationMatrix` 经 CSPICE `pxform` 取旋转（`SpiceAxes.cpp`），前提是用户已加载所需内核。

#### 8.5.4 数据文件与转换工具

- **`IAUFile`**（`class GMAT_API IAUFile`，`IAUFile.hpp:39`）：单例，读 `IAU_SOFA.DAT`（`IAUFile.hpp:79`）的 IAU2000 数据表，`GetIAUData(epoch, iau, dim, order)`（`IAUFile.hpp:50`）按历元插值。
- **`ICRFFile`**（`class GMAT_API ICRFFile`，`ICRFFile.hpp:40`）：单例，读 `ICRF_Table.txt`（`ICRFFile.hpp:88`）的 ICRF Euler 旋转向量，`RotateFromICRFtoFK5/RotateFromFK5toICRF`（`ICRFFile.hpp:53-55`）做 FK5↔ICRF 状态旋转。
- **`ItrfCoefficientsFile`**（`class GMAT_API ItrfCoefficientsFile`，`ItrfCoefficientsFile.hpp:59`）：读 `NUTATION.DAT`/`NUT85.DAT`（`ItrfCoefficientsFile.hpp:64-65`）的章动/行星系数表；`GmatItrf::NutationTerms` 枚举 `NUTATION_1980/1996/2000`（`ItrfCoefficientsFile.hpp:45-50`）；`GetNutationTerms/GetPlanetaryTerms`（`ItrfCoefficientsFile.hpp:87-92`）输出傅里叶项供 `ComputeNutationMatrix` 使用。数据源注明来自 Vallado 的 celestrak 软件页（`ItrfCoefficientsFile.hpp:31-32`）。
- **`CoordinateConverter`**（`class GMAT_API CoordinateConverter`，`CoordinateConverter.hpp:43`）：**通用转换器**（不派生 GmatBase）。`Convert(epoch, inState, inCoord, outState, outCoord, forceComputation, omitTranslation)`（`CoordinateConverter.cpp:194/270` 等重载）算法：若两系基系统一，直接 `inCoord->ToBaseSystem` + `outCoord->FromBaseSystem`；若基系统不同（FK5 vs ICRF），先 `ConvertFromBaseToBase`（`CoordinateConverter.cpp:805/843`）经 `RotateFromICRFtoFK5`（`CoordinateConverter.cpp:1019`）补 ICRF→FK5 旋转。记录 `lastRotMatrix/lastRotDotMatrix`（`CoordinateConverter.hpp:112-113`）供调用方取最近一次旋转矩阵。这是 `OrbitData`、`EphemerisWriter`、`BodyFixedPoint` 等所有状态换算的公共工具。
- **`CoordinateTransformation`**（`CoordinateTransformation.hpp:39`）：静态工具 `TransformState(epoch, oldFrame, stateWrtOldFrame, newFrame)`（`CoordinateTransformation.hpp:42-43`），基于轴系做状态变换（含速度项的框架旋转修正）。
- **`CoordinateTranslation`**（`CoordinateTranslation.hpp`）：平移工具（原点平移），与 `CoordinateTransformation` 配套。
- **`TransformUtil`**（`class GMAT_API TransformUtil`，`TransformUtil.hpp:42`）：静态工具：`TransformOrbitalState`（`TransformUtil.hpp:45-49`，任意状态表示/坐标系间转换，支持 `"Spline"` 历表平滑）、`CalculateOrbitalJacobian`（`TransformUtil.hpp:50-55`，轨道状态对输入/时间偏导，供估计器用）。
- **`CoordinateSystemException.hpp/.cpp`**：`class CoordinateSystemException : public BaseException`（`CoordinateSystemException.hpp:37`）。

### 8.6 interface 目录（8 个文件）

- **`Interface`**（`class GMAT_API Interface : public GmatBase`，`src/base/interface/Interface.hpp:36`）：外部接口基类，只有 `Open(name)/Close(name)`（`Interface.hpp:43-44`）。当前无派生类（MATLAB 通道不经过它），保留接口抽象。
- **`GmatInterface`**（`class GMAT_API GmatInterface`，`GmatInterface.hpp:39`）：**MATLAB 接口单例**（`Instance()`，`GmatInterface.hpp:42`）。工作原理：`OpenScript/ClearScript/PutScript`（`GmatInterface.hpp:45-47`）把 MATLAB 侧传来的脚本写进 `std::stringstream mStringStream`（`GmatInterface.hpp:77`）并用 `RedirectBuffer` 把 `std::cin` 重定向到该流（`GmatInterface.hpp:72-73`），从而让 GMAT 解释器从字符串流读脚本（`BuildObject/UpdateObject/RunScript`，`GmatInterface.hpp:48-50`）；`ExecuteCallback/RegisterCallbackServer/PutCallbackData/GetCallbackResults`（`GmatInterface.hpp:53-58`）实现 MATLAB→GMAT 回调（`callbackObj` 为 `GmatBase*`，`GmatInterface.hpp:83`）；`GetGmatObject/GetParameter`（`GmatInterface.hpp:61-63`）把对象/参数序列化为字符串返回 MATLAB。外部优化器（8.3.3）依赖它。
- **`SocketServer`**（`class SocketServer`，`SocketServer.hpp:59`）：套接字服务器（localhost:3000，`SocketServer.hpp:55-56`）。`RunServer/OnAccept/RunRequest`（`SocketServer.hpp:75-77`）接受客户端；`OnRequest(char*)`（`SocketServer.hpp:72`）处理请求；`OnPoke`（`SocketServer.hpp:73`）接收数据推送。Windows 用 `winsock2.h`、Unix 用 `sys/socket.h`（`SocketServer.hpp:34-52`）。用于外部进程（如旧 MATLAB 连接）与 GMAT 通信。
- **`InterfaceException.hpp/.cpp`**：`class InterfaceException : public BaseException`。

### 8.7 api 目录（10 个文件）

- **`ApiClass`**（`class GMAT_API ApiClass`，`ApiClass.hpp:34`）：近空基类（仅构造/析构），API 对象体系的地基（当前无实际行为）。
- **`APIFunctions.hpp/.cpp`**：**顶层 API 函数集**（C 风格自由函数，全部 `GMAT_API` 导出），分四组（签名见 `APIFunctions.hpp:44-93`）：
  1. 查询类：`Help/ShowObjects/ShowClasses/ShowObjectsForID/ShowClassesForID/Exists/GetObject/GetSolarSystem/GetCommands/GetNestedCommands`（`APIFunctions.hpp:44-53`）；
  2. 脚本工作流：`LoadScript/LoadInclude/RunScript/SaveScript/GetRuntimeObject/GetRunSummary/Execute`（`APIFunctions.hpp:55-63`）；
  3. 引擎访问：`Setup/Construct/Copy/Initialize/Update/Clear/UseLogFile/EchoLogFile`（`APIFunctions.hpp:66-80`）——`Construct(type, name, extraData...)` 是 API 侧的对象工厂（内部经 `Moderator` 与工厂）；
  4. 解释器访问：`Command/DeleteCommand`（`APIFunctions.hpp:83-84`）。
  内部辅助 `ProcessParameters/ProcessUpdateParameters`（`APIFunctions.hpp:88-93`）把 `extraData` 键值串解析后写进对象参数。
- **`APIMessageReceiver`**（`class APIMessageReceiver : public MessageReceiver`，`APIMessageReceiver.hpp:42`）：**API 模式的消息接收器单例**（`Instance()`，`APIMessageReceiver.hpp:45`），替代 GUI 的 `ConsoleMessageReceiver`：`ShowMessage/LogMessage/PopupMessage`（`APIMessageReceiver.hpp:47-60`）写入 `messageQueue`（`APIMessageReceiver.hpp:82`）与 `logFile`（`APIMessageReceiver.hpp:89-92`），API 宿主（Python/Java 等）可 `GetMessage` 拉取。
- **`HelpSystem`**（`class GMAT_API HelpSystem`，`HelpSystem.hpp:44`）：**API 帮助系统单例**。`BuildHelp(helpfile)`（`HelpSystem.hpp:66`）解析帮助文件，`itemHelp` map（`HelpSystem.hpp:58`）存主题→行列表；`Help(forItem)`（`HelpSystem.hpp:49`）返回文本。`ProcessOnlineCommentBlock`（`HelpSystem.hpp:68`）把源码在线注释块转成帮助条目。
- **`APIException.hpp/.cpp`**：`class APIException : public BaseException`。

### 8.8 spice 目录（18 个文件，需 `__USE_SPICE__` 编译）

SPICE 子系统把 GMAT 对象桥接到 NAIF CSPICE。注意：`src/base/spice/` 自身无 `__USE_SPICE__` 宏，但包含 `SpiceUsr.h`/`SpiceZfc.h`（`SpiceInterface.hpp:60-63`、`SpiceKernelWriter.hpp:67-70`）；工程级开关（`__USE_SPICE__`）出现在消费方（如 `EphemManager.hpp:41-43`、`BodyFixedPoint.hpp:47-49`），构建脚本按开关决定是否编译本目录。

- **`SpiceInterface`**（`class GMAT_API SpiceInterface`，`SpiceInterface.hpp:68`）：CSPICE 桥接基类。静态内核管理：`LoadKernel/LoadKernels/UnloadKernel/UnloadAllKernels/IsLoaded`（`SpiceInterface.cpp:322/409/428/519/571`），已加载内核表 `loadedKernels`（`SpiceInterface.hpp:122`）；`FindKernel`（`SpiceInterface.cpp:834`）按 `FileManager` 的路径配置解析内核全路径。时间换算 `SpiceTimeToA1/A1ToSpiceTime`（`SpiceInterface.cpp:716/741`，经 `TimeSystemConverter`）；`GetNaifID`（`SpiceInterface.cpp:674`）对象名→NAIF ID；`IsValidKernel`（`SpiceInterface.cpp:137`）按类型校验内核合法性（用 SPICE 的 `spkobj_c` 等探测）；合法的光行差标志表 `VALID_ABERRATION_FLAGS[9]` 与帧表 `VALID_FRAMES[12]`（`SpiceInterface.hpp:109-111`）。
- **`SpiceKernelReader`**（`class GMAT_API SpiceKernelReader : public SpiceInterface`，`SpiceKernelReader.hpp:52`）：读取器基类，持有 SPICE 侧数据指针 `objectNameSPICE/naifIDSPICE/observerNaifIDSPICE/etSPICE/referenceFrameSPICE`（`SpiceKernelReader.hpp:98-106`）。
  - **`SpiceOrbitKernelReader`**（`SpiceOrbitKernelReader.hpp:46`）：读 SPK 星历，`GetEphemerisState` 等经 CSPICE `spkezr_c` 取状态（含光行差校正）。
  - **`SpiceAttitudeKernelReader`**（`SpiceAttitudeKernelReader.hpp:43`）：读 CK 姿态，`GetAttitude` 经 `ckgp_c` 取四元数+角速度。
- **`SpiceKernelWriter`**（`class GMAT_API SpiceKernelWriter : public SpiceInterface`，`SpiceKernelWriter.hpp:72`）：写入器基类（当前空壳，子类实现具体格式）。
  - **`SpiceOrbitKernelWriter`**（`SpiceOrbitKernelWriter.hpp:73`）：**写 SPK**（Data Type 13，Hermite 不等步长插值，几何无光行差）。构造参数含对象/中心体名与 NAIF ID、插值阶数 `deg`（默认 7）、帧 `"J2000"`（`SpiceOrbitKernelWriter.hpp:76-79`）；`WriteSegment`（`:86-87`）写一段（`spkw13_c`）；`AddMetaData/FinalizeKernel`（`:88-90`）经临时文本文件 `GMATtmpSPKcmmnt<objName>.txt` 把注释写入 SPK（`SpiceOrbitKernelWriter.hpp:47-53`，`tmpTxtFile` 成员 `:133`）；文件名形如 `<objName>-<yyyymmdd>-<data-type>-<n>.bsp`（`:38-46`）。
  - **`SpiceAttitudeKernelWriter`**（`SpiceAttitudeKernelWriter.hpp:74`）：写 CK 姿态内核（`ckw01_c` 等）。
  - **`SpiceFrameKernelWriter`**（`SpiceFrameKernelWriter.hpp:48`）：写 FK 帧内核。
  - **`SpiceSCClockKernelWriter`**（`SpiceSCClockKernelWriter.hpp:49`）：写 SCLK 航天器时钟内核。
- 消费关系：`EphemWriterSPK` 与 `AttitudeWriterCK`（subscriber 目录）分别委托 `SpiceOrbitKernelWriter`/`SpiceAttitudeKernelWriter`（`EphemWriterSPK.hpp:33`、`AttitudeWriterCK.hpp:36` 前向声明）；`SpiceAxes`、`BodyFixedAxes`、`BodyFixedPoint`、`EphemManager` 经 `SpiceInterface` 读内核。

### 8.9 asset 目录（6 个文件）

- **`BodyFixedPoint`**（`class GMAT_API BodyFixedPoint : public SpacePoint`，`src/base/asset/BodyFixedPoint.hpp:52`）：**体固连点基类**——固定在某天体表面上的点（地面站/中继点之祖）。数据：`cBodyName/theBody`（附着天体，`BodyFixedPoint.hpp:151-153`）、`meanEquatorialRadius/flattening`（`:155-157`）、`stateType/horizon`（地理坐标类型/地平类型，`:163-165`）、`location[3]/bfLocation[3]`（地理坐标/体固连直角坐标，`:167-169`）。关键虚函数：`GetMJ2000State(const A1Mjd&)`（`:125-127`）把体固连位置经 `BodyFixedStateConverter`/`CoordinateConverter` 换算到 MJ2000（含自转相位）；`GetBodyFixedLocation/GetSphericalLocation`（`:133-134`）；`GetBodyFixedCoordinateSystem`（`:135-136`，懒创建体固连坐标系）；`IsValidID`（`:139`，校验 `"001"` 式 3 位 NAIF ID 字符串）。参数表含 `CentralBody/Latitude/Longitude/Altitude/...`（`BodyFixedPoint.cpp` 实现，枚举续接 `SpacePointParamCount`）。
- **`GroundstationInterface`**（`class GMAT_API GroundstationInterface : public BodyFixedPoint`，`GroundstationInterface.hpp:40`）：**地面站接口**，纯虚析构（`GroundstationInterface.hpp:47`）防止直接实例化；纯虚 `IsValidElevationAngle(state_sez)`（`:52`，SEZ 系仰角有效性检查）、`CreateErrorModelForSignalPath(scName, scId)`（`:53-54`，为信号路径建误差模型）、`GetErrorModelMap`（`:55-56`）。真实地面站（`GroundStation`）在插件/其他库（libStation）中实现并派生它——本目录只留接口层。
- **`AssetException.hpp/.cpp`**：`class AssetException : public BaseException`。

### 8.10 configs 目录（8 个文件）

- **`ConfigManager`**（`class GMAT_API ConfigManager`，`src/base/configs/ConfigManager.hpp:73`）：**配置管理器单例**（`Instance()`，`ConfigManager.hpp:76`），管理「沙箱克隆前」的已配置对象（头注释 `ConfigManager.hpp:70-72`：管理被克隆进沙箱之前的配置对象）。约 20 个 `AddXxx`（`AddObject/AddSpacecraft/AddSubscriber/AddParameter/AddSolver/AddFunction/AddCoordinateSystem/AddMeasurementModel/...`，`ConfigManager.cpp:170-906`）按类型注册；`GetXxx(name)` 取对象（`GetSpacecraft/GetSubscriber/GetParameter/GetSolver/GetCoordinateSystem/...`，`ConfigManager.hpp:144-174`）；`GetListOfItems/GetListOfAllItems`（`ConfigManager.cpp:1014/1221`）供 GUI 列出可用对象；**`AddClone(name, cloneName)`**（`ConfigManager.cpp:1290`）与 `ReconfigureItem`（`ConfigManager.cpp:2120`）实现"对象已存在则克隆复用"；`RenameItem/RelatedNameChange`（`ConfigManager.cpp:1484/2890`）处理重命名传播；`RemoveAllItems/RemoveItem`（`ConfigManager.cpp:1836/1906`）清理。内部是一张 `ObjectMap`（名字→GmatBase*，`ConfigManager.hpp:178`）加按类型索引的多张表。
- **`ItemManager`**（`class GMAT_API ItemManager`，`ItemManager.hpp:41`）：条目管理器基类——纯虚析构（`ItemManager.hpp:46`）+ `virtual void UpdateObjects(ofType)`（`ItemManager.hpp:48`），是 `PluginItemManager` 与 GUI 的 `GuiItemManager`（wxWidgets 侧）的公共接口（`ItemManager.hpp:38-40`）。
- **`PluginItemManager`**（`class GMAT_API PluginItemManager : public ItemManager`，`PluginItemManager.hpp:44`）：**插件条目管理器单例**——对 GUI 插件组件扮演 `GuiItemManager` 角色（`PluginItemManager.hpp:41-43`）。`AddWidget/RemoveWidget`（`PluginItemManager.hpp:50-51`）登记插件控件；`UpdateObjectList/RenameObject`（`PluginItemManager.hpp:54-57`）响应对象增删改名；`GetListOfObjects(ofType)`（`PluginItemManager.hpp:61`）供插件查询；成员 `std::vector<GmatWidget*> widgets`（`PluginItemManager.hpp:65`）。
- **`ConfigManagerException.hpp/.cpp`**：`class ConfigManagerException : public BaseException`。

## 三、关键设计模式与数据流

**1. 参数的「多继承双半」模式。** 系统参数 = `RealVar`（参数身份）+ `XxxData`（求值引擎）：`OrbitReal : public RealVar, public OrbitData`（`OrbitReal.hpp:40`）。叶子类（`KepSMA` 等 146 个）只有 ~40 行，把分量 ID 传给装配层，`Evaluate()` 一行转发到 `OrbitData::GetXxxReal(itemId)`。这套「薄叶子 + 厚数据层」把开普勒/笛卡尔/球/春分点/Brouwer/Delaunay 等 15+ 元素集的换算全部收拢在 `OrbitData`，并经 `StateConversionUtil`（gmatutil，[第3章](CH03-math.md)）实现。数据层再以 `RefData` 基类统一「引用对象解析 → InitializeRefObjects → 换算 → 分量返回」生命周期。

**2. 参数的「默认拒绝」虚函数协议。** `Parameter` 的 `EvaluateReal/EvaluateRvector/EvaluateRmatrix/EvaluateString`（`Parameter.cpp:927-1041`）与 `GetReal/SetReal/...` 基类实现全部抛 `ParameterException`——叶子只重写自己支持的类型入口，其余保持抛异常，把「类型 × 参数」错配显式暴露。配合 `ParameterInfo` 单例的「类型串 → 能力位」注册表（`ParameterInfo.hpp:51-64`），GUI/报告系统无需实例化即可查询可绘图/可报告/可设标志。

**3. 函数执行的数据流（FOS/LOS/GOS + 调用栈）。** `CallFunction`/`FunctionRunner`（[第5章](CH05-command.md)）→ `FunctionManager::Execute`（`FunctionManager.cpp:913`）：`PrepareObjectMap` 合并 LOS+GOS（`:776-835`）→ 注入太阳系/瞬态力 → `SetInputElementWrapper` 逐实参绑定 → 重建 `ObjectInitializer` → `currentFunction->Initialize/Execute`。嵌套/递归经 `callStack/losStack` 与 `PushToStack/PopFromStack`（`:2514/2534`）做对象存储快照；`GmatFunction` 即 `UserDefinedFunction`，其函数内命令序列 `fcs` 由 `SetFunctionControlSequence` 挂接，函数结束后 `Finalize` 把函数内 Parameter 引用复位回全局订阅者（`UserDefinedFunction.cpp:246-292`）。

**4. 求解器状态机与「变量/目标」双通道。** `Solver` 定义 15 态状态机（`Solver.hpp:61-78`），`AdvanceState` 按态分派（`Solver.cpp:657-700`）；`Vary` 命令经 `SetSolverVariables/SetResultValue`（`Solver.hpp:190/229`）与求解器交换变量/目标。`DifferentialCorrector` 把「名义运行 → 扰动运行 → 差分建 Jacobian → 求逆 → 修正量限幅 → 更新变量」走成 `NOMINAL→PERTURBING→CALCULATING→CHECKINGRUN` 循环（`DifferentialCorrector.cpp:932-977`），并支持 Newton-Raphson/Broyden/ModifiedBroyden 三算法（`DifferentialCorrector.cpp:1132-1245`）。`ISolverListener::VariabledChanged`（`DifferentialCorrector.cpp:1452`）把每步变量值推给 GUI。

**5. 订阅者数据管道。** `Publisher`（[第2章](CH02-foundation.md)）→ `Subscriber::ReceiveData`（`Subscriber.cpp:435`）→ 虚函数 `Distribute`（`Subscriber.cpp:2121/2130`）→ 派生类输出。数据块结束/运行结束用 `FlushData/SetEndOfRun`（`Subscriber.cpp:470/485`）以空数据调用触发。订阅者按「元素包装器」求值：`ReportFile`/`XyPlot` 用 `yParamWrappers`（`Subscriber.hpp:237`）在 `Distribute` 里逐个 `EvaluateReal/EvaluateString` 并格式化；`EphemerisFile` 则把 `currState/currCov/currAccel/currQuat` 缓冲进 `EphemerisWriter`，由具体 writer 插值后按格式写出。

**6. 坐标系「旋转 + 平移」两段式换算。** `CoordinateSystem::ToBaseSystem`（`CoordinateSystem.cpp:1158-1192`）= `axes->RotateToBaseSystem`（轴系旋转到基系方向）+ `TranslateToBaseSystem`（原点平移到基系原点），`coincident` 时跳过平移；反向 `FromBaseSystem` 对称。`CoordinateConverter::Convert`（`CoordinateConverter.cpp:270`）在任意两系间换算，基系统不同（FK5↔ICRF）时经 `ConvertFromBaseToBase` 补 ICRF 旋转（`CoordinateConverter.cpp:805/1019`）。轴系侧，`AxisSystem::CalculateRotationMatrix` 纯虚（`AxisSystem.hpp:205-207`），FK5 归算五件套（岁差/章动/恒星时/恒星时率/极移，`AxisSystem.hpp:324-344`）带 `lastXxx` 历元缓存，同历元重复求值零成本（`AxisSystem.hpp:266-291`）。

**7. 单例矩阵。** 本章单例：`ParameterInfo`、`ConfigManager`、`PluginItemManager`、`GmatInterface`、`APIMessageReceiver`、`HelpSystem`、`IAUFile`、`ICRFFile`（数据文件类）。共同模式：私有构造 + `static Instance()` + 静态 `theInstance`/`instance` 成员。

## 四、文件清单附录

### 8.A parameter 目录（153 个文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/parameter/Parameter.hpp` | 参数抽象基类声明 | `Parameter : GmatBase`；`Evaluate*` 虚函数族、`GmatParam::ParameterKey/DepObject/CycleType` |
| `src/base/parameter/Parameter.cpp` | 参数基类实现 | 构造(`:102`)、`Evaluate()`(`:1087`)、`EvaluateReal`(`:927`)、`PARAMETER_TEXT`(`:51`) |
| `src/base/parameter/paramdefs.hpp` | 参数容器 typedef | `ParameterPtrArray/StringParamPtrMap/StringParamPtrPair` |
| `src/base/parameter/ParameterInfo.hpp/.cpp` | 参数注册表单例 | `Instance/Add/IsPlottable/IsReportable/IsSettable` |
| `src/base/parameter/ParameterDatabase.hpp/.cpp` | 参数数据库容器 | `Add/GetParameter/Remove/RenameParameter` |
| `src/base/parameter/ParameterException.hpp` | 参数异常（纯头） | `ParameterException : BaseException` |
| `src/base/parameter/ParameterDatabaseException.hpp` | 数据库异常（纯头） | `ParameterDatabaseException : BaseException` |
| `src/base/parameter/RealVar.hpp/.cpp` | Real 参数中间基类 | `RealVar : Parameter`；`mRealValue/VALUE` |
| `src/base/parameter/Variable.hpp/.cpp` | 脚本数值变量 | `Variable : RealVar`；`EvaluateReal`(`:193`) |
| `src/base/parameter/StringVar.hpp/.cpp` | 字符串变量基类 | `StringVar : Parameter`；`mStringValue` |
| `src/base/parameter/Array.hpp/.cpp` | 一/二维数组变量 | `Array : Parameter`；`SetSize/GetRmatrix/EvaluateRmatrix` |
| `src/base/parameter/RvectorVar.hpp/.cpp` | Rvector 变量基类 | `RvectorVar : Parameter`；`VECTOR_SIZE` |
| `src/base/parameter/Rmat33Var.hpp/.cpp` | 3×3 矩阵变量 | `Rmat33Var : Parameter` |
| `src/base/parameter/Rmat66Var.hpp/.cpp` | 6×6 矩阵变量 | `Rmat66Var : Parameter` |
| `src/base/parameter/Rvec3Var.hpp/.cpp` | 三维向量变量 | `Rvec3Var : Parameter` |
| `src/base/parameter/Rvec6Var.hpp/.cpp` | 六维向量变量 | `Rvec6Var : Parameter` |
| `src/base/parameter/RefData.hpp/.cpp` | 引用数据基类 | `RefData`；`ValidateRefObjects`(纯虚)、`mRefObjList` |
| `src/base/parameter/OrbitData.hpp/.cpp` | 轨道数据层 | `OrbitData : RefData`；`GetKepState`(`:722`)、`GetKepReal`(`:1168`) |
| `src/base/parameter/SpacecraftData.hpp/.cpp` | 航天器质量/硬件数据层 | `SpacecraftData : RefData`；`DRY_MASS..HW_R_SB_33` 枚举 |
| `src/base/parameter/TimeData.hpp/.cpp` | 时间数据层 | `TimeData : RefData`；`A1/TAI/TT/TDB/UTC` 枚举、`TimeSystemConverter` |
| `src/base/parameter/AttitudeData.hpp/.cpp` | 姿态数据层 | `AttitudeData : RefData`；`DCM_11..ATTITUDE_CONSTRAINT_TYPE_ID` |
| `src/base/parameter/BplaneData.hpp/.cpp` | B 平面数据层 | `BplaneData : RefData` |
| `src/base/parameter/BurnData.hpp/.cpp` | 点火数据层 | `BurnData : RefData`；瞬态力 |
| `src/base/parameter/EnvData.hpp/.cpp` | 环境数据层 | `EnvData : RefData` |
| `src/base/parameter/PlanetData.hpp/.cpp` | 行星数据层 | `PlanetData : RefData` |
| `src/base/parameter/OrbitReal.hpp/.cpp` | 轨道 Real 装配层 | `OrbitReal : RealVar, OrbitData`；`mItemId` |
| `src/base/parameter/OrbitRvec6.hpp/.cpp` | 轨道 Rvec6 装配层 | `OrbitRvec6 : Rvec6Var, OrbitData` |
| `src/base/parameter/OrbitRmat33.hpp/.cpp` | 轨道 Rmat33 装配层 | `OrbitRmat33 : Rmat33Var, OrbitData` |
| `src/base/parameter/OrbitRmat66.hpp/.cpp` | 轨道 Rmat66 装配层 | `OrbitRmat66 : Rmat66Var, OrbitData` |
| `src/base/parameter/OrbitTime.hpp/.cpp` | 轨道周期参数 | `OrbitTime : OrbitReal` |
| `src/base/parameter/AttitudeReal.hpp/.cpp` | 姿态 Real 装配层 | `AttitudeReal : RealVar, AttitudeData` |
| `src/base/parameter/AttitudeRmat33.hpp/.cpp` | 姿态矩阵装配层 | `AttitudeRmat33 : Rmat33Var, AttitudeData` |
| `src/base/parameter/AttitudeRvector.hpp/.cpp` | 姿态向量装配层 | `AttitudeRvector : RvectorVar, AttitudeData` |
| `src/base/parameter/AttitudeString.hpp/.cpp` | 姿态字符串装配层 | `AttitudeString : StringVar, AttitudeData` |
| `src/base/parameter/BallisticMassReal.hpp/.cpp` | 质量特性装配层 | `BallisticMassReal : RealVar, SpacecraftData` |
| `src/base/parameter/BurnReal.hpp/.cpp` | 点火装配层 | `BurnReal : RealVar, BurnData` |
| `src/base/parameter/BplaneReal.hpp/.cpp` | B 平面装配层 | `BplaneReal : RealVar, BplaneData` |
| `src/base/parameter/EnvReal.hpp/.cpp` | 环境装配层 | `EnvReal : RealVar, EnvData` |
| `src/base/parameter/HardwareReal.hpp/.cpp` | 硬件 Real 装配层 | `HardwareReal : RealVar, SpacecraftData` |
| `src/base/parameter/HardwareRvector.hpp/.cpp` | 硬件向量装配层 | `HardwareRvector : RvectorVar, SpacecraftData` |
| `src/base/parameter/HardwareString.hpp/.cpp` | 硬件字符串装配层 | `HardwareString : StringVar, SpacecraftData` |
| `src/base/parameter/PlanetReal.hpp/.cpp` | 行星装配层 | `PlanetReal : RealVar, PlanetData` |
| `src/base/parameter/TimeReal.hpp/.cpp` | 时间 Real 装配层 | `TimeReal : RealVar, TimeData` |
| `src/base/parameter/TimeString.hpp/.cpp` | 时间字符串装配层 | `TimeString : StringVar, TimeData` |
| `src/base/parameter/KeplerianParameters.hpp/.cpp` | 开普勒元素参数 | `KepSMA..ModKepElem` 15 类；`Evaluate`→`GetKepReal/GetKepState` |
| `src/base/parameter/CartesianParameters.hpp/.cpp` | 笛卡尔状态参数 | `CartX..CartState` 7 类 |
| `src/base/parameter/SphericalParameters.hpp/.cpp` | 球坐标参数 | `SphRMag..SphAzFpaElem` 10 类 |
| `src/base/parameter/EquinoctialParameters.hpp/.cpp` | 春分点元素参数 | `EquinSma..EquinState` 13 类（含 Dot 变体） |
| `src/base/parameter/ModEquinoctialParameters.hpp/.cpp` | 改进春分点参数 | `ModEquinP..ModEquinState` 7 类 |
| `src/base/parameter/AlternateEquinoctialParameters.hpp/.cpp` | 替代春分点参数 | `AltEquinP/AltEquinQ/AltEquinState` |
| `src/base/parameter/DelaunayParameters.hpp/.cpp` | Delaunay 元素参数 | `Dela_l..DelaState` 7 类 |
| `src/base/parameter/BrouwerMeanLongParameters.hpp/.cpp` | Brouwer 长周期参数 | `BLlongSMADP..BLlongState` 7 类 |
| `src/base/parameter/BrouwerMeanShortParameters.hpp/.cpp` | Brouwer 短周期参数 | `BLshortSMAP..BLshortState` 7 类 |
| `src/base/parameter/PlanetodeticParameters.hpp/.cpp` | 行星大地坐标参数 | `PldRMAG..PldState` 7 类 |
| `src/base/parameter/AngularParameters.hpp/.cpp` | 角动量/β 角参数 | `SemilatusRectum..DLA` 8 类 |
| `src/base/parameter/OrbitalParameters.hpp/.cpp` | 拱点/周期/能量参数 | `VelApoapsis..Energy` 7 类 |
| `src/base/parameter/BplaneParameters.hpp/.cpp` | B 平面参数 | `BdotT/BdotR/BVectorMag/BVectorAngle` |
| `src/base/parameter/IncomingAsymptoteParameters.hpp/.cpp` | 入射渐近线参数 | `IncAsymRadPer..IncAsymState` 6 类 |
| `src/base/parameter/OutgoingAsymptoteParameters.hpp/.cpp` | 出射渐近线参数 | `OutAsymRadPer..OutAsymState` 6 类 |
| `src/base/parameter/TimeParameters.hpp/.cpp` | 时间参数 | `CurrA1MJD..ElapsedSecsFromStart` 15 类 |
| `src/base/parameter/AttitudeParameters.hpp/.cpp` | 姿态参数 | `DCM11..AttitudeConstraintType` 40 类 |
| `src/base/parameter/PlanetParameters.hpp/.cpp` | 行星位置参数 | `MHA/Longitude/Altitude/Latitude/LST` |
| `src/base/parameter/BallisticMassParameters.hpp/.cpp` | 质量特性参数 | `DryMass..AtmosDensityScaleFactorSigma` 32 类 |
| `src/base/parameter/HardwareParameters.hpp/.cpp` | 硬件参数 | `FuelMass..PlateZ` 60 类 |
| `src/base/parameter/BurnParameters.hpp/.cpp` | 点火参数 | `ImpBurnElements/TotalMassFlowRate/TotalAcceleration/TotalThrust` |
| `src/base/parameter/OrbitStmParameters.hpp/.cpp` | 状态转移矩阵参数 | `OrbitStm/OrbitStmA/B/C/D` |
| `src/base/parameter/OrbitCovarianceParameters.hpp/.cpp` | 轨道协方差参数 | `OrbitErrorCovariance` |
| `src/base/parameter/NumberWrapper.hpp/.cpp` | 数字字面量包装器 | `NumberWrapper : ElementWrapper`；`value` |
| `src/base/parameter/StringWrapper.hpp/.cpp` | 字符串字面量包装器 | `StringWrapper : ElementWrapper` |
| `src/base/parameter/BooleanWrapper.hpp/.cpp` | 布尔字面量包装器 | `BooleanWrapper : ElementWrapper` |
| `src/base/parameter/OnOffWrapper.hpp/.cpp` | 开关字面量包装器 | `OnOffWrapper : ElementWrapper` |
| `src/base/parameter/ObjectWrapper.hpp/.cpp` | 整对象包装器 | `ObjectWrapper : ElementWrapper`；`EvaluateObject` |
| `src/base/parameter/ParameterWrapper.hpp/.cpp` | Parameter 包装器 | `ParameterWrapper : ElementWrapper`；`param` |
| `src/base/parameter/VariableWrapper.hpp/.cpp` | Variable 包装器 | `VariableWrapper : ElementWrapper`；`var` |
| `src/base/parameter/ArrayWrapper.hpp/.cpp` | Array 整体包装器 | `ArrayWrapper : ElementWrapper` |
| `src/base/parameter/ArrayElementWrapper.hpp/.cpp` | 数组元素包装器 | `ArrayElementWrapper : ElementWrapper`；`row/column` 子包装器 |
| `src/base/parameter/StringObjectWrapper.hpp/.cpp` | 字符串对象包装器 | `StringObjectWrapper : ElementWrapper` |
| `src/base/parameter/ObjectPropertyWrapper.hpp/.cpp` | 对象字段包装器 | `ObjectPropertyWrapper : ElementWrapper`；`object/propID`、`TakeRequiredAction` |
| `src/base/parameter/ExpressionParser.hpp/.cpp` | 简单表达式解析器 | `EvalExp/EvalTwoTerms/EvalParenExp`（遗留） |

### 8.B function 目录（40 个文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/function/Function.hpp/.cpp` | 函数抽象基类 | `Function : GmatBase`；`Initialize/Execute/Finalize`、`FUNCTION_PATH/INPUT/OUTPUT` |
| `src/base/function/ObjectManagedFunction.hpp/.cpp` | 对象管理函数中间基类 | `ObjectManagedFunction : Function`；`inputArgMap/outputArgMap/objectStore` |
| `src/base/function/BuiltinGmatFunction.hpp/.cpp` | 内建函数基类 | `BuiltinGmatFunction : ObjectManagedFunction` |
| `src/base/function/UserDefinedFunction.hpp/.cpp` | 用户脚本函数（GmatFunction 载体） | `UserDefinedFunction : ObjectManagedFunction`；`fcs/functionObjectMap/automaticObjectMap` |
| `src/base/function/FunctionManager.hpp/.cpp` | 函数调用管理器 | `FunctionManager`；`Execute`(`:913`)、`PrepareObjectMap`(`:776`)、`PushToStack`(`:2514`) |
| `src/base/function/FunctionException.hpp/.cpp` | 函数异常 | `FunctionException : BaseException` |
| `src/base/function/Angle.hpp/.cpp` | 夹角内建函数 | `Angle : BuiltinGmatFunction`；`Execute`(`:187`) |
| `src/base/function/ConvertTime.hpp/.cpp` | 时间换算内建函数 | `ConvertTime : BuiltinGmatFunction` |
| `src/base/function/GetEphemStates.hpp/.cpp` | 读历表状态内建函数 | `GetEphemStates : BuiltinGmatFunction`；`ReadSpice/Code500/STK/CCSDS*File` |
| `src/base/function/GetLastState.hpp/.cpp` | 取末次发布状态函数 | `GetLastState : BuiltinGmatFunction` |
| `src/base/function/Num2str.hpp/.cpp` | 数字转字符串函数 | `Num2str : BuiltinGmatFunction` |
| `src/base/function/Pause.hpp/.cpp` | 暂停函数 | `Pause : BuiltinGmatFunction` |
| `src/base/function/QuaternionProduct.hpp/.cpp` | 四元数乘法函数 | `QuaternionProduct : BuiltinGmatFunction` |
| `src/base/function/QuaternionRotation.hpp/.cpp` | 四元数旋转函数 | `QuaternionRotation : BuiltinGmatFunction` |
| `src/base/function/QuaternionToDCM.hpp/.cpp` | 四元数→DCM 函数 | `QuaternionToDCM : BuiltinGmatFunction` |
| `src/base/function/RotationMatrix.hpp/.cpp` | 旋转矩阵构造函数 | `RotationMatrix : BuiltinGmatFunction` |
| `src/base/function/SetSeed.hpp/.cpp` | 随机种子设置函数 | `SetSeed : BuiltinGmatFunction` |
| `src/base/function/Sign.hpp/.cpp` | 符号函数 | `Sign : BuiltinGmatFunction` |
| `src/base/function/Str2num.hpp/.cpp` | 字符串转数字函数 | `Str2num : BuiltinGmatFunction` |
| `src/base/function/SystemTime.hpp/.cpp` | 系统时间函数 | `SystemTime : BuiltinGmatFunction` |

### 8.C solver 目录（21 个文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/solver/Solver.hpp/.cpp` | 求解器基类（状态机） | `Solver : GmatBase`；`SolverState/MachineMode/ExitMode`、`AdvanceState`(`:657`) |
| `src/base/solver/DifferentialCorrector.hpp/.cpp` | 微分改正器 | `DifferentialCorrector : Solver`；`AdvanceState`(`:853`)、`CalculateParameters`(`:1126`)、`CalculateJacobian`(`:1539`)、`InvertJacobian`(`:1576`) |
| `src/base/solver/Optimizer.hpp/.cpp` | 优化器基类 | `Optimizer : Solver`；`Optimize()=0`(`:141`)、`SetConstraintValues` |
| `src/base/solver/InternalOptimizer.hpp/.cpp` | 内嵌优化器接口 | `InternalOptimizer : Optimizer` |
| `src/base/solver/ExternalOptimizer.hpp/.cpp` | 外部优化器接口 | `ExternalOptimizer : Optimizer`；`FUNCTION_PATH`、`GmatInterface` |
| `src/base/solver/DerivativeModel.hpp/.cpp` | 导数模型基类 | `DerivativeModel`；`FORWARD/CENTRAL/BACKWARD_DIFFERENCE`、`Calculate()=0` |
| `src/base/solver/Jacobian.hpp/.cpp` | 雅可比计算 | `Jacobian : DerivativeModel` |
| `src/base/solver/Gradient.hpp/.cpp` | 梯度计算 | `Gradient : DerivativeModel` |
| `src/base/solver/LineSearch.hpp/.cpp` | 线搜索（占位） | `LineSearch`（未实现） |
| `src/base/solver/ISolverListener.hpp/.cpp` | 求解器监听接口 | `ISolverListener`；`VariabledChanged` 回调 |
| `src/base/solver/SolverException.hpp` | 求解器异常（纯头） | `SolverException : BaseException` |

### 8.D subscriber 目录（46 个文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/subscriber/Subscriber.hpp/.cpp` | 订阅者基类 | `Subscriber : GmatBase`；`ReceiveData`(`:435`)、`Distribute`(虚)、`SetElementWrapper`(`:873`) |
| `src/base/subscriber/ReportFile.hpp/.cpp` | 报告文件 | `ReportFile : Subscriber`；`WriteData`(`:370`)、`Initialize`(`:680`)、`Distribute`(`:1802`) |
| `src/base/subscriber/TextEphemFile.hpp/.cpp` | 文本历表文件 | `TextEphemFile : ReportFile` |
| `src/base/subscriber/EphemerisFile.hpp/.cpp` | 历表文件基类 | `EphemerisFile : Subscriber`；`CreateEphemerisWriter`(`:2023`)、`Distribute`(`:2965`) |
| `src/base/subscriber/EphemerisWriter.hpp/.cpp` | 历表写入器基类 | `EphemerisWriter`；`HandleOrbitData()=0`、`BufferOrbitData()=0` |
| `src/base/subscriber/EphemWriterWithInterpolator.hpp/.cpp` | 带插值写入器 | `EphemWriterWithInterpolator : EphemerisWriter`；`interpolator/epochsOnWaiting` |
| `src/base/subscriber/EphemWriterCCSDS.hpp/.cpp` | CCSDS 写入器 | `EphemWriterCCSDS : EphemWriterWithInterpolator` |
| `src/base/subscriber/EphemWriterCode500.hpp/.cpp` | Code500 写入器 | `EphemWriterCode500 : EphemWriterWithInterpolator` |
| `src/base/subscriber/EphemWriterSPK.hpp/.cpp` | SPK 写入器 | `EphemWriterSPK : EphemerisWriter`；`SpiceOrbitKernelWriter` |
| `src/base/subscriber/EphemWriterSTK.hpp/.cpp` | STK 写入器 | `EphemWriterSTK : EphemWriterWithInterpolator` |
| `src/base/subscriber/AttitudeWriterCK.hpp/.cpp` | CK 姿态写入器 | `AttitudeWriterCK : EphemerisWriter`；`SpiceAttitudeKernelWriter` |
| `src/base/subscriber/EphemManager.hpp/.cpp` | 历表管理器 | `EphemManager`；`Record/Provide/StopRecording`、`GetOccultationIntervals` |
| `src/base/subscriber/XyPlot.hpp/.cpp` | XY 曲线图 | `XyPlot : Subscriber`；`SetXParameter/AddYParameter`、`Distribute`(`:1758`) |
| `src/base/subscriber/OrbitPlot.hpp/.cpp` | 轨道图中间基类 | `OrbitPlot : Subscriber`；`mViewCoordSystem/mObjectArray` |
| `src/base/subscriber/OrbitView.hpp/.cpp` | 3D 轨道视图 | `OrbitView : OrbitPlot`；视点/显示参数表 |
| `src/base/subscriber/GroundTrackPlot.hpp/.cpp` | 地面轨迹图 | `GroundTrackPlot : OrbitPlot` |
| `src/base/subscriber/OpenGlPlot.hpp/.cpp` | OpenGL 轨道图（旧） | `OpenGlPlot : Subscriber`；`GetColor/SetColor` |
| `src/base/subscriber/GroundTrack.hpp/.cpp` | 地面轨迹数据订阅者 | `GroundTrack : Subscriber` |
| `src/base/subscriber/OwnedPlot.hpp/.cpp` | 求解器自绘图 | `OwnedPlot : Subscriber` |
| `src/base/subscriber/MessageWindow.hpp/.cpp` | 消息窗口 | `MessageWindow : Subscriber` |
| `src/base/subscriber/DynamicDataDisplay.hpp/.cpp` | 动态数据显示 | `DynamicDataDisplay : Subscriber` |
| `src/base/subscriber/DynamicDataInterface.hpp/.cpp` | **0 字节占位文件** | 无内容 |
| `src/base/subscriber/DynamicDataStruct.hpp` | DDD 数据结构（纯头） | `struct DDD`（参数名/包装器/预警上下界） |
| `src/base/subscriber/SubscriberException.hpp` | 订阅者异常（纯头） | `SubscriberException : BaseException` |

### 8.E coordsystem 目录（76 个文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/coordsystem/CoordinateBase.hpp/.cpp` | 坐标系/轴系公共基类 | `CoordinateBase : GmatBase`；`ParameterUsage` 枚举、`UsesXxx()=0` |
| `src/base/coordsystem/CoordinateSystem.hpp/.cpp` | 坐标系 | `CoordinateSystem : CoordinateBase`；`ToBaseSystem`(`:1158`)、`Initialize`(`:1084`)、`CreateLocalCoordinateSystem` |
| `src/base/coordsystem/AxisSystem.hpp/.cpp` | 轴系基类 | `AxisSystem : CoordinateBase`；`CalculateRotationMatrix()=0`、FK5 归算五件套 |
| `src/base/coordsystem/InertialAxes.hpp/.cpp` | 惯性轴系基类 | `InertialAxes : AxisSystem` |
| `src/base/coordsystem/MJ2000EqAxes.hpp/.cpp` | J2000 赤道系（基系） | `MJ2000EqAxes : InertialAxes` |
| `src/base/coordsystem/MJ2000EcAxes.hpp/.cpp` | J2000 黄道系 | `MJ2000EcAxes : InertialAxes` |
| `src/base/coordsystem/ICRFAxes.hpp/.cpp` | ICRF 系 | `ICRFAxes : InertialAxes`；`ICRFFile` |
| `src/base/coordsystem/TOEEqAxes.hpp/.cpp` | 真赤道系（J2000 定向） | `TOEEqAxes : InertialAxes` |
| `src/base/coordsystem/TOEEcAxes.hpp/.cpp` | 真黄道系（J2000 定向） | `TOEEcAxes : InertialAxes` |
| `src/base/coordsystem/MOEEqAxes.hpp/.cpp` | 平赤道系（J2000 定向） | `MOEEqAxes : InertialAxes` |
| `src/base/coordsystem/MOEEcAxes.hpp/.cpp` | 平黄道系（J2000 定向） | `MOEEcAxes : InertialAxes` |
| `src/base/coordsystem/BodyInertialAxes.hpp/.cpp` | 天体惯性系 | `BodyInertialAxes : InertialAxes` |
| `src/base/coordsystem/DynamicAxes.hpp/.cpp` | 动力轴系基类 | `DynamicAxes : AxisSystem` |
| `src/base/coordsystem/MeanOfDateAxes.hpp/.cpp` | 平赤道/黄道基类 | `MeanOfDateAxes : DynamicAxes` |
| `src/base/coordsystem/MODEqAxes.hpp/.cpp` | 平赤道（历元）系 | `MODEqAxes : MeanOfDateAxes` |
| `src/base/coordsystem/MODEcAxes.hpp/.cpp` | 平黄道（历元）系 | `MODEcAxes : MeanOfDateAxes` |
| `src/base/coordsystem/TrueOfDateAxes.hpp/.cpp` | 真赤道/黄道基类 | `TrueOfDateAxes : DynamicAxes` |
| `src/base/coordsystem/TODEqAxes.hpp/.cpp` | 真赤道（历元）系 | `TODEqAxes : TrueOfDateAxes` |
| `src/base/coordsystem/TODEcAxes.hpp/.cpp` | 真黄道（历元）系 | `TODEcAxes : TrueOfDateAxes` |
| `src/base/coordsystem/TEMEAxes.hpp/.cpp` | 真赤道平春分点系 | `TEMEAxes : TrueOfDateAxes` |
| `src/base/coordsystem/BodyFixedAxes.hpp/.cpp` | 体固连系 | `BodyFixedAxes : DynamicAxes`；`CalculateRotationMatrix`(`:423`，Spacecraft/天体两分支) |
| `src/base/coordsystem/EquatorAxes.hpp/.cpp` | 天体赤道面系 | `EquatorAxes : DynamicAxes`；`DeFile` |
| `src/base/coordsystem/TopocentricAxes.hpp/.cpp` | 站心系 | `TopocentricAxes : DynamicAxes` |
| `src/base/coordsystem/ObjectReferencedAxes.hpp/.cpp` | 对象参考轴系基类 | `ObjectReferencedAxes : DynamicAxes`；`SetPrimary/SecondaryObject` |
| `src/base/coordsystem/BodySpinSunAxes.hpp/.cpp` | 自旋轴—太阳系 | `BodySpinSunAxes : ObjectReferencedAxes` |
| `src/base/coordsystem/GeocentricSolarEclipticAxes.hpp/.cpp` | GSE 系 | `GeocentricSolarEclipticAxes : ObjectReferencedAxes` |
| `src/base/coordsystem/GeocentricSolarMagneticAxes.hpp/.cpp` | GSM 系 | `GeocentricSolarMagneticAxes : ObjectReferencedAxes` |
| `src/base/coordsystem/LocalAlignedConstrainedAxes.hpp/.cpp` | 局部对齐约束系 | `LocalAlignedConstrainedAxes : DynamicAxes` |
| `src/base/coordsystem/ITRFAxes.hpp/.cpp` | ITRF 地固系 | `ITRFAxes : DynamicAxes` |
| `src/base/coordsystem/SpiceAxes.hpp/.cpp` | SPICE 帧轴系 | `SpiceAxes : AxisSystem`；`SetSpiceFrameId` |
| `src/base/coordsystem/IAUFile.hpp/.cpp` | IAU 数据文件单例 | `IAUFile`；`GetIAUData` |
| `src/base/coordsystem/ICRFFile.hpp/.cpp` | ICRF 表单例 | `ICRFFile`；`RotateFromICRFtoFK5` |
| `src/base/coordsystem/ItrfCoefficientsFile.hpp/.cpp` | 章动/行星系数表 | `ItrfCoefficientsFile`；`GetNutationTerms/GetPlanetaryTerms` |
| `src/base/coordsystem/CoordinateConverter.hpp/.cpp` | 通用坐标系转换器 | `CoordinateConverter`；`Convert`(`:270`)、`GetLastRotationMatrix` |
| `src/base/coordsystem/CoordinateTransformation.hpp/.cpp` | 轴系状态变换 | `TransformState` 静态 |
| `src/base/coordsystem/CoordinateTranslation.hpp/.cpp` | 原点平移工具 | 平移静态方法 |
| `src/base/coordsystem/TransformUtil.hpp/.cpp` | 轨道状态/雅可比工具 | `TransformOrbitalState/CalculateOrbitalJacobian` |
| `src/base/coordsystem/CoordinateSystemException.hpp/.cpp` | 坐标系异常 | `CoordinateSystemException : BaseException` |

### 8.F interface 目录（8 个文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/interface/Interface.hpp/.cpp` | 外部接口基类 | `Interface : GmatBase`；`Open/Close` |
| `src/base/interface/GmatInterface.hpp/.cpp` | MATLAB 接口单例 | `GmatInterface`；`PutScript/ExecuteCallback/GetParameter` |
| `src/base/interface/SocketServer.hpp/.cpp` | 套接字服务器 | `SocketServer`；`RunServer/OnRequest/OnPoke`（localhost:3000） |
| `src/base/interface/InterfaceException.hpp/.cpp` | 接口异常 | `InterfaceException : BaseException` |

### 8.G api 目录（10 个文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/api/ApiClass.hpp/.cpp` | API 基类（近空） | `ApiClass` |
| `src/base/api/APIFunctions.hpp/.cpp` | 顶层 API 函数 | `Help/Construct/Execute/RunScript/Setup/Update/Clear` 等 |
| `src/base/api/APIMessageReceiver.hpp/.cpp` | API 消息接收器单例 | `APIMessageReceiver : MessageReceiver`；`GetMessage/LogMessage` |
| `src/base/api/HelpSystem.hpp/.cpp` | API 帮助单例 | `HelpSystem`；`BuildHelp/Help` |
| `src/base/api/APIException.hpp/.cpp` | API 异常 | `APIException : BaseException` |

### 8.H spice 目录（18 个文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/spice/SpiceInterface.hpp/.cpp` | CSPICE 桥接基类 | `SpiceInterface`；`LoadKernel`(`:322`)、`SpiceTimeToA1`(`:716`)、`GetNaifID`(`:674`) |
| `src/base/spice/SpiceKernelReader.hpp/.cpp` | 内核读取基类 | `SpiceKernelReader : SpiceInterface`；SPICE 侧数据指针 |
| `src/base/spice/SpiceOrbitKernelReader.hpp/.cpp` | SPK 读取器 | `SpiceOrbitKernelReader : SpiceKernelReader` |
| `src/base/spice/SpiceAttitudeKernelReader.hpp/.cpp` | CK 读取器 | `SpiceAttitudeKernelReader : SpiceKernelReader` |
| `src/base/spice/SpiceKernelWriter.hpp/.cpp` | 内核写入基类 | `SpiceKernelWriter : SpiceInterface` |
| `src/base/spice/SpiceOrbitKernelWriter.hpp/.cpp` | SPK 写入器 | `SpiceOrbitKernelWriter : SpiceKernelWriter`；`WriteSegment/AddMetaData/FinalizeKernel` |
| `src/base/spice/SpiceAttitudeKernelWriter.hpp/.cpp` | CK 写入器 | `SpiceAttitudeKernelWriter : SpiceKernelWriter` |
| `src/base/spice/SpiceFrameKernelWriter.hpp/.cpp` | FK 写入器 | `SpiceFrameKernelWriter : SpiceKernelWriter` |
| `src/base/spice/SpiceSCClockKernelWriter.hpp/.cpp` | SCLK 写入器 | `SpiceSCClockKernelWriter : SpiceKernelWriter` |

### 8.I asset 目录（6 个文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/asset/BodyFixedPoint.hpp/.cpp` | 体固连点基类 | `BodyFixedPoint : SpacePoint`；`GetMJ2000State/GetBodyFixedLocation` |
| `src/base/asset/GroundstationInterface.hpp/.cpp` | 地面站接口 | `GroundstationInterface : BodyFixedPoint`；`IsValidElevationAngle`(纯虚) |
| `src/base/asset/AssetException.hpp/.cpp` | 资产异常 | `AssetException : BaseException` |

### 8.J configs 目录（8 个文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/configs/ConfigManager.hpp/.cpp` | 配置管理器单例 | `ConfigManager`；`AddXxx/GetXxx/AddClone/ReconfigureItem` |
| `src/base/configs/ItemManager.hpp/.cpp` | 条目管理器基类 | `ItemManager`；`UpdateObjects` |
| `src/base/configs/PluginItemManager.hpp/.cpp` | 插件条目管理器单例 | `PluginItemManager : ItemManager`；`AddWidget/GetListOfObjects` |
| `src/base/configs/ConfigManagerException.hpp/.cpp` | 配置异常 | `ConfigManagerException : BaseException` |
