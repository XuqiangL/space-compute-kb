# 第11章 GUI 命令、求解器、函数与其余面板

本章范围：`src/gui` 下的 `command`、`function`、`solver`、`subscriber`、`rendering`、`resource`、`asset`、`plugin`、`include` 九个目录，共 **348 个文件**（142 个 C++ 代码文件、200 个位图/图标、6 个资源/数据文件）。核心主题：命令面板（GmatCommandPanel 家族）与 GmatCommand 子类的双向同步、求解器面板的容差/最大迭代参数网格、订阅器（XYPlot/ReportFile/OrbitView/GroundTrackPlot/EphemerisFile）配置面板、OpenGL 渲染与 3DS 模型加载体系、资源/插件/通用头文件与 200 个图标位图。

> 说明：本版本源码树中**不存在 SolvePanel**（旧版 GMAT 曾有此面板）；"求解"类命令面板由 `TargetPanel`/`OptimizePanel` 承担，求解器本身的参数面板在 `solver` 目录。命令基类见 [第5章](CH05-command.md)，求解器/订阅者/函数基类见 [第8章](CH08-base-subsystems.md)，GUI 框架（GmatPanel/GuiInterpreter/GuiItemManager/GmatAppData）见 [第9章](CH09-gui-core.md)，动力学类面板见 [第10章](CH10-gui-dynamics.md)，插件体系见 [第4章](CH04-executive-factory.md) 与 [第13章](CH13-plugins-a.md)。

## 一、本章目录树

```
src/gui/
├── asset/          (2 文件)  GroundStationPanel.hpp/.cpp          —— 地面站配置面板
├── command/        (36 文件) 18 个命令面板 × (hpp+cpp)            —— 命令配置面板家族
├── function/       (4 文件)  FunctionSetupPanel / MatlabFunctionSetupPanel
├── include/        (204 文件) DoxygenGuiIntro.hpp、gmatwxdefs.hpp、gmatwxrcs.hpp、
│                              ddesetup.hpp、bitmaps/（200 个 .xpm/.png/.ico/.icns/.bmp/.gif）
├── plugin/         (2 文件)  WxGuiInterface.hpp/.cpp              —— 插件 GUI 单例接口
├── rendering/      (25 文件) Camera/Light/Rendering/GmatOpenGLSupport/FallbackFont/
│                              GLStars/LoadPOV/ModelManager/ModelObject/Structure/
│                              StructureReader/StructureReader3ds/SurfaceBase
├── resource/       (6 文件)  GmatIcon.rc、GmatRc.rc、TrajectoryPlot.rc、
│                              GMAT.ico、GMATIcon.icns、GMATMac.icns
├── solver/         (12 文件) 6 个求解器面板 × (hpp+cpp)
└── subscriber/     (57 文件) 配置面板 8 + 3D 画布 3 + 时序图画布 5 + MDI 框架 9 +
                              地面轨迹 3 + 对话框 2 + 其余杂项（详见正文）
```

## 二、逐文件/逐类讲解

### 2.1 command 目录（36 个文件）

本目录共 18 个面板，全部 `public GmatPanel`。每个面板持有一个 `GmatCommand*`（命令基类见 [第5章](CH05-command.md)），通过 GmatBase 参数表 API（`GetParameterID` / `GetStringParameter` / `SetStringParameter` 等）与命令对象双向同步；`LoadData()` 负责"引擎 → 控件"，`SaveData()` 负责"控件 → 引擎"，并由 `canClose` 标志与 `EnableUpdate()` 控制 Apply 按钮状态（契约见 [第9章](CH09-gui-core.md) 的 GmatPanel）。

#### GmatCommandPanel（GmatCommandPanel.hpp / GmatCommandPanel.cpp）

- **职责**：把命令的生成串（generating string）暴露为只读/可编辑文本框的通用命令面板，是所有"没有专门面板"命令的兜底。
- **关键类/函数**：
  - `GmatCommandPanel(wxWindow*, GmatCommand*)`（cpp L67）：保存 `theCommand`，并把 `mObject = (GmatBase*)cmd` 交给基类 GmatPanel 的"Show Script"按钮；随后 `Create()` 建控件、`EnableUpdate(false)` 关闭 Apply。
  - `Create()`（cpp L116）：只创建一个 `wxTextCtrl`（L130-131），放入 `theMiddleSizer`。
  - `LoadData()`（cpp L149）：把 `theCommand->GetGeneratingString(Gmat::NO_COMMENTS)` 填入文本框（L157-158）。
  - `SaveData()`（cpp L175）：核心校验链 `SetGeneratingString → InterpretAction → VerifyObjects → theGuiInterpreter->ValidateCommand`，任一步失败则 `canClose = false` 并弹窗。
  - `OnTextChange()`（cpp L242）：任何文本改动即 `EnableUpdate(true)`。

```cpp
// src/gui/command/GmatCommandPanel.cpp L189-202（SaveData 校验链）
std::string genString = theCommand->GetGeneratingString(Gmat::NO_COMMENTS);
try
{
   std::string cmdStr = commandTextCtrl->GetValue().WX_TO_STD_STRING;
   theCommand->SetGeneratingString(cmdStr);
   if (!theCommand->InterpretAction())
      canClose = false;

   else if (!theCommand->VerifyObjects())
      canClose = false;

   // Now validate command and create element wrappers
   else if (!theGuiInterpreter->ValidateCommand(theCommand))
      canClose = false;
}
```
逐行解释：先备份原生成串（失败时回滚，见 catch 块 L207-208）；把文本框字符串写回命令；`InterpretAction()` 让命令把脚本字符串解析为内部结构；`VerifyObjects()` 校验引用对象存在；最后经 `GuiInterpreter::ValidateCommand` 让解释器做整条命令的最终校验并建立元素包装。这是"文本式"命令面板双向同步的标准闭环：面板修改 → 命令内部状态 → 引擎可执行的命令序列。

#### PropagatePanel（PropagatePanel.hpp / PropagatePanel.cpp）

- **职责**：Propagate 命令配置面板：选择 Propagator 与 SpaceObject 的组合、配置停止条件（StopCondition）、反向传播、STM/A-matrix 选项与停止容差。
- **关键类/函数**：
  - 网格常量（hpp L60-72）：`MAX_PROP_ROW=15`、`MAX_PROP_COL=4`、`MAX_STOPCOND_ROW=10`、`MAX_STOPCOND_COL=5`，以及列索引常量 `PROP_NAME_SEL_COL/PROP_NAME_COL/PROP_SOS_SEL_COL/PROP_SOS_COL/STOPCOND_LEFT_SEL_COL/STOPCOND_LEFT_COL/STOPCOND_RELOPER_COL/STOPCOND_RIGHT_SEL_COL/STOPCOND_RIGHT_COL`——"选择列（勾选生效）+ 值列"成对出现，是 GMAT 网格面板的通用布局。
  - 数据暂存结构 `PropType`（hpp L74-81）与 `StopCondType`（hpp L83-92）：`isChanged` 脏标记 + `wxString` 界面值 + `StopCondition*` 底层指针，SaveData 时按行回写。
  - `Create()`（cpp L171）建双网格与复选框；`InitializeData()`（L355）、`DisplayPropagator()`（L385）、`DisplayStopCondition()`（L406）、`UpdateStopCondition(Integer)`（L443）。
  - 行内编辑回调：`GetNewPropagatorName`（L525）、`GetNewSpaceObjectList`（L549）、`GetNewStopCondLeftValue`（L613）、`GetNewStopCondRightValue`（L656）——用户点开下拉/选择框时用 `GuiItemManager` 组装候选列表。
  - `LoadData()`（L947）把 `thePropCmd` 的 `Propagator`/`SpaceObject`/`StopCondition` 列表灌入网格；`SaveData()`（L1130）反向写回。
  - 重命名联动：`PrepareObjectNameChange()`（L119）与 `ObjectNameChanged()`（L139）——资源树重命名 Propagator/Spacecraft 时同步网格文本。
- **重点展开（双向同步）**：面板与 `Propagate` 命令（[第5章](CH05-command.md)）的同步不是逐字段 `SetStringParameter`，而是"整行校验 + 整表回写"。SaveData 先把 15×4 网格全部读出，统计空行、缺传播器、缺航天器三类错误：

```cpp
// src/gui/command/PropagatePanel.cpp L1144-1155（网格完整性检查）
for (Integer i=0; i<MAX_PROP_ROW; i++)
{
   propName = propGrid->GetCellValue(i, PROP_NAME_COL);
   soNames = propGrid->GetCellValue(i, PROP_SOS_COL);

   if (propName == "" && soNames == "")
      ++blankProps;
   else if (propName != "" && soNames == "")
      emptySos.Add(propName);
   else if (propName == "" && soNames != "")
      emptyProps.Add(soNames);
}
```
随后（L1161-1222）对每个非空传播器调用 `theGuiInterpreter->GetConfiguredObject()` 验证其确为 `PropSetup`，对航天器字符串按逗号拆分逐名验证为 `SpaceObject`，并禁止"Formation + STM/A-matrix"组合（L1210-1217）。全部通过后 `canClose=true` 才允许关闭面板；修改被丢弃则回滚。

#### TargetPanel（TargetPanel.hpp / TargetPanel.cpp）

- **职责**：Target 命令面板：选择求解器（Targeter）、求解模式、退出模式、进度窗口与"Apply Corrections"按钮。
- **关键类/函数**：
  - 控件：`mSolverComboBox`（Targeter 名）、`mSolverModeComboBox`（SolveMode）、`mExitModeComboBox`（ExitMode）、`mProgressWindowCheckBox`、`mApplyCorrectionsButton`（hpp L48-52）。
  - `Create()`（cpp L84）；`LoadData()`（L160）；`SaveData()`（L192）；`OnComboBoxChange`（L224）；`OnApplyButtonPress`（L237）。
- **重点展开（双向同步的"短参数表"形态）**：Target 命令的参数都是求解器顶层字符串/布尔参数，面板直读直写，无需网格：

```cpp
// src/gui/command/TargetPanel.cpp L192-218（SaveData）
std::string solverName = mSolverComboBox->GetValue().WX_TO_STD_STRING;
std::string solverMode = mSolverModeComboBox->GetValue().WX_TO_STD_STRING;
std::string exitMode   = mExitModeComboBox->GetValue().WX_TO_STD_STRING;

theCommand->SetStringParameter(theCommand->GetParameterID("Targeter"),
                               solverName);
theCommand->SetStringParameter(theCommand->GetParameterID("SolveMode"),
      solverMode);
theCommand->SetStringParameter(theCommand->GetParameterID("ExitMode"),
      exitMode);

if (mProgressWindowCheckBox->IsChecked())
   theCommand->SetBooleanParameter("ShowProgressWindow", true);
else
   theCommand->SetBooleanParameter("ShowProgressWindow", false);
```
`LoadData()`（L160-186）用相同的参数名 `GetStringParameter("Targeter")` 等反向填充控件。`OnApplyButtonPress`（L237-245）是命令面板触发命令动作（`TakeAction`）的范例：先检查所有 Vary 面板已关闭，再 `theCommand->TakeAction("ApplyCorrections")` 让命令把校正量写回变量。

#### OptimizePanel（OptimizePanel.hpp / OptimizePanel.cpp）

- **职责**：Optimize 命令面板；与 TargetPanel 结构几乎完全相同（同样的求解器/模式/退出模式/进度窗口/Apply 按钮，hpp L48-52）。
- **关键类/函数**：`Create()`（cpp L82）、`LoadData()`（L167）、`SaveData()`（L198）、`OnApplyButtonPress`（L242，同样执行 `TakeAction("ApplyCorrections")`）。设计上 Optimize 与 Target 是同一"求解循环"命令的两种脚本形式，故面板复用同一布局。

#### ManeuverPanel（ManeuverPanel.hpp / ManeuverPanel.cpp）

- **职责**：Maneuver 命令面板：选择 Burn（推力器机动）与受控航天器，可选反向机动（backprop）。
- **关键类/函数**：控件 `burnCB`/`satCB`/`backpropCheckBox`（hpp L50-52）；事件 `OnBurnComboBoxChange`（cpp L94）、`OnSatComboBoxChange`（L102）、`OnBackpropCheckBoxChange`（L111）；`Create()`（L128）、`LoadData()`（L200）、`SaveData()`（L272）。SaveData 把 Burn 名与 Spacecraft 名写入命令的 `Burn`/`Spacecraft` 引用参数，勾选 backprop 时追加反向传播标记。

#### ReportPanel（ReportPanel.hpp / ReportPanel.cpp）

- **职责**：Report 命令面板：选择 ReportFile 订阅器与要写入报告文件的参数列表。
- **关键类/函数**：
  - 控件：`mReportFileComboBox`、`mSelectedListBox`（已选参数）、`mViewButton`（hpp L55-57）。
  - `Create()`（cpp L120）、`LoadData()`（L181）、`SaveData()`（L241）、`OnButtonClick`（L324）、`OnComboBoxChange`（L363）。
  - 双向同步要点：LoadData 用 `theCommand->GetRefObjectNameArray(Gmat::PARAMETER)` 读出参数名数组填入列表；SaveData 用 `AddParameter`/`RemoveParameter` 系列 API 把列表写回 Report 命令，同时把 `AddReport`/`RemoveReport` 作用到 ReportFile 订阅器——这是命令面板跨对象（命令 + 订阅器）同步的代表。

#### AchievePanel（AchievePanel.hpp / AchievePanel.cpp）

- **职责**：Target 循环内 Achieve 命令面板：设置目标参数名、目标值与容差，绑定求解器。
- **关键类/函数**：`mAchieveCommand`（Achieve*，hpp L49）、文本域 `mGoalNameTextCtrl/mGoalValueTextCtrl/mToleranceTextCtrl` 与 `mSolverComboBox`；`Create()`（cpp L100）、`LoadData()`（L168）、`SaveData()`（L226）、`OnSolverSelection`（L346）。容差以 `wxString` 暂存（hpp L54 注释掉的 `Real mTolerance` 说明容差从"数值"改成了"字符串校验"路线），SaveData 里用 GmatPanel 的 `CheckReal` 校验后再 `SetRealParameter("Tolerance", ...)`。

#### VaryPanel（VaryPanel.hpp / VaryPanel.cpp）

