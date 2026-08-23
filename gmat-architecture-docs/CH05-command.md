# 第5章 src/base/command 命令系统

本章负责 `src/base/command/` 目录下的全部 C++ 源码，共 **106 个文件**（53 个 `.hpp` 头文件 + 53 个 `.cpp` 实现文件）。该目录是 GMAT 的「任务控制序列（Mission Control Sequence, MCS）」命令层：每一条脚本命令（`Propagate`、`Target`、`Maneuver`、`If` 等）都对应一个 `GmatCommand` 派生类，由解释器解析脚本行生成对象，再由 Moderator/Sandbox 组装成可执行的双向链表并逐条驱动。

> **范围说明（以 glob 实际清单为准）**：用户提到的 `DifferentialCorrector` 不是命令，而是求解器（位于 `src/base/solver/`，由 `Target` 命令通过 `Solver` 接口引用，见第 6 章求解器）；`CallMatlabFunction` 不在本目录，它是 `CallFunction` 的子类、位于 `src/plugins/`（本目录只有父类 `CallFunction` 与 `CallBuiltinGmatFunction`）；「MissionSequence」对应本目录的 `BeginMissionSequence` 命令与「任务控制序列」这一概念。这三者均不展开。

## 一、本章目录树

```
src/base/command/                     (106 文件：53 .hpp + 53 .cpp)
│
├── 命令基类与基础设施
│   ├── GmatCommand.hpp/.cpp          命令根基类（纯虚 Execute、序列链表、状态机）
│   ├── CommandException.hpp/.cpp     命令子系统专用异常
│   └── CommandUtil.hpp/.cpp          序列遍历/查找/删除等自由函数工具集
│
├── 分支与求解器框架（中间抽象层）
│   ├── BranchCommand.hpp/.cpp        分支命令基类（持有 branch[] 子分支）
│   ├── ConditionalBranch.hpp/.cpp    条件分支基类（If/While 的条件求值）
│   ├── SolverBranchCommand.hpp/.cpp  求解器循环命令基类（Target/Optimize）
│   └── SolverSequenceCommand.hpp/.cpp 求解器序列命令基类（Vary/Achieve/Minimize/NLC）
│
├── 传播与机动
│   ├── PropagationEnabledCommand.hpp/.cpp  传播使能命令基类（PropSetup/Propagator 装配）
│   ├── Propagate.hpp/.cpp                  时间/停止条件传播命令
│   ├── Maneuver.hpp/.cpp                   脉冲机动（ImpulsiveBurn）
│   ├── BeginFiniteBurn.hpp/.cpp            开启有限推力（瞬态力）
│   └── EndFiniteBurn.hpp/.cpp              关闭有限推力
│
├── 求解器控制序列命令
│   ├── Target.hpp/.cpp  /  EndTarget.hpp/.cpp   打靶（DifferentialCorrector 等）
│   ├── Optimize.hpp/.cpp / EndOptimize.hpp/.cpp 优化循环
│   ├── Vary.hpp/.cpp      变量定义
│   ├── Achieve.hpp/.cpp   目标定义
│   ├── Minimize.hpp/.cpp  最小化目标
│   ├── NonlinearConstraint.hpp/.cpp  非线性约束
│   └── RunSolver.hpp/.cpp 单命令求解器基类
│
├── 控制流命令
│   ├── If.hpp/.cpp  ElseIf.hpp/.cpp  Else.hpp/.cpp  EndIf.hpp/.cpp
│   ├── While.hpp/.cpp  EndWhile.hpp/.cpp
│   └── For.hpp/.cpp  EndFor.hpp/.cpp
│
├── 输出与绘图命令
│   ├── Report.hpp/.cpp      写入 ReportFile
│   ├── Write.hpp/.cpp       写入消息窗口/日志/ReportFile
│   ├── SaveMission.hpp/.cpp 保存整个任务脚本
│   ├── Toggle.hpp/.cpp      开关 Subscriber
│   ├── PlotCommand.hpp/.cpp 绘图命令基类
│   ├── ClearPlot.hpp/.cpp  PenUp.hpp/.cpp  PenDown.hpp/.cpp  MarkPoint.hpp/.cpp
│   ├── UpdateDynamicData.hpp/.cpp  刷新动态数据显示
│   └── FindEvents.hpp/.cpp  事件定位
│
├── 对象管理与赋值
│   ├── ManageObject.hpp/.cpp  对象管理基类（Create/Global）
│   ├── Create.hpp/.cpp        运行期创建对象
│   ├── Assignment.hpp/.cpp    赋值/方程命令（GMAT 语句）
│   ├── RHSEquation.hpp/.cpp   右端表达式（MathTree）管理器
│   ├── Stop.hpp/.cpp          中断命令
│   └── NoOp.hpp/.cpp          空操作命令
│
└── 函数与脚本
    ├── BeginMissionSequence.hpp/.cpp  进入命令模式
    ├── BeginScript.hpp/.cpp  EndScript.hpp/.cpp  ScriptEvent 块
    ├── CallFunction.hpp/.cpp  BeginFunction.hpp/.cpp  EndFunction.hpp/.cpp
    ├── CallBuiltinGmatFunction.hpp/.cpp
    └── (EndScript/EndFunction 同列)
```

## 二、逐文件/逐类讲解

### 2.1 命令基类与基础设施

#### 2.1.1 GmatCommand.hpp — 命令根基类

**职责**：定义所有命令对象共享的协议、对象关联存储、序列链表节点与运行状态。`GmatCommand` 直接继承 `GmatBase`（`src/base/foundation/GmatBase.hpp:506` 还定义了被命令复用的 `TakeAction` 虚函数）。

**类声明与「晚期绑定」哲学**（`GmatCommand.hpp:74`）：

```cpp
class GMAT_API GmatCommand : public GmatBase   // line 74
{
public:
   GmatCommand(const std::string &typeStr);
   virtual ~GmatCommand();
   ...
   virtual bool        Execute() = 0;          // line 220，纯虚函数
```

文件头注释（`GmatCommand.hpp:64-73`）明确：命令对象在脚本解析期**不绑定**具体资源对象，只记录名字；等 Sandbox 填满对象表与完整命令序列后，再统一调用 `Initialize()` 做「晚绑定」，然后从序列头开始 `Execute()`。

**参数表（`GmatCommand.hpp:242-256`）**：命令在 `GmatBase` 之上新增 3 个字符串参数：

| ID 枚举值 | 参数名 | 类型 | 含义 |
|---|---|---|---|
| `COMMENT` | `Comment` | STRING | 命令注释（只读，走特殊通道） |
| `SUMMARY` | `Summary` | STRING | 本命令执行摘要（`GetStringParameter` 时动态构造） |
| `MISSION_SUMMARY` | `MissionSummary` | STRING | 整段任务摘要 |

**子命令容器 / 序列链表（`GmatCommand.hpp:276-281`）**：

```cpp
/// Pointer to the next GmatCommand in the sequence; NULL at the end
GmatCommand          *next;          // line 277
/// Pointer to the previous GmatCommand in the sequence; NULL if at the start
GmatCommand          *previous;      // line 279
/// Indicator of the current nesting level
Integer              level;          // line 281
```

`next`/`previous` 构成双向链表，`level` 记录嵌套深度；`GetChildCommand()`（`GmatCommand.hpp:197`）在基类恒返回 `NULL`，由 `BranchCommand` 重写返回子分支入口。分支命令（`If`/`While`/`Target` 等）持有 `std::vector<GmatCommand*> branch`，通过 `GetNext()` 重写把控制权在主线与子分支间切换。

**核心协议（`GmatCommand.hpp:188-232`）**：

| 方法 | 行号 | 语义 |
|---|---|---|
| `Initialize()` | 188 | 运行前初始化：调用 `AssignObjects()` 绑定对象指针 |
| `GetNext()/GetPrevious()` | 189-190 | 取后继/前驱（分支命令重写实现跳转） |
| `Append/Insert/Remove` | 193-195 | 链表增删 |
| `InterpretAction()` | 201 | 命令内自解析脚本行（默认返回 `false`，交外部 Interpreter） |
| `VerifyObjects()` | 202 | 运行前校验（默认 `true`） |
| `DepthIncrement()` | 204 | 分支深度变化（+1/-1/0） |
| `HasPropStateChanged()` | 205 | 是否改变了传播状态（触发传播器重启） |
| `Execute()` | 220 | **纯虚**，每个命令的动作主体 |
| `SkipInterrupt()` | 221 | 是否跳过用户中断轮询（如 `Assignment` 重写为 true） |
| `RunComplete(bool)` | 222-223 | 运行终止时重置命令到空闲态 |
| `SetRunState(...)` | 224 | 设置当前 `Gmat::RunState` |
| `HasConfigurationChanged()` | 226 | 命令是否被用户修改过 |
| `HasAFunction()/NeedsServerStartup()/IsExecuting()` | 228-230 | 函数/服务端/执行中标志 |

