# 文件接口（FileInterface）

> 译自 GMAT R2026a 帮助文档 FileInterface.html

**FileInterface** —— 数据文件的接口。

## 描述

`FileInterface` 资源是数据文件的接口，可用于加载任务数据，如 `Spacecraft`（航天器）状态信息和物理属性。一旦与文件建立接口，就可以使用 `Set` 命令加载数据并将其应用到目标。

目前支持以下文件格式：

- `TVHF_ASCII`：TCOPS 向量保持文件（TVHF）的 ASCII 格式，由 NASA 戈达德航天中心飞行动力学设施定义。该文件包含可传输到 `Spacecraft` 资源的航天器状态和物理信息。

**另请参阅**：`Set`

## 字段

| 字段 | 描述 |
| --- | --- |
| `Filename` | 要读取文件的完整路径。相对路径相对于包含 GMAT 可执行文件的目录解释。如果省略路径，则假定为 "`./`"。**数据类型**：字符串；**允许值**：有效文件路径；**访问**：set；**默认值**：（无）；**单位**：N/A；**接口**：GUI、脚本 |
| `Format` | 要读取文件的格式。目前唯一允许的格式是 "`TVHF_ASCII`"。**数据类型**：枚举值；**允许值**：`TVHF_ASCII`；**访问**：set；**默认值**：`TVHF_ASCII`；**单位**：N/A；**接口**：GUI、脚本 |

## GUI

> [图：FileInterface 资源 GUI]

`FileInterface` GUI 有两个字段：`Format` 的可选选项列表（目前只有 `TVHF_ASCII`），以及 `Filename` 的输入框。点击 `Filename` 框右侧的 **Browse（浏览）** 可交互式地选择文件。

## 备注

`FileInterface` 资源支持的每种文件格式都暴露一组关键字，可用于提取特定数据元素。这些关键字可用在 `Set` 命令的 `Data` 选项中，用法如下：

```
Set <目标> <来源> (Data = {关键字[, 关键字]})
```

如果使用 `'All'` 关键字，则选中 "All" 列中带勾选的字段。

### TVHF_ASCII

| 关键字 | 源字段 | 描述 | 'All' |
| --- | --- | --- | --- |
| `CartesianState` | "CARTESIAN COORDINATES" | 笛卡尔状态元素（`X`、`Y`、`Z`、`VX`、`VY`、`VZ`） | ✓ |
| `Cr` | "CSUBR" | 反射系数 | ✓ |
| `Epoch` | "EPOCH TIME FOR ELEMENTS" | 状态向量历元 | ✓ |

#### 限制

以下限制适用于 `TVHF_ASCII` 格式：

- 仅支持 J2000 坐标系。
- 多记录文件中只加载第一条记录。

## 示例

读取 TVHF 文件并用它配置航天器：

```
Create Spacecraft aSat
Create FileInterface tvhf
tvhf.Filename = 'statevec.txt'
tvhf.Format = 'TVHF_ASCII'

BeginMissionSequence

Set aSat tvhf
```

说明：创建文件接口指向 statevec.txt，在任务序列中用 `Set` 命令把文件中的状态数据加载到航天器 aSat。