# 第10章 GUI 动力学类面板（传播器/力模型/航天器/坐标系）

本章负责 `src/gui/` 下八个与动力学/飞行器配置直接相关的子目录：`propagator/`（4 个文件）、`solarsys/`（18 个文件）、`spacecraft/`（28 个文件）、`forcemodel/`（2 个文件）、`hardware/`（10 个文件）、`burn/`（4 个文件）、`event/`（2 个文件）、`coordsystem/`（6 个文件），合计 **74 个代码文件**（37 对 .hpp/.cpp）。

> 范围说明（以 glob 实际清单为准）：① `src/gui/` 下**不存在** `attitude/` 子目录，`AttitudePanel` 实际位于 `src/gui/spacecraft/` 内，本章按 spacecraft/ 目录讲解；② 本 clone 中**不存在**独立的 `ForceModelPanel` 类——力模型配置（引力场、大气阻力、SRP、相对论修正、磁场的勾选与参数）整体嵌入 `PropagationConfigPanel` 的 Force Model 区段（含 `ShowForceModel` 调试函数），`forcemodel/` 目录仅有辅助弹窗 `DragInputsDialog`；③ GUI 面板到 base 对象的参数绑定**不经过 `ElementWrapper`**（该类在 `src/base/foundation/ElementWrapper.*`，属 [第2章](CH02-foundation.md)，仅用于脚本方程解析），面板使用 `GmatBase::GetParameterID()` + `Get/Set*Parameter()` 直连链路，本章第三节会给出真实调用链并说明原因。

## 一、本章目录树

```
src/gui/
├── propagator/                  (4 文件：2 .cpp + 2 .hpp)
│   ├── PropagationConfigPanel.hpp/.cpp   传播配置主面板（积分器 + 力模型 + SPK）
│   └── PropagatorSelectDialog.hpp/.cpp   传播器选择对话框
├── coordsystem/                 (6 文件：3 .cpp + 3 .hpp)
│   ├── CoordPanel.hpp/.cpp              坐标系通用子面板（轴/原点/约束）
│   ├── CoordSystemConfigPanel.hpp/.cpp  坐标系配置面板（GmatPanel）
│   └── CoordSysCreateDialog.hpp/.cpp    新建坐标系对话框
├── spacecraft/                  (28 文件：14 .cpp + 14 .hpp)
│   ├── SpacecraftPanel.hpp/.cpp         航天器主面板（Notebook 聚合 8 个子面板）
│   ├── OrbitPanel.hpp/.cpp              轨道面板（六要素/笛卡尔切换）
│   ├── AttitudePanel.hpp/.cpp           姿态面板（模型/状态表示切换）
│   ├── BallisticsMassPanel.hpp/.cpp     弹道系数/质量面板（含 SPAD）
│   ├── ThrusterPanel.hpp/.cpp           推力器挂接选择面板
│   ├── TankPanel.hpp/.cpp               燃料箱挂接选择面板
│   ├── FormationSetupPanel.hpp/.cpp     编队成员选择面板
│   ├── PowerSystemPanel.hpp/.cpp        电源系统选择面板
│   ├── SpicePanel.hpp/.cpp              SPICE 内核/NAIF ID 面板
│   ├── VisualModelPanel.hpp/.cpp        可视化模型面板（滑块/颜色）
│   ├── VisualModelCanvas.hpp/.cpp       OpenGL 模型预览画布
│   ├── OrbitDesignerDialog.hpp/.cpp     轨道设计器（6 类标称轨道）
│   ├── OrbitSummaryDialog.hpp/.cpp      轨道设计结果摘要
│   └── SpaceObjectSelectDialog.hpp/.cpp 空间对象选择对话框
├── solarsys/                    (18 文件：9 .cpp + 9 .hpp)
│   ├── UniversePanel.hpp/.cpp           太阳系/历元源配置面板
│   ├── CelestialBodyPanel.hpp/.cpp      天体主面板（Notebook 聚合 4 页）
│   ├── CelestialBodyPropertiesPanel.hpp/.cpp   天体属性（mu/半径/扁率/PCK）
│   ├── CelestialBodyOrbitPanel.hpp/.cpp        天体轨道（历元源/二体根数）
│   ├── CelestialBodyOrientationPanel.hpp/.cpp  天体定向（自转轴/旋转速率/FK）
│   ├── CelestialBodyVisualizationPanel.hpp/.cpp 天体可视化（纹理/3D 模型）
│   ├── BarycenterPanel.hpp/.cpp          质心（Barycenter）成员选择面板
│   ├── LibrationPointPanel.hpp/.cpp      平动点面板（主/次天体 + L1~L5）
│   └── CelesBodySelectDialog.hpp/.cpp    天体选择对话框
├── hardware/                    (10 文件：5 .cpp + 5 .hpp)
│   ├── BurnThrusterPanel.hpp/.cpp        推力器/机动通用面板（基类）
│   ├── ThrusterConfigPanel.hpp/.cpp      推力器配置面板（BurnThrusterPanel 派生）
│   ├── PowerSystemConfigPanel.hpp/.cpp   电源系统配置面板
│   ├── TankAndMixDialog.hpp/.cpp         油箱+混合比对话框（wxGrid）
│   └── ThrusterCoefficientDialog.hpp/.cpp 推力器多项式系数对话框（wxGrid）
├── burn/                        (4 文件：2 .cpp + 2 .hpp)
│   ├── FiniteBurnSetupPanel.hpp/.cpp     有限推力机动面板
│   └── ImpulsiveBurnSetupPanel.hpp/.cpp  脉冲机动面板（BurnThrusterPanel 派生）
├── event/                       (2 文件：1 .cpp + 1 .hpp)
│   └── EventLocatorPanel.hpp/.cpp        事件定位器面板（Contact/Eclipse/Intrusion）
└── forcemodel/                  (2 文件：1 .cpp + 1 .hpp)
    └── DragInputsDialog.hpp/.cpp         大气阻力输入对话框（F10.7/Kp/文件）
```

## 二、逐文件/逐类讲解

### 10.1 propagator/ —— 传播配置

#### src/gui/propagator/PropagationConfigPanel.hpp（480 行）

职责：声明传播配置面板 `PropagationConfigPanel`，把「积分器 + 力模型 + 非积分器传播器（SPK）」三类配置收敛到一张 `GmatPanel` 派生面板上。

- 继承自 `GmatPanel`（src/gui/foundation/GmatPanel.hpp，见 [第2章](CH02-foundation.md)），重写 `Create()/LoadData()/SaveData()` 三个虚函数（hpp L351-353）。
- **`ForceType` 结构体**（hpp L91-172）是面板内部的核心数据载体：每个"主天体"对应一条记录，保存 `bodyName`、`gravType`（引力场模型名）、`tideData/tideModel`、`dragType`、`magfType`、`gravDegree/gravOrrder/gravStmLimit`（注意源码拼写 `gravOrrder`，hpp L100）、势文件/潮汐文件名及全路径，以及底层力对象指针 `pmf/gravf/dragf/srpf`（PointMassForce/GravityField/DragForce/SolarRadiationPressure）。构造函数提供默认值（degree=4、order=4、STM limit=100），并重载 `operator=` 做深拷贝。注释（hpp L347）明确「Restricted to one primary」：GMAT 1.0 起只允许一个主天体，因此只用单个 `primaryBodyData` 指针而非数组，多主天体代码被注释保留。
- 改动标志位家族（hpp L180-185、L316-330）：`isForceModelChanged/isDegOrderChanged/isPotFileChanged/isTideFileChanged/isIntegratorChanged/isOriginChanged/isErrControlChanged/isSRPModelChanged/isDragModelChanged` 等，全部在 `Initialize()` 中清零，在事件处理器中置位，`SaveData()` 只保存被置位的区块——这是整个 GUI 层"按需写回"的通用机制。
- 控件集合：积分器组 `initialStepSize/accuracy/minStep/maxStep/maxStepAttempt/minIntError/nomIntError` 七个 `wxTextCtrl` + `theStopCheckBox`（hpp L212-230、L252）；SPK 组 `propagatorStepSizeTextCtrl/propCentralBodyComboBox/propagatorEpochFormatComboBox/startEpochCombobox`（hpp L255-268）；力模型组若干 ComboBox（积分器/原点/主天体/引力模型/潮汐数据/潮汐模型/大气模型/磁场模型/误差控制/SRP 模型/阻力模型，hpp L232-242）。
- 枚举：`MagfModelType`（只有 NONE_MM，hpp L74-78）、`ErrorControlType`（NONE_EC/RSSSTEP/RSSSTATE/LARGESTSTEP/LARGESTSTATE，hpp L81-89）。控件 ID 从 `ID_TEXT = 42000` 起（hpp L443-476）。
- 事件处理器（hpp L392-428）：文本更新、CheckBox 切换、ComboBox 选择、按钮（添加天体、引力文件搜索/保存、潮汐搜索、Setup（阻力配置）、磁场搜索、PM 编辑、SRP 编辑）。

#### src/gui/propagator/PropagationConfigPanel.cpp（5044 行）

职责：实现上述面板的创建、加载、保存与各区块联动。这是本章篇幅最大的文件，也是 GUI 层与 `PropSetup/Propagator/ODEModel` 核心引擎交互最密集的地方。

- **构造函数**（L117-159）：`mObjectName = propName`；约定力模型名为 `propSetupName + "_ForceModel"`（L123）；通过 `theGuiInterpreter->GetSolarSystemInUse()` 取太阳系（L136）；`theGuiInterpreter->GetConfiguredObject(propSetupName)` 取 `PropSetup`（L145）后 `SetObject(obj)`（L146）再 `Create(); Show();`。
- **事件表**（L72-107）：把按钮/文本/组合框事件全部路由到 `GmatPanel::OnOK/OnApply/OnCancel/OnScript/OnHelp` 或本类处理器。注意 `EVT_TEXT(ID_CB_PROP_EPOCHSTART, ...)`（L106）同时挂在 ComboBox 上，用于 `StartEpoch` 可编辑输入。
- **`Create()`**（L190 起）：按区块构造控件。积分器区块（L212-417）：积分器 ComboBox 由 `IntegratorCount` 个工厂类型填充（L219-227）；初始步长/精度/最小/最大步长/最大尝试次数文本控件全部带 `wxTextValidator(wxGMAT_FILTER_NUMERIC)` 与工具提示（从 `wxConfigBase` 读取 `...Hint`）。力模型区块（L419-）：错误控制 ComboBox（L437-441）、中心天体 ComboBox（L451-453，经 `theGuiManager->GetCelestialBodyComboBox` 注册）、主天体 ComboBox（L467-474）；引力区（L492-647）：模型 ComboBox + 阶/次/STM 上限文本 + 势文件文本与搜索/保存位图按钮 + Tide 区（数据源/模型/文件）；阻力区（L650-686）：大气模型 ComboBox + `Setup` 按钮（弹 `DragInputsDialog`）+ 阻力模型 ComboBox；磁场区（L688-）与 SRP/相对论区。典型控件构造如下（L223-227）：

```cpp
   theIntegratorComboBox =
      new wxComboBox( this, ID_CB_INTGR, integratorString,
                      wxDefaultPosition, wxDefaultSize, IntegratorCount,
                      intgArray, wxCB_DROPDOWN|wxCB_READONLY );
   theIntegratorComboBox->SetToolTip(pConfig->Read(_T("IntegratorTypeHint")));
```
  解读：积分器列表在 `Initialize()` 里从 `theGuiInterpreter->GetListOfFactoryItems(Gmat::PROPAGATOR)` 动态取得（见下），这里只负责展示；只读下拉框保证用户只能选合法类型。

