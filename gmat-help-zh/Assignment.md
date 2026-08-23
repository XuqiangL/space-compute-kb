# 赋值命令（Assignment，=）
> 译自 GMAT R2026a 帮助文档 Assignment.html

赋值命令（`=`）—— 将变量或资源字段设置为某个值，可以使用数学表达式。

## 脚本语法

```
settable_item = expression
```

## 描述

赋值命令（在 GUI 中称为 `Equation` 命令）允许你将资源字段或参数设置为某个值，可以使用数学表达式。GMAT 使用赋值运算符（'='）表示赋值命令。赋值运算符使用以下语法，其中 LHS 表示运算符的左侧，RHS 表示运算符的右侧：

```
LHS = RHS
```

在该表达式中，左侧（`LHS`）被设置为右侧（`RHS`）的值。`LHS` 和 `RHS` 表达式的语法各不相同，但两者必须求值为兼容的数据类型，命令才能成功。

### 左侧（LHS）

赋值命令的左侧必须是以下任一类型的单个项：

- 允许的资源（例如 `Spacecraft`、`Variable`、`Array`）
- 允许资源的资源字段（例如 `Spacecraft`.`Epoch`、`Spacecraft`.`DateFormat`）
- 可设置的资源参数（例如 `Spacecraft`.`X`、`ReportFile`.`Precision`）
- `Array` 或 `Array` 元素

要确定哪些字段和参数可以被设置，请参见相应资源的文档。

### 右侧（RHS）

赋值命令的右侧可以由以下任意内容组成：

- 字面量值
- 资源（例如 `Spacecraft`、`Variable`、`Array`）
- 资源字段（例如 `Spacecraft`.`Epoch`、`Spacecraft`.`DateFormat`）
- 资源参数（例如 `Spacecraft`.`X`、`ChemicalThruster`.`K1`）
- `Array` 或 `Array` 元素
- 数学表达式（见下文）

MATLAB 函数调用被视为与赋值命令不同的概念。更多信息请参见相应的参考页。

## GUI

> [图：GUI 中 Equation（赋值）命令的属性面板]

脚本语言中的赋值命令对应于 GUI 中的 `Equation` 命令。`Equation` 属性框允许你在自由格式的文本框中输入表达式的两侧。每侧的默认值是 "`Not_Set`"；这些只是占位符，在任务运行时是无效的。你可以在每个框中输入与上文脚本语言所述相同的语法。当你点击 `OK` 或 `Apply` 时，GMAT 会验证表达式的两侧，并对任何警告或错误给出反馈。

## 备注

### 数据类型兼容性

一般来说，在所有表达式求值之后，左侧和右侧的数据类型必须匹配。这意味着 `Spacecraft` 资源只能被设置为另一个 `Spacecraft` 资源，数值参数只能被设置为数值，`String` 资源只能被设置为字符串值。此外，`Array` 实例的维数必须匹配，命令才能成功。对于数值量，赋值命令不区分整数和浮点值。

### 参数

参数可以用在赋值命令的任一侧，但可能有某些限制。

在命令的右侧，可以使用任何参数。如果某个参数接受依赖项（例如 `Spacecraft`.*CoordinateSystem*.`X`）而依赖项被省略，则将使用默认依赖值。对于依赖坐标系的参数，默认值是 `EarthMJ2000Eq`。对于依赖中心天体的参数，默认值是 `Earth`。

在左侧，只能使用可设置（可写）的参数。此外，不能指定依赖项，除非在赋值命令两侧的依赖项等效的特殊情况下。在左侧，被省略依赖项的默认值自动取为所引用 `Spacecraft` 的 `CoordinateSystem` 字段及其中心天体的当前值。

以下示例展示了参数的合法与非法用法：

