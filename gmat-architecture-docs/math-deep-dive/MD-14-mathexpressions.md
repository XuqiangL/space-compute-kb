# 第14章 脚本数学表达式引擎数学

本章范围：`src/base/math/` 目录下全部 54 对 `.hpp` / `.cpp` 文件，聚焦**脚本数学表达式引擎**（以 `MathNode` 为根的表达式树）中每个内置函数的**数学定义**（公式）、**求值机制**（`Evaluate`/`MatrixEvaluate` 递归、`ValidateInputs`/`GetOutputInfo` 类型与维度传播）以及**与 ElementWrapper/参数系统的桥接**。体系结构层面的讲解（继承体系、`MathTree`/`MathParser` 组装流程、`MathFactory` 工厂）已在[第3章](../CH03-math.md)覆盖，本章不再重复，只做相对链接引用。

> **公式来源纪律**：本章每一条公式均从 `Evaluate()`/`MatrixEvaluate()` 的代码实现及其委托的底层数值函数（`src/gmatutil/util/RealUtilities.cpp`、`RandomNumber.cpp`、`Rmatrix.cpp`、`Rvector.cpp`、`Rvector3.cpp`）中提炼，全部行号都经 read 验证，禁止凭记忆编造。

---

## 一、表达式树求值机制（基础设施类）

### 1.1 MathNode —— 表达式树节点抽象基类（协议根）

- **公式**：无（协议类，不参与数值计算）。
- **代码位置**：`src/base/math/MathNode.hpp:40`（类声明），`src/base/math/MathNode.cpp:45-56`（构造器）、`:127-131`（`SetRealValue`）、`:136-155`（`SetMatrixValue`）。
- **深度讲解**：`MathNode` 直接继承 `GmatBase`，是表达式树中一切节点（叶、运算符、函数）的公共协议。六个纯虚函数构成求值契约：

```cpp
// MathNode.hpp:73-80（节选）
virtual bool         ValidateInputs() = 0;                 // 求值前的类型/维度校验（轻量“编译期”检查）
virtual void         GetOutputInfo(Integer &type,          // 输出类型 + 行列数推导（维度传播）
                                   Integer &rowCount, Integer &colCount) = 0;
virtual Real         Evaluate() = 0;                       // 标量求值入口（递归）
virtual Rmatrix      MatrixEvaluate() = 0;                 // 矩阵求值入口（递归）
virtual bool         SetChildren(MathNode *leftChild, MathNode *rightChild) = 0; // 组装二叉子树
virtual MathNode*    GetLeft() = 0;                        // 取左子树
virtual MathNode*    GetRight() = 0;                       // 取右子树
```

- 求值采用**后序遍历递归**：`MathTree::Evaluate()`（`src/base/interpreter/MathTree.cpp:368-376`）只做一行 `return theTopNode->Evaluate();`，由顶层节点逐层下推，叶节点（`MathElement`）取回实时值后自底向上合成结果；`MatrixEvaluate` 同理（`MathTree.cpp:382-390`）。树的组装与初始化见 [第3章 §2.1](../CH03-math.md)。
- 数据成员三标记：`isNumber`（字面量）、`isFunction`（函数节点）、`isFunctionInput`（函数实参，交 `FunctionRunner` 处理）；`elementType` 区分 `Gmat::REAL_TYPE` 与 `Gmat::RMATRIX_TYPE`。
- 构造器把 `realValue`/`stringValue` 初始化为 `REAL_PARAMETER_UNDEFINED`/`STRING_PARAMETER_UNDEFINED`（`MathNode.cpp:51-52`），保证“未赋值”可被识别。
- **实测缺陷提示**：复制构造函数 `MathNode.cpp:87` 写的是 `isFunctionInput (mn.isFunction)`，把函数输入标记错赋成了函数标记（应为 `mn.isFunctionInput`）；赋值运算符 `MathNode.cpp:115` 则正确。两处不一致，复制粘贴隐患，读代码时注意（已在 [第3章](../CH03-math.md) 指出）。

### 1.2 MathFunction —— 二叉运算节点基类

- **公式**：无（提供通用校验与维度推导工具）。
- **代码位置**：`src/base/math/MathFunction.hpp:39`（类声明）、`:56-57`（成员 `leftNode/rightNode`）；`src/base/math/MathFunction.cpp:142-155`（`SetChildren`）、`:179-200`（`GetScalarOutputInfo`）、`:207-240`（`GetMatrixOutputInfo`）、`:251-298`（`ValidateScalarInputs`）、`:309-351`（`ValidateMatrixInputs`）。
- **深度讲解**：约 34 个一元/二元函数类的公共基类，把「维度/类型检查」与「数值计算」分离——校验集中在基类，子类 `Evaluate()` 只写数值公式。

```cpp
// MathFunction.cpp:142-155  SetChildren：允许左子为空（支持一元 +、一元 - 等）
bool MathFunction::SetChildren(MathNode *leftChild, MathNode *rightChild)
{
   if (leftChild)          // 左子非空则绑定
      leftNode = leftChild;
   else
      leftNode = NULL;     // 左子为空：一元函数（如 sin(x) 把 x 放左子、右子留空）
   if (rightChild)         // 右子同理
      rightNode = rightChild;
   else
      rightNode = NULL;
   return true;
}
```

- `GetScalarOutputInfo`（`MathFunction.cpp:179-200`）：输出固定为 1×1 `REAL_TYPE`；注释特别说明「1×1 矩阵按标量返回」（`ArrayWrapper::EvaluateReal()` 会把 1×1 矩阵折成实数）。`GetMatrixOutputInfo`（`:207-240`）：输出行列取左节点的**转置**（`rowCount=col1; colCount=row1`），供 `Transpose` 这类“单输入、输出转置”函数复用；`allowScalarInput=false` 时左子非 `RMATRIX_TYPE` 直接抛异常。
- `ValidateScalarInputs`（`:251-298`）：要求左子（及右子）为 `REAL_TYPE` 或 1×1 矩阵，否则抛 `MathException`。**实测缺陷提示**：`:279` 校验右子时误写为 `leftNode->GetOutputInfo(...)`（应为 `rightNode`），即右子类型实际未校验；功能上被 `GetOutputInfo` 的维度合并逻辑兜住，但属明显笔误。
- `ValidateMatrixInputs(bool allowScalarInput)`（`:309-351`）：要求输入为矩阵；`allowScalarInput=true` 时放行标量（供 `Norm`、`Inverse` 复用）。
- 基类 `Evaluate`/`MatrixEvaluate`（`MathFunction.cpp:124-136`）直接抛 `MathException`（“cannot return Real/Matrix”），强制子类覆写；未覆写 `MatrixEvaluate` 的子类（如全部三角函数）在矩阵语境下会得到明确报错而非静默错误。

### 1.3 MathElement —— 叶节点（字面量 / 参数 / 数组绑定）

- **公式**：无（值是外部注入的，叶节点本身只做取值）。
- **代码位置**：`src/base/math/MathElement.hpp:44`（类声明）、`:86-95`（成员）；`src/base/math/MathElement.cpp:53-83`（构造器）、`:173-270`（`GetOutputInfo`）、`:299-358`（`Evaluate`）、`:364-418`（`MatrixEvaluate`）、`:766-843`（`SetWrapperObject`）、`:853-889`（`FindWrapper`）。
- **深度讲解**：表达式树最末端的“值来源”。构造器用 `GmatStringUtil::ToReal` 判断名字能否解析为实数——能则登记为字面量，不能则记为参数引用：

```cpp
// MathElement.cpp:68-77（构造器节选）
Real rval;
if (GmatStringUtil::ToReal(name, &rval))   // 名字能转成实数 → 字面量
{
   SetRealValue(rval);                     // 缓存标量值
   SetNumberFlag(true);                    // 标记 isNumber
}
else
{
   SetRefObjectName(Gmat::PARAMETER, name); // 否则当作 Parameter/Array 的引用名
}
```

