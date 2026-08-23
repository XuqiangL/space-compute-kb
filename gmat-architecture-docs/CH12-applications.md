# 第12章 可执行程序、控制台与样例脚本

本章范围：负责 GmatConsole 控制台应用（`src/console/`，9 个文件）、各可执行程序的 `main()` 入口（`application/bin/` 目录级 + 实际入口源码 `src/console/driver.cpp`、`src/gui/app/GmatApp.cpp`）、样例脚本 `application/samples/`（197 个文件）、以及 `application/` 下其余配套目录：`output/`、`matlab/`、`utilities/`、`userfunctions/`、`userincludes/`、`api/`、`extras/`、`debug/`、`docs/`、`plugins/`。本章共覆盖约 590 个文件，其中源码/脚本类逐文件讲解，数据与文档类按目录级说明 + 代表文件深读 + 表格清单覆盖。

> 注意：`application/bin/` 目录内**不含任何 `.cpp/.c` 源码**（仅配置文件、Python 包与 MATLAB 加载脚本），可执行程序的 `main()` 入口实际位于 `src/console/driver.cpp`（GmatConsole）与 `src/gui/app/GmatApp.cpp`（GMAT GUI）。这一点在 2.2 节详述。

## 一、本章目录树

```
L:\gmat888
├── src\console\                        GmatConsole 控制台应用（9 文件）
│   ├── CMakeLists.txt                   构建脚本
│   ├── driver.cpp / driver.hpp          main() 与命令行分发
│   ├── ConsoleMessageReceiver.cpp/.hpp  控制台消息接收器（单例）
│   ├── ConsoleAppException.cpp/.hpp     控制台专用异常
│   └── PrintUtility.cpp/.hpp            序列打印工具（单例）
├── application\bin\                    运行目录（12 文件，无源码）
│   ├── GMAT.ini                         GUI 帮助/提示文本映射
│   ├── gmat_startup_file*.txt           启动文件（含 mac_linux/public 变体）
│   ├── gmatpy\__init__.py               Python API 包入口
│   ├── load_gmat.m                      MATLAB API 加载脚本
│   └── MacConfigure.txt                 macOS MATLAB/SNOPT 路径
├── application\samples\                样例脚本（197 文件）
│   ├── Ex_*.script (78)                 功能示例（Hohmann/GEO/地月/火星等）
│   ├── Tut_*.script (10)                用户指南教程
│   ├── Navigation\ (24)                 估计/滤波导航示例
│   ├── CSALT\ (46)                      最优控制 C++ 样例
│   ├── NeedMatlab\ (2) / NeedSNOPT\ (3) / NeedVF13ad\ (13)  依赖专有求解器
│   ├── OptimalControl\ (9)              最优控制脚本
│   ├── SupportFiles\ (11)               数据/被 include 的辅助脚本
│   └── AlphaAndBetaFeatures\ (1)        readme
├── application\output\                 （空，仅 .gitignore）
├── application\matlab\                  MATLAB 接口（21 文件）
├── application\utilities\python\        Python 工具（13 文件）
├── application\userfunctions\           用户函数（26 文件：gmat .gmf / python）
├── application\userincludes\            include 片段（2 文件）
├── application\api\                     Python/MATLAB API 示例（24 文件）
├── application\extras\                  Notepad++ 语法高亮（2 文件）
├── application\debug\                   调试用配置镜像（7 文件）
├── application\docs\                    文档（约 277 文件，目录级）
└── application\plugins\                （空，仅 .gitignore）
```

## 二、逐文件/逐类讲解

### 2.1 GmatConsole 控制台应用（src/console/，9 文件）

GmatConsole 是 GMAT 的无 GUI 命令行版本，与 GUI 共用同一套 **core**（`Moderator`、`CommandFactory`、`FactoryManager` 等全部来自 `src/base`），区别仅在"消息接收器"与"命令序列呈现方式"：控制台把 `MessageInterface` 接到 `ConsoleMessageReceiver`，把命令序列打印交给 `PrintUtility`。

#### 2.1.1 `driver.cpp`（908 行）—— 程序入口与命令行分发

职责：`GmatConsole` 的 `main()` 与全部顶层函数（帮助、脚本解释、批处理、保存、版本、命令摘要、DE 数据导出、参数解析）。

关键函数列表与解读：

- **`ShowHelp()`**（`driver.cpp:67-90`）：打印 `Usage` 三段式说明——① 无参交互模式；② 单脚本一次性运行；③ `--batch/--run/--logfile/--startup_file/...` 等选项（`:69-89`）。注意帮助文本明确标注 `--minimize`、`--start-server` 对控制台是"ignored"（`:83-84`），说明这些选项是从 GUI 命令行继承而来、控制台做了静默忽略以保持参数兼容。

- **`RunScriptInterpreter(script, verbosity, batchmode)`**（`:106-187`）：核心"解释→运行"流程。先 `std::ifstream fin(script)` 检查脚本存在性（`:110-125`），不存在时单脚本模式打印错误返回、批处理模式抛 `ConsoleAppException`；随后调用 `mod->InterpretScript(script)`（`:147`）把脚本文本解释成命令序列；`verbosity != 0` 时用 `PrintUtility::PrintEntireSequence(top)` 打印整个序列（`:169-173`）；最后 `mod->RunMission()`（`:178`），返回值 `!= 1` 即抛异常。这段是控制台与 GUI 共用的 `Moderator` 三阶段（解释→取首命令→执行）的最直白体现。

  ```cpp
  // driver.cpp:144-186（节选）
  bool canRun;
  try {
     canRun = mod->InterpretScript(script);          // 1) 文本→命令树
     if (!canRun) { ... throw ...; }
  } catch (BaseException &oops) {
     MessageInterface::ShowMessage("ERROR!!!!!! ---- %s\n", oops.GetFullMessage().c_str());
     throw;
  }
  GmatCommand *top = mod->GetFirstCommand();          // 2) 取出序列首命令
  if (verbosity != 0) {
     PrintUtility* pu = PrintUtility::Instance();
     pu->PrintEntireSequence(top);                    //    可选打印整条序列
  }
  if (canRun) {
     if (mod->RunMission() != 1)                      // 3) 执行任务
        throw ConsoleAppException("Moderator::RunMission failed");
  }
  ```
  逐行：`InterpretScript` 把脚本解析并构建命令流；`GetFirstCommand()` 返回序列头部 `GmatCommand*`（链表式命令树）；`PrintEntireSequence` 递归遍历打印；`RunMission()` 返回 1 表示成功，否则抛异常终止。

- **`RunBatch(batchfilename)`**（`:201-302`）：批处理。逐 `batchfile >> script` 读取脚本名（`:220`）；以 `%` 开头的行视为注释跳过（`:231`）；`--summary` 行调用 `ShowCommandSummary()`（`:224-227`）；每个脚本用 `try/catch` 包裹执行并统计 `successful/failed/skipped`（`:236-264`）；末尾打印 `Batch Run Statistics` 汇总（`:278-283`），并列出失败、跳过脚本清单（`:285-299`）。返回值是解析到的脚本行数。

- **`SaveScript(filename)`**（`:314-325`）：调用 `mod->SaveScript(filename)`（`:323`）把当前已运行脚本回写，空文件名或未运行过则打印提示。

- **`ShowVersionInfo()`**（`:333-348`）：用 `GmatGlobal::Instance()->GetGMATBuildDate()/GetGMATBuildTime()`（`:339,345`）替代 `__DATE__/__TIME__` 宏（对应 bug GMT-7399 的修复注释），保证版本信息与构建系统一致。

- **`ShowCommandSummary(filename)`**（`:360-395`）：取 `mod->GetFirstCommand()`，若首命令是 `NoOp` 则跳到下一条（`:374-382`，因 Moderator 常在序列头插一个占位 `NoOp`）；从命令对象取 `GetStringParameter("MissionSummary")` 打印（`:388`）。文件输出暂未实现（`:393`）。

- **`DumpDEData(secsToStep, spanInSecs)`**（`:409-450`）：调试用 DE 星历导出。从 `mod->GetSolarSystemInUse()`（`:420`）取 `Earth/Luna`，逐历元调用 `GetMJ2000State`/`GetMJ2000Acceleration`（`:435-437`）写出 `EarthMoonDe.txt`。

- **`CheckForStartupAndLogFile(argc, argv)`**（`:466-541`）：在 `main()` 初始化前**单独**扫描 `--logfile/-l` 与 `--startup_file/-s`（`:480,502`），因为日志文件路径依赖启动文件读出的 `OUTPUT_PATH`，必须先把启动文件名拿到手。指定启动文件不存在时抛 `ConsoleAppException`（`:517-522`）。默认启动文件 `gmat_startup_file.txt`（`:469`）。