- **`Initialize()`**（L2025-2134）：置空全部对象指针与标志位（L2031-2071）；默认积分器 `"RKV 8(9)"`（L2045）；用工厂目录填充 `integratorArray/integratorTypeArray`（L2075-2081）；阻力模型数组 = `"None"` + 大气模型工厂项（L2084-2089）；误差控制枚举数组（L2102-2106）；SRP 模型数组 `"Spherical"/"SPADFile"`（L2092-2094、L2109-2110）；重力势文件关键字映射 `theFileMap["JGM-2"]="JGM2_FILE"` 等（L2115-2120）；阻力数据默认缓冲 F10.7=150、F10.7A=150、Kp=3（L2131-2132）。
- **`LoadData()`**（L866-998）：按 `thePropagator->UsesODEModel()` 分支——积分器型传播器取 `thePropSetup->GetODEModel()`（L879），非积分器（SPK）型则读 `StepSize/CentralBody/EpochFormat/StartEpoch` 四个参数到 SPK 缓冲并置位对应 changed 标志（L891-901），还读取 `StartOptions` 填充起点历元下拉（L905-913）。随后 `PopulateForces()`、`UpdatePrimaryBodyComboBoxList()`、`theIntegratorComboBox->SetSelection(typeId)`、`DisplayIntegratorData(false)`、`DisplayForceData()`（L919-972），最后按是否 Integrator 调 `ShowIntegratorLayout()`（L982-989）。
- **`PopulateForces()`**（L1003-1333）：遍历 `ODEModel` 的力列表，按 `force->GetTypeName()` 分派：`PointMassForce` → 加入 `pointMassBodyList`（L1052-1078）；`GravityField` → 首次创建 `primaryBodyData`、填充势文件/潮汐文件、经 `GravityField::GetModelType(potFileFullPath, bodyName)` 推断引力模型类型（L1151-1158）；同时检查"同一天体既是主天体又是点质量"的冲突并弹警告（L1066-1077、L1172-1185）。
- **`SaveData()`**（L1334-1955）：先做校验——主天体必须选了引力模型（L1366-1375）、`Other` 模型必须有势文件（L1381-1390）、主天体与点质量不能同时为空（L1403-1410）；然后分块写回：积分器变更时先 `SaveIntegratorData()`，再 `thePropSetup->SetPropagator(thePropagator, true)`（L1450，base 内部会克隆，故随后重新取指针 L1452）；力模型变更时**重建** `ODEModel`（L1486：`new ODEModel(fmName, "ForceModel")`），依次加入点质量力（L1493-1500）、重力场（L1508-1551，通过 `theGuiInterpreter->CreateObject("GravityField","")` 新建并重设 BodyName/PotentialFile/TideFile/Degree/Order）、阻力（L1581-1663，必要时经 `CreateObject` 造大气模型、写回 F10.7/F10.7A/MagneticIndex 与 CSSI/Schatten 文件字符串缓冲）；SRP 与相对论部分通过 `SetOnOffParameter` 写回。
- **`DisplayIntegratorData(bool integratorChanged)`**（L2140-2379）：用户切换积分器时（L2150-2254）把 `integratorTypeArray[propIndex]` 中的 `-` 替换为 `_` 生成对象名（L2154-2156），经 `GetConfiguredObject` 或 `CreateObject` 得到新 `thePropagator`（L2158-2163）；从非积分器切回时若 `theForceModel == NULL` 则按 `PropSetup` 的 `FM` 参数或默认命名取/建 ODEModel（L2194-2206）。积分器数据显示：`PredictorCorrector` 才显示最小/标称积分误差（L2260-2298），`StopIfAccuracyIsViolated` 勾选框值取自 `GetBooleanParameter(GetParameterID("StopIfAccuracyIsViolated"))`（L2300-2304）；五个数值文本用 `GetRealParameter("InitialStepSize"/"Accuracy"/"MinStep"/"MaxStep")` 与 `GetIntegerParameter("MaxStepAttempts")` 填充（L2308-2318）。
- **`ShowIntegratorLayout(bool, bool)`**（L4934-5043）：按 `thePropagator->IsOfType("Integrator"/"PredictorCorrector"/"Code500Propagator")` 切换两组控件的显隐——积分器型显示步长/精度/误差、隐藏 SPK 控件；星历型隐藏力模型与积分器、显示 `StepSize/CentralBody/EpochFormat/StartEpoch`，其中中心天体下拉被固定为 `"Provided by file"` 且禁用（L5024-5029）。末尾按运行模式决定是否显示"保存势文件"按钮（L5038-5039）。
- 其余方法：`DisplayForceData()`（L2384）、`DisplayPrimaryBodyData()`（L2413）、`DisplayGravityFieldData()`（L2435）、`DisplayAtmosphereModelData()`（L2638）、`DisplaySRPData()`（L2767）、`DisplayErrorControlData()`（L2781）、`SaveIntegratorData()`（L3097）、`SavePropagatorData()`（L3226）、`SaveDegOrder()`（L3300）、`SavePotFile()`（L3406）、`SaveTideFile()`（L3499）、`OnGravityModelComboBox`（L3805，切换模型时联动阶/次/文件区显隐）、`OnAtmosphereModelComboBox`（L3963）、`OnSetupButton`（L4535，弹 `DragInputsDialog` 并回填 `dragParameterBuffer/dragStringBuffer`）、`OnPMEditButton`（L4628）、`OnSRPEditButton`（L4688）、`ShowForceModel`（L4911-4930，调试用，打印 ODEModel 全部力）。

#### src/gui/propagator/PropagatorSelectDialog.hpp/.cpp（80 + 183 行）

职责：模态对话框，让用户在已有 `PropSetup` 列表中选择传播器（例如把 PropSetup 与传播器解耦重新绑定）。

- 继承 `GmatDialog`（src/gui/foundation/GmatDialog.*），重写 `Create/LoadData/SaveData/ResetData`（hpp L58-61）。
- `Create()`（cpp L78-139）：`wxListBox` 内容来自 `theGuiInterpreter->GetListOfObjects(Gmat::PROP_SETUP)`（cpp L95-97），单选用 `wxLB_SINGLE`；隐藏底部按钮条（L136-138），由 `mAddButton/mCancelButton` 承担确认/取消。
- `OnButton()`（cpp L144-159）：点 OK 且选中项与当前 `mPropName` 不同时置 `mHasSelectionChanged=true` 并记录 `mNewPropName`，然后 `Close()`；`GetPropagatorName()`（L70-73）供调用方取回结果。`LoadData()`（L164-167）把当前名设回列表。典型用途：在 `PropagationConfigPanel` 之外快速切换与 PropSetup 绑定的传播器，或由资源树右键触发。

### 10.2 coordsystem/ —— 坐标系配置

#### src/gui/coordsystem/CoordPanel.hpp/.cpp（178 + 1646 行）

职责：坐标系配置的**可复用子面板**，同时被 `CoordSystemConfigPanel`（编辑已有坐标系）与 `CoordSysCreateDialog`（新建坐标系）嵌入——这是本章"组合面板"模式的代表。

- 继承 `wxPanel` 并混入 `UserInputValidator`（hpp L38，提供 `CheckReal/CheckRealRange/IsValidName` 等校验工具）。
- 控件：`originComboBox`（原点 SpacePoint）、`typeComboBox`（轴系类型）、`primaryComboBox/secondaryComboBox`（主/次天体）、`refObjectComboBox/constraintCSComboBox`（LocalAlignedConstrained 用的参考对象与约束坐标系）、`x/y/zComboBox`（ObjectReferenced 的 R/V/N 轴选择）、`epochTextCtrl/intervalTextCtrl`（hpp L123-146）。
- 开关位（hpp L87-95）：`mShowPrimaryBody/mShowSecondaryBody/mShowAlignmentConstraint/mShowEpoch/mShowXyz/mShowUpdate`，由轴系类型决定哪些控件可见可编辑。公开的 `Get*ComboBox()`（hpp L48-58）把控件句柄暴露给两个宿主。
- **`EnableOptions(AxisSystem *axis)`**（cpp L100-374）：核心联动逻辑。从 `typeComboBox` 取轴型名（缺省 `"MJ2000Eq"`，L115）；若未传轴对象，则用 `theGuiInterpreter->CreateObject(typeStr, "")` 临时造一个同型轴（L122-123），只为了读它的能力标志；然后按 `UsesPrimary()/UsesSecondary()/UsesReferenceObject()/UsesEpoch()/UsesXAxis().../UsesNutationUpdateInterval()`（返回 `GmatCoordinate::NOT_USED/REQUIRED_UNMODIFIABLE` 等）逐一决定 `mShow*`（L140-188）。对特殊轴型做硬编码：GSE/GSM 固定主=Earth、次=Sun 并禁用（L316-326），BodySpinSun 固定主=Sun、次=原点（L327-337）。非可编辑模式（内建坐标系）则全部禁用（L343-366）。
- **`CreateAxis()`**（cpp L648-745）：读各 ComboBox 当前值 → `IsValidAxis()` 校验 → `theGuiInterpreter->CreateObject(axisType, "")` 创建轴实例 → 按 `Uses*` 标志逐项 `SetPrimaryObject/SetSecondaryObject/SetXAxis/SetYAxis/SetZAxis/SetEpoch(a1mjd)/SetReferenceObject/SetRefObject(constraintCS)`，末了 `CheckAlignmentConstraintValues(true, axis)` 写回对齐/约束向量。任何异常都会 `delete axis; axis = NULL`（L732-733），由宿主决定是否放弃。
- **`IsValidAxis()/IsValidXYZ()`**（cpp L793-920）：ObjectReferenced 要求主/次天体非空且不同（L809-824）；XYZ 必须正交——R/V/N 任意一者在 X/Y/Z 中出现超过一次即报错（L867-903），且三轴中必须恰好留一个空串（L912-919）。
- **`SaveData(const std::string &coordName, AxisSystem *axis, wxString &epochFormat)`**（cpp L1247-1646）：若坐标系不存在则 `CreateObject("CoordinateSystem", coordName)` 新建（L1270-1301）；**先 `csClone = coordSys->Clone()` 留备份**（L1312），随后 `SetRefObject(axis, Gmat::AXIS_SYSTEM, "")`（L1317）、`SetStringParameter("Origin", ...)` 与 `SetRefObject(origin, Gmat::SPACE_POINT, ...)`（L1327-1334）；出错时 `coordSys->Copy(csClone)` 回滚（L1344）。主/次天体设置区分「可编辑」与 `setThoughDisabled`（强制写对象而非名字，因为 `SetStringParameter` 会拒绝修改不可改字段，L1402-1410）。J2000 体缺失时统一把 Earth 设为 J2000Body（L1366-1375）。

#### src/gui/coordsystem/CoordSystemConfigPanel.hpp/.cpp（91 + 438 行）

职责：编辑**已有**坐标系的 `GmatPanel`，是 `CoordPanel` 的第一种宿主。

- 构造（cpp L56-69）：`theGuiInterpreter->GetConfiguredObject(coordName)` 取坐标系；`mEpochFormat` 缺省 `"A1ModJulian"`。
- `Create()`（cpp L94-106）：按 `theCoordSys->IsBuiltIn()` 决定 `CoordPanel(this, false)`（内建只读）还是 `CoordPanel(this, true)`。
- `LoadData()`（cpp L116-174）：从 `CoordPanel` 取回全部控件句柄（L125-136）；`theCoordSys->GetStringParameter("Origin")` 填原点（L141-147）；`theCoordSys->GetRefObject(Gmat::AXIS_SYSTEM, "")` 取轴后调 `mCoordPanel->ShowAxisData(axis)`（L149-154），记录 `previousType/previousOrigin` 供失败回退，并取轴的 `EpochFormat`（L157）。
- `SaveData()`（cpp L184-358）：按"epoch → 轴系 → 原点"顺序写回（顺序有讲究：原点必须在轴系之后设置，见 L298-301 注释）。轴变更时 `mCoordPanel->CreateAxis()` 新建轴、`mCoordPanel->SaveData(...)` 落库、成功后 `theCoordSys->SetRefObject(axis, Gmat::AXIS_SYSTEM, "")` + `Initialize()`（L254-262）；异常时把 `oldAxis` 设回并重初始化（L277-284）。原点变更时 `SetStringParameter("Origin", originName)` + `SetRefObject(origin, Gmat::SPACE_POINT, origin->GetName())` + `Initialize()`（L311-324），失败则恢复 `previousOrigin`（L339-344）。
- 事件（cpp L383-437）：`OnComboUpdate` 按事件源区分——原点变 → `mOriginChanged`；轴型变 → `mCoordPanel->EnableOptions()`（联动显隐）+ `mObjRefChanged`；主/次/参考/约束/X/Y/Z 变 → `mObjRefChanged`。

