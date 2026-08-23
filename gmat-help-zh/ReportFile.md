# 报告文件资源（ReportFile）
> 译自 GMAT R2026a 帮助文档 ReportFile.html

ReportFile —— 把数据报告到文本文件。

## 描述

`ReportFile` 资源允许你把数据写入文本文件，该文件可在任务运行完成后查看。GMAT 允许你报告用户定义的 `Variable`（变量）、`Array`（数组）、`String`（字符串）和对象参数（Object Parameters）。GMAT 让你控制任务运行结束时生成的输出报告文件的格式属性。你可以在 GUI 或脚本接口中创建 `ReportFile` 资源。GMAT 还提供了通过 `Toggle` `On`/`Off` 命令控制何时开始和停止向文本文件写入数据的选项。关于 `ReportFile` 资源与 `Toggle` 命令之间交互的详细讨论，请参见下面的"备注"一节。

**另请参见**：Report、Toggle

## 字段

| 字段 | 描述 |
|------|------|
| `Add` | 允许用户向报告文件添加任意数量的用户定义 `Variable`、`Array`、`String` 或对象参数。要添加多个用户定义的变量或参数，用花括号包围要报告的值。例如 `MyReportName.Add ={Sat.X, Sat.Y, Var1, Array(1,1)}`；GUI 的 **Selected Value(s)** 字段等同于脚本的 `Add` 字段。此字段不能在任务序列中修改。<br>数据类型：引用数组<br>允许的值：任何用户定义的参数，例如变量、数组、字符串或对象参数<br>访问方式：set<br>默认值：`{DefaultSC.A1ModJulian, DefaultSC.EarthMJ2000Eq.X}`<br>单位：N/A<br>接口：GUI、脚本 |
| `AppendToExistingFile` | 允许用户把文本追加到现有文件，而不是在使用前清空它。如果此字段设置为 `True` 但文件尚不存在，则创建一个新文件。目标文件的设置请参见 `Filename` 字段。<br>数据类型：布尔<br>允许的值：True、False<br>访问方式：set<br>默认值：`False`<br>单位：N/A<br>接口：GUI、脚本 |
| `ColumnWidth` | 此字段定义报告文件中数据列的宽度。`ColumnWidth` 的值应用于所有数据列。例如，如果 `ColumnWidth` 设置为 20，则每个数据列宽 20 个空白字符。<br>数据类型：整数<br>允许的值：整数 > 1<br>访问方式：set<br>默认值：23<br>单位：字符<br>接口：GUI、脚本 |
| `Delimiter` | 当 `FixedWidth` 字段关闭时，此字段激活。`Delimiter` 字段允许你以 `Comma`（逗号）、`Semicolon`（分号）、`Space`（空格）和 `Tab`（制表符）分隔格式把数据报告到报告文件。<br>数据类型：枚举<br>允许的值：`Comma`、`SemiColon`、`Space`、`Tab`<br>访问方式：set<br>默认值：此字段激活时，默认为 `Space`<br>单位：N/A<br>接口：GUI、脚本 |
| `Filename` | 允许用户定义报告文件的文件路径和文件名。<br>数据类型：字符串<br>允许的值：合法的文件路径和名称<br>访问方式：set<br>默认值：`ReportFile1.txt`<br>单位：N/A<br>接口：GUI、脚本 |
| `FixedWidth` | 允许你启用或禁用 `Delimiter` 和 `ColumnWidth` 字段。当此字段打开时，`Delimiter` 字段不可用，`ColumnWidth` 字段激活，可用于改变数据列的宽度。当 `FixedWidth` 字段关闭时，`ColumnWidth` 字段不可用，`Delimiter` 字段激活可用。<br>数据类型：布尔<br>允许的值：On、Off<br>访问方式：set<br>默认值：`On`<br>单位：N/A<br>接口：GUI、脚本 |
| `LeftJustify` | 当 `LeftJustify` 字段设置为 `On` 时，数据左对齐并出现在列的最左侧。如果 `LeftJustify` 字段设置为 `Off`，则数据在列中居中。<br>数据类型：布尔<br>允许的值：On、Off<br>访问方式：set<br>默认值：On<br>单位：N/A<br>接口：GUI、脚本 |
| `Maximized` | 允许用户最大化 `ReportFile` 窗口。此字段不能在任务序列中修改。<br>数据类型：布尔<br>允许的值：true、false<br>访问方式：set<br>默认值：false<br>单位：N/A<br>接口：脚本 |
| `Precision` | 允许用户设置写入报告的数据的有效数字位数。<br>数据类型：整数<br>允许的值：整数 > 1<br>访问方式：set<br>默认值：16<br>单位：与被报告的变量相同<br>接口：GUI、脚本 |
| `RelativeZOrder` | 允许用户选择哪个 `ReportFile` 首先显示在屏幕上。`RelativeZOrder` 值最低的 `ReportFile` 最后显示，而 `RelativeZOrder` 值最高的 `ReportFile` 最先显示。此字段不能在任务序列中修改。<br>数据类型：整数<br>允许的值：整数 ≥ 0<br>访问方式：set<br>默认值：0<br>单位：N/A<br>接口：脚本 |
| `Size` | 允许用户控制生成的报告文件的显示大小。[0 0] 矩阵中的第一个值控制报告文件窗口的水平大小，第二个值控制垂直大小。此字段不能在任务序列中修改。<br>数据类型：实数数组<br>允许的值：任何实数<br>访问方式：set<br>默认值：[ 0 0 ]<br>单位：N/A<br>接口：脚本 |
| `SolverIterations` | 此字段决定在求解器（`Targeter`、`Optimize`）序列期间与摄动轨迹关联的数据是否写入报告文件。当 `SolverIterations` 设置为 `All` 时，所有摄动/迭代都写入报告文件。当 `SolverIterations` 设置为 `Current` 时，只有当前解写入报告文件。当 `SolverIterations` 设置为 `None` 时，只显示迭代过程结束后的最终解，并且只把最终解报告到报告文件。<br>数据类型：枚举<br>允许的值：`All`、`Current`、`None`<br>访问方式：set<br>默认值：`Current`<br>单位：N/A<br>接口：GUI、脚本 |
| `UpperLeft` | 允许用户把生成的报告文件显示窗口向任意方向平移。[0 0] 矩阵中的第一个值帮助水平平移报告文件窗口，第二个值帮助垂直平移窗口。此字段不能在任务序列中修改。<br>数据类型：实数数组<br>允许的值：任何实数<br>访问方式：set<br>默认值：[ 0 0 ]<br>单位：N/A<br>接口：脚本 |
| `WriteHeaders` | 此字段指定是否在报告文件中包含描述变量的表头。<br>数据类型：布尔<br>允许的值：True、False<br>访问方式：set<br>默认值：True<br>单位：N/A<br>接口：GUI、脚本 |
| `WriteReport` | 此字段指定是否把数据写入报告 `FileName`。<br>数据类型：布尔<br>允许的值：True、False<br>访问方式：set<br>默认值：True<br>单位：N/A<br>接口：GUI、脚本 |
| `ZeroFill` | 允许在写入报告的数据中补零，以匹配所设的精度。<br>数据类型：布尔<br>允许的值：On、Off<br>访问方式：set<br>默认值：Off<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

