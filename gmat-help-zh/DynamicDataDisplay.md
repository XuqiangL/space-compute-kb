# 动态数据显示（DynamicDataDisplay）

> 译自 GMAT R2026a 帮助文档 DynamicDataDisplay.html

**DynamicDataDisplay** —— 用户自定义资源，与 `UpdateDynamicData` 命令配合使用，把参数的当前值打印到 GUI 上的表格中。

## 描述

`DynamicDataDisplay` 是一种资源，它生成由用户选定参数组成的表格，并在使用 `UpdateDynamicData` 命令的任务序列中更新。该显示的目的是让用户可以选择在任务执行过程中直接看到数据发生的变化。

使用该资源时的各种选项包括：设置参数的文字颜色、设置数据单元格的背景颜色、设置警告条件边界和设置临界条件边界。该资源最常用于循环序列中，例如 for 循环、优化、目标定位等。

**另请参阅**：`UpdateDynamicData`

## 字段

| 字段 | 描述 |
| --- | --- |
| `AddParameters` | 设置所需行参数的字段。该数组的第一个条目必须是所需的行号。例如：`MyDynamicDataDisplay.AddParameters = {1, Sat.X, Array(2, 1)};`。**数据类型**：引用数组；**允许值**：任何变量、数组元素、字符串或对象参数（不能使用整个数组）；**访问**：set；**默认值**：2x2 空表；**单位**：N/A；**接口**：GUI、脚本 |
| `BackgroundColor` | 设置显示所选参数值的单元格背景颜色的字段。该数组的第一个条目必须是要更改背景色的参数，后跟所需颜色，即 `MyDynamicDataDisplay.BackgroundColor = {ParamName, Color}`。**数据类型**：字符串数组；**允许值**：DynamicDataDisplay 对象中的任何参数名，以及 GUI 文本颜色选择器中可用的任何颜色、有效的预定义颜色名或 0 到 255 之间的 RGB 三元组值；**访问**：set；**默认值**：White；**单位**：N/A；**接口**：GUI、脚本 |
| `CritBounds` | 设置参数临界边界的字段。超出这些边界会把参数值的文字变为设定的临界颜色。第一个条目是应用这些边界的参数，第二个是实数数组，即 `MyDynamicDataDisplay.CritBounds = {ParamName, [LowerBound UpperBound]}`。**数据类型**：字符串数组；**允许值**：任意实数；**访问**：set；**默认值**：[-9.999e300, 9.999e300]；**单位**：N/A；**接口**：GUI、脚本 |
| `CritColor` | 设置参数值一旦超出所定义临界边界后文字将变为的颜色的字段。**数据类型**：整数数组或字符串；**允许值**：GUI 文本颜色选择器中可用的任何颜色、有效的预定义颜色名或 0 到 255 之间的 RGB 三元组值；**访问**：set；**默认值**：Red；**单位**：N/A；**接口**：GUI、脚本 |
| `Maximized` | 允许用户最大化 `DynamicDataDisplay` 窗口。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：true、false；**访问**：set；**默认值**：false；**单位**：N/A；**接口**：脚本 |
| `RelativeZOrder` | 允许用户选择哪个 `DynamicDataDisplay` 最先显示在屏幕上。`RelativeZOrder` 值最低的最后显示，值最高的最先显示。该字段不能在任务序列中修改。**数据类型**：整数；**允许值**：整数 ≥ 0；**访问**：set；**默认值**：0；**单位**：N/A；**接口**：脚本 |
| `RowTextColors` | 设置显示参数值文字颜色的字段。该数组的第一个条目必须是以字符串形式输入的所需行号，即 `MyDynamicDataDisplay.RowTextColors = {RowNum, Color1, Color2, ...};`。颜色数量不能超过所选行中的参数数量。**数据类型**：字符串数组；**允许值**：DynamicDataDisplay 对象包含的任何行号，以及 GUI 文本颜色选择器中可用的任何颜色、有效的预定义颜色名或 0 到 255 之间的 RGB 三元组值；**访问**：set；**默认值**：Black；**单位**：N/A；**接口**：GUI、脚本 |
| `Size` | 允许用户控制所生成 DynamicDataDisplay 的显示尺寸。[0 0] 矩阵中第一个值控制水平尺寸，第二个值控制垂直尺寸。该字段不能在任务序列中修改。**数据类型**：实数数组；**允许值**：任意实数；**访问**：set；**默认值**：[ 0 0 ]；**单位**：N/A；**接口**：脚本 |
| `TextColor` | 设置显示所选参数值文字颜色的字段。该数组的第一个条目必须是要更改文字颜色的参数，后跟所需颜色，即 `MyDynamicDataDisplay.TextColor = {ParamName, Color}`。**数据类型**：字符串数组；**允许值**：DynamicDataDisplay 对象中的任何参数名，以及 GUI 文本颜色选择器中可用的任何颜色、有效的预定义颜色名或 0 到 255 之间的 RGB 三元组值；**访问**：set；**默认值**：Black；**单位**：N/A；**接口**：脚本 |
| `UpperLeft` | 允许用户沿任意方向平移所生成的显示窗口。[0 0] 矩阵中第一个值水平平移 DynamicDataDisplay，第二个值垂直平移窗口。该字段不能在任务序列中修改。**数据类型**：实数数组；**允许值**：任意实数；**访问**：set；**默认值**：[ 0 0 ]；**单位**：N/A；**接口**：脚本 |
| `WarnBounds` | 设置参数警告边界的字段。超出这些边界会把参数值的文字变为设定的警告颜色。第一个条目是应用这些边界的参数，第二个是实数数组，即 `MyDynamicDataDisplay.WarnBounds = {ParamName, [LowerBound UpperBound]}`。**数据类型**：字符串数组；**允许值**：DynamicDataDisplay 对象中的任何参数名和任意实数；**访问**：set；**默认值**：[-9.999e300, 9.999e300]；**单位**：N/A；**接口**：GUI、脚本 |
| `WarnColor` | 设置参数值一旦超出所定义警告边界后文字将变为的颜色的字段。**数据类型**：整数数组或字符串；**允许值**：GUI 文本颜色选择器中可用的任何颜色、有效的预定义颜色名或 0 到 255 之间的 RGB 三元组值；**访问**：set；**默认值**：GoldenRod；**单位**：N/A；**接口**：GUI、脚本 |