```
Create Spacecraft aSat1 aSat2
aSat2.CoordinateSystem = 'EarthFixed'
Create Variable x
BeginMissionSequence
x = aSat1.EarthFixed.X       % Valid: Parameter with dependency on RHS
x = aSat1.EarthMJ2000Eq.X    % Valid: This and next statement are equiv.
x = aSat1.X                  % Valid: Default dep. value is EarthMJ2000Eq.

x = aSat1.Mars.Altitude      % Valid: Parameter with dependency on RHS
x = aSat1.Earth.Altitude     % Valid: This and next statement are equiv.
x = aSat1.Altitude           % Valid: Default dependency value is Earth.

aSat2.X = 1e5                % Valid: Default parameter value is EarthFixed.
aSat2.EarthMJ2000Eq.X = 1e5  % INVALID: Dependencies not allowed on LHS.
aSat2.EarthFixed.X = 1e5     % Valid: Special case because value = default.

aSat2.EarthMJ2000Eq.X = aSat1.EarthFixed.X    % INVALID: Dependency on LHS
aSat2.EarthMJ2000Eq.X = aSat1.EarthMJ2000Eq.X % INVALID: Dependency on LHS
aSat2.EarthFixed.X = aSat1.EarthFixed.X       % Valid: Special case

% DANGEROUS! Valid, but sets EarthMJ2000Eq RHS values to EarthFixed LHS param.
aSat2.X = aSat1.EarthMJ2000Eq.X

% DANGEROUS! RHS default is EarthMJ2000Eq, LHS default is current setting on
% aSat2 (EarthFixed in this case).
aSat2.X = aSat1.X
```

逐段说明：第一组中，右侧带依赖项（`EarthFixed`、`EarthMJ2000Eq`）的参数均合法；省略依赖项时使用默认值 `EarthMJ2000Eq`。第二组同理，中心天体依赖项默认值为 `Earth`。第三组中，`aSat2.X = 1e5` 合法（左侧省略依赖项时取 aSat2 当前坐标系 EarthFixed）；`aSat2.EarthMJ2000Eq.X = 1e5` 非法，因为左侧不允许指定依赖项；`aSat2.EarthFixed.X = 1e5` 合法，属于"指定值等于默认值"的特殊情况。第四组中，左侧带依赖项的语句均非法，唯一合法的是两侧依赖项等效的特殊情况。最后两句虽然合法但危险：`aSat2.X = aSat1.EarthMJ2000Eq.X` 会把 EarthMJ2000Eq 坐标系的值赋给按 EarthFixed 解释的左侧参数；`aSat2.X = aSat1.X` 中右侧默认取 EarthMJ2000Eq，而左侧默认取 aSat2 的当前设置（本例中为 EarthFixed），两侧坐标系不一致。

### 数学表达式

赋值命令支持在命令右侧使用内联数学表达式。这些表达式遵循 MATLAB 表达式的一般语法规则，可以使用多种运算符和内置函数。

#### 解析

数学表达式通过下文所述的任何运算符或内置函数的出现来识别。在执行之前，表达式中的所有空白字符（如空格和制表符）都会被移除。

#### 数据类型

数学表达式作用于数值（整数或浮点数）。这包括以下内容：

- 字面量值
- 数值资源（`Variable`、`Array`）
- 可读取的资源参数（例如 `Spacecraft`.`X`、`ChemicalThruster`.`K1`）
- `Array` 元素
- 计算参数（例如 `Spacecraft`.`OrbitPeriod`）
- 嵌套的数学表达式

GMAT 的若干运算符和函数是向量化的，因此它们既可以作用于标量数值，也可以作用于整个 `Array` 资源。
#### 运算符

**向量化运算符**

| 运算符 | 说明 |
|--------|------|
| `+` | 加法或一元正号。`X+Y` 将 `X` 与 `Y` 相加。`X` 和 `Y` 必须具有相同的维数，除非其中之一是标量。 |
| `-` | 减法或一元负号。`-X` 是 `X` 的相反数，`X` 可以是任意大小。`X-Y` 从 `X` 中减去 `Y`。`X` 和 `Y` 必须具有相同的维数，除非其中之一是标量。 |
| `*` | 乘法。`X*Y` 是 `X` 与 `Y` 的乘积。若 `X` 和 `Y` 都是标量，则为简单的代数乘积。若 `X` 是矩阵或向量而 `Y` 是标量，则 `X` 的所有元素都乘以 `Y`（反之亦然）。若 `X` 和 `Y` 都是非标量，则 `X*Y` 执行矩阵乘法，且 `X` 的列数必须等于 `Y` 的行数。 |
| `'` | 转置。`X'` 是 `X` 的转置。若 `X` 是标量，则 `X'` 等于 `X`。 |

**标量运算符**