**RunState 状态机**：命令持有的 `Gmat::RunState currentRunState`（`GmatCommand.hpp:341-342`）来自 `src/gmatutil/include/utildefs.hpp:188-199`：

```cpp
enum RunState
{
   IDLE = 10000,
   RUNNING,
   PAUSED,
   TARGETING,
   OPTIMIZING,
   ESTIMATING,
   SOLVING,
   SOLVEDPASS,
   WAITING
};
```

`GmatCommand::SetRunState`（`GmatCommand.cpp:2295-2298`）只是存值；真正消费它的是传播类（如 `Propagate::Execute` 检查 `publisher->GetRunState()==RUNNING||SOLVING` 才评估停止条件，`Propagate.cpp:4517-4518`）与求解器类。

#### 2.1.2 GmatCommand.cpp — 基类实现

**构造函数（`GmatCommand.cpp:147-196`）**：`GmatBase(Gmat::COMMAND, typeStr)` 注册对象类型，`next/previous` 置 `NULL`、`level=-1`，`currentRunState` 初始为 `Gmat::RUNNING`，并初始化 `TextParser parser`（`commandNameList` 塞入 `typeStr`）。

**析构函数（`GmatCommand.cpp:214-288`）**：关键设计——析构会**递归删除 `next`**：

```cpp
if (!this->IsOfType("BranchEnd"))   // line 228
{
   if (next) {                      // line 231
      delete next;                  // line 242  ← 级联析构整条链
   }
}
```

因此清理一条序列只需 delete 头命令；`BranchEnd`（`EndIf` 等）不删 `next`，因为它们的 `next` 回指到分支头，避免循环删除。

**序列操作**：

- `Append`（`GmatCommand.cpp:1814-1869`）：沿 `next` 走到链尾；若途中遇到 `BranchCommand` 则把追加委派给它（`current->Append(cmd)`，1837-1842 行），使新命令进入正确的子分支。非 `BranchEnd` 节点会回填 `cmd->previous`。
- `Insert`（`1937-1970`）与 `Remove`（`1985-2034`）：递归定位；`Remove` 对 `BranchEnd` 直接返回 `NULL`。
- `ForceSetNext/ForceSetPrevious`（`1772-1800`）：**危险接口**，直接改指针、跳过链表维护，注释明示「Usage can lead to serious memory leaks」。

**Initialize（`GmatCommand.cpp:1630-1720`）**：先校验 `objectMap`/`globalObjectMap`/`solarSys` 非空（缺则抛 `CommandException`），再 `isInitialized = AssignObjects()` 完成晚绑定，随后清理上轮命令摘要缓冲区（`epochData/stateData/parmData/fuelMassData`）。

**InterpretAction（`GmatCommand.cpp:2144-2147`）**：默认返回 `false`（不内部解析）；`Propagate/Maneuver/Achieve/Vary/Report` 等重写它实现命令内解析。

**RunComplete 重载**：`RunComplete(bool isHead)`（`2233-2259`）沿 `next` 遍历调用每个命令的 `RunComplete()`，遇到 `BranchEnd` 跳过以免循环；`RunComplete()`（`2268-2278`）重置 `streamID=-1`、`isInitialized=false`。

**HasConfigurationChanged（`GmatCommand.cpp:3160-3177`）**：`commandChanged` 标志的 getter/setter，供 Moderator 判断任务是否被修改。

#### 2.1.3 CommandException.hpp/.cpp — 命令专用异常

`CommandException : public BaseException`（`CommandException.hpp:42`），构造默认消息类型为 `Gmat::GENERAL_`（`CommandException.hpp:46-50`）。命令层几乎全部 `throw CommandException(...)` 报告解析、初始化、执行错误；`Stop` 命令也用它抛「有意中断」。

#### 2.1.4 CommandUtil.hpp/.cpp — 序列工具函数

`namespace GmatCommandUtil`（`CommandUtil.hpp:37-70`）提供命令链表遍历的自由函数：`GetFirstCommand/GetLastCommand/GetNextCommand/GetPreviousCommand/GetMatchingEnd/GetParentCommand/GetSubParent/RemoveCommand/IsElseFoundInIf/ClearCommandSeq/IsAfter` 以及调试用的 `GetCommandSeqString/ShowCommand`。它是 Moderator、GUI 与命令对象之间共享的「序列结构」工具层，不依赖对象业务逻辑。

### 2.2 分支与求解器框架（中间抽象层）

#### 2.2.1 BranchCommand.hpp/.cpp — 分支命令基类

`BranchCommand : public GmatCommand`（`BranchCommand.hpp:41`）。持有 `std::vector<GmatCommand*> branch`（`BranchCommand.hpp:119`）与一组状态标志 `commandComplete/commandExecuting/branchExecuting/branchToExecute/branchToFill`（`120-129`）。

关键接口：

```cpp
void     AddBranch(GmatCommand *cmd, Integer which = 0);   // line 49
virtual bool ExecuteBranch(Integer which = 0);              // line 52
virtual bool Append(GmatCommand *cmd);                      // line 55  重写链表维护
virtual GmatCommand* GetNext();                             // line 77  重写跳转
virtual GmatCommand* GetChildCommand(Integer whichOne = 0); // line 78  返回子分支
```

`BranchCommand` 把 `Append/Insert/Remove` 委派到「当前正在填充的分支」（`branchToFill`），这是 `If`/`While`/`Target` 等命令能把后续脚本行收集进自己子分支的机制。`ExecuteBranch` 逐条执行子分支，并维护 `current`/`lastFired` 指针（`134-137`）。

#### 2.2.2 ConditionalBranch.hpp/.cpp — 条件分支基类

`ConditionalBranch : public BranchCommand`（`ConditionalBranch.hpp:49`）。为 `If`/`While` 提供**条件求值**：`SetCondition(lhs, op, rhs, atIndex)` 与 `SetConditionOperator(op, atIndex)`（`62-67`），内部保存 `lhsList/opStrings/rhsList` 及对应的 `lhsWrappers/rhsWrappers`（`ElementWrapper*` 向量，`166-181`）。

运算符与逻辑符枚举（`ConditionalBranch.hpp:145-161`）：

```cpp
enum OpType { EQUAL_TO=0, NOT_EQUAL, GREATER_THAN, LESS_THAN,
              GREATER_OR_EQUAL, LESS_OR_EQUAL, NumberOfOperators };   // line 145
enum LogicalOpType { AND=0, OR, NumberOfLogicalOperators };            // line 156
```

`EvaluateCondition(which)` / `EvaluateAllConditions()`（`123-124`）用 `ElementWrapper` 求值两侧并与 `OpType` 比较，`LogicalOpType` 连接多条件。

#### 2.2.3 SolverBranchCommand.hpp/.cpp — 求解器循环命令基类

`SolverBranchCommand : public BranchCommand`（`SolverBranchCommand.hpp:43`），是 `Target`/`Optimize` 的父类，连接 `Solver` 对象并驱动求解状态机。

核心成员与参数（`SolverBranchCommand.hpp:126-179`）：

```cpp
std::list<ISolverListener*> listeners;   // line 126 求解器窗口监听者
std::string         solverName;          // line 127 求解器名字（如 "DC1"）
Solver              *theSolver;          // line 128 求解器实例
solverStartMode     startMode;           // line 129
solverExitMode      exitMode;            // line 130
```

参数 ID（`170-178`）：`SOLVER_NAME_ID`（即 `SolverName`）、`SOLVER_SOLVE_MODE`、`SOLVER_EXIT_MODE`、`SOLVER_SOLVE_MODE_OPTIONS`、`SOLVER_EXIT_MODE_OPTIONS`、`SOLVER_SHOW_PROGRESS`。

求解进入/退出模式枚举（`111-124`）：

