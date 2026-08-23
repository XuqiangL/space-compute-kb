# GMAT 导览（Tour of GMAT）
> 译自 GMAT R2026a 帮助文档 TourOfGmat.html

**第 3 章（Chapter 3）**

## 本章目录

- 用户界面概述（User Interfaces Overview）
  - 图形界面概述（GUI Overview）
  - 脚本界面概述（Script Interface Overview）
  - 图形界面/脚本界面交互与规则（GUI/Script Interface Interactions and Rules）
- 资源树（Resources Tree，见 ResourceTree.html）
  - 组织结构（Organization）
  - 文件夹菜单（Folder Menus）
  - 资源菜单（Resource Menus）
- 任务树（Mission Tree，见 MissionTree.html）
  - 任务树显示（Mission Tree Display）
  - 视图过滤工具栏（View Filters Toolbar）
  - 任务序列菜单（Mission Sequence Menu）
  - 命令菜单（Command Menu）
  - 停靠/取消停靠/位置摆放（Docking/Undocking/Placement）
- 命令摘要（Command Summary，见 CommandSummary.html）
  - 数据可用性（Data Availability）
  - 数据内容（Data Contents）
  - 支持的命令（Supported Commands）
  - 坐标系（Coordinate Systems）
- 输出树（Output Tree，见 Output.html）
- 脚本编辑器（Script Editor，见 ScriptEditor.html）
  - 活动脚本（Active Script）
  - 图形界面/脚本同步（GUI/Script Synchronization）
  - 脚本列表（Scripts List）
  - 编辑窗口（Edit Window）
  - 查找与替换（Find and Replace）
  - 文件控制（File Controls）
  - 保存状态指示器（Save Status Indicator）

## 用户界面概述（User Interfaces Overview）

GMAT 提供多种设计与执行任务的途径。两个主要界面是图形用户界面（GUI）和脚本界面（script interface）。这些界面可以互换，各自支持 GMAT 的大部分功能。当您在脚本界面中工作时，使用的是 GMAT 的自定义脚本语言。为避免诸如两个界面相互依赖（循环依赖）之类的问题，您必须遵循一些基本规则。下面我们讨论这些界面，然后讨论在每个界面中工作的基本规则与最佳实践。

### 图形界面概述（GUI Overview）

当您启动会话时，GMAT 桌面会显示一个已加载的默认任务。GMAT 桌面在每个平台上都具有原生的外观与体验，且大多数桌面组件在所有平台上都受支持。

#### Windows 图形界面（Windows GUI）

当您在 Windows 上打开 GMAT 并单击工具栏中的 Run（运行）时，GMAT 会执行默认任务，如下图所示。图下方列出的工具在 GMAT 桌面中可用。

> [图 3.1：GMAT 桌面（Windows）]

- **Menu Bar（菜单栏）**

  菜单栏包含 File（文件）、Edit（编辑）、Window（窗口）和 Help（帮助）功能。

  在 Windows 上，File 菜单包含标准的 Open（打开）、Save（保存）、Save As（另存为）和 Exit（退出）功能，以及 Open Recent（最近打开）。Edit 菜单包含脚本编辑器激活时的脚本编辑功能。Window 菜单包含在 GMAT 桌面内组织图形窗口和脚本编辑器的工具，例如 Tile（平铺）窗口、Cascade（层叠）窗口和 Close（关闭）窗口的功能。Help 菜单包含 Online Help（在线帮助）、Tutorials（教程）的链接，以及指向 GMAT 缺陷报告系统的 Report An Issue（报告问题）选项、Welcome Page（欢迎页）和 Provide Feedback（提供反馈）链接。

- **Toolbar（工具栏）**

  工具栏提供对常用控件的便捷访问，例如文件控件、用于任务执行的 Run（运行）、Pause（暂停）和 Stop（停止），以及图形动画控件。在 Windows 和 Linux 上，工具栏位于 GMAT 窗口顶部；在 Mac 上，它位于 GMAT 框架的左侧。由于工具栏在 Mac 上是垂直的，一些工具栏选项以缩写形式显示。

  GMAT 允许您同时编辑任务的原始脚本文件表示和 GUI 表示。这两种任务表示可能会产生不一致的更改。位于工具栏中的 GUI/Script Sync Status（GUI/脚本同步状态）指示器向您显示两种任务表示的状态。更多讨论见下文"GUI/脚本交互与同步（GUI/Script Interactions and Synchronization）"一节。

- **Resources Tab（资源选项卡）**

  Resources 选项卡将资源树（Resources tree）带到桌面前景。

- **Resources Tree（资源树）**

  资源树显示所有已配置的 GMAT 资源，并将它们组织成逻辑分组。在 GMAT 脚本中使用 Create（创建）命令创建的所有对象都可以在 GMAT 桌面的资源树中找到。