- **`main(argc, argv)`**（`:556-907`）：入口，流程如下：
  1. 打印横幅（`"***  GMAT Console Application"`）与构建日期（`:574-578`）；
  2. 实例化 `ConsoleMessageReceiver::Instance()` 并 `MessageInterface::SetMessageReceiver(...)`（`:591-592`）；
  3. `CheckForStartupAndLogFile` 预解析（`:602`），若有 `--logfile` 则 `gmatGlobal->SetLogfileSource(CMD_LINE, logFile)`（`:606-610`）；
  4. `mod = Moderator::Instance()` 并 `mod->Initialize(startUpFile)`（`:618-625`）——**失败直接 `exit(EXIT_FAILURE)`**；
  5. `mod->CreateDefaultParameters()`（`:628`）填充参数库；
  6. 分支：`argc < 2` 进入交互式 `do/while` 循环（`:630-751`，逐条读 `std::cin`，识别 `q/Q/--exit`、`--help`、`--run`、`--batch`、`--save`、`--version`、`--summary`、`--verbose`、隐藏的 `--DumpDEData` 等）；`argc >= 2` 进入非交互模式（`:752-893`，`argc==2` 且非 `-` 开头则直接当作脚本名运行 `:756-769`，否则逐参数解析）；
  7. 顶层 `catch (BaseException &ex)`（`:895-901`）打印 `EXIT_FAILURE` 退出码并 `exit(EXIT_FAILURE)`；
  8. 正常路径调用 `Moderator::Instance()->Finalize()`（`:903`）后 `exit(EXIT_SUCCESS)`（`:905`）。

  **退出码约定**：成功 `EXIT_SUCCESS`（通常 0），初始化失败或运行异常 `EXIT_FAILURE`（通常 1）。控制台**不支持** GUI 的 `-8/-7/...` 细粒度沙箱退出码（见 2.2.2 `OnExit` 注释）。

#### 2.1.2 `driver.hpp`（63 行）

职责：声明 `driver.cpp` 中全部顶层函数原型。

要点：`:40-48` 定义枚举 `RUN_SCRIPT=2001, RUN_BATCH, SAVE, SUMMARY, PARSE, HELP, VERBOSE`（历史上用于交互菜单命令码，现已被字符串选项取代但仍保留）；`:50-61` 声明 `ShowHelp/RunScriptInterpreter/RunBatch/SaveScript/ShowVersionInfo/ShowCommandSummary/DumpDEData/CheckForStartupAndLogFile/main`。注意 `RunScriptInterpreter` 的 `batchmode` 参数有默认值 `false`（`:52`）。

#### 2.1.3 `ConsoleMessageReceiver.cpp`（619 行）+ `.hpp`（102 行）

职责：`MessageReceiver` 抽象基类的控制台实现——把 GMAT 内部所有消息（`ShowMessage/PopupMessage/LogMessage`）重定向到标准输出与日志文件。类声明见 `ConsoleMessageReceiver.hpp:43-100`，继承 `public MessageReceiver`，作为单例（`theInstance` 静态指针 `:81`）。

关键成员与方法：

- **`Instance()`**（`.cpp:74-80`）：惰性构造单例（`theInstance == NULL` 才 `new`）。

- **`ShowMessage(const std::string&)`**（`:94-102`）：关键技巧——先 `GmatStringUtil::Replace(msg, "%", "%%")`（`:100`）把 `%` 转义，因为脚本注释以 `%` 开头，直接传 `vsprintf` 会被误当作格式符；再转调变参版本。

- **`ShowMessage(const char*, ...)`**（`:116-143`）：`va_start/vsprintf/va_end` 完成格式化（`:137-139`），缓冲区大小 = `strlen(msg) + MAX_MESSAGE_LENGTH`（`:125`），随后 `LogMessage` 输出并 `delete[]`。

- **`PopupMessage(...)`**（`:163-222`）：控制台无弹窗，两条重载都退化为"补换行后写日志"（`:217-220`）。

- **`GetLogFileName()`**（`:233-265`）：优先用命令行日志名；无路径时拼上 `FileManager::LOG_FILE` 的输出路径（`:245-252`）；异常兜底为 `GmatLog.txt`（`:255-262`）。

- **`OpenLogFile(filename, append)`**（`:362-420`）：先 `IsValidLogFile` 校验避免覆盖非日志文件（`:368-372`）；按 `append` 选 `"a"/"w"` 模式 `fopen`（`:380-383`）；打开成功后写日志头（构建日期，`:406-408`）与模式说明。

- **`LogMessage(const std::string&)`**（`:451-477`）：`printToConsole` 为真则 `std::cout << msg`（`:453-454`）；`logEnabled` 才写日志，日志未打开时先 `SetLogFile(GetLogFileName())` 惰性打开（`:460-463`）；最终 `fprintf(logFile, ...)` + `fflush`（`:474-475`）。

- **构造函数**（`:600-608`）：初始化列表设定 `MAX_MESSAGE_LENGTH(10000)`、`logFile(NULL)`、`logEnabled(false)`、`logFileSet(false)`、`printToConsole(true)`，并向 `messageQueue` 压入首条消息 `"ConsoleMessageReceiver: Starting GMAT ..."`。

设计要点：控制台消息接收器是"日志即输出"的极简实现，`GetMessage/PutMessage/ClearMessageQueue` 均为空操作（`:545-572`），因为这些队列语义只在 GUI 事件循环里有意义。`ToggleConsolePrinting`（`:584-587`）允许在 `--verbose off` 场景下抑制屏幕回显。

#### 2.1.4 `ConsoleAppException.cpp`（51 行）+ `.hpp`（57 行）

职责：控制台专用异常类型。类声明 `ConsoleAppException.hpp:47-54`，继承 `public BaseException`。实现只有构造函数（`.cpp:40-44`），把细节字符串包成 `BaseException("Console Application Execution Failed: ", details)`——即异常消息统一带前缀 `"Console Application Execution Failed: "`，便于日志中区分来源。析构函数为空。

#### 2.1.5 `PrintUtility.cpp`（126 行）+ `.hpp`（61 行）

职责：把 Moderator 构建好的命令树打印到标准输出，用于 `--verbose` 模式与调试。声明见 `PrintUtility.hpp:41-60`，单例（`onlyInstance` `:58`），且注释明确 `// No GMAT_API here because this class is used in the exe, not in a DLL`（`:40`）——它是 exe 内部类，不参与 DLL 导出。

关键方法：

- **`PrintEntireSequence(GmatCommand* firstCmd)`**（`.cpp:63-76`）：从首命令沿 `GetNext()` 链表遍历，打印 `Command::<TypeName>`；遇有子命令（`GetChildCommand(0) != NULL`，即 `Target/For/If` 等带分支命令）递归调 `PrintBranch(current, 0)`（`:70-71`）。

- **`PrintBranch(GmatCommand* brCmd, Integer level)`**（`:99-125`）：递归打印分支。`level` 控制缩进点数（`:` 前缀 + `level+1` 组 `...`，`:112-114`）；`nextInBranch != current` 的终止条件（`:109`）防止分支链表回环。

这两个方法展示了 `GmatCommand` 的**树形 + 链表混合结构**：同层命令靠 `GetNext()` 串成链表，控制流命令通过 `GetChildCommand(n)` 挂接子序列，这正是 Mission Sequence 在内存中的真实形态。

#### 2.1.6 `CMakeLists.txt`（101 行）

职责：构建 `GmatConsole` 可执行目标。要点：`SET(TargetName GmatConsole)`（`:17`）；源文件仅 4 个 `driver.cpp / ConsoleAppException.cpp / PrintUtility.cpp / ConsoleMessageReceiver.cpp`（`:21-26`）；`ADD_EXECUTABLE`（`:37`）；**仅链接 `GmatUtil` 与 `GmatBase` 两个库**（`:46-47`）——这两个库把整个 GMAT 核心（Moderator、工厂、参数系统）编译进去，控制台因此无需再链 GUI/wxWidgets；debug 后缀显式设置（`:42`，因 `CMAKE_DEBUG_POSTFIX` 对可执行文件不生效）；`_SETOUTPUTDIRECTORY(... bin)`（`:55`）把产物放到 `bin/`；Apple 平台额外创建用户级 bin 符号链接（`:71-87`）。

### 2.2 可执行程序入口与启动差异

`application/bin/` 目录**没有** `main()` 源码——它是**运行时部署目录**，装的是 `GMAT.ini`、启动文件、`gmatpy` Python 包、`load_gmat.m` 与构建好的可执行/库。各可执行程序的 `main()` 实际位置与构建目标如下（依据 `src/CMakeLists.txt:20-66`）：

| 可执行 | main() 位置 | CMake 目标 | 产物名 | 备注 |
|---|---|---|---|---|
| GMAT（GUI） | `src/gui/app/GmatApp.cpp:87` `IMPLEMENT_APP(GmatApp)` | `GmatGUI`（`src/gui/CMakeLists.txt:33`） | `GMAT`（`OUTPUT_NAME "GMAT"`，`:290`） | wxWidgets 应用 |
| GmatConsole | `src/console/driver.cpp:556` `int main()` | `GmatConsole`（`src/console/CMakeLists.txt:17`） | `GmatConsole` | 控制台应用 |
| CSALTTester | `src/csaltTester/.../TestOptCtrl.cpp` | `CSALTTester`（`src/csaltTester/CMakeLists.txt:25`） | `CSALTTester` | 仅当 `GMAT_INCLUDE_CSALT_TESTPROGRAM` |
| （库，非 exe）GmatUtil / GmatBase | — | `GmatUtil`/`GmatBase` | lib | 被上面所有 exe 链接 |