```cpp
enum solverStartMode { RUN_INITIAL_GUESS, RUN_AND_SOLVE, RUN_SOLUTION };  // line 111
enum solverExitMode  { DISCARD_AND_CONTINUE, SAVE_AND_CONTINUE, STOP };   // line 119
```

`solverName` 正是用户要求的「SolverName 参数」；`SolveMode`/`ExitMode` 对应脚本 `Target DC1 {SolveMode = Solve, ExitMode = DiscardAndContinue};`。`StoreLoopData/ResetLoopData/FreeLoopData/ApplySolution`（`152-156`）负责在每次迭代前保存航天器初态、迭代失败时回滚。`TakeAction` 被重写（`62-63`）以把「ResetLoopData」等动作广播给子分支命令。

#### 2.2.4 SolverSequenceCommand.hpp/.cpp — 求解器序列命令基类

`SolverSequenceCommand : public GmatCommand`（`SolverSequenceCommand.hpp:46`）。为 `Vary/Achieve/Minimize/NonlinearConstraint` 提供公共的「求解器名」接口，成员只有一个 `std::string solverName`（`93`）与参数 `SOLVER_NAME`（`98`）。类注释（`38-44`）说明它是「partial refactorization」：只抽取了名字访问的公共部分，完整重构待办。

### 2.3 传播与机动

#### 2.3.1 PropagationEnabledCommand.hpp/.cpp — 传播使能基类

`PropagationEnabledCommand : public GmatCommand`（`PropagationEnabledCommand.hpp:59`），是 `Propagate` 与 `RunSolver` 的父类，封装「驱动传播器」的通用接口。

关键成员（`PropagationEnabledCommand.hpp:85-158`）：

```cpp
StringArray                   propagatorNames;   // line 85  PropSetup 名字
std::vector<PropSetup*>       propagators;       // line 89  PropSetup 指针
std::vector<StringArray>      propObjectNames;   // line 93  每套传播的航天器名
std::vector<Propagator*>      p;                 // line 134 传播器
std::vector<ODEModel*>        fm;                // line 136 力模型
std::vector<PropagationStateManager*> psm;       // line 138 状态管理器
std::vector<PhysicalModel*>  *transientForces;   // line 140 瞬态力（有限推力）
```

接口 `PrepareToPropagate/AssemblePropagators/Step/TakeAStep`（`164-167`）与宏 `TIME_ROUNDOFF/DEFAULT_STOP_TOLERANCE`（`48-49`）定义时间舍入与停止容差。瞬态力机制（`AddTransientForce/ClearTransientForces`，`178-180`）由 `BeginFiniteBurn/EndFiniteBurn` 增删，供 `ODEModel` 在传播中按需开关推力。

#### 2.3.2 Propagate.hpp/.cpp — 传播命令

`Propagate : public PropagationEnabledCommand`（`Propagate.hpp:67`）。类注释（`52-66`）说明三种传播模式：同步模式（多套 PropSetup 同步时间）、单步模式（一次积分一步）、BackProp（反向传播）。

**参数 ID（`Propagate.hpp:308-323`）**：`AVAILABLE_PROP_MODES`、`PROP_COUPLED`（多航天器耦合）、`INTERRUPT_FREQUENCY`、`STOP_ACCURACY`、`SAT_NAME`、`PROP_NAME`、`STOP_WHEN`、`PROP_FORWARD`、`PROP_ALL_STM`、`CALC_ALL_AMATRIX`、`CALC_ALL_COVARIANCE`、`ORBIT_COLOR`。

**关键成员**：`propName/satName`（`188-191`）、`stopWhen`（`std::vector<StopCondition*>`，`202`）、`stopTrigger`（`206`）、`stopSats/stopWrappers/goalWrappers`（`218-224`）。传播模式枚举 `PropModes { INDEPENDENT, SYNCHRONIZED, BACK_PROP }`（`254-260`）。

**Execute 核心逻辑（`Propagate.cpp:4479-4588`）**：`Execute()` 是可重入的——先检查 `transientForces` 数量是否变化（`4490-4499`，变化则重置 `hasFired`）；首次进入调用 `PrepareToPropagate()`（`4511`），并在 `publisher->GetRunState()==RUNNING||SOLVING` 时**预评估停止条件**（`4517-4567`），若某个停止条件在第一步就已满足且上次已触发，则置 `checkFirstStep` 并跳过评估；随后进入 `while (!stopCondMet)` 主循环（`4574`），循环内对每个力模型 `fm[i]->UpdateInitialData(...)`（`4580`）或 `p[i]->UpdateFromSpaceObject()`（`4582`）刷新初始数据，再按步长推进。停止精度由 `stopWhen[i]->Evaluate()` 与 `timeAccuracy/firstStepTolerance` 比较决定。传播器内部机理见 `[第7章](CH07-propagator.md)`。

**脚本示例（1 行）**：

```script
Propagate DefaultProp(Sat1) {Sat1.ElapsedSecs = 600};
```

`Propagate` 关键字、传播器名 `DefaultProp`、航天器 `Sat1`、停止条件 `Sat1.ElapsedSecs = 600` 四要素一一对应 `propName/satName/stopWhen`。

#### 2.3.3 Maneuver.hpp/.cpp — 脉冲机动

`Maneuver : public GmatCommand`（`Maneuver.hpp:54`）。头文件注释给出标准脚本（`Maneuver.hpp:41-53`）：

```script
Create ImpulsiveBurn burn;
burn.CoordinateSystem = Local;
burn.Element1 = 0.125;         % km/s
Maneuver burn(Sat1);
```

成员 `burnName/burn/satName/sat`（`Maneuver.hpp:117-123`）与参数 `burnNameID/satNameID/backPropID`（`151-157`）。`backPropID` 控制是否按反向传播施加机动。

**Execute（`Maneuver.cpp:704-747`）**：取航天器历元 `sat->GetRealParameter("A1Epoch")`（`712`），`burn->SetSpacecraftToManeuver(sat)`（`721`），通知 Publisher 进入机动态 `publisher->SetManeuvering(this, true, epoch, satName, "ImpulsiveBurn")`（`724`），执行 `burn->Fire(NULL, epoch, maneuverBackwards)`（`726`）完成瞬时速度改变，再复位 Publisher 机动态（`729`）。

#### 2.3.4 BeginFiniteBurn.hpp/.cpp 与 EndFiniteBurn.hpp/.cpp

两者都是 `GmatCommand` 直接子类（`BeginFiniteBurn.hpp:46`、`EndFiniteBurn.hpp:46`），围绕**瞬态力**机制配合传播：`BeginFiniteBurn` 把 `FiniteBurn` 对应的 `FiniteThrust`（`burnForce`，`BeginFiniteBurn.hpp:90`）加入 Sandbox 的 `transientForces` 向量并激活推力器（`BeginFiniteBurn.cpp:623-702`），`EndFiniteBurn` 反向移除并熄灭推力器（`EndFiniteBurn.cpp:471-576`）。脚本成对使用：

```script
BeginFiniteBurn burn1(Sat1);
Propagate prop1(Sat1) {Sat1.ElapsedSecs = 100};
EndFiniteBurn burn1(Sat1);
```

### 2.4 求解器控制序列命令

#### 2.4.1 Target.hpp/.cpp 与 EndTarget.hpp/.cpp — 打靶循环

`Target : public SolverBranchCommand`（`Target.hpp:50`）。成员 `targeterConverged/targeterInFunctionInitialized/targeterRunOnce`（`95-97`）与参数 `TargeterConvergedID`（`101`）。

**Execute（`Target.cpp:624-713`）**：驱动求解器状态机。取 `Solver::SolverState state = theSolver->GetState()`（`652`）；命令完成后重置（`667-673`）；`!commandExecuting` 时 `StoreLoopData()` 保存初态再 `SolverBranchCommand::Execute()`，并 `theSolver->TakeAction("Reset")`（`682-693`）；`branchExecuting` 时执行子分支 `ExecuteBranch()`（`699`），分支跑完后根据 `state==Solver::FINISHED` 决定 PenDown/Lighten 或 PenUp 绘图订阅者（`702-713`）。`EndTarget` 的 `Execute()` 只 `BuildCommandSummary`（`EndTarget.cpp:136-149`），其 `next` 回指 `Target` 形成迭代环。

**脚本示例**：

