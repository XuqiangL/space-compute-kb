# 第9章 GUI 框架、任务树与输出界面

本章范围：`src/gui` 下 `foundation`、`app`、`view`、`mission`、`output`、`debugger`、`controllogic` 七个目录的全部 132 个源码文件（.hpp/.cpp，合计约 7.1 万行）。讲解重点：wxWidgets MDI 框架、GmatApp 启动流程、GmatMainFrame 主窗口（菜单/工具栏/状态栏/Sash 布局）、GmatMdiChildFrame 子窗口模板、GuiItemManager 控件工厂、MissionTree 任务树与 GmatCommand 命令对象双向绑定，以及 output/debugger/controllogic 面板。正文中的行号均经 read 工具逐一确认；未经验证的符号一律不写入。

## 一、本章目录树

```
src/gui/
├── foundation/   GUI 基础框架：面板/对话框基类、控件工厂、输入校验（36 个文件，~22,000 行）
│   ├── GmatPanel / GmatSavePanel / GmatDialog          —— 三种"页面"基类
│   ├── GmatMdiChildFrame                                —— MDI 子窗口模板
│   ├── GuiItemManager / UserInputValidator              —— 控件工厂 + 输入校验器
│   ├── GmatBaseSetupPanel / ArraySetupPanel / ParameterSetupPanel
│   │       / GmatColorPanel / SinglePathSetupPanel / MultiPathSetupPanel
│   ├── ArraySetupDialog / ParameterCreateDialog / ParameterSelectDialog
│   │       / ShowScriptDialog / ShowSummaryDialog
│   └── GmatStaticBoxSizer
├── app/          GUI 应用外壳：主框架、启动、解释器、接收器、服务器（54 个文件，~32,500 行）
│   ├── GmatApp / GmatAppData                            —— 应用入口与全局数据单例
│   ├── GmatMainFrame / GmatMenuBar / GmatToolBar / GmatNotebook
│   ├── GmatTreeItemData / MissionTreeItemData           —— 树节点数据与 ItemType 枚举
│   ├── ResourceTree / ScriptPanel / WelcomePanel
│   ├── GuiInterpreter / GuiPublisher / GuiMessageReceiver / GuiPlotReceiver / GuiListenerManager
│   ├── GmatConnection / GmatServer / GmatSocketServer   —— MATLAB 通信服务
│   └── AboutDialog / CompareFilesDialog / CompareTextDialog / FileUpdateDialog
│           / InteractiveMatlabDialog / RunScriptFolderDialog / SetPathDialog
│           / TextEphemFileDialog
├── view/         脚本编辑器（基于 wxStyledTextCtrl）（14 个文件，~5,100 行）
│   ├── ScriptEditor / EditorPanel / EditorPreferences / EditorPrintout
│   └── FindReplaceDialog / ViewTextFrame / ViewTextDialog
├── mission/      任务树（10 个文件，~7,800 行）
│   ├── MissionTree / DecoratedTree
│   └── MissionTreeToolBar / TreeViewOptionDialog / UndockedMissionPanel
├── output/       输出树与输出面板（8 个文件，~2,000 行）
│   ├── OutputTree
│   └── ReportFilePanel / EventFilePanel / CompareReportPanel
├── debugger/     调试器（6 个文件，~860 行）
│   ├── Breakpoint / DebuggerCommandFactory
│   └── InspectorPanel
└── controllogic/ 控制逻辑命令面板（4 个文件，~1,300 行）
    ├── ConditionPanel（If/While）
    └── ForPanel
```

## 二、逐文件/逐类讲解

### （一）src/gui/foundation —— GUI 基础框架

#### 1. GmatPanel（所有配置面板的基类）

**GmatPanel.hpp / GmatPanel.cpp**

- 职责：所有"对象配置页"（如 SpacecraftPanel、PropagatorPanel）的共同基类，负责统一底部按钮条（OK/Apply/Cancel/Help/Show Script/Command Summary）、sizer 骨架与标准事件流。
- 关键继承：`class GmatPanel : public wxPanel, public UserInputValidator`（GmatPanel.hpp:50）——同时继承 wx 面板与输入校验器，保证所有面板都能用同一套 `CheckReal/CheckInteger/CheckVariable` 校验入口。
- 三个纯虚函数构成子类契约（GmatPanel.hpp:87-89）：`virtual void Create() = 0;`（搭控件）、`virtual void LoadData() = 0;`（把对象数据灌入控件）、`virtual void SaveData() = 0;`（把控件值写回对象）。每个子类都遵循"构造 → Create → Show(LoadData)"三段式。

构造函数要点（GmatPanel.cpp:88-219）：

```cpp
GmatPanel::GmatPanel(wxWindow *parent, bool showBottomSizer, bool showScriptButton)
   : wxPanel(parent)
{
   ...
   theGuiInterpreter = GmatAppData::Instance()->GetGuiInterpreter();
   theGuiManager = GuiItemManager::GetInstance();
   UserInputValidator::SetGuiManager(theGuiManager);
   UserInputValidator::SetWindow(this);
   ...
   thePanelSizer = new wxBoxSizer(wxVERTICAL);
   if (showBottomSizer)
      theMiddleSizer = (wxSizer*)(new wxStaticBoxSizer(wxVERTICAL, this));
   ...
   theOkButton = new wxButton(this, ID_BUTTON_OK, "OK", ...);
   theApplyButton = new wxButton(this, ID_BUTTON_APPLY, GUI_ACCEL_KEY"Apply", ...);
   theCancelButton = new wxButton(this, ID_BUTTON_CANCEL, "Cancel", ...);
   theHelpButton = new wxButton(this, ID_BUTTON_HELP, GUI_ACCEL_KEY"Help", ...);
```

解读：面板不直接持有 Moderator，而是通过 `GmatAppData` 单例取得 `GuiInterpreter`（GUI 侧唯一对 Moderator 的访问通道），并通过 `GuiItemManager::GetInstance()` 取得控件工厂；这两条指针是 foundation 层所有面板的"标准接线"。快捷键 F1（帮助）、F7（显示脚本）、Ctrl+W（取消）在此注册（GmatPanel.cpp:209-214）。

事件流（GmatPanel.cpp）：
- `OnApply`（339 行）：若 `mDataChanged` 为真 → `SaveData()`；成功后 `mdichild->SetDirty(false)`、`theGuiInterpreter->ConfigurationChanged(mObject, true)` 通知 Moderator 配置已变，并回调 `GmatAppData::Instance()->GetMainFrame()->PanelObjectChanged(mObject)` 让主框架同步刷新资源树/任务树。
- `OnOK`（377 行）：先走与 OnApply 相同的保存路径，最后 `CloseActiveChild()` 关闭子窗口。
- `OnCancel`（419 行）：不保存，`SetDirty(false)` 后直接关窗。
- `OnHelp`（434 行）：从 `wxConfigBase` 的 `/Help` 段读对象类型对应的帮助 URL，修正相对路径后用 `wxLaunchDefaultApplication` 打开浏览器。
- `OnScript`（493 行）：弹出对象级脚本（ShowScriptDialog）。

按钮 ID 常量区段（GmatPanel.hpp:125-133）：`ID_BUTTON_OK = 8000` 起，Apply/Cancel/Help/Script/Summary 依次递增。

#### 2. GmatSavePanel（脚本保存面板基类）

**GmatSavePanel.hpp / GmatSavePanel.cpp**

- 职责：在 GmatPanel 基础上增加脚本保存能力，是 ScriptPanel、EditorPanel（脚本编辑器外壳）的直接基类。
- 关键成员：`mFilename/mScriptFilename`、`theSaveButton/theSaveAsButton/theCloseButton`、`mSaveSyncButton/mSaveSyncRunButton`（保存并同步/保存并运行）、`mScriptActiveLabel/mScriptDirtyLabel`（GUI/脚本同步状态指示）。
- 关键虚函数：`OnSave`、`OnSaveAs`、`OnClosePanel`、`OnScript`（GmatSavePanel.hpp:59-62），加上 `UpdateStatusOnClose()`（关闭前询问是否保存）、`ReloadFile()`、`MakeScriptActive()`。`Create/LoadData/SaveData` 仍为纯虚，由 ScriptPanel / EditorPanel 实现。

#### 3. GmatDialog（模态对话框基类）

**GmatDialog.hpp / GmatDialog.cpp**

- 职责：全部模态对话框（ParameterCreateDialog、CompareFilesDialog、SetPathDialog 等）的基类，结构镜像 GmatPanel：`class GmatDialog : public wxDialog, public UserInputValidator`（GmatDialog.hpp:46）。
- 契约纯虚函数（GmatDialog.hpp:68-72）：`Create()/LoadData()/SaveData()/ResetData()`——比 GmatPanel 多一个 `ResetData()`，因为对话框可能被反复打开、需要恢复初始值。
- 按钮 ID 区段 `ID_BUTTON_OK = 8100` 起（GmatDialog.hpp:103-109），与面板的 8000 区段错开，避免事件表冲突。
- `HasDataUpdated()` 供调用方查询数据是否变化；`EnableUpdate()` 控制 OK 键可用性。

#### 4. GmatMdiChildFrame（MDI 子窗口模板）

**GmatMdiChildFrame.hpp / GmatMdiChildFrame.cpp**

- 职责：GMAT 所有"可停靠面板窗口"的统一外壳。任务树双击资源/命令 → `GmatMainFrame::CreateChild()` → 创建 `GmatMdiChildFrame`，其客户区再放具体面板。
- 关键继承：`class GmatMdiChildFrame : public wxMDIChildFrame`（GmatMdiChildFrame.hpp:42）。
- 构造要点（GmatMdiChildFrame.cpp:80-156）：

```cpp
GmatMdiChildFrame::GmatMdiChildFrame(wxMDIParentFrame *parent,
                                     const wxString &name, const wxString &title,
                                     const GmatTree::ItemType type, ...)
{
   relativeZOrder          = maxZOrder++;
   usingSavedConfiguration = false;
   mChildName = name;
   mDirty = false; mOverrideDirty = false; mCanClose = true;
   mCanBeDeleted = true; childIsClosing = false;
   mItemType = type;
   ...
   theGuiInterpreter = gmatAppData->GetGuiInterpreter();
   ...
   #ifdef __CREATE_CHILD_MENU_BAR__
      theMenuBar = new GmatMenuBar(mItemType, parent->GetWindowMenu());
   #else
      theMenuBar = (GmatMenuBar*)(parent->GetMenuBar());
   #endif
   UpdateGuiItem(1, 0);
```

解读：`maxZOrder` 是静态计数器（GmatMdiChildFrame.hpp:112），每个子窗口获得递增的相对 Z 序，用于保存/恢复窗口叠放次序（写入 Subscriber 的 `RelativeZOrder` 参数，见 SaveChildPositionAndSize，565-710 行）。菜单栏默认复用主框架菜单（`__CREATE_CHILD_MENU_BAR__` 未定义时），窗口被激活/关闭时通过 `UpdateGuiItem(updateEdit, updateAnimation)`（782 行）按 `mItemType` 启用/禁用 Edit 菜单与运行工具条——例如只有 `SCRIPT_FILE` 子窗口才启用编辑菜单。

- 关键事件虚函数：`OnActivate`（350 行，激活时置 `mIsActiveChild` 并调 `UpdateActiveChild()`）、`OnIconize`（379 行）、`OnClose`（417-525 行）：

```cpp
void GmatMdiChildFrame::OnClose(wxCloseEvent &event)
{
   SaveChildPositionAndSize();
   GmatSavePanel* panel = ((GmatSavePanel*) GetAssociatedWindow());
   if (panel != NULL)
   {
      if (!panel->UpdateStatusOnClose())
      {
         event.Veto();
         mCanClose = false;
         return;
      }
   }
   GmatAppData::Instance()->GetMainFrame()->RemoveChild(GetName(), mItemType, mCanBeDeleted);
   if (mCanClose)
      childIsClosing = true;
}
```

解读：关闭前先保存窗口位置/大小（输出类窗口写入 Subscriber 参数、任务树窗口与脚本窗口写入 `wxFileConfig` 的 `/MissionTree/`、`/ScriptEditor/` 段），再询问关联面板是否可以关闭（脏脚本会弹保存提示），最后通知主框架从 `theMdiChildren` 列表移除。
- 关键访问器：`GetItemType/SetDataType`（类型驱动菜单与工厂）、`GetScriptTextCtrl/SetScriptTextCtrl`（非 STC 模式下脚本文本控件）、`SetDirty/IsDirty/OverrideDirty`（脏标记）、`SetPluginWidget/GetPluginWidget`（插件窗口）。
- 预留接口：`virtual wxString GetPlotName()`（61 行）等，子类（如 MdiChildViewFrame、MdiChildTsFrame）可覆盖。

