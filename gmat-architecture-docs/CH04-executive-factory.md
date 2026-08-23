# 第4章 执行引擎、工厂体系与脚本解释器

本章负责 `src/base/executive/`、`src/base/factory/`（含 `guicomponents/` 子目录）、`src/base/interpreter/`、`src/base/plugin/` 四个目录，共 **106 个代码文件**（53 个 `.hpp` + 53 个 `.cpp`）。它们构成 GMAT 的「运行时主干」：脚本 → 解释器 → Moderator → Sandbox → 对象 Initialize/Execute → Publisher → Subscriber 的完整链路都在这里落地。

> **范围说明（重要）**：本章任务书中的若干类名（Sequencer、PluginManager、IDynamicFactory、ConsoleMessageReceiver、ObjectMap 类）在本仓库（depth-1 克隆）中**并不以同名文件/类存在**，本章按真实代码给出其等价实现：
> - 「Sequencer」→ 命令链表的编排由 `Moderator::commands[]` + `Sandbox::sequence` 完成，没有独立 Sequencer 类；
> - 「PluginManager/IDynamicFactory」→ 由 `src/base/plugin/DynamicLibrary` + 各插件 `GmatPluginFunctions.cpp` 的 C 入口 + `FactoryManager::RegisterFactory` 完成；
> - 「ConsoleMessageReceiver」→ 位于 `src/console/`（不属本章目录），本章只在数据流中提及；
> - 「ObjectMap」→ 是 `src/gmatutil/include/utildefs.hpp:124` 的 typedef（`std::map<std::string, GmatBase*>`），不是类。
> - `BranchCommand` 位于 `src/base/command/`、`Subscriber` 位于 `src/base/subscriber/`、`ObjectInitializer`/`EquationInitializer` 位于 `src/base/foundation/`，本章在数据流与调用链中引用它们，但不做逐文件讲解（归属其它章节）。

## 一、本章目录树

```
src/base/
├── executive/                      # 执行引擎（18 文件）
│   ├── Moderator.hpp/.cpp           # 总控单例（本章核心）
│   ├── Sandbox.hpp/.cpp             # 运行沙箱：克隆对象、跑命令序列（本章核心）
│   ├── Publisher.hpp/.cpp           # 发布者：订阅者分发（本章核心）
│   ├── PublisherException.hpp/.cpp
│   ├── SandboxException.hpp/.cpp
│   ├── ListenerManager.hpp/.cpp
│   ├── ListenerManagerInterface.hpp/.cpp
│   ├── PlotInterface.hpp/.cpp
│   └── PlotReceiver.hpp/.cpp
├── factory/                        # 工厂体系（66 文件）
│   ├── Factory.hpp/.cpp             # 工厂抽象基类（本章核心）
│   ├── FactoryException.hpp/.cpp
│   ├── FactoryManager.hpp/.cpp      # 工厂注册/查找单例（本章核心）
│   ├── <30 个具体工厂>.hpp/.cpp      # 每个对象族一个工厂（60 文件）
│   └── guicomponents/               # GUI 插件控件工厂（6 文件）
│       ├── GmatWidget.hpp/.cpp
│       ├── GuiFactory.hpp/.cpp
│       └── PluginWidget.hpp/.cpp
├── interpreter/                    # 脚本解释器（16 文件）
│   ├── Interpreter.hpp/.cpp         # 解释器基类（10748 行实现）
│   ├── ScriptInterpreter.hpp/.cpp   # 脚本解释器单例（本章核心）
│   ├── ApiInterpreter.hpp/.cpp      # C/Python API 解释器
│   ├── ScriptReadWriter.hpp/.cpp    # 逻辑块读取/写出
│   ├── MathParser.hpp/.cpp          # 递归下降数学解析器
│   ├── MathTree.hpp/.cpp            # 数学表达式求值树
│   ├── Validator.hpp/.cpp           # 引用/wrapper 校验
│   └── InterpreterException.hpp/.cpp
└── plugin/                         # 插件运行时接口（6 文件）
    ├── DynamicLibrary.hpp/.cpp      # 动态库加载器（本章核心）
    ├── GuiInterface.hpp/.cpp
    └── GmatEventHandler.hpp/.cpp
```

## 二、逐文件/逐类讲解

### 2.1 executive —— 执行引擎

#### 2.1.1 Moderator.hpp / Moderator.cpp（总控单例，本章核心）

**职责**：`Moderator` 是 GMAT 运行的中央协调者，唯一实例（`static Moderator* Instance()`，`Moderator.hpp:99`）。它负责：创建核心管理器（FactoryManager/ConfigManager/Publisher/ScriptInterpreter）、注册所有内置工厂、加载插件、创建默认太阳系、持有脚本解释器与命令序列、把配置对象「灌」进 Sandbox、并触发 Initialize/Execute。

关键成员（`Moderator.hpp`）：

- `sandboxes`（`std::vector<Sandbox*>`，553 行）与 `commands`（`std::vector<GmatCommand*>`，555 行）：最多 `Gmat::MAX_SANDBOX = 4` 个沙箱（`Moderator.hpp:85`），每个沙箱对应一条命令链表。
- `objectMapInUse` / `previousObjectMap`（557–558 行）：当前生效的对象表指针，初始化时指向 `ConfigManager` 的配置对象表（见 `Moderator.cpp:377`）。
- `theFactoryManager` / `theConfigManager` / `thePublisher` / `theScriptInterpreter`（565–568 行）：四大核心依赖。
- `userLibraries`（`std::map<std::string, DynamicLibrary*>`，585 行）、`pluginGuiFactories`（587 行）：插件库与 GUI 工厂登记表。
- `runState` / `detailedRunState`（581–582 行）：全局运行状态（`Gmat::RunState`，见 `utildefs.hpp:188`）。

**初始化流程** `Moderator::Initialize()`（`Moderator.cpp:219`）：

```cpp
// Moderator.cpp:275-334（节选）
theFactoryManager = FactoryManager::Instance();        // 275
theConfigManager = ConfigManager::Instance();          // 283
// 注册全部内置工厂
theFactoryManager->RegisterFactory(new AtmosphereFactory());   // 291
theFactoryManager->RegisterFactory(new AttitudeFactory());
...
theFactoryManager->RegisterFactory(new SubscriberFactory());   // 311
theFactoryManager->RegisterFactory(new CelestialBodyFactory());
theFactoryManager->RegisterFactory(new PlanetographicRegionFactory()); // 313

if (thePublisher == NULL)
   thePublisher = Publisher::Instance();               // 317-318

theScriptInterpreter = ScriptInterpreter::Instance();  // 326
LoadPlugins();                                         // 334  ← 加载启动文件里的插件
theDefaultSolarSystem = CreateSolarSystem("DefaultSolarSystem"); // 337
```

逐行解读：
- 275–283：先建 FactoryManager 与 ConfigManager——工厂先于一切对象存在。
- 291–313：Moderator 逐一 `new` 出内置工厂并注册；这正是「工厂单例注册」的第一处集中体现。
- 317–318：Publisher 允许被 `OverridePublisher()`（`Moderator.cpp:210`）替换为派生类，供测试/GUI 注入。
- 326：脚本解释器也是单例；GUI 侧另有一个 `theUiInterpreter`（`Moderator.hpp:563`）。
- 334：`LoadPlugins()` 读取启动文件中的 `PLUGIN` 行，动态注册第三方工厂。
- 337：默认太阳系 `DefaultSolarSystem` 本身也是经 `CreateSolarSystem()` 走工厂创建的。
- 358–367：至少创建一个 Sandbox 与一个 `NoOp` 命令（空头结点），保证命令链表有起点。

**对象创建** `Moderator::CreateObject()`（`Moderator.cpp:2363`）是对外统一入口，按 `objTypeId` 分派到 `CreateSpacecraft` / `CreateAxisSystem` / `CreateCelestialBody` …（2375–2406 行），其余类型落到通用路径：`theFactoryManager->CreateObject(objTypeId, type, name)`（2412 行），成功后 `AddObjectToObjectMapInUse()`（2431 行）挂入当前对象表。`CreateOtherObject()`（2463 行）是「不配置」对象的变体（StopCondition、AxisSystem、MathNode 等）。

**任务运行** `Moderator::RunMission()`（`Moderator.cpp:7242`）：

```cpp
// Moderator.cpp:7302-7324（节选）
try
{
   AddSolarSystemToSandbox(sandboxNum-1);      // 7308
   AddTriggerManagersToSandbox(sandboxNum-1);
   AddInternalCoordSystemToSandbox(sandboxNum-1);
   AddPublisherToSandbox(sandboxNum-1);        // 7311
   AddSubscriberToSandbox(sandboxNum-1);       // 7312
   AddOtherObjectsToSandbox(sandboxNum-1);     // 7313
   AddCommandToSandbox(sandboxNum-1);          // 7316
   InitializeSandbox(sandboxNum-1);            // 7324
}
catch (BaseException &e) { status = -2; ... isRunReady = false; }  // 7326-7332
```