- **职责**：Target/Optimize 循环内 Vary 命令面板：选择变量、初值、扰动量、最大步长、上下限与加减性缩放因子。
- **关键类/函数**：
  - 7 个文本域：`mVarNameTextCtrl/mInitialTextCtrl/mPertTextCtrl/mMaxStepTextCtrl/mLowerValueTextCtrl/mUpperValueTextCtrl/mAdditiveTextCtrl/mMultiplicativeTextCtrl`（hpp L55-62）。
  - `Create()`（cpp L109）、`LoadData()`（L233）、`SaveData()`（L320）、`SetControlEnabling(GmatBase*)`（L642，按求解器类型启用/禁用上下限与步长控件）、`OnSolverSelection`（L604）。
  - 构造参数 `inOptimize`（hpp L44）区分 Target-Vary 与 Optimize-Vary 两种语境；SaveData 通过 `mVaryCommand->SetStringParameter("Variable", ...)` 与 `SetRealParameter`（InitialValue/Perturbation/MaxStep/Lower/Upper/AdditiveScaleFactor/MultiplicativeScaleFactor）写回。

#### NonlinearConstraintPanel（NonlinearConstraintPanel.hpp / NonlinearConstraintPanel.cpp）

- **职责**：Target 循环内 NonlinearConstraint 命令面板：左/右表达式、比较算子（<=、==、>=）与容差。
- **关键类/函数**：`mLHSTextCtrl/mRHSTextCtrl/mTolTextCtrl`、`mComparisonComboBox`、`mSolverComboBox`（hpp L43-51）；`Create()`（cpp L86）、`LoadData()`（L181）、`SaveData()`（L233）。SaveData 把表达式字符串经 `mNonlinearConstraintCommand->SetStringParameter("Expression")` 写入并触发其内部解析。

#### MinimizePanel（MinimizePanel.hpp / MinimizePanel.cpp）

- **职责**：Optimize 循环内 Minimize 命令面板：选择要最小化的参数与绑定求解器。
- **关键类/函数**：`mVariableTextCtrl/mChooseButton/mSolverComboBox`（hpp L56-60）；`Create()`（cpp L90）、`LoadData()`（L136）、`SaveData()`（L175）、`ShowGoalSetup()`（L231，弹目标选择对话框）。SaveData 用 `mMinimizeCommand->SetStringParameter("Objective")` 写入目标参数全名（含对象限定）。

#### AssignmentPanel（AssignmentPanel.hpp / AssignmentPanel.cpp）

- **职责**：Assignment 命令面板：编辑 `lhs = rhs` 赋值语句的两侧文本。
- **关键类/函数**：`mLhsTextCtrl/mRhsTextCtrl`（hpp L50-51）；`Create()`（cpp L86）、`LoadData()`（L133）、`SaveData()`（L159）、`OnCancel`（L386，覆盖基类：取消时把暂存的 lhs/rhs 还原）。SaveData 用 `theCommand->SetStringParameter("LHS"/"RHS")` 写回；`mIsTextModified` 驱动 Apply 按钮。

#### CallFunctionPanel（CallFunctionPanel.hpp / CallFunctionPanel.cpp）

- **职责**：CallGmatFunction 命令面板：选择函数、编辑输入/输出参数列表。
- **关键类/函数**：`theFunctionComboBox/theInputTextCtrl/theOutputTextCtrl`（hpp L58-61）；`PrepareObjectNameChange()`（cpp L97）与 `ObjectNameChanged()`（L117，函数名/参数重命名联动）；`Create()`（L146）、`LoadData()`（L229）、`SaveData()`（L324）。SaveData 把输入/输出参数串按逗号解析后经 `theCommand->SetStringArrayParameter("Input"/"Output")` 写回。

#### BeginFiniteBurnPanel / EndFiniteBurnPanel（各 hpp+cpp）

- **职责**：BeginFiniteBurn / EndFiniteBurn 命令面板：选择有限推力 Burn 与受控航天器（两个面板控件与逻辑几乎对称）。
- **关键类/函数**：`mFiniteBurnComboBox`、`mSatTextCtrl`（hpp L50-51），工具函数 `ToWxArrayString`/`ToWxString`（L53-54，StringArray↔wxArrayString 转换）；BeginFiniteBurnPanel：`Create()`（cpp L150）、`LoadData()`（L227）、`SaveData()`（L260）；EndFiniteBurnPanel：`Create()`（L150）、`LoadData()`（L228）、`SaveData()`（L261）。SaveData 用 `SetStringParameter("Thruster")`（有限推力）与 `SetStringParameter("Spacecraft")` 写回。

#### FindEventsPanel（FindEventsPanel.hpp / FindEventsPanel.cpp）

- **职责**：FindEvents 命令面板：选择事件定位器（locator）与是否追加结果。
- **关键类/函数**：`locatorCB`、`appendCheckBox`（hpp L49-50）；`OnLocatorComboBoxChange`（cpp L93）、`OnAppendCheckBoxChange`（L102）、`Create()`（L119）、`LoadData()`（L172）、`SaveData()`（L221）。SaveData 用 `SetStringParameter("EventLocator")` 与 `SetBooleanParameter("Append")` 写回。

#### ManageObjectPanel（ManageObjectPanel.hpp / ManageObjectPanel.cpp）

- **职责**：Save 类命令（保存对象状态）面板：用复选列表框勾选要保存的对象。
- **关键类/函数**：`mObjectCheckListBox`（hpp L47）；`Create()`（cpp L99）、`LoadData()`（L172）、`SaveData()`（L202）、`OnCheckListBoxChange`（L261）。SaveData 收集勾选项经 `theCommand->SetObjectList` 系列写回。

#### ScriptEventPanel（ScriptEventPanel.hpp / ScriptEventPanel.cpp）

- **职责**：ScriptEvent（BeginScript/EndScript）面板：以文本编辑脚本事件内容与注释，保存时整体替换命令序列。
- **关键类/函数**：
  - 双窗口布局：`theCommentsWin`/`theScriptsWin`（wxSashLayoutWindow，hpp L74-75）与 `mCommentTextCtrl`；可选 `ScriptEditor`（`__USE_STC_EDITOR__` 编译开关，hpp L43-45）。
  - 构造签名与众不同：`ScriptEventPanel(wxWindow*, MissionTreeItemData*)`（hpp L51）——直接拿任务树节点数据，而非 GmatCommand。
  - `Create()`（cpp L143）、`LoadData()`（L315）、`SaveData()`（L387）、`SaveComments()`（L808）、`ReplaceScriptEvent()`（L846，用新命令替换旧命令的前后指针以保持命令链）、`ShowCommand()`（L1104，调试用）。
  - 保存语义：脚本文本修改后，`ReplaceScriptEvent()` 把原 ScriptEvent 命令从命令链摘除并插入新命令——这是唯一会"替换命令对象"的面板。

#### TogglePanel（TogglePanel.hpp / TogglePanel.cpp）

- **职责**：Toggle 命令面板：选择订阅器列表并开/关（On/Off）。
- **关键类/函数**：`mSubsCheckListBox`、`mOnRadioButton/mOffRadioButton`（hpp L55-57）；构造参数 `forXyPlotOnly`/`showToggleState`（hpp L42-43，供 XY 绘图中只列 XYPlot 订阅器）；`TakeAction(wxString)`（cpp L107）；`Create()`（L137）、`LoadData()`（L205）、`SaveData()`（L282）。SaveData 收集勾选订阅器名并设置开关状态写回命令。

### 2.2 solver 目录（12 个文件）

本目录 6 个面板全部围绕 `Solver`（基类见 [第8章](CH08-base-subsystems.md) 的 solver）配置：两个"专用"面板（DCSetupPanel、SQPSetupPanel）、一个"通用反射"面板（SolverSetupPanel），以及三个辅助面板（SolverCreatePanel、SolverGoalsPanel、SolverVariablesPanel）。

#### SolverSetupPanel（SolverSetupPanel.hpp / SolverSetupPanel.cpp）

- **职责**：插件求解器（如 VF13ad、旧 SteepestDescent）没有专属面板时的**通用参数面板**：遍历 Solver 的全部可写参数，自动生成"标签 + 控件"网格（hpp 注释 L37-48 明确此定位）。
- **关键类/函数**：
  - 数据成员：`propertyDescriptors`（wxStaticText* 向量）、`propertyControls`（wxControl* 向量）、`controlMap`（参数名→控件序号映射，hpp L79-83）。
  - `Setup()`（cpp L193）：遍历 `theSolver->GetParameterCount()`，跳过只读参数（`IsParameterReadOnly`），每参数建标签 + 控件并登记 `controlMap`。
  - `BuildControl()`（cpp L245）：按参数类型分派——BOOLEAN 建只读 wxComboBox（"true"/"false"），STRING/其余建 wxTextCtrl。

```cpp
// src/gui/solver/SolverSetupPanel.cpp L245-271（按参数类型建控件）
wxControl *SolverSetupPanel::BuildControl(wxWindow *parent, Integer index)
{
   wxControl *control = NULL;

   Gmat::ParameterType type = theSolver->GetParameterType(index);

   switch (type)
   {
      case Gmat::BOOLEAN_TYPE:
         {
            wxComboBox *cbControl = new wxComboBox(parent, ID_COMBOBOX, "true",
                  wxDefaultPosition, wxDefaultSize, 2, TF_SCHEMES,
                  wxCB_READONLY);

            control = cbControl;
         }
         break;

      case Gmat::STRING_TYPE:
      default:
         control = new wxTextCtrl(parent, ID_TEXTCTRL,
                     wxT(""), wxDefaultPosition, wxSize(100,-1));
         break;
   }

   return control;
}
```
  - `LoadControl(const std::string&)`（L282）与 `SaveControl()`（L337）：再按类型回读/写回（`GetBooleanParameter`/`GetRealParameter`/`GetIntegerParameter`/`GetStringParameter`）。这套"反射式"面板是本目录的核心设计：新求解器只要实现 GmatBase 参数表，GUI 零修改即可配置。
- **双向同步**：`LoadData()`（L117）遍历 controlMap 调 `LoadControl`；`SaveData()`（L156）遍历调 `SaveControl`，失败则 `canClose=false`。

#### SQPSetupPanel（SQPSetupPanel.hpp / SQPSetupPanel.cpp）

- **职责**：SQP 求解器（Sequential Quadratic Programming，优化器）专用面板：**容差/最大迭代参数网格** + 报告文件/样式 + 进度窗口。
- **关键类/函数**：
  - 7 个文本域（hpp L64-78）：`tolFunTextCtrl`（TolFun）、`tolConTextCtrl`（TolCon）、`tolXTextCtrl`（TolX）、`maxFunEvalsTextCtrl`（MaxFunEvals）、`maxIterTextCtrl`（MaximumIterations）、`diffMinChangeTextCtrl`/`diffMaxChangeTextCtrl`（DiffMinChange/DiffMaxChange）；另加 `showProgressCheckBox`、`reportfileTextCtrl`、`styleComboBox`（ReportStyle：Normal/Concise/Verbose/Debug，cpp Setup L305-309）。
  - `Create()`（cpp L102）→ `Setup()`（L303，用 wxFlexGridSizer 双列网格排布）；`LoadData()`（L110）；`SaveData()`（L194）；事件 `OnTextUpdate/OnComboBoxChange/OnCheckboxChange/OnBrowse`（L403-440）。
- **重点展开（容差/最大迭代网格）**：LoadData 从求解器逐参数取出并填框；注意 MaximumIterations 是整型参数，走 `GetIntegerParameter(GetParameterID(...))`（L156），其余为字符串参数：

```cpp
// src/gui/solver/SQPSetupPanel.cpp L144-157（LoadData：容差与迭代上限）
valueStr = theSolver->GetStringParameter("TolFun");
tolFunTextCtrl->SetValue(wxString(valueStr.c_str()));

valueStr = theSolver->GetStringParameter("TolCon");
tolConTextCtrl->SetValue(wxString(valueStr.c_str()));

valueStr = theSolver->GetStringParameter("TolX");
tolXTextCtrl->SetValue(wxString(valueStr.c_str()));

valueStr = theSolver->GetStringParameter("MaxFunEvals");
maxFunEvalsTextCtrl->SetValue(wxString(valueStr.c_str()));

valueStr = wxString::Format("%d",theSolver->GetIntegerParameter(theSolver->GetParameterID("MaximumIterations")));
maxIterTextCtrl->SetValue(wxString(valueStr.c_str()));
```
SaveData（L194-234）反向校验：TolFun/TolCon/TolX/DiffMinChange/DiffMaxChange 用 `CheckReal`，MaximumIterations/MaxFunEvals 用 `CheckInteger`（均要求 > 0），全部通过后 `SetStringParameter`/`SetIntegerParameter` 写回（L248-254）——这是"容差/迭代参数网格"的标准双向往返：字符串界面 ↔ 数值校验 ↔ 引擎参数。

#### DCSetupPanel（DCSetupPanel.hpp / DCSetupPanel.cpp）

- **职责**：DifferentialCorrector（微分校正器）专用面板：最大迭代、报告文件/样式、算法与差分方法、进度窗口。
- **关键类/函数**：`theDC`（DifferentialCorrector*，hpp L51）；控件 `maxTextCtrl/reportfileTextCtrl/showProgressCheckBox/styleComboBox/algorithmComboBox/derivativeMethodComboBox/browseButton`（hpp L62-72）；`Create()`（cpp L93）、`LoadData()`（L101）、`SaveData()`（L138）、`Setup()`（L202 与 L299 两段布局）、`OnBrowse`（L393，wxFileDialog 选报告文件）。SaveData 用 `SetIntegerParameter("MaximumIterations")`、`SetStringParameter("ReportFile"/"ReportStyle"/"Algorithm"/"DerivativeMethod")` 写回。

#### SolverCreatePanel（SolverCreatePanel.hpp / SolverCreatePanel.cpp）

- **职责**：新建求解器向导面板——注意它直接 `public wxPanel`（hpp L45），**不继承 GmatPanel**，是本章唯一非 GmatPanel 的面板。
- **关键类/函数**：`theGuiInterpreter`（hpp L53）；`Initialize()`（cpp L69）、`Setup()`（L74）、`GetData()`（L159）、`SetData()`（L164）、`OnTextUpdate`（L169）、`OnButton`（L174）。功能为输入求解器名字，经 `GuiInterpreter` 创建求解器对象。

#### SolverGoalsPanel（SolverGoalsPanel.hpp / SolverGoalsPanel.cpp）