#### src/gui/coordsystem/CoordSysCreateDialog.hpp/.cpp（100 + 390 行）

职责：新建坐标系的 `GmatDialog`，`CoordPanel` 的第二种宿主。

- 构造（cpp L64-73）与 `Create()`（cpp L82-119）：额外放一个 `nameTextCtrl`（坐标系名）+ `CoordPanel(this, true)`。
- `SaveData()`（cpp L174-314）：名字校验链——非空（L184-191）→ `IsValidName`（L195，UserInputValidator）→ 不能是命令类型名（L199-206）；epoch 与对齐/约束文本按修改标志校验（L211-239）；随后 `mCoordPanel->CreateAxis()` 建轴 → `mCoordPanel->SaveData(coordName, axis, wxFormatName)` 落库（L267-278）；失败时 `theGuiInterpreter->RemoveObjectIfNotUsed(Gmat::COORDINATE_SYSTEM, coordName)` 清理半成品（L286）；成功置 `mIsCoordCreated=true`。若名字已存在则 `wxLogError` 拒绝（L304-309）。重复打开对话框再次 Save 时走 `mIsCoordCreated` 分支复用已有轴（L251-261）。
- 事件（cpp L344-389）：文本修改 → `EnableUpdate(true)` + 按控件置 `mIsTextModified/mIsLACTextModified`；轴型 ComboBox 变 → `mCoordPanel->EnableOptions()`。

### 10.3 spacecraft/ —— 航天器配置（本章最重目录）

#### src/gui/spacecraft/SpacecraftPanel.hpp/.cpp（148 + 416 行）

职责：航天器配置主面板——一个 `wxNotebook` 聚合 8 个专项子面板，负责"克隆工作副本 + 分页收集改动 + 整体写回"。

- 继承 `GmatPanel`，重写 `Create/LoadData/SaveData` 与 `RefreshObjects`（hpp L59、L63-65）。
- **`Create()`**（cpp L131-246）：核心技巧在 L138——`currentSpacecraft = new Spacecraft(*theSpacecraft)`（拷贝构造，非 Clone），之后所有子面板都编辑这份工作副本，避免半途取消污染真实对象；同时把内部坐标系与配置的坐标系引用拷入副本（L148-153）。子面板构造：`OrbitPanel/AttitudePanel/BallisticsMassPanel/TankPanel/PowerSystemPanel/SpicePanel(__USE_SPICE__ 条件编译)/VisualModelPanel` 直接挂 notebook（L176-225），`ThrusterPanel` 挂在一个二级 `actuatorNotebook`（L166-170、L201-202），notebook 页序为 Orbit/Attitude/Ballistic-Mass/Tanks/Power System/[SPICE]/Actuators/Visualization（L228-239）。
- **`LoadData()`**（cpp L256-293）：依次 `theXxxPanel->LoadData()`；`mObject = theSpacecraft`（供 Show Script）；最后 `EnableUpdate(false)` 显式关掉 Apply（各子面板自己的事件会再打开，L282-284）。
- **`SaveData()`**（cpp L303-371）：按 `IsDataChanged()` 依次驱动子面板 `SaveData()` 并聚合 `CanClosePanel()`（L317-346）；任一失败则 `EnableUpdate(true)` 提前返回（L348-352）；全部通过后 `theSpacecraft->Copy(currentSpacecraft)`（L364）把工作副本整体写回——这是"克隆-编辑-复制"闭环的落点。
- `OnPageChange()`（cpp L383-392）：切页时刷新 Tanks/Thruster/Attitude/PowerSystem/SPICE 页数据；`RefreshObjects(Gmat::COORDINATE_SYSTEM)`（cpp L404-415）转发给 `theOrbitPanel->RefreshComponents()`，实现坐标系列表动态更新。

#### src/gui/spacecraft/OrbitPanel.hpp/.cpp（208 + 3431 行）

职责：轨道页——六要素/笛卡尔切换、坐标系/历元格式选择、状态校验与换算。这是本章第二个讲解重点。

- 继承 `wxPanel`；关键成员：`Rvector6 mCartState/mTempCartState/mOutState`（内部系笛卡尔 / 暂存 / 显示系状态，hpp L103-106）、`CoordinateConverter mCoordConverter`（hpp L108）、`mStateTypeNames/mAnomalyTypeNames`（hpp L69-71）、`textCtrl[6]` + `epochValue`（hpp L186-187）、四个 ComboBox（anomaly/mCoordSys/epochFormat/stateType，hpp L191-194）。
- 状态类型来源：`StateConversionUtil::GetStateTypeList()/GetTypeCount()`（cpp L1533-1534，base 模块，见 [第6章](CH06-dynamics.md)）；历元格式来源：`TimeSystemConverter::Instance()->GetValidTimeRepresentations()`（cpp L173-175）。
- **`LoadData()`**（cpp L143-331）：读 `DateFormat/A1Epoch/Epoch`（L178-190）；为防重复解析，非 TAIModJulian 的历元先转成 TAI 字符串缓存 `mTaiMjdStr`（L194-210）；取 `GetRefObjectName(Gmat::COORDINATE_SYSTEM)` 与 `GetRefObject` 得到输出坐标系（L213-238）；`BuildValidStateTypes()` + `BuildValidCoordinateSystemList()` 建合法列表（L273-275）；若状态类型是 Keplerian/ModKeplerian 则从 base 的 `Anomaly` 表填真近点角下拉（L287-301）；`mCartState.Set(theSpacecraft->GetState().GetState())`（L309）后 `DisplayState()`。
- **`OnComboBoxChange()`**（cpp L783-1031）：三路分支。①历元格式变（L797-860）：用 `theTimeConverter->Convert(mFromEpochFormat, fromMjd, mEpochStr, toEpochFormat, outMjd, outStr)` 即时换算并回填文本（L835-838），TAI 缓存机制保证反复切换不回漂移；失败则回退原格式（L854-855）。②坐标系或状态类型变（L864-975）：先若用户改过状态则 `CheckState(tempState)` 校验（L889-905）；从 Cartesian 切走时用 `StateConversionUtil::Convert(mCartState, "Cartesian", "Keplerian", mu, flat, radius, "TA")` 现算真近点角（L907-934）；换坐标系时经 `GetConfiguredObject` 取新系、`SetRefObjectName + SetRefObject` 挂到航天器上（L941-960），异常回滚（L964-973）。③真近点角类型变（L979-1022）：目前只允许 "TA"，强制回写 `mAnomalyTypeNames[StateConversionUtil::TA]`（L984-985）。
- **`DisplayState()`**（cpp L1339-1464）：组装"半状态"——用户改过的分量取文本框、未改的取 `mOutState`（L1353-1363）；Keplerian 类状态改 SMA/ECC/TA 时重算真近点角（L1371-1393）；历元变则先转 A1 写回 `theSpacecraft->SetEpoch(epochFormat, newEpoch, a1mjd)`（L1410-1433）；核心换算在 `BuildState()`，换算后回填 6 个文本框并 `SetLabelsUnits(stateTypeStr)` 更新标签/单位（L1445-1449）。
- **`BuildState()`**（cpp L1718-1818）：双段换算链——`StateConversionUtil::Convert(inputState, mFromStateTypeStr, "Cartesian", mu, flat, radius, mAnomalyType)` 把显示表示转笛卡尔（L1765-1769）→ `mCoordConverter.Convert(A1Mjd(mEpoch), midState, mFromCoord, mCartState, mInternalCoord)` 转内部系（L1772-1773）→ 再 `mCoordConverter.Convert(..., mCartState, mInternalCoord, midState, mOutCoord)` 转目标系（L1788-1789）→ `StateConversionUtil::Convert(midState, "Cartesian", stateTypeStr, ...)` 转目标表示（L1798-1802）。mu/flattening/radius 由 `GetOriginData()`（L3391 起）从原点 `SpacePoint` 取。
- `CheckState()`（cpp L1890）按 `stateTypeStr` 分发给 `CheckCartesian/CheckKeplerian/CheckModKeplerian/CheckSphericalAZFPA/CheckSphericalRADEC/CheckEquinoctial/CheckModifiedEquinoctial/CheckAlternateEquinoctial/CheckDelaunay/CheckPlanetodetic/CheckOutgoingAsymptote/CheckIncomingAsymptote/CheckBrouwerMeanShort/CheckBrouwerMeanLong`（cpp L1988-3259），每个校验函数内部做范围检查与单位换算（如 km↔m、deg↔rad）后经 `StateConversionUtil::Convert` 反算笛卡尔再回填。

#### src/gui/spacecraft/AttitudePanel.hpp/.cpp（433 + 3873 行）

职责：姿态页——姿态模型选择（Spinner/PrecessingSpinner/NadirPointing/CCSDS-AEM 等）、姿态状态表示切换（欧拉角/四元数/DCM/MRP，hpp L400-407 枚举 `StateType`）与角速率表示切换（欧拉角速率/角速度，hpp L410-415），并在切换时实时换算。

- 继承 `wxPanel`；`Attitude *theAttitude`、`CoordinateConverter cc`、`attCS/toCS/fromCS` 三个坐标系（hpp L180-187）；`Rmatrix33 dcmat / Rvector q / Rvector3 ea/mrp/av/ear` 保存当前表示（hpp L232-238）；每类文本的 `*Modified[]` 标志族（hpp L249-272）。
- **`LoadData()`**（cpp L852-1015）：`theSpacecraft->GetRefObject(Gmat::ATTITUDE, "")` 取姿态对象，NULL 时用 `attitudeModelArray[0]` 造默认并 `SetRefObject` 挂回（L860-876）；读 `AttitudeDisplayStateType/AttitudeRateDisplayStateType/AttitudeModelName/EulerAngleSequence/AttitudeCoordinateSystem` 五个参数填下拉（L892-906）；`LoadAttitudeAndRateData(theAttitude)`（L930，L3487 起）统一读状态/角速率并按当前表示缓存到 `dcmat/q/ea/mrp/av/ear`；最后 `DisplayDataForModel(attitudeModel)`（L1007，L1989 起）切换页面区段。
- **`SaveData()`**（cpp L1025-1264）：`ValidateState("Both", true)` 校验奇异性（L1044）；若模型变更则 `theGuiInterpreter->CreateObject(attitudeModel, "")` 新建姿态对象（L1067-1072），此后全部写向新对象；按 `csModified/seqModified/stateTypeModified/stateModified/rateStateTypeModified/stateRateModified` 分块 `SetStringParameter/SetRvectorParameter/SetRmatrixParameter` 写回（L1135-1239）；新模型经 `theSpacecraft->SetRefObject(useAttitude, Gmat::ATTITUDE, "")` 挂接（L1247-1249，旧对象由 Spacecraft 释放）。
- 模型专属数据：`Load/SavePrecessingSpinnerData`（L3083/L3119，自旋轴、章动参考矢量、进动角/速率、章动角、自旋角/速率）、`Load/SaveNadirPointingData`（L3258/L3292，参考天体、约束类型、body 对齐/约束矢量）、`Load/SaveCCSDSAttitudeData`（L3385/L3412，AEM 文件）。表示切换事件 `OnStateTypeSelection`（L2553）先 `ValidateState` 再 `DisplayState` 族函数换算；`Display*`（L2654-3082）与 `Update*`（L3571-3873）成对出现：前者把缓存数值渲染到控件，后者把控件数值换算后写回缓存并同步其他表示。

#### src/gui/spacecraft/BallisticsMassPanel.hpp/.cpp（118 + 761 行）

职责：弹道系数与质量页——干重、阻力系数 Cd、反射系数 Cr、阻力面积、SRP 面积，以及 SPAD（SPADSRPFile/SPADDragFile）文件与缩放系数/插值方法。

- 继承 `wxPanel`；`Create()`（cpp L108）把数值文本全部加 `wxGMAT_FILTER_NUMERIC` 校验器；SPAD 区有文件浏览按钮与插值方法下拉。
- `LoadData()`（cpp L310-362）：`theSpacecraft->GetRealParameter(dryMassID/...)` 批量取值（L330-339）→ `theGuiManager->ToWxString` 填控件。
- `SaveData()`（cpp L372-635）：对每个字段 `GetParameterID` → `GmatStringUtil::ToReal` + 范围检查（干重/面积 ≥0，L400-408）→ `SetRealParameter(dryMassID, rvalue)`；非法则弹 `PopupMessage` 并 `canClose=false`（L405-408）。SPAD 字段类似处理（L460-635）。事件处理器（L636-761）置位 `spadSRPFileChanged/spadDragFileChanged` 并 `EnableUpdate(true)`。