`src/CMakeLists.txt` 的构建顺序（`:24-66`）固定为 `gmatutil → base → console → (csalt → csaltTester) → gui`，即**先建两个核心库，再建各可执行程序**。

#### 2.2.1 GmatConsole 启动顺序（`driver.cpp:556-628`）

1. 打印横幅（`:574-578`）；
2. 建立 `ConsoleMessageReceiver` 并挂到 `MessageInterface`（`:591-592`）；
3. 预解析启动文件/日志文件参数（`:602`）；
4. `Moderator::Instance()` → `mod->Initialize(startUpFile)`（`:618-625`），失败 `exit(EXIT_FAILURE)`；
5. `mod->CreateDefaultParameters()`（`:628`）；
6. 进入交互循环或参数分发（`:630` 起）。

控制台**没有** Publisher、GuiInterpreter、DebuggerCommandFactory 等 GUI 专属组件。

#### 2.2.2 GMAT GUI 启动顺序（`src/gui/app/GmatApp.cpp`）

GUI 用 wxWidgets 的 `IMPLEMENT_APP(GmatApp)`（`GmatApp.cpp:87`）生成真正的 `main()`；`GmatApp` 继承 `wxApp`（`GmatApp.hpp:46`），程序入口逻辑全在虚函数 `OnInit()`。

- **构造函数**（`:92-117`）：在 `OnInit` 之前就建立 `GuiMessageReceiver`（`:95-96`）、`GuiPlotReceiver`（`:98-99`）、`GuiListenerManager`（`:101-102`）三个 GUI 专属接收器，并把它们挂到 `MessageInterface/PlotInterface/ListenerManagerInterface`；Linux 下调用 `XInitThreads()`（`:113-116`）。这三点是 GUI 与控制台在"消息/绘图/监听"三层的根本差异。

- **`OnInit()`**（`:127-526`）关键顺序：
  1. `GmatAppData::Instance()` 与 `FileManager::Instance()`，取 `fm->GetFullStartupFilePath()`（`:146-148`）；
  2. `theModerator = Moderator::Instance()`，并 `OverridePublisher(GuiPublisher::Instance())`（`:188-191`）——**GUI 覆写发布者**，把任务进度广播到界面；
  3. `CheckForStartupAndLogFile()` 预解析（`:195`）；
  4. `theModerator->Initialize(startupFileToRead, true)`（`:219`，第二个参数 `true` 表示 GUI 模式）；
  5. 注册 `DebuggerCommandFactory`（`:222`），建 `GuiInterpreter` 并 `SetUiInterpreter/SetInterpreterMapAndSS`（`:224-227`）——把脚本编辑器与解释器绑定；
  6. 恢复工作目录、`ProcessCommandLineOptions()`（`:316-322`）；
  7. 显示 splash（`:347-405`）、`LoadDefaultMission()`（`:407`）；
  8. `new GmatMainFrame(...)` 创建主窗口（`:413-417`）并 `Show`（`:459-465`）；
  9. 按命令行标志 `BuildAndRunScript` / `RunBatch`（`:473-484`）。

- **`OnExit()`**（`:547-568`）：`theModerator->Finalize()`（`:551`）后取 `theModerator->GetExitCode()`（`:563`），非 1 则 `exit(exitCode)`。文件头注释（`:533-545`）列出了 GUI 的细粒度退出码：`0` 成功、`-1` 沙箱号无效、`-2` 沙箱初始化异常、`-3` 沙箱初始化未知错误、`-4` 用户中断、`-5` 沙箱执行异常、`-6` 沙箱执行未知错误、`-7` 无任务序列、`-8` 脚本错误。

- **`ProcessCommandLineOptions()`**（`:738-1052`）：GUI 命令行选项与控制台**重叠但更丰富**：`-h/--help`、`-l/--logfile`、`-s/--startup_file`、`-m/--minimize`（`:895-898` 设 `MINIMIZED_GUI`）、`-r/--run`（`:831-843`）、`-v/--version`、`-x/--exit`（`:849-852` 设 `EXIT_AFTER_RUN`）、`-ns/--no_splash`（`:941-942`）、`--nits`（`:899-936` NITS 客户端模式）、`--start-server`（`:825-829`）。**无选项参数的裸脚本名**会被识别为脚本文件并设 `buildScript=true`（`:968-1032`）。

- **`BuildAndRunScript(runScript)`**（`:1058-1147`）：GUI 的"构建+运行"是 `theMainFrame->BuildScript(...)`（`:1079`）与 `theMainFrame->RunCurrentScript()`（`:1104`），二者都经主窗口中转（触发编辑器/运行面板更新）；`EXIT_AFTER_RUN` 时 `SetAutoExitAfterRun(true)` 并 `Close()`（`:1132-1141`）。

**启动差异 5 点小结**（详见 2.2 与上文）：
1. 入口机制不同：GUI 用 wxWidgets `IMPLEMENT_APP` 生成 main 并在 `OnInit()` 初始化；控制台用普通 `int main()`。
2. 消息/绘图/监听三件套不同：GUI 用 `Gui*` 实现并额外挂 `PlotInterface`/`ListenerManagerInterface`，控制台只有 `ConsoleMessageReceiver`。
3. Publisher：GUI `OverridePublisher(GuiPublisher)`，控制台用 Moderator 默认发布者。
4. GUI 初始化额外做 `DebuggerCommandFactory`、`GuiInterpreter`、splash、`LoadDefaultMission`、`GmatMainFrame`；控制台只到 `CreateDefaultParameters` 为止。
5. 退出码粒度不同：控制台仅 `EXIT_SUCCESS/EXIT_FAILURE`，GUI 提供 `0/-1..-8` 沙箱级退出码。
6. 二者**共用同一 `Moderator::Instance()` 与全部工厂**——脚本解释、对象创建、任务执行逻辑完全一致。

### 2.3 application/bin/（12 文件）

逐文件说明：

#### 2.3.1 `GMAT.ini`（419 行）

职责：GUI 的 `wxConfig` 风格 ini，集中存放三类信息：`[Help]` 节把 GUI 各面板/对象名映射到 help 文档 URL（`:1-34`，如 `Planet=file://../docs/help/html/CelestialBody.html`）；各对象节的 `*Hint` 键（如 `[Propagator] IntegratorTypeHint` 等，`:85-`）提供 GUI 控件悬浮提示文本；`[Welcome/Links]`（`:374-396`）、`[Welcome/Samples]`（`:397-398`，指向 `../samples`）、`[GettingStarted/Tutorials]`（`:400-418`）配置欢迎页链接。它是**纯 GUI 资源**，控制台不读取。

#### 2.3.2 `gmat_startup_file.txt`（216 行）

职责：GMAT 全局启动文件（GUI 与控制台**都**读取），由 `Moderator::Initialize(startupFile)` 交给 `FileManager` 解析。结构：

- 命名约定注释（`:4-30`）：`*_PATH` 路径、`*_FILE` 文件名、相对路径相对可执行目录、`*_POT_FILE/*_TEXTURE_FILE` 约定、重复 `_FILE` 取最后、多条 `*_FUNCTION_PATH` 自上而下搜索、`PLUGIN` 按序加载；
- `WRITE_GMAT_KEYWORD=OFF` 等运行时开关（`:36-42`）；
- `PLUGIN = ../plugins/libXXX`（`:48-83`）：默认/Alpha/专有/外部四组插件，注释说明"插件按顺序加载"；
- 路径与文件节（`:85-204`）：`ROOT_PATH=../`（`:94`）、`OUTPUT_PATH=../output/`（`:97`）、`LOG_FILE`（`:98`）、`GMAT_INCLUDE_PATH=ROOT_PATH/userincludes/`（`:105`）、`GMAT_FUNCTION_PATH=ROOT_PATH/userfunctions/gmat`（`:107`）、`MATLAB_FUNCTION_PATH`（`:109-110`）、`PYTHON_MODULE_PATH`（`:112`）、行星历表 DE/SPK 文件（`:117-123`）、重力势文件（`:142-153`）、纹理/星表/模型（`:158-186`）等——这些键把**启动文件、include 目录、函数目录、数据文件**全部连接起来；
- Debug 选项（`:207-216`）多为注释。

关键点：`OUTPUT_PATH` 在 `:97` 定义后，`LOG_FILE=OUTPUT_PATH/GmatLog.txt`（`:98`）引用它，这印证了 `driver.cpp:612-613` 注释"必须读启动文件后才能设日志文件"的原因。

#### 2.3.3 `gmat_startup_file.public.txt` / `gmat_startup_file_mac_linux.txt` / `gmat_startup_file_mac_linux.public.txt`

职责：与 `gmat_startup_file.txt` 内容基本一致的变体——`public` 版去除专有/内部插件行（公开分发），`mac_linux` 版适配 Unix 路径。目录级说明即可。

#### 2.3.4 `gmatpy/__init__.py`（45 行）与 `gmatpy/__init__.specific.py`（13 行）