#### 5. GuiItemManager（GUI 控件工厂与资源缓存）

**GuiItemManager.hpp / GuiItemManager.cpp**（cpp 7374 行，foundation 最大文件）

- 职责：单例控件工厂 + 全部资源对象的"名称清单缓存"。所有面板需要"选择航天器/坐标系/参数"之类的下拉框、列表框、复选列表框时，都由它创建并自动注册到资源更新监听列表，资源增删后自动刷新。
- 关键继承：`class GuiItemManager : public ItemManager`（GuiItemManager.hpp:50）——ItemManager 是基础库中按对象类型管理资源清单的基类（在 `src/base`，属其他章节）。
- 说明：严格讲它按"控件类别 + 对象类型"创建控件（`GetObjectTypeComboBox`、`GetSpacecraftComboBox`、`GetPropertyListBox` 等，GuiItemManager.hpp:187-395），而"按工厂字符串创建面板"的职责在 `GmatMainFrame::CreateNewResource()` 的 switch 中（见 app 节）。两者合起来构成完整的面板工厂链。

核心机制：
- `GetObjectTypeComboBox(wxWindow*, wxWindowID, const wxSize&, const wxArrayString)`（cpp 2197 行）创建"对象类型"下拉框；其余 `Get*ComboBox/Get*ListBox/Get*CheckListBox` 都遵循同一模式：先查内部缓存列表（如 `theSpacecraftList`），构造控件后把指针与排除列表压入 `mSpacecraftCBList` 等 vector，之后任何 `UpdateAll()` 都会遍历这些 vector 刷新内容。
- `UpdateAll(UnsignedInt objType)`（774 行）：

```cpp
void GuiItemManager::UpdateAll(UnsignedInt objType)
{
   if (objType != Gmat::UNKNOWN_OBJECT)
   {
      switch (objType)   // 只刷新指定类型
      { case Gmat::GROUND_STATION: UpdateGroundStation(true); break; ... }
      return;
   }
   // 全量刷新：依次调用各类型 Update*
   UpdateCelestialPoint(false);
   UpdateFormation(false);
   UpdateSpacecraft(false);
   UpdateBurn(false);
   UpdateParameter(false);
   UpdateSolarSystem(false);
   UpdateCoordSystem(false);
   UpdatePropagator(false);
   ...
}
```

- 资源更新监听（GmatPanel.hpp 视角）：面板调用 `AddToResourceUpdateListeners(this)` 注册，`PrepareObjectNameChange()`/`NotifyObjectNameChange()` 负责对象改名时同步所有已注册控件里的旧名。
- 校验入口：`IsValidParameter/IsValidObjectProperty/IsValidVariable`（IsValidVariable 在 cpp 587 行）把字符串"变量名/对象属性/数组元素"解析为合法参数表达式，供 UserInputValidator 复用。
- 数据精度：`theDataPrecision = GmatGlobal::Instance()->GetDataPrecision()`（cpp 7323 行），`ToWxString(Real)` 用该精度格式化数值。
- 构造函数（7313-7366 行）把所有计数器清零后调 `UpdatePropertyList()` 预建属性名清单。

#### 6. UserInputValidator（输入校验工具）

**UserInputValidator.hpp / UserInputValidator.cpp**

- 职责：供 GmatPanel/GmatDialog 复用的一组"字符串 → 类型 + 范围"校验函数，校验失败时记录错误信息并置 `mIsInputValid = false`。
- 关键方法：`CheckReal/CheckInteger/CheckIntegerRange/CheckRealRange`（含 onlyMsg 只报错模式、checkRange 区间检查、positive/zeroOk 约束）、`CheckVariable`（委托 GuiItemManager::IsValidVariable）、`CheckTimeFormatAndValue`、`IsValidName/CheckFileName/CheckLength`（UserInputValidator.hpp:49-100）。
- 转换工具：`ToWxString/ToReal/ToInteger/ToWxArrayString`（102-108 行）。

#### 7. GmatBaseSetupPanel（通用属性面板）

**GmatBaseSetupPanel.hpp / GmatBaseSetupPanel.cpp**（cpp 1886 行）

- 职责：没有定制面板的对象（如 FuelTank、SOLVER、USER_DEFINED_OBJECT）使用的"自动生成"配置面板：遍历对象的可写参数表，按参数类型自动生成文本框/下拉框/复选列表框，并用 `data/gui_config` 下的 ini 文件（GUI_CONFIG_PATH）控制标签、单位、分组与排序。
- 关键继承：`class GmatBaseSetupPanel : public GmatPanel`（GmatBaseSetupPanel.hpp:68）。
- 核心方法：`BuildControl`（80 行声明）按参数类型分派控件生成；`CreateControls`（83 行）批量创建；`GetParameterLabel/GetParameterUnit`（90-91 行）从 ini 读取标签/单位；`CreateGroups/SortGroups/SortProperties`（93-98 行）实现分组布局；`RefreshProperties/RefreshProperty`（106-109 行）在组合框变化时联动刷新（reloadOnCBChange 开关，构造参数 72 行）。
- 重要成员：`controlMap/inverseControlMap`（参数 ID ↔ 控件双向映射）、`managedComboBoxMap/managedCheckListBoxMap`（交给 GuiItemManager 管理的控件）、`localObject`（提交前在克隆对象上验证改动）。
- 事件：`OnTextUpdate/OnComboBoxChange/OnCheckBoxChange/OnCheckListBoxChange/OnBrowseButton`（112-122 行）。

#### 8. ArraySetupPanel / ParameterSetupPanel（数组与变量面板）

**ArraySetupPanel.hpp / ArraySetupPanel.cpp**

- 职责：数组（ARRAY）对象的编辑面板：`wxGrid` 单元格直接编辑矩阵值，名称/行列数/单个元素值文本框辅助。
- 关键成员：`Rmatrix mRmat`（保存数组值，ArraySetupPanel.hpp:45）、`Parameter *mParam`、`wxGrid *mArrGrid`。`SaveData()` 把网格值写回 Parameter 的 Rmatrix；`CheckCellValue` 校验单元格实数。

**ParameterSetupPanel.hpp / ParameterSetupPanel.cpp**

- 职责：用户变量（VARIABLE）与字符串（STRING）的编辑面板；`mIsStringVar` 区分两种类型（ParameterSetupPanel.hpp:45），`SaveData()` 分别写 `SetRealParameter`/`SetStringParameter`。

#### 9. 路径设置面板

**SinglePathSetupPanel.hpp / SinglePathSetupPanel.cpp**：单条路径（如输出目录）的"文本框 + Browse 按钮"面板；`HasDataChanged()`/`GetFullPathName()`（hpp 41-42 行）供 SetPathDialog 汇总。

**MultiPathSetupPanel.hpp / MultiPathSetupPanel.cpp**：多条路径（GMAT 函数路径、MATLAB 路径）的列表框管理面板：Add/Replace/Remove/Up/Down/Browse 按钮操作 `wxListBox *mPathListBox`（hpp 54-57 行）。

#### 10. 参数与数组对话框

**ArraySetupDialog.hpp / ArraySetupDialog.cpp**：数组编辑对话框版（与 ArraySetupPanel 同构，但继承 GmatDialog 并多 `ResetData()`）。

**ParameterCreateDialog.hpp / ParameterCreateDialog.cpp**（cpp 1466 行）：创建用户变量/数组/字符串的模态对话框。`enum ParameterType { VARIABLE, ARRAY, STRING }`（hpp 44-49 行）；内部用 `wxNotebook` 分三页，`CreateVariable/CreateString/CreateArray`（hpp 147-149 行）分别构造对应 Parameter 并加入 Moderator 配置；`OnOK` 被重写为"Close"语义（hpp 63 行）。

**ParameterSelectDialog.hpp / ParameterSelectDialog.cpp**（cpp 2263 行）：参数选择对话框，是 GMAT 最复杂的对话框之一：对象类型下拉 → 对象列表框 → 硬件/属性联动 → 选中列表，最终拼出参数名（`FormParameterName/FormArrayElement`，hpp 196-197 行）。构造参数多达 16 个（hpp 42-56 行），控制"只显示可绘图参数、允许数组元素、允许多选、用于停止条件"等模式；内部复用一个 `GuiItemManager::CreateParameterSizer` 布局。`SaveData` 后 `GetParamNameArray()` 返回选中参数集。

**ShowScriptDialog.hpp / ShowScriptDialog.cpp**：展示单个对象生成脚本的模态框（GmatDialog 子类），`theScript` 文本控件可选中复制；`showAsSingleton` 控制是否输出 "Create" 行（hpp 57 行）。

**ShowSummaryDialog.hpp / ShowSummaryDialog.cpp**：展示命令摘要（`GmatCommand` 的 summary），`summaryForMission`/`physicsOnly` 支持整任务/仅物理摘要模式（hpp 51 行），带坐标系下拉框与"另存为"按钮。

**GmatColorPanel.hpp / GmatColorPanel.cpp**：SpacePoint 轨道/目标颜色选择子面板（wxColourPickerCtrl），供 SpacecraftPanel 等嵌入；`GetOrbitColor/GetTargetColor` 返回 `UnsignedInt` 颜色值（hpp 57-58 行），与基础库 `GmatColor` 及 PlotInterface 颜色规范对齐。

**GmatStaticBoxSizer.hpp / GmatStaticBoxSizer.cpp**：跨 wxWidgets 版本兼容的静态框 sizer：wx3.0 及非 Mac 上继承 `wxStaticBoxSizer`，老 Mac 上退化为 `wxBoxSizer` + 自绘 `wxStaticText` 标签（hpp 38-42 行），统一 `SetLabel` 接口。

### （二）src/gui/app —— 应用外壳

#### 1. GmatApp（程序入口）

**GmatApp.hpp / GmatApp.cpp**（cpp 1171 行）

- 职责：GMAT GUI 的 wxApp 子类，程序从这里启动。
- 关键宏：

```cpp
// GmatApp.cpp:87
IMPLEMENT_APP(GmatApp)
```

解读：wxWidgets 用该宏在运行时创建全局应用对象并定义 `wxGetApp()` 访问器（返回类型安全的 `GmatApp&` 而非 `wxApp&`），同时生成 `main()`。这是"wxWidgets 程序的入口即 GmatApp::OnInit"的机制根源。

- 类声明（GmatApp.hpp:46-91）：`class GmatApp : public wxApp`，覆写 `virtual bool OnInit()`（56 行）、`int OnExit()`（58 行）、`int FilterEvent(wxEvent&)`（59 行）；私有状态：`theModerator`（70 行）、`theMainFrame`（71 行）、`scriptToRun/buildScript/runScript/runBatch/startMatlabServer/skipSplash`（72-79 行）、`startupMessageBuffer`（83 行，命令行反馈信息缓冲，等 Moderator 就绪后再显示）。
- 构造函数（GmatApp.cpp:92-117）：三件关键接线——

```cpp
GmatApp::GmatApp()
: theMainFrame( NULL )
{
   GuiMessageReceiver *theMessageReceiver = GuiMessageReceiver::Instance();
   MessageInterface::SetMessageReceiver(theMessageReceiver);

   GuiPlotReceiver *thePlotReceiver = GuiPlotReceiver::Instance();
   PlotInterface::SetPlotReceiver(thePlotReceiver);

   GuiListenerManager *theListenerManager = GuiListenerManager::Instance();
   ListenerManagerInterface::SetListenerManager(theListenerManager);

   theModerator = (Moderator *)NULL;
   showMainFrame = true; scriptToRun = ""; ...
}
```

解读：在构造阶段就把三个"接收器"单例挂到基础库的静态接口上——消息、绘图、监听器全部从"控制台实现"切换为"GUI 实现"，之后引擎任意模块 `MessageInterface::ShowMessage(...)` 都会流进 GUI 消息窗口。Linux 下额外 `XInitThreads()` 保证 X11 线程安全（113-116 行）。

- `OnInit()`（127-526 行）——启动主流程：