#### src/gui/spacecraft/ThrusterPanel.hpp/.cpp（89 + 301 行）

职责：把已配置的 `Thruster` 对象挂接到航天器的"Thrusters"多值参数上——典型双列表（available/selected）管理。

- 继承 `wxPanel`；`mExcludedThrusterList` 记录已选名单（hpp L69）。
- `Create()`（cpp L85-168）：`theSpacecraft->GetParameterID("Thrusters")` + `GetStringArrayParameter` 得到已挂推力器（L113-118）→ 用 `theGuiManager->GetThrusterListBox(this, ID_LISTBOX, wxSize(150,200), &mExcludedThrusterList)` 注册可用列表（L120-122，GuiItemManager 会按排除表自动过滤）→ 右侧 `selectedThrusterListBox` 为普通 `wxListBox`。
- `OnButtonClick()`（cpp L211-300）：`selectButton` 把选中项从可用列表移到已选列表并同步排除表（L213-239）；`removeButton` 反向（L240-261）；`selectAll/removeAll` 批量移动（L262-299）；每次置 `dataChanged=true; theScPanel->EnableUpdate(true)`。
- `LoadData()`（cpp L173-187）把 `Thrusters` 数组填进已选列表；**`SaveData()`**（cpp L192-206）是先 `theSpacecraft->TakeAction("RemoveThruster", "")` 清空再逐条 `SetStringParameter(paramID, name)` 重挂——利用多值字符串参数的追加语义重建整个列表：

```cpp
   theSpacecraft->TakeAction("RemoveThruster", "");
   Integer count = selectedThrusterListBox->GetCount();
   for (Integer i = 0; i < count; i++)
   {
      paramID = theSpacecraft->GetParameterID("Thrusters");
      theSpacecraft->SetStringParameter(paramID,
         std::string(selectedThrusterListBox->GetString(i).c_str()));
   }
```
  解读：`SetStringParameter` 对多值参数按"追加"语义工作，所以必须先 `TakeAction("RemoveThruster")` 清空；这是多记录参数的标准写回套路（TankPanel 对 "Tanks" 同理）。

#### src/gui/spacecraft/TankPanel.hpp/.cpp（90 + 335 行）

职责：把 `FuelTank` 挂接到航天器的 "Tanks" 参数。结构与 `ThrusterPanel` 完全同构（hpp 与 cpp 布局一一对应）：`mExcludedTankList`、`GetFuelTankListBox`（cpp L138-140）、`select/remove/selectAll/removeAll` 按钮、`LoadData` 用 `GetParameterID("Tanks")` 填已选（cpp L208-213）、`SaveData` 用 `TakeAction("RemoveTank")` + `SetStringParameter("Tanks")` 重建（cpp L225-260）。区别仅在于资源类型（FuelTank vs Thruster）与参数名，不再赘述。

#### src/gui/spacecraft/FormationSetupPanel.hpp/.cpp（78 + 364 行）

职责：编队（Formation）成员管理面板。继承 `GmatPanel`（hpp L40）。

- 构造（cpp L78-88）：`mFormation = (FormationInterface*)GetConfiguredObject(mFormationName)`；`mClonedFormation = (FormationInterface*)(mFormation->Clone())`——克隆工作副本模式。
- `Create()`（cpp L118-204）：`mSoExcList` 先加入编队自身名字（防自环，L139）；可用列表 `theGuiManager->GetSpaceObjectListBox(this, AVL_LISTBOX, wxSize(150,200), &mSoExcList, false)`（L141-143）；事件表（cpp L49-61）里 `EVT_LISTBOX_DCLICK` 支持双击直接添加/移除。
- `LoadData()`（cpp L210-228）：`mClonedFormation->GetStringArrayParameter(GetParameterID("Add"))` 取成员列表填已选框并同步排除表。
- `SaveData()`（cpp L234-）：`mClonedFormation->SetBooleanParameter("Clear", true)` 清空后逐条 `SetStringParameter("Add", name)`；`RefreshObjects` 处理 `Gmat::SPACECRAFT` 类型资源刷新。

#### src/gui/spacecraft/PowerSystemPanel.hpp/.cpp（81 + 251 行）

职责：为航天器选择电源系统（`PowerSystem` 对象）。极简面板：一个 ComboBox。

- `Create()`（cpp L98-143）用 `theGuiManager->GetPowerSystemComboBox` 注册；`LoadData()`（cpp L153-167）`GetStringParameter("PowerSystem")` 填值；`SaveData()`（cpp L177-210）变更时 `SetStringParameter("PowerSystem", ...)`。`OnComboBoxChange`（cpp L221-250）处理 `"No Power System Selected"` 占位项：选中真实电源系统后把它从下拉删除（L233-239），保证空选状态只能作为初始态存在。

#### src/gui/spacecraft/SpicePanel.hpp/.cpp（188 + 1078 行，仅 `__USE_SPICE__` 编译）

职责：航天器 SPICE 配置——SPK/CK/SCLK/FK 四类内核文件列表 + NAIF ID/参考系 NAIF ID。

- `Create()`（cpp L442-645）为四类内核各建一个 `wxListBox` + Browse/Remove 按钮；`LoadData()`（cpp L364-441）从 `theSpacecraft` 读 `OrbitSpiceKernelName/AttitudeSpiceKernelName/SCLKSpiceKernelName/FramesSpiceKernelName/NAIFId/NAIFIdReferenceFrame` 填充。
- `SaveData()`（cpp L134-363）：每个文件名先 `std::ifstream` 验证存在（L173-181），再 `SetStringParameter(GetParameterID("OrbitSpiceKernelName"), strval)`；删除操作经 `spkFilesToDelete` 队列在保存时 `RemoveSpiceKernelName("Orbit", ...)` 执行（见 L724-772 的 Remove 处理器与 SaveData 尾部）。事件处理器按四类内核各三件套（Browse/Remove/ListBoxChange，L681-1048）+ NAIF ID 文本（L1050-1070）编排。

#### src/gui/spacecraft/VisualModelPanel.hpp/.cpp（176 + 997 行）

职责：航天器可视化模型配置页——模型文件选择、旋转/平移/缩放滑块、轨道/目标颜色选择，右侧内嵌 `VisualModelCanvas` 实时预览。

- `Create()`（cpp L154-434）构建滑块组（`xRotSlider/yRotSlider/zRotSlider/xTranSlider/yTranSlider/zTranSlider/scaleSlider`）、对应数值文本、`modelTextCtrl` + 浏览按钮、`mOrbitColorCtrl/mTargetColorCtrl` 两个 `wxColourPickerCtrl`、`showEarthButton/autoscaleButton/recenterButton`。
- `LoadData()`（cpp L438-491）：从 `currentSpacecraft` 读 `ModelFile/ModelOffsetX/Y/Z/ModelRotationX/Y/Z/ModelScale` 填文本与滑块（滑块刻度 = 值×100，L457-459）；`InitializeCanvas()`（L549-568）用 `GetModelFileFullPath()` 让画布加载模型；无模型文件时 `ToggleInterface(false)` 禁用全部控件（L476-480）。
- `SaveData()`（cpp L907-959）：把滑块/文本值经 `GetParameterID("ModelOffsetX")` 等写回 `currentSpacecraft`。滑块事件 `OnSlide`（L610）双向同步滑块↔文本，颜色事件 `OnColorPickerChange`（L682）把颜色写入 `ModelOrbitColor/ModelTargetColor`。

#### src/gui/spacecraft/VisualModelCanvas.hpp/.cpp（97 + 552 行）

职责：OpenGL 预览画布，直接渲染航天器 3D 模型。

- 继承 `wxGLCanvas`（hpp L42）；成员 `Camera mCamera`、`Light mLight`、`ModelObject *loadedModel`（hpp L71-77）；事件 `OnPaint/OnMouse/OnKeyDown`（hpp L62-64）。
- 构造（cpp L64-109）：相机定位 `(15000,15000,15000)` 看向原点，白光光源，`glClearColor(0,0,0,1)`。
- `OnPaint()`（cpp L127-）：`SetGLContext()` → 首次 `InitGL()` → 延迟加载模型（L154-156）→ 视口/投影/相机矩阵（`gluPerspective`+`gluLookAt`，L179-193）→ LIGHT1 光照 → 渲染：`GetModelId()==-1` 时画默认 `DrawSpacecraft(198, red, yellow)`（L209-214），否则读 `ModelOffsetX/.../ModelScale` 设到 `loadedModel` 再 `DrawAsSpacecraft(true)`（L217-229）→ `DrawAxes()` + 可选线框地球参考（L234-239）。
- `Rotate/Translate/Scale`（hpp L53-55）供面板滑块调用；`LoadModel(const wxString &)` 经 `ModelManager` 加载并延迟到 GL 上下文内执行（cpp 内 `needToLoadModel` 标志）。

#### src/gui/spacecraft/OrbitDesignerDialog.hpp/.cpp（289 + 3725 行）

职责：轨道设计器对话框——按用户勾选的参数反解六类标称轨道（Sun Sync/Repeat Sun Sync/Repeat Ground Track/Geostationary/Molniya/Frozen），把结果回填到 OrbitPanel。

- 继承 `GmatDialog`；内嵌 base 层设计对象 `SunSync orbitSS / RepeatSunSync orbitRSS / RepeatGroundTrack orbitRGT / Frozen orbitFZN / OrbitDesignerTime orbitTime`（hpp L122-126，均为值对象；注释 L117-120 承认这些应改成指针并延迟构造）。
- `Create()`（cpp L114-）：轨道类型下拉（6 项，L117-118）、历元格式下拉（8 项，L119-120）、7 个输入参数 CheckBox+TextCtrl（SMA/ALT/ECC/INC/ROP/ROA/P，L145-181）、3 个时间参数（Epoch/RAAN/Initial LST，L159-165）、9 个输出只读框（L176-206）。
- `OnFindOrbit()`（cpp L2249-2523）：按 `orbitType` 调 `orbitSS.CalculateSunSync(paramOneVal, input1Val, ...)` 等，`IsError()` 时弹错并 `canClose=false`（L2258-2264），否则把 `GetSMA()/GetALT()/GetECC()/GetINC()/GetROP()/GetROA()/GetP()` 以 16 位精度 `%.16f` 填入输出框（L2265-2285）。各 `Display*`（L2618-3464）负责按轨道类型显隐输入参数。
- 结果取回：`GetElementsString()`（L3547）把输出拼成 `wxArrayString`、`GetElementsDouble()`（L3653）拼成 `Rvector6`、`GetEpoch()/GetEpochFormat()`（L3708-3730），OrbitPanel 的 `OnButton`（OrbitPanel.cpp L1090 起）在用户点 Orbit Designer 后据此回填六要素。

#### src/gui/spacecraft/OrbitSummaryDialog.hpp/.cpp（63 + 124 行）

职责：只读摘要对话框，展示轨道设计结果文本。`Create()`（cpp L85-91）放一个 `wxTE_MULTILINE|wxTE_READONLY|wxTE_RICH` 的 `wxTextCtrl`；构造时隐藏 Cancel/Help 按钮（cpp L52-53）；`LoadData/SaveData/ResetData` 为空实现。

#### src/gui/spacecraft/SpaceObjectSelectDialog.hpp/.cpp（84 + 332 行）

职责：空间对象多选对话框（可用/已选双列表 + 箭头按钮）。`Create()`（cpp L103-）可用列表 `theGuiManager->GetSpaceObjectListBox`，已选列表预填 `mSoSelList`；`OnButton` 按事件源移动条目并维护 `mHasSelectionChanged`；`GetSpaceObjectNames()` 返回选择结果。与 `PropagatorSelectDialog/CelesBodySelectDialog` 同属"双列表选择对话框"家族。

### 10.4 solarsys/ —— 太阳系与天体配置