- **实时取值**：`Evaluate()` 中若 `refObject` 非空，经 `FindWrapper(refObjectName)`（`MathElement.cpp:322`）在 `theWrapperMap` 里找到 `ElementWrapper` 后调用 `wrapper->EvaluateReal()`（`:332`）取 **Sandbox 实时值**——不是构造期缓存的初值。`SetWrapperObject` 在 `SetRefObject` 阶段（`MathElement.cpp:619-634` → `:766`）只缓存初值（`matrix = arr->GetRmatrix()` 于 `:821`、`realValue = refObject->GetReal()` 于 `:833`），保证循环/积分过程中参数变化能反映到表达式。
- `GetOutputInfo`（`:173-270`）是**维度传播的起点**：绑定 `Array` 时用 `GmatStringUtil::GetArrayIndexVar` 解析 `(row,col)` 下标（`:229`）；整组引用（`rowStr=="-1" && colStr=="-1"`，`:242-249`）返回真实行列数，单元素引用退化为 1×1 标量（`:251-256`）。数组“切片”`a(:,1)` 的注释（`:236-239`）表明是预留能力。
- `MatrixEvaluate`（`:364-418`）：`RMATRIX_TYPE` 走 `wrapper->EvaluateArray()`（`:390`）；标量分支先调 `Evaluate()` 再包装成 1×1 `Rmatrix`（`:414`）。
- `RenameRefObject`（`:462-560`）：对 `refObjectName`、`wrapperObjectNames` 及整个 `theWrapperMap` 做对象改名同步，用临时 `tempMap` + `swap`（`:513`、`:548-549`）避免迭代中修改原 map。
- **与参数系统的桥接**：`FindWrapper`（`:853-889`）是叶节点与「Sandbox 中的实时数据」之间的唯一通道——查不到名字或 wrapper 为 NULL 都抛 `MathException`。

### 1.4 BuiltinFunctionNode —— 多参数函数节点基类（第二代）

- **公式**：无（通用参数解析与 wrapper 装配）。
- **代码位置**：`src/base/math/BuiltinFunctionNode.hpp:37`（类声明）、`:62-71`（成员）；`src/base/math/BuiltinFunctionNode.cpp:51-108`（构造器）、`:162-212`（`SetMathWrappers`）、`:330-344`（`ValidateWrappers`）。
- **深度讲解**：2016 年新增的第二代函数节点基类（作者 Linda Jun），与 `MathFunction` 的「二叉左/右子树」不同，用**参数名字列表 + `ElementWrapper` 数组**表达 `FuncName(arg1, arg2, …)` 形式的多参数函数。构造器解析原始调用文本 `desc`：

```cpp
// BuiltinFunctionNode.cpp:65-101（构造器节选：解析参数列表）
StringArray items = GmatStringUtil::DecomposeBy(desc, "(");  // 按 '(' 切开函数名与参数区
if (items.size() == 2)
{
   std::string args = GmatStringUtil::RemoveLastString(items[1], ")"); // 去掉尾部 ')'
   args = GmatStringUtil::Trim(args);                        // 去空白，兼容 "MyFunc( [a b c])"
   if (GmatStringUtil::IsEnclosedWithBrackets(args))         // 向量形式 [1 2 3]
   {
      StringArray argList = GmatStringUtil::SeparateBrackets(args, "[]", " ,;", true);
      for (unsigned int i = 0; i < argList.size(); i++)
      {
         inputNames.push_back(argList[i]);                   // 记录每个实参名
         inputArgWrappers.push_back(NULL);                   // 占位，待 SetMathWrappers 填充
      }
   }
   else
   { /* SeparateByComma(args) 走逗号分隔分支，逻辑同上 */ }
}
```

- `SetMathWrappers`（`:162-212`）遍历 `theWrapperMap`，把与 `inputNames` 同名的 `ElementWrapper` 指针按索引填入 `inputArgWrappers`——这是第二代节点与 Sandbox 实时数据的桥接点（第一代走 `MathElement`，第二代直接持有 wrapper 数组）。
- `ValidateWrappers`（`:330-344`）：逐一检查 `inputArgWrappers[i]` 非 NULL，否则抛 `MathException`，在每次求值前由子类调用。
- 基类 `Evaluate`/`MatrixEvaluate`（`:218-230`）抛异常，`SetChildren`（`:236-239`）抛「not valid for BuiltinFunctionNode」——该家族不属于二叉树。

### 1.5 NumericFunctionNode / StringFunctionNode —— 数值 / 字符串函数中间基类

- **代码位置**：`src/base/math/NumericFunctionNode.cpp:111-132`（`ValidateInputs`）、`:137-156`（`GetOutputInfo`）；`src/base/math/StringFunctionNode.cpp:110-148`（`ValidateInputs`）、`:153-172`（`GetOutputInfo`）、`:177-198`（`ValidateWrappers`）。
- **深度讲解**：两个中间基类把「输出类型」固定下来，子类只需写求值：
  - `NumericFunctionNode::GetOutputInfo` 固定输出 `REAL_TYPE`、1×1（`NumericFunctionNode.cpp:146-148`）；`ValidateInputs` 是空实现直接返回 true（`NumericFunctionNode.cpp:119-131`）——注意这**不是**“跳过校验”的意思，而是数值函数家族把校验放在各子类 `Evaluate()` 的 wrapper 检查里（如 `Mod` 检查 `inputArgWrappers.size() != 2`）。
  - `StringFunctionNode::GetOutputInfo` 固定输出 `Gmat::STRING_TYPE`（`StringFunctionNode.cpp:162`）；`ValidateInputs` 检查调用文本语法（有参数、有右括号，`StringFunctionNode.cpp:121-139`）；`ValidateWrappers`（`:177-198`）在基类非空检查之上，要求**第一个输入 wrapper 是字符串类型**，否则抛异常。
- 派生关系：`Cross3`、`Diag`、`Min`、`Mod` 属 `NumericFunctionNode`；`Sprintf`、`Strcat`、`Strcmp`、`Strfind`、`Strlen`、`Strrep`、`Substr` 属 `StringFunctionNode`。其中 `Strcmp`/`Strfind`/`Strlen` 覆写 `GetOutputInfo` 改回 `REAL_TYPE`（见 §3.7），返回的是数值而非字符串。

### 1.6 FunctionRunner —— 表达式内联调用 GmatFunction

- **公式**：无（委托执行）。
- **代码位置**：`src/base/math/FunctionRunner.hpp:42`（类声明）、`:88-98`（成员）；`src/base/math/FunctionRunner.cpp:67-76`（构造器）、`:292-327`（`SetGlobalObjectMap`）、`:435-538`（`GetOutputInfo`）、`:575-654`（`Evaluate`）、`:665-717`（`MatrixEvaluate`）、`:727-779`（`EvaluateObject`）、`:813-852`（`FindObject`）、`:861-953`（`HandlePassingMathExp`）。
- **深度讲解**：让脚本数学表达式能直接调用用户 `GmatFunction`，例如 `x = MyFunc(a,b) + 1`。它是 `MathFunction` 派生类（保持二叉树外形），但求值把控制权交给内嵌的 `FunctionManager`。

```cpp
// FunctionRunner.cpp:613-640（Evaluate 核心节选）
Real result = -9999.9999;                       // 哨兵初值
theFunctionManager.SetInternalCoordinateSystem(internalCS); // 补设内部坐标系（临时修复）
result = theFunctionManager.Evaluate(callingFunction);     // 核心一行：委托 FunctionManager 执行
WrapperArray wrappersToDelete = theFunctionManager.GetWrappersToDelete();
for (WrapperArray::iterator ewi = wrappersToDelete.begin();
     ewi < wrappersToDelete.end(); ewi++)       // 回收函数输出 wrapper，防内存泄漏
{
   if ((*ewi) != NULL)
   {
      delete (*ewi);                            // 删除输出 wrapper
      (*ewi) = NULL;
   }
}
return result;
```

- `GetOutputInfo`（`:435-538`）：从 `function->GetOutputTypes(rowCounts, colCounts)`（`:450`）推断返回值——`VARIABLE_WT`→`REAL_TYPE` 1×1（`:465-470`）、`ARRAY_WT`→`RMATRIX_TYPE` 按真实行列（`:471-477`）、`OBJECT_WT`→`OBJECT_TYPE`（`:478-483`），并要求函数**恰好返回一个值**（`outputTypes.size()>1` 抛异常，`:458-462`）。
- `SetGlobalObjectMap`（`:292-327`）：用 `FindObject(theFunctionName)` 在对象表里找到 `Function` 对象并 `SetFunction`（`:303`、`:318-319`），找不到抛异常。
- `FindObject`（`:813-852`）：先剥掉 Array 下标后缀 `name.find('(')`（`:818-820`），然后**先查局部对象表（LOS）再查全局对象表（GOS）**（`:843-849`）——GMAT 作用域规则的体现。
- `HandlePassingMathExp`（`:861-953`）被 `#ifdef __ALLOW_MATH_EXP_NODE__` 整体包裹（当前未启用），是「向函数传整棵表达式子节点」的半成品（`@todo` 标注，`:858`），属于预留能力而非现役路径。

### 1.7 EquationWrapper —— 方程包装（CSALT 桥接）