逐行解读：运行前先 `sandboxes[i]->Clear()`（7283 行）清空上次残留；随后把太阳系、TriggerManager、内坐标系、Publisher、Subscriber、其余对象、命令序列**按序**加入沙箱；`InitializeSandbox`（10891–10894 行）只是转发 `sandboxes[index]->Initialize()`。初始化成功后（`isRunReady` 仍为 true）在 7356–7378 行进入 `ExecuteSandbox()`（转发 `Execute()`，10899–10902 行）。`RunScript()`（8052–8056 行）是 `RunMission` 的别名封装。

**脚本入口** `Moderator::InterpretScript()`（`Moderator.cpp:7672`）：设置工作目录 → `theScriptInterpreter->Interpret(filename)`（7717 行）→ 成功后补插 `BeginMissionSequence`（7808–7853 行）→ 置 `isRunReady`。两个重载：按文件名（7672 行）与按 `std::istringstream`（7903 行，供 GUI 脚本编辑器/函数模式使用）。

**异常与状态**：`RunMission` 用返回码区分：`-2` 沙箱初始化失败、`-3` 未知/系统异常、`-4` 用户中断（匹配 `"interrupted"`，7394 行）、`-5` 运行期错误（7402 行）。`GetUserInterrupt()` / `GetRunState()` / `ChangeRunState()`（`Moderator.hpp:437–440`）把暂停/停止意图经状态机传给 Sandbox 的 `Interrupt()`。

#### 2.1.2 Sandbox.hpp / Sandbox.cpp（运行沙箱，本章核心）

**职责**：`Sandbox` 是一次任务运行的隔离工作区（`Sandbox.hpp:62`）。它**克隆**配置对象形成本地副本，跑命令链表，并通过 Publisher 向外广播数据。核心成员（`Sandbox.hpp:116–140`）：

- `objectMap` / `globalObjectMap` / `combinedObjectMap`（116–120 行）：本地对象存储（LOS）、全局对象存储（GOS）、二者合并视图（供函数解释器用）。
- `sequence` / `current`（128–130 行）：命令链表头与当前执行指针。
- `state`（`runMode` 枚举，97–106 行：`IDLE/INITIALIZED/RUNNING/PAUSED/STOPPED/REFRESH/RESET`）。
- `objInit`（`ObjectInitializer*`，140 行）：负责把对象引用关联起来（实际类在 `src/base/foundation/`）。
- `interruptCount` / `pollFrequency`（136–138 行）：中断轮询节流计数（每 50 次执行检查一次）。

**对象克隆入沙箱** `Sandbox::AddObject()`（`Sandbox.cpp:181`）：

```cpp
// Sandbox.cpp:204-229（节选）
if (FindObject(name) == NULL)          // 尚未加入
{
   cloned = obj->Clone();              // 218：克隆，隔离配置对象
   SetObjectByNameInMap(name, cloned); // 229：写入 objectMap
   Integer count = cloned->GetOwnedObjectCount();
   for (Integer i = 0; i < count; ++i) // 239-248：把从属 Subscriber 也订阅
   {
      GmatBase* oo = cloned->GetOwnedObject(i);
      if (oo->IsOfType(Gmat::SUBSCRIBER))
         AddOwnedSubscriber((Subscriber*)oo);
   }
}
```

逐行解读：沙箱不直接操作 `ConfigManager` 持有的对象，而是 `Clone()` 出副本（218 行），保证运行时修改不回写配置、也允许多次运行互不干扰；229 行把副本放进本地 `objectMap`；239–248 行顺带把对象「拥有」的 Subscriber 注册到 Publisher。

**初始化** `Sandbox::Initialize()`（`Sandbox.cpp:581`）分三步：

1. 构建 `ObjectInitializer` 并初始化对象（669–693 行）：

```cpp
// Sandbox.cpp:669-693（节选）
objInit = new ObjectInitializer(solarSys, &objectMap, &globalObjectMap,
      internalCoordSys);              // 669-670
try
{
   objInit->InitializeObjects();      // 684
}
catch (BaseException &be)
{
   SandboxException se("");
   se.SetDetails("Error initializing objects in Sandbox.\n%s\n",
                 be.GetFullMessage().c_str());
   throw se;                          // 691：包装后重抛
}
```

2. 把 `IsGlobal()` 的对象从 LOS 迁到 GOS（714–784 行，含坐标系的全局化特殊处理 730–776 行）。
3. 遍历命令链表逐个 `current->Initialize()`（875–990 行），**收集异常而非立即中断**：

```cpp
// Sandbox.cpp:875-1013（节选）
while (current)
{
   try { ... current->SetObjectMap(&objectMap);
            current->SetGlobalObjectMap(&globalObjectMap);
            rv = current->Initialize(); ... }       // 940
   catch (BaseException &be)
   {
      if (ReportError(be))            // 982：抑制重复告警
      {
         ++exceptionCount;
         exceptionTypes.push_back(be.GetMessageType());
         exceptions.push_back(be.GetFullMessage()); // 985-986
      }
   }
   current = current->GetNext();      // 989：继续下一条命令
}
...
if (exceptionCount > 0)
{
   for (...) MessageInterface::ShowMessage(...);    // 1003-1010
   throw SandboxException("Errors were found in the mission control "
         "sequence; ...");            // 1011-1013：最后统一抛出
}
state = INITIALIZED;                  // 1020
```

逐行解读：这是 GMAT 的**「继续初始化」语义**——一条命令初始化失败不立刻中断，而是把异常（类型 + 全文）压入 `exceptions`/`exceptionTypes`，继续初始化后续命令，最后统一打印并抛出一个 `SandboxException`（1011–1013 行）。`be.GetMessageType()`（985 行）用于区分 `Gmat::ERROR_` 与 `Gmat::GENERAL_`/`WARNING_`（枚举见 `utildefs.hpp:179-186`），只有 `ERROR_` 才计入错误编号（1006–1009 行）。`ReportError()`（2338–2349 行）目前只抑制重复的 Python 接口告警。

**执行** `Sandbox::Execute()`（`Sandbox.cpp:1040`）：

```cpp
// Sandbox.cpp:1063-1253（节选）
try
{
   while (current)
   {
      if (Interrupt()) { ... }             // 1068：暂停/停止检查
      ...
      try
      {
         rv = current->Execute();          // 1186：真正执行命令
         if (!rv) throw SandboxException(...);  // 1199
         if (current->AffectsClones()) { UpdateClones(...); }  // 1202-1231
         current = current->GetNext();     // 1233：前进
      }
      catch (BaseException &e)
      {
         std::string errormsg = e.GetDetails();
         errormsg = current->AddFileInfoToErrorMessage(errormsg); // 1247 附脚本行号
         e.SetDetails(errormsg);
         throw;                            // 1249：重抛
      }
   }
}
catch (BaseException &e)
{
   sequence->RunComplete(true);            // 1259：收尾清理
   state = STOPPED;
   errorInPreviousFcs = true;
   throw;                                  // 1269：继续向上抛给 Moderator
}
```

逐行解读：
- 1065–1253 是执行主循环：每执行一条命令前先 `Interrupt()`（1068 行）检查用户是否暂停/停止；暂停时 `publisher->Ping()` 后 `continue`（1076–1080 行），停止时 `NotifyEndOfRun()` 后抛 `"Execution interrupted"`（1099 行，`Moderator.cpp:7394` 据此识别 `-4`）。
- 1186 行 `current->Execute()` 是唯一执行点；1188–1200 行把「命令返回 false」翻译成异常。
- 1202–1231 行处理「克隆更新」：若命令修改了拥有本地克隆的对象（如 `Vary`/`Achieve` 改航天器状态），调用 `UpdateClones()`（2055 行）按 `PASS_TO_ALL` / `PASS_TO_REGISTERED` / `SKIP_UPDATES` 三种策略把改动同步给克隆体（`PassToAll` 2094 行、`PassToBranchCommand` 2219 行、`UpdateAndInitializeCloneOwner` 2273 行）。
- 1235–1252 内层 catch：用 `AddFileInfoToErrorMessage` 给错误附加脚本文件与行号（1247 行）后 `throw;` 重抛——异常穿透一层，交由 1255–1270 外层 catch 统一做 `RunComplete`、置 STOPPED、再重抛给 Moderator。**这层层包装重抛就是任务书中「捕获异常并重新抛出以支持 Continue 语义」的落点**：Moderator 拿到的是带脚本定位信息的完整异常。

**中断节流** `Sandbox::Interrupt()`（`Sandbox.cpp:1306`）：用 `interruptCount`/`pollFrequency`（默认 50，构造器 99–100 行）节流，每 50 次调用才查一次 `Moderator::GetUserInterrupt()`，映射到 `PAUSED/STOPPED/RUNNING` 状态。