```cpp
bool GmatApp::OnInit()
{
   wxInitAllImageHandlers();
   SetAppName("GMAT");
   ...
   GmatAppData *gmatAppData = GmatAppData::Instance();
   FileManager *fm = FileManager::Instance();
   std::string startupFile = fm->GetFullStartupFilePath();

   theModerator = Moderator::Instance();
   theModerator->OverridePublisher(GuiPublisher::Instance());   // 用 GUI 发布器
   ...
   StringArray theFiles = CheckForStartupAndLogFile();           // 解析 --startup_file / --logfile
   ...
   if (theModerator->Initialize(startupFileToRead, true))        // 引擎初始化
   {
      FactoryManager::Instance()->RegisterFactory(new DebuggerCommandFactory);  // 注册 Breakpoint 工厂
      GuiInterpreter *guiInterp = GuiInterpreter::Instance();
      theModerator->SetUiInterpreter(guiInterp);
      theModerator->SetInterpreterMapAndSS(guiInterp);
      guiInterp->BuildCreatableObjectMaps();                     // 建立可创建对象/命令清单
      gmatAppData->SetGuiInterpreter(...);
      ...
      // 读个性化配置恢复主窗口位置/大小（Windows）
      ...
      // 闪屏（SPLASH_FILE，4 秒超时）
      ...
      theModerator->LoadDefaultMission();                        // 默认任务
      theMainFrame = new GmatMainFrame((wxFrame *)NULL, -1,
            _T("GMAT - General Mission Analysis Tool"), position, size,
            wxDEFAULT_FRAME_STYLE | wxHSCROLL | wxVSCROLL);
      ...
      theMainFrame->Show(true);
      theMainFrame->ManageMissionTree();
      ...
      if (buildScript && runScript) BuildAndRunScript(true);     // 命令行 --run
      ...
      status = true;
   }
   return status;
}
```

解读：顺序为 ① 单例装配（GmatAppData/Moderator/GuiPublisher）→ ② 命令行参数预解析 → ③ 引擎初始化（读 gmat_startup_file）→ ④ 注册调试命令工厂 → ⑤ 装配 GuiInterpreter → ⑥ 恢复窗口配置/闪屏 → ⑦ 加载默认任务 → ⑧ 创建并显示 GmatMainFrame → ⑨ 命令行脚本构建/运行。任一环节异常被 `BaseException` 捕获后写入消息并返回 false（513-525 行），应用立即退出。

- `OnExit()`（547-568 行）：`theModerator->Finalize()` 收尾，若引擎退出码非 1 则 `exit(exitCode)`。
- `FilterEvent(wxEvent&)`（582-606 行）：全局键事件钩子——F3 转发给 `theMainFrame->OnFindNext`、Ctrl+H 转发 `OnReplaceNext`；返回 1 表示事件已被消费。这让"查找下一个"在编辑器失焦时依然生效。
- `CheckForStartupAndLogFile()`（648-731 行）：从 argv 抓 `--startup_file/-s` 与 `--logfile/-l` 两个参数。
- `ProcessCommandLineOptions()`（738-1052 行）：完整命令行解析——`-h/--help`（用法文本进 startupMessageBuffer）、`-v/--version`、`-r/--run`（置 buildScript+runScript）、`-x/--exit`（`GmatGlobal::SetRunMode(EXIT_AFTER_RUN)`）、`-m/--minimize`（`MINIMIZED_GUI`）、`-n/--nits`（NITS 客户端模式，校验 NITS 插件存在并置 runScript）、`-ns/--no_splash`（跳过闪屏）；裸参数按脚本文件名处理（构建完整路径、校验存在性，943-1041 行）。
- `BuildAndRunScript(bool runScript)`（1058-1147 行）：命令行自动运行路径——`theMainFrame->BuildScript(...)` 后 `theMainFrame->RunCurrentScript()`；`EXIT_AFTER_RUN` 模式下调 `SetAutoExitAfterRun(true)` 并 Close（1132-1146 行）。
- `WriteMessage`（1161-1170 行）：带时间戳的日志写入。

#### 2. GmatAppData（全局数据单例）

**GmatAppData.hpp / GmatAppData.cpp**

- 职责：GUI 全局指针仓库：MainFrame、三棵树（ResourceTree/MissionTree/OutputTree）、消息窗口、字体、个性化配置等，供任何面板/窗口无参获取。
- 单例：`static GmatAppData* Instance()`（cpp 64-72 行），`theGmatAppData` 静态指针（hpp 125 行）。
- 构造函数（cpp 513-547 行）：

```cpp
GmatAppData::GmatAppData()
{
   theMainFrame = NULL; theResourceTree = NULL; theMissionTree = NULL;
   theOutputTree = NULL; theMessageWindow = NULL; theCompareWindow = NULL;
   theMessageTextCtrl = NULL;
   theFontSize = 8; theScriptFontSize = 9;
   theTempScriptName = "$gmattempscript$.script";
   thePersonalizationConfig = NULL; theIconFileSet = false;
   wxFontInfo fontSettings(theFontSize);
   fontSettings.Family(wxFONTFAMILY_MODERN);
   theFont = wxFont(fontSettings);
   theScriptFont = wxFont(fontSettings);
   theScriptFont.SetPointSize(theScriptFontSize);
   wxFileConfig *pConfig = new wxFileConfig(wxEmptyString, wxEmptyString,
         "GMAT.ini", wxEmptyString, wxCONFIG_USE_LOCAL_FILE | wxCONFIG_USE_RELATIVE_PATH);
   wxConfigBase::Set(pConfig);
}
```

解读：字体默认 8 点（wx2.8 兼容），脚本字体 9 点；`GMAT.ini` 局部配置被设为 wx 全局配置。`GetPersonalizationConfig()`（134 行起）懒加载 PERSONALIZATION_FILE 指定的个性化文件（找不到则退回 OS 用户目录默认配置）。
- 图标管理：`SetIconFile()`（479 行）/`ResetIconFile()`（454 行）/`SetIcon(wxTopLevelWindow*, ...)`（hpp 116 行）把启动文件指定的图标应用到顶层窗口。

#### 3. GmatMainFrame（MDI 主框架）

**GmatMainFrame.hpp / GmatMainFrame.cpp**（cpp 7274 行，app 目录最大文件）

- 职责：应用主窗口：菜单栏、工具栏、状态栏、左侧笔记本（Resource/Mission/Output 三页）、底部消息窗口、MDI 子窗口管理、运行控制。
- 关键继承：`class GmatMainFrame : public wxMDIParentFrame`（GmatMainFrame.hpp:77）——整个窗口体系基于 wxWidgets MDI（多文档界面）框架，所有编辑/配置/输出页都是 MDI 子窗口。

构造函数（GmatMainFrame.cpp:320-683）按顺序装配：
1. 菜单栏：`theMenuBar = new GmatMenuBar(GmatTree::UNKNOWN_ITEM, GetWindowMenu())`（Windows 传 Window 菜单，382-385 行）；默认禁用 Edit 菜单（399-400 行，仅脚本子窗口激活时启用）。
2. 状态栏：`CreateStatusBar(4, wxBORDER)`，字段宽 `{1,150,-3,-1}`（412-415 行）。
3. 工具栏：`new GmatToolBar(this, wxTB_FLAT)`（Mac 用 `wxTB_VERTICAL`，430-433 行）。
4. Sash 布局双窗格：底部消息窗 `theMessageWin`（`wxSashLayoutWindow`，455-495 行，内含只读多行 `msgTextCtrl`，最大 320000 字符，513 行）与左侧主窗 `theMainWin`（548-569 行）。
5. 笔记本：`theNotebook = new GmatNotebook(theMainWin, ...)`（574-575 行），并把主框架指针注入三棵树（578-580 行）。
6. 帮助控制器：Windows 用 `wxCHMHelpController` 加载 CHM（614-616 行）。
7. 加速键表（625-634 行）：F5 运行、F10 截图、F9/Shift+F9 动画播放/停止、Ctrl+PageUp/Down 切页、Ctrl+H 查找。
8. 帮助菜单欢迎页：`pConfig->Read("/Main/ShowWelcomeOnStart", ..., "true")` 为真时 `OnHelpWelcome()`（594-602 行）。

MDI 子窗口工厂 `CreateChild(GmatTreeItemData *item, bool restore)`（871-1038 行）是任务树→面板的核心桥：

```cpp
GmatMdiChildFrame* GmatMainFrame::CreateChild(GmatTreeItemData *item, bool restore)
{
   if (IsChildOpen(item, restore)) return NULL;      // 已打开则复用
   GmatTree::ItemType itemType = item->GetItemType();

   if (itemType > GmatTree::BEGIN_OF_RESOURCE &&
       itemType < GmatTree::END_OF_RESOURCE)
      newChild = CreateNewResource(item->GetTitle(), item->GetName(), itemType, obj);
   else if (itemType > GmatTree::BEGIN_OF_COMMAND &&
            itemType < GmatTree::END_OF_COMMAND)
      newChild = CreateNewCommand(itemType, item);
   else if (itemType > GmatTree::BEGIN_OF_CONTROL &&
            itemType < GmatTree::END_OF_CONTROL)
      newChild = CreateNewControl(item->GetTitle(), item->GetName(), itemType, item->GetCommand());
   else if (itemType > GmatTree::BEGIN_OF_OUTPUT &&
            itemType < GmatTree::END_OF_OUTPUT)
      newChild = CreateNewOutput(item->GetTitle(), item->GetName(), itemType);
   else if (itemType == GmatTree::MISSION_TREE_UNDOCKED)
      newChild = CreateUndockedMissionPanel(item->GetTitle(), item->GetName(), itemType);
   ...
   if (newChild != NULL) { PositionNewChild(newChild, numChildren); ... }
   return newChild;
}
```

解读：`GmatTree::ItemType` 枚举的分段（BEGIN_OF_RESOURCE..END_OF_RESOURCE 等，定义在 GmatTreeItemData.hpp:200-403）直接决定分派分支——这就是任务树节点类型驱动面板工厂的第一层。

`CreateNewResource(...)`（4377-4621 行）是第二层：switch 按 itemType 实例化具体面板塞进 `wxScrolledWindow`：

```cpp
wxGridSizer *sizer = new wxGridSizer(1, 0, 0);
GmatMdiChildFrame *newChild = new GmatMdiChildFrame(this, name, title, itemType);
wxScrolledWindow *scrolledWin = new wxScrolledWindow(newChild);

switch (itemType)
{
case GmatTree::ARRAY:
   sizer->Add(new ArraySetupPanel(scrolledWin, name), 0, wxGROW|wxALL, 0);   break;
case GmatTree::GROUND_STATION:
   sizer->Add(new GroundStationPanel(scrolledWin, name), 0, wxGROW|wxALL, 0); break;
case GmatTree::SPACECRAFT:
   sizer->Add(new SpacecraftPanel(scrolledWin, name), 0, wxGROW|wxALL, 0);    break;
case GmatTree::FUELTANK_CHEMICAL:
case GmatTree::FUELTANK_ELECTRIC:
   sizer->Add(new GmatBaseSetupPanel(scrolledWin, name), 0, wxGROW|wxALL, 0); break;
case GmatTree::SCRIPT_FILE:
   { ... newChild->SetEditor(editorPanel->GetEditor()); ... }                break;
...
default:
   sizer->Add(new GmatBaseSetupPanel(scrolledWin, name), 0, wxGROW|wxALL, 0); break;
}
scrolledWin->SetScrollRate(5, 5); scrolledWin->SetAutoLayout(TRUE);
scrolledWin->SetSizer(sizer); sizer->Fit(scrolledWin);
theMdiChildren->Append(newChild);
```

解读：预定义的航天器/测站/推进器等用定制面板；燃料箱、解算器、未识别类型一律落到 `GmatBaseSetupPanel` 兜底（default 分支，4576 行）——这是"无定制面板也能编辑任意对象"的保证。脚本文件则挂 `EditorPanel`（STC 版）或 `ScriptPanel`（文本控件版，`__USE_STC_EDITOR__` 开关，4532-4551 行），并把编辑器指针回填到子窗口。
- `CreateNewCommand`（4843 行）/`CreateNewControl`（4992 行，If/For/While 用 ConditionPanel/ForPanel）/`CreateNewOutput`（5049 行，Report/Event/Compare 输出面板）/`CreateUndockedMissionPanel`（5140 行，任务树脱锚为 MDI 子窗）。
- 插件通道：`CreatePluginChild(title, name, panelType, itemType, forObject, &widget)`（4642-4647 行）与 `GetPluginWidget`（hpp 344-345 行）通过 `GuiFactory`/`GmatWidget` 让插件注册自己的配置面板；`guiFactories` 容器（hpp 343 行）持有插件工厂列表。
- 运行控制链：`OnRun`（3954 行）→ `RunCurrentMission()`（2884 行，`EnableMenuAndToolBar(false,true)` 冻结菜单、`wxYield()` 让 GUI 出时间片、调 `theGuiInterpreter->RunMission(1)`）→ `RunCurrentScript()`（2799 行）→ `BuildAndRunScript(filename, addToResourceTree)`（2821 行，`CloseCurrentProject()` → `InterpretScript(...)` → `RunCurrentMission()`）。`StopRunningMission()`/`ResumeRun()` 对应暂停/继续。
- 脚本解释：`InterpretScript(filename, scriptOpenOpt, closeScript, readBack, ...)`（2529 行）调 GuiInterpreter 解释脚本并按 `GmatGui::ScriptOption`（hpp 67-75 行）决定出错时是否打开脚本。
- 子窗口管理：`GetNumberOfChildOpen`（1099 行，按类型统计）、`RemoveChild`、`CloseAllChildren`、`PositionNewChild/RepositionChildren`（级联平铺新窗口）、`SaveChildPositionsAndSizes`（写配置）。
- 界面状态机：`UpdateMenus(bool openOn)`（5679 行）、`EnableMenuAndToolBar(enable, missionRunning, forAnimation)`（hpp 234 行）、`PanelObjectChanged(GmatBase *obj)`（3183 行，面板保存后刷新资源/任务/输出三棵树）、`ManageMissionTree()`（3360 行，根据 GUI 模式停靠/脱锚任务树）。
- 消息回调：`NotifyRunCompleted()`、`SetAutoExitAfterRun`、`GetHelpController`。