| 运算符 | 说明 |
|--------|------|
| `/` | 除法。`X/Y` 用 `X` 除以 `Y`。若 `X` 和 `Y` 都是标量，则为简单的代数商。若 `X` 是矩阵或向量，则每个元素都除以 `Y`。`Y` 必须是非零标量。 |
| `^` | 幂。`X^Y` 将 `X` 升为 `Y` 次幂。`X` 和 `Y` 必须是标量。特殊情况是 `X^(-1)`：当作用于方阵 `X` 时，返回 `X` 的逆矩阵。 |

当多个表达式组合在一起时，GMAT 使用以下运算顺序。运算从列表顶部的运算符开始，依次向下进行。在同一优先级内，运算从左到右进行。

1. 括号 `()`
2. 转置（`'`）、幂（`^`）
3. 一元正号（`+`）、一元负号（`-`）
4. 乘法（`*`）、除法（`/`）
5. 加法（`+`）、减法（`-`）

#### 内置函数

GMAT 在数学表达式中支持以下内置函数。支持的函数包括：常见的标量函数（即只接受单个值的函数，如 sin 和 cos）、作用于整个矩阵或向量的矩阵函数，以及字符串函数。

**标量数学函数**

| 函数 | 说明 |
|------|------|
| `sin` | 正弦。在 `Y = sin(X)` 中，`Y` 是角 `X` 的正弦。`X` 必须以弧度为单位。`Y` 的取值范围为 [-1, 1]。 |
| `cos` | 余弦。在 `Y = cos(X)` 中，`Y` 是角 `X` 的余弦。`X` 必须以弧度为单位。`Y` 的取值范围为 [-1, 1]。 |
| `tan` | 正切。在 `Y = tan(X)` 中，`Y` 是角 `X` 的正切。`X` 必须以弧度为单位。正切函数在归一化为 p/2 或 -p/2 的角度处无定义。 |
| `asin` | 反正弦。在 `Y = asin(X)` 中，`Y` 是 `X` 的反正弦。`X` 必须在 [-1, 1] 范围内，`Y` 的取值范围为 [-p/2, p/2]。 |
| `acos` | 反余弦。在 `Y = acos(X)` 中，`Y` 是 `X` 的反余弦。`X` 必须在 [-1, 1] 范围内，`Y` 的取值范围为 [0, p]。 |
| `atan` | 反正切。在 `Y = atan(X)` 中，`Y` 是 `X` 的反正切。`Y` 的取值范围为 (-p/2, p/2)。 |
| `atan2` | 四象限反正切。在 `A = atan2(Y, X)` 中，`A` 是 `Y/X` 的反正切。`A` 的取值范围为 (-p, p]。除取值范围更大外，`atan2(Y, X)` 等价于 `atan(Y/X)`。 |
| `log` | 自然对数。在 `Y = log(X)` 中，`Y` 是 `X` 的自然对数。`X` 必须为正且非零。 |
| `log10` | 常用对数。在 `Y = log10(X)` 中，`Y` 是 `X` 的常用（以 10 为底）对数。`X` 必须为正且非零。 |
| `exp` | 指数。在 `Y = exp(X)` 中，`Y` 是 `X` 的指数（e^X）。 |
| `DegToRad` | 弧度转换。在 `Y = DegToRad(X)` 中，`Y` 是以弧度为单位的角度 `X`。`X` 必须是以度为单位的角度。 |
| `RadToDeg` | 度数转换。在 `Y = RadToDeg(X)` 中，`Y` 是以度为单位的角度 `X`。`X` 必须是以弧度为单位的角度。 |
| `abs` | 绝对值。在 `Y = abs(X)` 中，`Y` 是 `X` 的绝对值。 |
| `sqrt` | 平方根。在 `Y = sqrt(X)` 中，`Y` 是 `X` 的平方根。`X` 必须非负。 |

**数值处理函数**

| 函数 | 说明 |
|------|------|
| `mod` | 除后取模。`mod(x,y)` 返回 `x - n*y`，其中当 `y ~= 0` 时 `n = floor(x/y)`。按约定，`mod(x,x)` 为 `x`。 |
| `ceil` | 向正无穷方向取整。`ceil(X)` 将 `X` 向正无穷方向取为最近的整数。 |
| `floor` | 向负无穷方向取整。`floor(X)` 将 `X` 向负无穷方向取为最近的整数。 |
| `fix` | 向零方向取整。`fix(X)` 将 `X` 向零方向取为最近的整数。 |