- **职责**：旧式求解器"目标（Goal）"编辑面板：网格编辑目标参数/值/容差，绑定求解器（Target 循环的 Achieve 目标的集中编辑视图）。
- **关键类/函数**：`goalsGrid`（wxGrid，hpp L47）+ 下方 `descTextCtrl/varTextCtrl/valueTextCtrl/tolTextCtrl` 与 `solverComboBox/editButton/updateButton`；`Create()`（cpp L69）、`LoadData()`（L75）、`SaveData()`（L84）、`Setup()`（L99）、`OnCellValueChanged`（L228）、`OnSolverSelection`（L198）、`OnButton`（L203）。

#### SolverVariablesPanel（SolverVariablesPanel.hpp / SolverVariablesPanel.cpp）

- **职责**：旧式求解器"变量（Vary）"编辑面板：网格编辑变量/扰动/最大步长/上下限（Vary 命令的集中编辑视图）。
- **关键类/函数**：`varsGrid` + `descTextCtrl/varTextCtrl/pertTextCtrl/maxTextCtrl/lowerTextCtrl/upperTextCtrl`（hpp L47-62）；`Create()`（cpp L69）、`LoadData()`（L75）、`SaveData()`（L82）、`Setup()`（L96）、`OnCellValueChanged`（L261）。

### 2.3 subscriber 目录（57 个文件）

订阅器基类（Subscriber/XyPlot/ReportFile/OrbitView/GroundTrackPlot/EphemerisFile/DynamicDataDisplay 等）见 [第8章](CH08-base-subsystems.md)。本目录分六组：**配置面板**（引擎参数 ↔ 控件）、**3D 画布**（OpenGL 绘制）、**时序图画布**（TsPlot 2D 绘制库）、**MDI 子窗口框架**（订阅器运行时窗口）、**地面轨迹窗口**、**对话框**。

#### （a）配置面板（8 个文件对 + 1 个单文件）

##### SubscriberSetupPanel（SubscriberSetupPanel.hpp / SubscriberSetupPanel.cpp）

- **职责**：插件订阅器无专属面板时的**通用参数面板**，与 SolverSetupPanel 同构（hpp 注释 L37-48）：遍历 `theSubscriber->GetParameterCount()` 自动生成控件。
- **关键类/函数**：`propertyDescriptors/propertyControls/controlMap`（hpp L79-83）；`Setup()`（cpp L194）、`LoadControl()`（L283）、`SaveControl()`（L339）、`BuildControl()`（cpp 内联于 Setup，L210 附近按类型分派）；`LoadData()`（L118）、`SaveData()`（L157）。

##### XyPlotSetupPanel（XyPlotSetupPanel.hpp / XyPlotSetupPanel.cpp）

- **职责**：XYPlot 订阅器配置面板：X 参数（1 个）、Y 参数（多个）、SolverIterations、显示/网格开关。
- **关键类/函数**：`mXyPlot`（XyPlot*，hpp L50）；`mSolverIterComboBox/mXSelectedListBox/mYSelectedListBox/mViewXButton/mViewYButton/showPlotCheckBox/showGridCheckBox`（hpp L64-70）；`PrepareObjectNameChange`（cpp L134）/`ObjectNameChanged`（L154，参数重命名联动）；`Create()`（L279）、`LoadData()`（L389）、`SaveData()`（L467）。
- **双向同步要点**：X 参数经 `GetStringParameter(XyPlot::XVARIABLE)` 单值读入（L409），Y 参数经 `GetStringArrayParameter(XyPlot::YVARIABLES)` 数组读入（L424）；SaveData 反向用 `SetStringParameter("XVariable")`/`SetStringArrayParameter("YVariables")` 写回。SolverIterations 组合框（Current/All）直接映射订阅器参数：

```cpp
// src/gui/subscriber/XyPlotSetupPanel.cpp L399-405（LoadData 前段）
mObject = mXyPlot;

showPlotCheckBox->SetValue(mXyPlot->IsActive());
showGridCheckBox->SetValue(mXyPlot->GetBooleanParameter(XyPlot::SHOW_GRID));
mSolverIterComboBox->
   SetValue(mXyPlot->GetStringParameter(Subscriber::SOLVER_ITERATIONS).c_str());
```

##### ReportFileSetupPanel（ReportFileSetupPanel.hpp / ReportFileSetupPanel.cpp）

- **职责**：ReportFile 订阅器配置面板：文件名、写开关、表头/左对齐/零填充/定宽/追加、分隔符、列宽/精度与参数列表。
- **关键类/函数**：`reportFile`（ReportFile*，hpp L51）；控件（hpp L60-73）：`delimiterComboBox/colWidthTextCtrl/precisionTextCtrl/mFileTextCtrl/writeCheckBox/showHeaderCheckBox/leftJustifyCheckBox/zeroFillCheckBox/fixedWidthCheckBox/appendFileCheckBox/mSolverIterComboBox/mSelectedListBox/mBrowseButton/mViewButton`；`Create()`（cpp L205）、`LoadData()`（L373）、`SaveData()`（L506）、`OnCheckBoxChange`（L181）、`OnButtonClick`（L681）、`OnComboBoxChange`（L742）。
- **双向同步要点**：布尔参数经 `GetBooleanParameter(id)` 直读（L404-432）；On/Off 型参数（LeftJustify/ZeroFill）经 `GetOnOffParameter(id)` 比较 "On"（L410-420）；分隔符是单字符参数，按字符映射到组合框文本（L434-442）：

```cpp
// src/gui/subscriber/ReportFileSetupPanel.cpp L434-442（分隔符字符→组合框）
id = reportFile->GetParameterID("Delimiter");
wxString aDelimiter;
aDelimiter = reportFile->GetStringParameter(id)[0];
if (aDelimiter == " ")
   delimiterComboBox->SetValue("Space");
else if (aDelimiter == "\t")
   delimiterComboBox->SetValue("Tab");
else if (aDelimiter == ",")
   delimiterComboBox->SetValue("Comma");
```

##### OrbitViewPanel（OrbitViewPanel.hpp / OrbitViewPanel.cpp）

- **职责**：OrbitView 订阅器配置面板——本章最复杂的订阅器面板：对象（航天器/天体）增删、坐标系、视点定义（参考对象/向量/方向）、FOV、数据采集频率、绘制开关（线框/赤道面/XY 面/轴/网格/太阳线/星等）。
- **关键类/函数**：
  - 控件海（hpp L102-159）：`mShowPlotCheckBox` 等 14 个复选框、`mDataCollectFreqTextCtrl` 等 19 个文本域、`mSpacecraftListBox/mCelesPointListBox/mSelectedScListBox/mSelectedObjListBox` 4 个列表 + add/remove/clear 按钮、`mSolverIterComboBox/mCoordSysComboBox/mViewPointRefComboBox/mViewPointVectorComboBox/mViewDirectionComboBox/mViewUpCsComboBox/mViewUpAxisComboBox` 7 个组合框。
  - `InitializeData()`（cpp L197）、`Create()`（L223，超长布局）、`LoadData()`（L768）、`SaveData()`（L1101）、`ValidateFovValues()`（L2227）。
  - 对象操作事件：`OnAddSpacePoint`（L1615）、`OnRemoveSpacePoint`（L1715）、`OnClearSpacePoint`（L1782）、`OnSelectAvailObject/OnSelectSpacecraft/OnSelectOtherObject`（L1820-1842）；绘制开关 `OnCheckBoxChange`（L1852）；`ShowSpacePointOption`（L2156，按对象类型显示/隐藏相关选项）。
- **双向同步要点**：航天器列表经 `GetStringArrayParameter("Spacecraft")` 与"排除列表"（`mExcludedScList`）两套逻辑维持；视点向量（ViewPointRef/ViewPointVector/ViewDirection）各 3 分量文本域与 OrbitView 的 Rvector3 参数互转；FOV 数值由 `ValidateFovValues` 保证在 `mFovMin/mFovMax` 范围内。`ObjectNameChanged`（L166）保证资源树重命名时对象列表同步。

##### GroundTrackPlotPanel（GroundTrackPlotPanel.hpp / GroundTrackPlotPanel.cpp）

- **职责**：GroundTrackPlot 订阅器配置面板：中心天体、纹理图、数据采集/更新频率、最大点数、对象勾选与轨道颜色。
- **关键类/函数**：`mGroundTrackPlot`（hpp L57）；`mCentralBodyComboBox/mTextureMapTextCtrl/mObjectCheckListBox/mSolverIterComboBox` 与 4 个频率文本域（hpp L81-94）；`InitializeData()`（cpp L185）、`Create()`（L205）、`LoadData()`（L442）、`SaveData()`（L544）、`OnBrowseButton`（L713）、`OnCheckListBoxChange`（L755）；颜色支持在 `__USE_COLOR_FROM_SUBSCRIBER__` 编译开关下启用（`OnColorPickerChange` L779、`SaveObjectColors` L949）。

##### EphemerisFilePanel（EphemerisFilePanel.hpp / EphemerisFilePanel.cpp）

- **职责**：EphemerisFile 订阅器通用配置面板：文件格式（SPK/CCSDS/STK）、航天器、坐标系、插值器/阶数、步长、历元与坐标系统选项（按格式动态显隐控件）。
- **关键类/函数**：`clonedObj`（GmatBase* 克隆，hpp L51——面板对对象做克隆编辑，SaveData 才提交）；控件 `spacecraftComboBox/writeEphemerisCheckBox/fileFormatComboBox/fileNameTextCtrl/interpolatorComboBox/interpolationOrderTextCtrl/outputFormatComboBox/epochFormatComboBox/initialEpochComboBox/finalEpochComboBox/eventBoundariesCheckBox` 与动态组 `allCoordSystemComboBox/code500ComboBox/onlyMj2000EqComboBox/allStepSizeComboBox/numericStepSizeTextCtrl/distanceUnitComboBox`（hpp L76-107）；`Create()`（cpp L117）、`LoadData()`（L357）、`SaveData()`（L417）、`LoadControl`（L660）/`SaveControl`（L791，通用反射）、`ShowCoordSystems`（L1229）/`ShowCode500Items`（L1273）/`ShowInterpolatorAndStepSize`（L1301，按文件格式显隐）；`managedComboBoxMap`（hpp L122）交 GuiItemManager 统一管理可选对象。

##### DynamicDataDisplaySetupPanel（DynamicDataDisplaySetupPanel.hpp / DynamicDataDisplaySetupPanel.cpp）

- **职责**：DynamicDataDisplay（动态数据显示）订阅器配置面板：行/列数、警告/临界色、每格参数设置。
- **关键类/函数**：`mDisplay`（DynamicDataDisplay*，hpp L46）、`displayDataStruct`（`std::vector<std::vector<DDD>>`，L47，DDD 为参数设置结构）；`mDisplayRowTextCtrl/mDisplayColTextCtrl/mWarnColorPickerCtrl/mCritColorPickerCtrl/mDisplayDataGrid/mUpdateButton`（hpp L56-63）；`Create()`（cpp L75）、`LoadData()`（L177）、`SaveData()`（L259）、`OnUpdate`（L291，重建网格）、`OnGridCellDClick`（L378，弹出单格设置对话框）、`SetParamDefaultValues`（L469）。

##### DynamicDataSettingsDialog（DynamicDataSettingsDialog.hpp / DynamicDataSettingsDialog.cpp）

- **职责**：单格参数设置对话框（DynamicDataDisplay 面板的格子编辑器）：参数名、警告/临界上下界、文字/背景色。
- **关键类/函数**：`public GmatDialog`（hpp L41）；`GetParamSettings()` 返回 `DDD`、`WasDataSaved()`（hpp L46-47）；`Create()`（cpp L95）、`LoadData()`（L175）、`SaveData()`（L204）、`ResetData()`（L261）、`OnSelect`（L275，选择参数）。

#### （b）3D 画布（ViewCanvas 家族）

##### ViewCanvas（ViewCanvas.hpp / ViewCanvas.cpp）

- **职责**：所有 OpenGL 画布的抽象基类：GL 上下文、纹理、环形数据缓冲、坐标系转换、光照、绘制流程骨架。
- **关键类/函数**：
  - 继承：`public wxGLCanvas`（hpp L42）。纯虚绘制接口（hpp L106-115、L357-360、L383、L392-398、L435-436）：`ClearPlot/RedrawPlot/ShowDefaultView/DrawWireFrame/OnDrawGrid/DrawInOtherCoordSystem/ViewAnimation/OnPaint/OnSize/OnMouse/OnKeyDown/SetupWorld/DrawFrame/DrawPlot/DrawObjectOrbit/DrawObjectTexture/DrawObject/DrawOrbitLines/ConvertObjectData/ConvertObject` 等，由 OrbitViewCanvas/GroundTrackCanvas 实现。
  - 数据缓冲：`mTime/mIsDrawing/mObjectGciPos/mObjectViewPos/mObjectViewVel/mObjectQuat/mRotMatViewToInternal/mRotMatViewToEcliptic`（hpp L316-341）与环形缓冲索引算法 `ComputeRingBufferIndex`（cpp L1507）/`ComputeActualIndex`（L1573）。
  - 初始化：`GmatGLCanvasAttribs[4] = { WX_GL_DOUBLEBUFFER, WX_GL_DEPTH_SIZE, 16, 0 }`（cpp L84）、`SetGLContext`（L321）、`InitializePlot`（L380）、`InitOpenGL`（L436）。
  - 数据更新入口：`UpdatePlot(...)`（cpp L903）——引擎每个数据步调用一次，负责把位置/速度/颜色灌入缓冲；`UpdateSolverData`（L2349）/`UpdateSpacecraftData`（L2407）/`UpdateOtherData`（L2559）。
  - 模型/纹理：`LoadBodyTextures`（L1633）、`LoadSpacecraftModels`（L2092）、`LoadOtherObjectModels`（L2225）、`BindTexture`、`AddAlphaToTexture`（L2013）。
  - 求解器数据绘制：`DrawSolverData`（L3178）、`DrawOrbit`（L3134）、`DrawStatus`（L3245）。
- **重点展开**：ViewCanvas 采用"模板方法 + 环形缓冲"架构——继承者实现"画什么"（各 DrawXxx 纯虚），基类实现"何时画、画在哪"（更新频率 `mUpdateFrequency`、每帧重绘点数 `mNumPointsToRedraw`、MAX_DATA 环形缓冲）。求解器迭代数据显示时（`mIsSolving`），`mSolverAllPosX/Y/Z`（hpp L346-348）按迭代次数着色，即 OrbitView 中"多次迭代轨迹叠加"效果的来源。