```script
Target DC1 {SolveMode = Solve, ExitMode = DiscardAndContinue};
Vary DC1(Sat1.X = 7000, {Perturbation = 0.0001, Lower = 6000, Upper = 8000});
Achieve DC1(Sat1.RMAG = 42164, {Tolerance = 0.1});
Maneuver burn1(Sat1);
Propagate prop1(Sat1);
EndTarget;
```

#### 2.4.2 Vary.hpp/.cpp — 变量定义

`Vary : public SolverSequenceCommand`（`Vary.hpp:60`）。参数 ID（`142-155`）：`SOLVER_NAME`、`VARIABLE_NAME`、`INITIAL_VALUE`、`PERTURBATION`、`VARIABLE_LOWER`、`VARIABLE_UPPER`、`VARIABLE_MAXIMUM_STEP`、`ADDITIVE_SCALE_FACTOR`、`MULTIPLICATIVE_SCALE_FACTOR`、`CURRENT_VALUE`。对应成员是 `ElementWrapper*` 向量（`168-204`）。

**Execute（`Vary.cpp:1459-1518`）**：首次执行（`!solverDataFinalized`）时读取初值/扰动/上下界/最大步长/加性与乘性缩放因子，做量纲缩放（`varData[0..5]`，`1510-1517`）后 `solver->SetSolverResults(...)` 把变量登记给求解器；后续执行刷新变量值。`SetInitialValue`（`130`）供求解器回写校正值。

#### 2.4.3 Achieve.hpp/.cpp — 目标定义

`Achieve : public SolverSequenceCommand`（`Achieve.hpp:45`）。参数（`137-144`）：`targeterNameID/goalNameID/goalValueID/toleranceID/achievedValueID`；成员 `targeterName/goalName/goal/achieve/tolerance/targeter/goalId/achievedValue`（`112-132`）。

**Execute（`Achieve.cpp:1089-1158`）**：首次执行把目标值与容差 `goalData[0]=goal->EvaluateReal()`, `goalData[1]=tolerance->EvaluateReal()` 传给 `targeter->SetSolverResults(goalData, goalName)`（`1110-1123`）；后续每次迭代用 `achieve->EvaluateReal()` 更新浮动目标 `targeter->UpdateSolverGoal(goalId, val)`（`1144`），再用 `targeter->SetResultValue(goalId, val)` 提交当前达成值（`1152`）。

#### 2.4.4 Optimize.hpp/.cpp 与 EndOptimize.hpp/.cpp — 优化循环

`Optimize : public SolverBranchCommand`（`Optimize.hpp:39`）。参数 `OPTIMIZER_NAME/OPTIMIZER_CONVERGED`（`94-99`）。成员 `RunInternalSolver/RunExternalSolver`（`91-92`）区分内置优化器与外置（如 MATLAB）优化器。

**Execute（`Optimize.cpp:568-637`）**：先判断是否需要重初始化（`576-587`）；`!commandExecuting` 时 `StoreLoopData()` + `SolverBranchCommand::Execute()` + `theSolver->TakeAction("Reset")`（`610-628`）；随后按 `theSolver->IsSolverInternal()` 分支调用 `RunInternalSolver(state)` 或 `RunExternalSolver(state)`（`634-637`）。`ExecuteBranch` 被重写（`Optimize.hpp:56`）以管理绘图 PenUp/PenDown。

#### 2.4.5 Minimize.hpp/.cpp — 最小化目标

`Minimize : public SolverSequenceCommand`（`Minimize.hpp:45`）。参数 `OPTIMIZER_NAME/OBJECTIVE_NAME/OBJECTIVE_VALUE`（`128-134`）。**Execute（`Minimize.cpp:871-925`）**：首次把目标函数当前值 `objective->EvaluateReal()` 经 `optimizer->SetSolverResults(minData, objectiveName, "Objective")` 登记（`887-890`），之后每次迭代 `optimizer->SetResultValue(objId, val, "Objective")` 提交目标值（`907`）。

#### 2.4.6 NonlinearConstraint.hpp/.cpp — 非线性约束

`NonlinearConstraint : public SolverSequenceCommand`（`NonlinearConstraint.hpp:45`）。参数（`115-125`）：`OPTIMIZER_NAME/CONSTRAINT_ARG1/LHS_CONSTRAINT_VALUE/OPERATOR/CONSTRAINT_ARG2/RHS_CONSTRAINT_VALUE/TOLERANCE`。约束运算符枚举 `Operator { LESS_THAN_OR_EQUAL, GREATER_THAN_OR_EQUAL, EQUAL }`（`131-136`）。

**Execute（`NonlinearConstraint.cpp:1190-1254`）**：首次把约束登记给优化器（`optimizer->SetSolverResults(&conData, arg1Name, isIneqString)`，`1211`）；后续求 `desiredValue=arg2->EvaluateReal()`、`constraintValue=arg1->EvaluateReal()`，按 `op`（`EQUAL/LESS_THAN_OR_EQUAL/...`）把差值作为约束残差提交给优化器（`1226-1254`）。

#### 2.4.7 RunSolver.hpp/.cpp — 单命令求解器基类

`RunSolver : public PropagationEnabledCommand`（`RunSolver.hpp:45`）。类注释（`38-44`）说明它是「单命令版」求解器状态机命令的基类（对应 `RunSimulator`/`RunEstimator` 等插件命令），与 `SolverBranchCommand`（求解器控制序列版）互补。成员仅 `std::string solverName`（`63`）。

### 2.5 控制流命令

#### 2.5.1 If.hpp/.cpp、ElseIf.hpp/.cpp、Else.hpp/.cpp、EndIf.hpp/.cpp

`If : public ConditionalBranch`（`If.hpp:46`），参数 `NEST_LEVEL`（`88`）记录嵌套深度。

**If::Execute（`If.cpp:185-258`）**：若 `branchExecuting` 则继续 `ExecuteBranch(branchToExecute)`（`195`），分支结束则置完成；否则 `ConditionalBranch::Execute()` 后 `EvaluateAllConditions()` 判定真/假（`217`），全真执行第 0 分支、存在 `Else` 则执行第 1 分支、否则直接完成（`217-249`）。`Else` 与 `EndIf` 的 `Execute()` 仅 `BuildCommandSummary(true)`（`Else.cpp:144-148`、`EndIf.cpp:133-137`）。`ElseIf`（`ElseIf.hpp:63`）在编译宏 `__INCLUDE_ELSEIF__` 保护下（默认关闭，见 `CommandFactory.cpp:160-163`），结构上预留但未默认启用。

**脚本示例**：

```script
If Sat1.ElapsedSecs > 600
   Maneuver burn1(Sat1);
Else
   Propagate prop1(Sat1);
EndIf
```

#### 2.5.2 While.hpp/.cpp 与 EndWhile.hpp/.cpp

`While : public ConditionalBranch`（`While.hpp:45`）。**Execute（`While.cpp:282-371`）**：先检测空循环（`GetChildCommand(0)->IsOfType("EndWhile")` 则告警跳过，`296-312`）；对含 `Elapsed` 的时间条件做「重置初始历元」的特殊处理（`317-353`，使 `ElapsedSecs` 条件在每轮循环重新计时）；`branchExecuting` 时 `ExecuteBranch()`，否则 `ConditionalBranch::Execute()` 后按条件决定是否进入循环体。`EndWhile::Execute()` 仅摘要（`EndWhile.cpp:140-150`），其 `next` 回指 `While` 形成循环。

```script
While Sat1.ElapsedDays < 1
   Propagate prop1(Sat1);
EndWhile
```

#### 2.5.3 For.hpp/.cpp 与 EndFor.hpp/.cpp

`For : public BranchCommand`（`For.hpp:45`）。参数 `START_VALUE/END_VALUE/STEP/INDEX_NAME/START_NAME/END_NAME/INCREMENT_NAME`（`114-124`），成员 `startValue/endValue/stepSize/currentValue/numPasses/currentPass` 及四个 `ElementWrapper*`（`139-166`）。

**Execute（`For.cpp:312-388`）**：分支执行完后 `currentValue += stepSize`（`334`），并在越界前把值写回索引变量 `indexWrapper->SetReal(currentValue)`（`345-347`）；`StillLooping()` 判定是否继续（`368`），否则 `publisher->FlushBuffers()` 并把 `currentValue` 重置为 `UNINITIALIZED_VALUE` 以便下次重跑（`377-383`）。`RunComplete`（`397-401`）同样重置计数。