- **Mission Tab（任务选项卡）**

  Mission 选项卡将任务树（Mission Tree）带到桌面前景。

- **Mission Tree（任务树）**

  任务树显示控制任务中事件时间顺序的 GMAT 命令。任务树包含 GMAT 脚本中 `BeginMissionSequence`（开始任务序列）命令之后的所有脚本行。您可以取消停靠任务树（如下图所示），方法是右键单击 Mission 选项卡并将其拖到图形窗口中。您也可以按以下步骤操作：

  1. 单击 Mission 选项卡，将任务树带到前景。
  2. 在任务树中右键单击 Mission Sequence（任务序列）文件夹，并在菜单中选择 Undock Mission Tree（取消停靠任务树）。

  > [图 3.2：取消停靠的任务树（Undocked Mission Tree）]

- **Output Tab（输出选项卡）**

  Output 选项卡将输出树（Output Tree）带到桌面前景。

- **Output Tree（输出树）**

  输出树包含 GMAT 输出，例如报告文件和图形显示。

- **Message Window（消息窗口）**

  当您在 GMAT 中运行任务时，包括警告、错误和进度在内的信息会写入消息窗口。例如，如果脚本文件中存在语法错误，详细的错误消息会写入消息窗口。

- **Status Bar（状态栏）**

  状态栏包含有关 GUI 状态的各种信息性消息。任务运行时，左窗格中会出现 Busy（忙）指示器。当鼠标光标在星下点轨迹（Ground Track）窗口上移动时，中间窗格会显示光标的纬度和经度。

### 脚本界面概述（Script Interface Overview）

GMAT 脚本编辑器是一个文本界面，可让您直接使用 GMAT 的内置脚本语言编辑任务。在下图"图 3.3 GMAT 脚本编辑器"中，脚本编辑器在 GMAT 桌面中最大化显示，并标注了与脚本编辑相关的项目。

> [图 3.3：GMAT 脚本编辑器（GMAT Script Editor）]

- **Scripts Folder（脚本文件夹）**

  GMAT 桌面允许您同时打开多个脚本文件。打开的脚本文件显示在资源树的 Scripts（脚本）文件夹中。双击 Scripts 文件夹中的脚本即可在脚本编辑器中打开它。GMAT 桌面在单独的脚本编辑器中显示每个脚本。GMAT 以粗体名称指示当前在 GUI 中表示的脚本。同一时间只能将一个脚本加载到 GUI 中。

- **Script Status Box（脚本状态框）**

  Script Status（脚本状态）框指示正在编辑的脚本是否已加载到 GUI 中。对于当前在 GUI 中表示的脚本，该框显示 Active Script（活动脚本），其余脚本显示 Inactive Script（非活动脚本）。

- **Save,Sync Button（保存并同步按钮）**

  Save,Sync 按钮将脚本文件的任何更改保存到磁盘，使脚本成为活动脚本，并使 GUI 与脚本同步。

- **Save,Sync,Run Button（保存、同步并运行按钮）**

  Save,Sync,Run 按钮将脚本文件的任何更改保存到磁盘，使脚本成为活动脚本，使 GUI 与脚本同步，并执行该脚本。

- **Save As Button（另存为按钮）**

  当您单击 Save As 时，GMAT 显示 Choose A File（选择文件）对话框，允许您使用新文件名保存脚本。保存后，GMAT 将脚本加载到 GUI 中，使新文件成为活动脚本。

- **Close（关闭）**

  Close 按钮关闭脚本编辑器。

### 图形界面/脚本界面交互与规则（GUI/Script Interface Interactions and Rules）

GMAT 桌面同时支持脚本界面和 GUI 界面，这些界面设计为彼此一致。您可以将脚本和 GUI 视为同一数据的不同"视图"：资源和任务命令序列。GMAT 允许您在视图（脚本和 GUI）之间切换，并同时以可编辑状态打开同一视图。下面我们描述脚本和 GUI 界面的行为、交互和规则，以便您避免混淆和潜在的数据丢失。

#### GUI/脚本交互与同步（GUI/Script Interactions and Synchronization）

GMAT 允许您同时编辑任务的脚本文件表示和 GUI 表示。这些表示可能会产生不一致的更改。位于工具栏中的 GUI/Script Sync Status（GUI/脚本同步状态）窗口指示两种表示的状态。在 Mac 上，状态以缩写形式显示在左侧工具栏中。Synchronized（已同步，绿色）表示脚本和 GUI 包含相同的信息。GUI Modified（GUI 已修改，黄色）表示 GUI 中有尚未保存到脚本的更改。Script Modified（脚本已修改，黄色）表示脚本中有尚未加载到 GUI 的更改。Unsynchronized（未同步，红色）表示脚本和 GUI 中都有更改。