**清理** `Sandbox::Clear()`（`Sandbox.cpp:1347`）：先退订所有 Subscriber（1374、1467 行），删除 LOS/GOS 中的克隆对象（1414、1498 行），`publisher->ClearPublishedData()`（1515 行），最后 `state = IDLE`（1596 行）。构造/拷贝/赋值均私有（`Sandbox.hpp:160–161`），禁止外部复制沙箱。

#### 2.1.3 Publisher.hpp / Publisher.cpp（发布-订阅分发，本章核心）

**职责**：`Publisher` 是观察者模式里的「主题」，唯一实例（`Publisher.hpp:43`）。命令（Provider，如 `Propagate`）先 `RegisterPublishedData()` 注册数据元信息，运行中反复 `Publish()`，Publisher 遍历 `subscriberList` 调 `ReceiveData()` 分发给每个订阅者。

关键成员（`Publisher.hpp`）：
- `subscriberList`（`std::list<Subscriber*>`，112 行）：订阅者链表，`Subscribe()` 去重追加（`Publisher.cpp:118`，138 行用 `find` 判重）。
- `providerMap`（`std::map<GmatBase*, std::vector<DataType>*>`，154 行）：provider 指针 → 其注册过的数据标签/ID 列表；`DataType` 结构体（142–151 行）存 `labels` 与 `id`。
- `currProviderId` / `providerId`（116/114 行）：当前 provider 序号。
- `runState`（123 行）：与 Moderator 同步的运行状态，用于告知订阅者「正在解算」等。

**Publish 的三个重载**（对应「消息类型」——按数据类型分派）：
- `Publish(GmatBase*, Integer, Real*, Integer, Real)`（`Publisher.cpp:250`）：实数轨道数据（主通道）；
- `Publish(Integer, char*, Integer)`（434 行）：字符串数据；
- `Publish(Integer, Integer*, Integer)`（495 行）：整型数据。

**分发循环**（以 Real 为例，`Publisher.cpp:368-416`）：

```cpp
// Publisher.cpp:368-416（节选）
std::list<Subscriber*>::iterator current = subscriberList.begin();
while (current != subscriberList.end())
{
   if (ephemsOnly && !((*current)->IsOfType(Gmat::EPHEMERIS_FILE)))
   { ++current; continue; }                       // 394-398：step 模式只发星历
   (*current)->SetDataLabels((*dataList)[id].labels);   // 400
   if (count > 0)
      (*current)->SetProvider(provider, data[0]);       // 404
   (*current)->SetPropagationDirection(...);            // 409
   if (!(*current)->ReceiveData(stream))  return false; // 411 字符串形式
   if (!(*current)->ReceiveData(data, count)) return false; // 413 原始数组
   current++;
}
```

逐行解读：发布前先把 `Real` 数据用 `sprintf("%16le")` 拼成字符串流（339–352 行），便于订阅者直接落文件/写窗口；循环里先 `SetDataLabels` + `SetProvider`（400/404 行）告知本批数据的列名与来源，再以两种形式（字符串 411 行、原始数组 413 行）调 `ReceiveData`，任一订阅者拒绝即中断返回 false。398 行体现了「只给星历文件订阅者」的方向过滤。

**注册** `RegisterPublishedData()`（`Publisher.cpp:686`）：`id == -1` 时新建 `DataType` 挂入 `providerMap`（768–798 行），返回新 id；`id != -1` 时只刷新订阅者运行状态（727–748 行）。注释（681–684 行）明确：目前只有 `Propagate` 命令注册并发布轨道数据。

**结束/刷新**：`FlushBuffers()`（560 行）→ 各订阅者 `FlushData()`；`NotifyEndOfRun()`（581 行）→ 各订阅者 `SetEndOfRun()`（Sandbox 执行结束、用户中断时都会调用，见 `Sandbox.cpp:1089` 与 1278 行）；`ClearPublishedData()`（611 行）→ 清空 `providerMap`、`subscriberList` 与订阅者标签（沙箱 `Clear()` 调用，`Sandbox.cpp:1515`）。

**GmatBase 如何与它绑定**：`Subscriber` 本身是 `GmatBase` 的子类（`Publisher.hpp:34` include `Subscriber.hpp`）。绑定发生在 `Sandbox::AddSubscriber()`（`Sandbox.cpp:1616`）：先 `AddObject()` 克隆订阅者，再 `publisher->Subscribe(newSub)`（1623 行）。因此配置里每个 `ReportFile`/`XYPlot`/`EphemerisFile` 对象在进沙箱时自动成为订阅者，运行期由 `Propagate` 命令调 `RegisterPublishedData` + `Publish` 驱动数据流。

#### 2.1.4 PublisherException / SandboxException（异常类，简要）

- `PublisherException`（`PublisherException.hpp:43`）继承 `BaseException`，构造只收 `details`；由 `Publisher::Publish(char/Integer)` 在 provider 未注册时抛出（`Publisher.cpp:448`、506 行）。
- `SandboxException`（`SandboxException.hpp:48`）同样继承 `BaseException`，但构造多收一个 `Gmat::MessageType mt`（默认 `Gmat::ERROR_`，52 行），使沙箱能抛出「非错误」级别的异常（如 `Gmat::GENERAL_`，见 `Sandbox.cpp:1894` 的 FCS 创建失败）。两者的实现 `.cpp` 都是几行的「转发构造 + 空析构」样板。

#### 2.1.5 ListenerManager / ListenerManagerInterface（GUI 解算器监听，简要）

- `ListenerManager`（`ListenerManager.hpp:41`）是纯抽象接口，唯一虚函数 `CreateSolverListener(...)`（45 行）让 GUI 创建「解算器窗口」监听器；构造函数 protected（50 行）保证只能被 GUI 派生类实例化。
- `ListenerManagerInterface`（`ListenerManagerInterface.hpp:42`）是它的静态门面：`SetListenerManager()`（47 行）注入实现，`CreateSolverListener()`（50 行）转发调用。作用是把 solver 的执行回显与 GUI 解耦——engine 侧只依赖接口，GUI 启动时注入实现。

#### 2.1.6 PlotReceiver / PlotInterface（绘图通道，简要）

- `PlotReceiver`（`PlotReceiver.hpp:54`）是 OpenGL 3D / XY 图的抽象接口（约 30 个纯虚函数，62–236 行），同时定义 `GmatPlot::ViewType` 枚举（44–52 行：`TRAJECTORY_PLOT`/`ENHANCED_3D_VIEW`/`GROUND_TRACK_PLOT`）。
- `PlotInterface`（`PlotInterface.hpp:45`）是静态门面，持有一个 `PlotReceiver*`（248 行），`SetPlotReceiver()`（50 行）由 GUI 注入实现；其余全部静态方法（`CreateGlPlotWindow`/`UpdateGlPlot`/`CreateXyPlotWindow`…）都转发给 receiver。这样 base 层的订阅者/命令可以调 `PlotInterface::UpdateXyPlot(...)` 而不依赖 wxWidgets/OpenGL 头文件。

### 2.2 factory —— 工厂体系

#### 2.2.1 Factory.hpp / Factory.cpp（抽象基类，本章核心）

**职责**：`Factory`（`Factory.hpp:81`）是所有工厂的基类，按「对象族」组织——一个具体工厂负责创建一类对象（Spacecraft、Parameter、GmatCommand…）。关键接口：

- `virtual GmatBase* CreateObject(ofType, withName)`（85 行）——通用创建，基类实现**直接抛异常**（`Factory.cpp:56-61`），强制子类覆盖；
- 一整套 `virtual Xxx* CreateXxx(...)`（89–163 行）——如 `CreateSpacecraft` 基类抛 `"requested object must be of type SpaceObject"`（`Factory.cpp:81-85`）；只覆盖它负责的那一类，其余继承基类抛异常版本；
- `virtual StringArray GetListOfCreatableObjects(qualifier)`（167 行）——返回本工厂能创建的类型名列表（成员 `creatables`，209 行）；
- `GetFactoryType()`（187 行）、`IsTypeCaseSensitive()`（188 行）、`GetListOfViewableObjects/Unviewable`（174–176 行）、`GetOverriddenTypes()`（184 行，AWB 扩展：让插件工厂声明「覆盖」内置类型）。

构造函数是 **protected**（195–198 行），只收 `UnsignedInt ofType`（对象族枚举，如 `Gmat::SPACECRAFT`）与可选 `StringArray createList`。派生工厂在构造里 `creatables.push_back(...)` 填类型名，并调用 `GmatType::RegisterType(...)` 登记类型字符串（见 2.2.4 示例）。

#### 2.2.2 FactoryManager.hpp / FactoryManager.cpp（注册/查找单例，本章核心）

**职责**：`FactoryManager`（`FactoryManager.hpp:84`）是 Moderator 与工厂之间的唯一中介，单例。成员 `factoryList`（`std::list<Factory*>`，205 行）、`factoryTypeList`（207 行）、`overrideFactoryList`（`std::map<std::string, Factory*>`，220 行）。