##### OrbitViewCanvas（OrbitViewCanvas.hpp / OrbitViewCanvas.cpp）

- **职责**：OrbitView 的 3D 画布：星空、天体/航天器模型、轨道线、坐标系平面、太阳线、视点定义。
- **关键类/函数**：`public ViewCanvas`（hpp L45）；`mStars`（GLStars*，L132）、`mCamera`（L138）、`mLight`（L141）；视点定义指针 `pViewPointRefObj/pViewPointVectorObj/pViewDirectionObj` 与向量（L191-203）；`ClearPlot`（cpp L342）、`RedrawPlot`（L366）、`ShowDefaultView`（L396）、`GotoObject`（L527）、`SetGl3dViewOption`（L751）；绘制链 `DrawPlot`（L1821）→ `DrawObjectOrbit`（L1928）→ `DrawOrbitLines`（L2221）→ `DrawSpacecraft3dModel`（L2628）/`DrawCelestialBody3dModel`（L2755）→ `DrawStars`（L2846）；坐标系转换 `ConvertObjectData`（L3018）/`ConvertObject`（L3095）。

##### GroundTrackCanvas（GroundTrackCanvas.hpp / GroundTrackCanvas.cpp）

- **职责**：GroundTrackPlot 的 2D OpenGL 画布：中心天体纹理底图 + 经纬网格 + 地面轨迹线 + 星下点圆。
- **关键类/函数**：`public ViewCanvas`（hpp L45）；`mCamera/mLight/mCentralBodyName/mCentralBodyTextureFile`（hpp L99-112）；`SetGl2dDrawingOption`（cpp L272）、`ClearPlot`（L296）、`RedrawPlot`（L320）；绘制：`DrawPlot`（L910）、`DrawGroundTrackLines`（L1399，把两时刻位置经坐标转换画到球面）、`DrawGridLines`（L1510）、`DrawCentralBodyTexture`（L1563）、`DrawCircleAt`（L1646，星下点足迹）、`DrawSpacecraft`（L1769）、`DrawGroundStation`（L1832）、`RotateBodyUsingAttitude`（L1932，让纹理球按天体姿态旋转）。

#### （c）时序图画布（TsPlot 家族）

##### TsPlotCanvas（TsPlotCanvas.hpp / TsPlotCanvas.cpp）

- **职责**：通用 2D 时序图绘制控件（独立于 OpenGL 的 wxDC 绘制库）：坐标轴、网格、图例、缩放、曲线管理。`public wxWindow`（hpp L28）。
- **关键类/函数**：曲线容器 `std::vector<TsPlotCurve*> data`（hpp L117）；纯虚绘制接口 `DrawAxes/DrawLabels/PlotData/Rescale`（hpp L196-199）由 TsPlotXYCanvas 等实现；`OnPaint`（cpp L171）、`DrawGrid`（L752）、`DrawLegend`（L779）、`AddData`（L917）、`Zoom`（L1388）、`UnZoom`（L1427）、`PenUp/PenDown`（L1438/L1458，断笔续笔）、`Darken/Lighten`（L1477/L1498）、`MarkPoint/MarkBreak`（L1519/L1541）、`SetAxisLimit`（L1682）、`Rescale`（L1779）。标尺类型 `MarkerType` 枚举定义在 TsPlotDefs.hpp（L48-65：x/circle/plus/star/square/diamond 等）。

##### TsPlotXYCanvas（TsPlotXYCanvas.hpp / TsPlotXYCanvas.cpp）

- **职责**：XY 时序图画布：实现 TsPlotCanvas 的 4 个纯虚绘制方法。
- **关键类/函数**：`public TsPlotCanvas`（hpp L21）；`DrawAxes`（cpp L68）、`DrawLabels`（L234）、`PlotData`（L308，逐曲线画线/标记/误差棒）、`Rescale`（L569）。

##### TsPlotCurve（TsPlotCurve.hpp / TsPlotCurve.cpp）

- **职责**：单条时序曲线的数据模型：横/纵坐标、误差棒、断笔点、颜色/标记变化点。
- **关键类/函数**：数据 `abscissa/ordinate/highError/lowError`、`penUpIndex/colorIndex/breakIndex/markerIndex/highlightIndex`（hpp L98-120）；`AddData`（cpp L72）、`Clear`（L267）、`PenUp/PenDown`（L334/L357）、`SetColour`（L453）、`DarkenColour/LightenColour`（L499/L516）、`AddBreak/BreakAndDiscard`（L588/L609）。`friend class TsPlotCanvas/TsPlotXYCanvas/...`（hpp L131-134）允许画布直接访问内部向量。

##### TsPlotOptionsDialog（TsPlotOptionsDialog.hpp / TsPlotOptionsDialog.cpp）

- **职责**：时序图外观选项对话框：标题、轴标签、线宽/线型、X/Y 最小值/最大值、刻度数、精度、对数刻度。
- **关键类/函数**：`public wxDialog`（hpp L28）；大量 getter/setter（hpp L41-84，如 `GetPlotTitle/SetXMin/GetXTickCount`）；`UpdateLabels`（cpp L265）；X/Y 上下限启用复选框事件 `OnSettableXMinimum` 等（L489-507）。

#### （d）MDI 子窗口框架

##### MdiGlPlotData（MdiGlPlotData.hpp / MdiGlPlotData.cpp）

- **职责**：OpenGL 绘图窗口的事件枚举与静态数据。
- **关键类/函数**：`GmatPlot::GlEventType`（hpp L44-63：`MDI_GL_QUIT=500` 起，`MDI_GL_ZOOM_IN/OUT`、`MDI_GL_VIEW_ANIMATION`、`MDI_GL_SHOW_OPTION_PANEL`、`MDI_GL_SHOW_WIRE_FRAME` 等——注释"不要改 500，更大数字会失效"）；typedef `wxStringColorMap/wxStringBoolMap`（L38-39）；`MdiGlPlot` 静态成员（cpp L31-33：`mdiChildren/numChildren/usePresetSize`）。

##### MdiTsPlotData（MdiTsPlotData.hpp / MdiTsPlotData.cpp）

- **职责**：XY 时序图窗口的事件枚举与静态数据（与 MdiGlPlotData 对称）。
- **关键类/函数**：`GmatPlot::TsEventType`（hpp L36-48：`MDI_TS_QUIT=600` 起，`MDI_TS_OPEN_PLOT_FILE/MDI_TS_CLEAR_PLOT/MDI_TS_DRAW_GRID` 等）；`MdiTsPlot` 静态成员（cpp L31-33）。

##### MdiChildViewFrame（MdiChildViewFrame.hpp / MdiChildViewFrame.cpp）

- **职责**：3D 可视化 MDI 子窗口基类：持有 ViewCanvas、转发订阅器配置与数据更新。
- **关键类/函数**：`public GmatMdiChildFrame`（hpp L49）；`mCanvas`（ViewCanvas*，L173）；大量 getter/setter 转发（hpp L60-96）；`SetGlObject`（cpp L751）、`SetGlCoordSystem`（L764）、`SetGl2dDrawingOption`（L778）、`SetGl3dDrawingOption`（L790）、`SetGl3dViewOption`（L805）、`UpdatePlot`（L849，转发给画布）、`InitializePlot`（L905）、`RefreshPlot`（L927）、`DeletePlot`（L946）、`SetEndOfRun`（L960）；菜单事件 `OnClearPlot/OnChangeTitle/OnShowDefaultView/OnQuit`（L548-605）；窗口事件 `OnActivate/OnPlotSize/OnMove/OnPlotClose/OnClose`（L614-728）。

##### MdiChild3DViewFrame（MdiChild3DViewFrame.hpp / MdiChild3DViewFrame.cpp）

- **职责**：3D 视图子窗口（3DView 订阅器）：在 MdiChildViewFrame 基础上定制 3D 绘制/视点选项。
- **关键类/函数**：`public MdiChildViewFrame`（hpp L45）；重写 `SetGl3dDrawingOption`（cpp L78）、`SetGl3dViewOption`（L98）。

##### MdiChildTrajFrame（MdiChildTrajFrame.hpp / MdiChildTrajFrame.cpp）

- **职责**：轨迹（OrbitView 旧式）子窗口：持 OpenGlOptionDialog，提供"选项"菜单。
- **关键类/函数**：`public MdiChildViewFrame`（hpp L48）；`mOptionDialog`（L64）；`GetOptionDialog`（L56）、`EnableAnimation`（cpp L102）、`OnShowOptionDialog`（L112）、`OnDrawWireFrame`（L143）。

##### MdiChildTsFrame（MdiChildTsFrame.hpp / MdiChildTsFrame.cpp）

- **职责**：XY 时序图 MDI 子窗口：封装 TsPlotCanvas，向订阅器提供曲线/数据操作 API。
- **关键类/函数**：`public GmatMdiChildFrame`（hpp L53）；`mXyPlot`（TsPlotCanvas*，L56）、`mLogTextCtrl`、`mViewOptionMenu`；曲线 API `AddPlotCurve`（cpp L328）、`DeletePlotCurve`（L411）、`AddDataPoints`（L446）、`PenUp/PenDown`（L486/L502）、`Darken/Lighten`（L521/L540）、`MarkPoint/MarkBreak`（L558/L576）、`ChangeColor/ChangeMarker`（L620/L640）、`SetLineWidth/SetLineStyle`（L660/L679）、`CurveSettings`（L755）、`RedrawCurve`（L808）；`ReadXyPlotFile`（L206，读 .xyplot 文件）；`MAX_NUM_CURVE=20`（hpp L145，GMT-2411 从 6 提到 20）。

##### MdiChildGroundTrackFrame（MdiChildGroundTrackFrame.hpp / MdiChildGroundTrackFrame.cpp）

- **职责**：地面轨迹图子窗口：转发 2D 绘制选项到 GroundTrackCanvas。
- **关键类/函数**：`public MdiChildViewFrame`（hpp L45）；`SetGl2dDrawingOption`（cpp L78）。

##### MdiChildDynamicDataFrame（MdiChildDynamicDataFrame.hpp / MdiChildDynamicDataFrame.cpp）

- **职责**：动态数据显示子窗口：wxGrid 表格实时刷新参数名与值，支持文字/背景色。
- **关键类/函数**：`public GmatMdiChildFrame`（hpp L53）；`dynamicDataGrid/gridSizer/isSizePreset`（hpp L83-91）；`SetTableSize`（cpp L134）、`UpdateDynamicData`（L179，按 DDD 结构刷新表格）、`DeleteDynamicDataGrid`（L205）、`SetDynamicDataCellTextColor`（L221）、`SetDynamicDataCellBackgroundColor`（L251）。

##### MdiTableViewFrame（MdiTableViewFrame.hpp / MdiTableViewFrame.cpp）

- **职责**：求解器收敛过程表格窗口：变量/约束/目标三张网格 + 收敛状态横幅，实现 ISolverListener 接口接收求解器事件。
- **关键类/函数**：`public GmatMdiChildFrame, ISolverListener`（hpp L49）；`ConvergenceType{ITERATING, CONVERGENCE, NO_CONVERGENCE}`（L52-55）；`variableGrid/constraintGrid/objectiveGrid/convergenceText`（L92-98）；监听回调 `ConstraintChanged`（cpp L467）、`Convergence`（L520）、`ObjectiveChanged`（L337）、`VariabledChanged`（L382/L427）、`SetConvergence`（L540）；`Create()`（L110）。

#### （e）地面轨迹窗口（2025 年新移植组件）

##### GroundTrackWindow（GroundTrackWindow.hpp / GroundTrackWindow.cpp）

- **职责**：地面轨迹绘图子窗口（自 Astrodynamics Workbench® 移植，hpp 注释 L26-29）：承载 GroundTrackArea，转发订阅器数据。
- **关键类/函数**：`public GmatMdiChildFrame`（hpp L47）；`theMap`（GroundTrackArea*，L93）、`theSS`（SolarSystem*，L96）；`AddData`（cpp L238，把经纬度数据交给地图）、`SetOption`（L258）、`SetColor`（L288）、`SetLineWidth`（L303）、`LabelData`（L317）、`UpdatePlot`（L329）、`ResetForNewRun`（L341）、`TakeAction`（L354）、`SetSolarSystem`（L365）。

##### GroundTrackArea（GroundTrackArea.hpp / GroundTrackArea.cpp）

- **职责**：地面轨迹的实际绘制面板（wxPanel）：纹理底图 + 经纬网格 + 轨迹曲线 + 站点标记（AWB 移植）。
- **关键类/函数**：`public wxPanel`（hpp L39）；内部结构 `MarkedPoint`（hpp L66-72：站名/纬度/经度/颜色）；`textureMap/bgImage/bgScaledMap/data/startColors/theSats/points`（hpp L75-127）；`AddData`（cpp L419）、`SetDataNames`（L469）、`Clear`（L487）、`OnPaint`（L503，用 wxDC 画底图与曲线）、`OnSize`（L705）、`SetSolarSystem`（L718）；`GroundTrackCurve` 存储轨迹（数据模型见下）。

##### GroundTrackCurve（GroundTrackCurve.hpp / GroundTrackCurve.cpp）

- **职责**：地面轨迹线段数据模型：x/y/t 数据、颜色变化点、断笔点（AWB 移植，hpp 注释 L26-29）。
- **关键类/函数**：`xData/yData/tData/colorChangeLocation/colors/penUp/label`（hpp L106-122）；`AddData`（cpp 内联于 hpp L45-46 声明，实现见 cpp）、`Clear`、`PenUp`（hpp L99-102，记录断笔位置）、`SetColor/GetColor`（hpp L85-97，颜色随点变化）。

#### （f）对话框

##### OpenGlOptionDialog（OpenGlOptionDialog.hpp / OpenGlOptionDialog.cpp）

- **职责**：3D 轨迹窗口的"视图选项"对话框：线框/XY 面/轴/太阳线开关、坐标系统、动画更新间隔/帧增量、对象显隐与颜色。
- **关键类/函数**：`public wxDialog`（hpp L51）；`mTrajFrame`（MdiChildTrajFrame*，hpp L83）；`Create()`（cpp L264）、`LoadData()`（L493）、`SaveData()`（L571）、`ShowData()`（L548）、`ResetData()`（L649）、`UpdateObjectList`（L217）/`UpdateObjectListBox`（L657）、`ShowColorDialog`（L682）、`OnApplyButtonClick`（L839）；动画与对象颜色通过 `GmatPlot::MDI_GL_*` 事件或直接回调 `mTrajFrame` 生效。

