# MATLAB 接口（MatlabInterface）
> 译自 GMAT R2026a 帮助文档 MatlabInterface.html

MATLAB Interface —— 与 MATLAB 系统的接口。

## 描述

MATLAB 接口提供到 Mathworks MATLAB 环境的链接，允许 GMAT 像运行 GMAT 脚本语言的原生函数一样运行 MATLAB 函数。

该接口不能通过脚本语言直接控制，但可以在 GMAT GUI 中控制。GMAT 会在调用 MATLAB 函数时自动启动该接口。

GMAT 有两个组件提供对该接口的用户访问。关于声明 MATLAB 函数的详细信息，请参见 `MatlabFunction` 参考文档。关于调用函数和传递数据的详细信息，请参见 `CallMatlabFunction` 参考文档。

**另请参见**：CallMatlabFunction、MatlabFunction

## GUI

> [图：资源树中 Interfaces 文件夹下的 MATLAB 接口图标]

MATLAB 接口在资源树的 `Interfaces`（接口）文件夹中提供一个图标，可用于控制该接口。右键点击该图标会显示两个选项：`Open`（打开）和 `Close`（关闭）。

`Open` 菜单项使 GMAT 打开到 MATLAB 引擎的连接，这会在后台显示一个 MATLAB 命令窗口。此后，GMAT 与 MATLAB 之间的所有通信都使用该连接，直到连接关闭。同一时间只能打开一个连接。

`Close` 菜单项使 GMAT 关闭任何已打开的到 MATLAB 引擎的连接。如果没有打开的连接，它没有任何效果。

## 备注

### 接口设置

GMAT 要成功发起与 MATLAB 的通信，必须满足以下条件。所有条件必须对同一个 MATLAB 实例同时成立：

- 在运行 GMAT 的同一台机器上安装兼容的、已授权的 MATLAB 版本。GMAT 在发布时会用当时的最新版 MATLAB 进行测试，已知 R2006b 及更新版本可以工作。
- GMAT 与所安装 MATLAB 的体系结构（32 位或 64 位）必须匹配。例如，32 位版本的 GMAT 只与 32 位版本的 MATLAB 兼容。
- 在 Windows 上：
  1. 把以下路径（其中 *MATLAB* 是 MATLAB 安装版本的路径）添加到你的 `Path` 环境变量（用户变量或系统变量均可）：*MATLAB*\bin\win32（64 位版本的 GMAT 对应 `win64`）。如果仍有问题，尝试把该路径放到系统路径的最开头。
  2. 通过运行以下命令把 MATLAB 注册为 COM 服务器：**matlab -regserver**。MATLAB 安装程序会自动完成此操作。若要手动执行，请以管理员权限打开命令窗口并运行上述命令。确保在包含你希望使用的可执行文件的文件夹中运行该命令（即 *MATLAB*\bin\win32 或 *MATLAB*\bin\win64）。
- 在 macOS 上：
  1. 打开 bin 目录中的 MacConfigure.txt，编辑 MATLAB_APP_PATH 字段，使其指向你的 MATLAB 应用程序包的位置。
  2. 如果 MATLAB 接口在 GmatConsole 命令行应用程序下不工作，你可能需要配置终端，使系统能够加载 MATLAB 库并启动 MATLAB。例如，如果你使用 .bashrc，可能需要添加类似如下的内容：

     **export MATLAB = \<path/to/MATLAB/app/location/\>**

     **export DYLD_LIBRARY_PATH=$MATLAB/bin/maci64:$DYLD_LIBRARY_PATH**

     **export PATH=$PATH:$MATLAB/bin**

  > **注意**：R2010a 之后的 MATLAB 版本必须使用 64 位 GMAT 才能与之接口。
- 在 Linux 上：
  - Linux 上的 MATLAB 接口要求安装 C shell（csh）。这是 MathWorks 对启动 MATLAB 引擎（该接口使用）的要求。如果你的系统没有安装 csh，你的 Linux 发行版的包管理器应提供 csh 安装选项。
  - MATLAB 接口需要能够找到 MATLAB 共享库 libeng.so（及相关库）和 libMatlabEngine.so。对于 MATLAB R2019a，前者位于 MATLAB 的 bin/glnxa64 文件夹，后者位于 MATLAB 的 extern/bin/glnxa64 文件夹。启动 GMAT 并应用库路径设置的一种方法是带库路径启动应用程序。在 Linux 终端中，命令（以 MATLAB 安装在默认 /usr/local/MATLAB/R2019a 文件夹为例）：

    **LD_LIBRARY_PATH=/usr/local/MATLAB/R2019a/extern/bin/glnxa64:/usr/local/MATLAB/R2019a/bin/glnxa64 ./GMAT**

    即可完成此任务，以运行 MATLAB 接口所需的设置启动 GMAT GUI。

> **注意**：Windows 上的常见故障排除提示：
>
> - 如果你使用的是官方发布的 32 位版本 GMAT，请确保安装了 32 位版本的 MATLAB。
> - 如果上述路径已存在于你的系统 `Path` 变量中，请尝试把它放到路径的最前面。
> - 请确保 `Path` 变量中引用的 MATLAB 实例与运行 **matlab -regserver** 时使用的是同一个实例。

### MATLAB 引擎连接

> **警告**：注意：GMAT 在运行完成后不会关闭它创建的 MATLAB 命令窗口。这允许手动检查 MATLAB 工作区，但如果在同一窗口中修改并重新运行 MATLAB 函数或路径，可能导致令人困惑的行为。
>
> 如果你正在频繁编辑脚本，我们建议在每次运行之间，右键点击资源树中的 Matlab 并点击 Close 来关闭 MATLAB 命令窗口。

当 GMAT 运行包含 MATLAB 函数调用的任务时，它会在发起函数调用之前打开到 MATLAB 引擎的连接，然后在 GMAT 会话的剩余时间内复用该连接。

MATLAB 引擎可以通过右键点击资源树中的 `Matlab` 项并选择 `Open` 和 `Close` 选项来手动控制。

## 示例

常见示例请参见 `MatlabFunction` 参考文档。