- **代码位置**：`src/base/math/EquationWrapper.hpp:40`（类声明，注意它**不在** `MathNode` 体系内，而是 `ElementWrapper` 的派生类）；`src/base/math/EquationWrapper.cpp:40-63`（构造器）、`:179-223`（`Initialize`）、`:234-237`（`ConstructTree`）、`:277-310`（`EvaluateEquation`）、`:325-353`（`EvaluateReal`）。
- **深度讲解**：2018 年（CSALT 采购合同）新增，把一段方程字符串包装成 `ElementWrapper`，供优化/CSALT 在标准参数框架里读写方程结果。
  - 构造器以 `wrapperType = Gmat::EQUATION_WT` 注册（`EquationWrapper.cpp:52`）；`ConstructTree` 调 `theTree.BuildExpression(theEquation, configObjectMap, true)`（`:236`）——复用 `RHSEquation`（即 `MathTree` 的外层封装）把方程文本解析成表达式树。
  - `Initialize`（`:179-223`）跑一遍 `theTree.GetMathTree(false)->GetOutputInfo(type, rows, cols)` 定出 `dataType`。
  - `EvaluateEquation`（`:277-310`）调 `theTree.RunMathTree(NULL)` 得到 `resultant` wrapper（`:286`），仅当 `dataType == REAL_TYPE` 且返回类型一致时置 `hasEvaluated = true`；`EvaluateReal`（`:325-353`）则从 `resultant->EvaluateReal()` 取实数结果。
  - 字符串/Rvector/Rmatrix 返回被注释禁用（`EquationWrapper.cpp:79-81`、`:403-412`），当前只支持 Real。

### 1.8 MathException —— 子系统异常

- **代码位置**：`src/base/math/MathException.hpp:37`（类声明：`public BaseException`）；`src/base/math/MathException.cpp:43-46`（构造器，消息前缀 `"Math Exception: "`）。
- **深度讲解**：表达式引擎所有错误（缺参、维度不匹配、非法类型、wrapper 缺失）统一抛此异常，经 `BaseException` 汇入 GMAT 异常体系，由命令执行层捕获并转成脚本报错文本。

---

## 二、内置函数数学定义

> 通用模板说明（下述每个 `MathFunction` 派生类都相同）：构造器以类名注册（如 `Add::Add(const std::string &nomme) : MathFunction("Add", nomme)`），`Clone()` 返回 `new X(*this)`，`GetOutputInfo`/`ValidateInputs` 做维度与类型检查，`Evaluate`/`MatrixEvaluate` 写数值公式。以下只列每个函数**与众不同**之处与数学定义。脚本级函数名到类的映射见 `src/base/factory/MathFactory.cpp:117-234`（`CreateMathNode`）与 `:334-397`（`BuildCreatables`），如 `"cross"→Cross3`、`"det"→Determinant`、`"inv"→Inverse`、`"transpose"→Transpose`、`"Deg2Rad"→DegToRad`（`:175-212`）。

### 2.1 算术运算符

#### Add（加法，含一元 +）

- **公式**：

$$a + b = \sum_{i,j} (a_{ij} + b_{ij}) \quad\text{（矩阵逐元素加）}$$

标量—矩阵混合时按“广播”处理：1×1 与 M×N 相加，结果取 M×N；一元 `+x` 直接返回 `x`（`Add.cpp:252-255`）。矩阵加法由 `Rmatrix::operator+`（`src/gmatutil/util/Rmatrix.cpp:296`）逐元素实现。

- **代码位置**：`src/base/math/Add.cpp:242-256`（`Evaluate`）、`:267-295`（`MatrixEvaluate`）、`:102-172`（`GetOutputInfo` 维度合并）、`:183-231`（`ValidateInputs`）。
- **深度讲解**：`Evaluate` 直接 `leftNode->Evaluate() + rightNode->Evaluate()`（`Add.cpp:253`），无维度检查——检查在 `GetOutputInfo`/`ValidateInputs` 阶段完成：先要求两子节点维度相同或其一为 1×1（`Add.cpp:142-158`），`ValidateInputs` 再放行「任一侧 1×1」或「两矩阵同维」（`Add.cpp:213-222`）。`MatrixEvaluate` 按三种类型组合分派：矩阵+矩阵（`Add.cpp:284-285`）、矩阵+标量（`:286-287`）、标量+矩阵（`:288-289`），靠 `Rmatrix` 与 `Real` 的运算符重载完成逐元素加法。注意 `Add` 是唯一允许 `leftNode==NULL` 的二元类（一元 `+`，`Add.cpp:111-113`、`:252-255`）。

#### Subtract（减法）

- **公式**：

$$a - b = \sum_{i,j} (a_{ij} - b_{ij})$$

标量—矩阵混合同 `Add`（1×1 广播）；矩阵减法由 `Rmatrix::operator-` 逐元素实现。

- **代码位置**：`src/base/math/Subtract.cpp:237-247`（`Evaluate`）、`:258-282`（`MatrixEvaluate`）、`:102-165`（`GetOutputInfo`）、`:176-226`（`ValidateInputs`）。
- **深度讲解**：与 `Add` 完全同构（维度合并逻辑几乎逐行相同，`Subtract.cpp:135-158`），但**不允许一元减**——`GetOutputInfo` 对缺失子节点直接抛异常（`Subtract.cpp:110-118`）；一元取负由独立类 `Negate` 表达。`Evaluate` 内先调 `ValidateInputs()` 再相减（`Subtract.cpp:243-244`），是少数在求值期再做一次校验的类。

#### Multiply（乘法，矩阵乘法语义）

- **公式**（矩阵乘法，行×列约定）：

$$(AB)_{ij} = \sum_{k=1}^{n} A_{ik} B_{kj}, \qquad A \in \mathbb{R}^{m\times n},\ B \in \mathbb{R}^{n\times p}$$

标量—矩阵混合为逐元素数乘 $cA$；两标量相乘为普通实数积。矩阵乘法由 `Rmatrix::operator*`（`src/gmatutil/util/Rmatrix.cpp:418`）实现。

- **代码位置**：`src/base/math/Multiply.cpp:278-336`（`Evaluate`）、`:347-382`（`MatrixEvaluate`）、`:101-172`（`GetOutputInfo`）、`:183-267`（`ValidateInputs`）。
- **深度讲解**：维度传播是核心看点。`GetOutputInfo` 默认取左子维度，仅当两子都是矩阵时按内积规则推导：`col1 == row2` → 输出 $m\times p$（`Multiply.cpp:135-141`）；否则若任一为 1×1 则输出取另一个的维度（`:144-154`）；都不满足抛「Inner matrix dimensions must agree」（`:156-157`）。`MatrixEvaluate` 三分派（`:364-373`）：矩阵×矩阵、标量×矩阵、矩阵×标量，直接复用 `Rmatrix` 运算符重载。`Evaluate`（标量语境）只对「结果为 1×1」的情况取值：两标量相乘（`:292-295`）、1×1 矩阵×标量/标量×1×1 矩阵（`:296-313`）、乃至 $1\times n$ 行向量乘 $n\times 1$ 列向量退化为标量（`:314-322` 取 `GetElement(0,0)`）——这是 `dot(a,b)` 效果在 `Multiply` 内的等价实现。

#### Divide（除法）

- **公式**：

$$\frac{a}{b} = a \cdot b^{-1} \quad\text{标量：直接 } a / b$$

矩阵除法**不是** $A B^{-1}$：`Rmatrix::operator/`（`src/gmatutil/util/Rmatrix.cpp:518`）做的是逐元素除法 $a_{ij}/b_{ij}$（要求同维或 1×1 广播），不是矩阵求逆。标量/矩阵仅当矩阵为 1×1 时允许（`Divide.cpp:240-246` 抛「Cannot divide a scalar by a matrix」）。

- **代码位置**：`src/base/math/Divide.cpp:267-282`（`Evaluate`）、`:293-328`（`MatrixEvaluate`）、`:101-164`（`GetOutputInfo`）、`:175-256`（`ValidateInputs`）。
- **深度讲解**：`Evaluate` 只做 `leftNode->Evaluate() / rightNode->Evaluate()`（`Divide.cpp:275`），除零保护依赖底层浮点语义。维度规则：矩阵÷矩阵要求同维或 1×1 广播（`Divide.cpp:229-237`）；矩阵÷标量放行（`:238-239`）；`GetOutputInfo` 同样支持 1×1 一侧广播（`:136-151`）。**注意与数学惯例的差异**：脚本里矩阵求逆请用 `inv()`（`Inverse` 类），`/` 不是逆运算。

#### Negate（一元取负）

- **公式**：

$$-a = -a \qquad \text{（逐元素取负，矩阵亦同）}$$

- **代码位置**：`src/base/math/Negate.cpp:153-156`（`Evaluate`）、`:162-165`（`MatrixEvaluate`）、`:98-111`（`GetOutputInfo`）、`:122-142`（`ValidateInputs`）。
- **深度讲解**：实现即 `leftNode->Evaluate() * -1`（`Negate.cpp:155`）与 `leftNode->MatrixEvaluate() * -1`（`:164`）——用标量乘法实现取负，复用 `Rmatrix::operator*(Real)`（`Rmatrix.cpp:700`）。`ValidateInputs` 只要求输入是任意数值类型（REAL 或 RMATRIX，`Negate.cpp:133`），输出维度原样透传（`:108-110`）。