#### src/gui/solarsys/UniversePanel.hpp/.cpp（114 + 917 行）

职责：太阳系（`SolarSystem`）顶层配置面板——历元源（DE 文件 / SPICE）、历元更新间隔、SPK/PCK 内核文件、是否用 TT 代替 TDB 驱动历元。

- 继承 `GmatPanel`；重写 `Create/LoadData/SaveData` 与 `OnScript`（hpp L45、L96-98）。
- `Create()`（cpp L153-315）：历元更新间隔文本（单位 seconds，L178-186）、历元源 ComboBox、DE 文件名文本+浏览按钮、SPK 内核文本+浏览、PCK 内核文本+浏览、`mOverrideCheckBox`（Use TT for Ephemeris）。
- `LoadData()`（cpp L316-469）：`theGuiInterpreter->GetPlanetarySourceTypes()/GetPlanetarySourceTypesInUse()` 取可用/在用历元源（L324-326）；`theSolarSystem->GetEphemUpdateInterval()`（L342）；`GetParameterID("EphemerisSource")` 读当前源（L370-372）；按源类型联动控件显隐——`TwoBodyPropagation` 禁用 DE 文件并隐藏 SPK/PCK（L379-389），`SPICE` 禁用 DE 文件（L400-405）；`GetStringParameter("SPKFilename"/"PCKFilename")` 与 `GetBooleanParameter("UseTTForEphemeris")` 填内核名与勾选框（L441-450）。
- `SaveData()`（cpp L479-681）：`CheckReal` 校验间隔（L499-503）；变更时 `SetEphemUpdateInterval(interval)`、`SetStringParameter(GetParameterID("EphemerisSource"), srcSelection)`、`SetStringParameter("SPKFilename", ...)` 等；SPK/PCK 文件保存前用 `FileManager` 解析路径并验证存在。

#### src/gui/solarsys/CelestialBodyPanel.hpp/.cpp（92 + 254 行）

职责：天体配置主面板——`wxNotebook` 聚合 Properties/Orbit/Orientation/Visualization 四个子面板（hpp L68-71）。

- 构造（cpp L62-77）：`origCelestialBody = GetConfiguredObject(name)`；`isUserDefined` 标志决定是否可编辑。
- `Create()`（cpp L99-130）：`theCelestialBody = (CelestialBody*)(origCelestialBody->Clone())`——克隆工作副本；四个子面板全部指向这份克隆。
- `SaveData()`（cpp L168-207）：与 SpacecraftPanel 相同套路——按 `IsDataChanged()` 驱动子面板保存并聚合 `CanClosePanel()`，最后 `origCelestialBody->Copy(theCelestialBody)` 整体写回（L204）。
- `OnPageChange`（cpp L218-253）：切页时 `Navigate()` 让首个可编辑项获得焦点而非选中高亮（修复 GMT-4723 的 wx3.0 问题，L231-233 注释）。

#### src/gui/solarsys/CelestialBodyPropertiesPanel.hpp/.cpp（144 + 667 行）

职责：天体属性页——引力常数 mu、赤道半径、扁率、PCK 行星常数内核列表。

- `SaveData()`（cpp L128-）：`muChanged/eqRadChanged/flatChanged` 分别经 `theCBPanel->CheckReal` 校验（mu/半径要求 >0，扁率 ≥0，L161-193）后 `SetGravitationalConstant(mu)/SetEquatorialRadius(eqRad)/SetFlattening(flat)`（L254-259）；PCK 内核先验证文件存在再 `SetStringParameter(GetParameterID("PlanetarySpiceKernelName"), strval)`（L231-233），删除经 `pckFilesToDelete` 调 `RemoveSpiceKernelName("Planetary", ...)`（L236-242）。
- `LoadData()`（L 起 ~L330 前）：`GetRealParameter("Mu"/"EquatorialRadius"/"Flattening")` + PCK 文件数组填充列表。

#### src/gui/solarsys/CelestialBodyOrbitPanel.hpp/.cpp（222 + 1257 行）

职责：天体轨道页——位置速度源（PosVelSource）、SPK 内核、NAIF ID、中心天体、以及非太阳天体的"初始二体状态"（历元 + SMA/ECC/INC/RAAN/AOP/TA）。

- `SaveData()`（cpp L161-）：`ephemSrcChanged` → `SetStringParameter(GetParameterID("PosVelSource"), strval)`（L179-181）；历元文件/SPK 文件逐一验证存在（L189-229）；`naifIDChanged` → `theCBPanel->CheckInteger` 校验后 `SetIntegerParameter("NAIFId", tmpint)`（L231-240）；`cBodyChanged` → `SetStringParameter("CentralBody")`（L248-252）；二体状态：历元经 `A1Mjd a1Epoch(tmpval)` 后 `SetTwoBodyEpoch(a1Epoch)`（L263-265），六根数逐项 `CheckReal` 校验后组成 `Rvector6` 再 `SetTwoBodyElements(elements)`（L267-，含 AOP/TA 弧度转换）。
- 控件显隐联动在 `LoadData`（L349 起）与事件处理器中：`isSun` 或非用户定义天体时隐藏二体输入区；SPICE 可用性由 `__USE_SPICE__` 决定。

#### src/gui/solarsys/CelestialBodyOrientationPanel.hpp/.cpp（203 + 1060 行）

职责：天体定向页——旋转数据源（SpinAxis/Constant/Sidereal/IAU2000/IAUSimplified/IAU2006 等）、章动更新间隔、自转轴赤经/赤纬常数与变率、旋转常数/速率、SPICE 框架 ID、FK 内核。

- `SaveData()`（cpp L149-348）：`rotationDataSourceChanged` → `SetStringParameter(GetParameterID("RotationDataSource"))`；各实数参数（`NutationUpdateInterval/SpinAxisRAConstant/SpinAxisRARate/SpinAxisDECConstant/SpinAxisDECRate/RotationConstant/RotationRate`）经 `CheckReal` 校验后 `SetRealParameter`；`spiceFrameIDChanged` → `SetStringParameter("SpiceFrameId")`；FK 内核与 Properties 页的 PCK 逻辑相同（验证文件→`SetStringParameter(GetParameterID("FramesSpiceKernelName"))`→删除经 `RemoveSpiceKernelName("Frames", ...)`）。
- `LoadData()`（cpp L349-434）：`isEarth/isLuna` 标志按天体名特判，控制哪些字段可编辑（如地球的旋转速率等字段只读，因为 IAU 模型已定义）。

#### src/gui/solarsys/CelestialBodyVisualizationPanel.hpp/.cpp（114 + 785 行）

职责：天体可视化页——纹理文件（`TextureMapFileName`）、3D 模型文件（`3DModelFile`）、模型偏移/旋转/缩放（`3DModelOffsetX/Y/Z`、`3DModelRotationX/Y/Z`、`3DModelScale`）。

- `LoadData()`（cpp L113-171）：全部经 `theBody->GetParameterID(...)` + `GetStringParameter/GetRealParameter` 读取，数值用 `guiManager->ToWxString` 格式化。
- `SaveData()`（cpp L181-）：文本是否被改由 `IsModified()` 判定；每个数值字段先 `theBody->IsParameterValid("3DModelOffsetX", strval)` 让 base 做合法值校验（拿 `GetLastErrorMessage()` 报错，L222-227），通过再 `GmatStringUtil::ToReal` 转数后 `SetRealParameter`——这是"校验交给 base"的典型用法。
- `Create()`（cpp L457-620）生成 9 个文本控件 + 2 个浏览按钮。

#### src/gui/solarsys/BarycenterPanel.hpp/.cpp（91 + 365 行）

职责：质心（Barycenter）配置面板——成员天体双列表 + 颜色面板。

- 构造（cpp L65-78）：`theClonedBarycenter = (Barycenter*)(theBarycenter->Clone())`；`mIsBuiltIn` 决定是否可编辑。
- `Create()`（cpp L104-145）：可用天体列表 `theGuiManager->GetCelestialBodyListBox` + 选中列表 + 箭头按钮 + `GmatColorPanel`（颜色属性，hpp L50、cpp L140）。
- `LoadData()`（cpp L155-）：内建质心用 `GetBuiltInNames()`，用户定义用 `GetStringArrayParameter("BodyNames")`（空时回落 `GetDefaultBodies()`，L159-169）；`SaveData()` 用 `TakeAction("Clear")` + `SetStringParameter("Add", body)` 重建成员列表。

#### src/gui/solarsys/LibrationPointPanel.hpp/.cpp（74 + 431 行）

职责：平动点（LibrationPoint）配置面板——主天体/次天体 ComboBox + L1~L5 下拉 + 颜色面板。

- `Create()`（cpp L141-199）：`theGuiManager->GetCelestialPointComboBox` 注册主/次天体；`librationList[] = {"L1","L2","L3","L4","L5"}`（L145）。
- `LoadData()`（cpp L209-250）：`UpdateComboBoxes()` 重新填天体列表后，`GetStringParameter("Primary"/"Secondary"/"Point")` 填三个下拉。
- `SaveData()`（cpp L260-356）：主/次天体不能相同（L271-278）；`GetParameterID("Primary")` + `SetStringParameter` + `SetRefObject(primary, Gmat::SPACE_POINT, spName)`（L293-296），J2000 体缺失时补 Earth（L299-300）；`SetStringParameter("Point")` 写平动点；最后 `theLibrationPt->Copy(theClonedLibPoint)`（L348）克隆写回。

#### src/gui/solarsys/CelesBodySelectDialog.hpp/.cpp（92 + 406 行）

职责：天体选择对话框（双列表）。`Create()`（cpp L116-）按 `mShowCalPoints` 决定用 `GetCelestialPointListBox`（含 LibrationPoint/Barycenter 等计算点）还是 `GetCelestialBodyListBox`；`OnSelectBody/OnListBoxDoubleClick`（支持双击移动）维护 `mBodyNames`；`ShowBodyOption` 控制隐藏天体（如从列表剔除某天体）。

### 10.5 hardware/ —— 推力器/电源硬件配置

#### src/gui/hardware/BurnThrusterPanel.hpp/.cpp（181 + 1341 行）

职责：推力器与机动的**通用基类面板**，同时服务 `ThrusterConfigPanel`（推力器）与 `ImpulsiveBurnSetupPanel`（脉冲机动）——本章第三种讲解重点（力模型勾选之外的"推力器/油箱"重点）。

- 继承 `GmatPanel`；`theObject` 指向被测对象，`localObject` 是"验证用克隆"（hpp L62-64）。
- `Create()`（cpp L138-537）：坐标系区（`coordSysComboBox` 由 `GetCoordSysComboBox` 注册并插入 `"Local"` 项（L164-169）、`originComboBox`、`axesComboBox`（枚举值来自 `theObject->GetPropertyEnumStrings("Axes")`，L179））；推力矢量区 `elem1-3TextCtrl`（L213-237）；按对象类型条件构造——`IsOfType(Gmat::THRUSTER)` 才有 Duty Cycle/Thrust Scale Factor（L242-259）与 `configButton`（多项式配置，L361-369），`IsOfType(Gmat::IMPULSIVE_BURN)` 才有 Isp（L338-348）；质量区 `decMassCheckBox`、油箱 `tankTxtCtrl/tankComboBox`（二选一，默认用混合比模式隐藏 ComboBox，L304-320）、`mixRatioTxtCtrl`、`tankSelectorButton`、`gravityAccelTextCtrl`。
- **`LoadData()`**（cpp L538-753）：推力方向参数名按类型区分——ImpulsiveBurn 用 `Element1/2/3`，Thruster 用 `ThrustDirection1/2/3`（L550-561）；逐参数 `GetParameterID` + `GetRealParameter/GetBooleanParameter/GetStringArrayParameter` 填控件（L567-592）；`MixRatio` 用 `GetRvectorParameter` 读（L599-603）；`useMixRatio` 为假时走单油箱模式（L610-638）；`DecrementMass` 未勾选时禁用油箱/混合比/重力加速度/Isp（L641-668）；化学推力器读 `C1..Cn/K1..Kn`，电推力器读 `ThrustCoeff1..n/MassFlowCoeff1..n`（L670-740，系数名经 `std::stringstream` 拼接）。
- **`SaveData()`**（cpp L758-798）——"克隆-校验-提交"三段式：