**随机数函数**

| 函数 | 说明 |
|------|------|
| `randn` | 正态分布伪随机数。`R = randn(N)` 返回一个 N×N 矩阵，包含取自标准正态分布的伪随机值。`R = randn()` 返回单个随机数。 |
| `rand` | 均匀分布伪随机数。`R = rand(N)` 返回一个 N×N 矩阵，包含取自开区间 `(0,1)` 上标准均匀分布的伪随机值。`R = rand()` 返回单个随机数。 |
| `SetSeed` | 设置随机数生成的种子。`SetSeed(X)` 设置随机数生成器的种子，`X` 必须是正实数。注意：`SetSeed` 调用的是 C++11 随机数生成器的种子算法，该算法要求无符号整数。由于 GMAT 脚本语言只支持实数，编译器会进行类型转换，将实数向下取整为最近的整数。我们建议传入尾数为零的实数（即 "1.0" 或 "198.0"）。 |

**矩阵函数**

| 函数 | 说明 |
|------|------|
| `norm` | 2-范数。在 `Y = norm(X)` 中，`Y` 是 `X` 的 2-范数，`X` 必须是向量（即某一维必须为 1）。若 `X` 是标量，则 `Y` 等于 `X`。 |
| `det` | 行列式。在 `Y = det(X)` 中，`Y` 是 `X` 的行列式。若 `X` 是矩阵，其行数必须等于列数。若 `X` 是标量，则 `Y` 等于 `X`。为提高效率，GMAT 的行列式实现目前限制在 9×9 或更小的矩阵。 |
| `cross` | 向量叉积。在 `C = cross(A,B)` 中，`C` 是 `A` 与 `B` 的向量叉积。`A` 和 `B` 必须是 3 元素数组。 |
| `inv` | 逆。在 `Y = inv(X)` 中，`Y` 是 `X` 的逆。`X` 必须是矩阵或标量。若 `X` 是矩阵，其行数必须等于列数。`X^(-1)` 是等价的替代语法。 |
**字符串处理函数**

| 函数 | 说明 |
|------|------|
| `strcat` | 字符串连接。`STROUT = strcat(S1, S2, ..., SN)` 连接多个字符串。输入可以是字符串变量和字符串字面量的组合。 |
| `strfind` | 字符串查找。`INDEX = strfind(TEXT,PATTERN)` 返回 `PATTERN` 在 `TEXT` 中首次出现的起始索引。如果未找到 `PATTERN`，则 `INDEX = -1`。 |
| `strrep` | 字符串替换。`NEWSTR = strrep(OLDSTR,OLDSUBSTR,NEWSUBSTR)` 将字符串 `OLDSTR` 中所有出现的子串 `OLDSUBSTR` 替换为字符串 `NEWSUBSTR`。 |
| `strcmp` | 字符串比较。`FLAG = strcmp(S1,S2)` 比较字符串 `S1` 和 `S2`，若完全相同则返回逻辑 1（真），否则返回逻辑 0（假）。 |
| `strlen` | 字符串长度。`LENGTH = strlen(S1)` 返回字符串 s1 的长度。 |
| `substr` | 子字符串。`S2 = substr(S1, START, END = strlen(s1))` 从字符串 S1 创建子串，起始索引为 START，结束索引为 END（从零开始计数）。END 是可选参数。如果省略 END，则 END 被视为字符串长度，创建的子串一直延续到原字符串的末尾。 |
| `sprintf` | 将格式化数据写入字符串。`STRING = sprintf(FORMATSPEC, A, ...)` 按照 `FORMATSPEC`（C 语言风格的格式说明）格式化 `A,...` 中的数据。注意：GMAT 的 `sprintf` 函数调用的是 C 库 `iostream` 中的 sprintf 函数。此外，GMAT 脚本语言不支持整数数据类型，只支持双精度浮点数。格式说明的原型为：`%[flags][width][.precision][length]specifier` |

**格式说明符（Specifiers）**