职责：Python API 包入口。`__init__.py`：把自身目录加入 `sys.path`（`:9`）；Windows 下用 `ctypes.cdll.LoadLibrary` 预加载 `libGmatUtil/libGmatBase/libStation/libGmatEstimation`（`:12-18`，保证 DLL 依赖顺序）；按当前解释器版本 `import _pyXY`（`:31-32`，如 `_py312`）并把其符号注入本模块命名空间（`:37-41`）；最后 `FileManager.Instance().SetBinDirectory(...)`（`:44-45`）初始化。`__init__.specific.py` 是**版本专用子目录**（如 `bin/gmatpy/_py39`）里的入口，`from .gmat_py import *` 等导入三组 SWIG 生成模块（`:11-13`）。

#### 2.3.5 `load_gmat.m`（103 行）

职责：MATLAB API 加载脚本。切到 GMAT bin 目录（`:11-22`），`javaclasspath` 加载 `gmat/station/navigation` 三个 jar（`:33-48`），经 `gmat_matlab_loadlibrary` 从 Java 侧加载共享库（`:59-61`），`gmat.Moderator.Instance()` + `gmat.gmat.Setup(gmatStartupFile)`（`:64-65`），可选 `LoadScript` 并解析错误列表（`:81-95`）。用 `onCleanup` 保证退出时还原工作目录（`:7-8,100-102`）。

#### 2.3.6 `MacConfigure.txt`（19 行）

职责：macOS 构建所需的 `MATLAB_APP_PATH`、`SNOPT_LIB_PATH`、`GFORTRAN_LIB_PATH` 模板（`:16-18`），注释说明只有使用 CSALT 才需要 SNOPT/gfortran。

### 2.4 samples/ 代表性脚本逐行解读（12 个）

samples 是 GMAT 脚本语言（`.script`）的官方示例库，完整展示对象创建、参数设置、`BeginMissionSequence` 及 `Propagate/Target/Report` 等命令。下面挑 12 个代表脚本解读（覆盖 Hohmann 转移、GEO 转移、地月转移、火星轨道、B 平面目标、控制流、脚本数学、积分器、电推进、include、GMAT 函数、教程）。

#### 2.4.1 `Ex_HohmannTransfer.script`（128 行）—— 霍曼转移 + 双段 Target

脚本头注释（`:1-7`）说明"演示如何打靶（target）一个 Hohmann 转移"。

- **航天器**（`:14`）：`Create Spacecraft DefaultSC;` 创建默认航天器（使用内建默认轨道参数）。
- **力模型与传播器**（`:20-24`）：`Create ForceModel DefaultProp_ForceModel;` + `Create Propagator DefaultProp;`，`DefaultProp.FM = DefaultProp_ForceModel;`（`:24`）把力模型绑定到传播器。
- **两次冲量**（`:30-40`）：`Create ImpulsiveBurn TOI;`（入轨点火）与 `GOI`（GEO 圆化点火）；`CoordinateSystem=Local / Origin=Earth / Axes=VNB`（`:32-34,38-40`）把速度增量定义在**地心 VNB 当地坐标系**（V=速度向、N=轨道法向、B=侧向）。
- **求解器**（`:46`）：`Create DifferentialCorrector DC;` 打靶求解器。
- **可视化**（`:55-108`）：`OpenFramesInterface OFI_EarthView` 及其 `View`（`TheView/Earth_View/DefaultSC_View`）设置视点、`DrawObject/DrawXYPlane/DrawLabel/DrawGrid` 数组开关（`:64-67`）、星场（`:72-74`）。
- **任务序列**（`:113-128`）—— 脚本核心：

  ```
  :115  Propagate 'Prop to Perigee' DefaultProp(DefaultSC) {DefaultSC.Periapsis};
  :118  Target 'Raise and Circularize' DC {SolveMode = Solve, ExitMode = DiscardAndContinue};
  :119    Vary 'Vary TOI.V' DC(TOI.Element1 = 0.5, {Perturbation = 0.0001, Lower = 0, Upper = 3.14159, MaxStep = 0.2});
  :120    Maneuver 'Apply TOI' TOI(DefaultSC);
  :121    Propagate 'Prop to Apogee' DefaultProp(DefaultSC) {DefaultSC.Apoapsis};
  :122    Achieve 'Achieve RMAG' DC(DefaultSC.Earth.RMAG = 42165, {Tolerance = 0.1});
  :123    Vary 'Vary GOI.V' DC(GOI.Element1 = 0.5, {Perturbation = 0.0001, Lower = 0, Upper = 3.14159, MaxStep = 0.2});
  :124    Maneuver 'Apply GOI' GOI(DefaultSC);
  :125    Achieve 'Achieve ECC' DC(DefaultSC.ECC = 0, {Tolerance = 0.1});
  :126  EndTarget;  % For targeter DC
  :128  Propagate 'Prop 1 Day' DefaultProp(DefaultSC) {DefaultSC.ElapsedSecs = 86400};
  ```
  逐行：`:115` 先传播到近地点；`:118` 打开 Target 段（`SolveMode=Solve` 求真实解、`ExitMode=DiscardAndContinue` 失败不中止）；`:119` `Vary` 让 DC 以 `TOI.Element1`（V 向速度增量）为自变量（初值 0.5，扰动、上下界、最大步长）；`:120` `Maneuver` 施加该点火；`:121` 传播到远地点；`:122` `Achieve` 约束 `RMAG=42165 km`（GEO 半径）；`:123-125` 第二阶段变 `GOI.Element1` 圆化轨道（`ECC=0`）；`:128` 最后传播 1 天。这是 GMAT "Vary→Maneuver→Propagate→Achieve" 打靶套路的**最小教科书范例**。

#### 2.4.2 `Ex_GEOTransfer.script`（305 行）—— 三阶段 GEO 转移（完整 GUI 导出风格）

这是 GUI "另存为脚本" 的典型产物：航天器段（`:13-44`）设置 `DateFormat=TAIModJulian`、`Epoch='21545'`、6 个开普勒根数（`:19-24`）与质量/阻力/光压（`:25-29`）、`NAIFId`、姿态显示（`:30-44`）。力模型段（`:51-67`）配 `CentralBody=Earth`、`SRP=On`、20×20 地球重力场 `JGM2.cof`（`:58-60`）、`MSISE90` 大气（`:64-67`）。传播器段（`:73-82`）选 `PrinceDormand78` 积分器、`InitialStepSize=60`、`Accuracy=1e-12`。

三次打靶（`:272-295`）对应"抬远地点→变面+改近地点→降远地点"：
- `:272-277` 变 `TOI.Element1` 使远地点 `RMAG=85000`；
- `:282-289` 同时变 `MCC.Element1/Element2`（V、N 分量）实现变面与改近地点，`Achieve INC=2` + `RMAG=42195`；
- `:291-295` 变 `MOI.Element1` 使 `SMA=42166.90`。

`Create Variable I lowerBound upperBound`（`:127`）与 `lowerBound=-119; upperBound=-117.5;`（`:129-130`）演示变量声明与赋值。`DC` 求解器段（`:136-142`）设 `ShowProgress/ReportStyle/ReportFile/MaximumIterations=25/DerivativeMethod=ForwardDifference`。

#### 2.4.3 `Ex_LunarTransfer.script`（332 行）—— 地月转移（B 平面打靶 + 月球捕获）

- **航天器**（`:14-30`）：`DateFormat=UTCGregorian`、笛卡尔状态（`:20-25`，近地停泊轨道）。
- **双力模型**：`AllForces`（地球中心，`:36-61`，`PointMasses={Sun,Luna,Venus,Mars,...}` 多体，`:40`）与 `MoonAllForces`（月球中心，`:62-76`，`LP165P.cof` 月球重力场）。对应双传播器 `EarthFull`（`:78-87`）与 `MoonFull`（`:89-98`）。
- **坐标系**（`:126-147`）：`EarthSunRot`、`MoonMJ2000Eq`、`EarthMoonRot` 三个自定义坐标系（`ObjectReferenced` 轴，`:129-133`）。
- **任务序列**（`:287-332`）核心是 B 平面打靶：

  ```
  :293  Propagate 'Prop to Perigee' EarthFull(Sat) {Sat.Periapsis};
  :299  Target 'Target B-Plane' DC1 {SolveMode = Solve, ExitMode = DiscardAndContinue, ShowProgressWindow = true};
  :301    Vary 'Vary TOI.V' DC1(TOI.Element1 = 0.14, {...});
  :302    Vary 'Vary TOI.B' DC1(TOI.Element3 = 0.1,  {...});
  :304    Maneuver 'Apply TOI' TOI(Sat);
  :306    Propagate 'Prop to Moon SOI' EarthFull(Sat) {Sat.Earth.RMAG = 325000, StopTolerance = 1e-005};
  :307    Propagate 'Prop to Periselene' MoonFull(Sat) {Sat.Luna.Periapsis, StopTolerance = 1e-005};
  :309    Achieve 'Achieve BdotR' DC1(Sat.MoonMJ2000Eq.BdotT = 15000.4401777, {Tolerance = 3});
  :310    Achieve 'Achieve BdotT' DC1(Sat.MoonMJ2000Eq.BdotR = 4000.59308992, {Tolerance = 3});
  :313  EndTarget;  % For targeter DC1
  :318  Target 'Target Lunar Insertion' DC1 {...};
  :320    Vary 'Vary LOI.V' DC1(LOI.Element1 = -0.65198120104, {...});
  :322    Maneuver 'Apply LOI' LOI(Sat);
  :324    Achieve 'Achieve ECC = 0' DC1(Sat.Luna.ECC = 0, {Tolerance = 0.0001});
  :326  EndTarget;
  :332  Propagate 'Prop 15 days' MoonFull(Sat) {Sat.ElapsedDays = 15};
  ```
  逐行：`:293` 传至近地点；`:299` 开 Target 段；`:301-302` 双自变量（`TOI.Element1` 的 V 分量 + `Element3` 的 B 分量）打 B 平面；`:304` 施加点火；`:306` 地球传播到月球影响球（`RMAG=325000` 近似月球 SOI）；`:307` 切换 `MoonFull` 传到近月点；`:309-310` 用 `BdotT/BdotR` 约束 B 平面坐标（`Tolerance=3 km`）；`:318-326` 第二次打靶用 `LOI.Element1` 把月球轨道圆化（`ECC=0`）；`:332` 传播 15 天。此处展示了 **跨中心体传播器切换** 与 **B 平面参数** 两个高级用法。