#### 4. GmatMenuBar（菜单栏）

**GmatMenuBar.hpp / GmatMenuBar.cpp**

- 职责：构建并维护主菜单栏；`GmatMenu` 命名空间集中定义全部菜单 ID。
- 构造：`GmatMenuBar(itemType, windowMenu)`（cpp 58-63 行）→ `CreateMenu(itemType, windowMenu)`（77 行起）按 `GmatGlobal::GetRunModeStartUp()` 判断测试模式后组装：
  - File（91-124 行）：New（子菜单 Script/New Mission）、Open、Open Recent、Save、Save As、Print Setup/Print（`__ENABLE_PRINT__`）、Exit。
  - Edit（129-159 行）：Undo/Redo/Cut/Copy/Paste/Comment/Uncomment/Select All，STC 模式下追加 Find/Find Next/Line Numbers/Goto/Indent。
  - Tools（166-174 行）：Compare Files、Generate Text Ephemeris File（测试模式）。
  - Help（180-194 行）：Welcome Page、Help、Using GMAT、Tutorials、Check for Updates、Report an Issue、Feedback、About。
  - Window（233-235 行）：Close All / Close（Windows 上）。
- ID 常量（GmatMenuBar.hpp:50-144）：File=10000 段、Edit=11000 段、Script=12000 段、Tools=13000 段、运行工具=14000 段、动画=15000 段、MATLAB=16000 段、Help=17000 段；`MENU_HELP_ABOUT = wxID_ABOUT`（141 行）保证 Mac 下 About 进 Apple 菜单。
- `UpdateRecentMenu(files)`（cpp 287-305 行）：重建最近脚本子菜单（Ctrl+Shift+1..5 快捷键）。

#### 5. GmatToolBar（主工具栏）

**GmatToolBar.hpp / GmatToolBar.cpp**

- 职责：主窗口工具栏。
- 构造（cpp 70-79 行）：`CreateToolBar(this)` + `AddAnimationTools` + `AddGuiScriptSyncStatus` + `AddAdvancedStatusField` 四段拼装。
- `CreateToolBar`（85-209 行）：17 个 PNG 图标（NewScript/OpenScript/SaveMission/Copy/Cut/Paste/Run/Pause/Stop/CloseAll/CloseOne/NewMission/build/Help/WebHelp/screenshot）按固定顺序入列，按钮 ID 直接复用 GmatMenu 的常量（如 `MENU_FILE_NEW_SCRIPT`、`TOOL_RUN`），因此工具栏按钮与菜单项共享事件处理；初始禁用 Pause/Stop/Screenshot 等（199-201 行）。
- `AddAnimationTools`（221 行）：动画播放/停止/加速/减速/选项按钮，仅 `mAnimationEnabled` 时启用。
- `AddGuiScriptSyncStatus`（303 行）/`AddAdvancedStatusField`（348 行）：工具栏右侧的"GUI↔脚本同步状态"与"高级模式"静态文本。

#### 6. GmatNotebook（左侧三页笔记本）

**GmatNotebook.hpp / GmatNotebook.cpp**

- 职责：主框架左侧的 wxNotebook，承载 Resource/Mission/Output 三棵树（及 Mission 页工具栏）。
- 构造函数（cpp 66-111 行）：

```cpp
GmatNotebook::GmatNotebook(wxWindow *parent, ...)
   : wxNotebook(parent, id, pos, size, style)
{
   panel = CreateResourcePage();      AddPage(panel, wxT("Resources"));
   mMissionPagePanel = CreateMissionPage();  AddPage(mMissionPagePanel, wxT("Mission"));
   GmatAppData::Instance()->SetMissionTree(missionTree);
   missionTree->SetNotebook(this);
   missionTree->AddDefaultMission();  // 默认任务序列进树
   panel = CreateOutputPage();        AddPage(panel, wxT("Output"));
}
```

- `CreateResourcePage`（243-266 行）：new `ResourceTree`（wxTR_HAS_BUTTONS|wxTR_HIDE_ROOT|wxTR_LINES_AT_ROOT|wxTR_SINGLE|wxTR_FULL_ROW_HIGHLIGHT）并注册进 GmatAppData。
- `CreateMissionPage`（277 行起）：MissionTree + MissionTreeToolBar 组合页；`CreateOutputPage`（337 行）：OutputTree。
- 脱锚/回锚：`CreateUndockedMissionPanel()`（143-182 行）用 `GmatTreeItemData("Mission", MISSION_TREE_UNDOCKED)` 经主框架 CreateChild 生成独立 MDI 窗口，然后 `DeletePage(1)` 删掉内嵌 Mission 页；`RestoreMissionPage()`（188-231 行）反向重建。
- `OnNotebookSelChange`（371 行）：页切换时同步刷新树。

#### 7. GmatTreeItemData / GmatTree 命名空间（树节点类型系统）

**GmatTreeItemData.hpp / GmatTreeItemData.cpp**

- 职责：定义树节点的数据类型，以及贯穿全 GUI 的三组图标枚举 + 核心的 `GmatTree::ItemType` 节点类型枚举。
- 四组枚举（hpp 35-404 行）：
  - `ResourceIconType`（39-124 行）：资源树图标，顺序即 `ResourceTree::AddIcons()` 的建图标顺序（注释 37-38 行明示）；`RESOURCE_ICON_COUNT` 收尾。
  - `MissionIconType`（128-177 行）：任务树图标（Propagate/Target/While/For/If/ScriptEvent/Vary/Achieve/...）。
  - `OutputIconType`（180-194 行）：输出树图标。
  - `ItemType`（200-403 行）：节点类型，**分段设计**（注释 197-199 行明确"不要改动顺序，GmatMainFrame::CreateChild 依赖它"）：
    - 资源文件夹段 40000~（RESOURCES_FOLDER...PLUGIN_FOLDER，205-227 行）
    - 资源对象段 `BEGIN_OF_RESOURCE = 41000` 起（SPACECRAFT/GROUND_STATION/HARDWARE/.../SCRIPT_FILE，238-308 行），`END_OF_RESOURCE` 收尾
    - 命令段 `BEGIN_OF_COMMAND = 43000` 起（PROPAGATE/TARGET/OPTIMIZE/.../USER_COMMAND，321-350 行），`END_OF_COMMAND = 43900` 收尾
    - 控制逻辑段 `BEGIN_OF_CONTROL = 44000`（IF_CONTROL/FOR_CONTROL/WHILE_CONTROL/...，353-360 行）
    - 输出段 `BEGIN_OF_OUTPUT = 46000`（OUTPUT_ORBIT_VIEW/OUTPUT_REPORT/OUTPUT_TEXT_EPHEM_FILE/...，372-386 行）
    - 无面板段 `BEGIN_NO_PANEL = 47000`（BEGIN_MISSION_SEQUENCE/STOP/END_TARGET/END_IF_CONTROL/...，389-402 行）
- `GmatTreeItemData` 类（hpp 407-435 行）：`wxTreeItemData` 子类，保存 `mItemName/mItemTitle/mItemType/mIsClonable/mHasPluginGui`；虚函数 `GetCommand()`（默认空实现）与 `GetNodeId()` 供 MissionTreeItemData 覆盖。
- cpp（GmatTreeItemData.cpp:55-58 行）构造体赋值四个成员。

#### 8. MissionTreeItemData（任务树节点数据）

**MissionTreeItemData.hpp / MissionTreeItemData.cpp**

- 职责：任务树节点的数据载体，在 GmatTreeItemData 之上增加 `GmatCommand *theCommand` 与 `wxTreeItemId theNodeId`（hpp 49-50 行）——这是"树节点 ↔ 命令对象双向绑定"的关键数据结构。
- 构造（cpp 48-55 行）：`: GmatTreeItemData(name, type, title, false)` 并把 `mItemTitle = name`（任务树中标题即名称），记录命令指针。
- `GetCommand/SetCommand`（65-80 行）、`GetNodeId/SetNodeId`（85-96 行）。

#### 9. ResourceTree（资源树）

**ResourceTree.hpp / ResourceTree.cpp**（cpp 6837 行）

- 职责：左侧"Resources"页的树：默认资源（太阳系天体、坐标系、航天器、推进器、燃烧、解算器、订阅器等）的层级展示，右键菜单创建/重命名/删除/克隆对象。
- 关键继承：`class ResourceTree : public wxTreeCtrl, public UserInputValidator`（hpp 43 行）。
- 构造函数（cpp 294-356 行）：`CreatePopupMenuMap()` 建右键菜单映射、`RegisterGuiPluginResources()` 注册插件资源、`AddIcons()` 加图标、`AddDefaultResources()` 灌默认资源、最后 `theGuiManager->UpdateAll()` 预建控件清单。
- `CreateObject(objType, objName, createDefault)`（827/846 行）：调 GuiInterpreter 在沙箱中创建对象；`AddObjectToTree(GmatBase *obj)`（1019 行）把对象按类型挂到对应文件夹节点。
- `AddDefaultResources()`（1083 行）→ `AddDefaultBodies/AddDefaultGroundStation/AddDefaultSpacecraft/.../AddDefaultCoordSys/AddDefaultScripts`（hpp 173-190 行），逐个文件夹灌默认对象。
- `UpdateResource(resetCounter, onlyChildNodes)`（441 行）：任务重载后重建资源树。
- 右键菜单：`ShowMenu` + `CreatePopupMenu(itemType, gmatType, subtype)`（hpp 270-276 行）——菜单项按 GmatTree::ItemType 动态组装，插件可经 `AddUserTreeNode/AddUserResources` 追加节点。
- 脚本相关：`AddScriptItem/AddScript`、`MakeScriptActive`、`BuildScript`、脚本文件夹运行（`IsScriptFolderRunning/QuitRunningScriptFolder`，hpp 68-69 行）。
- 拖放克隆：`OnBeginDrag/OnEndDrag`（hpp 205-207 行）；标签编辑 `OnBeginLabelEdit/OnEndLabelEdit`（202-203 行）→ `RenameObject` 经 GuiInterpreter 改名并联动 GuiItemManager。

#### 10. ScriptPanel（脚本编辑外壳，非 STC 版）

**ScriptPanel.hpp / ScriptPanel.cpp**：非 STC 模式的脚本编辑面板：`wxTextCtrl *mFileContentsTextCtrl`（hpp 43 行）+ 行号框 `mLineNumberTextCtrl`；`ClickButton(bool run)` 触发保存/构建/运行；`OnTextUpdate` 统计行号。STC 模式对应的 EditorPanel 位于 `src/gui/view`，见本章 view 节。

#### 11. GuiInterpreter（GUI↔Moderator 桥）

**GuiInterpreter.hpp / GuiInterpreter.cpp**

- 职责：GUI 访问引擎的唯一门面：创建对象/命令、解释脚本、运行任务、刷新三棵树。是 Moderator 的"UI 解释器"（`SetUiInterpreter` 注入）。
- 关键继承：`class GuiInterpreter : public ScriptInterpreter`（hpp 42 行）——脚本解释与对象创建能力继承自 ScriptInterpreter（基础库），GUI 侧补充树刷新与 GUI 反馈。
- 单例：`static GuiInterpreter* Instance()`（hpp 46 行）。
- 对象/命令创建（几乎全部是"转发到 theModerator"的薄封装）：
  - `CreateObject(type, name, manage, createDefault, ...)`（hpp 88-90 行）→ `theModerator->CreateObject(...)`。
  - `CreateDefaultCommand(type, name, refCmd)`（cpp 925-946 行）：

```cpp
GmatCommand* GuiInterpreter::CreateDefaultCommand(const std::string &type,
                                                  const std::string &name,
                                                  GmatCommand *refCmd)
{
   GmatCommand *cmd = theModerator->CreateDefaultCommand(type, name, refCmd);
   #if !defined __CONSOLE_APP__
   GmatMainFrame *mainFrame = GmatAppData::Instance()->GetMainFrame();
   if (cmd == NULL)
      mainFrame->UpdateGuiScriptSyncStatus(3, 0);   // GUI 错误
   else
      mainFrame->UpdateGuiScriptSyncStatus(2, 0);   // GUI 脏
   #endif
   return cmd;
}
```