**注册** `RegisterFactory()`（`FactoryManager.cpp:84`）：

```cpp
// FactoryManager.cpp:84-102（节选）
bool FactoryManager::RegisterFactory(Factory* fact)
{
   if (fact == NULL) return false;
   factoryList.push_back(fact);                    // 94
   factoryTypeList.push_back(fact->GetFactoryType());  // 95
   StringArray overrides = fact->GetOverriddenTypes();
   for (UnsignedInt i = 0; i < overrides.size(); ++i)
      SetOverride(fact, overrides[i]);             // 100：处理覆盖声明
   return true;
}
```

**创建** 每个类型一个入口，如 `CreateSpacecraft()`（145 行）：

```cpp
// FactoryManager.cpp:145-152
SpaceObject* FactoryManager::CreateSpacecraft(const std::string &ofType,
                                              const std::string &withName)
{
   Factory* f = FindFactory(Gmat::SPACECRAFT, ofType);
   if (f != NULL)
      return f->CreateSpacecraft(ofType, withName);
   return NULL;
}
```

通用入口 `CreateObject()`（120–129 行）走 `FindFactory(generalType, ofType)` 后调 `f->CreateObject`。所以 `CreateSpacecraft("DefaultSC")` 的完整路径是：**Moderator::CreateSpacecraft → FactoryManager::CreateSpacecraft → FindFactory(Gmat::SPACECRAFT,"Spacecraft") → SpacecraftFactory::CreateSpacecraft → new Spacecraft("DefaultSC")**。

**查找** `FindFactory()`（`FactoryManager.cpp:1143`）：先查 `overrideFactoryList`（1154–1155 行，插件覆盖优先）；否则遍历 `factoryList`，比对 `GetFactoryType()`（1162 行）与 `GetListOfCreatableObjects()`（1166 行）中是否含目标类型；对大小写敏感工厂先用 `GmatStringUtil::Capitalize()` 归一化（1186–1187 行，只有数学类型不敏感，兼容 MATLAB 大小写）；`Gmat::PARAMETER` 还有 owner 匹配逻辑（1196–1217 行）。`GetBaseTypeOf()`（1072 行）反向把类型名映射回对象族枚举，供 GUI 资源树使用。`SetOverride()`（1354 行）实现插件的「类型替换」。

**列表**：`GetListOfItems()`（914 行）、`GetListOfAllItems()`（931 行）、`GetAllObjectTypeArrayMap()`（1019 行）等，全部基于 `factoryTypeList` 遍历累积，是 GUI 资源树/下拉框的数据源。

#### 2.2.3 FactoryException（异常类，简要）

`FactoryException`（`FactoryException.hpp:37`）继承 `BaseException`，构造收默认参数 `details`（41 行），由 `Factory` 基类各未实现的 `Create*` 抛出（`Factory.cpp:59` 等）。它把「此工厂不创建该类对象」的编程错误统一为可捕获异常。

#### 2.2.4 SpacecraftFactory（具体工厂范例）

`SpacecraftFactory`（`SpacecraftFactory.hpp:38`）演示了每个具体工厂的标准四件套：默认构造 / `createList` 构造 / 拷贝构造 / 赋值运算 + 析构，且只覆盖 `CreateObject` 与 `CreateSpacecraft`：

```cpp
// SpacecraftFactory.cpp:72-78
SpaceObject* SpacecraftFactory::CreateSpacecraft(const std::string &ofType,
                                                 const std::string &withName)
{
   if (ofType == "Spacecraft")
      return new Spacecraft(withName);
   return NULL;
}
```

```cpp
// SpacecraftFactory.cpp:89-100
SpacecraftFactory::SpacecraftFactory() :
   Factory(Gmat::SPACECRAFT)
{
   if (creatables.empty())
      creatables.push_back("Spacecraft");              // 94
   GmatType::RegisterType(Gmat::SPACECRAFT, "Spacecraft");   // 98
   GmatType::RegisterType(Gmat::SPACEOBJECT, "SpaceObject");
}
```

逐行解读：构造时把族枚举传基类、填 `creatables`、并向全局 `GmatType` 表登记「枚举 ↔ 脚本字符串」映射（98–99 行，这是脚本写 `Create Spacecraft sat;` 能识别 `Spacecraft` 的依据）。`CreateSpacecraft` 只认 `"Spacecraft"` 一个具体类型，其余返回 NULL（`FactoryManager` 据此报「无法创建」）。

#### 2.2.5 CommandFactory / SubscriberFactory / FunctionFactory / MathFactory / ParameterFactory（较详细）

- **CommandFactory**（`CommandFactory.cpp`，403 行）：创建所有 `GmatCommand` 子类，`creatables` 在 240–286 行列出了全部脚本命令：`BeginMissionSequence`/`Propagate`/`Maneuver`/`Achieve`/`Target`/`Optimize`/`Vary`/`If`/`For`/`While`/`ElseIf`/`EndIf`/`EndFor`/`EndWhile`/`Report`/`SaveMission`/`ScriptEvent`/`Stop`…（分支/循环的 `If/For/While` 都在此，配合 `BranchCommand` 形成控制流）。
- **SubscriberFactory**（`SubscriberFactory.cpp:134-146`）：创建全部订阅者：`ReportFile`/`TextEphemFile`/`MessageWindow`/`XYPlot`/`EphemerisFile`/`OpenGLPlot`/`Enhanced3DView`/`OrbitView`/`GroundTrackPlot`/`OwnedPlot`/`DynamicDataDisplay`——正是 Publisher 分发循环里的接收端。
- **FunctionFactory**（`FunctionFactory.cpp:244` 起）：创建 `GmatFunction`/`MatlabFunction` 与内建数学函数（`GetLastState`/`ConvertTime`/`RotationMatrix`/`QuaternionProduct`…）。
- **MathFactory**（`MathFactory.cpp:339-396`）：创建 `MathElement`/`MathNode` 运算子（`Add`/`Multiply`/`Sin`/`Cos`/`Transpose`/`Inv`/`DegToRad`/`Sprintf`/`FunctionRunner`…），供 `MathParser` 建表达式树时按名实例化节点。
- **ParameterFactory**（`ParameterFactory.cpp:764` 起，1168 行）：最庞大的工厂，创建三类对象：用户容器 `Variable`/`String`/`Array`；系统参数（时间、坐标系、轨道根数、姿态、质量属性等数百个 `X/Y/Z/SMA/ECC/...`）；以及 `Element1..3`/`V/N/B`（引力位、陀螺参数）。`ParameterFactory.cpp:764-1067+` 的 `creatables` 列表本身就是 GMAT 参数体系的「字典」。

#### 2.2.6 其余 25 个具体工厂（2–6 句/个）

以下工厂结构同 `SpacecraftFactory`（四件套 + 覆盖对应 `Create*`），差异只在 `creatables` 内容与 `CreateXxx` 的分支：

- **AssetFactory**：创建 `GroundStation`（`AssetFactory.cpp:57`），SpacePoint 类的地面站。
- **AtmosphereFactory**：创建大气模型 `Exponential`/`MSISE90`/`JacchiaRoberts`（`AtmosphereFactory.cpp:115-118`）。
- **AttitudeFactory**：创建姿态模型 `CoordinateSystemFixed`/`Spinner`/`PrecessingSpinner`/`NadirPointing`/`CCSDS-AEM`/`SpiceAttitude`/`ThreeAxisKinematic`/`CommandableNadirPointing`（`AttitudeFactory.cpp:127-138`）。
- **AxisSystemFactory**：创建轴系 `MJ2000Eq/Ec`、`TOE*`、`MOE*`、`TOD*`、`MOD*`、`ObjectReferenced`/`Equator`/`BodyFixed`/`BodyInertial`/`GSE`/`GSM`/`Topocentric`/`SPICE`/`ICRF`/`TEME` 等（`AxisSystemFactory.cpp:213-236`）。
- **BurnFactory**：创建 `ImpulsiveBurn`/`FiniteBurn`（`BurnFactory.cpp:99-100`）。
- **CalculatedPointFactory**：创建 `LibrationPoint`/`Barycenter`（`CalculatedPointFactory.cpp:105-106`）。
- **CelestialBodyFactory**：创建 `Star`/`Planet`/`Moon`/`Comet`/`Asteroid`（`CelestialBodyFactory.cpp:116-120`）。
- **CoordinateSystemFactory**：创建 `CoordinateSystem`（`CoordinateSystemFactory.cpp:97`）。
- **FieldOfViewFactory**：创建 `ConicalFOV`/`RectangularFOV`/`CustomFOV`（`FieldOfViewFactory.cpp:108-110`）。
- **FormationFactory**：创建 `Formation`（`FormationFactory.cpp:94`）。
- **HardwareFactory**：创建硬件 `FuelTank`/`ChemicalTank`/`ElectricTank`/`Thruster`/`ChemicalThruster`/`ElectricThruster`/`NuclearPowerSystem`/`SolarPowerSystem`/`Imager`（`HardwareFactory.cpp:128-136`，前二者已 deprecated）。
- **InterfaceFactory**：基类代码中**不创建任何接口**（`InterfaceFactory.cpp:75-76` 注释明示），`MatlabInterface` 等由插件工厂提供；它只登记 `GmatType::INTERFACE`（`InterfaceFactory.cpp:97`）。是「抽象工厂留口、插件填空」的典型。
- **ODEModelFactory**：创建 `ForceModel`/`ODEModel`（`ODEModelFactory.cpp:98-99`）。
- **PhysicalModelFactory**：创建力模型 `PointMassForce`/`GravityField`/`SolarRadiationPressure`/`DragForce`/`FiniteThrust`/`RelativisticCorrection`（`PhysicalModelFactory.cpp:118-123`）。
- **PlanetographicRegionFactory**：创建 `PlanetographicRegion`（`PlanetographicRegionFactory.cpp:94`）。
- **PlateFactory**：创建 `Plate`（`PlateFactory.cpp:98`）。
- **PropagatorFactory**：创建积分器 `RungeKutta89`/`PrinceDormand78`/`PrinceDormand45`/`RungeKutta68`/`RungeKutta56`/`AdamsBashforthMoulton`（`PropagatorFactory.cpp:125-132`）。
- **PropSetupFactory**：创建 `PropSetup`（传播设置容器，`PropSetupFactory.cpp:98`）。
- **SolarSystemFactory**：创建 `SolarSystem`（`SolarSystemFactory.cpp:94`）。
- **SolverFactory**：创建 `DifferentialCorrector`（`SolverFactory.cpp:117`），其余求解器由 Estimation 等插件提供。
- **StopConditionFactory**：创建 `StopCondition`（`StopConditionFactory.cpp:98`）。
- **CelestialBodyFactory** 已列；**CalculatedPointFactory** 已列。

