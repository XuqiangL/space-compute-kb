# 命令行用法（Command-Line Usage）
> 译自 GMAT R2026a 帮助文档 CommandLine.html

命令行用法——从命令行启动 `GMAT` 应用程序。

## 语法（Synopsis）

```
GMAT [option...] [script_file]
GMATConsole [option...] [script_file]
```

说明：以上两条命令分别为图形界面版与控制台版的启动形式；`option` 为可选参数，`script_file` 为可选的脚本文件路径。

## 描述（Description）

`GMAT` 命令启动 GMAT 图形界面。如果不带参数运行，GMAT 启动时加载默认任务。如果指定了 `script_file`，且它是 GMAT 脚本的有效路径，GMAT 会加载该脚本并保持打开状态，但不运行它。`GMATConsole` 命令启动 GMAT 控制台界面。各界面支持的选项见下文。

## 选项（Options）

| 选项 | 说明 |
|------|------|
| `-b`，`--batch` | 运行在指定文件中列出的多个脚本。 |
| `-h`，`--help` | 启动 GMAT 并显示命令行用法信息：GUI 版本显示在消息窗口中，控制台界面显示在终端中。 |
| `-l <filename>`，`--logfile <filename>` | 指定日志文件（在控制台交互模式下被忽略）。 |
| `-m`，`--minimize` | 以最小化界面启动 GMAT。 |
| `-ns`，`--no_splash` | 启动 GMAT 时不显示启动画面（splash screen）。 |
| `-r <filename>`，`--run <filename>` | 加载后自动运行指定的脚本。 |
| `--save <filename>` | 保存当前脚本（仅交互模式）。 |
| `--start-server` | 启动时开启 GMAT Server（控制台版忽略）。 |
| `-s <filename>`，`--startup_file <filename>` | 指定启动文件（Startup File）（在控制台交互模式下被忽略）。 |
| `--summary` | 写出命令摘要（仅交互模式）。 |
| `--verbose` | 运行期间将信息消息输出到屏幕（默认为开）。 |
| `-v`，`--version` | 启动 GMAT 并在消息窗口中显示版本信息。 |
| `-x`，`--exit` | 运行指定脚本后退出 GMAT。如果仅与脚本名一起指定（即不带 --run 选项），GMAT 只是打开然后关闭。 |

## 优先级规则（Precedence Rules）

某些文件位置（例如日志文件）可以在多个位置设置。优先级规则如下：命令行设置具有最高优先级，一旦设置就总是使用这些值。第二优先级为脚本级设置，例如 `GmatGlobal.LogFile = C:\myLog.txt`。最后，如果以上方法都未设置，则使用启动文件（Startup File）中的值。

当启动文件配置为使用 `RUN_MODE = TESTING` 时，还有额外的优先级规则。在这种情况下，启动文件中的日志文件名具有优先级；输出路径可被图形界面 File（文件）菜单中的 `Set File Paths`（设置文件路径）选项，或资源树（Resource Tree）中 Scripts（脚本）菜单里的 `Run Scripts`（运行脚本）选项中的设置覆盖。

## 示例（Examples）

启动 GMAT 并运行脚本 `MyScript.script`：

```
GMAT MyScript.script
```

说明：将脚本文件名作为唯一参数传入时，GMAT 加载该脚本并保持打开。

以最小化界面运行脚本，随后退出：

```
GMAT --minimize --exit MyScript.script
```

说明：`--minimize` 使界面最小化运行，`--exit` 使 GMAT 在脚本运行结束后自动退出。
