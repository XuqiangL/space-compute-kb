# 字符串资源（String）
> 译自 GMAT R2026a 帮助文档 String.html

String —— 用户定义的字符串变量。

## 描述

`String` 资源用于存储一个字符串值，供任务序列中的命令使用。

在脚本环境中，`String` 资源在创建时被初始化为字符串 `'STRING_PARAMETER_UNDEFINED'`。在 GUI 环境中，它们被初始化为空字符串（`''`）。String 资源可以使用字符串字面量赋值，也可以（在任务序列中）使用其他 `String` 资源、数值型 `Variable` 资源或字符串类型的资源参数赋值。

**另请参见**：Array、Variable

## 字段

`String` 资源没有字段；取而代之的是直接给资源本身设置所需的值。

| 字段 | 描述 |
|------|------|
| *value* | 字符串变量的值。<br>数据类型：字符串<br>允许的值：N/A<br>访问方式：set、get<br>默认值：`''`（空）（GUI）；`'STRING_PARAMETER_UNDEFINED'`（脚本）<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

> [图：String 资源的创建窗口]

GMAT GUI 允许你在不离开窗口的情况下一次创建多个 `String` 资源。创建 `String` 的步骤：

1. 在 **String Name** 框中输入所需的字符串名称。
2. 在 **String Value** 框中输入字符串的初始值。此项为必填，且必须是字面字符串值。设置该值时不需要引号。
3. 单击 **=>** 按钮创建该字符串并将其添加到右侧列表中。

你可以用这种方式创建多个 `String` 资源。要在此窗口中编辑已有字符串，在右侧列表中单击它并编辑其值。必须再次单击 **=>** 按钮才能保存更改。

> [图：String 资源的属性编辑窗口]

你也可以在主 GMAT 窗口的资源树中双击已有的 `String`。这会打开上面的字符串属性框，允许你编辑该单个字符串的值。

## 备注

`String` 资源可以（在任务序列中）使用数值型 `Variable` 资源来设置。赋值时，`Variable` 的数值会被转换为字符串。数值将以浮点或科学记数法（取更合适者）转换为字符串表示，最多保留 16 位有效数字。

## 示例

创建一个字符串并赋予字面值：

```
Create ReportFile aReport

Create String aStr
aStr = 'MyString'

BeginMissionSequence

Report aReport aStr
```

说明：创建报告文件和字符串资源 aStr，赋字面值 'MyString'，然后在任务序列中把 aStr 写入报告文件。