#### 2.2.7 guicomponents/（GUI 插件控件工厂，简要）

- **GmatWidget**（`GmatWidget.hpp:45`）：GUI 附加控件的基类，持 `PluginWidget*`（77 行）与 `GmatBase* theObject`（75 行），提供几何布局（top/bottom/left/right，85–90 行）与 `WidgetMode`（`DIALOG/PANEL`，61–66 行）。
- **GuiFactory**（`GuiFactory.hpp:45`）：GUI 工厂抽象基类，纯虚 `CreateWidget(ofType, parent, forObj)`（51 行）与 `SupportsType()`（53 行）；`creatables`（61 行）记录可创建的控件类型。GUI 具体实现（wxWidgets 版）在 `src/gui` 里派生出中间工厂。
- **PluginWidget**（`PluginWidget.hpp:35`）：控件基类，`RenameObject`/`UpdateObjectList`（41–43 行）响应对象增删改，`MinimizeOnRun`/`GetIcon`（44–45 行）提供运行时行为与图标。

### 2.3 interpreter —— 脚本解释器

#### 2.3.1 Interpreter.hpp / Interpreter.cpp（基类，实现达 10748 行）

**职责**：`Interpreter`（`Interpreter.hpp:76`）定义解析/写出的抽象接口，并承载「文本 ↔ GMAT 对象/命令」的全部公共逻辑（类型识别、命令装配、wrapper 构建）。

- 纯虚 `virtual bool Interpret() = 0`（94 行）与 `virtual bool Build(Gmat::WriteMode) = 0`（107 行）：读入/写出方向的两个入口，由子类实现。
- `virtual GmatBase* CreateObject(type, name, manage, createDefault, ...)`（125–127 行）：脚本里 `Create Spacecraft sat;` 的落点，内部走 `Moderator`/`FactoryManager`。
- `SetContinueOnError` / `GetContinueOnError`（142–143 行）：**解析期「Continue」开关**——设置后，一处脚本错误不终止整体解释，错误累积进 `errorList`（147 行）。
- 命令装配族 `Assemble*Command`（284–294 行）：`AssembleCommand`/`AssembleCallFunctionCommand`/`AssembleConditionalCommand`/`AssembleForCommand`/`AssembleTargetCommand`/`AssembleOptimizeCommand`…把文本描述翻译成 `GmatCommand` 子类及参数。
- `theModerator`/`theValidator`/`theObjectMap`/`theReadWriter`/`theTextParser`（202–213 行）：解释器依赖的五件套。
- `inCommandMode`/`beginMissionSeqFound`/`continueOnError` 等状态标志（224–255 行）。

`Interpreter.cpp` 是本章体量最大的实现（10748 行），但多为 `CreateXxx`/`AssembleXxx` 的长 case 分发，本章不逐行展开；其职责一句话概括：**把脚本文本的每个逻辑块翻译成对象或命令，并把命令串成链表交给 Moderator**。

#### 2.3.2 ScriptInterpreter.hpp / ScriptInterpreter.cpp（本章核心）

**职责**：`ScriptInterpreter`（`ScriptInterpreter.hpp:41`）继承 `Interpreter`，单例（`Instance()`，44 行），负责真实 `.script` 文件与函数的读取/写出。

**三趟读取**（不是字面意义的「双缓冲队列」，而是 `ReadFirstPass → ReadScript → FinalPass` 三遍扫描 + 命令链表缓冲），见 `Interpret()`（`ScriptInterpreter.cpp:150`）：

```cpp
// ScriptInterpreter.cpp:199-214（节选）
bool retval0 = ReadFirstPass();      // 199：第一遍，校验控制逻辑配对
bool retval1 = false;
bool retval2 = false;
if (retval0)
{
   retval1 = ReadScript();           // 208：第二遍，逐块解析成对象/命令
   if (retval1)
      retval2 = FinalPass();         // 214：第三遍，解析引用（wrapper）
}
```

逐行解读：
- `ReadFirstPass()`（795 行）用 `seekg` 逐字符扫一遍全文（818–882 行），只提取 `If/For/While/Target/Optimize/...` 等 `IsBranchCommand()` 分支命令名与行号（864–868 行），交给 `CheckBranchCommands()`（895 行）检查 `Begin/End` 是否配对——**在真正解析前先拦下不平衡的控制流**。
- `ReadScript()`（1151 行）用 `ScriptReadWriter::ReadFirstBlock()`（1209 行）读头部注释与首个逻辑块，之后 `while (currentBlock != "")` 循环（1224 行）：`theTextParser.EvaluateBlock()` 判定块类型（`DEFINITION_BLOCK`/`COMMAND_BLOCK`/`ASSIGNMENT_BLOCK`，1235–1237 行）→ `DecomposeBlock()` 拆行 → 分派到 `ParseDefinitionBlock`/`ParseCommandBlock`/`ParseAssignmentBlock`/`ParseIncludeBlock`（`ScriptInterpreter.hpp:129-135`，实现分别在 2364/2576/2726/3182 行）。
- `FinalPass()` 在全部对象/命令就位后统一解析引用（把 `Sat.X` 文本绑定到真实 `Parameter` 对象、把对象名绑定到 `GmatBase*`）。
- 两个重载 `Interpret(GmatCommand*, ...)`（277 行，函数/ScriptEvent 模式）与 `Interpret(filename)`（361 行，先 `CheckEncoding()` 校验 ASCII，379 行）共用同一套三趟逻辑。

**与 Moderator 的协作**：`Moderator::InterpretScript`（`Moderator.cpp:7717`）调 `theScriptInterpreter->Interpret(filename)`；命令被 `AppendCommand` 进 `Moderator::commands[]`；解释结束后 `Moderator` 补插 `BeginMissionSequence`（7808–7853 行）并置 `isRunReady`。运行时由 `Moderator::RunMission` 把命令链表 `AddCommandToSandbox` 复制进沙箱执行。GmatFunction 场景：`Sandbox::HandleGmatFunction`（`Sandbox.cpp:1770`）回调 `moderator->InterpretGmatFunction(...)`（1886 行）→ `Moderator::InterpretGmatFunction`（`Moderator.cpp:6151`）→ `ScriptInterpreter::InterpretGmatFunction`（`ScriptInterpreter.cpp:649`）就地解析函数体并返回其 FCS（函数控制序列）。

**写出**：`Build()`（695 行）/`Build(filename, mode)`（717 行）与 `Moderator::SaveScript`（7975 行）配合，把对象与命令反序列化成脚本；`ScriptInterpreter.hpp:141-164` 的 `Write*` 族按「资源段 → 命令段」的顺序分区写出。

#### 2.3.3 ScriptReadWriter.hpp / ScriptReadWriter.cpp（逻辑块读写，较详细）