#### 2.4.4 `Ex_MarsOrbit.script`（305 行）—— 火星星座 + Formation

- **星座**（`:15-128`）：创建 `MPS1..MPS4`（RAAN 依次 0/90/180/270 的四星 Walker 构型，`:24,44,63,82`）与 `MarsOrbiter`、`MarsSupply`（双曲线轨道 `SMA=-30000, ECC=1.3`，`:118-119`）；`Create Formation MPS; MPS.Add = {...}`（`:130-131`）把六星打包成编队对象。
- **三套力模型/传播器**（`:137-188`）：`MarsProp_ForceModel`（火星中心点质量）、`EarthProp_ForceModel`、`SunProp_ForceModel`。
- **任务序列**（`:300-304`）：`Propagate 'Prop to Periapsis' MarsProp(MPS, {MPS1.Mars.Periapsis});` —— 注意传播对象是 `MPS`（编队），停止条件引用 `MPS1.Mars.Periapsis`；随后 `Maneuver 'Apply TOI' TOI(MarsSupply)` 对单星点火，`Propagate 'Prop 1 Day' MarsProp(MPS, {MPS1.ElapsedDays = 1})`。脚本 `:300` 的 `BeginMissionSequence` 无分号、`:118/:157/:223/:241` 等行省略分号，是 GMAT 解析器**容忍缺分号**的例证（较旧脚本）。

#### 2.4.5 `Tut_SimulatingAnOrbit.script`（143 行）—— "模拟一条轨道"教程

最小可运行轨道传播：航天器段（`:12-43`）用开普勒根数定义高椭圆轨道（`SMA=83474.318, ECC=0.89652, TA=180`，`:18-23`）；力模型段（`:46-66`）配 10×10 地球重力 + `JacchiaRoberts` 大气 + `PointMasses={Luna,Sun}`（`:50`）；传播器段（`:72-81`）`RungeKutta89`；任务序列仅一行 `Propagate LowEarthProp(Sat) {Sat.Earth.Periapsis};`（`:143`）。它是新用户入门的最小范例，也是 `Ex_ControlFlow`、`Ex_MathInScript` 等脚本的基座。

#### 2.4.6 `Ex_MarsBPlane.script`（356 行）—— 火星 B 平面打靶（MAVEN 型任务）

- **航天器 + 贮箱**（`:12-62`）：`Create Spacecraft MAVEN`（笛卡尔近地状态，`:18-23`）、`Create ChemicalTank MainTank`（`:53-62`，`FuelMass=1718`、`PressureRegulated`）；`MAVEN.Tanks={MainTank}`（`:29`）。
- **三力模型**（`:68-111`）：`NearEarth_ForceModel`（地球，8×8 JGM2）、`DeepSpace_ForceModel`（日心，`:85-95`）、`NearMars_ForceModel`（火星，8×8 Mars50c）。
- **变量**（`:319-321`）：`Create Variable EarthSOI MarsSOI BdotT BdotR deltaV; EarthSOI=1000000; MarsSOI=577204;`。
- **任务序列**（`:327-350`）两段打靶：

  ```
  :330  Target DC {SolveMode = Solve, ExitMode = DiscardAndContinue, ShowProgressWindow = true};
  :331-333  Vary TCM1.Element1/Element2/Element3 （三维 TCM 修正）
  :334    Propagate 'Prop 3 Days' NearEarth(MAVEN) {MAVEN.ElapsedDays = 3, StopTolerance = 1e-005};
  :335    Propagate 'Prop to TCM1' DeepSpace(MAVEN) {MAVEN.ElapsedDays = 12, StopTolerance = 1e-005};
  :336    Maneuver 'Apply TCM1' TCM1(MAVEN);
  :337    Propagate 'Prop 280 Days' DeepSpace(MAVEN) {MAVEN.ElapsedDays = 280};
  :338    Propagate 'Prop to Mars Periapsis' NearMars(MAVEN) {MAVEN.Mars.Periapsis, MAVEN.ElapsedDays = 20};
  :339    Achieve 'Achieve BdotT' DC(MAVEN.MarsInertial.BdotT = 2700, {Tolerance = .1});
  :340    Achieve 'Achieve BdotR' DC(MAVEN.MarsInertial.BdotR = -7000, {Tolerance = .1});
  :341  EndTarget;
  :343  Target DC {...};
  :344    Vary 'Vary MOI.V' DC(MOI.Element1 = -2, {...});
  :345    Maneuver 'Apply MOI' MOI(MAVEN);
  :346    Propagate 'Prop to Mars Apoapsis' NearMars(MAVEN) {MAVEN.Mars.Apoapsis};
  :347    Achieve 'Achieve RMAG' DC(MAVEN.Mars.RMAG = 12000, {Tolerance = .1});
  :348  EndTarget;
  ```
  逐行：`:331-333` 三个 `Vary` 以 TCM1 的三轴分量为自变量；`:334-338` 依次地球段→日心段→TCM→日心段→火星段，`StopTolerance` 控制事件定位精度，`:338` 的停止条件同时含 `Mars.Periapsis` 与 `ElapsedDays=20`（取先到者）；`:339-340` 用火星惯性系 B 平面 `BdotT/BdotR` 收敛；`:343-348` 第二次打靶求 `RMAG=12000` 的火星捕获。这是 GMAT **行星际打靶** 的完整示范。

#### 2.4.7 `Ex_ControlFlow.script`（112 行）—— For / While / If 控制流

脚本头（`:1-5`）说明"演示 For、While、If"。对象只建最小集：`Sat`（`:12-23`）、点质量力模型 `FM` 与传播器 `EarthPointMass`（`:29-32`）、变量 `I`（`:38`）。任务序列（`:81-112`）四种控制流：

  ```
  :86   For 'For I = 1:1:5' I = 1:1:5;
  :87     Propagate 'Prop to Apoapsis' EarthPointMass(Sat) {Sat.Apoapsis};
  :88   EndFor;
  :93   While 'While Epoch < 26882' Sat.TAIModJulian < 26882
  :94     Propagate 'Prop to Apoapsis' EarthPointMass(Sat) {Sat.Apoapsis};
  :95   EndWhile;
  :101  If 'If Sat.TA > 178' Sat.TA > 178
  :102    Propagate 'Prop to Periapsis' EarthPointMass(Sat) {Sat.Periapsis};
  :103  EndIf;
  :108  If 'If Sat.TA > 90' Sat.TA > 90
  :109    Propagate 'Prop to Periapsis' ...
  :110  Else
  :111    Propagate 'Prop to Apoapsis' ...
  :112  EndIf;
  ```
  逐行：`:86` For 循环（`I=1:1:5` 步进语法）；`:93` While 用 `Sat.TAIModJulian` 做条件；`:101` 单分支 If；`:108-112` If/Else 二分支。每类控制流命令都以首参数字符串作**显示标签**（`'For I = 1:1:5'` 等），对应 `GmatCommand` 的 `GetStringParameter("MissionSummary")` 所输出的文本。

#### 2.4.8 `Ex_GMATFunction_Math.script`（32 行）—— GMAT 函数调用

```
:11  Create GmatFunction cross;
:13  Create Array crossProd[3,1] vec1[3,1] vec2[3,1]
:15  Create ReportFile rf
:20  BeginMissionSequence;
:22-24  vec1(1,1)=0.5; vec1(2,1)=-0.5; vec1(3,1)=0.75;
:26-28  vec2(1,1)=1.5; vec2(2,1)=-5.5; vec2(3,1)=7.75;
:30  [crossProd] = cross(vec1,vec2)
:32  Report rf crossProd
```
逐行：`:11` 声明一个 `GmatFunction` 对象（函数体在 `userfunctions/gmat/cross.gmf`，见 2.5.1）；`:13` 声明三个 3×1 数组；`:15` 声明报告文件订阅者；`:30` 用 `[输出] = 函数(输入)` 语法调用 GMAT 函数；`:32` `Report rf crossProd` 把结果写入报告文件。这是"脚本↔GmatFunction 文件"协同的最小示例。

