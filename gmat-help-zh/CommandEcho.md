# 命令回显开关（CommandEcho）
> 译自 GMAT R2026a 帮助文档 CommandEcho.html

CommandEcho —— 切换 `Echo` 命令的使用。

## 脚本语法

```
CommandEcho EchoSetting
```

## 描述

`EchoCommand` 命令用于在整个任务序列中打开或关闭 `Echo` 的使用。这允许把任务序列的特定部分显示到消息窗口和生成的日志文件中。该命令是 `ScriptTools` 插件的一部分。

## 选项

| 选项 | 描述 |
|------|------|
| `EchoSetting` | 指定 `Echo` 命令当前的 `EchoSetting` 应为开还是关。<br>接受的数据类型：字符串<br>允许的值：On、Off<br>默认值：Off<br>是否必需：是<br>接口：GUI、脚本 |

## GUI

`CommandEcho` 命令可在任务序列的任何位置打开或关闭 `Echo`。任务序列中可以放置任意数量的该命令。通过 GUI 设置 `EchoSetting` 时会出现下图所示的消息框。要打开该命令，只需把文本中的 Off 替换为 On。注意，如果该命令被重命名，新名称会以引号包围的形式显示在此 GUI 界面中。

> [图：CommandEcho 命令的 GUI 消息框，文本为 CommandEcho Off]