#### Power（幂）

- **公式**：

$$x^y = \operatorname{pow}(x, y)$$

（标准 C 库 `pow`，`src/gmatutil/util/RealUtilities.cpp:1019-1022`。）

- **代码位置**：`src/base/math/Power.cpp:193-196`（`Evaluate`）、`:98-137`（`GetOutputInfo`，仅 `GetScalarOutputInfo`）、`:148-182`（`ValidateInputs`）。
- **深度讲解**：只支持**标量**（含 1×1 矩阵）：底数/指数必须为 `REAL_TYPE` 或 1×1 矩阵（`Power.cpp:163-172`），且只实现 `Evaluate`——`MatrixEvaluate` 走基类抛「cannot return Matrix」。`GetOutputInfo` 里旧版维度检查整段被 `#if 0` 注释掉（`:102-136`），说明维度推导后来被简化到 `GetScalarOutputInfo`（`Power.cpp:100`）。脚本里 `x^y` 与 `Power(x,y)` 同义（`MathFactory.cpp:171-172`）。

#### Mod（取模）

- **公式**：

$$\operatorname{mod}(a,b) = a - b\left\lfloor \frac{a}{b} \right\rfloor, \qquad b \ne 0$$

实现见 `src/gmatutil/util/RealUtilities.cpp:120-127`。这是**被除数符号相关**的取模（结果符号与 $a$ 一致），区别于 `Rem` 的截断式 `a - Integer(a/b)*b`（`RealUtilities.cpp:132-139`）。

- **代码位置**：`src/base/math/Mod.cpp:123-158`（`Evaluate`，核心 `:151`）、构造器 `:48-51`（`NumericFunctionNode("Mod", name)`）。
- **深度讲解**：第二代多参数节点，`Evaluate` 先校验 `inputArgWrappers.size() == 2`（`Mod.cpp:132-133`），再从两个 wrapper 取实数值（`Mod.cpp:148-149`）委托 `GmatMathUtil::Mod`。除零由 `GmatMathUtil::Mod` 抛 `ArgumentError`（`RealUtilities.cpp:122-125`）。脚本语法为 `mod(a, b)`（`MathFactory.cpp:169-170`）。

#### Min（最小值）

- **公式**：

$$\min(a_1, a_2, \ldots, a_n) = \min_{1\le k\le n} a_k$$

- **代码位置**：`src/base/math/Min.cpp:122-164`（`Evaluate`，核心比较循环 `:149-156`）、构造器 `:48-51`。
- **深度讲解**：多参数数值函数，参数个数 ≥1（`Min.cpp:133-135`）。线性扫描：`i==0` 时以第一个参数为初值（`Min.cpp:149-150`），其后逐参数比较、遇更小值更新（`:153-155`）。注意 GMAT 脚本中二元 `min(a,b)` 走此节点；参数个数任意（可变参数），这是第一代二叉 `MathFunction` 无法表达的，正是 `BuiltinFunctionNode` 家族存在的意义。

### 2.2 矩阵与向量函数

#### Determinant（行列式）

- **公式**：

$$\det(A) = \begin{cases} a_{11} & n=1 \\ a_{11}a_{22} - a_{12}a_{21} & n=2 \\ \sum_{j=1}^{n} a_{1j}\, C_{1j} & n\ge 3 \end{cases}$$

其中 $C_{1j}$ 为第一行第 $j$ 列的代数余子式（余子式展开，按第一行）；$n>9$ 时改用 LU 分解（`src/gmatutil/util/Rmatrix.cpp:980-983`）。具体 3×3 展开式（Sarrus）见 `Rmatrix.cpp:970-975`。

- **代码位置**：`src/base/math/Determinant.cpp:160-173`（`Evaluate`，核心 `:167`）、`:100-111`（`GetOutputInfo` 固定 1×1 REAL）、`:122-149`（`ValidateInputs`）。
- **深度讲解**：`Evaluate` 先查左子类型：矩阵走 `(leftNode->MatrixEvaluate()).Determinant()`（`Determinant.cpp:165-168`，委托 `Rmatrix::Determinant`，`Rmatrix.cpp:937-1009`）；标量输入则原样返回（`Determinant.cpp:170-172`）——即 `det(scalar)=scalar`。`ValidateInputs` 要求方阵（`Determinant.cpp:145-146` 抛「only supports a square matrix」）；非方阵与非数值输入都抛 `MathException`。脚本语法 `det(m)`（`MathFactory.cpp:177-178`）。

#### Inverse（矩阵 / 标量求逆）

- **公式**：

$$A^{-1}: \quad A A^{-1} = A^{-1} A = I, \qquad \det(A) \ne 0$$

标量输入时 $x^{-1} = \operatorname{pow}(x, -1) = 1/x$（`src/base/math/Inverse.cpp:148`）。矩阵求逆算法为**全选主元 Gauss-Jordan 消元**（`Rmatrix.cpp:1097-1228`）：每步在未使用过的行/列里挑模最大元素作主元（`Rmatrix.cpp:1164-1181`），主元行归一化并交换到主元列（`:1190-1199`），对其余行消元（`:1202-1213`），最后按记录的行列交换顺序复原（`:1217-1226`）；对角矩阵走快速分支直接逐元取倒数（`Rmatrix.cpp:1125-1141`）。

- **代码位置**：`src/base/math/Inverse.cpp:146-149`（`Evaluate` 标量分支）、`:159-192`（`MatrixEvaluate`，核心 `:187`）、`:98-107`（`GetOutputInfo`）、`:117-136`（`ValidateInputs`）。
- **深度讲解**：唯一「标量/矩阵双返回类型」的类：`GetOutputInfo` 先假定 `RMATRIX_TYPE`，若左子为 1×1 则改报 `REAL_TYPE`（`Inverse.cpp:100-105`）。`ValidateInputs` 用 `ValidateMatrixInputs(true)` 放行标量（`:122`），再要求矩阵必须方阵（`:129-130`）。奇异矩阵由 `Rmatrix::Inverse` 抛 `IsSingular`（`Rmatrix.cpp:1183-1184`，主元绝对值小于 `zeroValue` 默认 $10^{-12}$，`Rmatrix.cpp:1234-1237`）。脚本语法 `inv(m)`（`MathFactory.cpp:181-182`）。

#### Norm（范数）

- **公式**（欧氏 2-范数）：

$$\|v\|_2 = \sqrt{\sum_{i} v_i^2}$$

标量输入时取绝对值 $\|x\| = |x|$。实现见 `src/gmatutil/util/Rvector.cpp:796-804`（`Norm()`：逐元平方求和再开方）。

- **代码位置**：`src/base/math/Norm.cpp:138-166`（`Evaluate`，行向量分支 `:145-148`、列向量分支 `:149-152`、标量分支 `:162-166`）、`:101-113`（`GetOutputInfo` 固定 1×1 REAL）、`:124-127`（`ValidateInputs`）。
- **深度讲解**：只接受**向量或标量**：行向量取 `GetRow(0).Norm()`（`Norm.cpp:147`），列向量取 `GetColumn(0).Norm()`（`:151`）；真正的矩阵（行、列都 >1）抛「Can only be done on a vector or a scalar」（`:153-159`），注释说明矩阵范数留待将来按需实现（`:154-156`）。标量分支返回 `GmatMathUtil::Abs(result)`（`:165`）。`ValidateInputs` 委托 `ValidateMatrixInputs(true)`（`:126`）允许矩阵/标量，真正的形状约束在 `Evaluate` 里做。

#### Transpose（转置）

- **公式**：

$$\left(A^{\mathsf T}\right)_{ij} = A_{ji}, \qquad A \in \mathbb{R}^{m\times n} \Rightarrow A^{\mathsf T} \in \mathbb{R}^{n\times m}$$

- **代码位置**：`src/base/math/Transpose.cpp:197-235`（`Evaluate`）、`:246-279`（`MatrixEvaluate`，核心 `:274`）、`:101-132`（`GetOutputInfo`）、`:143-186`（`ValidateInputs`）。
- **深度讲解**：`GetOutputInfo` 直接复用基类 `GetMatrixOutputInfo` 的“输出 = 左子转置”约定（`rowCount=col1; colCount=row1`，`Transpose.cpp:122-125`）；标量转置被允许（Bug 2186 修复，`:118-120` 注释）。`MatrixEvaluate` 委托 `Rmatrix::Transpose`（`Rmatrix.cpp:1072`）。`Evaluate` 特判：1×1 矩阵转置返回元素值（`Transpose.cpp:209-220`），标量转置原样返回（`:226-233`）。脚本语法 `transpose(m)` 或 `m'`（`MathFactory.cpp:189-190`）。

