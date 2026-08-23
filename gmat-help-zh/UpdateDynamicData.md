# 更新动态数据命令（UpdateDynamicData）
> 译自 GMAT R2026a 帮助文档 UpdateDynamicData.html

UpdateDynamicData —— 与 `DynamicDataDisplay` 配合使用的命令，用于更新 GUI 显示表格中正在显示的数据。

## 描述

`UpdateDynamicData` 命令用于指定在任务序列中的何处让 `DynamicDataDisplay` 将其数据更新为当前值。这允许用户控制在任务序列的哪些点上看到新数据。用户还可以指定只更新 `DynamicDataDisplay` 中的某些数据，而不是整个表格。该命令可以放在任务序列中的任何所需位置，并且可以对同一个 `DynamicDataDisplay` 使用多次。

**另请参见**：DynamicDataDisplay

## 字段

| 字段 | 描述 |
|------|------|
| `DynamicTableName` | 设置本命令将更新哪个 DynamicDataDisplay 对象的字段。<br>数据类型：字符串<br>允许的值：任何 DynamicDataTable 对象<br>访问方式：set<br>默认值：N/A<br>单位：N/A<br>接口：GUI、脚本 |
| `DataList` | 设置在所选表格中更新哪些参数的字段，其余数据保持不变。<br>数据类型：任何参数<br>允许的值：当前所选 DynamicDataDisplay 中的任何参数<br>访问方式：set<br>默认值：N/A<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

下图展示了使用基本命令 GUI 面板的 `UpdateDynamicData`：

> [图：UpdateDynamicData 命令的 GUI 面板]

## 示例

创建一个 `DynamicDataDisplay`，并在任务序列中使用 `UpdateDynamicData` 命令更新该显示：

```
Create Spacecraft DefaultSC;
Create Propagator DefaultProp;

Create DynamicDataDisplay myDisplay;
DynamicDataDisplay.AddParameters(1, DefaultSC.X, DefaultSC.Y);

BeginMissionSequence
Propagate DefaultProp(DefaultSC) (DefaultSC.ElapsedSecs = 12000.0);
UpdateDynamicData myDisplay;
Propagate DefaultProp(DefaultSC) (DefaultSC.ElapsedSecs = 24000.0);
UpdateDynamicData myDisplay DefaultSC.X;
```

说明：创建动态数据显示表 myDisplay 并加入 DefaultSC 的 X、Y 两个参数。传播 12000 秒后执行 `UpdateDynamicData myDisplay`，把整张表刷新为当前值；再传播 24000 秒后执行 `UpdateDynamicData myDisplay DefaultSC.X`，只更新表中的 DefaultSC.X 一项，其余数据保持不变。