下图显示了 `ReportFile` 资源的默认名称和设置：

> [图：ReportFile 资源的默认 GUI 设置窗口]

## 备注

### 使用 Filename 字段时的行为

GMAT 允许你以两种方式指定报告文件的名称。使用 `FileName` 字段时报告文件的默认命名约定如下所示：

```
Create ReportFile aReport
aReport.Filename    = 'ReportFile1.txt'
aReport.WriteReport = true
```

说明：用单引号包围文件名的标准写法。

另一种命名报告文件的方法是不在报告文件名周围使用任何单引号。

```
Create ReportFile aReport
aReport.Filename = ReportFile1.txt
aReport.WriteReport = true
```

说明：文件名也可以不加引号直接赋值。

### 数据如何报告到报告文件

GMAT 允许你以两种方式把数据报告到报告文件：你可以使用 `ReportFile.Add` 字段或 `Report` 命令。

你可以使用 `ReportFile` 资源的 `.Add` 字段添加数据，此方法在每个传播步把数据报告到报告文件。下面的示例脚本片段展示了如何使用 `.Add` 字段报告历元和选定的轨道根数：

```
Create Spacecraft aSat
Create ReportFile aReport

aReport.Add = {aSat.UTCGregorian aSat.Earth.SMA, aSat.Earth.ECC, ...
aSat.Earth.TA, aSat.EarthMJ2000Eq.RAAN}

Create Propagator aProp

BeginMissionSequence
Propagate aProp(aSat) {aSat.ElapsedSecs = 8640.0}
```

说明：通过 aReport.Add 花括号列表登记要报告的参数（历元、半长轴、偏心率、真近点角、升交点赤经）；传播 8640 秒期间，每个积分步都会把这些数据写入报告文件。

如果 `BeginMissionSequence` 之下没有包含 `Propagate` 命令，GMAT 的 `ReportFile.Add` 字段将不会在每个传播步把所选数据报告到报告文件。