```script
For I = 1 : 10
   Propagate prop1(Sat1);
EndFor
```

### 2.6 输出与绘图命令

#### 2.6.1 Report.hpp/.cpp — 写 ReportFile

`Report : public GmatCommand`（`Report.hpp:52`）。参数 `REPORTFILE/ADD`（`142-147`）；成员 `rfName/reporter/parmNames/parms/parmWrappers`（`117-135`）。

**Execute（`Report.cpp:928-1000`）**：校验 `parms`/`reporter` 非空后，从 `ReportFile` 读 `Precision/LeftJustify/ZeroFill/ColumnWidth` 配置（`949-960`），需要时写表头（`978-979`），再 `reporter->TakeAction("ActivateForReport","On")` + `reporter->WriteData(parmWrappers)` 落盘（`988-989`）。类注释（`48-50`）说明 Publisher 暂不能正确传字符串，故 Report 直写 ReportFile。

```script
Report rf1 Sat1.X Sat1.Y Sat1.Z;
```

#### 2.6.2 Write.hpp/.cpp — 写消息窗口/日志

`Write : public GmatCommand`（`Write.hpp:43`）。输出风格枚举 `CONCISE/VERBOSE/SCRIPTABLE`（`141-146`）与 `ADD` 参数（`150-154`）。

**Execute（`Write.cpp:568-637`）**：先对可写对象 `SetForceGenerateObjectString(true)`（`589`），若绑定 `ReportFile` 则 `ExecuteReport()`（`598-599`），随后按 `outputStyle` 把每个 `ElementWrapper` 转成字符串（`CONCISE`→`ToString()`，`VERBOSE`→`"<desc> ="` 前缀，`SCRIPTABLE`→`Create Variable ...;` 形式，`618-637`）写入消息窗口。

```script
Write Sat1.X " km/s";
```

#### 2.6.3 SaveMission.hpp/.cpp — 保存任务脚本

`SaveMission : public GmatCommand`（`SaveMission.hpp:39`），参数 `FILE_NAME`（`82-86`）。**Execute（`SaveMission.cpp:131-170`）**：仅当该命令是主脚本（非函数内）**且是最后一条命令**时（`currentFunction==NULL && GetLastCommand(this)==this`，`135`），取 `Moderator::Instance()->GetScript()` 写盘，无扩展名时补 `.script`（`149-150`）。

```script
SaveMission myMission;
```

#### 2.6.4 Toggle.hpp/.cpp — 开关订阅者

`Toggle : public GmatCommand`（`Toggle.hpp:47`）。成员 `toggleState/subNames/subs`（`98-102`）。**Execute（`Toggle.cpp:196-247`）**：遍历订阅者列表，逐个 `(*s)->Activate(toggleState)` 并 `TakeAction("ToggleOn"/"ToggleOff")`（`227-231`）；函数内会先 `BuildSubscriberList()` 刷新指针（`216`）。

```script
Toggle plot1 Off;
```

#### 2.6.5 PlotCommand.hpp/.cpp 及其子类

`PlotCommand : public GmatCommand`（`PlotCommand.hpp:42`）是绘图命令基类，参数 `SUBSCRIBER`（`89`），成员 `plotNameList/thePlotList`（`94-95`）。四个子类都只重写 `Initialize/Execute`，动作是调用 `thePlotList` 中订阅者的 `TakeAction`：

- `ClearPlot::Execute`（`ClearPlot.cpp:179`）→ `TakeAction("ClearData")`；
- `PenUp::Execute`（`PenUp.cpp:176`）→ 停止绘制；
- `PenDown::Execute`（`PenDown.cpp:180`）→ 恢复绘制；
- `MarkPoint::Execute`（`MarkPoint.cpp:181`）→ 在图上做标记点。

#### 2.6.6 UpdateDynamicData.hpp/.cpp — 刷新动态数据

`UpdateDynamicData : public GmatCommand`（`UpdateDynamicData.hpp:40`），参数 `DYNAMIC_DATA_DISPLAY/ADD_UPDATE_DATA/AVAILABLE_PARAMS`（`89-95`），成员 `dynamicData/dynamicDataStruct/dynamicTableName/dataToUpdate`（`79-87`）。`Execute`（`UpdateDynamicData.cpp:539`）把参数值写入 `DynamicDataDisplay` 供 GUI 表格刷新。

#### 2.6.7 FindEvents.hpp/.cpp — 事件定位

`FindEvents : public GmatCommand`（`FindEvents.hpp:41`），参数 `EVENT_LOCATOR/APPEND_FLAG`（`104-109`），成员 `eventLocatorName/eventLocator/appendFlag`（`117-123`）。`Execute`（`FindEvents.cpp:551`）驱动 `EventLocator` 在传播结果上定位事件（如进/出阴影、交会等）并写报告。

### 2.7 对象管理与赋值

#### 2.7.1 ManageObject.hpp/.cpp 与 Create.hpp/.cpp

`ManageObject : public GmatCommand`（`ManageObject.hpp:43`）是 `Create`（及注释掉的 `Global`）的基类，参数 `OBJECT_NAMES`（`88-92`）。`Create : public ManageObject`（`Create.hpp:42`）参数 `OBJECT_TYPE`（`76-80`）。

`Create` 的 `Execute()` 是**空操作**（`Create.cpp:417-421`）——真正的创建发生在 `Initialize()`（`Create.cpp:313`）里：克隆参考对象并插入本地/全局对象存储。`DEFAULT_TO_NO_CLONES` 与 `DEFAULT_TO_NO_REFOBJECTS`（`Create.hpp:72-73`）表明它不参与克隆传播。

```script
Create Spacecraft Sat1;
Create Array A[3,3];
```

#### 2.7.2 Assignment.hpp/.cpp 与 RHSEquation.hpp/.cpp — 赋值/方程

`Assignment : public GmatCommand`（`Assignment.hpp:50`）。头注释给出三种形式（`Assignment.hpp:30-35`）：`GMAT object.parameter = value;`、`GMAT variable = parameter;`、`GMAT variable = equation;`。成员 `lhs/rhs/lhsWrapper/rhsWrapper/rhsEquation/mathWrapperMap`（`116-130`）。

**Execute（`Assignment.cpp:987-1066`）**：校验 `lhsWrapper` 与 `rhsWrapper/rhsEquation` 非空（`1010-1018`）；`rhsEquation==NULL` 时用 `ElementWrapper::SetValue` 做普通赋值，否则运行右端 `MathTree` 计算（`1059` 起）；`AffectsClones()/GetUpdatedObject()/GetUpdatedObjectParameterIndex()`（`Assignment.hpp:107-109`）使赋值结果能同步到克隆对象。`SkipInterrupt()`（`Assignment.hpp:85`）被重写为跳过中断轮询，保证赋值原子性。

`RHSEquation`（`RHSEquation.hpp:43`）**不是命令**，是 `Assignment` 右端表达式的管理器：`BuildExpression` 解析字符串成 `MathTree`（`55-57`），`RunMathTree` 求值（`58`），`GetMathWrapperMap` 暴露中间变量（`61`）。

```script
Sat1.X = 7000;
GMAT myVar = Sat1.SMA / 2;
```

#### 2.7.3 Stop.hpp/.cpp 与 NoOp.hpp/.cpp

`Stop` 的 `Execute()` 直接抛异常（`Stop.cpp:114-119`）：

```cpp
throw CommandException(
   "Command Sequence intentionally interrupted by Stop command.\n");
```

用于脚本调试断点。`NoOp` 的 `Execute()`（`NoOp.cpp:107`）为空操作，作为 Moderator 序列链表的占位头节点。

### 2.8 函数与脚本

#### 2.8.1 BeginMissionSequence.hpp/.cpp

`BeginMissionSequence : public GmatCommand`（`BeginMissionSequence.hpp:42`）。`Execute()` 仅 `BuildCommandSummary(true)`（`BeginMissionSequence.cpp:112-116`）。它是 MCS 的「起始标记」：`CommandFactory` 把它注册为 `sequenceStarters`（`CommandFactory.cpp:244`），Moderator 据此切换命令模式。

```script
BeginMissionSequence;
```

#### 2.8.2 BeginScript.hpp/.cpp 与 EndScript.hpp/.cpp