**职责**：`ScriptReadWriter`（`ScriptReadWriter.hpp:39`）是文本 IO 助手，单例。`ReadFirstBlock()`（57 行）读头部注释 + 第一个逻辑块；`ReadLogicalBlock()`（59 行）读一个「逻辑块」（GMAT 脚本以 `%----` 分隔、以 `Create/Propagate/If` 等关键字起头、可能跨多行的语句集合）。内部处理跨平台换行 `CrossPlatformGetLine()`（81 行）、注释 `IsComment()`、空行 `IsBlank()`、续行 `...`（`HasEllipsis`/`HandleEllipsis`，84–85 行），并维护 `currentLineNumber`（73 行）供报错定位。`WriteText()`（60 行）负责按 `lineWidth`（71 行）折行写出。

#### 2.3.4 ApiInterpreter（C/Python API 解释器，简要）

`ApiInterpreter`（`ApiInterpreter.hpp:41`）继承 `Interpreter`，2023 年新增（作者 Alex Campbell），是**非脚本、直接 API 调用**的解析通道：`Interpret()`（47 行）从 API 命令串构建命令；`ParseCommandBlock(type, desc, inCmd)`（53 行）把 `type + desc` 组装成命令；`HandleError()`（67 行）定制错误上报。它与 `ScriptInterpreter` 并存，说明 GMAT 已从「纯脚本驱动」演进为「脚本/API 双入口」。

#### 2.3.5 MathParser / MathTree（数学表达式解析与求值，较详细）

- **MathParser**（`MathParser.hpp:46`）用**递归下降**算法把一行内联数学（如 `sqrt(x^2+y^2)*2`）拆成二叉树。公开入口 `Parse(str)`（59 行）与 `IsEquation()`（55 行）；私有 `ParseParenthesis`/`ParseAddSubtract`/`ParseMultDivide`/`ParseMatrixOps`/`ParsePower`/`ParseUnary`/`ParseMathFunctions`/`ParseUnitConversion`（82–89 行）按运算优先级自高到低逐层分解，正是递归下降的典型层次。构造收 `ObjectMap*`（50 行）以便把变量名解析成参数。
- **MathTree**（`MathTree.hpp:48`）继承 `GmatBase`，是解析产物的运行时容器：`theTopNode`（102 行）指向树根，`Evaluate()`（70 行）深度优先求值返回 `Real`，`MatrixEvaluate()`（71 行）返回矩阵；`Initialize(objectMap, globalObjectMap)`（72–73 行）把沙箱对象表灌给每个 `MathNode`（经 `SetObjectMapToRunner` 等 125–130 行）。方程命令执行时即调用这些方法（沙箱在 `Sandbox.cpp:803-828` 先 `SetupEquation` 再 `InitializeEquations`）。

#### 2.3.6 Validator（校验器，较详细）

`Validator`（`Validator.hpp:52`）单例，从 `Interpreter` 中独立出来（2008 年），专职「校验对象/命令并构建 ElementWrapper」。关键接口：`ValidateCommand()`（66 行）校验命令引用并造 wrapper；`ValidateEquation()`（68 行）校验方程；`CreateElementWrapper()`（72 行）把 `"Sat.X"` 这类文本包装成可求值的 `ElementWrapper`（分 `CreateSolarSystemWrapper`/`CreateForceModelWrapper`/`CreateParameterWrapper`/`CreatePropertyWrapper` 等，107–128 行）；`CreateParameter`/`CreateArray`/`CreateSystemParameter`（81–94 行）自动补建缺失参数。沙箱在命令 `Initialize` 失败时回调 `moderator->ValidateCommand(current)` 再重试（`Sandbox.cpp:953`），是「校验—初始化」协同的关键。

#### 2.3.7 InterpreterException（异常类，简要）

`InterpreterException`（`InterpreterException.hpp:43`）继承 `BaseException`，构造收 `details` 与 `Gmat::MessageType mt = Gmat::GENERAL_`（51 行）。默认 `GENERAL_`（而非 `ERROR_`）是为了避免函数解析失败被重复计入错误计数（注释 48–51 行，呼应 `Sandbox.cpp:1888-1894` 的 Bug 2272 处理）。

### 2.4 plugin —— 插件运行时接口

#### 2.4.1 DynamicLibrary.hpp / DynamicLibrary.cpp（动态库加载器，本章核心）

**职责**：`DynamicLibrary`（`DynamicLibrary.hpp:127`）是 GMAT 的「插件加载器」，封装各平台动态库 API，并定义了插件库必须导出的 C 函数契约（头注释 44–126 行完整说明）：

```text
必须导出：  Integer  GetFactoryCount();
            Factory* GetFactoryPointer(Integer index);
            void     SetMessageReceiver(MessageReceiver* mr);
可选导出：  GetTriggerManagerCount / GetTriggerManager(i)      —— TriggerManager
            GetMenuEntryCount / GetMenuEntry(i)                 —— 资源树节点
            GetGuiToolkitName / GetGuiFactoryCount / GetGuiFactory —— GUI 控件
```

**加载** `LoadDynamicLibrary()`（`DynamicLibrary.cpp:168`）：Windows 走 `LoadLibrary`（175–177 行，Unicode 时转宽字符），Linux/Mac 走 `dlopen`（196/206 行，Linux 先只传文件名以便走 rpath/`LD_LIBRARY_PATH`，203 行注释）。加载成功后 `GetFunction("SetMessageReceiver")`（218 行）把引擎的消息接收器注入插件，插件打印消息即回传 GMAT（220 行）。

**符号解析** `GetFunction()`（247 行）：`GetProcAddress`（257 行）/`dlsym`（259 行），找不到则抛 `GmatBaseException`（262–265 行）。`GetFactoryCount()`（280 行）与 `GetGmatFactory(index)`（312 行）据此调用插件的 `GetFactoryCount`/`GetFactoryPointer` 拿回 `Factory*`。`GetTriggerManager`/`GetMenuEntry`/`GetGuiFactory`（340 行起）同法调用对应可选入口。

**与 Moderator/FactoryManager 的衔接**（`Moderator.cpp:896 LoadAPlugin`）：

```cpp
// Moderator.cpp:945-993（节选）
DynamicLibrary *theLib = LoadLibrary(pluginName);       // 945
if (theLib != NULL)
{
   Integer fc = theLib->GetFactoryCount();               // 949
   for (Integer i = 0; i < fc; ++i)
   {
      newFactory = theLib->GetGmatFactory(i);            // 964
      theFactoryManager->RegisterFactory(newFactory);    // 967
   }
   Integer triggerCount = theLib->GetTriggerManagerCount(); // 1000
   ...
   Integer menuCount = theLib->GetMenuEntryCount();      // 1019
   ...
   Integer guiFactoryCount = theLib->GetGuiFactoryCount();  // 1049
   for (...) pluginGuiFactories.push_back(theLib->GetGuiFactory(i)); // 1050-1054
}
```

逐行解读：`LoadAPlugin` 先把路径斜杠归一化（915–919 行），Linux 控制台模式还会跳过含 `PluginWidget` 的 GUI 插件（925–943 行）；加载成功后把插件工厂逐个 `RegisterFactory`（967 行）——**这正是插件新工厂并入 2.2.2 的 `factoryList` 的入口**，从而 `CreateSpacecraft` 一类的字符串创建能命中插件类型。最后把 TriggerManager、菜单节点、GUI 工厂分别登记（1000–1054 行）。`LoadPlugins()`（848 行）遍历启动文件的 `PLUGIN` 列表逐个 `LoadAPlugin`，完成后刷新两个解释器的 `BuildCreatableObjectMaps()`（876–879 行），让插件类型立即出现在脚本识别表里。

#### 2.4.2 GuiInterface / GmatEventHandler（GUI 插件桥，简要）

- `GuiInterface`（`GuiInterface.hpp:49`）：插件访问 GUI 的单例门面，纯虚 `CreateGuiElement()`（57 行）由 GUI 具体实现；注释（44–45 行）明确「单一 GUI 工具集」约束（wxWidgets 或 Qt 二选一）。派生类设置 `instance` 指针。
- `GmatEventHandler`（`GmatEventHandler.hpp:44`）：GUI 插件事件处理基类，纯虚 `ConnectEvent(rec, parent, messageID)`（53 行）把控件事件连到资源。

#### 2.4.3 与 plugins/ 目录的呼应

`plugins/` 下每个插件项目都含 `src/.../plugin/GmatPluginFunctions.cpp`，是 2.4.1 契约的**实现端**。以 `DataCallbackPlugin` 为例（`plugins/DataCallbackPlugin/src/base/plugin/GmatPluginFunctions.cpp`）：

```cpp
// GmatPluginFunctions.cpp:45-101（节选）
extern "C"
{
   Integer GetFactoryCount() { return 1; }                       // 56-59
   Factory* GetFactoryPointer(Integer index)                     // 72-87
   {
      switch (index) { case 0: factory = new DataCallbackFactory; break; }
      return factory;
   }
   void SetMessageReceiver(MessageReceiver* mr)                  // 98-101
   {
      MessageInterface::SetMessageReceiver(mr);
   }
}
```