### 2.4 rendering 目录（25 个文件）

OpenGL 渲染支撑层：相机/光照/绘制工具函数/模型加载/3DS 解析。被 2.3 的画布（ViewCanvas 家族）与 ModelManager 使用。

#### Camera（Camera.hpp / Camera.cpp）

- **职责**：3D 相机：位置/朝向（forward/up/right 正交基）、视点中心、FOV、平移/旋转/缩放/重定位。
- **关键类/函数**：`position/forward/up/right/view_center/fovDeg/trackingId`（hpp L44-54）；`Relocate`（cpp L212/L224）、`Translate/TranslateW`（L60/L90，世界系/相机系）、`Rotate`（L173）、`ReorthogonalizeVectors`（L155，正交化漂移的基向量）、`ZoomIn/ZoomOut`（L236/L256）、`Reset`（L275）；内部 `CameraMode` 枚举（hpp L76，STILL/FOLLOW_TRACKING 等，跟踪功能当前注释未启用）。

#### Light（Light.hpp / Light.cpp）

- **职责**：OpenGL 光源：位置、镜面反射色、是否平行光。
- **关键类/函数**：`specular[4]/position/directional`（hpp L49-51）；`GetPosition/GetColor/IsDirectional`（cpp L86/L93/L100）、`SetColor`（L110/L120）、`SetDirectional`（L128）、`SetPosition`（L132/L136）。

#### Rendering（Rendering.hpp / Rendering.cpp）

- **职责**：一组自由函数形式的 GL 绘制原语：球、线、立方体、航天器简化模型、圆、方块、字符串、平面。
- **关键类/函数**：`GlColorType`/`GlRgbColorType` 结构（hpp L36-51，注意 GlColorType 按 Intel 存储序把 blue 放第一位）；`SetColor`（cpp L42）、`DrawSphere`（L56，gluSphere 封装）、`DrawLine`（L84/L104/L125 三种重载）、`DrawCube`（L137）、`DrawSpacecraft`（L184，球 + 翼片近似）、`DrawEquatorialPlanes`（L204）、`DrawCircle`（L211/L226）、`DrawSquare`（L259）、`DrawStringAt`（L278/L290，位图文字）。

```cpp
// src/gui/rendering/Rendering.cpp L84-95（GL 线段原语）
void DrawLine(GlColorType *color, const Rvector3 &start, const Rvector3 &end)
{
   glPushMatrix();
   glBegin(GL_LINES);

   glColor3ub(color->red, color->green, color->blue);
   glVertex3f(start[0], start[1], start[2]);
   glVertex3f(end[0], end[1], end[2]);

   glEnd();
   glPopMatrix();
}
```
逐行解释：`glPushMatrix/glPopMatrix` 保护调用方矩阵栈；`glBegin(GL_LINES)` 到 `glEnd()` 之间提交两个顶点构成一条线段；颜色经 `glColor3ub` 以字节（0-255）设定。所有画布画轨道线、网格线都走这组原语。

#### GmatOpenGLSupport（GmatOpenGLSupport.hpp / GmatOpenGLSupport.cpp）

- **职责**：平台相关的 OpenGL 初始化与截图：像素格式、默认字体、屏幕截图。
- **关键类/函数**：`SetPixelFormatDescriptor`（cpp L46）、`SetDefaultGLFont`（L134）、`InitGL`（L166）、`ScreenShotSave`（L217）。

#### FallbackFont（FallbackFont.hpp，单头文件）

- **职责**：8×8 像素的 CGA 字体位图数组（公有领域 IBM CGA 字体），OpenGL 位图文字在无系统字体时的后备。
- **关键类/函数**：`unsigned char FallbackFont[]`（L6-134，每字符 8 字节）。纯数据文件，无类。

#### GLStars（GLStars.hpp / GLStars.cpp）

- **职责**：星空绘制单例：从文件加载恒星/星座/星座边界，按亮度分组建顶点数组绘制。
- **关键类/函数**：`Instance()` 单例（hpp L55）；容量常量（hpp L43-49）：`MAXSTARS=42101`、`MAXLINES=1600`、`MAXBORDERS=64000`、`GROUPCOUNT=18`；`InitStars`（cpp L376）、`ReadStars`（L90）、`ReadConstellations`（L155）、`ReadBorders`（L237）、`SetVector`（L330，RA/Dec→三维单位向量）、`Correct1875`（L347，岁差修正到 1875 历元）、`DrawStarsVA`（L394，顶点数组 + 点尺寸分组绘制）。

#### LoadPOV（LoadPOV.hpp / LoadPOV.cpp）

- **职责**：POV-Ray 格式模型加载工具（自 Odyssey 移植）。
- **关键类/函数**：`LoadPOV(ModelObject*, const std::string&)`（cpp L94）。

#### ModelManager（ModelManager.hpp / ModelManager.cpp）

- **职责**：模型仓库单例：把磁盘模型文件加载为 ModelObject，按路径缓存并分配整数 ID，共享 GL 上下文。
- **关键类/函数**：`Instance()`（cpp L44-49）；`modelMap`（int→ModelObject*）与 `modelIdMap`（路径→int，hpp L41-42）；`LoadModel(std::string&)`（cpp L148-190）：命中缓存直接返回 ID，否则新建 ModelObject→`Load(modelPath)`→登记两表：

```cpp
// src/gui/rendering/ModelManager.cpp L159-182（缓存 + 加载）
// Check if modelPath found in the map, if found return modelId
if (modelIdMap.find(modelPath) != modelIdMap.end())
{
   int modelId = modelIdMap[modelPath];
   return modelId;
}

ModelObject *newModel = new ModelObject();

newModel->Load(modelPath);
modelMap[numElements] = newModel;
modelIdMap[modelPath] = numElements;
numElements++;
```
  - `GetSharedGLContext/SetSharedGLContext`（L104/L113）：多画布共享 GL 上下文（Bug 2591 修复：上下文删除移入 ModelManager 析构，L88-97）。析构/`ClearModel`（L122）统一释放所有 ModelObject。

#### ModelObject（ModelObject.hpp / ModelObject.cpp）

- **职责**：单个模型对象：从 .3ds 加载几何/材质/纹理，按航天器或天体姿态自渲染，支持阴影体。
- **关键类/函数**：`TheStructure`（Structure*，hpp L55）、`matrix_type`/`rgba_type`（hpp L37-48）；`Load(const std::string&)`（cpp L88，按扩展名分派 3DS/POV 读取器）、`LoadTextures`（L147）、`DrawAsSpacecraft`（L386）/`DrawAsCelestialBody`（L391）→ `Draw(isLit, ispacecraft)`（L402）→ `SetMatrix`（L422）；姿态/位置/缩放 setter `SetRotation/SetAttitude/SetScale/SetBodyPosition`（L329-367）；`Reset`（L375）；私有 4×4 矩阵工具 `MatrixIdentity/MatrixRotation/MatrixMult` 等（L506-591，注释说明用 C 数组而非 Rmatrix 是为了速度）。

#### Structure（Structure.hpp / Structure.cpp）

- **职责**：模型结构树：材质（ZMaterial）、关节（Joint）、附属件（ZAppendage）、整体 Structure 的旋转/质心/渲染。
- **关键类/函数**：
  - `ZMaterial`（hpp L34-60）：颜色/光泽度/纹理映射（UScale/VScale/UOffset/VOffset）/GL 纹理 ID。
  - `Joint`（hpp L85-122）：最多 3 个旋转轴（Use/Axis/Vary/Minimum/Maximum/DefaultDeg/CurrDeg），`GetMatrix`/`SetAngleDeg`/`SetToDefault`，静态轴向量 `XX/YY/ZZ`（L118-120）。
  - `ZAppendage`（hpp L124-149）：一个附属件 = 颜色 + `SurfaceGroup Body` + `Joint TheJoint` + 基座名。
  - `Structure`（hpp L174-206）：`Appendages`/`Materials` 数组、`Center`/`Radius`；`AddAppendage`（cpp L389）、`AddMaterial`（L395）、`SetJointsToDefault`（L401）、`FindMaterial`（L409）、`CalcBodyRotations`（L427）、`CalcCenter`（L445）、`Render`（L468）、`Write`（L460，写出调试文件）、`WriteSummary`（L475）。
- **继承/组合要点**：Structure 不继承 GmatBase，是纯渲染数据类；SurfaceBase（见下）是几何载体，Structure 通过 ZAppendageArray 持有多个 `SurfaceGroup`。

#### StructureReader（StructureReader.hpp / StructureReader.cpp）

- **职责**：结构文件读取器抽象基类：给定文件名产出 Structure*。
- **关键类/函数**：`Filename`/`TheStructure`（hpp L49-50）；纯虚 `virtual void Execute() = 0`（hpp L46）；构造/析构（cpp L30/L37）。派生：StructureReader3ds。

#### StructureReader3ds（StructureReader3ds.hpp / StructureReader3ds.cpp）

- **职责**：Autodesk 3DS 二进制格式解析器：按 chunk（块）递归读取网格/材质/纹理坐标。
- **关键类/函数**：辅助结构 `ZIntegerVector/ZMaterialData/ChunkReport`（hpp L31-79）；解析状态成员 `Ob4000_Name/Ob4110_Vectors/Ob4120_Faces/Ob4130_Material[100]/ObA010_Ambient...`（hpp L124-154，命名即 3DS chunk ID：0x4110 顶点、0x4120 面、0x4130 材质、0xA000 材质数据）；`ReadChunk`（cpp L252，核心递归）、`ReadChunks`（L852）、`BuildMesh`（L105 hpp 声明）、小端读取原语 `ReadLeInt/ReadLeShort/ReadLeFloat/ReadCstr`（L941-967）、`Execute`（L979）；大量 `Clear*` 释放函数（L132-243）。

#### SurfaceBase（SurfaceBase.hpp / SurfaceBase.cpp）

- **职责**：多边形网格体系：SurfaceBase（抽象）→ SurfaceGroup（组）与 SurfaceMesh（网格），配套向量缓存/包围盒/面工具。
- **关键类/函数**：
  - `SurfaceBase`（hpp L34-59）：纯虚 `InitWrtSpacecraft/MinMax/RotateBody/Render/WriteSummary`。
  - `SurfaceGroup`（hpp L84-103）：`ZChildArray Children` 递归组合。
  - `ZVectorCache/ZVectorCacheArray`（hpp L140-181）：顶点缓存（WrtBody/WrtSpacecraft 双坐标系）与包围盒 `ZMinMax`。
  - `ZFace`（hpp L198-217）：三角面（3 顶点索引 + 纹理坐标 + 法向索引），`Sides/Perimeter/Area/Density`（cpp L344-376）。
  - `SurfaceMesh`（hpp L219-247）：`Vectors`（ZVectorCacheArray）+ `Faces`；`BuildNormals`（cpp L464）、`Render`（L484）、`InitWrtSpacecraft`（L440）、`RotateBody`（L450）。

### 2.5 resource 目录（6 个文件）

- **GmatIcon.rc**（1 行）：`appIcon ICON "GMAT.ico"`——Windows 资源脚本，把 GMAT.ico 绑定为应用图标。
- **GmatRc.rc**（4 行）：`#include "wx/msw/wx.rc"`——引入 wxWidgets 自带 Windows 资源（光标/图标等）。
- **TrajectoryPlot.rc**（5 行）：把 `bitmaps/open.bmp`、`zoomin.bmp`、`zoomout.bmp` 注册为 `open/zoomin/zoomout` BITMAP 资源（轨迹窗口工具栏）。
- **GMAT.ico / GMATIcon.icns / GMATMac.icns**（二进制）：Windows/通用/Mac 平台的应用图标，由上述 .rc 或构建系统引用。

### 2.6 asset 目录（2 个文件）

#### GroundStationPanel（GroundStationPanel.hpp / GroundStationPanel.cpp）

- **职责**：GroundStation 资源（地面站）配置面板：站 ID、硬件、位置（按状态类型）、最小仰角、中心天体、地平参考（HorizonReference）。注意该面板位于 `gui/asset`，与引擎侧 `GroundStation` 类（[第6章](CH06-dynamics.md) 硬件/interface）对应。
- **关键类/函数**：`theGroundStation/localGroundStation`（GroundstationInterface*，hpp L83-84，本地克隆编辑模式）；控件：`stationIDTextCtrl/hardwareTextCtrl/location1-3TextCtrl/minElevationCtrl/centralBodyComboBox/stateTypeComboBox/horizonReferenceComboBox`（hpp L86-102）；`Create()`（cpp L118）、`LoadData()`（L310）、`SaveData()`（L350）、`UpdateControls()`（L501，按状态类型切换位置标签与单位：Geocentric→纬度/经度/高度，BodyFixed→X/Y/Z）、`OnStateTypeComboBoxChange`（L568）、`OnHorizonReferenceComboBoxChange`（L635）。
- **双向同步要点**：位置三分量按当前状态类型（经纬高 vs 笛卡尔）读写引擎参数，`location1Unit` 等标签随状态类型切换（米/度），是"单位随上下文切换"的面板范例。

### 2.7 plugin 目录（2 个文件）

#### WxGuiInterface（WxGuiInterface.hpp / WxGuiInterface.cpp）

- **职责**：wxWidgets 版 GUI 插件接口单例：插件经 `GuiInterface`（基类见 [第4章](CH04-executive-factory.md)）创建对象并登记到资源树。
- **关键类/函数**：`public GuiInterface`（hpp L44）；`Instance()` 单例（cpp L43-48）；`CreateObject(ofType, withName)`（cpp L64-83）：调基类工厂创建 GmatBase 后 `resourceTree->AddObjectToTree(retval)` 挂入资源树：

```cpp
// src/gui/plugin/WxGuiInterface.cpp L64-83（创建对象并登记资源树）
GmatBase* WxGuiInterface::CreateObject(const std::string& ofType,
      const std::string& withName)
{
   GmatBase *retval = GuiInterface::CreateObject(ofType, withName);

   if (retval)
   {
      if (resourceTree)
      {
         resourceTree->AddObjectToTree(retval);
      }
   }

   return retval;
}
```
  - `CreateGuiElement(ofType, withName)`（L100-106）：GUI 元素创建占位（当前返回 NULL）；`SetResourceTree(ResourceTree*)`（L117）；构造（L131-136）取 `GuiInterpreter::Instance()`。插件体系见 [第13章](CH13-plugins-a.md)。