```cpp
   if (localObject != NULL) delete localObject;
   localObject = mObject->Clone();
   SaveData(localObject);
   localObject->TakeAction("ClearTanks");
   if (useMixRatio) {
      for (UnsignedInt i = 0; i < tankNames.size(); ++i)
         localObject->SetStringParameter("Tank", tankNames[i]);
      for (UnsignedInt i = 0; i < mixRatio.size(); ++i)
         localObject->SetRealParameter("MixRatio", mixRatio[i], i);
   }
   ...
   if (canClose)
      theObject->Copy(localObject);
```
  解读：先克隆出 `localObject`，把所有改动写到克隆上（`SaveData(localObject)` 内部用 `CheckReal/CheckRealRange` 校验并把非法输入置 `canClose=false`）；油箱/混合比用"ClearTanks + 逐条追加"重建；只有全部合法才 `theObject->Copy(localObject)` 提交——任何非法输入都不会污染真实对象。
- `SaveData(GmatBase *theObject)`（cpp L804-1007）：真正写参数的重载——`CoordinateSystem/Origin/Axes/Element1-3/DecrementMass/GravitationalAccel/ThrustDirection*` 等经 `GetParameterID + Set*Parameter` 落库（L818-1007），含 `SetRvectorParameter("ThrustDirection", Rvector3(elem1,elem2,elem3))` 与 `SetBooleanParameter`。
- 事件：`OnTextChange`（L1008）、`OnCheckBoxChange`（L1018，勾 DecrementMass 时联动油箱区使能）、`OnComboBoxChange`（L1069，坐标系/原点/轴联动 `UpdateOriginAxes()` L1227）、`OnButtonClick`（L1125，`configButton` 弹 `ThrusterCoefficientDialog`、`tankSelectorButton` 弹 `TankAndMixDialog` 并回填 `tankNames/mixRatio`）。

#### src/gui/hardware/ThrusterConfigPanel.hpp/.cpp（54 + 273 行）

职责：推力器配置面板，`BurnThrusterPanel` 的第一个派生类，追加推力器专属字段。

- 构造（cpp L53-73）：`isElectric = theObject->IsOfType("ElectricThruster")`（L65）；`SetObject(theObject)` 成功才 `Create(); Show();`。
- `LoadData()`（cpp L87-135）：先读 `DutyCycle/ThrustScaleFactor`（L96-100）；电推力器再读 `ThrustModel/MinimumUsablePower/MaximumUsablePower/FixedEfficiency/Isp/ConstantThrust`（L102-122）；然后 `BurnThrusterPanel::LoadData()`，最后 `EnableDataForThrustModel(thrustModel)` 按模型（ConstantThrust/Curve）显隐电推力器字段（L129-130，实现于 BurnThrusterPanel.cpp L1259-1305）。
- `SaveData()`（cpp L141-273）：`IsModified()` 判定 Duty Cycle/Scale Factor（L163-172）、电推力器的 Min/Max 功率（`>0` 校验，L188-201）、效率/Isp/常推力（L203-225）；`isThrustModelChanged` 写 `ThrustModel`（L230-235）；全部通过后 `BurnThrusterPanel::SaveData()` 走通用提交（L268）。

#### src/gui/hardware/PowerSystemConfigPanel.hpp/.cpp（157 + 972 行）

职责：电源系统（`PowerSystem`）配置面板，处理 SolarPowerSystem/NuclearPowerSystem 两类对象。

- 构造（cpp L74-109）：`isSolar = theObject->IsOfType("SolarPowerSystem")`；`localObject` 克隆提交模式与 BurnThrusterPanel 相同。
- `Create()`（cpp L132-395）：General 区（Epoch Format ComboBox、Initial Max Power（kW）、Decay Rate（percent/year）、Margin（percent））+ Coefficients 区（Bus Coeff1-3，单位 kW/kW·AU/kW·AU²，L220-245）；`isSolar` 追加 Shadow Model ComboBox、Shadow Bodies（只读文本 + Select 按钮，弹 `CelesBodySelectDialog`，L248-268）、Solar Coeff1-5（L270-318）。
- `LoadData()`（cpp L396-527）与 `SaveData(GmatBase *)`（cpp L565-762）：逐参数 `GetParameterID` + `Get/Set*Parameter`；`SaveData()`（L528-564）克隆 `localObject` → 写克隆 → `theObject->Copy(localObject)`。`OnBodiesEditButton`（L885）弹天体选择对话框回填 `shadowBodiesList`。

#### src/gui/hardware/TankAndMixDialog.hpp/.cpp（99 + 460 行）

职责：油箱 + 混合比编辑对话框——本章 wxGrid 多记录管理的代表。

- 继承 `GmatDialog`；数据：`selectedTanks/tankNames`（wxArrayString）+ `mixValues`（wxArrayDouble）。
- `Create()`（cpp L101-179）：左侧可用油箱列表 `GetFuelTankListBox`（L118-119）；右侧 **`wxGrid`**（L148-164）——`CreateGrid(100, 2)`，列 0 "Tank" 只读、列 1 "Mix Factor" 挂 `wxGridCellFloatRenderer` + `wxGridCellFloatEditor`（L157-164）。固定 100 行是硬编码上限（无自动增行逻辑）。
- `OnButton()`（cpp L192-281）：添加油箱 → 在网格找空行写入名字与默认 `"1.000000"` 混合比并选中（L222-231）；移除 → 因 `DeleteRows` 在 wxGrid 上不可靠，改为"后续行上移直到空行"的滚动式删除（L247-265 注释）；清空 → 遍历回填可用列表（L267-278）。
- `SaveData()`（L 起，cpp L284-）：把网格第 1 列数值读回 `mixValues`；`GetTankNames()/GetMixValues()` 供 `BurnThrusterPanel` 取回。此对话框是 `BurnThrusterPanel::OnButtonClick`（tankSelectorButton）的落点。

#### src/gui/hardware/ThrusterCoefficientDialog.hpp/.cpp（86 + 323 行）

职责：推力器多项式系数编辑对话框——两个 `wxGrid` 页（化学：C/K 系数；电：T/MF 系数）。

- 构造（cpp L55-86）：接收 `GmatBase *obj`、`numCoefs`、两组初值 `coefs1/coefs2`；`isElectric = obj->IsOfType("ElectricThruster")`。
- `Create()`（cpp L91-156）：`wxNotebook` 内两个 `wxGrid`，各 `CreateGrid(coefsCount, 3)`，列 = 系数名（只读）/值/单位（只读）（L102-118）；页名按化学/电切换（L144-153）。
- `LoadData()`（cpp L161-234）：系数名与单位来自 base——`GetStringArrayParameter("T_UNITS"/"MF_UNITS"/"C_UNITS"/"K_UNITS")`（L182-192），名字用 `ThrustCoeff1..`/`C1..` 等流拼接；`SetCellValue` 填充三列。
- `SaveData()`（cpp L239-323）：逐格 `CheckReal` 校验（L261），值变化即置 `coefs1Modified/coefs2Modified`；`GetCoefs1Values()/GetCoefs2Values()` 供 `BurnThrusterPanel` 取回写 `localObject`。

### 10.6 burn/ —— 机动配置

#### src/gui/burn/FiniteBurnSetupPanel.hpp/.cpp（78 + 344 行）

职责：有限推力机动（`FiniteBurn`）面板——可用/已选推力器双列表（一个 FiniteBurn 可驱动多个推力器）。

- 继承 `GmatPanel`；`MAX_PROP_ROW = 5`（hpp L43，最多 5 台推力器）。
- `Create()`（cpp L106-）：`theBurn->GetParameterID("Thrusters")` + `GetStringArrayParameter` 得到已选名单填排除表（L126-131）；可用列表 `GetThrusterListBox`、已选列表普通 `wxListBox`（L135-148）；按钮组与 ThrusterPanel 相同。
- `SaveData()`（L 起 ~L344）：`TakeAction("Clear")` + 逐条 `SetStringParameter("Thrusters", name)` 重建。`LoadData` 把已选推力器填回列表。

#### src/gui/burn/ImpulsiveBurnSetupPanel.hpp/.cpp（47 + 194 行）

职责：脉冲机动（`ImpulsiveBurn`）面板，`BurnThrusterPanel` 的第二个派生类。

- 构造（cpp L53-73）：`useMixRatio = false`（L65）——脉冲机动只有单油箱，不走混合比分支。
- `Create()`（cpp L87-116）：调 `BurnThrusterPanel::Create()` 后改写标签——`Element1/2/3`（km/s 单位，L102-107）、`vectorBoxSizer->SetLabel("Delta-V Vector")`（L108），体现"同一套布局、不同术语"的复用设计。
- `LoadData()`（cpp L122-144）：先填 Isp 再调基类 `LoadData()`。
- `SaveData(GmatBase *theObject)`（cpp L150-194）：Isp 校验（`>= 0`）后 `SetRealParameter("Isp")`，再 `BurnThrusterPanel::SaveData(theObject)`，最后 `theObject->Validate()`（L183）做一次质量消耗设置的整体校验。

### 10.7 event/ —— 事件定位器

#### src/gui/event/EventLocatorPanel.hpp/.cpp（204 + 1787 行）

职责：事件定位器面板，一个类服务三类对象——`ContactLocator`（测站接触）、`EclipseLocator`（地影）、`IntrusionLocator`（天体凌入），按 `locatorType` 枚举（hpp L195-201：CONTACT/ECLIPSE/INTRUSION/UNKNOWN）切换控件组。

- 继承 `GmatPanel`；`localObject` 克隆提交模式（hpp L55-56）；约 30 个 `isXxxChanged` 标志（hpp L66-92）。
- 构造（cpp L80-124）：`IsOfType` 判定三类定位器（L96-103）。
- `Create()`（cpp L154-590）：公共区——Spacecraft/Target ComboBox（CONTACT 用 `GetSpacecraftComboBox` 标 "Target"，L208-217）、Occulting/Intruding Bodies `wxCheckListBox`（L222-247，INTRUSION 时剔除持有传感器的航天器 L239-246）、Central Body（仅 INTRUSION，L252-258）；按类型分派——CONTACT 的 Observers（`GetGroundStationCheckListBox`，L274-284）、ECLIPSE 的 Eclipse Types（L286-291）、INTRUSION 的 Sensors（`GetImagerCheckListBox`，L293-297）；公共区还有 Filename + 浏览、Run Mode、Write Report、Use Entire Interval、Epoch Format/Initial/Final Epoch、light-time delay/恒星像差复选框（CONTACT 另有 light-time direction 下拉，L373-389）。
- `LoadData()`（cpp L591-992）：按定位器类型读 `Spacecraft/Target/OccultingBodies/IntrudingBodies/Observers/EclipseTypes/Sensors/Imagers/Filename/StepSize/InitialEpoch/FinalEpoch` 等参数填充（勾选列表经 `IsChecked/Check` 双向同步）。
- `SaveData(GmatBase *forObject)`（cpp L1034-1398）：`CheckReal` 校验 StepSize（L1052-1061）；`CheckFileName` 校验输出文件名（L1083-1092）；历元经 `CheckTimeFormatAndValue` 校验后 `SetStringParameter("InputEpochFormat"/"InitialEpoch"/"FinalEpoch")`（L1103-1137）；多值列表写回套路：`forObject->TakeAction("Clear", "OccultingBodies")` 后遍历 `IsChecked` 的项逐条 `SetStringParameter(paramID, bodyName)`（L1182-1195）；Eclipse Types 用 `SetOnOffParameter` 逐类型开关（L1210-）。`SaveData()`（L993-1033）克隆 `localObject` 后调 `SaveData(localObject)` 再 `theObject->Copy(localObject)`。

### 10.8 forcemodel/ —— 力模型辅助

#### src/gui/forcemodel/DragInputsDialog.hpp/.cpp（127 + 511 行）

职责：Jacchia-Roberts 阻力输入对话框——编辑 F10.7/F10.7A 太阳流量、地磁指数 Kp，以及历史/预测流量文件模型与 CSSI/Schatten 文件。