#### Cross3（三维叉积）

- **公式**（$\mathbb{R}^3$ 叉积）：

$$\vec{a}\times\vec{b} = \begin{pmatrix} a_2 b_3 - a_3 b_2 \\ a_3 b_1 - a_1 b_3 \\ a_1 b_2 - a_2 b_1 \end{pmatrix}$$

实现见 `src/gmatutil/util/Rvector3.cpp:387-393`（友元函数 `Cross`）。文件头注释（`Cross3.cpp:180-186`）给出了等价的脚本级 cross.gmf 定义，公式一致。

- **代码位置**：`src/base/math/Cross3.cpp:189-258`（`MatrixEvaluate`，核心 `:240`）、`:151-170`（`GetOutputInfo` 固定 1×3 RMATRIX）、`:123-146`（`ValidateInputs`）。
- **深度讲解**：第二代多参数节点，`MatrixEvaluate` 要求恰好两个参数（`Cross3.cpp:198-199`），两个输入都必须是 3 元素向量——3×1 或 1×3 均可（`:227-228`），按行/列形态分别取值填入 `Rvector3`（`:230-237`），调友元 `Cross(vec1, vec2)`（`:240`）后把结果写回 1×3 `Rmatrix result(1,3)`（`:196`、`:242-244`）。形态非法抛「Cross product requires two 3-element vectors」（`:248-249`）。注意输出固定为**行向量 1×3**（`GetOutputInfo` 注释「Output can be 1x3 or 3x1」，`:160`，实际实现取 1×3）。脚本语法 `cross(a,b)`（`MathFactory.cpp:175-176`）。

#### Diag（对角矩阵）

- **公式**：

$$\operatorname{diag}(d_1,\ldots,d_n) = \begin{pmatrix} d_1 & 0 & \cdots & 0 \\ 0 & d_2 & \cdots & 0 \\ \vdots & & \ddots & \vdots \\ 0 & 0 & \cdots & d_n \end{pmatrix}$$

- **代码位置**：`src/base/math/Diag.cpp:196-231`（`MatrixEvaluate`，对角填充 `:218-222`）、`:156-181`（`GetOutputInfo`）、`:131-151`（`ValidateInputs`）。
- **深度讲解**：第二代多参数节点，输入为向量形式 `diag([1 2 3])`（构造器按方括号解析出 3 个参数，`BuiltinFunctionNode.cpp:73-85`）。`GetOutputInfo` 以 `inputNames.size()` 定矩阵阶数（`Diag.cpp:170-173`，缓存到 `numRows/numCols`）。`MatrixEvaluate` 分配 $n\times n$ 零矩阵（`Rmatrix` 默认零初始化），循环只写 `i==j` 对角元素（`Diag.cpp:218-222`）。文件头注释（`Diag.cpp:188-193`）给出了 `diag([1 2 3])` 的期望输出。脚本语法 `diag([...])`（`MathFactory.cpp:179-180`）。

### 2.3 三角函数 / 反三角 / 双曲函数

> 本族全部为第一代 `MathFunction` 一元节点：参数放左子、右子为空。除 `Atan2` 外**只实现 `Evaluate`**（`MatrixEvaluate` 走基类抛「cannot return Matrix」）。所有委托的 `GmatMathUtil` 函数都带一个 `cycleInRad` 周期参数 $T$（默认 $2\pi$），缩放方向分两种：**正向函数**（`Sin/Cos/Tan/Sinh/Cosh/Tanh`）把自变量缩放为 $\frac{2\pi}{T}x$ 再调库函数；**反函数**（`Asin/Acos/Atan/Asinh/Acosh`）把库函数结果缩放为 $\frac{T}{2\pi}\cdot\operatorname{lib}(x)$。默认 $T=2\pi$ 时两者都退化为标准库函数本身。

#### Sin / Cos / Tan

- **公式**（`src/gmatutil/util/RealUtilities.cpp:319-325`、`:345-351`、`:356-362`）：

$$\sin x = \sin\!\left(\frac{2\pi}{T}x\right),\quad \cos x = \cos\!\left(\frac{2\pi}{T}x\right),\quad \tan x = \tan\!\left(\frac{2\pi}{T}x\right), \qquad T = 2\pi\ \text{(默认)}$$

默认周期下即标准正弦/余弦/正切；角度以**弧度**为单位。三个实现先检查 `cycleInRad <= 0` 抛 `ArgumentError`，再调标准库。

- **代码位置**：`src/base/math/Sin.cpp:125-128`（`Evaluate`）、`Cos.cpp:126-129`、`Tan.cpp:126-129`；三者的 `GetOutputInfo`/`ValidateInputs` 均为 `GetScalarOutputInfo` / `ValidateScalarInputs`（`Sin.cpp:100`、`:114`）。
- **深度讲解**：允许 1×1 矩阵作输入（`ValidateScalarInputs` 放行，`MathFunction.cpp:269-275`），输出固定 1×1 实数。脚本语法 `sin(x)` 等（`MathFactory.cpp:193-198`）。

#### Asin / Acos / Atan

- **公式**（`RealUtilities.cpp:407-431`、`:438-461`、`:467-473`）：

$$\arcsin x = \frac{T}{2\pi}\,\operatorname{asin}(x),\quad \arccos x = \frac{T}{2\pi}\,\operatorname{acos}(x),\quad \arctan x = \frac{T}{2\pi}\,\operatorname{atan2}(x, 1)$$

默认周期下即标准反正弦/反余弦/反正切（`GmatMathUtil::ATan(Real y, Real x=1.0, ...)` 单参调用等价于 $\operatorname{atan2}(x,1)$，见 `src/gmatutil/util/RealUtilities.hpp:98`）。反三角有**定义域容差处理**：$|x|>1$ 时若 $x\in(1-\epsilon,1+\epsilon]$ 返回 $\pi/2$（$\arcsin$，`RealUtilities.cpp:420-421`）或 $0$（$\arccos$，`:450-451`），$x\in(-1-\epsilon,-1+\epsilon]$ 返回 $-\pi/2$（`:422-423`）或 $\pi$（`:452-453`），否则抛「not within -1.0 and 1.0」。

- **代码位置**：`src/base/math/Asin.cpp:126-129`、`Acos.cpp:126-129`、`Atan.cpp:126-129`；三者 `GetOutputInfo`/`ValidateInputs` 同 `Sin` 系。
- **深度讲解**：`Atan.cpp` 单参调用 `GmatMathUtil::ATan(leftNode->Evaluate())`，靠头文件默认参数 `x=1.0` 绑定（`RealUtilities.hpp:98`）。输出单位弧度。其余同 `Sin` 系（标量或 1×1 矩阵输入，1×1 实数输出）。

#### Atan2（四象限反正切）

- **公式**：

$$\phi = \operatorname{atan2}(y, x), \qquad y = \text{left 子节点},\ x = \text{right 子节点}$$

返回值 $\phi\in(-\pi,\pi]$，由 $(x,y)$ 象限决定：$\phi=\arctan(y/x)$ 并修正到正确象限，$x=0, y>0$ 时 $\phi=\pi/2$。**注意实参顺序**：代码是 `atan2(leftNode->Evaluate(), rightNode->Evaluate())`，即**左子是 $y$、右子是 $x$**（`Atan2.cpp:160`）；类注释“returns the arc tangent of right node / left node”是误导性文字，以代码为准。

- **代码位置**：`src/base/math/Atan2.cpp:158-160`（`Evaluate`）、`:99-126`（`GetOutputInfo`，旧维度检查被注释）、`:137-146`（`ValidateInputs`）。
- **深度讲解**：与其它一元函数不同，`Atan2` 是**二元** `MathFunction`（左右子都用），且直接调用 C 库 `atan2`（`#include <math.h>`，`Atan2.cpp:33`）而非 `GmatMathUtil::ATan2`。`ValidateInputs` 委托 `ValidateScalarInputs`（`Atan2.cpp:145`）——注意基类该函数在 `:279` 有“左子重复校验”笔误，右子类型实际未查，但两个子节点都要求非 NULL（`:139-143`）。脚本语法 `atan2(y,x)`（`MathFactory.cpp:205-206`）。

#### Sinh / Cosh / Tanh

- **公式**（`RealUtilities.cpp:380-388`、`:367-375`、`:393-401`）：

$$\sinh x = \sinh\!\left(\frac{2\pi}{T}x\right),\quad \cosh x = \cosh\!\left(\frac{2\pi}{T}x\right),\quad \tanh x = \tanh\!\left(\frac{2\pi}{T}x\right)$$

