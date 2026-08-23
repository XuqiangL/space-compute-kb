# Python 接口（PythonInterface）
> 译自 GMAT R2026a 帮助文档 PythonInterface.html

Python Interface —— 与 Python 编程语言的接口。

## 描述

Python 接口提供到 Python 编程语言的链接，允许 GMAT 像运行 GMAT 脚本语言的原生函数一样运行 Python 函数。

该接口没有任何可以通过 GMAT 脚本语言直接控制的参数。GMAT 会在调用 Python 函数时自动启动 Python 接口。

Python 接口通过 GMAT 的 CallPythonFunction 命令访问。关于调用函数和传递数据的详细信息，请参见 `CallPythonFunction` 参考文档。

**另请参见**：CallPythonFunction

## GUI

GMAT 中的 Python 接口由内部启动和驱动。用户无法从 GMAT 图形用户界面直接访问该接口。

## 备注

### 接口设置

GMAT 要成功调用兼容的 Python 实例，必须同时满足以下条件：

- GMAT 启动文件必须指定与所安装 Python 版本匹配的 Python 接口版本（见下方的兼容性表）。同一时间只能加载一个版本的 Python 接口。注意，未经测试的 Python 接口版本仅为方便起见而提供。

  | Python 版本 | Python 接口插件 | 状态 |
  |-------------|-----------------|------|
  | 3.9（64 位） | libPythonInterface_py39 | 已测试 |
  | 3.10（64 位） | libPythonInterface_py310 | 已测试 |
  | 3.11（64 位） | libPythonInterface_py311 | 已测试 |
  | 3.12（64 位） | libPythonInterface_py312 | 已测试 |
  | 3.13（64 位） | libPythonInterface_py313 | 轻度测试 |
  | 3.14（64 位） | libPythonInterface_py314 | 轻度测试 |

- GMAT 不支持 32 位 Python。
- Python 接口访问用户机器上的 Python 模块。此功能（包括 Python 使用的路径信息）按操作系统分别配置，如下所示。
- 在 Windows 上：
  - 以下路径条目（其中 *Python* 是所安装 Python 版本的完整路径）必须存在于 `Path` 环境变量中：

    *Python*

    *Python*\Scripts

  - 以下路径（其中 *Python* 是所安装 Python 版本的路径）必须存在于 `PYTHONPATH` 环境变量中：

    *Python*\Lib\site-packages

  - `PYTHONHOME` 环境变量必须设置为包含 python3*X*.dll 的目录，其中 *3X* 表示 Python 版本，例如 **python39.dll**。该目录通常是你的 Python 安装或 Anaconda 环境的根目录。

  如果你使用 Anaconda Python，这些路径可以设置为指向你希望 GMAT 使用的 Anaconda 环境内的目录。
- 在 macOS 上：
  - 在 macOS 上，Python 接口只与 Python.org 发行的 Python 版本配合工作。这些安装必须位于以下特定目录（Python.org 的默认位置）：`/Library/Frameworks/Python.framework/Versions/3.X`
  - Python 接口尚未在 macOS 上用 Anaconda Python 测试过。
  - 以下条目（其中 *Python* 是所安装 Python 3.X 的完整路径）必须存在于 GMAT 启动文件中。这允许 Python 接口访问 Numpy 等 Python 包：

    `PYTHON_MODULE_PATH = `*Python*`/lib/python3.X/site-packages`

    注意，启动文件中允许多个 `PYTHON_MODULE_PATH` 条目，它们可以放在文件中的任何位置。
  - Mac 平台不支持 Python 3.6 和 3.7 版本。
- 在 Linux 上：
  - GMAT 构建中使用的 Python 版本通常使用从终端访问的默认 Python 包（例如 Python 3.12）。
  - 启用 MATLAB 接口的用户可能会发现 Python 接口因库冲突而无法加载。如果 Python 接口报告问题 **undefined symbol: XML_SetHashSalt**，说明 MATLAB 自带的 expat 库与该发行版 Python 3 安装所需的库之间存在冲突。此问题可以通过在 GMAT 启动前用 LD_PRELOAD 命令加载系统 expat 库来纠正。命令 **LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libexpat.so ./GMAT** 会先加载 expat 库再启动 GMAT，从而解决 Ubuntu 22.04 等系统上的该问题。

> **注意**：Windows 上的常见故障排除提示：
>
> - GMAT 是 64 位应用程序。请确保安装了 64 位版本的 Python。
> - 如果上述路径已存在于你的系统 `Path` 变量中，请尝试把它放到路径说明的最前面。

### Python 引擎连接

> **警告**：GMAT 在运行完成后不会关闭 Python 接口。这一特性避免了在一次运行中重复加载某些 Python 模块时可能出现的异常行为，但如果在同一 GMAT 会话中修改并重新运行 Python 文件，可能导致令人困惑的行为。
>
> 我们建议在编辑 Python 函数后重启 GMAT，以保证重新运行脚本时你的修改生效。

当 GMAT 运行包含 Python 函数调用的任务时，它会在发起函数调用之前把 Python 作为嵌入式系统加载到 GMAT 的内存中，然后在 GMAT 会话的剩余时间内复用该系统。

## 示例

常见示例请参见 `CallPythonFunction` 参考文档。