- 继承 `GmatDialog`；构造（cpp L68-98）接收 `DragForce *dragForce`（校验用）、`Real *dragBuffer`（3 元数值缓冲）与 `std::vector<std::string> *dragStringBuffer`（6 元字符串缓冲）——它**不直接写 DragForce**，而是写 PropagationConfigPanel 传入的缓冲，由面板在 SaveData 时统一落库（PropagationConfigPanel.cpp L1649-1661）。
- `Create()`（cpp L116-254）：Model Selection 区（historic/predicted 文件模型 ComboBox，选项 `ConstantFluxAndGeoMag/CSSISpaceWeatherFile/SchattenFile`，L171-183）+ Files 区（CSSI/Schatten 文件名只读文本 + 浏览按钮）+ Model Configuration 区（F10.7/F10.7A/Kp 文本、Schatten Error Model 下拉 `Nominal/PlusTwoSigma/MinusTwoSigma`、Timing 下拉 `NominalCycle/EarlyCycle/LateCycle`，L178-183）。
- `LoadData()`（cpp L260-283）：从两个缓冲按索引填控件（`theForceData[0..2]`、`(*theForceStringArray)[0..5]`）。
- `SaveData()`（cpp L289-441）：`CheckReal` + `CheckRealRange`（Kp ∈ [0,9]，L311-314）；非恒定流量模型时用 `theDragForce->CheckFluxFile(fileToCheck, isHistoric)` 验证文件内容（L322-366）；通过后写回缓冲（L377-429）。文件为空弹错（L384-401）。

## 三、关键设计模式与数据流

### 3.1 面板基类生命周期（GmatPanel/GmatDialog 模板）

本章 74 个文件里，凡"独立窗口面板"一律继承 `GmatPanel`（`PropagationConfigPanel`、`SpacecraftPanel`、`CoordSystemConfigPanel`、`CelestialBodyPanel`、`UniversePanel`、`BarycenterPanel`、`LibrationPointPanel`、`FormationSetupPanel`、`BurnThrusterPanel` 及其派生、`EventLocatorPanel`、`PowerSystemConfigPanel`、`FiniteBurnSetupPanel`），凡"模态对话框"一律继承 `GmatDialog`（`PropagatorSelectDialog`、`CoordSysCreateDialog`、`OrbitDesignerDialog`、`OrbitSummaryDialog`、`SpaceObjectSelectDialog`、`CelesBodySelectDialog`、`TankAndMixDialog`、`ThrusterCoefficientDialog`、`DragInputsDialog`）。两类基类都要求派生类实现虚函数三/四件套：

```
GmatPanel:  构造 → Create() 建控件 → Show() → LoadData() 填值
           用户编辑 → EnableUpdate(true) 亮 Apply
           Apply/OK → SaveData() 校验+写回 → canClose 决定是否允许关闭
GmatDialog: 构造 → Create() → ShowData() → LoadData()
           SaveData() 结果经 Get*() 访问器交给调用方（如 GetPropagatorName/GetElementsDouble）
```

"改动标志位"（`isXxxChanged/dataChanged`）是所有面板的状态机核心：事件处理器置位 + `EnableUpdate(true)`，`SaveData` 只处理置位区块，成功后清零并 `EnableUpdate(false)`。`GmatPanel`/`GmatDialog`/`GuiItemManager` 基类本身位于 `src/gui/foundation/`，逐文件讲解见 [第2章](CH02-foundation.md)。

### 3.2 克隆-编辑-复制（Clone-Edit-Copy）与克隆-校验-提交

两个互补的写回策略，避免 GUI 编辑污染真实对象：

- **面板级克隆工作副本**：`SpacecraftPanel`（`currentSpacecraft = new Spacecraft(*theSpacecraft)`，SpacecraftPanel.cpp L138）、`CelestialBodyPanel`（`theCelestialBody = origCelestialBody->Clone()`，CelestialBodyPanel.cpp L102）、`BarycenterPanel`（`theClonedBarycenter`，BarycenterPanel.cpp L70）、`LibrationPointPanel`（`theClonedLibPoint`，L76）、`FormationSetupPanel`（`mClonedFormation`，FormationSetupPanel.cpp L84）。所有子面板编辑副本；`SaveData` 聚合子面板成功后 `真实对象->Copy(副本)`（SpacecraftPanel.cpp L364、CelestialBodyPanel.cpp L204、LibrationPointPanel.cpp L348）。
- **保存时克隆校验**：`BurnThrusterPanel::SaveData()`（BurnThrusterPanel.cpp L758-798）——`localObject = mObject->Clone()` → 写克隆 → `theObject->Copy(localObject)`；`PowerSystemConfigPanel`、`EventLocatorPanel`、`ThrusterConfigPanel` 同款。`CoordPanel::SaveData` 更进一步：`csClone = coordSys->Clone()` 后在 `SetRefObject(axis/origin)` 异常分支里 `coordSys->Copy(csClone)` 回滚（CoordPanel.cpp L1312-1347）。

### 3.3 控件→base 对象的参数绑定链路（GetParameterID + Get/Set*Parameter）

用户需求中的"wxTextCtrl 经 ElementWrapper 到 base 对象"在本仓库**不成立**：`ElementWrapper`（src/base/foundation/ElementWrapper.hpp/.cpp，见 [第2章](CH02-foundation.md)）只服务脚本/方程解析（`ElementWrapper` 把字符串表达式包装成可求值的参数访问器），GUI 面板从未包含它（对 `src/gui` 全目录检索 `ElementWrapper` 零命中）。GUI 实际链路是**直连 GmatBase 参数系统**，以 `BallisticsMassPanel::SaveData` 为例（BallisticsMassPanel.cpp L378-408）：

```cpp
   Integer dryMassID = theSpacecraft->GetParameterID("DryMass");
   ...
   inputString = dryMassTextCtrl->GetValue();
   if ((GmatStringUtil::ToReal(inputString,&rvalue)) && (rvalue >= 0.0))
      theSpacecraft->SetRealParameter(dryMassID, rvalue);
   else { ...canClose = false; }
```

完整链路（读方向与写方向对称）：

```
wxTextCtrl::GetValue()  (wxString)
   → GmatStringUtil::ToReal / theGuiManager->ToWxString   (字符串↔Real 互转)
   → theObject->GetParameterID("DryMass")                  (GmatBase 参数表查 ID)
   → theObject->GetRealParameter(id) / SetRealParameter(id, val)
   → GmatBase 内部按 id 分发的 Set/Get 实现（含单位换算与范围检查，见 [第2章](CH02-foundation.md)）
```

特例：①多值字符串参数（Thrusters/Tanks/OccultingBodies）用 `TakeAction("Clear"/"RemoveXxx") + 逐条 SetStringParameter` 重建（ThrusterPanel.cpp L192-206、EventLocatorPanel.cpp L1182-1195）；②Rvector 参数用 `SetRvectorParameter("ThrustDirection", Rvector3(...))`（BurnThrusterPanel.cpp L818-）；③"校验交给 base"：`CelestialBodyVisualizationPanel::SaveData` 先 `theBody->IsParameterValid("3DModelOffsetX", strval)` 再转数写回（L222-232）；④开关类参数用 `Get/SetOnOffParameter`（PropagationConfigPanel.cpp L1026-1031）。

### 3.4 GuiItemManager 资源注册/注销与刷新

所有需要"跟随全局对象集合变化"的 ComboBox/ListBox 都经 `GuiItemManager` 注册：`GetCelestialBodyComboBox`（PropagationConfigPanel.cpp L452）、`GetCoordSysComboBox`（BurnThrusterPanel.cpp L165）、`GetThrusterListBox`（ThrusterPanel.cpp L121）、`GetFuelTankListBox`（TankPanel.cpp L139）、`GetSpaceObjectListBox`（FormationSetupPanel.cpp L142）、`GetCelestialPointComboBox`（LibrationPointPanel.cpp L159）、`GetSpacePointCheckListBox`（EventLocatorPanel.cpp L227）等。配套纪律：析构里必须 `UnregisterComboBox/UnregisterListBox/UnregisterCheckListBox`（PropagationConfigPanel.cpp L175-181、ThrusterPanel.cpp L74-76、EventLocatorPanel.cpp L135-141）。资源变化通知：`SpacecraftPanel::RefreshObjects(Gmat::COORDINATE_SYSTEM)` → `OrbitPanel::RefreshComponents()`（SpacecraftPanel.cpp L404-415）重建坐标系下拉；`LibrationPointPanel` 构造时 `AddToResourceUpdateListeners(this)`（L155）实现天体增删即时刷新。

### 3.5 组合面板（Notebook 聚合）与按需写回

两个复合面板用 `wxNotebook` 聚合子面板：

- `SpacecraftPanel`：8 页（含二级 Actuators 笔记本），`SaveData` 只驱动 `IsDataChanged()` 为真的子面板，且**先做全部校验、再统一提交**（SpacecraftPanel.cpp L317-352 先聚合 `CanClosePanel`，L354-361 才调 Tanks/Thruster/PowerSystem 的保存，L364 最后 `Copy`）。
- `CelestialBodyPanel`：4 页（Properties/Orbit/Orientation/Visualization），同款聚合逻辑（CelestialBodyPanel.cpp L177-204）。

子面板自身是普通 `wxPanel`（OrbitPanel/AttitudePanel/BallisticsMassPanel/TankPanel/ThrusterPanel/SpicePanel/VisualModelPanel/PowerSystemPanel/CoordPanel/CelestialBody*Panel），通过 `IsDataChanged()/CanClosePanel()` 两个访问器向宿主汇报状态——这是"宿主-子面板"契约的核心接口。

### 3.6 工厂式对象创建

GUI 不直接 `new` base 对象，一律经 `GuiInterpreter` 工厂，保证对象注册进配置库：`CreateObject(integratorType, name)`（PropagationConfigPanel.cpp L2161-2163）、`CreateNewODEModel(theForceModelName)`（L2205）、`CreateObject("GravityField","")`（L1531）、`CreateObject(axisType, "")`（CoordPanel.cpp L668）、`CreateObject(attitudeModel, "")`（AttitudePanel.cpp L1067-1068）、`CreateObject("CoordinateSystem", coordName)`（CoordPanel.cpp L1280-1281）。工厂项列表（哪些积分器/大气模型可用）同样来自 `theGuiInterpreter->GetListOfFactoryItems(...)`（PropagationConfigPanel.cpp L2075-2089），实现 GUI 与引擎注册表自动同步。

### 3.7 双列表（available/selected）与 wxGrid 多记录管理

- **双列表选择**（ThrusterPanel/TankPanel/FiniteBurnSetupPanel/FormationSetupPanel/BarycenterPanel/SpaceObjectSelectDialog/PropagatorSelectDialog/CelesBodySelectDialog）：左可用列表由 GuiItemManager 按排除表自动过滤，右已选列表普通 `wxListBox`；`->/<-/=>/<=` 按钮或双击移动条目，同步维护排除表；保存时 `TakeAction("Clear") + 逐条 SetStringParameter`。
- **wxGrid**（TankAndMixDialog：100×2 只读列+浮点编辑列；ThrusterCoefficientDialog：`coefsCount×3` 系数/值/单位）：用 `wxGridCellFloatRenderer/wxGridCellFloatEditor` 提供数值编辑，`SetReadOnly` 锁定元数据列，保存时逐格 `CheckReal` 校验并收集"值是否变化"标志（ThrusterCoefficientDialog.cpp L254-274）。TankAndMixDialog 的"删除行上移"（L247-265）与 100 行硬上限是值得注意的实现细节（wxGrid 无便捷 DeleteRows，作者选择滚动式清理）。

### 3.8 力模型配置的 GUI 落点

本 clone 没有独立 `ForceModelPanel`；`PropagationConfigPanel` 的 Force Model 区块承担全部力模型配置：`ODEModel` 的 `CentralBody/ErrorControl`、主天体的 `GravityField`（模型/阶次/STM/势文件/潮汐）、`DragForce`（大气模型 + `DragInputsDialog` 缓冲 + DragModel）、`SolarRadiationPressure`（SRP 勾选 + 模型下拉）、`RelativisticCorrection` 勾选。保存时按 `ForceType` 缓冲**整体重建** `ODEModel`（PropagationConfigPanel.cpp L1486-1550），与 base 侧 `ODEModel::AddForce` 的运行时装配（见 [第6章](CH06-dynamics.md)）一一对应；`ShowForceModel`（L4911-4930）是开发期打印力列表的调试入口。