`BeginScript : public GmatCommand`（`BeginScript.hpp:44`），标记一段在 GUI ScriptEvent 面板中逐字显示的脚本块（`BeginScript.hpp:27-30`）；`EndScript` 成对收尾。`Execute()` 均为空操作（`BeginScript.cpp:123`、`EndScript.cpp:108`）。

#### 2.8.3 CallFunction.hpp/.cpp 与 CallBuiltinGmatFunction.hpp/.cpp

`CallFunction : public GmatCommand`（`CallFunction.hpp:44`）。参数 `FUNCTION_NAME/ADD_INPUT/ADD_OUTPUT/COMMAND_STREAM`（`149-156`）；成员 `mFunction/mFunctionName/mInputList/mOutputList/fm(FunctionManager)/isGmatFunction/isMatlabFunction/isBuiltinGmatFunction`（`135-144`）。`Execute`（`CallFunction.cpp:1103`）通过内部 `FunctionManager fm` 执行被调函数体；`IsMatlabFunctionCall()`（`72`）识别 MATLAB 函数（真正的 `CallMatlabFunction` 子类在 plugins，见本章范围说明）。`CallBuiltinGmatFunction : public CallFunction`（`CallBuiltinGmatFunction.hpp:35`）重写 `Initialize/Execute/RunComplete`（`163/236` 行）执行内置 GMAT 函数。

#### 2.8.4 BeginFunction.hpp/.cpp 与 EndFunction.hpp/.cpp

`BeginFunction : public GmatCommand`（`BeginFunction.hpp:43`），参数 `FUNCTION_NAME/INPUTS/OUTPUTS/INPUT_OBJECT_NAMES/OUTPUT_OBJECT_NAMES`（`139-147`），成员 `gfun/inputs/outputs/localMap/returnObjects`（`113-126`）。`BeginFunction` 是 `GmatFunction` 函数体的入口命令：`Initialize`（`BeginFunction.cpp:689`）把函数形参与调用实参通过 `localMap` 建立局部变量/克隆映射，`Execute`（`1057`）依次执行函数体命令；`EndFunction`（`EndFunction.hpp:41`）标记函数体结束，`Execute`（`EndFunction.cpp:92`）处理返回对象。

## 三、关键设计模式与数据流

### 3.1 命令继承树（ASCII）

`GmatBase`（`src/base/foundation/GmatBase.hpp`）之上的命令体系如下（本目录 53 个类，其中 52 个是命令类，`CommandException` 与 `RHSEquation` 非命令）：

```
GmatBase
└── GmatCommand                              ← 根基类（纯虚 Execute）
    ├── NoOp
    ├── Stop
    ├── BeginMissionSequence
    ├── BeginScript / EndScript
    ├── Maneuver
    ├── Report / Write / SaveMission / Toggle
    ├── Assignment
    ├── BeginFunction / EndFunction
    ├── BeginFiniteBurn / EndFiniteBurn
    ├── FindEvents / UpdateDynamicData
    ├── CallFunction
    │   └── CallBuiltinGmatFunction
    ├── ManageObject
    │   └── Create
    ├── PlotCommand
    │   ├── ClearPlot
    │   ├── PenUp
    │   ├── PenDown
    │   └── MarkPoint
    ├── PropagationEnabledCommand            ← 传播能力抽象
    │   ├── Propagate
    │   └── RunSolver
    ├── SolverSequenceCommand                ← 求解器序列命令公共名接口
    │   ├── Vary
    │   ├── Achieve
    │   ├── Minimize
    │   └── NonlinearConstraint
    ├── Else / ElseIf / EndIf / EndWhile / EndFor / EndTarget / EndOptimize   ← 分支端点(直接继承)
    └── BranchCommand                        ← 分支能力抽象
        ├── For
        ├── ConditionalBranch
        │   ├── If
        │   └── While
        └── SolverBranchCommand
            ├── Target
            └── Optimize
```

设计要点：① 能力按「横切关注点」分层——传播能力（`PropagationEnabledCommand`）、分支能力（`BranchCommand`）、条件求值（`ConditionalBranch`）、求解器驱动（`SolverBranchCommand`）各占一层；② 分支端点（`EndIf` 等）刻意直接继承 `GmatCommand` 而非 `BranchCommand`，因为它们的 `next` 回指分支头、析构时不级联删除（见 `GmatCommand.cpp:228` 的 `IsOfType("BranchEnd")` 判断）；③ 多继承被完全避免，用组合（`Solver`/`ElementWrapper`/`StopCondition` 指针）表达「求解」「求值」「停止」等行为。

### 3.2 工厂模式与脚本行 → 对象

命令实例全部由 `CommandFactory`（`src/base/factory/CommandFactory.cpp`，虽不在本目录但直接消费本目录类）创建：

- `CommandFactory::CreateCommand`（`CommandFactory.cpp:127-223`）是一串 `if (ofType == "...") return new X;` 的显式工厂（非注册表映射）。
- `creatables` 列表（`238-287`）登记 40+ 个脚本关键字：`Achieve/Assignment/BeginFiniteBurn/BeginMissionSequence/BeginScript/CallFunction/CallBuiltinGmatFunction/ClearPlot/Create/Write/Else/(ElseIf)/EndFor/EndIf/EndOptimize/EndTarget/EndWhile/EndScript/EndFiniteBurn/Equation/For/If/GMAT/Maneuver/MarkPoint/Minimize/NonlinearConstraint/NoOp/Optimize/PenUp/PenDown/Propagate/Report/SaveMission/ScriptEvent/Stop/FindEvents/Target/Toggle/Vary/While/UpdateDynamicData`。
- `unviewables`（`289-331`）列出 GUI MissionTree 菜单中隐藏的命令（如 `NoOp/BeginMissionSequence`、求解器内部的 `Vary/Achieve/Minimize/NonlinearConstraint`、自动生成的 `If/For/While` 等）。
- `GmatType::RegisterType(Gmat::COMMAND, "Command")`（`333`）注册对象类型。

脚本解析流程：`Interpreter` 读到 MCS 行 → `IsCommandType`（`src/base/interpreter/Interpreter.cpp:10406`）识别关键字 → `Moderator::CreateCommand`（`Moderator.hpp:381`）经工厂造对象 → 命令自身 `InterpretAction()`（若重写）或外部 `Interpreter` 填充参数 → `Moderator::AppendCommand/InsertCommand`（`Moderator.hpp:386-393`）把对象接入序列链表。

### 3.3 序列组装与执行（Moderator/Sandbox → 链表 → 逐条驱动）

1. **组装**：Moderator 维护一条以 `NoOp` 起始、`BeginMissionSequence` 为序列头（`Moderator.cpp:7851` 的 `CreateCommand("BeginMissionSequence", ...)`）的命令链表。`AppendCommand` 最终落到 `GmatCommand::Append`（`GmatCommand.cpp:1814`），遇到 `BranchCommand` 自动把后续命令路由进子分支（`1837-1842`），从而把「文本缩进」翻译成「分支归属」。

2. **执行**：Sandbox 持 `sequence` 指针，`Sandbox::Execute()`（`Sandbox.cpp:1040`）的循环是整条序列的驱动器：

```cpp
current = sequence;                        // line 1059
while (current)                            // line 1065
{
   if (Interrupt()) { ... }                // line 1068 中断轮询
   rv = current->Execute();                // line 1186 执行当前命令
   if (!rv) throw SandboxException(...);   // line 1188-1199
   current = current->GetNext();           // line 1233 取后继（分支命令重写）
}
```

`current = current->GetNext()` 是核心：普通命令返回 `next`；`BranchCommand`/`SolverBranchCommand` 重写 `GetNext`，在主线、子分支、`BranchEnd` 回跳之间切换，从而实现 `If/While/Target` 的循环与分支语义——**控制流不是靠递归，而是靠重写 `GetNext()` 的指针跳转**。

3. **晚绑定与校验**：序列建好后，Sandbox 对每个命令调用 `Initialize()`（`GmatCommand.cpp:1630` → `AssignObjects()`）把 `objectMap/globalObjectMap/solarSys` 里的真实对象指针绑定到命令成员；`VerifyObjects()`/`Validate()` 做运行前校验。

### 3.4 异常处理与中断机制（与「ThrowInterruptException」的对照）

本目录**不存在** `ThrowInterruptException` 这类方法——中断不是命令主动抛出的，而是**执行层轮询**：