解读：创建命令后立即更新主框架的 GUI/脚本同步状态指示（3=error, 2=dirty），这是 GUI 状态机与引擎操作耦合的典型点。
  - `AppendCommand/InsertCommand/DeleteCommand/GetFirstCommand`（cpp 953-1011 行）→ Moderator 同名的命令序列操作，任务树增删命令时调用。
- 任务运行：`RunMission(sandboxNum)`（1071-1075 行）先 `SetWidgetCreator(&GuiInterpreter::CreateWidget)`（插件窗口创建器），再转 Moderator。
- 脚本：`InterpretScript(filename, readBack, newPath)`（1133/1170 行）、`SaveScript(filename, mode)`（1188 行）、`GetScript(mode)`（1204 行）。
- 树刷新：`UpdateView(Integer type)`（1259-1267 行）按位掩码 0x01/0x02/0x04 分别刷资源/任务/输出树：

```cpp
void GuiInterpreter::UpdateView(Integer type)
{
   if (type & 0x01) UpdateResourceTree();
   if (type & 0x02) UpdateMissionTree();
   if (type & 0x04) UpdateOutputTree();
}
```

`UpdateResourceTree`（1273 行）先 `CloseAllChildren()` 再 `UpdateResource(true)`；`UpdateMissionTree`（1287 行）调 `UpdateMission(true)`；`UpdateOutputTree`（1298 行）调 `UpdateOutput(false, true, true)`。
- GUI 控制虚函数：`SetInputFocus/NotifyRunCompleted/UpdateView/CloseCurrentProject/ResetIconFile`（hpp 183-188 行）——这些是 Moderator 回调 GUI 的虚接口。
- `GetListOfFactoryItems/GetListOfAllFactoryItems`（hpp 60-65 行）：查询工厂可创建对象清单（MissionTree 构造时用它取可显示命令列表）。
- 构造函数（cpp 1348-1354 行）调 `ScriptInterpreter::Initialize()`。

#### 12. 消息/绘图/监听接收器

**GuiMessageReceiver.hpp / GuiMessageReceiver.cpp**：`MessageReceiver` 子类单例，把引擎 `MessageInterface` 的输出接到 GUI 消息窗口：`ShowMessage`（写 `msgTextCtrl`，超长截断）、`PopupMessage(msgType, ...)`（按 Gmat::MessageType 弹窗）、`LogMessage`（写日志文件）、`GetMessage/PutMessage/ClearMessageQueue`（hpp 74-76 行，队列缓冲）。

**GuiPlotReceiver.hpp / GuiPlotReceiver.cpp**（cpp 2667 行）：`PlotReceiver` 子类单例，把引擎绘图接口接到 GUI 绘图窗口：OpenGL 轨道视图（`CreateGlPlotWindow/UpdateGlPlot/SetGl3dDrawingOption/...`）、XY 图（`CreateXyPlotWindow/AddXyPlotCurve/XyPlotPenUp/UpdateXyPlot/...`）、动态数据显示（`CreateDynamicDataDisplay/UpdateDynamicDataDisplay`）、地面轨迹（`CreateGroundTrackWindow/UpdateGroundTrackData`）四族接口（hpp 52-221 行）。实际窗口由绘图插件（OpenGL 等）创建，此处负责调用 `GmatMainFrame::CreateChild` 打开输出子窗口并转发数据。

**GuiListenerManager.hpp / GuiListenerManager.cpp**：`ListenerManager` 子类单例，创建求解器监听窗口：`CreateSolverListener(tableName, oldName, positionX, ...)`（cpp 100 行）按名称映射复用已打开的监听窗口（`nameMap`，hpp 62 行）。

**GuiPublisher.hpp / GuiPublisher.cpp**：`Publisher` 子类单例（`Instance()` 返回 `Publisher*`，cpp 45-53 行），在基础发布器之上叠加节流后的 `wxYield()`：`Publish(...)` 转发后调 `Ping()`（cpp 102-109 行），`Ping()` 用 `wxStopWatch yieldStopWatch` 每约 33ms 让出一次事件循环，保证长时间传播时 GUI 仍响应（hpp 42-44 行注释明示设计意图）。

#### 13. MATLAB 通信：GmatConnection / GmatServer / GmatSocketServer

**GmatConnection.hpp / GmatConnection.cpp**：`wxConnection` 子类，wxIPC 服务端连接：`OnExec(topic, data)`（cpp 76 行）→ `RunRequest`（278 行）把脚本交给 Moderator 执行；`OnPoke`（90 行）→ `RunPoke`（327 行）处理变量赋值；`OnRequest/OnStartAdvise/OnDisconnect` 支撑双工通信。

**GmatServer.hpp / GmatServer.cpp**：`wxServer` 子类：`OnAcceptConnection(topic)` 创建 `GmatConnection`；`GetConnection()/Disconnect()` 管理当前连接。主框架的 `StartMatlabServer()` 用它监听 MATLAB 客户端。

**GmatSocketServer.hpp / GmatSocketServer.cpp**：TCP socket 版服务器（端口 3000，`TCP_PORT` 宏 hpp 56 行；Windows winsock2 / Linux pthread 双实现）：`RunServer()` 监听、`StaticOnAccept/OnAccept` 线程化处理连接、`OnRequest/OnPoke` 解析命令；通过 `ID_SOCKET_POKE/ID_SOCKET_REQUEST`（hpp 122-124 行）向 `wxEvtHandler* evthandler` 转发事件。

#### 14. 应用级对话框

**AboutDialog.hpp / AboutDialog.cpp**：`wxDialog`，"关于 GMAT"：版本信息 + `wxHyperlinkCtrl` 许可链接。

**CompareFilesDialog.hpp / CompareFilesDialog.cpp**：批量比较文件对话框：基准目录 + 比较目录 + 容差 + 跳过空行/保存结果选项；`GetCompareTolerance()/GetNumDirsToCompare()/GetCompareDirectories()`（hpp 42-53 行）输出比较参数。

**CompareTextDialog.hpp / CompareTextDialog.cpp**：文本/数值逐行比较对话框（OutputTree 右键 Compare 触发），`mIsNumericCompare`（hpp 102 行）区分文本/数值模式。

**FileUpdateDialog.hpp / FileUpdateDialog.cpp**：`wxDialog` + `IFileUpdater`（基础库接口）：显示待更新文件网格，`InitializeFiles()/GenerateBatchFile()`（hpp 52-54 行）批量更新。

**InteractiveMatlabDialog.hpp / InteractiveMatlabDialog.cpp**：交互式 MATLAB 对话框：输入/输出 `wxGrid` + 函数下拉框，`SetupCommand()/SetResults()`（hpp 84-85 行）构造 `CallFunction` 命令完成参数传递。

**RunScriptFolderDialog.hpp / RunScriptFolderDialog.cpp**：脚本文件夹批量运行对话框：起始序号/数量/过滤字符串/容差/比较目录等；`GetFilterString(bool &exclude)`（hpp 43 行）等 getter 供 ResourceTree 执行批量任务。

**SetPathDialog.hpp / SetPathDialog.cpp**：`SetPathDialog : GmatDialog`，组合 `MultiPathSetupPanel`（GMAT 函数路径、MATLAB 路径）与 `SinglePathSetupPanel`（输出目录）到 `wxNotebook *mPathNotebook`（hpp 48-51 行），`SaveData()` 把路径写回 FileManager。

**TextEphemFileDialog.hpp / TextEphemFileDialog.cpp**：文本星历文件生成对话框：文件路径/时间间隔/坐标系/历元格式/航天器选择，`CreateTextEphem()`（hpp 85 行）生成。

**WelcomePanel.hpp / WelcomePanel.cpp**：`wxFrame` 欢迎页：从 `welcome_page.ini`（wxFileConfig）读分组链接（最近脚本/样例/帮助），`FillGroup(...)`（hpp 53-55 行）生成 `wxFlexGridSizer` 的超链接组；`OnOpenRecentScript/OnOpenHelpLink/OnOpenSampleScript` 处理跳转。

### （三）src/gui/view —— 脚本编辑器

#### 1. ScriptEditor（STC 脚本编辑器）

**ScriptEditor.hpp / ScriptEditor.cpp**（cpp 2390 行）

- 职责：基于 `wxStyledTextCtrl`（Scintilla）的 GMAT 脚本编辑器：GMAT 语言词法高亮、代码折叠、行号、括号匹配、查找替换、注释/取消注释、缩进等。
- 关键继承：`class ScriptEditor: public wxStyledTextCtrl`（ScriptEditor.hpp:41）；`friend class EditorProperties; friend class EditorPrint;`（43-44 行）允许偏好/打印类访问私有成员。
- 构造（cpp 118 行）：设置行号边距、折叠边距、Tab 宽度；`UserSettings(filename)`/`DeterminePrefs(filename)`（hpp 109/131 行）按扩展名选语言。
- 语言/词法配置：`InitializePrefs(const wxString &name)`（cpp 1485-1584 行）：

```cpp
bool ScriptEditor::InitializePrefs(const wxString &name)
{
   StyleClearAll();
   GmatEditor::LanguageInfoType const* curInfo = NULL;
   bool found = false;
   for (int index = 0; index < GmatEditor::globalLanguagePrefsSize; index++)
   {
      curInfo = &GmatEditor::globalLanguagePrefs[index];
      if (curInfo->name == name) { found = true; break; }
   }
   if (!found) return false;
   SetLexer(curInfo->lexer);
   mLanguage = curInfo;
   SetMarginType(mLineNumberID, wxSTC_MARGIN_NUMBER);
   StyleSetForeground(wxSTC_STYLE_LINENUMBER, wxColour(_T("DARK GREY")));
   SetMarginWidth(mLineNumberID, mLineNumberMargin);
   ...
   for (index = 0; index < STYLE_TYPES_COUNT; index++)
   {
      int styleType = curInfo->styles[index].type;
      if (styleType == -1) continue;
      const GmatEditor::StyleInfoType &curType = GmatEditor::globalStylePrefs[styleType];
      ...
      StyleSetBold(index, (curType.fontstyle & GMAT_STC_STYLE_BOLD) > 0);
      StyleSetItalic(index, (curType.fontstyle & GMAT_STC_STYLE_ITALIC) > 0);
      ...
   }
}
```

解读：语言（GMAT 脚本）的 lexer、各 style 类型（关键字/注释/字符串/数字...）的前景/背景/字体/加粗等全部来自 `GmatEditor::globalLanguagePrefs/globalStylePrefs` 静态表（定义于 EditorPreferences.cpp）；编辑器启动时用当前配置对象的可创建对象/命令名生成关键字列表（`mObjCreatablesArray/mCmdCreatablesArray`，hpp 159-160 行）。
- 语法高亮：`ApplySyntaxHighlight(int fromPos, int toPos)`（cpp 1666 行）+ `OnStyleNeeded` 惰性分块着色；`ApplyFoldLevels` 计算折叠层。
- 文件操作：`LoadFile()/SaveFile()`（cpp 2260/2289 行）、`IsModified()`；`OnTextChange` 里回调父 GmatSavePanel 置脏并更新行号。
- 编辑事件族：`OnFind/OnFindNext/OnReplaceNext/OnReplaceAll/OnGoToLine/OnBraceMatch/OnIndentMore/OnIndentLess/OnComment/OnUncomment` 等（hpp 61-106 行）。
- STC 专属事件：`OnMarginClick`（折叠箭头）、`OnCharAdded`（自动缩进）、`OnStyleNeeded`（着色请求）。
- ID 区段 `STC_ID_PROPERTIES = 18000` 起（hpp 178-234 行）。

#### 2. EditorPanel（脚本编辑外壳，STC 版）

**EditorPanel.hpp / EditorPanel.cpp**：STC 模式（`__USE_STC_EDITOR__`）下脚本编辑子窗口内的面板：`class EditorPanel: public GmatSavePanel`（EditorPanel.hpp:39），内部持有 `ScriptEditor *mEditor`（hpp 52 行）；`Create/LoadData/SaveData` 实现 GmatSavePanel 契约；`ClickButton(bool run)`（hpp 49 行）触发保存/构建/运行；`OnSyncButton/OnSyncRunButton`（同步到 GUI / 同步并运行）。`GmatMainFrame::CreateNewResource` 的 `SCRIPT_FILE` 分支（GmatMainFrame.cpp:4540）用它创建面板并把 `GetEditor()` 回填给 GmatMdiChildFrame。