## 四、文件清单附录

### 表 10-1 src/gui/propagator/（4 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/propagator/PropagationConfigPanel.hpp | 传播配置面板声明；ForceType 结构、标志位、控件 ID | PropagationConfigPanel、ForceType、ErrorControlType |
| src/gui/propagator/PropagationConfigPanel.cpp | 积分器/力模型/SPK 配置实现；ODEModel 重建 | Initialize(L2025)、LoadData(L866)、SaveData(L1334)、DisplayIntegratorData(L2140)、ShowIntegratorLayout(L4934) |
| src/gui/propagator/PropagatorSelectDialog.hpp | 传播器选择对话框声明 | PropagatorSelectDialog |
| src/gui/propagator/PropagatorSelectDialog.cpp | PROP_SETUP 列表选择 | Create(L78)、OnButton(L144) |

### 表 10-2 src/gui/coordsystem/（6 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/coordsystem/CoordPanel.hpp | 坐标系通用子面板声明；显隐开关位 | CoordPanel、Get*ComboBox |
| src/gui/coordsystem/CoordPanel.cpp | 轴/原点/约束配置；轴系创建与校验 | EnableOptions(L100)、CreateAxis(L648)、IsValidAxis(L793)、SaveData(L1247) |
| src/gui/coordsystem/CoordSystemConfigPanel.hpp | 坐标系配置面板声明 | CoordSystemConfigPanel |
| src/gui/coordsystem/CoordSystemConfigPanel.cpp | 已有坐标系编辑 | LoadData(L116)、SaveData(L184)、OnComboUpdate(L406) |
| src/gui/coordsystem/CoordSysCreateDialog.hpp | 新建坐标系对话框声明 | CoordSysCreateDialog |
| src/gui/coordsystem/CoordSysCreateDialog.cpp | 名字校验 + 轴创建落库 | SaveData(L174)、OnTextUpdate(L344) |

### 表 10-3 src/gui/spacecraft/（28 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/spacecraft/SpacecraftPanel.hpp | 航天器主面板声明 | SpacecraftPanel、ID_NOTEBOOK |
| src/gui/spacecraft/SpacecraftPanel.cpp | Notebook 聚合 8 子面板；克隆写回 | Create(L131)、LoadData(L256)、SaveData(L303)、RefreshObjects(L404) |
| src/gui/spacecraft/OrbitPanel.hpp | 轨道页声明；状态/坐标系缓存 | OrbitPanel、mCartState、mOutState |
| src/gui/spacecraft/OrbitPanel.cpp | 六要素/笛卡尔切换、坐标换算 | OnComboBoxChange(L783)、DisplayState(L1339)、BuildState(L1718)、CheckState(L1890) |
| src/gui/spacecraft/AttitudePanel.hpp | 姿态页声明；StateType/RateStateType 枚举 | AttitudePanel、AttStateTypeCount |
| src/gui/spacecraft/AttitudePanel.cpp | 姿态模型/表示切换、换算 | LoadData(L852)、SaveData(L1025)、DisplayDataForModel(L1989)、LoadAttitudeAndRateData(L3487) |
| src/gui/spacecraft/BallisticsMassPanel.hpp | 弹道/质量页声明 | BallisticsMassPanel |
| src/gui/spacecraft/BallisticsMassPanel.cpp | 干重/Cd/Cr/面积/SPAD 读写 | LoadData(L310)、SaveData(L372) |
| src/gui/spacecraft/ThrusterPanel.hpp | 推力器挂接页声明 | ThrusterPanel、mExcludedThrusterList |
| src/gui/spacecraft/ThrusterPanel.cpp | Thrusters 多值参数双列表管理 | Create(L85)、SaveData(L192)、OnButtonClick(L211) |
| src/gui/spacecraft/TankPanel.hpp | 油箱挂接页声明 | TankPanel、mExcludedTankList |
| src/gui/spacecraft/TankPanel.cpp | Tanks 多值参数双列表管理 | Create(L85)、SaveData(L225) |
| src/gui/spacecraft/FormationSetupPanel.hpp | 编队成员面板声明 | FormationSetupPanel |
| src/gui/spacecraft/FormationSetupPanel.cpp | Formation Add/Clear 成员管理 | Create(L118)、LoadData(L210)、SaveData(L234) |
| src/gui/spacecraft/PowerSystemPanel.hpp | 电源选择页声明 | PowerSystemPanel |
| src/gui/spacecraft/PowerSystemPanel.cpp | PowerSystem 组合框绑定 | LoadData(L153)、SaveData(L177) |
| src/gui/spacecraft/SpicePanel.hpp | SPICE 面板声明（__USE_SPICE__） | SpicePanel、spk/ck/sclk/fk 内核数组 |
| src/gui/spacecraft/SpicePanel.cpp | 四类内核列表 + NAIF ID | SaveData(L134)、LoadData(L364)、Create(L442) |
| src/gui/spacecraft/VisualModelPanel.hpp | 可视化模型页声明 | VisualModelPanel、滑块/颜色控件 |
| src/gui/spacecraft/VisualModelPanel.cpp | 模型文件/变换滑块/颜色 | LoadData(L438)、InitializeCanvas(L549)、SaveData(L907) |
| src/gui/spacecraft/VisualModelCanvas.hpp | OpenGL 画布声明 | VisualModelCanvas、Camera、Light |
| src/gui/spacecraft/VisualModelCanvas.cpp | 模型渲染/相机/光照 | OnPaint(L127)、LoadModel(L)、DrawAxes |
| src/gui/spacecraft/OrbitDesignerDialog.hpp | 轨道设计器声明；sunElements 结构 | OrbitDesignerDialog、SunSync/RepeatSunSync/RepeatGroundTrack/Frozen |
| src/gui/spacecraft/OrbitDesignerDialog.cpp | 6 类标称轨道反解 | OnFindOrbit(L2249)、Display*（L2618-3464）、GetElementsString(L3547) |
| src/gui/spacecraft/OrbitSummaryDialog.hpp | 摘要对话框声明 | OrbitSummaryDialog |
| src/gui/spacecraft/OrbitSummaryDialog.cpp | 只读多行摘要 | Create(L85) |
| src/gui/spacecraft/SpaceObjectSelectDialog.hpp | 空间对象选择对话框声明 | SpaceObjectSelectDialog |
| src/gui/spacecraft/SpaceObjectSelectDialog.cpp | 双列表多选 | Create(L103)、OnButton |

### 表 10-4 src/gui/solarsys/（18 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/solarsys/UniversePanel.hpp | 太阳系配置面板声明 | UniversePanel |
| src/gui/solarsys/UniversePanel.cpp | 历元源/SPK/PCK/TT 配置 | Create(L153)、LoadData(L316)、SaveData(L479) |
| src/gui/solarsys/CelestialBodyPanel.hpp | 天体主面板声明 | CelestialBodyPanel |
| src/gui/solarsys/CelestialBodyPanel.cpp | 4 页 Notebook 聚合 | Create(L99)、SaveData(L168)、OnPageChange(L218) |
| src/gui/solarsys/CelestialBodyPropertiesPanel.hpp | 属性页声明 | CelestialBodyPropertiesPanel |
| src/gui/solarsys/CelestialBodyPropertiesPanel.cpp | mu/半径/扁率/PCK | SaveData(L128) |
| src/gui/solarsys/CelestialBodyOrbitPanel.hpp | 天体轨道页声明 | CelestialBodyOrbitPanel |
| src/gui/solarsys/CelestialBodyOrbitPanel.cpp | 历元源/SPK/NAIF/二体根数 | SaveData(L161) |
| src/gui/solarsys/CelestialBodyOrientationPanel.hpp | 天体定向页声明 | CelestialBodyOrientationPanel |
| src/gui/solarsys/CelestialBodyOrientationPanel.cpp | 自转轴/旋转速率/FK | SaveData(L149)、LoadData(L349) |
| src/gui/solarsys/CelestialBodyVisualizationPanel.hpp | 天体可视化页声明 | CelestialBodyVisualizationPanel |
| src/gui/solarsys/CelestialBodyVisualizationPanel.cpp | 纹理/3D 模型属性 | LoadData(L113)、SaveData(L181) |
| src/gui/solarsys/BarycenterPanel.hpp | 质心面板声明 | BarycenterPanel |
| src/gui/solarsys/BarycenterPanel.cpp | 成员天体双列表 + 颜色 | Create(L104)、LoadData(L155) |
| src/gui/solarsys/LibrationPointPanel.hpp | 平动点面板声明 | LibrationPointPanel |
| src/gui/solarsys/LibrationPointPanel.cpp | 主/次天体 + L1~L5 | Create(L141)、LoadData(L209)、SaveData(L260) |
| src/gui/solarsys/CelesBodySelectDialog.hpp | 天体选择对话框声明 | CelesBodySelectDialog |
| src/gui/solarsys/CelesBodySelectDialog.cpp | 双列表选择（可含计算点） | Create(L116)、OnSelectBody |

### 表 10-5 src/gui/hardware/（10 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/hardware/BurnThrusterPanel.hpp | 推力器/机动通用面板声明 | BurnThrusterPanel、系数缓冲 |
| src/gui/hardware/BurnThrusterPanel.cpp | 坐标系/推力矢量/油箱/系数；克隆校验提交 | Create(L138)、LoadData(L538)、SaveData(L758)、SaveData(GmatBase*)(L804) |
| src/gui/hardware/ThrusterConfigPanel.hpp | 推力器面板声明（派生） | ThrusterConfigPanel |
| src/gui/hardware/ThrusterConfigPanel.cpp | DutyCycle/电推力器字段 | LoadData(L87)、SaveData(L141) |
| src/gui/hardware/PowerSystemConfigPanel.hpp | 电源系统配置面板声明 | PowerSystemConfigPanel |
| src/gui/hardware/PowerSystemConfigPanel.cpp | 功率/衰减/裕度/系数/影锥 | Create(L132)、LoadData(L396)、SaveData(GmatBase*)(L565) |
| src/gui/hardware/TankAndMixDialog.hpp | 油箱+混合比对话框声明 | TankAndMixDialog、wxGridCellFloatRenderer |
| src/gui/hardware/TankAndMixDialog.cpp | 100 行混合比网格编辑 | Create(L101)、OnButton(L192) |
| src/gui/hardware/ThrusterCoefficientDialog.hpp | 系数对话框声明 | ThrusterCoefficientDialog |
| src/gui/hardware/ThrusterCoefficientDialog.cpp | C/K 或 T/MF 双网格编辑 | Create(L91)、LoadData(L161)、SaveData(L239) |

### 表 10-6 src/gui/burn/（4 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/burn/FiniteBurnSetupPanel.hpp | 有限推力机动面板声明 | FiniteBurnSetupPanel、MAX_PROP_ROW |
| src/gui/burn/FiniteBurnSetupPanel.cpp | Thrusters 双列表管理 | Create(L106)、SaveData |
| src/gui/burn/ImpulsiveBurnSetupPanel.hpp | 脉冲机动面板声明（派生） | ImpulsiveBurnSetupPanel |
| src/gui/burn/ImpulsiveBurnSetupPanel.cpp | Element1-3/Delta-V/Isp | Create(L87)、SaveData(GmatBase*)(L150) |

### 表 10-7 src/gui/event/（2 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/event/EventLocatorPanel.hpp | 事件定位器面板声明；locatorType 枚举 | EventLocatorPanel、CONTACT/ECLIPSE/INTRUSION |
| src/gui/event/EventLocatorPanel.cpp | 三类定位器参数编辑 | Create(L154)、LoadData(L591)、SaveData(GmatBase*)(L1034) |

### 表 10-8 src/gui/forcemodel/（2 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/forcemodel/DragInputsDialog.hpp | 阻力输入对话框声明 | DragInputsDialog |
| src/gui/forcemodel/DragInputsDialog.cpp | F10.7/Kp/流量文件编辑（写缓冲） | Create(L116)、LoadData(L260)、SaveData(L289) |