即标准双曲函数（默认周期 $T=2\pi$）。三者的 `GmatMathUtil` 实现还额外检查 $\cos x \approx 0$ 时抛异常（`RealUtilities.cpp:371-372`、`:384-385`、`:397-398`）——历史遗留的保守检查。

- **代码位置**：`src/base/math/Sinh.cpp:149-151`、`Cosh.cpp:152-154`、`Tanh.cpp:149-151`。
- **深度讲解**：与 `Sin` 系不同，**严格要求 `REAL_TYPE` 输入**：`GetOutputInfo` 在 `type1 != Gmat::REAL_TYPE` 时抛「Left is not scalar」（`Sinh.cpp:105-106`、`Cosh.cpp:105-106`、`Tanh.cpp:105-106`），1×1 矩阵也不行；`ValidateInputs` 同（`Sinh.cpp:134-137`）。输出类型/维度透传左子（`Sinh.cpp:109-111`）。

#### Asinh / Acosh（反双曲）

- **公式**（`RealUtilities.cpp:491-507`、`:513-534`）：

$$\operatorname{arsinh}x = \frac{T}{2\pi}\,\operatorname{asinh}(x) \xlongequal{\text{MSVC 分支}} \frac{T}{2\pi}\,\ln\!\left(x+\sqrt{x^2+1}\right)$$

$$\operatorname{arcosh}x = \frac{T}{2\pi}\,\operatorname{acosh}(x) \xlongequal{\text{MSVC 分支}} \frac{T}{2\pi}\,\ln\!\left(x+\sqrt{x^2-1}\right),\quad x\ge 1$$

非 MSVC 平台直接调 C 库 `asinh`/`acosh`；MSVC 下用对数—根式恒等式手工实现（`RealUtilities.cpp:499-503`、`:523-529`，因为旧版 VC 无 `asinh`）。`Acosh` 对 $x<1$ 抛「undefined for input values < 1.0」（`:527-529`）。

- **代码位置**：`src/base/math/Asinh.cpp:149-151`、`Acosh.cpp:149-151`；二者 `GetOutputInfo`/`ValidateInputs` 同 `Sinh` 系（严格要求 `REAL_TYPE`，`Asinh.cpp:105-106`、`:134-137`）。
- **深度讲解**：`Asinh.cpp:127` 抛错信息误写为「RadToDeg() - Missing input arguments」——复制粘贴遗留，实际执行路径不受影响。输出单位弧度。

### 2.4 初等函数与取整

> 本族 8 个函数全部为 `MathFunction` 一元节点，`GetOutputInfo`/`ValidateInputs` 统一走 `GetScalarOutputInfo`/`ValidateScalarInputs`（允许 1×1 矩阵输入，输出 1×1 实数），只实现 `Evaluate`。**重要发现**：`MathFactory::BuildCreatables`（`MathFactory.cpp:334-397`）的 creatables 列表里，三角函数只登记到 `Atan2`（`:371-378`），**没有登记** `Sinh/Cosh/Tanh/Asinh/Acosh` 五个双曲函数类（`Ceil/Floor/Fix` 则登记于 `:350-353`）——即双曲函数类当前无法经工厂从脚本创建，属登记缺口（类本身完整，见 §2.3）。

#### Exp / Log / Log10 / Sqrt / Abs / Ceil / Floor / Fix（合并条目）

- **公式**（实现位置：`src/gmatutil/util/RealUtilities.cpp`）：

$$\operatorname{e}^{x} = \exp(x) \qquad\text{（`RealUtilities.cpp:993-996`）}$$

$$\ln x = \log(x),\quad \log_{10} x = \log_{10}(x), \qquad x > 0 \text{（`RealUtilities.cpp:582-588`、`:598-604`，输入 } \le 0 \text{ 抛异常）}$$

$$\sqrt{x} = \sqrt{x}, \qquad x \ge 0 \text{（`RealUtilities.cpp:974-983`，输入 } < 0 \text{ 抛异常）}$$

$$|x| = \operatorname{fabs}(x) \qquad\text{（`RealUtilities.cpp:64-67`）}$$

$$\lceil x \rceil = \operatorname{ceil}(x) \qquad\text{（`RealUtilities.cpp:112-115`）}$$

$$\lfloor x \rfloor = \operatorname{floor}(x) \qquad\text{（`RealUtilities.cpp:95-98`）}$$

$$\operatorname{fix}(x) = \operatorname{sgn}(x)\cdot\lfloor|x|\rfloor \qquad\text{（向零取整，`RealUtilities.cpp:103-107`）}$$

- **代码位置**：

| 函数 | 类文件 `Evaluate`（核心行） | 委托 |
|---|---|---|
| `Exp` | `src/base/math/Exp.cpp:126-129`（`:128`） | `GmatMathUtil::Exp` |
| `Log` | `src/base/math/Log.cpp:126-129`（`:128`） | `GmatMathUtil::Log`（自然对数） |
| `Log10` | `src/base/math/Log10.cpp:126-129`（`:128`） | `GmatMathUtil::Log10` |
| `Sqrt` | `src/base/math/Sqrt.cpp:125-128`（`:127`） | `GmatMathUtil::Sqrt` |
| `Abs` | `src/base/math/Abs.cpp:126-129`（`:128`） | `GmatMathUtil::Abs` |
| `Ceil` | `src/base/math/Ceil.cpp:126-129`（`:128`） | `GmatMathUtil::Ceiling` |
| `Floor` | `src/base/math/Floor.cpp:126-129`（`:128`） | `GmatMathUtil::Floor` |
| `Fix` | `src/base/math/Fix.cpp:126-129`（`:128`） | `GmatMathUtil::Fix` |

- **深度讲解**：定义域约束由 `GmatMathUtil` 层保证（`Log/Log10` 要求 $x>0$、`Sqrt` 要求 $x\ge 0$，否则抛 `ArgumentError`），节点层不做数学域检查。`Abs` 是标量绝对值，**没有**向量/矩阵范数语义（矩阵范数请用 `Norm`）。三个取整函数语义区分：`ceil` 向上、`floor` 向下、`fix` 向零（`fix(-3.7)=-3` 而 `floor(-3.7)=-4`）。脚本语法 `exp/log/log10/sqrt/abs/ceil/floor/fix`（`MathFactory.cpp:149-166`）。

### 2.5 单位换算

#### DegToRad（度 → 弧度）

- **公式**：

$$\theta_{\text{rad}} = \frac{\pi}{180}\,\theta_{\text{deg}}$$

换算因子 `RAD_PER_DEG = PI/180`，其中 `PI = 3.14159265358979323846264338327950288419716939937511`（`src/gmatutil/util/GmatConstants.hpp:186`、`:192-193`）。实现链：`DegToRad.cpp` → `GmatMathUtil::DegToRad`（`RealUtilities.cpp:281-284`）→ `GmatMathUtil::Rad`（`RealUtilities.cpp:260-266`）→ `RAD_PER_DEG * deg`。

- **代码位置**：`src/base/math/DegToRad.cpp:126-129`（`Evaluate`，核心 `:128`）、`:98-101`（`GetOutputInfo`）、`:112-115`（`ValidateInputs`）。
- **深度讲解**：`GmatMathUtil::DegToRad(deg, modBy2Pi=false)` 第二参数默认关闭“模 $2\pi$”归约；脚本节点调用时只传角度，因此不做角度归约。允许 1×1 矩阵输入（`ValidateScalarInputs`）。脚本别名 `DegToRad` 与 `Deg2Rad` 都映射到本类（`MathFactory.cpp:209-210`）。

#### RadToDeg（弧度 → 度）

- **公式**：

$$\theta_{\text{deg}} = \frac{180}{\pi}\,\theta_{\text{rad}}$$

换算因子 `DEG_PER_RAD = 180/PI`（`GmatConstants.hpp:194-195`）。实现链：`RadToDeg.cpp` → `GmatMathUtil::RadToDeg`（`RealUtilities.cpp:289-292`）→ `GmatMathUtil::Deg`（`RealUtilities.cpp:271-276`）→ `DEG_PER_RAD * rad`。

- **代码位置**：`src/base/math/RadToDeg.cpp:124-127`（`Evaluate`，核心 `:126`）、`:98-101`（`GetOutputInfo`）、`:112-115`（`ValidateInputs`）。
- **深度讲解**：与 `DegToRad` 互逆（默认无 360° 归约）。脚本别名 `RadToDeg` 与 `Rad2Deg` 都映射到本类（`MathFactory.cpp:211-212`）。

### 2.6 随机数

