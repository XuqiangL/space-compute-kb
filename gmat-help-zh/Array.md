# 数组资源（Array）
> 译自 GMAT R2026a 帮助文档 Array.html

Array —— 用户定义的一维或二维数组变量。

## 描述

`Array` 资源用于存储一维或二维的数值集合，例如向量或矩阵。在大多数命令中，数组的单个元素可以代替字面数值使用。

数组必须在创建时确定维数，使用以下语法：

```
Create Array anArray[rows, columns]
```

如果只指定一个维度，则创建行向量。

数组值在创建时初始化为零。可以使用字面数值逐个赋值，也可以（在任务序列中）使用 `Variable` 资源、`Array` 资源元素、数值类型的资源参数或求值为标量数值的 `Equation` 命令赋值。

```
anArray(row, column) = value
```

如果赋值时只指定一个维度，则假定 *row* 为 1。

在任务序列中，也可以使用另一个 `Array` 资源或求值为数组的 `Equation` 对 `Array` 进行整体赋值。赋值两侧必须大小完全相同。

```
anArray = array expression
```

**另请参见**：String、Variable

## 字段

`Array` 资源没有字段；取而代之的是直接给资源元素本身设置所需的值。

| 字段 | 描述 |
|------|------|
| *rows* | 行数（创建时），或正在寻址的行。数组的总大小为 *rows* × *columns*。此字段为必填。<br>数据类型：整数<br>允许的值：整数 >= 1<br>访问方式：set<br>默认值：1<br>单位：N/A<br>接口：GUI、脚本 |
| *columns* | 列数（创建时），或正在寻址的列。数组的总大小为 *rows* × *columns*。此字段为必填。<br>数据类型：整数<br>允许的值：整数 >= 1<br>访问方式：set<br>默认值：1<br>单位：N/A<br>接口：GUI、脚本 |
| *value* | 正在寻址的数组元素的值。<br>数据类型：实数<br>允许的值：-∞ < 实数 < ∞<br>访问方式：set、get<br>默认值：0.0<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

> [图：Array 资源的创建窗口]

GMAT GUI 允许你在不离开窗口的情况下一次创建多个 `Array` 资源。创建 `Array` 的步骤：

1. 在 **Array Name** 框中输入所需的数组名称。
2. 分别在 **Row** 和 **Column** 框中输入所需的行数和列数。要创建一维数组，将 **Row** 设为 1。
3. 单击 **=>** 按钮创建该数组并将其添加到右侧列表中。
4. 单击 **Edit** 按钮编辑数组元素的值。

你可以用这种方式创建多个 `Array` 资源。要在此窗口中编辑已有数组，在右侧列表中单击它。单击 **Edit** 更改元素值，或编辑 **Row** 和 **Column** 的值。必须再次单击 **=>** 按钮才能保存对数组大小的更改。

> [图：Array 资源的元素编辑窗口]

你可以通过在创建数组时单击 **Edit**，或在主 GMAT 窗口的资源树中双击该数组，来编辑 `Array` 的元素。编辑窗口允许你使用行、列列表并单击 **Update** 逐个更改数组元素，或者直接在窗口下部的表格中输入数据。数据表格支持以下几种鼠标和键盘操作：

- 单击单元格一次将其选中
- 再次单击已选中的单元格、双击未选中的单元格，或按 F2 编辑其值
- 使用方向键选择相邻单元格
- 单击角落的表头单元格选中整个表格
- 拖动列和行的分隔线调整行高或列宽
- 双击表头中的行或列分隔线自动调整行高或列宽

## 备注

GMAT 的 `Array` 资源存储按一维或二维组织的任意数量的数值。在内部，无论是否存在小数部分，元素都以双精度实数存储。`Array` 资源可以使用一个或两个维度说明符来创建和赋值。下面的示例展示了每种情况下的行为：

```
% a is a row vector with 3 elements
Create Array a[3]
a(1) = 1    % same as a(1, 1) = 1
a(2) = 2    % same as a(1, 2) = 2
a(3) = 3    % same as a(1, 3) = 3

% b is a matrix with 5 rows and 3 columns
Create Array b[5, 3]
b(1) = 1    % same as b(1, 1) = 1
b(2) = 2    % same as b(1, 2) = 2
b(3) = 3    % same as b(1, 3) = 3
b(4) = 4    % error: b(1, 4) does not exist
b(4, 3) = 4 % row 4, column 3
```

说明：a 是含 3 个元素的行向量，单下标 a(1) 等价于 a(1,1)。b 是 5 行 3 列的矩阵，单下标 b(n) 表示第 1 行第 n 列，因此 b(4) 越界报错；要访问第 4 行第 3 列必须写 b(4,3)。

## 示例

创建并输出一个数组：

```
Create ReportFile aReport
Create Variable i idx1 idx2
Create Array fib[9]

BeginMissionSequence

fib(1) = 0
fib(2) = 1
For i=3:9
   idx1 = i-1
   idx2 = i-2
   fib(i) = fib(idx1) + fib(idx2)
EndFor
Report aReport fib
```

说明：创建 9 元素行向量 fib，先写入斐波那契数列的前两项 0 和 1，再用 For 循环逐项计算 fib(i) = fib(i-1) + fib(i-2)（通过变量 idx1、idx2 作下标），最后把整个数组写入报告文件。