- `Sandbox::Execute` 每轮循环调用 `Interrupt()`（`Sandbox.cpp:1068`）；`PAUSED` 时 `publisher->Ping()` 后 `continue`（`1076-1080`），否则 `sequence->RunComplete(true)` + `throw SandboxException("Execution interrupted")`（`1084-1099`）。
- 命令层通过 `SkipInterrupt()`（`GmatCommand.cpp:2216`，默认 `false`）声明「是否允许跳过中断轮询」，`Assignment` 重写为跳过以保证赋值原子性。
- 命令自身的错误统一用 `CommandException`（`CommandException.hpp:42`）抛给 Sandbox 的 `catch (BaseException&)`（`Sandbox.cpp:1235`），并附上脚本行号后继续上抛。

命令执行态由 `Gmat::RunState`（`utildefs.hpp:188-199`）承载：`IDLE/RUNNING/PAUSED/TARGETING/OPTIMIZING/ESTIMATING/SOLVING/SOLVEDPASS/WAITING`。`GmatCommand::SetRunState`（`GmatCommand.cpp:2295`）是入口，`Propagate`（`Propagate.cpp:4517`）与求解器循环命令据其判断是否继续推进。

## 四、文件清单附录

| 相对路径 | 职责 | 关键类/函数 | 命令类型 | 基类 | 主要参数 |
|---|---|---|---|---|---|
| `src/base/command/GmatCommand.hpp` | 命令根基类声明 | `Execute()=0`、`Initialize`、`GetNext`、`Append` | —（抽象） | `GmatBase` | `Comment/Summary/MissionSummary` |
| `src/base/command/GmatCommand.cpp` | 基类实现 | `Initialize`(1630)、`Append`(1814)、`RunComplete`(2233) | — | — | — |
| `src/base/command/CommandException.hpp` | 命令异常声明 | `CommandException` | —（异常） | `BaseException` | — |
| `src/base/command/CommandException.cpp` | 命令异常实现 | — | — | — | — |
| `src/base/command/CommandUtil.hpp` | 序列工具声明 | `GmatCommandUtil::GetFirstCommand` 等 | —（工具） | — | — |
| `src/base/command/CommandUtil.cpp` | 序列工具实现 | `GetMatchingEnd`、`ClearCommandSeq` | — | — | — |
| `src/base/command/BranchCommand.hpp` | 分支基类声明 | `AddBranch`、`ExecuteBranch`、`GetNext` | —（抽象） | `GmatCommand` | — |
| `src/base/command/BranchCommand.cpp` | 分支实现 | `TakeAction`(1158)、`ExecuteBranch`(1221) | — | — | — |
| `src/base/command/ConditionalBranch.hpp` | 条件分支声明 | `SetCondition`、`EvaluateAllConditions` | —（抽象） | `BranchCommand` | 条件数/逻辑符/左右式 |
| `src/base/command/ConditionalBranch.cpp` | 条件求值实现 | `Initialize`(448)、`EvaluateCondition` | — | — | — |
| `src/base/command/SolverBranchCommand.hpp` | 求解器循环基类声明 | `theSolver`、`StoreLoopData` | —（抽象） | `BranchCommand` | `SolverName/SolveMode/ExitMode/ShowProgress` |
| `src/base/command/SolverBranchCommand.cpp` | 求解器循环实现 | `InterpretAction`、`ApplySolution` | — | — | — |
| `src/base/command/SolverSequenceCommand.hpp` | 求解器序列基类声明 | `solverName` | —（抽象） | `GmatCommand` | `SolverName` |
| `src/base/command/SolverSequenceCommand.cpp` | 求解器序列实现 | 参数访问 | — | — | — |
| `src/base/command/PropagationEnabledCommand.hpp` | 传播使能基类声明 | `AssemblePropagators`、`Step`、`TakeAStep` | —（抽象） | `GmatCommand` | — |
| `src/base/command/PropagationEnabledCommand.cpp` | 传播使能实现 | `PrepareToPropagate` | — | — | — |
| `src/base/command/Propagate.hpp` | 传播命令声明 | `PropModes`、`stopWhen` | `Propagate` | `PropagationEnabledCommand` | `PropName/SatName/StopWhen/PropForward/PropAllSTM/StopAccuracy/OrbitColor` |
| `src/base/command/Propagate.cpp` | 传播实现 | `Execute`(4479)、`Initialize`(3289)、`InterpolateToStop` | | | |
| `src/base/command/Maneuver.hpp` | 脉冲机动声明 | `burn/sat` | `Maneuver` | `GmatCommand` | `BurnName/SatName/BackProp` |
| `src/base/command/Maneuver.cpp` | 机动实现 | `Execute`(704)、`InterpretAction`(559) | | | |
| `src/base/command/BeginFiniteBurn.hpp` | 开有限推力声明 | `maneuver/burnForce/transientForces` | `BeginFiniteBurn` | `GmatCommand` | `BurnName` |
| `src/base/command/BeginFiniteBurn.cpp` | 开有限推力实现 | `Execute`(623)、`TakeAction`(203) | | | |
| `src/base/command/EndFiniteBurn.hpp` | 关有限推力声明 | — | `EndFiniteBurn` | `GmatCommand` | `BurnName` |
| `src/base/command/EndFiniteBurn.cpp` | 关有限推力实现 | `Execute`(471) | | | |
| `src/base/command/Target.hpp` | 打靶命令声明 | `targeterConverged` | `Target` | `SolverBranchCommand` | `SolverName/TargeterConverged` |
| `src/base/command/Target.cpp` | 打靶实现 | `Execute`(624)、`Initialize`(483) | | | |
| `src/base/command/EndTarget.hpp` | 打靶结束声明 | — | `EndTarget` | `GmatCommand` | — |
| `src/base/command/EndTarget.cpp` | 打靶结束实现 | `Execute`(136)、`Insert`(164) | | | |
| `src/base/command/Optimize.hpp` | 优化命令声明 | `RunInternalSolver/RunExternalSolver` | `Optimize` | `SolverBranchCommand` | `OptimizerName/OptimizerConverged` |
| `src/base/command/Optimize.cpp` | 优化实现 | `Execute`(568) | | | |
| `src/base/command/EndOptimize.hpp` | 优化结束声明 | — | `EndOptimize` | `GmatCommand` | — |
| `src/base/command/EndOptimize.cpp` | 优化结束实现 | `Execute`(113) | | | |
| `src/base/command/Vary.hpp` | 变量定义声明 | `variable/perturbation` | `Vary` | `SolverSequenceCommand` | `SolverName/VariableName/InitialValue/Perturbation/Lower/Upper/MaxStep/AdditiveScale/MultiplicativeScale` |
| `src/base/command/Vary.cpp` | 变量实现 | `Execute`(1459)、`SetInitialValue` | | | |
| `src/base/command/Achieve.hpp` | 目标定义声明 | `goal/achieve/tolerance/targeter` | `Achieve` | `SolverSequenceCommand` | `SolverName/GoalName/GoalValue/Tolerance/AchievedValue` |
| `src/base/command/Achieve.cpp` | 目标实现 | `Execute`(1089)、`InterpretAction`(714) | | | |
| `src/base/command/Minimize.hpp` | 最小化声明 | `objective/optimizer` | `Minimize` | `SolverSequenceCommand` | `OptimizerName/ObjectiveName/ObjectiveValue` |
| `src/base/command/Minimize.cpp` | 最小化实现 | `Execute`(871) | | | |
| `src/base/command/NonlinearConstraint.hpp` | 非线性约束声明 | `arg1/arg2/tolerance/op` | `NonlinearConstraint` | `SolverSequenceCommand` | `OptimizerName/Arg1/LhsValue/Operator/Arg2/RhsValue/Tolerance` |
| `src/base/command/NonlinearConstraint.cpp` | 约束实现 | `Execute`(1190) | | | |
| `src/base/command/RunSolver.hpp` | 单命令求解器基类声明 | `solverName` | —（抽象） | `PropagationEnabledCommand` | `SolverName` |
| `src/base/command/RunSolver.cpp` | 单命令求解器实现 | `Initialize`(123) | — | — | — |
| `src/base/command/If.hpp` | If 声明 | `nestLevel` | `If` | `ConditionalBranch` | 条件/NestLevel |
| `src/base/command/If.cpp` | If 实现 | `Execute`(185) | | | |
| `src/base/command/ElseIf.hpp` | ElseIf 声明（宏保护） | — | `ElseIf` | `GmatCommand` | — |
| `src/base/command/ElseIf.cpp` | ElseIf 实现 | `Execute`(150) | | | |
| `src/base/command/Else.hpp` | Else 声明 | — | `Else` | `GmatCommand` | — |
| `src/base/command/Else.cpp` | Else 实现 | `Execute`(144) | | | |
| `src/base/command/EndIf.hpp` | EndIf 声明 | — | `EndIf` | `GmatCommand` | — |
| `src/base/command/EndIf.cpp` | EndIf 实现 | `Execute`(133)、`Insert`(152) | | | |
| `src/base/command/While.hpp` | While 声明 | `nestLevel/localParameters` | `While` | `ConditionalBranch` | 条件/NestLevel |
| `src/base/command/While.cpp` | While 实现 | `Execute`(282)、`Initialize`(202) | | | |
| `src/base/command/EndWhile.hpp` | EndWhile 声明 | — | `EndWhile` | `GmatCommand` | — |
| `src/base/command/EndWhile.cpp` | EndWhile 实现 | `Execute`(140)、`Insert`(165) | | | |
| `src/base/command/For.hpp` | For 声明 | `startValue/endValue/stepSize` | `For` | `BranchCommand` | `Start/End/Step/IndexName` |
| `src/base/command/For.cpp` | For 实现 | `Execute`(312)、`StillLooping` | | | |
| `src/base/command/EndFor.hpp` | EndFor 声明 | — | `EndFor` | `GmatCommand` | — |
| `src/base/command/EndFor.cpp` | EndFor 实现 | `Execute`(133) | | | |
| `src/base/command/Report.hpp` | Report 声明 | `reporter/parms` | `Report` | `GmatCommand` | `ReportFile/Add` |
| `src/base/command/Report.cpp` | Report 实现 | `Execute`(928)、`WriteHeaders` | | | |
| `src/base/command/Write.hpp` | Write 声明 | `OutputStyle` | `Write` | `GmatCommand` | `Add` |
| `src/base/command/Write.cpp` | Write 实现 | `Execute`(568) | | | |
| `src/base/command/SaveMission.hpp` | SaveMission 声明 | `fileName` | `SaveMission` | `GmatCommand` | `FileName` |
| `src/base/command/SaveMission.cpp` | SaveMission 实现 | `Execute`(131) | | | |
| `src/base/command/Toggle.hpp` | Toggle 声明 | `toggleState/subs` | `Toggle` | `GmatCommand` | `Subscriber/ToggleState` |
| `src/base/command/Toggle.cpp` | Toggle 实现 | `Execute`(196) | | | |
| `src/base/command/PlotCommand.hpp` | 绘图基类声明 | `thePlotList` | —（抽象） | `GmatCommand` | `Subscriber` |
| `src/base/command/PlotCommand.cpp` | 绘图基类实现 | `InterpretAction` | — | — | — |
| `src/base/command/ClearPlot.hpp` | ClearPlot 声明 | — | `ClearPlot` | `PlotCommand` | `Subscriber` |
| `src/base/command/ClearPlot.cpp` | ClearPlot 实现 | `Execute`(179) | | | |
| `src/base/command/PenUp.hpp` | PenUp 声明 | — | `PenUp` | `PlotCommand` | `Subscriber` |
| `src/base/command/PenUp.cpp` | PenUp 实现 | `Execute`(176) | | | |
| `src/base/command/PenDown.hpp` | PenDown 声明 | — | `PenDown` | `PlotCommand` | `Subscriber` |
| `src/base/command/PenDown.cpp` | PenDown 实现 | `Execute`(180) | | | |
| `src/base/command/MarkPoint.hpp` | MarkPoint 声明 | — | `MarkPoint` | `PlotCommand` | `Subscriber` |
| `src/base/command/MarkPoint.cpp` | MarkPoint 实现 | `Execute`(181) | | | |
| `src/base/command/UpdateDynamicData.hpp` | 动态数据声明 | `dynamicData/dynamicDataStruct` | `UpdateDynamicData` | `GmatCommand` | `DynamicDataDisplay/AddUpdateData/AvailableParams` |
| `src/base/command/UpdateDynamicData.cpp` | 动态数据实现 | `Execute`(539) | | | |
| `src/base/command/FindEvents.hpp` | 事件定位声明 | `eventLocator/appendFlag` | `FindEvents` | `GmatCommand` | `EventLocator/Append` |
| `src/base/command/FindEvents.cpp` | 事件定位实现 | `Execute`(551)、`InterpretAction`(583) | | | |
| `src/base/command/ManageObject.hpp` | 对象管理基类声明 | `objectNames` | —（抽象） | `GmatCommand` | `ObjectNames` |
| `src/base/command/ManageObject.cpp` | 对象管理实现 | `Initialize`(400) | — | — | — |
| `src/base/command/Create.hpp` | Create 声明 | `refObj/arrayNames` | `Create` | `ManageObject` | `ObjectType` |
| `src/base/command/Create.cpp` | Create 实现 | `Initialize`(313)、`Execute`(417) | | | |
| `src/base/command/Assignment.hpp` | 赋值命令声明 | `lhs/rhs/rhsEquation` | `Assignment`(=`GMAT`/`Equation`) | `GmatCommand` | `LHS/RHS` |
| `src/base/command/Assignment.cpp` | 赋值实现 | `Execute`(987)、`InterpretAction`(438) | | | |
| `src/base/command/RHSEquation.hpp` | 右端表达式声明 | `BuildExpression/RunMathTree` | —（工具） | — | — |
| `src/base/command/RHSEquation.cpp` | 右端表达式实现 | `MathTree` 构建 | — | — | — |
| `src/base/command/Stop.hpp` | Stop 声明 | — | `Stop` | `GmatCommand` | — |
| `src/base/command/Stop.cpp` | Stop 实现 | `Execute`(114) | | | |
| `src/base/command/NoOp.hpp` | NoOp 声明 | — | `NoOp` | `GmatCommand` | — |
| `src/base/command/NoOp.cpp` | NoOp 实现 | `Execute`(107) | | | |
| `src/base/command/BeginMissionSequence.hpp` | 序列头声明 | — | `BeginMissionSequence` | `GmatCommand` | — |
| `src/base/command/BeginMissionSequence.cpp` | 序列头实现 | `Execute`(112) | | | |
| `src/base/command/BeginScript.hpp` | Script 块头声明 | `IndentChildString` | `BeginScript` | `GmatCommand` | — |
| `src/base/command/BeginScript.cpp` | Script 块头实现 | `Execute`(123) | | | |
| `src/base/command/EndScript.hpp` | Script 块尾声明 | — | `EndScript` | `GmatCommand` | — |
| `src/base/command/EndScript.cpp` | Script 块尾实现 | `Execute`(108) | | | |
| `src/base/command/CallFunction.hpp` | 函数调用声明 | `mFunction/fm` | `CallFunction` | `GmatCommand` | `FunctionName/AddInput/AddOutput` |
| `src/base/command/CallFunction.cpp` | 函数调用实现 | `Execute`(1103)、`TakeAction`(758) | | | |
| `src/base/command/CallBuiltinGmatFunction.hpp` | 内置函数声明 | — | `CallBuiltinGmatFunction` | `CallFunction` | 继承 `CallFunction` |
| `src/base/command/CallBuiltinGmatFunction.cpp` | 内置函数实现 | `Execute`(163) | | | |
| `src/base/command/BeginFunction.hpp` | 函数体头声明 | `gfun/localMap/returnObjects` | `BeginFunction` | `GmatCommand` | `FunctionName/Inputs/Outputs` |
| `src/base/command/BeginFunction.cpp` | 函数体头实现 | `Execute`(1057)、`TakeAction`(582) | | | |
| `src/base/command/EndFunction.hpp` | 函数体尾声明 | `functionName` | `EndFunction` | `GmatCommand` | — |
| `src/base/command/EndFunction.cpp` | 函数体尾实现 | `Execute`(92) | | | |

> 注：表中「命令类型」列对应 `CommandFactory::CreateCommand`（`src/base/factory/CommandFactory.cpp:127-223`）注册的脚本关键字；`Assignment` 同时覆盖 `GMAT` 与 `Equation` 两个别名（`CommandFactory.cpp:166`）。`CommandException`/`RHSEquation`/`CommandUtil`/`PlotCommand` 等非可实例化命令类型标记为「—（抽象/工具）」。