#### 2.4.9 `Ex_IncludeMacro.script`（69 行）—— #Include 预处理宏

```
:12  #Include './SupportFiles/Ex_IncludeFile.script'
:19  Create Spacecraft DefaultSC;
:24  %(Already defined in Ex_IncludeFile.script)
:25  %Create ForceModel DefaultProp_ForceModel;
:26  %Create Propagator DefaultProp;
:28  DefaultProp.FM = DefaultProp_ForceModel;
:67  BeginMissionSequence;
:69  Propagate DefaultProp(DefaultSC) {DefaultSC.ElapsedSecs = 12000.0};
```
逐行：`:12` 的 `#Include` 把 `SupportFiles/Ex_IncludeFile.script`（其中已定义 `DefaultProp_ForceModel`、`DefaultProp`）内联进当前脚本；`:24-26` 注释说明"不要在本地重复创建"；`:28` 直接引用 include 进来的传播器。`#Include` 由解析器在**解释期**展开（等价于文本替换），是 GMAT 脚本复用的核心机制；`GMAT_INCLUDE_PATH` 启动键（`gmat_startup_file.txt:105`）即为此服务。

#### 2.4.10 `Ex_MathInScript.script`（222 行）—— 脚本内代数 + BeginScript

演示在脚本里手算开普勒根数并与 GMAT 内部换算对比。对象段：`Sat` 笛卡尔状态（`:22-33`）、传播器 `Prop`（`:41-50`）、数组 `rv/vv/hv/ev/nv`（`:56`）、大堆变量（`:59-61`）。任务序列（`:115-219`）：

- `:117-126` `BeginScript 'Define Constants' ... EndScript;` 定义 `pi2/d2r/mu/SMA/RAAN` 常量；
- `:128-219` `While 'While ElapsedDays < 1' Sat.ElapsedDays < 1.0` 循环内：`:130` `Propagate 'Prop One Step' Prop(Sat);` 推一步；`:133-198` `BeginScript 'Compute Kep Elements'` 内用叉积、点积、`sqrt/acos` 手算 `h/e/n/r/v`、`ECC/SMA/INC/RAAN/AOP/TA`，并用 `If ... EndIf` 修象限（`:179-197`）；`:201-216` `BeginScript 'Convert and Compare'` 转角度并算误差。
- 该脚本是 **BeginScript（内联脚本块）** 与 GMAT 内置数学函数（`sqrt/acos/DegToRad/norm` 等）的完整展示。

#### 2.4.11 `Ex_Integrators.script`（161 行）—— 六种数值积分器对比

`:36-38` 点质量力模型；`:46-106` 依次创建 6 个传播器，`Type` 分别为 `RungeKutta56 / RungeKutta68 / RungeKutta89 / PrinceDormand45 / PrinceDormand78 / AdamsBashforthMoulton`（`:49,59,69,79,89,99`），ABM 额外设 `LowerError/TargetError`（`:104-105`）。任务序列 `:154-161` 用六个传播器各传播 0.1 天（`:156-161`），逐条对照数值行为。它展示了 GMAT 支持的**全部积分器类型名**。

#### 2.4.12 `Ex_ElectricPropulsion.script`（343 行）—— 电推进 + FiniteBurn

- **硬件**（`:39-92`）：`ElectricTank ElectricTank1`（`:39-42`）、`ElectricThruster ElectricThruster1`（`:44-73`，`ThrustModel=ConstantThrustAndIsp`、多项式推力/质量流系数 `:61-70`、`Isp=2800`）、`SolarPowerSystem SolarPowerSystem1`（`:76-92`，`DualCone` 影模型）。
- **`FiniteBurn`**（`:150-153`）：`Create FiniteBurn FiniteBurn1; FiniteBurn1.Thrusters={ElectricThruster1}; FiniteBurn1.ThrottleLogicAlgorithm='MaxNumberOfThrusters';`。
- **任务序列**（`:327-341`）：`:330` 滑行 2 小时；`:332` `BeginFiniteBurn FiniteBurn1(DefaultSC);` 开启连续推力；`:333` 在推力下传播 1.98 天（`OrbitColor=Red` 标注）；`:336` `EndFiniteBurn` 关闭；`:337-341` 后续到达月球近点/地球远点/近点/`RMAG=400000` 等事件。这是**连续推力（FiniteBurn）**与**电推进硬件链**（航天器→贮箱→推力器→电源系统）的完整示例。

### 2.5 userfunctions / userincludes

#### 2.5.1 `userfunctions/gmat/`（8 个 `.gmf` + .gitignore）

GMAT 函数文件（`.gmf`），由 `Create GmatFunction` 或直接调用加载；搜索路径来自 `GMAT_FUNCTION_PATH`（`gmat_startup_file.txt:107`）。代表文件：

- **`cross.gmf`（9 行）**：叉积函数。第 1 行 `function [crossProd] = cross(vec1,vec2)` 声明签名；`:3` `Create Array crossProd[3,1]`；`:5` `BeginMissionSequence`；`:7-9` 三行赋值计算叉积分量。与 `Ex_GMATFunction_Math.script:30` 的 `[crossProd] = cross(vec1,vec2)` 完全对应。

- **`PropagateQuaternion.gmf`（50 行）**：四元数常角速度传播。`:6` `function [qNew] = PropagateQuaternion(q, w, dt)`；`:23-27` 创建数组/变量；`:33-35` `DegToRad` 把角速度转弧度；`:36-37` 计算 `Wmag` 与半转角 `Phi`；`:39-42` 构造四元数导数矩阵 `OmegaQ`；`:50` `qNew = cos(Phi)*q + (1/Wmag)*sin(Phi)*OmegaQ` 闭合解。展示了 `.gmf` 里也能用 `DegToRad/norm` 等内置函数与向量数组。

- **`QualityFactor.gmf`（146 行）**：MMS 编队品质因子。`:1` 签名含 7 个输入（4 航天器 + `FormSize`）与 7 个输出；`:23-27` 建位置/相对位置数组；`:41-52` 取各航天器 `X/Y/Z`；`:56-89` 按 `FormSize` 查表 `sizeConstant1..4`；`:93-98` 相对位置向量；`:102-107` 边长；`:111-115` 用三阶行列式算体积；`:119-124` 平均边长与理想体积、`QFvol`；`:128-142` 分段 `QFsize`；`:146` `QF = QFvol*QFsize`。展示了 `.gmf` 支持 `If/EndIf` 分支与**多返回值**。

其余 `.gmf`（`ComposeQuaternions`、`TargeterInsideFunction`、`TargetLEOStationKeeping`、`ToggleQuaternion`、`GMATFunction_1st_Targeter_In_Function_2nd_In_Script`）覆盖函数内打靶、四元数合成/翻转等，目录级说明即可。

#### 2.5.2 `userfunctions/python/`（18 个 `.py` + .gitignore + 7 个 socket-test-drivers）

Python 用户模块，搜索路径 `PYTHON_MODULE_PATH`（`gmat_startup_file.txt:112`）。代表文件：

- **`MathFunctions.py`（72 行）**：一组数学测试函数。`sqrt`（`:13-19`）、`add`（`:22-23`）、`addVerbose`（多返回值，`:26-27`）、`cross`（`:30-35`）、`crossArray`（返回 list，`:38-43`）、`magnitude`（`:46-47`）、`crossmag`（`:50-52`）、`anticross`（返回 list-of-list 的楔积矩阵，`:62-72`）。演示 GMAT Python 接口对"标量/多返回/list/list-of-list"四类返回值的类型映射。

- **`SimpleExternalForceModel.py`（88 行）**：自定义外部力模型。`GetDerivativesSRP(s, t, d, o)`（`:29`）实现"二体 + 太阳光压"的导数：`:31-33` 拆位置/速度；`:34` `mu=3.986004415e5`；`:38-48` 点质量加速度；`:54-58` 用 `gmat.GetObject('Sun')` 取太阳位置算相对矢量；`:60-67` 用 `gmat.GetRuntimeObject('SatExternal')` 取 `Cr/SRPArea/TotalMass`；`:73-78` 光压加速度；`:85` 合成导数。演示了 Python 侧如何调用 GMAT API 对象（`GetObject/GetRuntimeObject/GetNumber/GetMJ2000Position`）参与动力学计算。

- `SimpleExternalForceModel_NoAPI.py`、`AttitudeInterface.py`、`AttitudeTypes.py`、`IODFunctions.py`、`ArrayFunctions.py`、`StringFunctions.py`、`SimpleSockets.py` 及 `socket-test-drivers/` 7 文件（与 GMAT 通过 socket 同步 MJD/四元数，用于 COSMOS 联调）为同类补充。

#### 2.5.3 `userincludes/`（2 文件）