#### 3. EditorPreferences（编辑偏好与语言表）

**EditorPreferences.hpp / EditorPreferences.cpp**：定义 `namespace GmatEditor` 的三张全局表与样式位：
- `CommonInfoType`（hpp 104-119 行）：功能开关（syntaxEnable/foldEnable/indentEnable...）与显示开关（lineNumberEnable/wrapModeInitial...）。
- `LanguageInfoType`（124-135 行）：语言名、文件模式、lexer 号、`styles[STYLE_TYPES_COUNT]`（每个 style 的 type + 关键字串）、folds 位。
- `StyleInfoType`（140-154 行）：名称、前景/背景、字体名/字号、`fontstyle` 位（BOLD=1/ITALIC=2/UNDERL=4/HIDDEN=8，hpp 77-80 行）、lettercase、`foregroundRGB`（"Custom" 时用 RGB）。
- `extern const` 全局表声明（hpp 156-160 行）由 cpp 提供数据；STYLE_TYPES_COUNT=32（hpp 38 行）。

#### 4. EditorPrintout（编辑器打印）

**EditorPrintout.hpp / EditorPrintout.cpp**：`wxPrintout` 子类，把 `ScriptEditor` 内容分页打印：`OnPrintPage/OnBeginDocument/HasPage/GetPageInfo`（hpp 42-47 行），`PrintScaling(wxDC*)` 做 DC 缩放。

#### 5. FindReplaceDialog（查找替换对话框）

**FindReplaceDialog.hpp / FindReplaceDialog.cpp**：查找/替换对话框：`mFindComboBox/mReplaceComboBox` 记忆历史（`mFindArray/mReplaceArray`，hpp 58-59 行），按钮 Find Next/Find Prev/Replace/Replace All/Close 回调 `mEditor`（`SetEditor`，hpp 52 行）的对应事件处理器。

#### 6. ViewTextFrame / ViewTextDialog（文本查看窗口）

**ViewTextFrame.hpp / ViewTextFrame.cpp**：`wxFrame` 文本窗口（消息窗口、比较窗口的载体）：`AppendText/GetNumberOfLines/ClearText`（hpp 47-53 行）；`mWindowMode`（"Permanent"/"Temporary"，hpp 83-84 行）决定关闭后是否保留。
**ViewTextDialog.hpp / ViewTextDialog.cpp**：`wxDialog` 版文本查看（可编辑模式 `isEditable`，hpp 61 行）；`HasTextChanged/GetText`（hpp 51-52 行）。

### （四）src/gui/mission —— 任务树

#### 1. DecoratedTree（带装饰列的树控件）

**DecoratedTree.hpp / DecoratedTree.cpp**

- 职责：wxTreeCtrl 的扩展，在树节点右侧绘制"装饰列"（文本框），用于显示附加信息（目标器变量数/目标数等）。源自 Thinking Systems 的单元测试框架。
- `enum treeDecorations { DRAWOUTLINE, DRAWBOXES, BOXCOUNT, BOXWIDTH, PARMCOUNT }`（hpp 68-74 行）作为 `SetParameter(int id, int value)`（hpp 111 行）的参数。
- 自绘：`OnPaint`（hpp 116 行）覆写后调 `DrawOutline/DrawBoxes`（138-139 行）在行右侧画框写 `boxData`（hpp 131-132 行）文本。注释中自陈若干 bug（hpp 42-51 行：装饰串越界、索引语义不直观等）。
- MissionTree 继承它获得 `ExpandAll/Find/AddItem` 等工具方法。

#### 2. MissionTree（任务树）

**MissionTree.hpp / MissionTree.cpp**（cpp 5549 行）

- 职责：左侧"Mission"页的核心：把 Moderator 中的命令序列（GmatCommand 链表）可视化为树；右键菜单实现追加/插入/删除命令；节点编辑直接改命令对象；双击节点打开对应配置面板。这是"GUI 操作 ↔ 引擎命令对象双向绑定"的枢纽。
- 关键继承：`class MissionTree : public DecoratedTree`（MissionTree.hpp:52）。
- 构造函数（cpp 217-327 行）：

```cpp
MissionTree::MissionTree(...) : DecoratedTree(...), inScriptEvent(false), ...
{
   theGuiInterpreter = GmatAppData::Instance()->GetGuiInterpreter();
   theGuiManager = GuiItemManager::GetInstance();
   mViewAll = true; mUsingViewLevel = true; mViewLevel = 10;
   ...
   StringArray cmds = theGuiInterpreter->GetListOfViewableCommands();  // 可显示命令清单
   for (unsigned int i = 0; i < cmds.size(); i++)
   {
      #ifndef __ENABLE_NAV_GUI__
      if (cmds[i] == "RunSimulator" || ...) continue;
      #endif
      mCommandList.Add(cmds[i].c_str());
   }
   mCommandListForViewControl = mCommandList;
   mCommandListForViewControl.Add("For"); ... Add("Vary"); ...
   CreateCommandIdMap();       // 命令类型 -> 菜单 ID 映射
   CreateCommandCounterMap();  // 命令类型 -> 计数器映射（自动命名 Propagate1...）
   InitializeCounter();
   AddIcons();
   ...
}
```

解读：`mCommandList` 来自 GuiInterpreter 的工厂清单（即"哪些命令可以添加到任务序列"）；`mCommandListForViewControl` 额外含控制流命令（视图过滤用）。`cmdCounterMap`（hpp 320 行）为每个命令类型维护序号，用于未命名命令自动取名。
- 树 ↔ 命令绑定（核心数据流）：`UpdateMission(resetCounter, viewAll, collapse)`（406-431 行）→ `ClearMission()` + `UpdateCommand()`；`UpdateCommand()`（1070-1127 行）：

```cpp
void MissionTree::UpdateCommand()
{
   GmatCommand *cmd = theGuiInterpreter->GetFirstCommand();
   MissionTreeItemData *seqItemData =
      (MissionTreeItemData *)GetItemData(mMissionSeqSubId);
   wxTreeItemId node;
   if (cmd->GetTypeName() == "NoOp")
      seqItemData->SetCommand(cmd);
   while (cmd != NULL)
   {
      node = BuildTreeItem(mMissionSeqSubId, cmd, 0, isLastItemHidden);
      child = cmd->GetChildCommand(0);        // 分支命令的子命令
      if (child != NULL)
         ExpandChildCommand(node, cmd, 0);     // 递归展开 Target/While 等分支
      cmd = cmd->GetNext();                    // 沿命令链表前进
   }
   Expand(mMissionSeqSubId);
}
```

解读：任务树完全从命令链表"重建"：`GetFirstCommand()`（链表头 NoOp 哨兵）→ 沿 `GetNext()` 遍历，分支命令经 `GetChildCommand(0)` 递归。每个节点挂 `MissionTreeItemData`，其中持有该命令的真实指针。
- `AppendCommand(parent, icon, type, cmd, cmdCount)`（1338-1440 行）——建节点并反写命令：

```cpp
wxString cmdTypeName = cmd->GetTypeName().c_str();
wxString nodeName = cmd->GetName().c_str();
...
if (nodeName.Trim() == "" || nodeName == cmdTypeName)
   nodeName.Printf("%s%d", cmdTypeName.c_str(), cmdCount);
...
nodeName = GetCommandString(cmd, nodeName);        // 详细模式下显示命令串
cmd->SetSummaryName(nodeName.c_str());             // ★ 反写命令的摘要名
node = AppendItem(parent, nodeName, icon, -1,
                  new MissionTreeItemData(nodeName, type, nodeName, cmd));
return node;
```

解读：未命名命令按"类型名+计数"自动命名（Propagate1、Target1...），再把显示名写回 `cmd->SetSummaryName`——树标签与命令对象互相同步（GMT-209 的嵌套分支 End 命名问题在此处用 `branch->GetSummaryName()` 推导，1379-1393 行）。
- 增删命令（全部经 GuiInterpreter 落盘到沙箱）：
  - `Append(cmdTypeName)`（2040 行起）：右键"Append"——找当前节点/分支末端的 `prevCmd`（BranchCommand 用 `GmatCommandUtil::GetMatchingEnd()` 找匹配 End，2134 行；有 Else 时插到 Else 前，2138-2147 行）→ `CreateCommand`（650-679 行，经 `theGuiInterpreter->CreateDefaultCommand` 造对象）→ `InsertCommandToSequence(currCmd, prevCmd, cmdToInsert)`（738 行）调 GuiInterpreter::InsertCommand。
  - `InsertBefore`（2288 行）/`InsertAfter`（2462 行）：同类，方向不同。
  - `DeleteCommand(cmdName)`（2595 行）：从树删节点并 `GuiInterpreter::DeleteCommand`。
  - `CreateEndCommand(cmdTypeName, endType)`（685-732 行）：为 Target/For/While/If/ScriptEvent/Optimize 自动生成对应 End 命令。
- 节点行为：`OnItemRightClick`（2979 行）→ `ShowMenu(id, pt)`（3065 行）按节点类型组菜单（`CreateSubMenu/CreateTargetSubMenu/CreateOptimizeSubMenu/CreateControlLogicSubMenu`，hpp 209-213 行）；`OnItemActivated`/`OnDoubleClick`（2999/3017 行）→ `OpenItem(currId)`（4266-4285 行）：

```cpp
void MissionTree::OpenItem(wxTreeItemId currId)
{
   MissionTreeItemData *item = (MissionTreeItemData *)GetItemData(currId);
   MissionTreeItemData *parent = (MissionTreeItemData *)GetItemData(GetItemParent(currId));
   // Vary 在 Optimize 下时改为 OPTIMIZE_VARY 类型以选对面板
   if ((item->GetItemType() == GmatTree::VARY) &&
       (parent->GetItemType() == GmatTree::OPTIMIZE))
      item->SetItemType(GmatTree::OPTIMIZE_VARY);
   theMainFrame->CreateChild(item);   // 交给主框架工厂建面板
}
```

- 命名/计数：`ComposeNodeName`（4291 行）、`GetCommandString`（4335 行，`mShowDetailedItem` 时用 `cmd->GetGeneratingString(Gmat::NO_COMMENTS)` 做标签）、`ResetCommandCounter`（4634 行）、`CreateCommandIdMap/CreateCommandCounterMap/CreateMenuIds`（4455/4475/4514 行）——命令类型到 `MT_BEGIN_APPEND=1000..MT_END_APPEND=1999`（插入前后各 1000 个槽位）菜单 ID 的映射（hpp 311-318 行）。
- 视图控制：`SetViewAll/SetViewLevel/SetViewCommands`（543/552/582 行）配合 MissionTreeToolBar 过滤显示；`ChangeNodeLabel`（463 行）对象改名后更新标签；`PanelObjectChanged`（4611 行）。
- 默认任务：`AddDefaultMission()`（2784 行）→ `AddDefaultMissionSeq`（2833 行）插入 NoOp + BeginMissionSequence 骨架。
- 调试自测：`__TEST_MISSION_TREE_ACTIONS__` 宏下支持动作录制/回放（`WriteActions/WriteResults`，hpp 257-272 行）。
- 菜单 ID 枚举：`MT_RUN=100` 起、`MT_CONTROL_LOGIC=400`、`MT_BEGIN_APPEND=1000` 等（hpp 278-318 行）。

#### 3. MissionTreeToolBar（任务树视图工具栏）

**MissionTreeToolBar.hpp / MissionTreeToolBar.cpp**：任务树顶部的视图控制条：按层级查看（All/1/2/3 级）、按类别包含/排除（Physics/Solver/Script/Control 与 Report/Equation/Plot/Call）、自定义视图（`OnCustomView`，cpp 562 行 → TreeViewOptionDialog）。`SetMissionTreeExpandLevel`（cpp 133 行）联动 MissionTree::SetViewLevel。

#### 4. TreeViewOptionDialog（自定义视图对话框）

**TreeViewOptionDialog.hpp / TreeViewOptionDialog.cpp**：`wxDialog`：`mViewRadioBox`（按层级/按类别）+ `mViewCheckListBox`（命令清单多选）+ Check All/Uncheck All/Apply（hpp 58-61 行）。

#### 5. UndockedMissionPanel（脱锚任务面板）

**UndockedMissionPanel.hpp / UndockedMissionPanel.cpp**：任务树脱锚为独立 MDI 子窗口时的外壳：`GmatPanel` 子类，内含 `MissionTree *mMissionTree` 与 `MissionTreeToolBar *mMissionTreeToolBar`（hpp 63-64 行）；`Create()`（cpp 130 行）重建树与工具栏；`OnClose` 时经 GmatNotebook::RestoreMissionPage 回锚。

### （五）src/gui/output —— 输出界面

#### 1. OutputTree（输出树）