| 说明符 | 说明 |
|--------|------|
| `a` | 十六进制浮点数，小写 |
| `A` | 十六进制浮点数，大写 |
| `e` | 科学计数法（尾数/指数），小写 |
| `E` | 科学计数法（尾数/指数），大写 |
| `f` | 十进制浮点数，小写 |
| `F` | 十进制浮点数，大写 |
| `g` | 使用最短的表示：%e 或 %f |
| `G` | 使用最短的表示：%E 或 %F |
| `o` | 无符号八进制 |
| `x` | 无符号十六进制整数，小写 |
| `X` | 无符号十六进制整数，大写 |

**标志（Flags）**

| 标志 | 说明 |
|------|------|
| `+` | 强制在结果前加上正号或负号（+ 或 -），即使是正数。默认情况下只有负数前面带 - 号。 |
| `-` | 在给定字段宽度内左对齐；默认为右对齐（见 width 子说明符）。 |
| `#` | 与 o、x 或 X 说明符一起使用时，非零值前面分别加上 0、0x 或 0X。与 a、A、e、E、f、F、g 或 G 一起使用时，强制输出包含小数点，即使后面没有更多数字。默认情况下，如果后面没有数字，则不写小数点。 |
| `0` | 指定填充时，用零（0）而不是空格在左侧填充数字（见 width 子说明符）。 |
| （空格） | 如果不写符号，则在值前插入一个空格。 |

**宽度（Width）**

| 项 | 说明 |
|----|------|
| （数字） | 要打印的最小字符数。如果要打印的值短于此数，结果将用空格填充。即使结果更长，值也不会被截断。 |

**精度（Precision）**

| 项 | 说明 |
|----|------|
| （数字） | 对于 a、A、e、E、f 和 F 说明符：这是小数点后要打印的位数（默认为 6）。对于 g 和 G 说明符：这是要打印的最大有效数字位数。对于 s：这是要打印的最大字符数，默认打印所有字符直到遇到结尾的空字符。如果指定了句点但没有明确的精度值，则假定为 0。不支持整数说明符，因为 GMAT 脚本语言中没有整数数据类型。 |

**时间处理函数**

| 函数 | 说明 |
|------|------|
| `Pause` | 暂停。`Pause(T)` 暂停 GMAT 应用程序。输入为实数，表示暂停的秒数。暂停时间被截断到毫秒精度。 |
| `ConvertTime` | 时间转换。`ConvertTime(SF, EF, T)` 接受以 GMAT 预定义格式 SF 表示的时间值 T，并返回以 GMAT 格式 EF 表示的该时间。T 必须是 GMAT 时间字符串。SF 和 EF 必须是具有以下值之一的字符串："A1ModJulian"、"TAIModJulian"、"UTCModJulian"、"TDBModJulian"、"TTModJulian"、"A1Gregorian"、"TAIGregorian"、"UTCGregorian"、"TDBGregorian"、"TTGregorian"。 |
| `SystemTime` | 系统时间。`SystemTime(F)` 以格式 F 生成调用它的系统的当前时间。F 必须是具有以下值之一的字符串："A1ModJulian"、"TAIModJulian"、"UTCModJulian"、"TDBModJulian"、"TTModJulian"、"A1Gregorian"、"TAIGregorian"、"UTCGregorian"、"TDBGregorian"、"TTGregorian"。注意：SystemTime 在 Windows 与类 Unix 系统（如 Linux 和 Mac）之间的行为可能不同。 |

**四元数函数**

| 函数 | 说明 |
|------|------|
| `QuaternionProduct` | 四元数乘积。`QuaternionProduct(Q1, Q2)` 计算两个四元数 Q1 与 Q2 的乘积。它们以 [1,4] GMAT 数组提供，前三个元素表示向量部分，第四个元素为标量。返回包含乘积的 [1,4] 数组。如果乘积的标量元素为负，则改变四元数各元素的符号，以提供旋转角较小的解。如果输入未归一化，函数会自动执行归一化。 |
| `QuaternionRotation` | 四元数旋转。`QuaternionRotation(Q, V)` 将提供的 [1,3] 向量 V 绕 [1,4] 四元数 Q 定义的轴旋转。Q 的前三个元素表示四元数的向量部分，第四个元素是标量。正角度使向量沿逆时针方向转动。Q 在执行旋转前会自动归一化。 |
| `QuaternionToDCM` | 四元数转方向余弦矩阵。`QuaternionToDCM(Q)` 将提供的四元数 Q 转换为等价的方向余弦矩阵（DCM）。Q 以 [1,4] 数组提供，前三个元素是向量部分，最后一个元素是标量。返回的 DCM 以 [3,3] 数组提供。Q 在转换前由函数自动归一化。 |