- **`CreateIncludeSatA.script`（8 行）**：创建 `IncludeSatA` 设 `X/Z`（`:1-4`）、创建 `IncludeSatB`（`:6`），再 `#Include './InitializeNestedIncludeSatB.script'`（`:7`）——演示 **include 的嵌套**。
- **`InitializeNestedIncludeSatB.script`（2 行）**：被嵌套包含的片段，仅两行赋值 `IncludeSatB.X/Z`（`:1-2`）。二者配合说明 `#Include` 可任意嵌套、且被包含文件可引用包含方已创建的对象。

### 2.6 matlab/（21 文件）

MATLAB 接口分两组：

#### 2.6.1 `gmat_keyword/`（15 文件）—— 关键字式 DDE/套接字接口

这是 GMAT 早期 MATLAB 接口：MATLAB 通过 DDE（Windows）或套接字（Unix）向正在运行的 GMAT GUI 发送脚本命令字符串。`gmat_startup.m`（`:12-17`）`format long g` 并把两个子目录加入 MATLAB 路径。核心函数：

- **`CallGMAT.m`（81 行）**：把命令名 + 参数拼成 `'Create Spacecraft sat1;'` 形式（`:42-66`），Unix 走 `SendGMAT('Poke',str)`（`:70-72`），Windows 走 `Poke(gmatChannel,'script',str)`（`:79`）。
- **`OpenGMAT.m`（48 行）**：初始化会话，Windows 用 `ddeinit('4242','GMAT-MATLAB')`（`:24-35`），通道为 0 表示 GMAT 服务器未启动（`:42-43`）。
- **`RunGMAT.m`（17 行）**：`CallGMAT('Run','')` 触发构建并运行。
- 配套：`BuildRunGMAT`、`CloseGMAT`、`ClearGMAT`、`GetGMATObject`、`GetGMATVar`、`Poke`、`Request`、`UpdateGMAT`、`WaitForCallback`、`WaitForCallbackResults`、`WaitForGMAT`、`Advise`——构成完整的"建对象→改参数→跑任务→取结果"闭环。

#### 2.6.2 `gmat_fmincon/`（4 文件）—— fmincon 优化器驱动

- **`GmatFminconOptimizationDriver.m`（48 行）**：GMAT 调 MATLAB 的入口。`:41` 声明全局非线性约束；`:42` `OpenGMAT`；`:44-45` 调 `fmincon(@EvaluateGMATObjective, X0, ..., Lower, Upper, @EvaluateGMATConstraints, ...)`；`:47` `CallGMATfminconSolver(X)` 把收敛解回灌 GMAT。
- **`EvaluateGMATObjective.m` / `EvaluateGMATConstraints.m`**：供 fmincon 回调，分别经 `CallGMATfminconSolver` 请求 GMAT 计算目标值与约束。
- **`CallGMATfminconSolver.m`**：与 GMAT `FminconOptimizer` 插件通信的桥接函数。

### 2.7 api/（24 文件）

GMAT R2020a 起内置的官方 API，`API_README.txt`（`:1-63`）说明 Python/MATLAB 双环境用法与 `BuildApiStartupFile.py` 配置步骤。

- **`load_gmat.py`（28 行）**：模板加载器。`:12` `GmatInstall = "<TopLevelGMATFolder>"`（用户需改为本机路径）；`:19-22` 把 bin 加入 `sys.path` 并 `import gmatpy as gmat; gmat.Setup(Startup)`。
- **`BuildApiStartupFile.py`**：生成 `api_startup_file.txt`（把启动文件相对路径改绝对路径），使 API 可从任意目录运行。
- **`Ex_R2020a_*.py/.m`**（成对，16 个）：`BasicFM`、`BasicForceModel`、`CompleteForceModel`、`FindTheMoon`、`PropagationLoop`、`PropagationStep`、`RangeMeasurement` 七组的 Python/MATLAB 双实现；`Ex_R2025a_BasicTarget`、`Ex_R2025a_MarsBPlane` 为 R2025a 新增。其中 `Ex_R2020a_FindTheMoon.py`（65 行）是**参数扫描**范例：`:22-24` `gmat.GetObject("TOI"/"LeoTime"/"StartEpoch")` 取脚本对象；`:34-53` 三重循环 `SetField` 改值→`gmat.RunScript()`→`GetRuntimeObject("MoonDistance")` 读结果→记录最优；`:60-65` 回写最优解并 `gmat.SaveScript`。完整展示了 API 的 `LoadScript/GetObject/SetField/RunScript/GetRuntimeObject/GetNumber/SaveScript` 调用链。
- **`Ex_R2020a_ToLuna.script`（168 行）**：被上述脚本驱动的核心脚本，与普通 `.script` 结构相同，只是参数都用 `Create Variable` 显式声明（`:144-147`），以便 API 侧 `SetField` 修改。注意其命令行为 `GMAT Sat.DateFormat = ...`（`:10` 起带 `GMAT` 前缀），是 GMAT 脚本语言的等价写法。
- **`Jupyter/`（2 个 `.ipynb`）**：`Ex_R2020a_GMAT_Propagation.ipynb`、`Ex_R2020a_GMAT_States.ipynb` 交互式教学笔记本。

### 2.8 utilities/python/（13 文件）

- **`GMATDataFileManager.py`（747 行）**：数据文件更新工具（`GMATFileManager` 类）。`:14-62` docstring 说明功能与用法；构造函数（`:63-130`）配置目录、文件名、URL（`usnoLeapSecURL/naifURL/eopURL/spaceWeatherURL` 等，`:108-124`）；`UpdateAllFiles()`（`:147-202`）逐一调用 9 个 `Update*` 方法并汇总结果；`Downloadfile`（`:581-597`）用 `urllib.request.urlretrieve` 下载；`DownloadFTP`（`:600-635`）FTP 批量下载；`Handleoldfile/Archivefile`（`:637-661`）归档旧文件；`ExtractContentAndWrite`（`:663-707`）从 CSSI 空间天气文件解析 Ap 数据。脚本尾部 `:710-746` 是用户需修改的路径配置与主流程。
- **`navigation/`（12 文件）**：`README.txt` 说明这些是 EKF 滤波/平滑结果分析与 TDM/TRK-2-34/UTDF→GMD 转换工具（`:1-29`）。`export_measurements.py`、`plot_*.py`（6 个绘图）、`filter_smoother_consistency.py`、`tdm_to_gmd.py`、`trk234_to_gmd.py`、`utdf_to_gmd.py`、`xyz_to_vnb.py`。

### 2.9 extras / debug / docs / plugins / output（目录级）

- **`extras/`（2 文件）**：`README.txt`（`:1-11`）说明 `notepad++.xml` 是 Notepad++ 的 GMAT 语法高亮（识别 `.script/.gmf`）。
- **`debug/`（7 文件）**：与 `bin/` 结构相同的调试配置镜像（`GMAT.ini`、`gmat_startup_file.txt`、`gmat_startup_file_debuginstall.txt`、`gmatpy/`、`load_gmat.m`），用于 debug 安装目录。
- **`docs/`（约 277 文件）**：HTML/PDF 文档与 Sphinx 源码（`GMAT_API_Cookbook`、`GMAT_API_OC_HTML`、`CSALT_*` PDF 等），纯文档资源，目录级说明。
- **`plugins/`（2 文件）**：仅 `.gitignore` 与 `proprietary/.gitignore`——运行时插件库由构建系统生成到 `application/plugins/`，仓库内不提交二进制。
- **`output/`（1 文件）**：仅 `.gitignore`。**缺口**：本章任务要求覆盖"示例任务输出/脚本"，但该目录在 depth-1 克隆中为空（运行时产物不纳入版本库），故无法提供示例输出，运行时 `OUTPUT_PATH`（`gmat_startup_file.txt:97`）会在此生成 `GmatLog.txt`、报告、星历等。

## 三、关键设计模式与数据流

1. **单一 core、双前端**：GUI 与控制台共用 `Moderator`（单例）+ `CommandFactory/FactoryManager/FileManager`（均在 `src/base`），差异仅在 `MessageInterface` 接收器（`GuiMessageReceiver` vs `ConsoleMessageReceiver`）、Publisher（`GuiPublisher` vs 默认）与解释器/命令序列呈现（GUI 编辑器 vs `PrintUtility`）。`src/console/CMakeLists.txt:46-47` 只链 `GmatUtil+GmatBase` 即是"core 全在库里"的证明。

2. **消息接收器多态**：`MessageReceiver` 是抽象接口，`ConsoleMessageReceiver`（`src/console/ConsoleMessageReceiver.hpp:43`）把 `ShowMessage/PopupMessage/LogMessage` 统一为"控制台 + 日志文件"，弹出窗语义被降级为日志（`.cpp:163-222`）；GUI 版则接 wx 事件。二者都通过 `MessageInterface::SetMessageReceiver` 静态注入（`driver.cpp:592` / `GmatApp.cpp:96`）。

3. **启动文件驱动一切**：`gmat_startup_file.txt` 是配置中心——插件加载、路径（include/函数/Python/MATLAB/数据）、输出目录、日志全部由 `Moderator::Initialize(startupFile)` → `FileManager` 解析。控制台必须先读启动文件才能设日志文件（`driver.cpp:612-613`），因为 `LOG_FILE` 依赖 `OUTPUT_PATH`（`gmat_startup_file.txt:97-98`）。