**OutputTree.hpp / OutputTree.cpp**

- 职责：左侧"Output"页的树：Report/TextEphem/OrbitView/GroundTrack/XYPlot/Events 六类输出节点的生命周期管理。
- 关键继承：`class OutputTree : public wxTreeCtrl`（hpp 41 行）——注意没有 UserInputValidator（输出节点只读为主）。
- 构造函数（cpp 85-108 行）：`AddIcons()` + `AddDefaultResources()` + `theGuiManager->UpdateAll()`。
- `RemoveItem(type, name, forceRemove)`（cpp 122-210 行）：

```cpp
void OutputTree::RemoveItem(GmatTree::ItemType type, const wxString &name, bool forceRemove)
{
   wxTreeItemId parentId;
   switch (type)
   {
   case GmatTree::OUTPUT_ORBIT_VIEW:       parentId = mOrbitViewItem; break;
   case GmatTree::OUTPUT_GROUND_TRACK_PLOT:parentId = mGroundTrackItem; break;
   case GmatTree::OUTPUT_XY_PLOT:          parentId = mXyPlotItem; break;
   case GmatTree::OUTPUT_TEXT_EPHEM_FILE:
   case GmatTree::OUTPUT_REPORT:
   case GmatTree::OUTPUT_EVENT_REPORT:
      if (!forceRemove) return;   // 默认保留报告，供运行后查看
      ...
   }
   wxTreeItemId itemId = FindItem(parentId, name);
   if (itemId.IsOk()) { if (GetChildrenCount(parentId) == 1) Collapse(parentId); Delete(itemId); }
}
```

解读：报告的删除默认被拒绝（`forceRemove=false`），保证运行结束后用户仍能查看报告文件。
- `UpdateOutput(resetTree, removeReports, removePlots)`（266 行）：任务重载时按标志清空并重建输出节点。
- 右键菜单：`OnCompareTextLines/OnCompareNumericLines/OnCompareNumericColumns`（hpp 83-85 行）触发报告对比（CompareTextDialog + ViewTextFrame 展示结果）。

#### 2. ReportFilePanel（报告文件查看面板）

**ReportFilePanel.hpp / ReportFilePanel.cpp**：`wxPanel`：只读多行文本控件显示 ReportFile 内容（`mFileContentsTextCtrl`，hpp 60 行），Close/Help/Copy/Select All 按钮与右键菜单；`LoadData()` 从 `theReport`（ReportFile*，hpp 83 行）读当前内容。

#### 3. EventFilePanel（事件文件面板）

**EventFilePanel.hpp / EventFilePanel.cpp**：`wxPanel`：显示 EventLocator 输出的事件文件（`theLocator`，EventLocator*，hpp 79 行），结构同 ReportFilePanel。

#### 4. CompareReportPanel（比较报告面板）

**CompareReportPanel.hpp / CompareReportPanel.cpp**：`wxPanel`：文件对比结果文本显示（`AppendText/GetTextCtrl`，hpp 40-48 行），由 GmatMainFrame 的比较流程（CompareTextDialog 之后）挂载到输出子窗口。

### （六）src/gui/debugger —— 调试器

#### 1. Breakpoint（断点命令）

**Breakpoint.hpp / Breakpoint.cpp**

- 职责：一个 GmatCommand 子类命令 "Breakpoint"：执行到它时弹出 InspectorPanel，暂停任务供用户单步检查。命令序列初始化（Moderator 头部 NoOp 之后）放入任务。
- 关键继承：`class Breakpoint : public GmatCommand`（Breakpoint.hpp:45）；静态成员 `static InspectorPanel *debugger`（hpp 72 行）保证同一时刻只有一个调试器。
- `Execute()`（cpp 120-137 行）：

```cpp
bool Breakpoint::Execute()
{
   BuildCommandSummary();
   if (debugger == NULL)
   {
      debugger = new InspectorPanel();
      debugger->SetCommand(GetPrevious());   // 让检查器看"上一条命令"
      debugger->ShowModal();                 // 模态阻塞直到用户 Resume/End
      ClearDebugger();
   }
   else
      debugger->SetCommand(GetPrevious());
   return true;
}
```

- `GetGeneratingString`（163-171 行）返回空串——断点不写入脚本文件（脚本中无对应语法）。
- `GetObjectData(objName)`（174-182 行）：查询运行时对象并弹窗显示其生成串。
- `DEFAULT_TO_NO_CLONES / DEFAULT_TO_NO_REFOBJECTS`（hpp 68-69 行）禁用克隆与引用对象注册（调试命令不需要）。

#### 2. DebuggerCommandFactory（调试命令工厂）

**DebuggerCommandFactory.hpp / DebuggerCommandFactory.cpp**：`Factory(Gmat::COMMAND)` 子类（cpp 36-40 行），`creatables.push_back("Breakpoint")`；`CreateCommand(ofType, withName)`（cpp 75-82 行）返回 `new Breakpoint`。在 `GmatApp::OnInit` 中 `FactoryManager::RegisterFactory(new DebuggerCommandFactory)`（GmatApp.cpp:222）注册——这是唯一在 GUI 侧注册的引擎命令工厂。

#### 3. InspectorPanel（对象检查器）

**InspectorPanel.hpp / InspectorPanel.cpp**：`wxDialog`（模态）：
- 构造（cpp 56-151 行）：`theModerator = Moderator::Instance(); theInterpreter = theModerator->GetUiInterpreter();`；布局含"Spacecraft Only/All Objects"单选、"对象选择"下拉（`choices`）、右侧只读脚本文本（`theScript` 显示所选对象生成串）、Step/Resume Run/End Run 三按钮；最后 `theInterpreter->ChangeRunState("Pause")`（150 行）把运行置为暂停。
- `SetCommand(GmatCommand *cmd)`（153-158 行）：显示当前命令的生成串。
- `Step`（171 行起）：`currentcmd = currentcmd->GetNext()` 前进一步（BranchCommand 分支处理），到末尾则 `theMainFrame->OnStop(event)` 并 Destroy；否则 `theInterpreter->ChangeRunState("Step")` 继续。
- `PopulateLists()`（295 行）：从 Moderator 拉取航天器/全部对象名填充下拉。

### （七）src/gui/controllogic —— 控制逻辑命令面板

#### 1. ConditionPanel（If / While 条件面板）

**ConditionPanel.hpp / ConditionPanel.cpp**

- 职责：If 与 While 命令的配置面板（由 `GmatMainFrame::CreateNewControl` 在 `IF_CONTROL/WHILE_CONTROL` 时创建）。
- 关键继承：`class ConditionPanel : public GmatPanel`（hpp 43 行），持 `ConditionalBranch *theCommand`（hpp 62 行）。
- 网格列常量（hpp 53-60 行）：`MAX_ROW=10, MAX_COL=6`；列 0 命令名、1/3/5 为"参数/数值"切换选择列（LHS_SEL_CEL）、2 左值、3 条件、4/6 右值选择、5 右值。
- 构造（cpp 73-92 行）：`theCommand = (ConditionalBranch*)cmd;` → `Create()` → `Show()`；`mObjectTypeList` 预置 "Spacecraft"/"SpacePoint"/"ImpulsiveBurn"。
- `Create()`（117-156 行）：`conditionGrid->CreateGrid(MAX_ROW, MAX_COL, ...)`，列标题 LHS/Condition/RHS，`UpdateSpecialColumns()` 把选择列做成参数选择按钮。
- `LoadData()`（165 行起）：从 `theCommand->GetIntegerParameter("NumberOfConditions")` 读条件数，逐行解析左值/运算符/右值（参数或数值）。
- `SaveData()`：把网格内容写回 `SetIntegerParameter("NumberOfConditions")` 与各条件的 LHS/RHS 设置。
- 网格事件：`OnCellDoubleClick/OnCellLeftClick/OnCellRightClick/OnCellValueChange/OnGridTabbing/OnKeyDown`（hpp 75-80 行），`GetNewValue(row, col)` 弹出 ParameterSelectDialog 选参数。

#### 2. ForPanel（For 循环面板）

**ForPanel.hpp / ForPanel.cpp**：For 命令配置面板：`wxGrid` 八列（索引选择/索引/起始选择/起始/增量选择/增量/结束选择/结束，`GridColumn` 枚举 hpp 53-64 行）；持 `For *theForCommand`（hpp 83 行）；`LoadData()` 从 For 命令读 index/start/increment/end 参数（`mIndexIsParam/mStartIsParam/...` 记录每项是参数还是数值），`SaveData()` 反向写回；`GetNewValue` 同样弹参数选择对话框。

## 三、关键设计模式与数据流

### 1. wxWidgets MDI 窗口体系

窗口层级：

```
wxApp (GmatApp)
 └─ GmatMainFrame (wxMDIParentFrame)
     ├─ GmatMenuBar / GmatToolBar / wxStatusBar
     ├─ wxSashLayoutWindow theMainWin ── GmatNotebook
     │     ├─ ResourceTree 页
     │     ├─ MissionTree + MissionTreeToolBar 页
     │     └─ OutputTree 页
     ├─ wxSashLayoutWindow theMessageWin ── msgTextCtrl（消息窗口）
     └─ GmatMdiChildFrame ×N（配置面板 / 脚本编辑器 / 输出面板 / 脱锚任务树）
```

要点：所有"可打开页面"统一为 `GmatMdiChildFrame`（wxMDIChildFrame）外壳 + 内部面板；外壳负责菜单使能、脏标记、位置记忆、关闭流程；内部面板负责对象编辑。MDI 子窗口列表 `theMdiChildren`（wxList）由 GmatMainFrame 统一维护，`GetChild/RemoveChild/CloseAllChildren` 基于名称+ItemType 寻址。

### 2. 单例装配链（启动即接线）

| 单例 | 类型 | 挂接点 |
|---|---|---|
| GmatAppData | GUI 全局指针仓库 | GmatApp::OnInit 最早创建 |
| GuiInterpreter | GUI↔Moderator 门面 | `theModerator->SetUiInterpreter` |
| GuiMessageReceiver | 消息 | `MessageInterface::SetMessageReceiver`（GmatApp 构造） |
| GuiPlotReceiver | 绘图 | `PlotInterface::SetPlotReceiver`（GmatApp 构造） |
| GuiListenerManager | 求解器监听 | `ListenerManagerInterface::SetListenerManager`（GmatApp 构造） |
| GuiPublisher | 数据发布 + wxYield | `theModerator->OverridePublisher`（OnInit） |
| GuiItemManager | 控件工厂/清单缓存 | 各面板构造时 `GetInstance()` |

这些"接收器/发布器"单例把基础库的静态接口从控制台实现整体替换为 GUI 实现，是"引擎不感知界面、界面经接口回调"的桥接模式。

### 3. 树节点 ItemType 驱动的面板工厂（两级分派）

```
用户双击任务树/资源树节点
  → MissionTree::OpenItem / ResourceTree::OnItemActivated
  → GmatMainFrame::CreateChild(GmatTreeItemData*)     ← 第一级：按 ItemType 分段
       ├─ CreateNewResource  → switch(itemType) 实例化具体面板 ← 第二级
       │     ├─ 定制面板（SpacecraftPanel / GroundStationPanel / ...）
       │     └─ 兜底 GmatBaseSetupPanel（默认分支）
       ├─ CreateNewCommand   → 命令配置面板
       ├─ CreateNewControl   → ConditionPanel / ForPanel
       ├─ CreateNewOutput    → ReportFilePanel / EventFilePanel / CompareReportPanel
       └─ CreateUndockedMissionPanel
  → GmatMdiChildFrame 外壳 + wxScrolledWindow + 面板
```

`GmatTree::ItemType` 的分段（40000/41000/43000/44000/46000/47000）是这一工厂的分派键；`BEGIN_OF_*/END_OF_*` 边界常量保证新增类型落在正确分支。GuiItemManager 在第二级内为面板提供对象选择控件（按其"资源清单缓存"自动同步增删改名）。

### 4. MissionTree ↔ GmatCommand 双向绑定

- **树 → 命令（下行）**：任务树右键 Append/InsertBefore/InsertAfter/Delete → `MissionTree::CreateCommand`（`GuiInterpreter::CreateDefaultCommand` 造对象）→ `GuiInterpreter::InsertCommand/DeleteCommand` → Moderator 修改沙箱命令链表；`PanelObjectChanged` 等入口触发 `UpdateMission` 重绘。
- **命令 → 树（上行）**：脚本解释/加载后 `UpdateCommand()` 从 `GetFirstCommand()` 沿链表重建整树；每个节点 `MissionTreeItemData` 持有命令指针（`GetCommand()`）；节点显示名经 `cmd->SetSummaryName()` 反写命令——标签是命令的"摘要名"投影。
- **绑定失效处理**：`inScriptEvent` 标志跳过脚本事件内部命令；视图过滤（`mViewCommands/mViewLevel`）只影响显示不影响链表。