另一种把数据报告到报告文件的方法是通过 `Report` 命令。使用 `Report` 命令允许你在任务的特定点把数据报告到报告文件。下面的示例脚本片段展示了如何使用 `Report` 命令报告历元和选定的轨道根数：

```
Create Spacecraft aSat
Create ReportFile aReport

Create Propagator aProp

BeginMissionSequence

Report aReport aSat.UTCGregorian aSat.Earth.SMA aSat.Earth.ECC ...
aSat.Earth.TA aSat.EarthMJ2000Eq.RAAN

Propagate aProp(aSat) {aSat.ElapsedSecs = 8640.0}

Report aReport aSat.UTCGregorian aSat.Earth.SMA aSat.Earth.ECC ...
aSat.Earth.TA aSat.EarthMJ2000Eq.RAAN
```

说明：在传播前后各执行一次 Report 命令，只在任务初始点和传播 8640 秒后的终点两个特定位置写入数据。

### 使用 ReportFile 资源和 Report 命令时的行为与交互

假设你使用了一个 `ReportFile` 资源，并选择不写报告，即为字段 `WriteReport` 选择 `false`，如下例所示：

```
Create ReportFile aReport
aReport.Filename = ReportFile1.txt
aReport.Add = {aSat.A1ModJulian, aSat.Earth.SMA}
aReport.WriteReport = false
```

说明：WriteReport = false 表示该资源的自动报告（Add 字段）被关闭。

现在假设与此同时，你决定在任务树中使用 `Report` 命令，如下面的示例脚本片段所示：

```
BeginMissionSequence;
Report aReport aSat.A1ModJulian aSat.Earth.SMA aSat.Earth.ECC
Propagate aProp(aSat) {aSat.Earth.Periapsis}
Report aReport aSat.A1ModJulian aSat.Earth.SMA aSat.Earth.ECC
```

说明：任务序列中在传播到近地点前后各执行一次 Report 命令。

此时，你可能认为由于在 `ReportFile` 资源的 `WriteReport` 字段下选择了 false 选项，GMAT 将不会生成名为 `ReportFile1.txt` 的报告文件。恰恰相反，GMAT 会生成名为 `ReportFile1.txt` 的报告，但此报告只包含使用 `Report` 命令请求的数据。`ReportFile1.txt` 文本文件将只在任务的特定点包含历元、半长轴和偏心率。

### 在迭代过程中报告数据时的行为

GMAT 允许你指定在差分校正或优化等迭代过程中数据如何写入报告。`ReportFile` 资源的 `SolverIterations` 字段支持 3 个选项，如下表所述：

| SolverIterations 选项 | 描述 |
|----------------------|------|
| `All` | 显示迭代过程中的所有迭代/摄动，并把所有迭代/摄动报告到报告文件。 |
| `Current` | 在迭代过程结束后只显示当前迭代/摄动，并把当前解报告到报告文件。 |
| `None` | 在迭代过程结束后只显示最终解，并且只把最终解报告到报告文件。 |

### 报告写入的位置

GMAT 允许你把报告写入任何所需的路径或位置。你可以通过打开 GMAT 的启动文件 `gmat_startup_file.txt` 并在 `OUTPUT_PATH` 下定义绝对路径来实现。这允许你把报告文件保存在你选择的目录中，而不是保存在 GMAT 的默认 Output 文件夹中。在 `ReportFile.FileName` 字段中，如果没有提供路径而只定义了报告文件的名称，则报告文件会被写入 GMAT 的默认 Output 文件夹。报告写入的默认路径是位于 GMAT 安装主目录中的 Output 文件夹。

下面的示例脚本片段展示了当 `FileName` 字段下只提供报告文件名时，生成的报告写入何处。在本例中，`'ReportFile1.txt'` 报告被写入位于 GMAT 安装主目录中的 Output 文件夹：

```
Create ReportFile aReport

aReport.Filename = 'ReportFile1.txt'
aReport.Add      = {aSat.A1ModJulian, aSat.Earth.ECC}
```

说明：只给文件名不给路径时，报告写入 GMAT 默认 Output 文件夹。

另一种报告文件写入方法是定义相对路径。你可以在 GMAT 的启动文件 `gmat_startup_file.txt` 中的 `OUTPUT_PATH` 下定义相对路径。例如，你可以通过设置 `OUTPUT_PATH = C:/Users/rqureshi/Desktop/GMAT/mytestfolder/../output2/` 来设置相对路径。在此路径中，语法 ".." 表示"向上一级"。保存启动文件后，当脚本执行时，在 `FileName` 字段下命名的生成报告文件将被写入路径 `C:\Users\rqureshi\Desktop\GMAT\output2`。