> **注意（Caution）**
>
> GMAT 不会尝试合并或解决脚本和 GUI 中同时发生的更改；如果您在两个界面中都做了更改，必须选择要保存哪一种表示。

工具栏中的 Save（保存）按钮用 GUI 表示覆盖脚本。脚本编辑器上的 Save,Sync（保存并同步）按钮保存脚本表示并将其加载到 GUI 中。

#### GUI 如何映射到脚本（How the GUI Maps to a Script）

单击工具栏中的 Save（保存）按钮会将 GUI 表示保存到脚本文件；这与您在脚本编辑器中编辑的是同一个文件。出现在资源树中的 GUI 项在脚本文件中位于 `BeginMissionSequence` 命令之前，并按预定义的顺序写出。出现在任务树中的 GUI 项在脚本文件中位于 `BeginMissionSequence` 命令之后，顺序与它们在 GUI 中出现的顺序相同。

> **注意（Caution）**
>
> 如果您的脚本文件具有自定义格式（例如间距和数据组织），则应完全在脚本中工作。如果您将脚本加载到 GUI 中，然后单击工具栏中的 Save（保存），您将丢失脚本的格式（但不会丢失数据）。

#### 脚本如何映射到 GUI（How the Script Maps to the GUI）

单击脚本编辑器上的 Save,Sync（保存并同步）按钮会保存脚本表示并将其加载到 GUI 中。当您在 GMAT 脚本中工作时，您是在 GMAT 读写的原始文件中工作。每个脚本文件都必须包含一个名为 `BeginMissionSequence` 的命令。出现在 `BeginMissionSequence` 命令之前的脚本行用于创建和配置模型，这些数据将出现在 GUI 的资源树中。出现在 `BeginMissionSequence` 命令之后的脚本行定义您的任务序列，并出现在 GUI 的任务树中。下面是一个简短的脚本示例：

```
Create Spacecraft Sat
Sat.X = 3000
BeginMissionSequence
Sat.X = 1000
```

说明：`Sat.X = 3000` 行将笛卡尔状态的 x 分量设置为 3000；该值将出现在 Spacecraft（航天器）对话框的 Orbit（轨道）选项卡上。但是，由于 `Sat.X = 1000` 行出现在 `BeginMissionSequence` 命令之后，该行将作为赋值命令出现在 GUI 的任务树中。

#### 基本脚本语法规则（Basic Script Syntax Rules）

- 每个脚本文件必须包含且仅包含一个 `BeginMissionSequence` 命令。
- 在 `BeginMissionSequence` 命令之前不允许使用 GMAT 命令。
- 在脚本文件中，不能在 `BeginMissionSequence` 命令之前使用内联数学语句（方程）。（GMAT 将内联数学语句视为赋值命令。您不能在资源树中使用方程，因此也不能在 `BeginMissionSequence` 命令之前使用方程。）
- 在 GUI 中，您只能在赋值命令中使用内联数学语句。因此，您不能在设置航天器干质量的文本框中输入 `3000 + 4000` 或 `Sat.Y - 8`。
- GMAT 的脚本语言区分大小写。

  有关 GMAT 脚本语言的更完整讨论，请参阅《脚本语言（Script Language）》文档（见 ScriptLanguage.html）。

#### GUI 配置文件（GUI Configuration File）

用户可以通过 MyGmat.ini 文件修改一些 GUI 设置。`MyGMAT.ini` 配置文件位于 ROOT_PATH\data\gui_config 文件夹中，包含若干可配置的键，用于根据用户偏好定制 GMAT 窗口。

- **Open**：Open 键位于 ScriptEditor 节下，告诉 GMAT 在打开应用程序时是否应打开 GMAT 脚本编辑器。默认值为 false。
- **ShowWelcomeOnStart**：ShowWelcomeOnStart 键位于 Main 节下，告诉 GMAT 在打开应用程序时是否应打开欢迎窗口。默认值为 true。也可以通过取消选中欢迎窗口中的 "Show Welcome Page on Startup"（启动时显示欢迎页）复选框来修改。
- **DefaultConsoleHeight**：DefaultConsoleHeight 键位于 ConsoleWindow 节下，告诉 GMAT 打开应用程序时控制台窗口的默认大小。默认值为 100。
- **SetConsoleHeightToPrevious**：SetConsoleHeightToPrevious 键位于 ConsoleWindow 节下，告诉 GMAT 是否应保存上一会话的控制台窗口高度。如果用户在使用 GMAT 时更改了控制台窗口高度，GMAT 下次启动时将打开相同大小的窗口。默认值为 false。
- **PreviousConsoleHeight**：PreviousConsoleHeight 键位于 ConsoleWindow 节下，告诉 GMAT 上一个控制台窗口的高度。GMAT 将在关闭应用程序时为用户更新此值。此键仅在 SetConsoleHeightToPrevious 设置为 true 时使用。