### 5. GUI ↔ 引擎运行链

```
Run 按钮 (OnRun)
 → RunCurrentMission
   → EnableMenuAndToolBar(false)（冻结界面）
   → wxYield()（让界面出时间片）
   → GuiInterpreter::RunMission(1)
     → theModerator->RunMission(1)（沙箱执行）
   → 执行期间 GuiPublisher::Publish → wxYield（33ms 节流）
   → 订阅者经 GuiPlotReceiver / GuiListenerManager 更新绘图/求解窗口
 → NotifyRunCompleted → UpdateMenus(true)（解冻）
```

### 6. 持久化（个性化配置）

`GmatAppData::GetPersonalizationConfig()`（wxFileConfig）承载：主窗口位置/大小（`/MainFrame/UpperLeft`、`/MainFrame/Size`，GmatApp::OnInit 读取）、控制台高度（`/ConsoleWindow/...`）、子窗口位置（`/MissionTree/`、`/ScriptEditor/`）、欢迎页开关（`/Main/ShowWelcomeOnStart`）。输出类子窗口位置写入 Subscriber 参数（UpperLeft/Size/RelativeZOrder/Maximized），随对象脚本保存。

## 四、文件清单附录

### 表 9-1 foundation 目录（36 个文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| src/gui/foundation/GmatPanel.hpp/.cpp | 所有配置面板基类：按钮条、sizer、OK/Apply/Cancel 事件 | GmatPanel、OnApply/OnOK/OnCancel/OnHelp/OnScript、Create/LoadData/SaveData 纯虚 |
| src/gui/foundation/GmatSavePanel.hpp/.cpp | 脚本保存面板基类（脚本保存/同步/运行） | GmatSavePanel、OnSave/OnSaveAs/UpdateStatusOnClose/MakeScriptActive |
| src/gui/foundation/GmatDialog.hpp/.cpp | 模态对话框基类 | GmatDialog、Create/LoadData/SaveData/ResetData 纯虚 |
| src/gui/foundation/GmatMdiChildFrame.hpp/.cpp | MDI 子窗口模板：菜单使能/脏标记/位置记忆/关闭流程 | GmatMdiChildFrame、OnClose/SaveChildPositionAndSize/UpdateGuiItem |
| src/gui/foundation/GuiItemManager.hpp/.cpp | 控件工厂与资源清单缓存单例 | GuiItemManager、GetObjectTypeComboBox/GetPropertyListBox/UpdateAll/IsValidVariable |
| src/gui/foundation/UserInputValidator.hpp/.cpp | 输入校验工具 | UserInputValidator、CheckReal/CheckInteger/CheckVariable/CheckTimeFormatAndValue |
| src/gui/foundation/GmatBaseSetupPanel.hpp/.cpp | 通用参数面板（ini 驱动自动生成控件） | GmatBaseSetupPanel、BuildControl/CreateGroups/RefreshProperty |
| src/gui/foundation/ArraySetupPanel.hpp/.cpp | 数组（ARRAY）编辑面板 | ArraySetupPanel、SaveData/CheckCellValue |
| src/gui/foundation/ParameterSetupPanel.hpp/.cpp | 变量/字符串编辑面板 | ParameterSetupPanel、mIsStringVar |
| src/gui/foundation/ArraySetupDialog.hpp/.cpp | 数组编辑对话框 | ArraySetupDialog（GmatDialog 版） |
| src/gui/foundation/ParameterCreateDialog.hpp/.cpp | 创建变量/数组/字符串对话框 | ParameterCreateDialog、ParameterType、CreateVariable/CreateArray |
| src/gui/foundation/ParameterSelectDialog.hpp/.cpp | 参数选择对话框（对象-属性-参数三级联动） | ParameterSelectDialog、FormParameterName/ShowSpacecraft |
| src/gui/foundation/ShowScriptDialog.hpp/.cpp | 对象脚本展示对话框 | ShowScriptDialog、showAsSingleton |
| src/gui/foundation/ShowSummaryDialog.hpp/.cpp | 命令摘要展示对话框 | ShowSummaryDialog、summaryForMission/physicsOnly |
| src/gui/foundation/GmatColorPanel.hpp/.cpp | SpacePoint 颜色子面板 | GmatColorPanel、GetOrbitColor/GetTargetColor |
| src/gui/foundation/SinglePathSetupPanel.hpp/.cpp | 单路径设置面板 | SinglePathSetupPanel、GetFullPathName |
| src/gui/foundation/MultiPathSetupPanel.hpp/.cpp | 多路径列表管理面板 | MultiPathSetupPanel、UpdatePathNames |
| src/gui/foundation/GmatStaticBoxSizer.hpp/.cpp | 跨版本静态框 sizer | GmatStaticBoxSizer、SetLabel |

### 表 9-2 app 目录（54 个文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| src/gui/app/GmatApp.hpp/.cpp | 应用入口（wxApp） | GmatApp、IMPLEMENT_APP、OnInit/OnExit/FilterEvent/ProcessCommandLineOptions |
| src/gui/app/GmatAppData.hpp/.cpp | GUI 全局数据单例 | GmatAppData、Instance/GetMainFrame/GetPersonalizationConfig |
| src/gui/app/GmatMainFrame.hpp/.cpp | MDI 主框架：菜单/工具栏/子窗口工厂/运行控制 | GmatMainFrame、CreateChild/CreateNewResource/RunCurrentMission/ManageMissionTree |
| src/gui/app/GmatMenuBar.hpp/.cpp | 主菜单栏构建 | GmatMenuBar、CreateMenu/UpdateRecentMenu、GmatMenu 枚举 |
| src/gui/app/GmatToolBar.hpp/.cpp | 主工具栏 | GmatToolBar、CreateToolBar/AddAnimationTools/AddGuiScriptSyncStatus |
| src/gui/app/GmatNotebook.hpp/.cpp | 左侧三页笔记本 | GmatNotebook、CreateResourcePage/CreateMissionPage/CreateOutputPage/CreateUndockedMissionPanel |
| src/gui/app/GmatTreeItemData.hpp/.cpp | 树节点数据 + GmatTree 枚举 | GmatTree::ItemType/ResourceIconType/MissionIconType、GmatTreeItemData |
| src/gui/app/MissionTreeItemData.hpp/.cpp | 任务树节点数据（持命令指针） | MissionTreeItemData、GetCommand/SetCommand |
| src/gui/app/ResourceTree.hpp/.cpp | 资源树 | ResourceTree、CreateObject/AddDefaultResources/AddObjectToTree/UpdateResource |
| src/gui/app/ScriptPanel.hpp/.cpp | 脚本编辑面板（非 STC） | ScriptPanel、mFileContentsTextCtrl、ClickButton |
| src/gui/app/WelcomePanel.hpp/.cpp | 欢迎页 | WelcomePanel、FillGroup、OnOpenRecentScript |
| src/gui/app/GuiInterpreter.hpp/.cpp | GUI↔Moderator 门面 | GuiInterpreter、CreateDefaultCommand/RunMission/InterpretScript/UpdateView |
| src/gui/app/GuiPublisher.hpp/.cpp | 发布器 + 节流 wxYield | GuiPublisher、Publish/Ping |
| src/gui/app/GuiMessageReceiver.hpp/.cpp | 消息接收器 | GuiMessageReceiver、ShowMessage/PopupMessage/LogMessage |
| src/gui/app/GuiPlotReceiver.hpp/.cpp | 绘图接收器 | GuiPlotReceiver、CreateGlPlotWindow/UpdateXyPlot/UpdateDynamicDataDisplay |
| src/gui/app/GuiListenerManager.hpp/.cpp | 求解器监听窗口管理 | GuiListenerManager、CreateSolverListener |
| src/gui/app/GmatConnection.hpp/.cpp | wxIPC 服务端连接 | GmatConnection、OnExec/RunRequest/RunPoke |
| src/gui/app/GmatServer.hpp/.cpp | wxIPC 服务端 | GmatServer、OnAcceptConnection |
| src/gui/app/GmatSocketServer.hpp/.cpp | TCP socket 服务器 | GmatSocketServer、RunServer/OnRequest/OnPoke |
| src/gui/app/AboutDialog.hpp/.cpp | 关于对话框 | AboutDialog |
| src/gui/app/CompareFilesDialog.hpp/.cpp | 批量文件比较对话框 | CompareFilesDialog、GetCompareTolerance |
| src/gui/app/CompareTextDialog.hpp/.cpp | 文本/数值逐行比较对话框 | CompareTextDialog |
| src/gui/app/FileUpdateDialog.hpp/.cpp | 文件批量更新对话框 | FileUpdateDialog、GenerateBatchFile |
| src/gui/app/InteractiveMatlabDialog.hpp/.cpp | 交互式 MATLAB 对话框 | InteractiveMatlabDialog、SetupCommand/SetResults |
| src/gui/app/RunScriptFolderDialog.hpp/.cpp | 脚本文件夹批量运行对话框 | RunScriptFolderDialog、GetFilterString |
| src/gui/app/SetPathDialog.hpp/.cpp | 路径设置对话框 | SetPathDialog（组合 Multi/SinglePathSetupPanel） |
| src/gui/app/TextEphemFileDialog.hpp/.cpp | 文本星历生成对话框 | TextEphemFileDialog、CreateTextEphem |

### 表 9-3 view 目录（14 个文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| src/gui/view/ScriptEditor.hpp/.cpp | STC 脚本编辑器 | ScriptEditor、InitializePrefs/ApplySyntaxHighlight/LoadFile |
| src/gui/view/EditorPanel.hpp/.cpp | 脚本编辑外壳（STC） | EditorPanel、GetEditor |
| src/gui/view/EditorPreferences.hpp/.cpp | 编辑器语言/样式全局表 | GmatEditor::LanguageInfoType/StyleInfoType/CommonInfoType |
| src/gui/view/EditorPrintout.hpp/.cpp | 编辑器打印 | EditorPrintout、OnPrintPage/PrintScaling |
| src/gui/view/FindReplaceDialog.hpp/.cpp | 查找替换对话框 | FindReplaceDialog、SetEditor |
| src/gui/view/ViewTextFrame.hpp/.cpp | 文本查看帧 | ViewTextFrame、AppendText/SetWindowMode |
| src/gui/view/ViewTextDialog.hpp/.cpp | 文本查看对话框 | ViewTextDialog、isTextEditable |

### 表 9-4 mission 目录（10 个文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| src/gui/mission/MissionTree.hpp/.cpp | 任务树：命令序列可视化与编辑 | MissionTree、UpdateCommand/AppendCommand/Append/OpenItem/CreateCommandIdMap |
| src/gui/mission/DecoratedTree.hpp/.cpp | 带装饰列的树控件 | DecoratedTree、SetParameter/OnPaint |
| src/gui/mission/MissionTreeToolBar.hpp/.cpp | 任务树视图工具栏 | MissionTreeToolBar、OnViewByLevel/OnCustomView |
| src/gui/mission/TreeViewOptionDialog.hpp/.cpp | 任务树自定义视图对话框 | TreeViewOptionDialog |
| src/gui/mission/UndockedMissionPanel.hpp/.cpp | 脱锚任务面板外壳 | UndockedMissionPanel、GetMissionTree |

### 表 9-5 output 目录（8 个文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| src/gui/output/OutputTree.hpp/.cpp | 输出树 | OutputTree、RemoveItem/UpdateOutput |
| src/gui/output/ReportFilePanel.hpp/.cpp | 报告文件查看面板 | ReportFilePanel、mFileContentsTextCtrl |
| src/gui/output/EventFilePanel.hpp/.cpp | 事件文件查看面板 | EventFilePanel |
| src/gui/output/CompareReportPanel.hpp/.cpp | 比较结果查看面板 | CompareReportPanel、AppendText |

### 表 9-6 debugger 目录（6 个文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| src/gui/debugger/Breakpoint.hpp/.cpp | 断点命令 | Breakpoint、Execute/GetGeneratingString |
| src/gui/debugger/DebuggerCommandFactory.hpp/.cpp | 调试命令工厂 | DebuggerCommandFactory、CreateCommand |
| src/gui/debugger/InspectorPanel.hpp/.cpp | 对象检查器（调试面板） | InspectorPanel、SetCommand/Step/PopulateLists |

### 表 9-7 controllogic 目录（4 个文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| src/gui/controllogic/ConditionPanel.hpp/.cpp | If/While 条件面板 | ConditionPanel、LoadData/SaveData/GetNewValue |
| src/gui/controllogic/ForPanel.hpp/.cpp | For 循环面板 | ForPanel、LoadData/SaveData |
