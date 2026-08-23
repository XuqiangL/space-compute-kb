# 设置命令（Set）
> 译自 GMAT R2026a 帮助文档 Set.html

Set —— 从数据接口配置资源。

## 脚本语法

```
Set destination source (options)
```

## 描述

`Set` 命令按照 `options` 从 `source` 检索数据并填充 `destination`。时间系统、时间格式、状态类型和坐标系会自动转换为 `destination` 所要求的形式。

**另请参见**：FileInterface、Spacecraft

## 选项

| 选项 | 描述 |
|------|------|
| `destination` | 要从数据源填充的资源。<br>接受的数据类型：`Spacecraft`<br>允许的值：任何 `Spacecraft` 资源<br>默认值：（无）<br>是否必需：是<br>接口：GUI、脚本 |
| `source` | 从中获取数据的数据源。<br>接受的数据类型：`FileInterface`<br>允许的值：任何 `FileInterface` 资源<br>默认值：（无）<br>是否必需：是<br>接口：GUI、脚本 |
| `options` | 特定于所选 `source` 的选项。详见下文各节。 |

当 `source` 是 `FileInterface` 且 `Format` 为 "`TVHF_ASCII`" 时，可使用以下选项：

- `Data={keyword[, keyword, ...]}`：要从文件中检索的值的逗号分隔列表。默认为 `'All'`，即检索所有可用元素。可用的关键字记录在 `FileInterface` 参考文档的 "TVHF_ASCII" 一节中。

## GUI

> [图：Set 命令的 GUI 面板]

`Set` 的 GUI 是一个非常简单的文本框，允许你直接输入命令。默认情况下它没有参数，因此你必须自己补全命令。

## 示例

读取一个 TVHF 文件并用它配置航天器：

```
Create Spacecraft aSat
Create FileInterface tvhf
tvhf.Filename = 'statevec.txt'
tvhf.Format = 'TVHF_ASCII'

BeginMissionSequence

Set aSat tvhf
```

说明：创建 FileInterface 资源 tvhf 指向 TVHF_ASCII 格式的状态矢量文件 statevec.txt；`Set aSat tvhf` 读取文件中的全部数据并配置 aSat，时间系统、状态类型和坐标系会自动转换。

读取一个 TVHF 文件并只用它设置历元和笛卡尔状态：

```
Create Spacecraft aSat
Create FileInterface tvhf
tvhf.Filename = 'statevec.txt'
tvhf.Format = 'TVHF_ASCII'

BeginMissionSequence

Set aSat tvhf (Data = {'Epoch', 'CartesianState'})
```

说明：与上例类似，但通过 `Data` 选项只从文件中提取历元（Epoch）和笛卡尔状态（CartesianState）两项来配置航天器，其余数据忽略。