报告文件还可以写入的另一种方法是在 GMAT 的启动文件 `gmat_startup_file.txt` 中的 `OUTPUT_PATH` 下定义绝对路径。例如，你可以通过设置 `OUTPUT_PATH = C:/Users/rqureshi/Desktop/GMAT/mytestfolder/` 来设置绝对路径。当脚本执行时，在 `FileName` 字段下命名的报告文件将被写入绝对路径 `C:\Users\rqureshi\Desktop\GMAT\mytestfolder`。

你也可以不在 GMAT 的启动文件中定义相对或绝对路径，而是选择在 `FileName` 字段下定义绝对路径。例如，如果你设置 `ReportFile.FileName = C:\Users\rqureshi\Desktop\GMAT\mytestfolder\ReportFile.txt`，则报告文件将保存在 `mytestfolder` 中。

### 使用 ReportFile 资源和 Toggle 命令时的行为

GMAT 允许你在使用 `ReportFile` 资源的 `Add` 字段时使用 `Toggle` 命令。当对一个 `ReportFile` 发出 `Toggle Off` 命令时，在发出 `Toggle On` 命令之前不会有数据发送到报告文件。同样，当使用 `Toggle On` 命令时，数据在每个积分步发送到报告文件，直到使用 `Toggle Off` 命令为止。

下面的示例脚本片段展示了如何在使用 `ReportFile` 资源时使用 `Toggle Off` 和 `Toggle On` 命令。航天器的笛卡尔位置矢量被报告到报告文件。

```
Create Spacecraft aSat
Create Propagator aProp

Create ReportFile aReport
aReport.Filename = 'ReportFile1.txt'
aReport.Add      = {aSat.UTCGregorian, aSat.EarthMJ2000Eq.X ...
aSat.EarthMJ2000Eq.Y aSat.EarthMJ2000Eq.Z}

BeginMissionSequence

Toggle aReport Off
Propagate aProp(aSat) {aSat.ElapsedDays = 2}
Toggle aReport On
Propagate aProp(aSat) {aSat.ElapsedDays = 4}
```

说明：先用 Toggle Off 关闭报告，传播前 2 天不写入数据；再 Toggle On 打开报告，之后 4 天的传播中每个积分步都把历元和位置三分量写入报告文件。

### 在 ReportFile 的 Add 字段中指定空花括号时的行为

使用 `ReportFile.Add` 字段时，GMAT 不允许花括号留空。花括号必须始终填充你希望报告的值。如果花括号留空，GMAT 会抛出异常。下面的示例脚本片段展示了空花括号的例子。如果你运行此脚本，GMAT 会抛出异常，提醒你花括号不能留空。

```
Create Spacecraft aSat
Create Propagator aProp
Create ReportFile aReport

aReport.Add = {}

BeginMissionSequence
Propagate aProp(aSat) {aSat.ElapsedSecs = 8640.0}
```

说明：`aReport.Add = {}` 是非法写法，运行时会抛出异常。

## 示例

传播一条轨道，并在每个积分步把笛卡尔状态写入报告文件：

```
Create Spacecraft aSat
Create Propagator aProp

Create ReportFile aReport
aReport.Filename = 'ReportFile1.txt'
aReport.Add      = {aSat.EarthMJ2000Eq.X aSat.EarthMJ2000Eq.Y ...
aSat.EarthMJ2000Eq.Z aSat.EarthMJ2000Eq.VX ...
aSat.EarthMJ2000Eq.VY aSat.EarthMJ2000Eq.VZ}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedSecs = 8640.0}
```

说明：通过 Add 字段登记位置和速度六个分量，传播 8640 秒期间每个积分步自动写入报告文件。

传播一条轨道 1 天，并在任务的特定点把笛卡尔状态写入报告文件：

```
Create Spacecraft aSat
Create Propagator aProp

Create ReportFile aReport
aReport.Filename = 'ReportFile1.txt'

BeginMissionSequence

Report aReport aSat.EarthMJ2000Eq.X aSat.EarthMJ2000Eq.Y ...
aSat.EarthMJ2000Eq.Z aSat.EarthMJ2000Eq.VX ...
aSat.EarthMJ2000Eq.VY aSat.EarthMJ2000Eq.VZ

Propagate aProp(aSat) {aSat.ElapsedDays = 1}

Report aReport aSat.EarthMJ2000Eq.X aSat.EarthMJ2000Eq.Y ...
aSat.EarthMJ2000Eq.Z aSat.EarthMJ2000Eq.VX ...
aSat.EarthMJ2000Eq.VY aSat.EarthMJ2000Eq.VZ
```

说明：不使用 Add 字段，而是用 Report 命令在传播前和传播 1 天后两个特定点各写一次六分量状态。