逐行解读：`extern "C"`（45 行）保证符号名不被 C++ 名字修饰，`dlsym/GetProcAddress` 才能按字面名找到；`GetFactoryPointer` 按 index `new` 出对应工厂（79 行）——Moderator 端拿到指针后 `RegisterFactory`。该插件还额外导出 `SetCallback`/`getLastMessage`（114/160 行）供 C 接口调用，说明插件可以自由追加导出符号。`plugins/CMakeLists_PluginTemplate.txt` 与各插件 `CMakeLists.txt` 把 `GmatPluginFunctions.cpp` 编进 `.dll/.so/.dylib`，文件名写入 `bin/gmat_startup_file.txt` 的 `PLUGIN` 行后即被 `Moderator::LoadPlugins` 加载。

## 三、关键设计模式与数据流

### 3.1 继承/组合体系

```
BaseException
 ├─ PublisherException        （executive）
 ├─ SandboxException          （executive）
 ├─ FactoryException          （factory）
 └─ InterpreterException      （interpreter）

Factory                       （抽象基类，factory）
 ├─ SpacecraftFactory / CommandFactory / SubscriberFactory / ... （30 个具体工厂）
 └─ （插件里的工厂，经 DynamicLibrary 注册）

GmatBase
 ├─ Subscriber                 （src/base/subscriber，Publisher 的订阅端）
 └─ MathTree                   （interpreter，数学表达式容器）

Interpreter                   （抽象基类，interpreter）
 ├─ ScriptInterpreter         （单例，脚本解析）
 └─ ApiInterpreter            （单例，API 解析）

Moderator（单例）—组合→ FactoryManager（单例）、ConfigManager、Publisher（单例）、
                  ScriptInterpreter（单例）、Sandbox[]、GmatCommand[]（命令链表）
Sandbox       —组合→ ObjectInitializer、Publisher*、GmatCommand*（sequence）、
                  ObjectMap（LOS/GOS）、SolarSystem*、CoordinateSystem*
Publisher（单例）—聚合→ std::list<Subscriber*>、std::map<GmatBase*, vector<DataType>*>
```

### 3.2 工厂模式的落点

1. **注册**：`Moderator::Initialize`（`Moderator.cpp:291-313`）注册内置工厂；`LoadAPlugin`（967 行）注册插件工厂；`FactoryManager::RegisterFactory`（84 行）统一入 `factoryList`。
2. **查找**：`FactoryManager::FindFactory`（1143 行）按「对象族枚举 + 类型名」匹配，插件覆盖优先（1154 行）。
3. **创建**：`Moderator::CreateObject`（2363 行）→ `FactoryManager::CreateObject/CreateXxx`（120/145 行）→ 具体工厂 `CreateXxx`（如 `SpacecraftFactory.cpp:72`）→ `new ConcreteType(name)`。
4. **默认参数设置**：对象默认值的注入不在工厂里，而在 `ObjectInitializer`（`src/base/foundation/ObjectInitializer.hpp:56`，`InitializeObjects()` 69 行）与各 `Create*` 的 `createDefault` 分支（如 `Moderator::CreateSpacecraft` 2834–2845 行给航天器设内坐标系与 `EarthMJ2000Eq`）。工厂只负责「new 出正确子类 + 命名」，默认/引用装配交给 ObjectInitializer/Validator。

### 3.3 完整数据流图（文字版）

```
脚本文件 mission.script
      │
      ▼
[Moderator::InterpretScript]  Moderator.cpp:7672
      │  设工作目录、调 theScriptInterpreter->Interpret(file)
      ▼
[ScriptInterpreter::Interpret]  ScriptInterpreter.cpp:150
      │  ReadFirstPass() 校验控制流配对  (795)
      │  ReadScript()    逐逻辑块解析     (1151)
      │      ├─ 定义块 → ParseDefinitionBlock → 经 Moderator/FactoryManager 建对象
      │      ├─ 命令块 → ParseCommandBlock    → CreateCommand 建命令并串成链表
      │      └─ 赋值块 → ParseAssignmentBlock → Validator 造 ElementWrapper
      │  FinalPass()     解析引用/wrapper   (214)
      ▼
[Moderator::commands[]]  配置命令链表（含 BeginMissionSequence 补插, 7850）
      │
      ▼
[Moderator::RunMission]  Moderator.cpp:7242
      │  Clear() → Add{ SolarSystem, TriggerManagers, InternalCS, Publisher,
      │                    Subscriber, OtherObjects, Command } ToSandbox
      ▼
[Sandbox::Initialize]  Sandbox.cpp:581
      │  克隆对象入 objectMap/globalObjectMap（LOS/GOS）
      │  ObjectInitializer::InitializeObjects() 建引用/初始化对象 (684)
      │  遍历命令链表逐个 command->Initialize()，异常收集后统一抛 (875-1013)
      ▼
[Sandbox::Execute]  Sandbox.cpp:1040
      │  while(current) { Interrupt() 检查暂停/停止
      │    current->Execute()           ← 命令内部调 Propagate 等
      │        └─ Propagate: RegisterPublishedData() 注册数据列
      │                      Publish(Real*) 每步广播轨道状态
      │    current = current->GetNext() }
      │  命令抛异常 → 附脚本行号 → 重抛 → RunComplete() → 再抛给 Moderator
      ▼
[Publisher::Publish]  Publisher.cpp:250
      │  Real 数据 → sprintf 拼字符串流 → 遍历 subscriberList
      ▼
[Subscriber::ReceiveData]   ←─ ReportFile / XYPlot / OrbitView / EphemerisFile / MessageWindow
      │   （GUI 订阅者再经 PlotInterface/PlotReceiver 刷新画布；报告订阅者写文件）
      ▼
[Publisher::NotifyEndOfRun]  Publisher.cpp:581  →  各订阅者 SetEndOfRun()
      ▼
[Moderator] 设置 runState = IDLE，GUI 报告「运行结束」
```

### 3.4 异常/Continue 语义总结

- **解析期**：`Interpreter::continueOnError`（`Interpreter.hpp:255`）由 `SetContinueOnError` 控制，脚本错误累积进 `errorList` 而非立即中断。
- **初始化期**：`Sandbox::Initialize` 逐命令 `try/catch`，异常收集进 `exceptions`/`exceptionTypes`（按 `Gmat::MessageType` 区分 ERROR/GENERAL），继续初始化后续命令，最后统一抛出（`Sandbox.cpp:979-1013`）。
- **执行期**：`Sandbox::Execute` 内层 catch 用 `AddFileInfoToErrorMessage` 补脚本定位后 `throw;`（1235–1252 行），外层 catch 做 `RunComplete`/`STOPPED` 后再 `throw;`（1255–1270 行）；`Moderator::RunMission` 按异常文本区分用户中断（`-4`）与运行错误（`-5`）。

## 四、文件清单附录

### 4.1 executive（18 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/executive/Moderator.hpp` | 总控单例声明 | `Moderator`、`Instance`、`Initialize`、`RunMission`、`InterpretScript`、`CreateObject`、`LoadPlugins` |
| `src/base/executive/Moderator.cpp` | 总控实现（11131 行） | `Initialize`、`LoadAPlugin`、`LoadLibrary`、`CreateSpacecraft`、`RunMission`、`Add*ToSandbox` |
| `src/base/executive/Sandbox.hpp` | 沙箱声明 | `Sandbox`、`runMode` 枚举、`AddObject`、`Initialize`、`Execute`、`Interrupt` |
| `src/base/executive/Sandbox.cpp` | 沙箱实现（2350 行） | `AddObject`（克隆）、`Initialize`、`Execute`、`Clear`、`HandleGmatFunction`、`UpdateClones` |
| `src/base/executive/Publisher.hpp` | 发布者声明 | `Publisher`、`Subscribe`、`Publish`（3 重载）、`RegisterPublishedData`、`subscriberList`、`providerMap` |
| `src/base/executive/Publisher.cpp` | 发布者实现（1242 行） | `Subscribe`、`Unsubscribe`、`Publish(Real/char/Integer)`、`RegisterPublishedData`、`NotifyEndOfRun` |
| `src/base/executive/PublisherException.hpp` | 发布异常声明 | `PublisherException : BaseException` |
| `src/base/executive/PublisherException.cpp` | 发布异常实现 | `PublisherException(details)`、`~PublisherException` |
| `src/base/executive/SandboxException.hpp` | 沙箱异常声明 | `SandboxException(details, mt=ERROR_)` |
| `src/base/executive/SandboxException.cpp` | 沙箱异常实现 | 构造/析构转发 |
| `src/base/executive/ListenerManager.hpp` | 解算器监听接口声明 | `ListenerManager`、`CreateSolverListener`（纯虚） |
| `src/base/executive/ListenerManager.cpp` | 监听接口实现 | 构造/析构（protected） |
| `src/base/executive/ListenerManagerInterface.hpp` | 监听静态门面声明 | `ListenerManagerInterface`、`SetListenerManager`、`CreateSolverListener` |
| `src/base/executive/ListenerManagerInterface.cpp` | 监听静态门面实现 | 转发到 `theListenerManager` |
| `src/base/executive/PlotReceiver.hpp` | 绘图接收接口声明 | `PlotReceiver`、`GmatPlot::ViewType`、约 30 个纯虚 `*Plot*` |
| `src/base/executive/PlotReceiver.cpp` | 绘图接收实现 | `SetViewType`、`GetViewType` |
| `src/base/executive/PlotInterface.hpp` | 绘图静态门面声明 | `PlotInterface`、`SetPlotReceiver`、`CreateGlPlotWindow`、`UpdateXyPlot` 等 |
| `src/base/executive/PlotInterface.cpp` | 绘图静态门面实现 | 全部静态方法转发 `thePlotReceiver` |