4. **命令树 + 打靶数据流**：脚本 `InterpretScript` 生成 `GmatCommand` 链表（含 `Target/For/If` 子分支），`PrintUtility::PrintEntireSequence` 递归打印（`PrintUtility.cpp:63-125`）；执行时 `Target` 命令内 `Vary` 改自变量→`Maneuver` 施冲量→`Propagate` 推轨道→`Achieve` 判收敛，`DifferentialCorrector` 反复迭代（见 `Ex_HohmannTransfer.script:118-126`）。

5. **脚本↔函数↔include 协同**：`#Include` 文本内联（`Ex_IncludeMacro.script:12`）、`GmatFunction` 调用 `.gmf`（`Ex_GMATFunction_Math.script:30` ↔ `cross.gmf`）、Python 模块（`SimpleExternalForceModel.py` 回调 GMAT API）三种扩展机制共享 `GMAT_INCLUDE_PATH/GMAT_FUNCTION_PATH/PYTHON_MODULE_PATH` 搜索路径。

6. **调用链（控制台）**：`main → Moderator::Initialize(startupFile) → CreateDefaultParameters → (交互/批处理) RunScriptInterpreter → mod->InterpretScript → mod->GetFirstCommand → PrintUtility 打印 → mod->RunMission → Moderator::Finalize → exit(EXIT_SUCCESS/FAILURE)`。

7. **调用链（API）**：`load_gmat.py → gmatpy.__init__ → import _py312 → FileManager.SetBinDirectory → gmat.Setup(startup) → (示例) GetObject/SetField/RunScript/GetRuntimeObject`；MATLAB 侧对应 `load_gmat.m → gmat.Moderator.Instance + gmat.gmat.Setup`。

## 四、文件清单附录

### 4.1 src/console/（9 文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| src/console/CMakeLists.txt | 构建 GmatConsole 目标 | `TargetName=GmatConsole`、`ADD_EXECUTABLE`、链接 GmatUtil/GmatBase |
| src/console/driver.cpp | main() 与命令行分发 | `main`、`RunScriptInterpreter`、`RunBatch`、`ShowHelp`、`CheckForStartupAndLogFile`、`SaveScript`、`ShowCommandSummary`、`DumpDEData` |
| src/console/driver.hpp | 顶层函数原型与命令枚举 | 枚举 `RUN_SCRIPT..VERBOSE`、各函数声明 |
| src/console/ConsoleMessageReceiver.cpp | 控制台消息接收器实现 | `Instance`、`ShowMessage`、`PopupMessage`、`LogMessage`、`OpenLogFile`、`GetLogFileName` |
| src/console/ConsoleMessageReceiver.hpp | 消息接收器声明（单例） | `class ConsoleMessageReceiver : public MessageReceiver` |
| src/console/ConsoleAppException.cpp | 控制台异常实现 | `ConsoleAppException(std::string)` |
| src/console/ConsoleAppException.hpp | 控制台异常声明 | `class ConsoleAppException : public BaseException` |
| src/console/PrintUtility.cpp | 命令序列打印实现 | `Instance`、`PrintEntireSequence`、`PrintBranch` |
| src/console/PrintUtility.hpp | 命令序列打印声明 | `class PrintUtility`（exe 内部，无 GMAT_API） |

### 4.2 application/bin/（12 文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| application/bin/GMAT.ini | GUI 帮助/提示/欢迎页配置 | `[Help]`、`[Propagator]` 等 Hint 键 |
| application/bin/gmat_startup_file.txt | 全局启动文件（插件/路径/数据） | `PLUGIN`、`ROOT_PATH`、`OUTPUT_PATH`、`*_FUNCTION_PATH` |
| application/bin/gmat_startup_file.public.txt | 公开版启动文件（去专有插件） | 同主启动文件 |
| application/bin/gmat_startup_file_mac_linux.txt | Unix 版启动文件 | 同主启动文件 |
| application/bin/gmat_startup_file_mac_linux.public.txt | Unix 公开版启动文件 | 同主启动文件 |
| application/bin/gmatpy/__init__.py | Python API 包入口 | 版本探测 `_pyXY`、DLL 预加载、`SetBinDirectory` |
| application/bin/gmatpy/__init__.specific.py | 版本专用子包入口 | `from .gmat_py import *` 等 |
| application/bin/load_gmat.m | MATLAB API 加载 | `load_gmat`、`cleanupFun` |
| application/bin/MacConfigure.txt | macOS MATLAB/SNOPT 路径模板 | `MATLAB_APP_PATH` 等 |
| application/bin/.gitattributes / .gitignore / __pycache__/.gitignore | VCS 配置 | — |

### 4.3 application/samples/（197 文件，按子目录）

| 相对路径 | 文件数 | 职责 | 代表文件 |
|---|---|---|---|
| application/samples/*.script（Ex_ 前缀） | 78 | 功能示例 | Ex_HohmannTransfer、Ex_GEOTransfer、Ex_LunarTransfer、Ex_MarsOrbit、Ex_MarsBPlane、Ex_ControlFlow、Ex_MathInScript、Ex_Integrators、Ex_ElectricPropulsion、Ex_IncludeMacro、Ex_GMATFunction_Math |
| application/samples/*.script（Tut_ 前缀） | 10 | 用户指南教程 | Tut_SimulatingAnOrbit、Tut_SimpleOrbitTransfer、Tut_Mars_B_Plane_Targeting |
| application/samples/Navigation/ | 24 | 估计/滤波/测量仿真 | Ex_Estimate_*、Ex_FilterSmoother_GpsPosVec、Ex_RICdelta.gmf |
| application/samples/CSALT/ | 46 | 最优控制 C++ 样例（Driver/Point/Path/OcfObj 模板） | 1-Brachistochrone、6-GMAT-Hohmann、include/*.hpp、src/*Template.cpp |
| application/samples/NeedMatlab/ | 2 | 依赖 MATLAB 的示例 | Ex_CallMatlabFunctions、Ex_MatlabEnv |
| application/samples/NeedSNOPT/ | 3 | 依赖 SNOPT 的示例 | Ex_AlgebraicOptimization、Ex_MinFuelLunarTransfer、Ex_OptFiniteBurn |
| application/samples/NeedVF13ad/ | 13 | 依赖 VF13ad 优化器 | Ex_MarsLaunchWindowAnalysis、Tut_MultipleShootingTutorial_Step1..5 |
| application/samples/OptimalControl/ | 9 | CSALT/EMTG 最优控制脚本 | Ex_CelestialBodyRendezvous_Mars、Ex_EarthToMarsSOI_C3Eq0_CSALTTutorial |
| application/samples/SupportFiles/ | 11 | 被 include/引用的数据与脚本 | Ex_IncludeFile.script、Ex_TLE_Propagation_TLE.txt、CSSI_2004To2026.txt |
| application/samples/AlphaAndBetaFeatures/ | 1 | 目录说明 | readme.txt |

### 4.4 application/ 其余目录

| 相对路径 | 文件数 | 职责 | 代表文件 |
|---|---|---|---|
| application/output/ | 1 | 运行时输出目录（空） | .gitignore |
| application/matlab/ | 21 | MATLAB 接口（keyword 接口 + fmincon 驱动） | gmat_startup.m、gmat_keyword/CallGMAT.m、gmat_fmincon/GmatFminconOptimizationDriver.m |
| application/utilities/python/ | 13 | Python 工具（数据更新 + 导航分析） | GMATDataFileManager.py、navigation/*.py |
| application/userfunctions/gmat/ | 9 | GMAT 函数文件（.gmf） | cross.gmf、PropagateQuaternion.gmf、QualityFactor.gmf |
| application/userfunctions/python/ | 17 | Python 用户模块 + socket 测试驱动 | MathFunctions.py、SimpleExternalForceModel.py、socket-test-drivers/*.py |
| application/userincludes/ | 2 | include 片段 | CreateIncludeSatA.script、InitializeNestedIncludeSatB.script |
| application/api/ | 24 | Python/MATLAB API 示例 | load_gmat.py、Ex_R2020a_FindTheMoon.py、Ex_R2020a_ToLuna.script |
| application/extras/ | 2 | Notepad++ 语法高亮 | notepad++.xml、README.txt |
| application/debug/ | 7 | debug 安装配置镜像 | GMAT.ini、gmat_startup_file_debuginstall.txt |
| application/docs/ | 约 277 | HTML/PDF/Sphinx 文档 | GMAT_API_Cookbook、GMAT_API_OC_HTML、CSALT_* 规范 |
| application/plugins/ | 2 | 插件输出目录（空） | .gitignore、proprietary/.gitignore |

> 本章关键源码入口补充说明：可执行程序的 `main()` 位于 `src/console/driver.cpp:556`（GmatConsole）与 `src/gui/app/GmatApp.cpp:87`（`IMPLEMENT_APP(GmatApp)`，GMAT GUI），并非在 `application/bin/` 内；`application/bin/` 仅存放运行时配置与部署文件。
