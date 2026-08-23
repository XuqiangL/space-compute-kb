# 入门（Getting Started）
> 译自 GMAT R2026a 帮助文档 GettingStarted.html

**第 2 章（Chapter 2）**

## 本章目录

- 安装（Installation）
- [运行 GMAT（Running GMAT）](RunningGmat.md)
  - 启动 GMAT（Starting GMAT）
  - 退出 GMAT（Exiting GMAT）
- [示例任务（Sample Missions）](SampleMissions.md)
- [获取帮助（Getting Help）](GettingHelp.md)

## 安装（Installation）

应用程序包可在 GMAT 的 SourceForge 项目页面获取，地址为 `https://sourceforge.net/projects/gmat`。

主要平台提供以下软件包：

| 操作系统（Operating System） | 二进制包（Binary bundle） | 源代码（Source code） |
|:---:|:---:|:---:|
| Windows | ✔ | ✔ |
| macOS | ✔ | ✔ |
| Linux | ✔ | ✔ |

### 二进制包（Binary Bundle）

Windows 上的二进制包以 `.zip` 压缩包形式提供。使用时，将其解压到文件系统中的任意位置，并确保保持文件夹结构完整。要运行 GMAT，运行解压文件夹中的 `bin\GMAT.exe` 可执行文件。

macOS 二进制包以经过公证（notarized）的 DMG 文件形式提供。使用时，打开 DMG，将"GMAT R2026a"文件夹拖到全局 Applications 文件夹（需要管理员权限）或您用户账户的 Applications 文件夹。要运行生产级质量的 GMAT 控制台应用程序，打开终端，切换到 GMAT 的 `bin/` 文件夹，运行 `GmatConsole` 应用程序。要运行 Beta 级 GMAT 图形界面，运行 `bin/` 文件夹中的 `GMAT-R2026a_Beta.app` 应用程序。

GMAT 的 Linux 版本以压缩 tarball 打包。下载 Red Hat 或 Ubuntu 的 tarball，将内容解压到方便的位置（保持文件系统结构），GMAT 即可使用。要运行生产级质量的控制台应用程序，打开终端，切换到发行版的 `bin/` 文件夹，运行 `GmatConsole` 应用程序。Beta 质量的 GMAT 图形界面 `GMAT_Beta` 也可从该文件夹运行。（注意，GMAT 的 Linux 版本遵循 Linux 惯例，将支持库放在与 bin 文件夹平行的 lib 文件夹中。您可能需要在启动过程中通过设置 LD_LIBRARY_PATH 来加载该文件夹。）

### 源代码（Source Code）

GMAT 以平台无关的源代码包形式提供。编译说明请参阅 [GMAT Wiki](http://gmatcentral.org)。

GMAT 代码的发行快照可从 SourceForge 的 Git 仓库获取：

`https://git.code.sf.net/p/gmat/git`

仓库中为每个发行版提供了标签（tag）。