## GUI

下图显示 `DynamicDataDisplay` 资源的默认名称和设置：

> [图：DynamicDataDisplay 资源 GUI 设置面板]

下图显示要在 `DynamicDataDisplay` 资源中显示的参数的默认名称和设置：

> [图：DynamicDataDisplay 参数设置对话框]

设置面板中的网格表示当前已添加到该 `DynamicDataDisplay` 的参数。要更改网格尺寸，在 "Row"（行）和 "Column"（列）文本框中输入整数并点击 "Update"（更新）。在某个网格单元格上双击鼠标左键，会打开一个对话框，其中包含将放入所选单元格的参数的所有选项。"Select"（选择）按钮会把用户带到参数选择窗口以选择所需参数；选择后，用户还可以按需更改该参数的选项。点击 "Ok" 后，所选参数的名称会出现在初始面板上所选的单元格中。要从网格中移除不需要的参数，选中一个单元格并按 Delete 键。这会移除该参数，并把该单元格的所有其他设置恢复为默认值。

## 备注

### 各种输入下显示的行为

如果用户在脚本中跳过一行或多行（例如只在第 1 行和第 4 行放置参数），那么中间的行在 GUI 中只显示为空白单元格。构建表格时，每行的列数会与参数最多的行保持一致。例如，如果第 1 行有 5 个参数而第 2 行只有 3 个，第 2 行多出的两列仍会出现，只是留空。用户也可以通过用引号添加空字符串，或在使用设置面板时把网格中的格子留空，在网格中插入自己的空白字段。

### 警告和临界条件的行为

临界条件会覆盖警告条件，即：如果某参数当前显示警告颜色，随后超出临界边界，文字颜色将变为临界颜色。如果参数回到临界或警告边界之内，临界或警告颜色会分别移除。如果用户为某参数指定了黑色以外的文字颜色，那么即使边界被违反，警告和临界边界颜色也不会应用。

## 示例

创建一个名为 myDisplay 的 `DynamicDataDisplay` 资源，包含两行、用户设置的文字颜色，并在 mySC.X 上设置条件边界：

```
Create Spacecraft mySC;
Create DynamicDataDisplay myDisplay
myDisplay.AddParameters   = {1, mySC.X, mySC.Y};
myDisplay.AddParameters   = {2, '', mySC.Z};
myDisplay.RowTextColors   = {1, Red, Black};
myDisplay.TextColor       = {mySC.Z, [200 0 200]};
myDisplay.BackgroundColor = {mySC.Y, Blue};
myDisplay.WarnBounds      = {mySC.X, [-1000 1000]};
myDisplay.CritBounds      = {mySC.X, [-3000 3000]};
myDisplay.WarnColor       = Orange;
myDisplay.CritColor       = [200 150 0];
```

说明：第 1 行显示 X、Y，第 2 行显示空白与 Z；为各行和各参数设置文字/背景颜色，并为 X 配置警告与临界边界及对应颜色。

将 `DynamicDataDisplay` 与 `UpdateDynamicData` 命令配合使用：

```
Create Spacecraft mySC;
Create Propagator myProp;

Create DynamicDataDisplay myDisplay;
myDisplay.AddParameters = {1, mySC.EarthMJ2000Eq.X};

BeginMissionSequence
Propagate myProp(mySC) {mySC.ElapsedSec = 12000.0};
UpdateDynamicData myDisplay;
```

说明：传播 12000 秒后，用 `UpdateDynamicData` 刷新表格中显示的 X 坐标值。