### 2.8 function 目录（4 个文件）

#### FunctionSetupPanel（FunctionSetupPanel.hpp / FunctionSetupPanel.cpp）

- **职责**：GmatFunction（脚本函数）编辑面板：加载/新建/保存函数脚本文件，可选用 ScriptEditor（STC）。
- **关键类/函数**：`theGmatFunction`（Function*，hpp L58）、`mFullFunctionPath/mFunctionName/mIsNewFunction/mFilename`（hpp L59-69）；`mFileContentsTextCtrl`（hpp L51）或 `mEditor`（`__USE_STC_EDITOR__`，hpp L62-64）；`Create()`（cpp L137）、`LoadData()`（L186，读函数文件内容）、`SaveData()`（L227，写回文件并同步 Function 对象）、`OnButton`（L294，Load/Save/New）、`OnSaveAs`（L340）、`SetEditorModified`（L122）。

#### MatlabFunctionSetupPanel（MatlabFunctionSetupPanel.hpp / MatlabFunctionSetupPanel.cpp）

- **职责**：MatlabFunction 面板：选择 .m 文件路径（经 GuiInterpreter 登记 Matlab 函数）。
- **关键类/函数**：`theMatlabFunction`（Function*，hpp L46）；`mPathTextCtrl/mBrowseButton`（L50-51）；`Create()`（cpp L72）、`LoadData()`（L113）、`SaveData()`（L126）、`OnBrowse`/`OnButton`（L144）。

### 2.9 include 目录（204 个文件）

#### DoxygenGuiIntro.hpp

- **职责**：Doxygen `\mainpage` 页：GUI 代码总览（说明 GUI 与 libGmatUtil/libGmatBase 的关系、文档组织），纯注释文件（L1-39）。

#### gmatwxdefs.hpp

- **职责**：所有 GUI 源文件共用的 wxWidgets 头：编译器警告抑制、wx 预编译头、GLCanvas 支持、跨版本字符串宏。
- **关键内容**：`wxUSE_GLCANVAS 1`（L64-66）；平台宏 `GUI_ACCEL_KEY`（Windows 用 "&" 加速键前缀，L84-94）；wx 3.0 版本适配（L98-112）：`STD_TO_WX_STRING = wxString`、`WX_TO_STD_STRING = ToStdString()`、`gmatFD_OPEN = wxFD_OPEN`（旧版回退 `c_str()`/`wxOPEN`）；MSVC 4267 告警抑制（L33-36、L49-51）。

#### gmatwxrcs.hpp

- **职责**：平台图标资源引用：非 Windows 平台引入 `mondrian.xpm` 作为应用图标（L30-32）。

#### ddesetup.hpp

- **职责**：MATLAB 接口的 DDE（Windows 动态数据交换）配置：服务名/主题/项名。
- **关键内容**：`IPC_SERVICE "4242"`、`IPC_TOPIC "GMAT-MATLAB"`、`IPC_ADVISE_NAME "Item"`（L40-46）。配合 [第12章](CH12-applications.md) 的 matlab 接口。

#### bitmaps/ 目录（200 个文件）

- **职责**：GUI 全部图标位图资源，供工具栏、资源树、命令分类树、天体/对象图标使用。分七类：
  1. **通用工具栏/文件操作**（约 40 个）：`NewMission`、`OpenScript`、`SaveMission`、`CloseAll`、`CloseOne`、`Copy/Cut/Paste`、`Erase`、`Help`、`WebHelp`、`WriteInformation`、`NewScript`、`Screenshot`、`run/save/saveobject/preview/print/build/back/backall/up/down/forward`、`zoomin/zoomout`、`open.bmp`、`splash.bmp/.xpm`、`BlankIcon`、`DefaultMission`、`ClosedFolder/OpenFolder/file/folder/redfile/redfolder`、`mondrian.xpm`。
  2. **动画控制**（7 个）：`RunAnimation`（.bmp/.gif/.png/.xpm 四种格式）、`PauseAnimation`、`StopAnimation`、`FasterAnimation`、`SlowerAnimation`、`animation_options`。
  3. **天体图标**（19 个）：`sun/mercury/venus/earth/moon/moon_generic/mars/jupiter/saturn/uranus/neptune/pluto/triton/asteroid/comet/constellation/planet_generic`。
  4. **命令分类图标 mtc_\***（14 个）：`mtc_L1/mtc_L2/mtc_L3/mtc_LA`（命令库层级）、`mtc_IncControlFlow/mtc_IncPhysics/mtc_IncScriptEvent/mtc_IncSolver`（插入分类）、`mtc_ExcCall/mtc_ExcEquation/mtc_ExcPlot/mtc_ExcReport`（排除分类）、`mtc_CustomView/mtc_ClearFilters`。
  5. **命令图标 mt_\***（17 个）：`mt_CallGmatFunction/mt_CallMatlabFunction/mt_ClearPlot/mt_Default/mt_FindEvents/mt_Global/mt_MarkPoint/mt_Minimize/mt_NonlinearConstraint/mt_Report/mt_RunEstimator/mt_RunSimulator/mt_SaveMission/mt_SetCommand/mt_Stop/mt_WriteCommand`。
  6. **资源树类型图标 rt_\***（48 个）：`rt_Antenna/rt_Array/rt_Barycenter/rt_BoundaryValueSolver/rt_ChemicalTank/rt_ChemicalThruster/rt_ContactLocator/rt_CoordinateSystem/rt_Default/rt_DifferentialCorrector/rt_EclipseLocator/rt_ElectricTank/rt_ElectricThruster/rt_EphemerisFile/rt_Estimator/rt_FileInterface/rt_FiniteBurn/rt_Formation/rt_GmatFunction/rt_GroundStation/rt_GroundTrackPlot/rt_Hardware/rt_ImpulsiveBurn/rt_LibrationPoint/rt_Matlab/rt_MatlabFunction/rt_MatlabServer/rt_MeasurementModel/rt_NuclearPowerSystem/rt_Optimizer/rt_OrbitView/rt_Propagator/rt_Receiver/rt_ReportFile/rt_Script/rt_Simulator/rt_SolarPowerSystem/rt_SolarSystem/rt_Solver/rt_Spacecraft/rt_String/rt_Subscriber/rt_Tank/rt_Thruster/rt_Transmitter/rt_Transponder/rt_Variable/rt_XYPlot`。
  7. **命令/事件/杂项图标**（约 55 个）：`achieveevent/propagateevent/varyevent/scriptevent/target/toggle/forloop/whileloop/if/nestreturn/minimize/optimize/beginfb/endfb/deltav/equalsign/pendown/penup/matrix/matlabfunction/network/openglplot/report/copy/cut/paste/plot_dwn/plot_enl/plot_shr/plot_up/plot_zin/plot_zot/GMAT.icns/GMATMainIcon.ico` 等。
- **代表性文件**：`.xpm` 是 C 数组文本（wxWidgets 直接编译进程序）；`.png/.bmp/.gif/.ico/.icns` 是运行时/构建期二进制资源；`RunAnimation` 与 `Screenshot` 各有多种格式版本供不同平台/场景使用。全部 200 个文件清单见 `四、文件清单附录` 表 9。

## 三、关键设计模式与数据流

### 3.1 GmatPanel 模板方法：Create / LoadData / SaveData 三阶段生命周期

本章 141 个面板类（除 SolverCreatePanel、TsPlotCanvas 等少数 wx 原生控件）都遵守 GmatPanel 契约（[第9章](CH09-gui-core.md)）：构造 → `Create()`（建控件）→ `LoadData()`（引擎→控件）→ 用户编辑（各 `OnXxxChange` 调 `EnableUpdate(true)`）→ 点 Apply/OK 触发 `SaveData()`（控件→引擎）。`canClose` 是"校验闸门"：SaveData 中任何 `CheckReal/CheckInteger/GetConfiguredObject` 失败都置 `canClose=false` 阻止关闭。这是全章统一的面板生命周期模板方法。

### 3.2 参数表驱动的双向同步（GetParameterID / Get/SetXxxParameter）

所有面板通过 GmatBase 参数表（[第2章](CH02-foundation.md)）与引擎对象通信，不直接碰内部成员：`theCommand->GetParameterID("Targeter")` → `SetStringParameter(id, value)`。三类形态：
- **短参数表直读直写**：TargetPanel（L160-218）、ManeuverPanel、FindEventsPanel、ReportPanel——几个组合框/复选框，`LoadData`/`SaveData` 一一对应。
- **网格/列表整表回写**：PropagatePanel（15×4 传播器网格 + 10×5 停止条件网格，L1130-1249 先校验后回写）、SolverGoalsPanel/SolverVariablesPanel（wxGrid 目标/变量表）。
- **反射式通用面板**：SolverSetupPanel / SubscriberSetupPanel——不写死参数名，遍历 `GetParameterCount()` + `IsParameterReadOnly` 自动生成控件（cpp L193-213），`LoadControl`/`SaveControl` 按 `ParameterType` 分派（BOOLEAN→组合框、REAL/INTEGER/STRING→文本框）。
- **克隆编辑**：EphemerisFilePanel（`clonedObj`）、GroundStationPanel（`localGroundStation`）——先在克隆上编辑，SaveData 才提交引擎对象。

重命名联动是双向同步的延伸：`PrepareObjectNameChange`/`ObjectNameChanged(type, oldName, newName)` 在 PropagatePanel（cpp L119/L139）、CallFunctionPanel（L97/L117）、XyPlotSetupPanel（L134/L154）、ReportFileSetupPanel（L130/L150）、OrbitViewPanel（L146/L166）、GroundTrackPlotPanel（L134/L154）实现——资源树重命名对象后，面板里的引用字符串同步更新，避免悬垂引用。

### 3.3 求解器面板的"容差/最大迭代参数网格"

SQPSetupPanel 是典型：7 个容差/迭代文本域（TolFun/TolCon/TolX/MaxFunEvals/MaximumIterations/DiffMinChange/DiffMaxChange）构成参数网格，`LoadData` 逐格读引擎（cpp L144-163），`SaveData` 逐格 `CheckReal`/`CheckInteger` 校验后写回（L208-254）。DCSetupPanel 只取其中 MaximumIterations 加报告/算法/差分选项。SolverSetupPanel 把这一模式推广为"任意求解器参数的自动网格"。同一参数网格在运行期经 [第8章](CH08-base-subsystems.md) 的 Solver 参数表驱动迭代过程。

### 3.4 订阅器运行时数据流（引擎 → 窗口 → 画布）

```
引擎 Subscriber (XyPlot/OrbitView/GroundTrackPlot/ReportFile/...)
   │  (Subscriber 回调, 见第8章)
   ▼
GuiInterpreter ──► MdiChildXxxFrame::UpdatePlot(...)      (MdiChildViewFrame.cpp L849,
   │                                                        MdiChildTsFrame.cpp L446 AddDataPoints)
   ▼
ViewCanvas::UpdatePlot (ViewCanvas.cpp L903) ──► 环形缓冲 (mTime/mObjectGciPos/...,
   │                                              ComputeRingBufferIndex L1507)
   ▼
OnPaint → DrawPlot (OrbitViewCanvas.cpp L1821 / GroundTrackCanvas.cpp L910 /
                     TsPlotCanvas.cpp L171) ──► Rendering.cpp 原语 / wxDC
```
- 3D 通道：MdiChildViewFrame 把订阅器参数（对象、坐标系、视点、绘制开关）转发给 ViewCanvas 子类；数据逐点进环形缓冲，按 `mUpdateFrequency`/`mNumPointsToRedraw` 节流重绘；求解器迭代数据单独存 `mSolverAllPos*` 数组并着色叠加（DrawSolverData，L3178）。
- 2D 通道：MdiChildTsFrame 直接操作 TsPlotCanvas 的曲线 API（AddPlotCurve/AddDataPoints/PenUp/PenDown/Darken/Lighten/MarkPoint），TsPlotCanvas 负责坐标变换、缩放、图例。
- 地面轨迹通道（2025 新组件）：GroundTrackWindow::AddData（L238）→ GroundTrackArea::AddData（L419）→ GroundTrackCurve 存储 → OnPaint（L503）绘制底图与轨迹。
- 交互反向通道：画布/窗口菜单 → `TakeAction(action)` → GuiInterpreter/订阅器（如 OrbitViewCanvas::TakeAction L868、GroundTrackCanvas::TakeAction L469）；求解器表格窗口则通过 `ISolverListener` 回调（MdiTableViewFrame::ConstraintChanged L467、Convergence L520）实时显示收敛过程。

### 3.5 渲染模型体系：单例仓库 + 结构树 + 读取器分派

```
ModelManager（单例, ModelManager.cpp L44）──► ModelObject::Load（按扩展名分派, ModelObject.cpp L88）
                                                     │
                                     ┌───────────────┴───────────────┐
                                     ▼                               ▼
                          StructureReader3ds（3DS chunk 递归解析,     LoadPOV（POV-Ray）
                          StructureReader3ds.cpp L252/L979）
                                     │
                                     ▼
                          Structure（结构树: ZMaterial/Joint/ZAppendage, Structure.cpp L389+）
                                     │
                                     ▼
                          SurfaceBase（SurfaceGroup/SurfaceMesh 递归网格, SurfaceBase.cpp L116+）
                                     │
                                     ▼
                          ModelObject::Draw → Rendering.cpp 原语（GL 绘制）
```
画布（ViewCanvas 子类）经 `ModelManager::LoadModel` 拿模型 ID（按路径缓存，L148-190），共享一个 wxGLContext（L104-116），模型姿态由航天器状态驱动（`DrawSpacecraft3dModel` OrbitViewCanvas.cpp L2628）。星空是另一个单例（GLStars），恒星按亮度分组顶点数组绘制，1875 历元岁差修正（GLStars.cpp L347）。

### 3.6 插件 GUI 接口与面板 ID 隔离

WxGuiInterface 单例（WxGuiInterface.cpp L43）让插件对象创建自动进资源树（L76-79）。所有面板的事件 ID 用互不重叠的枚举区间（GmatCommandPanel 93000、PropagatePanel 44000、TargetPanel/OptimizePanel 51000、AchievePanel/VaryPanel/MinimizePanel/NonlinearConstraintPanel 53000、SolverSetupPanel/DCSetupPanel/SQPSetupPanel 55000、ScriptEventPanel 9000、ManeuverPanel/BeginFiniteBurnPanel/FindEventsPanel 80000、XyPlotSetupPanel 92000、ReportPanel/ReportFileSetupPanel/OrbitViewPanel 93000、GroundStationPanel 39010、TsPlotOptionsDialog 44400、OpenGlOptionDialog 8120、DynamicDataDisplaySetupPanel 9000、MdiGlPlotData 500、MdiTsPlotData 600 起），保证 wx 事件表互不串扰。