> 两类的**真随机源**在 `src/gmatutil/util/RandomNumber.cpp`：单例（`RandomNumber::Instance()`，`RandomNumber.cpp:52-57`）持有 C++11 `<random>` 引擎，构造器用 `std::random_device` 播种（`RandomNumber.cpp:268-279`）。`GmatMathUtil::Rand/Randn` 只是转发（`RealUtilities.cpp:642-646`、`:659-663`）。因此脚本里 `rand()`/`randn()` 每次运行序列不同，可用 `GmatMathUtil::SetSeed`（`RealUtilities.cpp:668-672`）固定种子（脚本级无直接命令，需经 C++ 侧）。

#### Rand（均匀随机数）

- **公式**：

$$u \sim U[a,b), \qquad u = a + (b-a)\,\xi,\quad \xi\sim U[0,1)$$

实现见 `RandomNumber.cpp:211-214`；基础样本 $\xi$ 由 `std::uniform_real_distribution` 产生并**拒绝恰好等于 1.0 的样本**（`RandomNumber.cpp:186-195` 的 do-while），保证半开区间 $[0,1)$。分布均值 $(a+b)/2$、方差 $(b-a)^2/12$（注释 `RandomNumber.cpp:202-204`）。

- **代码位置**：`src/base/math/Rand.cpp:186-208`（`Evaluate`，核心 `:200`）、`:219-247`（`MatrixEvaluate`）、`:258-315`（`GetOutputDimension`）、`:101-135`（`GetOutputInfo`）、`:146-180`（`ValidateInputs`）。
- **深度讲解**：`MathFunction` 系一元节点但**左子可空**：`rand()` 等价 `rand(1)`，返回单个 $U[0,1)$ 实数（`Rand.cpp:157-161`、`:200`）。若给整数参数 $n$（须为正整数，校验 `fabs(rval - round(rval)) < 0.000001`，`Rand.cpp:300-301`），则 `GetOutputInfo` 报 $n\times n$ 矩阵输出（`Rand.cpp:124-128`），`MatrixEvaluate` 填满 $n^2$ 个独立样本（`:235-237`）。`Evaluate` 里若输出维度 >1 抛「Left-hand-side of rand function is not an Array」（`:194-198`）——标量语境取 1×1 结果，矩阵语境走 `MatrixEvaluate`。脚本语法 `rand()`/`rand(n)`（`MathFactory.cpp:185-186`）。

#### Randn（高斯随机数）

- **公式**：

$$g \sim \mathcal{N}(\mu,\sigma^2), \qquad \mu=0,\ \sigma=1$$

实现为 `std::normal_distribution<double> Gauss(mean, stdev)` 的抽样（`RandomNumber.cpp:126-130`）；`Randn.cpp` 调用 `GmatMathUtil::Randn(0.0, 1.0)`（`Randn.cpp:200`），即标准正态 $\mathcal{N}(0,1)$。

- **代码位置**：`src/base/math/Randn.cpp:186-208`（`Evaluate`，核心 `:200`）、`:219-247`（`MatrixEvaluate`）、`:258-315`（`GetOutputDimension`）、`:101-135`（`GetOutputInfo`）、`:146-180`（`ValidateInputs`）。
- **深度讲解**：与 `Rand` 结构逐行同构（左子可空、正整数维度校验、$n\times n$ 矩阵填独立样本，`Randn.cpp:235-237`），差别只在采样函数（`Randn.cpp:231` vs `Rand.cpp:231`）。注释（`RandomNumber.cpp:102-106`、`RealUtilities.cpp:651-657`）说明“Gaussian（高斯）是正态的推广：零均值单位方差即正态”。脚本语法 `randn()`/`randn(n)`（`MathFactory.cpp:187-188`）。

### 2.7 字符串函数

> 本族全部为 `StringFunctionNode` 派生。共同机制（见 §1.5）：`GetOutputInfo` 默认报 `STRING_TYPE`，`ValidateWrappers` 要求首个输入为字符串；参数经 `inputArgWrappers` 取 `EvaluateString()`。**例外**：`Strcmp`、`Strfind`、`Strlen` 覆写 `GetOutputInfo` 为 `REAL_TYPE`（返回数值）。

#### Sprintf（格式化字符串）

- **公式**：无数学公式；等价于 C `sprintf` 的 GMAT 受限子集：

$$s = \texttt{format}\ \text{中每个}\ \texttt{\%spec}\ \text{被对应实参的格式化输出替换}$$

有效格式符：`%a %A %e %E %f %F %g %G`（浮点）与 `%s`（字符串）；`%c %d %i %o %u %x %X` 等**不支持**（`Sprintf.cpp:181-207` 注释）。支持 flags/width/precision 原型 `%[flags][width][.precision][length]specifier`，含可变宽度/精度 `*`。

- **代码位置**：`src/base/math/Sprintf.cpp:137-506`（`EvaluateString`；格式数校验 `:161-175`、格式解析 `:241-283`、逐实参格式化 `:297-478`、替换回写 `:480-489`）。
- **深度讲解**：实现要点：
  1. 用固定 30000 字符栈缓冲 `outBuffer`（`Sprintf.cpp:139-140`）；
  2. 先统计 `%` 与 `*` 个数，与实参个数不匹配抛异常（`:170-175`）；
  3. `SeparateBy(format, "%")` 切出格式片段（`:241`），`find_first_of("aAcdieEfFgGnopsuxX")` 定位格式符（`:257`），非法格式符抛异常（`:278-282`）；
  4. 对每个实参按数据类型分派：`REAL_TYPE` 校验格式符非整数类（`:394-401`）后调 C `sprintf`（`:405-410`），`STRING_TYPE` 只允许 `%s`（`:426-433`），其它类型转 `ToString()`（`:455`）；
  5. 最后用 `GmatStringUtil::ReplaceFirst` 把原格式串里的每个 spec 逐个替换为格式化结果（`:483-489`）。

```cpp
// Sprintf.cpp:384-415（REAL 分支核心节选）
switch (dataType)
{
case Gmat::REAL_TYPE:
   rval = wrapper->EvaluateReal();              // 取实数实参
   if (formatSpec.find_last_of("cdinopsuxX") != std::string::npos) // 整数类格式符对 Real 非法
      throw MathException(...);                 // 抛：Real 只允许 %a %A %e %E %f %F %g %G
   if (numStars == 2)                           // %*.*f：宽度+精度都来自实参
      retval = sprintf(outBuffer, formatSpec.c_str(), firstVal, secondVal, rval);
   else if (numStars == 1)                      // %*f：宽度来自实参
      retval = sprintf(outBuffer, formatSpec.c_str(), firstVal, rval);
   else                                         // 普通格式
      retval = sprintf(outBuffer, formatSpec.c_str(), rval);
   resultArray.push_back(outBuffer);            // 收集本实参的格式化输出
   break;
   // ...case Gmat::STRING_TYPE 只允许 %s，分支结构相同
```

- **代码位置**：`src/base/math/Sprintf.cpp:108-127`（`ValidateInputs`，仅委托基类）。
- 脚本语法 `sprintf(format, arg1, ...)`（`MathFactory.cpp:387`）。

#### Strcat（字符串拼接）

- **公式**：

$$\texttt{strcat}(s_1, s_2, \ldots, s_n) = s_1 s_2 \cdots s_n \quad\text{（直接串联，无分隔符）}$$

- **代码位置**：`src/base/math/Strcat.cpp:106-134`（`EvaluateString`，核心 `:125`）。
- **深度讲解**：逐参数 `result = result + wrapper->EvaluateString()`（`Strcat.cpp:125`），参数个数不限（≥1）；先 `ValidateWrappers()` 保证第一个是字符串。输出 `STRING_TYPE`（基类默认）。脚本语法 `strcat(a, b, 'literal')`（`MathFactory.cpp:388`）。

#### Strcmp（字符串比较）

- **公式**：

$$\texttt{strcmp}(s_1, s_2) = \begin{cases} 1 & s_1 = s_2 \\ 0 & s_1 \ne s_2 \end{cases}$$

- **代码位置**：`src/base/math/Strcmp.cpp:134-162`（`Evaluate`，比较 `:151-154`）、`:102-121`（`GetOutputInfo` 覆写为 `REAL_TYPE`）。
- **深度讲解**：恰好两个参数（`Strcmp.cpp:141-142`），`==` 全等比较（区分大小写），返回 1.0/0.0 实数——因此可写进数值表达式如 `if (strcmp(a,b) == 1)`。脚本语法 `strcmp(a, 'literal')`（`MathFactory.cpp:389`）。

#### Strfind（子串查找）

- **公式**：

$$k = \operatorname{strfind}(s, p) = \begin{cases} 1\text{-基起始下标} & p \subset s \\ -1 & p \not\subset s \end{cases}$$

实现：`s.find(p)` 返回 0 基位置后 **+1 修正为 1 基**（`Strfind.cpp:158-163`）。