**其他函数**

| 函数 | 说明 |
|------|------|
| `Sign` | 符号。`Sign(N)` 接受任意实数 N，若为正返回 1.0，若为零返回 0.0，若为负返回 -1.0。 |
| `Str2num` | 字符串转数值。`Str2num(S)` 接受字符串值 S 并将其转换为实数，存储在 GMAT 变量中。输入字符串 S 必须是合法实数的字符串表示。 |
| `Num2str` | 数值转字符串。`Num2str(N)` 接受数值 N 并将其转换为 GMAT 字符串。 |
| `RotationMatrix` | `RotationMatrix(CS, E, EF)` 生成坐标系在特定历元处的最新旋转矩阵和旋转导数矩阵。CS 必须是完整构建的 CoordinateSystem 对象。E 必须是包含历元的字符串。EF 是历元字符串的格式，必须是以下值之一："A1ModJulian"、"TAIModJulian"、"UTCModJulian"、"TDBModJulian"、"TTModJulian"、"A1Gregorian"、"TAIGregorian"、"UTCGregorian"、"TDBGregorian"、"TTGregorian"。 |
| `Angle` | `Angle(V, E1, E2)` 生成 3 个 SpacePoint 对象之间的夹角。第一个传入的参数必须是角的顶点，第 2、3 个参数必须是端点。至少有一个 SpacePoint 对象必须是 Spacecraft。 |

## 示例

计算一个基本的代数方程：

```
Create Variable A B C x y
x = 1
Create ReportFile aReport

BeginMissionSequence

A = 10
B = 20
C = 2

y = A*x^2 + B*x + C
Report aReport y
```

说明：创建变量并初始化 x=1；在任务序列中给 A、B、C 赋值，然后计算二次多项式 y = A*x² + B*x + C，最后用 Report 命令把 y 写入报告文件 aReport。

矩阵操作：

```
Create Array A[2,2] B[2,2] C[2,2] x[2,1] y[2,1]
Create ReportFile aReport

A(1,1) = 10
A(2,1) = 5
A(1,2) = .10
A(2,2) = 1

x(1,1) = 2
x(2,1) = 3

BeginMissionSequence

B = inv(A)
C = B'
y = C*x
Report aReport A B C x y
```

说明：创建若干 2×2 数组和 2×1 向量并初始化 A 与 x；在任务序列中，先求 A 的逆得到 B，再对 B 转置得到 C，然后计算矩阵乘积 y = C*x，最后将 A、B、C、x、y 全部输出到报告文件。

克隆资源：

```
Create Spacecraft Sat1 Sat2
Sat1.Cd = 1.87
Sat1.DryMass = 123.456

Create ReportFile aReport

BeginMissionSequence

Sat2 = Sat1
Report aReport Sat2.Cd Sat2.DryMass
```

说明：创建两颗卫星并设置 Sat1 的阻力系数与干质量；在任务序列中执行 `Sat2 = Sat1` 将 Sat1 整体复制给 Sat2（Spacecraft 资源支持整体赋值），然后输出 Sat2 的 Cd 和 DryMass 以验证复制结果。

使用内置函数：

```
Create Variable pi x y1 y2 y3
Create Array A[3,3]
Create Spacecraft aSat
Create ReportFile aReport

BeginMissionSequence

pi = acos(-1)

aSat.TA = pi/4
x = pi/4
A(1,1) = pi/4

y1 = sin(x)
y2 = sin(aSat.TA)
y3 = sin(A(1,1))

Report aReport y1 y2 y3
```

说明：用 `acos(-1)` 计算 π；然后把 π/4 分别赋给变量 x、航天器真近点角 `aSat.TA` 和数组元素 `A(1,1)`；接着分别对变量、资源参数和数组元素调用 `sin`，展示内置函数可作用于不同类型的数值来源；最后输出三个结果。