## 四、文件清单附录

### 表 1：command 目录（36 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/command/GmatCommandPanel.hpp | 通用脚本字符串命令面板声明 | GmatCommandPanel、Create/LoadData/SaveData、OnTextChange |
| src/gui/command/GmatCommandPanel.cpp | 生成串编辑与 InterpretAction/VerifyObjects/ValidateCommand 校验链 | ctor L67、SaveData L175 |
| src/gui/command/PropagatePanel.hpp | Propagate 面板声明：15×4 传播器网格、10×5 停止条件网格常量 | PropType、StopCondType、MAX_PROP_ROW 等（L60-72） |
| src/gui/command/PropagatePanel.cpp | 传播器/停止条件编辑、校验与双向同步 | Create L171、LoadData L947、SaveData L1130、OnCellValueChange L869 |
| src/gui/command/TargetPanel.hpp | Target 命令面板声明 | mSolverComboBox 等（L48-52） |
| src/gui/command/TargetPanel.cpp | Targeter/SolveMode/ExitMode/ApplyCorrections | LoadData L160、SaveData L192、OnApplyButtonPress L237 |
| src/gui/command/ManeuverPanel.hpp | Maneuver 命令面板声明 | burnCB、satCB、backpropCheckBox |
| src/gui/command/ManeuverPanel.cpp | Burn/航天器选择与反向机动 | Create L128、LoadData L200、SaveData L272 |
| src/gui/command/ReportPanel.hpp | Report 命令面板声明 | mReportFileComboBox、mSelectedListBox |
| src/gui/command/ReportPanel.cpp | ReportFile 与参数列表编辑 | LoadData L181、SaveData L241 |
| src/gui/command/AchievePanel.hpp | Achieve 命令面板声明 | mAchieveCommand、容差/目标文本域 |
| src/gui/command/AchievePanel.cpp | 目标名/值/容差编辑 | LoadData L168、SaveData L226 |
| src/gui/command/AssignmentPanel.hpp | Assignment 面板声明 | mLhsTextCtrl/mRhsTextCtrl |
| src/gui/command/AssignmentPanel.cpp | lhs=rhs 编辑与取消还原 | LoadData L133、SaveData L159、OnCancel L386 |
| src/gui/command/BeginFiniteBurnPanel.hpp | BeginFiniteBurn 面板声明 | mFiniteBurnComboBox、mSatTextCtrl |
| src/gui/command/BeginFiniteBurnPanel.cpp | 有限推力 Burn 开始配置 | Create L150、LoadData L227、SaveData L260 |
| src/gui/command/EndFiniteBurnPanel.hpp | EndFiniteBurn 面板声明 | 同 BeginFiniteBurnPanel |
| src/gui/command/EndFiniteBurnPanel.cpp | 有限推力 Burn 结束配置 | Create L150、LoadData L228、SaveData L261 |
| src/gui/command/CallFunctionPanel.hpp | CallGmatFunction 面板声明 | theFunctionComboBox、输入/输出文本域 |
| src/gui/command/CallFunctionPanel.cpp | 函数选择与参数列表编辑、重命名联动 | LoadData L229、SaveData L324、ObjectNameChanged L117 |
| src/gui/command/FindEventsPanel.hpp | FindEvents 面板声明 | locatorCB、appendCheckBox |
| src/gui/command/FindEventsPanel.cpp | 事件定位器选择 | Create L119、LoadData L172、SaveData L221 |
| src/gui/command/GmatCommandPanel.hpp | （同上） | |
| src/gui/command/ManageObjectPanel.hpp | Save 命令对象管理面板声明 | mObjectCheckListBox |
| src/gui/command/ManageObjectPanel.cpp | 对象勾选保存 | LoadData L172、SaveData L202 |
| src/gui/command/MinimizePanel.hpp | Minimize 命令面板声明 | mVariableTextCtrl、mSolverComboBox |
| src/gui/command/MinimizePanel.cpp | 目标参数选择 | LoadData L136、SaveData L175、ShowGoalSetup L231 |
| src/gui/command/NonlinearConstraintPanel.hpp | 非线性约束面板声明 | LHS/RHS/容差/比较算子控件 |
| src/gui/command/NonlinearConstraintPanel.cpp | 表达式与容差编辑 | LoadData L181、SaveData L233 |
| src/gui/command/OptimizePanel.hpp | Optimize 命令面板声明 | 同 TargetPanel 布局 |
| src/gui/command/OptimizePanel.cpp | 求解器/模式/ApplyCorrections | LoadData L167、SaveData L198 |
| src/gui/command/ScriptEventPanel.hpp | ScriptEvent 面板声明 | mCommentTextCtrl、wxSashLayoutWindow 双窗 |
| src/gui/command/ScriptEventPanel.cpp | 脚本事件文本编辑与命令链替换 | LoadData L315、SaveData L387、ReplaceScriptEvent L846 |
| src/gui/command/TogglePanel.hpp | Toggle 命令面板声明 | mSubsCheckListBox、On/Off 单选 |
| src/gui/command/TogglePanel.cpp | 订阅器开关 | LoadData L205、SaveData L282、TakeAction L107 |
| src/gui/command/VaryPanel.hpp | Vary 命令面板声明 | 7 个参数文本域 + 求解器组合框 |
| src/gui/command/VaryPanel.cpp | 变量/扰动/步长/上下限编辑 | LoadData L233、SaveData L320、SetControlEnabling L642 |

### 表 2：solver 目录（12 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/solver/SolverSetupPanel.hpp | 通用求解器参数面板声明 | propertyDescriptors/propertyControls/controlMap |
| src/gui/solver/SolverSetupPanel.cpp | 遍历可写参数自动建控件 | Setup L193、BuildControl L245、LoadControl L282、SaveControl L337 |
| src/gui/solver/SolverCreatePanel.hpp | 新建求解器向导声明（wxPanel） | theGuiInterpreter |
| src/gui/solver/SolverCreatePanel.cpp | 输入名字创建求解器 | Initialize L69、Setup L74、SetData L164 |
| src/gui/solver/SolverGoalsPanel.hpp | 求解目标网格面板声明 | goalsGrid |
| src/gui/solver/SolverGoalsPanel.cpp | 目标/值/容差网格编辑 | Setup L99、OnCellValueChanged L228 |
| src/gui/solver/SolverVariablesPanel.hpp | 求解变量网格面板声明 | varsGrid |
| src/gui/solver/SolverVariablesPanel.cpp | 变量/扰动/步长网格编辑 | Setup L96、OnCellValueChanged L261 |
| src/gui/solver/DCSetupPanel.hpp | 微分校正器面板声明 | theDC、算法/差分/报告控件 |
| src/gui/solver/DCSetupPanel.cpp | DC 最大迭代与报告配置 | LoadData L101、SaveData L138、OnBrowse L393 |
| src/gui/solver/SQPSetupPanel.hpp | SQP 优化器面板声明 | 7 个容差/迭代文本域 |
| src/gui/solver/SQPSetupPanel.cpp | 容差/最大迭代参数网格 | LoadData L110、SaveData L194、Setup L303 |

### 表 3：subscriber 目录（57 文件）——配置面板与对话框

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/subscriber/SubscriberSetupPanel.hpp | 通用订阅器参数面板声明 | controlMap 等 |
| src/gui/subscriber/SubscriberSetupPanel.cpp | 遍历订阅器可写参数自动建控件 | Setup L194、LoadControl L283、SaveControl L339 |
| src/gui/subscriber/XyPlotSetupPanel.hpp | XYPlot 面板声明 | mXyPlot、X/Y 参数列表 |
| src/gui/subscriber/XyPlotSetupPanel.cpp | X/Y 参数与求解迭代配置 | LoadData L389、SaveData L467、ObjectNameChanged L154 |
| src/gui/subscriber/ReportFileSetupPanel.hpp | ReportFile 面板声明 | 12 个控件（见正文） |
| src/gui/subscriber/ReportFileSetupPanel.cpp | 文件/格式/参数配置 | LoadData L373、SaveData L506 |
| src/gui/subscriber/OrbitViewPanel.hpp | OrbitView 面板声明（最大订阅器面板） | 40+ 控件、ShowSpacePointOption |
| src/gui/subscriber/OrbitViewPanel.cpp | 对象/视点/绘制选项配置 | Create L223、LoadData L768、SaveData L1101、ValidateFovValues L2227 |
| src/gui/subscriber/GroundTrackPlotPanel.hpp | GroundTrackPlot 面板声明 | mCentralBodyComboBox、纹理/频率控件 |
| src/gui/subscriber/GroundTrackPlotPanel.cpp | 中心天体/纹理/对象/颜色配置 | LoadData L442、SaveData L544 |
| src/gui/subscriber/EphemerisFilePanel.hpp | EphemerisFile 面板声明 | 克隆编辑 + 格式相关控件 |
| src/gui/subscriber/EphemerisFilePanel.cpp | 星历文件格式/坐标系/插值配置 | LoadData L357、SaveData L417、ShowCoordSystems L1229 |
| src/gui/subscriber/DynamicDataDisplaySetupPanel.hpp | 动态数据显示面板声明 | displayDataStruct（DDD） |
| src/gui/subscriber/DynamicDataDisplaySetupPanel.cpp | 行/列/颜色/单元格配置 | LoadData L177、SaveData L259、OnGridCellDClick L378 |
| src/gui/subscriber/DynamicDataSettingsDialog.hpp | 单格参数对话框声明 | DDD 读写 |
| src/gui/subscriber/DynamicDataSettingsDialog.cpp | 参数上下界/颜色编辑 | SaveData L204、OnSelect L275 |
| src/gui/subscriber/OpenGlOptionDialog.hpp | 3D 视图选项对话框声明 | mTrajFrame 回调 |
| src/gui/subscriber/OpenGlOptionDialog.cpp | 线框/平面/坐标系/动画选项 | Create L264、LoadData L493、SaveData L571 |

### 表 4：subscriber 目录——3D 画布与 TsPlot 画布

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/subscriber/ViewCanvas.hpp | OpenGL 画布抽象基类声明 | 纯虚 DrawXxx、环形缓冲成员 |
| src/gui/subscriber/ViewCanvas.cpp | GL 上下文/纹理/缓冲/绘制骨架 | UpdatePlot L903、ComputeRingBufferIndex L1507、DrawSolverData L3178 |
| src/gui/subscriber/OrbitViewCanvas.hpp | OrbitView 画布声明 | mStars/mCamera/mLight、视点对象 |
| src/gui/subscriber/OrbitViewCanvas.cpp | 3D 场景绘制 | DrawPlot L1821、DrawSpacecraft3dModel L2628、ConvertObjectData L3018 |
| src/gui/subscriber/GroundTrackCanvas.hpp | 地面轨迹画布声明 | mCentralBodyName 等 |
| src/gui/subscriber/GroundTrackCanvas.cpp | 球面纹理 + 轨迹绘制 | DrawPlot L910、DrawGroundTrackLines L1399、DrawCircleAt L1646 |
| src/gui/subscriber/TsPlotCanvas.hpp | 2D 时序图控件声明 | 纯虚 DrawAxes/DrawLabels/PlotData/Rescale |
| src/gui/subscriber/TsPlotCanvas.cpp | 坐标轴/网格/图例/缩放/曲线管理 | OnPaint L171、DrawGrid L752、Zoom L1388 |
| src/gui/subscriber/TsPlotXYCanvas.hpp | XY 时序图画布声明 | 继承 TsPlotCanvas |
| src/gui/subscriber/TsPlotXYCanvas.cpp | XY 轴/标签/数据绘制 | DrawAxes L68、PlotData L308、Rescale L569 |
| src/gui/subscriber/TsPlotCurve.hpp | 时序曲线数据模型声明 | 数据/断笔/颜色变化向量 |
| src/gui/subscriber/TsPlotCurve.cpp | 曲线数据增删与外观 | AddData L72、PenUp L334、SetColour L453 |
| src/gui/subscriber/TsPlotDefs.hpp | TsPlot 兼容定义与 MarkerType 枚举 | MarkerType（L48-65）、wx 版本宏 |
| src/gui/subscriber/TsPlotOptionsDialog.hpp | 时序图选项对话框声明 | getter/setter 群 |
| src/gui/subscriber/TsPlotOptionsDialog.cpp | 轴范围/刻度/精度编辑 | UpdateLabels L265、OnSettableXMinimum L489 |