- **代码位置**：`src/base/math/Strfind.cpp:133-175`（`Evaluate`，核心 `:148`、`:160-167`）、`:102-121`（`GetOutputInfo` 覆写为 `REAL_TYPE`）。
- **深度讲解**：恰好两个参数（`Strfind.cpp:140-141`）；返回**第一次**出现位置（`std::string::find` 语义），找不到返回 -1（`:166`）。1 基下标与 GMAT 数组下标约定一致。脚本语法 `strfind(a, 'literal')`（`MathFactory.cpp:390`）。

#### Strlen（字符串长度）

- **公式**：

$$L = \operatorname{strlen}(s) = |s| \quad\text{（字符数）}$$

- **代码位置**：`src/base/math/Strlen.cpp:158-182`（`Evaluate`，核心 `:174`）、`:127-146`（`GetOutputInfo` 覆写为 `REAL_TYPE`）。
- **深度讲解**：恰好一个参数（`Strlen.cpp:165-166`），`s1.length()` 即字节数（ASCII 场景等于字符数）。作者 Peter Candell，2024.07 新增（`Strlen.cpp:22-23`）。脚本语法 `strlen(a)`（`MathFactory.cpp:393`）。

#### Strrep（子串替换）

- **公式**：

$$\texttt{strrep}(s, s_{\text{old}}, s_{\text{new}}) = s\ \text{中所有}\ s_{\text{old}}\ \text{替换为}\ s_{\text{new}}$$

- **代码位置**：`src/base/math/Strrep.cpp:108-138`（`EvaluateString`，核心 `:130`）。
- **深度讲解**：恰好三个参数（`Strrep.cpp:115-116`），委托 `GmatStringUtil::Replace(str, oldStr, newStr, 0)`（`:130`）——**全部**出现（替换计数参数 0 表示不限次数）。输出 `STRING_TYPE`。脚本语法 `strrep(a, 'old', 'new')`（`MathFactory.cpp:391`）。

#### Substr（取子串）

- **公式**：

$$\texttt{substr}(s, \text{start}, \text{end}=\operatorname{strlen}(s)) = s[\text{start} : \text{end}) \quad\text{（左闭右开，0 基，闭区间语义见下）}$$

- **代码位置**：`src/base/math/Substr.cpp:126-187`（`EvaluateString`，核心 `:179`）、`:141-171`（参数解析与校验）、`:173-177`（越界校验）。
- **深度讲解**：2 或 3 个参数（`Substr.cpp:141`）：第一个必须字符串（`:144-147`），start/end 接受 `INTEGER_TYPE` 或 `REAL_TYPE` wrapper（`:149-163`），缺省 end = 全长（`:166`）。校验：`start >= s1.length()` 抛错（`:173-174`）、`start >= end` 抛错（`:176-177`）。最终 `s1.substr(start, end-start)`（`:179`）——注意注释写「substring goes from [start, end]」（`:121`）但实现是 C++ `substr` 的左闭右开 $[\text{start}, \text{end})$，即取到 end-1；**注释与实现不一致**，以代码为准。脚本语法 `substr(a, start, end=strlen)`（`MathFactory.cpp:392`）。

---

## 三、公式索引表

| 函数 | 文件:行（Evaluate/MatrixEvaluate 核心） | 所属类 |
|---|---|---|
| `Add`（加法，含一元 +） | `src/base/math/Add.cpp:253` / `:285` | `MathFunction` |
| `Subtract`（减法） | `src/base/math/Subtract.cpp:244` / `:273` | `MathFunction` |
| `Multiply`（乘法/矩阵乘法） | `src/base/math/Multiply.cpp:294` / `:365` | `MathFunction` |
| `Divide`（除法，逐元素） | `src/base/math/Divide.cpp:275` / `:312` | `MathFunction` |
| `Negate`（一元取负） | `src/base/math/Negate.cpp:155` / `:164` | `MathFunction` |
| `Power`（幂 $x^y$） | `src/base/math/Power.cpp:195` | `MathFunction` |
| `Mod`（取模） | `src/base/math/Mod.cpp:151` | `NumericFunctionNode` |
| `Min`（最小值） | `src/base/math/Min.cpp:150-155` | `NumericFunctionNode` |
| `Determinant`（行列式） | `src/base/math/Determinant.cpp:167` | `MathFunction` |
| `Inverse`（求逆） | `src/base/math/Inverse.cpp:148` / `:187` | `MathFunction` |
| `Norm`（2-范数） | `src/base/math/Norm.cpp:147` / `:151` / `:165` | `MathFunction` |
| `Transpose`（转置） | `src/base/math/Transpose.cpp:274` | `MathFunction` |
| `Cross3`（三维叉积） | `src/base/math/Cross3.cpp:240` | `NumericFunctionNode` |
| `Diag`（对角矩阵） | `src/base/math/Diag.cpp:218-222` | `NumericFunctionNode` |
| `Sin` | `src/base/math/Sin.cpp:127` | `MathFunction` |
| `Cos` | `src/base/math/Cos.cpp:128` | `MathFunction` |
| `Tan` | `src/base/math/Tan.cpp:128` | `MathFunction` |
| `Asin` | `src/base/math/Asin.cpp:128` | `MathFunction` |
| `Acos` | `src/base/math/Acos.cpp:128` | `MathFunction` |
| `Atan` | `src/base/math/Atan.cpp:128` | `MathFunction` |
| `Atan2`（四象限，左子为 y） | `src/base/math/Atan2.cpp:160` | `MathFunction` |
| `Sinh` | `src/base/math/Sinh.cpp:151` | `MathFunction` |
| `Cosh` | `src/base/math/Cosh.cpp:154` | `MathFunction` |
| `Tanh` | `src/base/math/Tanh.cpp:151` | `MathFunction` |
| `Asinh` | `src/base/math/Asinh.cpp:151` | `MathFunction` |
| `Acosh` | `src/base/math/Acosh.cpp:151` | `MathFunction` |
| `Exp` | `src/base/math/Exp.cpp:128` | `MathFunction` |
| `Log`（自然对数） | `src/base/math/Log.cpp:128` | `MathFunction` |
| `Log10` | `src/base/math/Log10.cpp:128` | `MathFunction` |
| `Sqrt` | `src/base/math/Sqrt.cpp:127` | `MathFunction` |
| `Abs` | `src/base/math/Abs.cpp:128` | `MathFunction` |
| `Ceil` | `src/base/math/Ceil.cpp:128` | `MathFunction` |
| `Floor` | `src/base/math/Floor.cpp:128` | `MathFunction` |
| `Fix` | `src/base/math/Fix.cpp:128` | `MathFunction` |
| `DegToRad`（×π/180） | `src/base/math/DegToRad.cpp:128` | `MathFunction` |
| `RadToDeg`（×180/π） | `src/base/math/RadToDeg.cpp:126` | `MathFunction` |
| `Rand`（均匀随机） | `src/base/math/Rand.cpp:200` / `:231` | `MathFunction` |
| `Randn`（正态随机） | `src/base/math/Randn.cpp:200` / `:231` | `MathFunction` |
| `Sprintf`（格式化） | `src/base/math/Sprintf.cpp:137-506`（`EvaluateString`） | `StringFunctionNode` |
| `Strcat`（拼接） | `src/base/math/Strcat.cpp:125`（`EvaluateString`） | `StringFunctionNode` |
| `Strcmp`（比较，返回 1/0） | `src/base/math/Strcmp.cpp:151-154` | `StringFunctionNode` |
| `Strfind`（查找，1 基） | `src/base/math/Strfind.cpp:160-167` | `StringFunctionNode` |
| `Strlen`（长度） | `src/base/math/Strlen.cpp:174` | `StringFunctionNode` |
| `Strrep`（替换） | `src/base/math/Strrep.cpp:130`（`EvaluateString`） | `StringFunctionNode` |
| `Substr`（子串） | `src/base/math/Substr.cpp:179`（`EvaluateString`） | `StringFunctionNode` |
| `FunctionRunner`（调 GmatFunction） | `src/base/math/FunctionRunner.cpp:617` / `:690` / `:752` | `MathFunction` |

> 说明：`Sprintf`/`Strcat`/`Strrep`/`Substr` 无 `Evaluate`/`MatrixEvaluate`（字符串节点走 `EvaluateString`，基类 `MathNode::EvaluateString` 默认返回 `STRING_PARAMETER_UNDEFINED`，见 `MathNode.cpp:177-180`）；`Strcmp`/`Strfind`/`Strlen` 有 `Evaluate` 且覆写 `GetOutputInfo` 返回 `REAL_TYPE`。基础设施类（`MathNode`/`MathFunction`/`MathElement`/`BuiltinFunctionNode`/`NumericFunctionNode`/`StringFunctionNode`/`MathException`/`EquationWrapper`）无数值公式，见本章第一节。