### 4.2 factory 顶层（60 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/factory/Factory.hpp` / `.cpp` | 工厂抽象基类 | `Factory`、`CreateObject`（抛异常）、`CreateXxx` 族、`GetListOfCreatableObjects` |
| `src/base/factory/FactoryException.hpp` / `.cpp` | 工厂异常 | `FactoryException : BaseException` |
| `src/base/factory/FactoryManager.hpp` / `.cpp` | 工厂注册/查找单例 | `FactoryManager`、`RegisterFactory`、`CreateObject/CreateXxx`、`FindFactory`、`GetBaseTypeOf` |
| `src/base/factory/AssetFactory.hpp` / `.cpp` | 创建地面站 | `CreateSpacePoint` → `GroundStation` |
| `src/base/factory/AtmosphereFactory.hpp` / `.cpp` | 创建大气模型 | `CreateAtmosphereModel` → `Exponential/MSISE90/JacchiaRoberts` |
| `src/base/factory/AttitudeFactory.hpp` / `.cpp` | 创建姿态模型 | `CreateAttitude` → `Spinner/NadirPointing/...` |
| `src/base/factory/AxisSystemFactory.hpp` / `.cpp` | 创建轴系 | `CreateAxisSystem` → `MJ2000Eq/.../TEME` |
| `src/base/factory/BurnFactory.hpp` / `.cpp` | 创建机动 | `CreateBurn` → `ImpulsiveBurn/FiniteBurn` |
| `src/base/factory/CalculatedPointFactory.hpp` / `.cpp` | 创建计算点 | `CreateCalculatedPoint` → `LibrationPoint/Barycenter` |
| `src/base/factory/CelestialBodyFactory.hpp` / `.cpp` | 创建天体 | `CreateCelestialBody` → `Star/Planet/Moon/Comet/Asteroid` |
| `src/base/factory/CommandFactory.hpp` / `.cpp` | 创建命令 | `CreateCommand` → 全部 `GmatCommand`（`Propagate/If/For/While/Target/...`） |
| `src/base/factory/CoordinateSystemFactory.hpp` / `.cpp` | 创建坐标系 | `CreateCoordinateSystem` → `CoordinateSystem` |
| `src/base/factory/FieldOfViewFactory.hpp` / `.cpp` | 创建视场 | `CreateFieldOfView` → `ConicalFOV/RectangularFOV/CustomFOV` |
| `src/base/factory/FormationFactory.hpp` / `.cpp` | 创建编队 | `CreateSpacecraft` → `Formation` |
| `src/base/factory/FunctionFactory.hpp` / `.cpp` | 创建函数 | `CreateFunction` → `GmatFunction/MatlabFunction` + 内建函数 |
| `src/base/factory/HardwareFactory.hpp` / `.cpp` | 创建硬件 | `CreateHardware` → 贮箱/推力器/电源/成像仪 |
| `src/base/factory/InterfaceFactory.hpp` / `.cpp` | 接口工厂（留口） | `CreateInterface`（基类不建，插件补） |
| `src/base/factory/MathFactory.hpp` / `.cpp` | 创建数学节点 | `CreateMathNode` → `Add/Sin/Transpose/.../FunctionRunner` |
| `src/base/factory/ODEModelFactory.hpp` / `.cpp` | 创建力模型容器 | `CreateODEModel` → `ForceModel/ODEModel` |
| `src/base/factory/ParameterFactory.hpp` / `.cpp` | 创建参数（最大） | `CreateParameter` → `Variable/Array` + 数百系统参数 |
| `src/base/factory/PhysicalModelFactory.hpp` / `.cpp` | 创建力模型 | `CreatePhysicalModel` → `GravityField/DragForce/SRP/...` |
| `src/base/factory/PlanetographicRegionFactory.hpp` / `.cpp` | 创建行星地理区 | `CreateCalculatedPoint` → `PlanetographicRegion` |
| `src/base/factory/PlateFactory.hpp` / `.cpp` | 创建板状物 | `CreatePlate` → `Plate` |
| `src/base/factory/PropagatorFactory.hpp` / `.cpp` | 创建积分器 | `CreatePropagator` → `RungeKutta89/.../AdamsBashforthMoulton` |
| `src/base/factory/PropSetupFactory.hpp` / `.cpp` | 创建传播设置 | `CreatePropSetup` → `PropSetup` |
| `src/base/factory/SolarSystemFactory.hpp` / `.cpp` | 创建太阳系 | `CreateSolarSystem` → `SolarSystem` |
| `src/base/factory/SolverFactory.hpp` / `.cpp` | 创建求解器 | `CreateSolver` → `DifferentialCorrector` |
| `src/base/factory/SpacecraftFactory.hpp` / `.cpp` | 创建航天器 | `CreateSpacecraft` → `Spacecraft` |
| `src/base/factory/StopConditionFactory.hpp` / `.cpp` | 创建停止条件 | `CreateStopCondition` → `StopCondition` |
| `src/base/factory/SubscriberFactory.hpp` / `.cpp` | 创建订阅者 | `CreateSubscriber` → `ReportFile/XYPlot/OrbitView/...` |

### 4.3 factory/guicomponents（6 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/factory/guicomponents/GmatWidget.hpp` / `.cpp` | GUI 控件基类 | `GmatWidget`、`SetWidget`、`GetGeometry`、`WidgetMode` |
| `src/base/factory/guicomponents/GuiFactory.hpp` / `.cpp` | GUI 工厂抽象基类 | `GuiFactory`、`CreateWidget`（纯虚）、`SupportsType` |
| `src/base/factory/guicomponents/PluginWidget.hpp` / `.cpp` | 控件基类 | `PluginWidget`、`RenameObject`、`UpdateObjectList`、`MinimizeOnRun` |

### 4.4 interpreter（16 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/interpreter/Interpreter.hpp` / `.cpp` | 解释器基类（10748 行） | `Interpreter`、`Interpret`（纯虚）、`Build`、`CreateObject`、`Assemble*Command` |
| `src/base/interpreter/ScriptInterpreter.hpp` / `.cpp` | 脚本解释器单例（4357 行） | `ScriptInterpreter`、`Interpret`、`ReadFirstPass`、`ReadScript`、`Parse*Block`、`InterpretGmatFunction` |
| `src/base/interpreter/ApiInterpreter.hpp` / `.cpp` | API 解释器单例 | `ApiInterpreter`、`Interpret`、`ParseCommandBlock` |
| `src/base/interpreter/ScriptReadWriter.hpp` / `.cpp` | 逻辑块读写助手 | `ScriptReadWriter`、`ReadFirstBlock`、`ReadLogicalBlock`、`HandleEllipsis` |
| `src/base/interpreter/MathParser.hpp` / `.cpp` | 递归下降数学解析（3819 行） | `MathParser`、`Parse`、`ParseAddSubtract/ParsePower/...` |
| `src/base/interpreter/MathTree.hpp` / `.cpp` | 表达式求值树 | `MathTree : GmatBase`、`Evaluate`、`MatrixEvaluate`、`Initialize` |
| `src/base/interpreter/Validator.hpp` / `.cpp` | 校验与 wrapper 构建（3785 行） | `Validator`、`ValidateCommand`、`CreateElementWrapper`、`CreateParameter` |
| `src/base/interpreter/InterpreterException.hpp` / `.cpp` | 解释器异常 | `InterpreterException : BaseException` |

### 4.5 plugin（6 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| `src/base/plugin/DynamicLibrary.hpp` / `.cpp` | 动态库加载器（561 行） | `DynamicLibrary`、`LoadDynamicLibrary`、`GetFunction`、`GetGmatFactory`、`GetMenuEntry` |
| `src/base/plugin/GuiInterface.hpp` / `.cpp` | GUI 插件桥单例 | `GuiInterface`、`Instance`、`CreateObject`、`CreateGuiElement`（纯虚） |
| `src/base/plugin/GmatEventHandler.hpp` / `.cpp` | GUI 事件处理基类 | `GmatEventHandler`、`ConnectEvent`（纯虚） |