### 表 5：subscriber 目录——MDI 框架与地面轨迹

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/subscriber/MdiGlPlotData.hpp | GL 绘图事件枚举与类型 | GlEventType（L44-63）、wxStringColorMap |
| src/gui/subscriber/MdiGlPlotData.cpp | GL 窗口静态数据定义 | MdiGlPlot::mdiChildren 等（L31-33） |
| src/gui/subscriber/MdiTsPlotData.hpp | 时序图事件枚举 | TsEventType（L36-48） |
| src/gui/subscriber/MdiTsPlotData.cpp | 时序图窗口静态数据定义 | MdiTsPlot 成员（L31-33） |
| src/gui/subscriber/MdiChildViewFrame.hpp | 3D 视图 MDI 基类声明 | mCanvas、大量转发 setter/getter |
| src/gui/subscriber/MdiChildViewFrame.cpp | 配置/数据转发到画布 | UpdatePlot L849、SetGlObject L751、SetGl3dViewOption L805 |
| src/gui/subscriber/MdiChild3DViewFrame.hpp | 3DView 子窗口声明 | 继承 MdiChildViewFrame |
| src/gui/subscriber/MdiChild3DViewFrame.cpp | 3D 选项定制 | SetGl3dDrawingOption L78、SetGl3dViewOption L98 |
| src/gui/subscriber/MdiChildTrajFrame.hpp | 轨迹子窗口声明 | mOptionDialog |
| src/gui/subscriber/MdiChildTrajFrame.cpp | 选项对话框菜单 | OnShowOptionDialog L112、OnDrawWireFrame L143 |
| src/gui/subscriber/MdiChildTsFrame.hpp | XY 时序子窗口声明 | mXyPlot、曲线 API 群 |
| src/gui/subscriber/MdiChildTsFrame.cpp | 曲线/数据操作封装 | AddPlotCurve L328、AddDataPoints L446、ReadXyPlotFile L206 |
| src/gui/subscriber/MdiChildGroundTrackFrame.hpp | 地面轨迹子窗口声明 | 继承 MdiChildViewFrame |
| src/gui/subscriber/MdiChildGroundTrackFrame.cpp | 2D 选项转发 | SetGl2dDrawingOption L78 |
| src/gui/subscriber/MdiChildDynamicDataFrame.hpp | 动态数据子窗口声明 | dynamicDataGrid |
| src/gui/subscriber/MdiChildDynamicDataFrame.cpp | 表格刷新与着色 | UpdateDynamicData L179、SetDynamicDataCellTextColor L221 |
| src/gui/subscriber/MdiTableViewFrame.hpp | 求解收敛表格窗口声明 | ISolverListener、三网格 |
| src/gui/subscriber/MdiTableViewFrame.cpp | 变量/约束/目标实时显示 | ConstraintChanged L467、Convergence L520 |
| src/gui/subscriber/GroundTrackWindow.hpp | 地面轨迹窗口声明 | theMap、theSS |
| src/gui/subscriber/GroundTrackWindow.cpp | 数据转发与菜单 | AddData L238、UpdatePlot L329、ResetForNewRun L341 |
| src/gui/subscriber/GroundTrackArea.hpp | 地面轨迹绘制面板声明 | MarkedPoint、bgImage、GroundTrackCurve 向量 |
| src/gui/subscriber/GroundTrackArea.cpp | 底图/网格/轨迹绘制 | AddData L419、OnPaint L503、SetSolarSystem L718 |
| src/gui/subscriber/GroundTrackCurve.hpp | 轨迹线段数据声明 | xData/yData/tData/penUp/colors |
| src/gui/subscriber/GroundTrackCurve.cpp | 轨迹数据操作 | AddData、PenUp、SetColor（部分内联于 hpp L85-102） |

### 表 6：rendering 目录（25 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/rendering/Camera.hpp | 相机声明 | position/forward/up/right、fovDeg |
| src/gui/rendering/Camera.cpp | 相机运动学 | Relocate L212、Rotate L173、ZoomIn L236 |
| src/gui/rendering/Light.hpp | 光源声明 | specular/position/directional |
| src/gui/rendering/Light.cpp | 光源设置 | SetColor L110、SetPosition L132 |
| src/gui/rendering/Rendering.hpp | GL 绘制原语声明 | GlColorType、DrawSphere 等 |
| src/gui/rendering/Rendering.cpp | GL 原语实现 | SetColor L42、DrawSphere L56、DrawLine L84、DrawSpacecraft L184 |
| src/gui/rendering/GmatOpenGLSupport.hpp | OpenGL 平台支持声明 | InitGL/SetPixelFormatDescriptor/ScreenShotSave |
| src/gui/rendering/GmatOpenGLSupport.cpp | GL 初始化/字体/截图 | InitGL L166、ScreenShotSave L217 |
| src/gui/rendering/FallbackFont.hpp | 8×8 CGA 后备字体数据 | FallbackFont[]（L6-134） |
| src/gui/rendering/GLStars.hpp | 星空单例声明 | MAXSTARS=42101、DrawStarsVA |
| src/gui/rendering/GLStars.cpp | 恒星/星座加载与绘制 | ReadStars L90、Correct1875 L347、DrawStarsVA L394 |
| src/gui/rendering/LoadPOV.hpp | POV-Ray 加载声明 | LoadPOV(ModelObject*, path) |
| src/gui/rendering/LoadPOV.cpp | POV-Ray 文件解析 | LoadPOV L94 |
| src/gui/rendering/ModelManager.hpp | 模型仓库单例声明 | modelMap/modelIdMap、共享 GL 上下文 |
| src/gui/rendering/ModelManager.cpp | 模型缓存/加载/释放 | Instance L44、LoadModel L148、ClearModel L122 |
| src/gui/rendering/ModelObject.hpp | 模型对象声明 | TheStructure、matrix_type |
| src/gui/rendering/ModelObject.cpp | 模型加载与自渲染 | Load L88、Draw L402、SetMatrix L422 |
| src/gui/rendering/Structure.hpp | 结构树声明 | ZMaterial/Joint/ZAppendage/Structure |
| src/gui/rendering/Structure.cpp | 结构树实现 | AddAppendage L389、CalcCenter L445、Render L468 |
| src/gui/rendering/StructureReader.hpp | 结构读取器抽象声明 | Execute() 纯虚 |
| src/gui/rendering/StructureReader.cpp | 读取器基类实现 | ctor L30、dtor L37 |
| src/gui/rendering/StructureReader3ds.hpp | 3DS 解析器声明 | chunk 状态成员（Ob4110_Vectors 等） |
| src/gui/rendering/StructureReader3ds.cpp | 3DS chunk 递归解析 | ReadChunk L252、Execute L979、ReadLeInt L941 |
| src/gui/rendering/SurfaceBase.hpp | 网格体系声明 | SurfaceBase/SurfaceGroup/SurfaceMesh/ZFace |
| src/gui/rendering/SurfaceBase.cpp | 网格/面/包围盒实现 | SurfaceGroup::Render L158、SurfaceMesh::BuildNormals L464 |

### 表 7：resource / asset / plugin / function 目录（14 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/resource/GmatIcon.rc | Windows 应用图标资源脚本 | appIcon ICON "GMAT.ico"（L1） |
| src/gui/resource/GmatRc.rc | wx 资源引入脚本 | #include "wx/msw/wx.rc"（L3） |
| src/gui/resource/TrajectoryPlot.rc | 轨迹窗口位图资源 | open/zoomin/zoomout BITMAP（L3-5） |
| src/gui/resource/GMAT.ico | Windows 应用图标（二进制） | — |
| src/gui/resource/GMATIcon.icns | 通用应用图标（二进制） | — |
| src/gui/resource/GMATMac.icns | Mac 应用图标（二进制） | — |
| src/gui/asset/GroundStationPanel.hpp | 地面站面板声明 | theGroundStation/localGroundStation |
| src/gui/asset/GroundStationPanel.cpp | 站属性配置（单位随状态类型切换） | LoadData L310、SaveData L350、UpdateControls L501 |
| src/gui/plugin/WxGuiInterface.hpp | 插件 GUI 接口声明 | Instance、resourceTree |
| src/gui/plugin/WxGuiInterface.cpp | 插件对象创建并登记资源树 | CreateObject L64、CreateGuiElement L100 |
| src/gui/function/FunctionSetupPanel.hpp | GmatFunction 编辑面板声明 | mFileContentsTextCtrl/mEditor |
| src/gui/function/FunctionSetupPanel.cpp | 函数脚本加载/保存 | LoadData L186、SaveData L227、OnSaveAs L340 |
| src/gui/function/MatlabFunctionSetupPanel.hpp | MatlabFunction 面板声明 | mPathTextCtrl/mBrowseButton |
| src/gui/function/MatlabFunctionSetupPanel.cpp | .m 文件路径选择 | LoadData L113、SaveData L126 |

### 表 8：include 目录——头文件（4 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| src/gui/include/DoxygenGuiIntro.hpp | Doxygen mainpage 总览 | \mainpage（L2） |
| src/gui/include/gmatwxdefs.hpp | 全局 wxWidgets 头与版本宏 | STD_TO_WX_STRING/WX_TO_STD_STRING（L98-112） |
| src/gui/include/gmatwxrcs.hpp | 平台图标资源引用 | mondrian.xpm（L31） |
| src/gui/include/ddesetup.hpp | MATLAB DDE 配置 | IPC_SERVICE "4242"（L40-46） |

### 表 9：include/bitmaps 目录（200 个位图/图标文件）

说明：`.xpm` 为 wxWidgets 直接编译的 C 数组文本；`.png/.bmp/.gif/.ico/.icns` 为二进制资源；按命名前缀分类，"职责"列给出类别归属。清单按 glob 结果（`src/gui/include/bitmaps/*`）完整列出：

| 相对路径（均在 src/gui/include/bitmaps/ 下） | 职责 |
| --- | --- |
| BlankIcon.xpm | 空白占位图标 |
| CloseAll.png、CloseAll.xpm、CloseOne.png、CloseOne.xpm | 关闭全部/单个窗口（工具栏） |
| ClosedFolder.xpm、OpenFolder.xpm、folder.xpm、redfolder.xpm | 文件夹图标（资源树/任务树） |
| Copy.png、Cut.png、Paste.png、copy.xpm、cut.xpm、paste.xpm | 复制/剪切/粘贴 |
| DefaultMission.xpm | 默认任务图标 |
| Erase.png、Erase.xpm | 擦除/清除 |
| FasterAnimation.png、FasterAnimation.xpm、PauseAnimation.xpm、RunAnimation.bmp/.gif/.png/.xpm、SlowerAnimation.png/.xpm、StopAnimation.png/.xpm | 动画控制（播放/暂停/停止/快/慢） |
| animation_options.xpm | 动画选项 |
| GMAT.icns、GMATMainIcon.ico | 应用图标（macOS/Windows） |
| Help.png、Help.xpm、WebHelp.png、WebHelp.xpm | 帮助 |
| NewMission.png、NewMission.xpm、SaveMission.png、SaveMission.xpm | 新建/保存任务 |
| NewScript.png、NewScript.xpm、OpenScript.png、OpenScript.xpm | 新建/打开脚本 |
| PauseMission.png、PauseMission.xpm、RunMission.png、RunMission.xpm、StopMission.png、StopMission.xpm | 任务运行控制 |
| Screenshot.png、screenshot.xpm | 截图 |
| WriteInformation.png、WriteInformation.xpm | 信息输出 |
| achieveevent.xpm、propagateevent.xpm、varyevent.xpm、scriptevent.xpm | 命令事件图标 |
| asteroid.xpm、comet.xpm、constellation.xpm、planet_generic.xpm | 小天体/星座 |
| back.xpm、backall.xpm、down.xpm、forward.xpm、up.xpm | 导航方向箭头 |
| beginfb.xpm、endfb.xpm、deltav.xpm、equalsign.xpm | 机动/等号图标 |
| build.xpm、preview.xpm、print.xpm、run.xpm、save.xpm、saveobject.xpm | 构建/预览/打印/运行/保存 |
| coordinatesystem.xpm、network.xpm、openglplot.xpm、matrix.xpm、matlabfunction.xpm | 对象类型图标 |
| earth.xpm、jupiter.xpm、mars.xpm、mercury.xpm、moon.xpm、moon_generic.xpm、neptune.xpm、pluto.xpm、saturn.xpm、sun.xpm、triton.xpm、uranus.xpm、venus.xpm | 天体图标 |
| file.xpm、redfile.xpm | 文件图标 |
| forloop.xpm、if.xpm、whileloop.xpm、nestreturn.xpm、minimize.xpm、optimize.xpm、target.xpm、toggle.xpm | 命令分类图标 |
| mt_CallGmatFunction.xpm、mt_CallMatlabFunction.xpm、mt_ClearPlot.xpm、mt_Default.xpm、mt_FindEvents.xpm、mt_Global.xpm、mt_MarkPoint.xpm、mt_Minimize.xpm、mt_NonlinearConstraint.xpm、mt_Report.xpm、mt_RunEstimator.xpm、mt_RunSimulator.xpm、mt_SaveMission.xpm、mt_SetCommand.xpm、mt_Stop.xpm、mt_WriteCommand.xpm | 命令树图标（mt_ 前缀） |
| mtc_ClearFilters.png、mtc_ClearFilters.xpm、mtc_CustomView.xpm、mtc_ExcCall.xpm、mtc_ExcEquation.xpm、mtc_ExcPlot.xpm、mtc_ExcReport.xpm、mtc_IncControlFlow.xpm、mtc_IncPhysics.xpm、mtc_IncScriptEvent.xpm、mtc_IncSolver.xpm、mtc_L1.xpm、mtc_L2.xpm、mtc_L3.xpm、mtc_LA.xpm | 命令分类树图标（mtc_ 前缀） |
| mondrian.xpm | wx 默认应用图标（见 gmatwxrcs.hpp） |
| pendown.xpm、penup.xpm | 落笔/抬笔（订阅器操作） |
| plot_dwn.xpm、plot_enl.xpm、plot_shr.xpm、plot_up.xpm、plot_zin.xpm、plot_zot.xpm | 绘图窗口工具条 |
| report.xpm | 报告图标 |
| rt_Antenna.xpm、rt_Array.xpm、rt_Barycenter.xpm、rt_BoundaryValueSolver.xpm、rt_ChemicalTank.xpm、rt_ChemicalThruster.xpm、rt_ContactLocator.xpm、rt_CoordinateSystem.xpm、rt_Default.xpm、rt_DifferentialCorrector.xpm、rt_EclipseLocator.xpm、rt_ElectricTank.xpm、rt_ElectricThruster.xpm、rt_EphemerisFile.xpm、rt_Estimator.xpm、rt_FileInterface.xpm、rt_FiniteBurn.xpm、rt_Formation.xpm、rt_GmatFunction.xpm、rt_GroundStation.xpm、rt_GroundTrackPlot.xpm、rt_Hardware.xpm、rt_ImpulsiveBurn.xpm、rt_LibrationPoint.xpm、rt_Matlab.xpm、rt_MatlabFunction.xpm、rt_MatlabServer.xpm、rt_MeasurementModel.xpm、rt_NuclearPowerSystem.xpm、rt_Optimizer.xpm、rt_OrbitView.xpm、rt_Propagator.xpm、rt_Receiver.xpm、rt_ReportFile.xpm、rt_Script.xpm、rt_Simulator.xpm、rt_SolarPowerSystem.xpm、rt_SolarSystem.xpm、rt_Solver.xpm、rt_Spacecraft.xpm、rt_String.xpm、rt_Subscriber.xpm、rt_Tank.xpm、rt_Thruster.xpm、rt_Transmitter.xpm、rt_Transponder.xpm、rt_Variable.xpm、rt_XYPlot.xpm | 资源树类型图标（rt_ 前缀，覆盖全部资源类型） |
| splash.bmp、splash.xpm | 启动画面 |
| open.bmp、zoomin.bmp、zoomin.xpm、zoomout.bmp、zoomout.xpm | 打开/缩放（见 TrajectoryPlot.rc） |

（表 9 共 200 行，与 glob 清单一致；全部文件仅作资源用途，无代码逻辑。）
