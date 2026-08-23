# 第3章 src/base/math 数值算法与数学库

本章范围：`L:\gmat888\src\base\math\` 目录下的全部 `.hpp` / `.cpp` 文件，共 **108 个**（54 个 `.hpp` + 54 个 `.cpp`，一一成对）。

> **重要的事实澄清（写在本章最前面）**：该目录在 GMAT 源码中实现的是**脚本数学表达式解析与求值子系统**——一个以 `MathNode` 为根的表达式树（Expression Tree），外加约 44 个内置数学/矩阵/字符串函数节点，以及把表达式包装成 `ElementWrapper` 的桥接类。任务书中设想的「插值器（Interpolator/Lagrange/Hermite）、Rmatrix/Rvector 矩阵库、四元数姿态数学、RungeKutta89 积分器 Butcher 表、CubicSpline、最小二乘测量矩阵」**并不位于本目录**，它们散布在仓库其他位置：
>
> | 任务书设想内容 | 实际所在位置 |
> |---|---|
> | Rmatrix / Rvector / Rmatrix33 / Rvector3 / Rmatrix66 / Rvector6 | `src\gmatutil\util\`（Rmatrix.hpp、Rvector.hpp 等） |
> | 标量数学函数库 `GmatMathUtil`（Sin/Cos/Randn/Pow/Mod… 的数值实现） | `src\gmatutil\util\RealUtilities.hpp` / `.cpp` |
> | 姿态 / 旋转矩阵 / 四元数 | `src\base\attitude\`（Attitude.hpp 等）、`src\base\parameter\AttitudeRmat33.*` |
> | 积分器（RungeKutta / RungeKutta89 / PredictorCorrector / RungeKuttaNystrom） | `src\base\propagator\` |
> | 测量模型 / 最小二乘估计矩阵 | `plugins\EstimationPlugin\src\base\measurement\` |
> | 插值器 / CubicSpline（C++ 类） | 本仓库 `src` 下无对应 C++ 类，仅存在于 `prototype\`（MATLAB/Python 原型） |
>
> 因此本章按**真实内容**撰写：讲解该表达式求值子系统的类层次、每个内置函数的求值公式与验证逻辑，并说明它与矩阵库/积分器等数值内核的调用关系（见「三、关键设计模式与数据流」）。

## 一、本章目录树

```
src/base/math/                          (共 108 个文件 = 54 .hpp + 54 .cpp)
├── MathNode.hpp/.cpp                   # 表达式树节点抽象基类
├── MathFunction.hpp/.cpp               # 二元运算符节点基类（leftNode/rightNode）
├── MathElement.hpp/.cpp                # 叶节点：绑定 Parameter/Array/字面量
├── MathException.hpp/.cpp              # 本子系统专用异常
├── BuiltinFunctionNode.hpp/.cpp        # 多参数 wrapper 风格函数节点基类（2016 新增）
├── NumericFunctionNode.hpp/.cpp        # 数值内置函数节点基类
├── StringFunctionNode.hpp/.cpp         # 字符串内置函数节点基类
├── FunctionRunner.hpp/.cpp             # 表达式内联调用 GmatFunction 的桥接节点
├── EquationWrapper.hpp/.cpp            # 把方程包装为 ElementWrapper（供 CSALT/优化用）
├── Add.hpp/.cpp  Subtract.hpp/.cpp     # 加法（含一元 +）/ 减法
├── Multiply.hpp/.cpp  Divide.hpp/.cpp  # 乘法（矩阵乘法）/ 除法
├── Negate.hpp/.cpp  Power.hpp/.cpp     # 一元取负 / 幂（x^y）
├── Mod.hpp/.cpp  Min.hpp/.cpp          # 取模 / 最小值
├── Cross3.hpp/.cpp  Determinant.hpp/.cpp  Diag.hpp/.cpp
├── Inverse.hpp/.cpp  Norm.hpp/.cpp  Transpose.hpp/.cpp   # 矩阵/向量函数族
├── Sin Cos Tan  Asin Acos Atan  Atan2        # 三角与反三角
├── Sinh Cosh Tanh  Asinh Acosh               # 双曲函数
├── Exp Log Log10  Sqrt  Abs  Ceil Floor Fix  # 初等函数与取整
├── DegToRad RadToDeg                          # 单位换算
├── Rand Randn                                 # 均匀/高斯随机数
└── Sprintf Strcat Strcmp Strfind Strlen Strrep Substr   # 字符串函数族
```

按基类统计（`class GMAT_API X : public ...` 声明行号经 grep 确认）：

| 基类 | 派生类（数量） |
|---|---|
| `MathFunction`（二元树节点） | Add、Subtract、Multiply、Divide、Negate、Power、Atan2、Sin、Cos、Tan、Asin、Acos、Atan、Sinh、Cosh、Tanh、Asinh、Acosh、Exp、Log、Log10、Sqrt、Abs、Ceil、Floor、Fix、DegToRad、RadToDeg、Determinant、Inverse、Norm、Transpose、Rand、Randn、FunctionRunner（34 个） |
| `NumericFunctionNode`（多参 wrapper 风格） | Cross3、Diag、Min、Mod（4 个） |
| `StringFunctionNode`（多参 wrapper 风格） | Sprintf、Strcat、Strcmp、Strfind、Strlen、Strrep、Substr（7 个） |
| `MathNode`（直接派生） | MathElement、MathFunction、BuiltinFunctionNode（3 个抽象/中间基类） |
| 其它 | MathException（`BaseException` 派生）、EquationWrapper（`ElementWrapper` 派生） |

## 二、逐文件/逐类讲解

### 2.1 表达式树基类与基础设施

#### MathNode.hpp / MathNode.cpp —— 表达式树节点抽象基类

- 职责一句话：定义表达式树中一切节点（叶、运算符、函数）的公共协议，是本章类层次的根。
- 类声明：`MathNode.hpp:40` `class GMAT_API MathNode : public GmatBase`。

```cpp
// MathNode.hpp:40-100（节选）
class GMAT_API MathNode : public GmatBase
{
   bool                 IsFunction() { return isFunction; }
   bool                 IsNumber() { return isNumber; }
   Integer              GetElementType() { return elementType; }
   Real                 GetRealValue() { return realValue; }
   const Rmatrix&       GetMatrixValue() { return matrix; }
   void                 SetRealValue(Real val);
   virtual void         SetMatrixValue(const Rmatrix &mat);
   // 抽象求值协议（每个具体节点必须实现）
   virtual bool         ValidateInputs() = 0;
   virtual void         GetOutputInfo(Integer &type, Integer &rowCount, Integer &colCount) = 0;
   virtual Real         Evaluate() = 0;
   virtual Rmatrix      MatrixEvaluate() = 0;
   virtual bool         SetChildren(MathNode *leftChild, MathNode *rightChild) = 0;
   virtual MathNode*    GetLeft() = 0;
   virtual MathNode*    GetRight() = 0;
protected:
   bool isNumber;  bool isFunction;  bool isFunctionInput;
   Integer elementType;      // Gmat::REAL_TYPE / Gmat::RMATRIX_TYPE
   Real realValue;           // 叶节点缓存标量
   Rmatrix matrix;           // 叶节点缓存矩阵
   std::string stringValue;
};
```

- 逐行解读：`Evaluate()` 与 `MatrixEvaluate()` 是递归求值入口，`GetOutputInfo()` 在求值前做类型/维度推导（相当于轻量「编译期」类型检查），`SetChildren/GetLeft/GetRight` 维系二叉结构。数据成员 `isNumber` 标记该节点是否为字面量、`isFunctionInput` 标记其是否为函数输入（交由 `FunctionRunner` 处理而非本节点求值），`elementType` 区分标量与矩阵。
- 构造器（`MathNode.cpp:45-56`）以 `Gmat::MATH_NODE` 注册到 GmatBase，并把 `realValue`/`stringValue` 初始化为 `REAL_PARAMETER_UNDEFINED`/`STRING_PARAMETER_UNDEFINED`，保证「未赋值」可被识别。
- **实测缺陷提示**：复制构造函数 `MathNode.cpp:87` 写的是 `isFunctionInput (mn.isFunction)`，把 `isFunctionInput` 错赋成了 `mn.isFunction`（应为 `mn.isFunctionInput`）；赋值运算符 `MathNode.cpp:115` 则正确复制了 `isFunctionInput`。两处不一致，属典型的复制粘贴隐患，读代码时注意。
- 模板/内联设计：本类不含模板；`IsFunction/IsNumber/GetElementType/GetRealValue/GetMatrixValue` 是头文件内联访问器（`MathNode.hpp:49-58`），用于高频的、无副作用的属性读取，避免函数调用开销。

#### MathFunction.hpp / MathFunction.cpp —— 二元运算符/函数节点基类

- 职责：为「两个子节点」的运算（+、-、*、/、^、二元函数）提供 `leftNode`/`rightNode` 的存储与通用校验。
- 类声明：`MathFunction.hpp:39` `class GMAT_API MathFunction : public MathNode`；成员 `MathFunction.hpp:56-57` `MathNode *leftNode; MathNode *rightNode;`。
- `SetChildren`（`MathFunction.cpp:142-155`）允许左子为空（支持一元 + / 一元 - 等），右子为空则置 NULL；基类的 `Evaluate`/`MatrixEvaluate`（`MathFunction.cpp:124-136`）直接抛异常「cannot return Real/Matrix」，强制子类覆写。
- 四个受保护的校验/推导助手是本类最有价值的部分：
  - `GetScalarOutputInfo`（`MathFunction.cpp:179-200`）：输出固定为 1×1 的 `REAL_TYPE`（注释特别说明「1×1 矩阵按标量返回」）。
  - `GetMatrixOutputInfo`（`MathFunction.cpp:207-240`）：输出行列取左节点的**转置**（`rowCount=col1; colCount=row1`），供 `Transpose` 这类「单输入、输出转置」函数复用。
  - `ValidateScalarInputs`（`MathFunction.cpp:251-298`）：要求输入为 `REAL_TYPE` 或 1×1 矩阵，否则抛 `MathException`。
  - `ValidateMatrixInputs(bool allowScalarInput)`（`MathFunction.cpp:309-351`）：要求输入为矩阵；`allowScalarInput=true` 时放行标量（供 `Norm`、`Inverse` 复用）。
- 设计意图：把「维度/类型检查」与「数值计算」分离——校验集中在基类，子类 `Evaluate()` 只写数值公式，这正是整个目录里约 34 个 `MathFunction` 派生类都极其短小的原因。

#### MathElement.hpp / MathElement.cpp —— 叶节点（绑定参数/数组/字面量）

- 职责：表达式树最末端的「值来源」。一个 `MathElement` 要么是数字字面量，要么是某个 GMAT `Parameter`/`Array` 的引用（运行时通过 `ElementWrapper` 取当前值）。
- 类声明：`MathElement.hpp:44` `class GMAT_API MathElement : public MathNode`；成员 `MathElement.hpp:86-95`：`refObject`（`Parameter*`，被绑定对象）、`refObjectName`、`refObjectType`、`wrapperObjectNames`（名字列表，逗号分隔）、`theWrapperMap`（`WrapperMap*`）。
- 构造器（`MathElement.cpp:53-83`）是关键：用 `GmatStringUtil::ToReal(name, &rval)` 判断名字能否转成实数——
  ```cpp
  // MathElement.cpp:68-77（节选）
  if (GmatStringUtil::ToReal(name, &rval)) { SetRealValue(rval); SetNumberFlag(true); }
  else                                    { SetRefObjectName(Gmat::PARAMETER, name); }
  ```
  能转则当作数字字面量；否则当作参数名，等待 `SetRefObject` 绑定。这种「按名字内容判别字面量 vs 引用」的写法使脚本 `x = 2*PI` 与 `x = 2*myParam` 共用同一类。
- `SetWrapperObject`（`MathElement.cpp:766-843`）：把 `refObject` 强转为 `Parameter*`，并按返回类型初始化 `elementType` 与缓存值；对 `Array` 还会解析下标（`GmatStringUtil::GetArrayIndex`，见 `MathElement.cpp:789`），按 `Array::GetRmatrix()` 取初始值。
- `GetOutputInfo`（`MathElement.cpp:173-270`）：若绑定的是 `Array`，用 `GetArrayIndexVar` 解析 `(row,col)`，整数组（`rowStr=="-1"&&colStr=="-1"`）返回真实维度，否则退化为 1×1 标量（取单个元素）。数组「切片」`a(:,1)` 的注释表明是预留能力。
- `Evaluate`（`MathElement.cpp:299-358`）：`refObject` 非空时经 `FindWrapper(refObjectName)` 找到 `ElementWrapper` 后调用 `EvaluateReal()` 取实时值；否则直接返回缓存的 `realValue`。`MatrixEvaluate`（`MathElement.cpp:364-418`）同理，标量会包装成 1×1 `Rmatrix` 返回。
- `RenameRefObject`（`MathElement.cpp:462-560`）：对 `refObjectName`、`wrapperObjectNames` 及整个 `theWrapperMap` 做名字替换（对象改名时同步更新），用临时 `tempMap` + `swap` 避免迭代中修改原 map。
- `FindWrapper`（`MathElement.cpp:853-889`）：在 `theWrapperMap` 中按名字查 `ElementWrapper`，查不到抛异常——这是叶节点与「Sandbox 中的实时数据」之间的唯一通道。

#### MathException.hpp / MathException.cpp —— 异常类型

- 职责：本章所有错误（维度不匹配、非法参数、缺参数、类型错误）的统一异常。
- 构造（`MathException.cpp:43-46`）：`BaseException("Math Exception: ", details)`——前缀固定为 `"Math Exception: "`，便于日志检索。声明见 `MathException.hpp:37`。

#### BuiltinFunctionNode.hpp / BuiltinFunctionNode.cpp —— 多参数 wrapper 风格函数基类

- 职责：2016 年新增的第二代函数节点基类，与 `MathFunction` 的「二叉左/右子树」不同，它用**参数列表 + ElementWrapper 数组**来表达 `FuncName(arg1, arg2, …)` 形式的多参数函数。
- 类声明：`BuiltinFunctionNode.hpp:37` `class GMAT_API BuiltinFunctionNode : public MathNode`；成员 `BuiltinFunctionNode.hpp:62-71`：`desc`（原始调用文本）、`inputNames`/`outputNames`、`theWrapperMap`、`inputArgWrappers`/`outputArgWrappers`。
- 构造器（`BuiltinFunctionNode.cpp:51-108`）直接解析 `desc`：用 `DecomposeBy(desc,"(")` 切出函数名与实参串，再 `RemoveLastString(...,")")` 去右括号；若实参形如 `[1 2 3]` 则 `SeparateBrackets` 按向量元素拆，否则 `SeparateByComma` 按逗号拆，每项 push 进 `inputNames` 并配一个 `NULL` 占位 wrapper。
- `SetMathWrappers`（`BuiltinFunctionNode.cpp:162-212`）把外部 `WrapperMap` 里与 `inputNames` 同名的 wrapper 填进 `inputArgWrappers`，实现「名字→wrapper」的绑定。
- `SetChildren/GetLeft/GetRight`（`BuiltinFunctionNode.cpp:236-257`）对这类节点无效，直接抛异常或返回 NULL——体现「非二叉树」的结构差异。
- `ValidateWrappers`（`BuiltinFunctionNode.cpp:330-344`）逐个检查 `inputArgWrappers[i]` 非 NULL，否则抛「Error evaluating ...」。

#### NumericFunctionNode.hpp / NumericFunctionNode.cpp —— 数值内置函数基类

- 职责：`BuiltinFunctionNode` 的数值分支，为 `Cross3/Diag/Min/Mod` 提供默认的标量输出信息与宽松校验。
- 类声明：`NumericFunctionNode.hpp:39`。`GetOutputInfo`（`NumericFunctionNode.cpp:137-156`）固定输出 `REAL_TYPE` 1×1；`ValidateInputs`（`NumericFunctionNode.cpp:111-132`）默认返回 `true`（具体维度校验留给子类，如 `Cross3` 的 3 元素要求）。

#### StringFunctionNode.hpp / StringFunctionNode.cpp —— 字符串内置函数基类

- 职责：`BuiltinFunctionNode` 的字符串分支。
- `GetOutputInfo`（`StringFunctionNode.cpp:153-172`）固定输出 `STRING_TYPE` 1×1；`ValidateInputs`（`StringFunctionNode.cpp:110-148`）额外检查 `desc` 去掉空白后非空、能按 `(` 分解、且以 `)` 结尾——即校验调用语法。
- 重写的 `ValidateWrappers`（`StringFunctionNode.cpp:177-198`）先调基类查 NULL，再要求**第一个输入为 STRING_TYPE**，否则抛「Expecting inputs of String type」。
- 注意：`Strcmp/Strfind/Strlen` 虽派生自本类，但输出被覆写为 `REAL_TYPE`（返回数值），见各自 `.cpp`。

### 2.2 表达式求值桥接

#### FunctionRunner.hpp / FunctionRunner.cpp —— 表达式内联调用 GmatFunction

- 职责：让用户脚本的数学表达式里能直接调用一个 GmatFunction（`Function`），例如 `x = MyFunc(a,b) + 1`。它是 `MathFunction` 派生类，但求值时把控制权交给 `FunctionManager`。
- 类声明：`FunctionRunner.hpp:42`；成员 `FunctionRunner.hpp:88-98`：`theFunctionManager`（真正的执行器）、`theObjectMap`/`theGlobalObjectMap`（局部/全局对象表）、`theFunctionName`、`theFunction`、`theInputNames`/`theOutputNames`、`theInputNodes`、`callingFunction`、`internalCS`。
- 一组 `SetXxx` 方法（`FunctionRunner.cpp:270-429`）把脚本运行时上下文（ObjectMap、SolarSystem、CoordinateSystem、TransientForces、Publisher）逐一下发给 `theFunctionManager`——函数体内要用到的任何 GMAT 对象都必须经这些通道注入。
- `SetGlobalObjectMap`（`FunctionRunner.cpp:292-327`）在全局对象表里 `FindObject(theFunctionName)` 找到 `Function` 并 `SetFunction`，找不到抛异常。
- `GetOutputInfo`（`FunctionRunner.cpp:433-538`）从 `function->GetOutputTypes()` 推断返回值：`VARIABLE_WT`→Real、`ARRAY_WT`→Rmatrix、`OBJECT_WT`→Object，并要求函数**只返回一个值**。
- `Evaluate`（`FunctionRunner.cpp:575-654`）：核心就一行 `result = theFunctionManager.Evaluate(callingFunction);`（`:617`），随后回收输出 wrapper 防泄漏。`MatrixEvaluate`（`:665-717`）与 `EvaluateObject`（`:727-779`）同理分派到 `FunctionManager::MatrixEvaluate/EvaluateObject`。
- `FindObject`（`FunctionRunner.cpp:813-852`）：先查**局部对象表（LOS）**再查**全局对象表（GOS）**，并忽略 `Array` 的下标后缀——这是 GMAT 作用域规则的体现。
- `HandlePassingMathExp`（`FunctionRunner.cpp:861-953`）被 `#ifdef __ALLOW_MATH_EXP_NODE__` 整体包裹（当前未启用），是「向函数传入整棵表达式子节点」的半成品（`@todo` 标注），属于预留能力而非现役路径。

#### EquationWrapper.hpp / EquationWrapper.cpp —— 把方程包装成 ElementWrapper

- 职责：把一个 RHS 方程字符串（如 `"x^2 + 2*y"`）包装成标准 `ElementWrapper`，使其能像普通参数一样被求值。主要用于 **CSALT（配点法最优控制）** 与优化类求解器。
- 类声明：`EquationWrapper.hpp:40` `class EquationWrapper: public ElementWrapper`（注意：它**不在** `MathNode` 体系内，而是 `ElementWrapper` 的派生类）。
- 成员 `EquationWrapper.hpp:84-105`：`theEquation`（方程字符串）、`dataType`（`Gmat::ParameterType`）、`theTree`（`RHSEquation`，内嵌一棵完整数学树）、`retVec`/`retMat`（Rvector/Rmatrix 返回容器）、`resultant`（求值结果 wrapper）、`refObjects`、`configObjectMap`/`equationObjectMap`、`hasEvaluated`。
- 构造器（`EquationWrapper.cpp:40-63`）把 `wrapperType` 设为 `Gmat::EQUATION_WT`。
- `ConstructTree`（`EquationWrapper.cpp:234-237`）调用 `theTree.BuildExpression(theEquation, configObjectMap, true)` 解析并建树；`Initialize`（`:179-192` / `:194-223`）调用 `theTree.Initialize(...)` 并借 `GetMathTree(false)->GetOutputInfo(...)` 推断返回类型。
- `EvaluateEquation`（`EquationWrapper.cpp:277-310`）执行 `resultant = theTree.RunMathTree(NULL)`，并按 `dataType` 校验返回类型一致性。`EvaluateReal`（`:325-353`）从 `resultant->EvaluateReal()` 取标量结果。字符串返回在代码中被注释禁用（`EquationWrapper.hpp:79-81`、`.cpp:403-412`）。

### 2.3 二元算术运算符（MathFunction 系）

> 通用结构（下述每个类都相同）：构造器以类名注册（如 `Add::Add : MathFunction("Add", nomme)`），`Clone()` 返回 `new X(*this)`，`GetOutputInfo`/`ValidateInputs` 做维度与类型检查，`Evaluate`/`MatrixEvaluate` 写数值公式。以下只列每个类**与众不同**之处与数学背景。

#### Add.hpp / Add.cpp —— 加法（含一元 +）

- 数学：$c = a + b$；支持标量广播（`M×N + 1×1`）。
- `GetOutputInfo`（`Add.cpp:102-172`）：维度不同时，允许「1×1 + M×N」与「M×N + 1×1」两种广播，否则抛「Dimensions are not the same」。左子为 NULL 时按右子维度兜底（`Add.cpp:129-134`），支持一元 `+`。
- `Evaluate`（`Add.cpp:242-256`）：`leftNode ? left+right : right`——一元 `+` 直接返回右操作数。`MatrixEvaluate`（`:267-295`）覆盖 矩阵+矩阵、矩阵+标量、标量+矩阵 三种组合。

#### Subtract.hpp / Subtract.cpp —— 减法

- 数学：$c = a - b$。`Evaluate`（`Subtract.cpp:237-247`）先 `ValidateInputs()` 再 `left-right`；`MatrixEvaluate`（`:258-283`）结构与 Add 对称（矩阵−矩阵/矩阵−标量/标量−矩阵）。

#### Multiply.hpp / Multiply.cpp —— 乘法（矩阵乘法语义）

- 数学：标量 $a\cdot b$；矩阵 $\mathbf C=\mathbf A\,\mathbf B$，要求内维一致 $\mathrm{col}(A)=\mathrm{row}(B)$。
- `GetOutputInfo`（`Multiply.cpp:101-172`）：两矩阵时校验 `col1 == row2`，否则仅当一方是 1×1 才广播，再否则抛「Inner matrix dimensions must agree」。
- `ValidateInputs`（`Multiply.cpp:183-267`）额外校验操作数**类型**（用 `PARAM_TYPE_STRING` 拼错误信息），禁止字符串参与乘法。
- `Evaluate`（`Multiply.cpp:278-336`）虽标量返回，但会处理「标量×1×1 矩阵」与「1×1 矩阵×标量」的退化情形；`MatrixEvaluate`（`:347-382`）直接复用 `Rmatrix` 的 `operator*`。

#### Divide.hpp / Divide.cpp —— 除法

- 数学：标量 $a/b$；矩阵除法沿用 `Rmatrix::operator/`。
- `ValidateInputs`（`Divide.cpp:175-256`）显式拒绝「标量 / 矩阵」（`:240-245` 抛「Cannot divide a scalar by a matrix」），仅允许「标量 / 1×1 矩阵」。`Evaluate`（`:267-282`）为 `left/right`。

#### Negate.hpp / Negate.cpp —— 一元取负

- 数学：$c = -a$。`GetOutputInfo`（`Negate.cpp:98-111`）输出类型/维度与左子一致；`Evaluate`（`:153-156`）`leftNode->Evaluate() * -1`；`MatrixEvaluate`（`:162-165`）`leftNode->MatrixEvaluate() * -1`。

#### Power.hpp / Power.cpp —— 幂

- 数学：$c = a^b$（指数为标量）。`ValidateInputs`（`Power.cpp:148-182`）要求两操作数都是标量或 1×1 矩阵，否则抛「must be a scalar or 1x1 matrix」；`Evaluate`（`:193-196`）`GmatMathUtil::Pow(left, right)`。

#### Mod.hpp / Mod.cpp —— 取模（NumericFunctionNode 系）

- 数学：$r = a \bmod b$（除法余数）。`Evaluate`（`Mod.cpp:123-158`）要求恰好 2 个实参，取 `GmatMathUtil::Mod(a, b)`。声明见 `Mod.hpp:39`。

#### Min.hpp / Min.cpp —— 最小值（NumericFunctionNode 系）

- 数学：$m=\min(a_1,\dots,a_n)$，支持**任意多个**实参。`Evaluate`（`Min.cpp:122-164`）从第 0 个起逐个比较取小。声明见 `Min.hpp:39`。

### 2.4 矩阵 / 向量函数

> 这一族是本章「数值味道」最浓的部分，但**真正的矩阵算法实现在 `Rmatrix`/`Rvector` 类里**（`src\gmatutil\util\`），这里的节点只是薄薄一层脚本绑定：`Evaluate` 里调 `Rmatrix::Determinant()/Inverse()/Transpose()` 等方法。

#### Determinant.hpp / Determinant.cpp —— 行列式

- 数学：$\det A$，仅方阵有意义。`ValidateInputs`（`Determinant.cpp:122-149`）要求输入为 `REAL/RMATRIX` 且方阵（`row1==col1`）；`Evaluate`（`:160-173`）对矩阵调 `leftNode->MatrixEvaluate().Determinant()`，标量则原样返回。声明见 `Determinant.hpp:35`。

#### Inverse.hpp / Inverse.cpp —— 矩阵求逆

- 数学：标量 $x^{-1}$ 或矩阵 $\mathbf A^{-1}$。`ValidateInputs`（`Inverse.cpp:117-136`）禁止非方阵（`:129-130` 抛「Cannot compute inverse of non-square matrix」）。`Evaluate`（`:146-149`）`GmatMathUtil::Pow(x, -1.0)`；`MatrixEvaluate`（`:159-192`）`leftNode->MatrixEvaluate().Inverse()`，并把 `BaseException` 捕获后重抛，保留底层（奇异矩阵等）诊断。声明见 `Inverse.hpp:36`。

#### Transpose.hpp / Transpose.cpp —— 转置

- 数学：$(\mathbf A^\top)_{ij}=\mathbf A_{ji}$。`GetOutputInfo`（`Transpose.cpp:102-132`）输出行列互换（`rowCount=col1; colCount=row1`）；标量转置等于自身（注释引用 Bug 2186，`Transpose.cpp:118-120`）。`MatrixEvaluate`（`:246-279`）`...Transpose()`。声明见 `Transpose.hpp:36`。

#### Norm.hpp / Norm.cpp —— 范数

- 数学：向量欧氏范数 $\|\mathbf v\|_2=\sqrt{\sum v_i^2}$，标量范数 = 绝对值。`Evaluate`（`Norm.cpp:138-167`）单行向量取 `GetRow(0).Norm()`、单列取 `GetColumn(0).Norm()`；注释明确「矩阵范数留待将来需求」。声明见 `Norm.hpp:35`。

#### Cross3.hpp / Cross3.cpp —— 三维叉积（NumericFunctionNode 系）

- 数学：$\mathbf c=\mathbf a\times\mathbf b$，分量式见 `Cross3.cpp:179-185` 注释（$c_1=a_2b_3-b_2a_3$ 等）。`MatrixEvaluate`（`Cross3.cpp:189-258`）要求两个 3 元素向量（3×1 或 1×3 均接受），组装 `Rvector3` 后调用**友元函数** `Cross(vec1,vec2)`（`Rvector3.hpp` 中声明，`Cross3.cpp:34` 注释「for friend function Cross()」）。声明见 `Cross3.hpp:39`。

#### Diag.hpp / Diag.cpp —— 构造对角阵（NumericFunctionNode 系）

- 数学：$\mathrm{diag}(d_1,\dots,d_n)$ 生成以 $d_i$ 为对角元的 $n\times n$ 矩阵。`GetOutputInfo`（`Diag.cpp:156-181`）用 `inputNames.size()` 决定 $n$（输出 n×n）；`MatrixEvaluate`（`:196-231`）只在对角元 `i==j` 处写 `EvaluateReal()`。声明见 `Diag.hpp:39`，私有成员 `numRows/numCols` 缓存维度（`Diag.cpp:51-56`）。

### 2.5 三角函数 / 反三角 / 双曲函数（MathFunction 系）

> 下列 12 个类的结构完全同构（以 `Sin` 为模板），每个只覆写 `GetOutputInfo`（转发 `GetScalarOutputInfo`）、`ValidateInputs`（转发 `ValidateScalarInputs`）、`Evaluate`（转发 `GmatMathUtil::X`）。数学背景统一说明，逐类只给「Evaluate 委托目标 + 行号」。

数学公式背景：

- 三角函数（弧度制输入，即脚本中三角函数按弧度计）：$\sin$、$\cos$、$\tan$，及反三角 $\arcsin$、$\arccos$、$\arctan$。
- 双曲函数：$\sinh x=\frac{e^x-e^{-x}}2$、$\cosh x=\frac{e^x+e^{-x}}2$、$\tanh x=\frac{\sinh x}{\cosh x}$，及反双曲 $\mathrm{asinh}$、$\mathrm{acosh}$。
- **精度/角度折返设计**：这些节点不直接调 C 标准库 `sin()`，而是委托 `GmatMathUtil::Sin/Cos/…`（`RealUtilities.hpp:87-104`）。后者签名为 `Sin(Real angleInRad, Real cycleInRad = GmatMathConstants::TWO_PI)`——即先对角度按 $2\pi$ 折返（角度归约），再交给底层实现，避免大角度（长时积分累积出的巨大角变量）直接喂给 `sin` 造成的精度损失。`ASin/ACos` 还带 `tol = GmatRealConstants::REAL_TOL` 容差参数处理边界（|x| 略超 1 的舍入）。

| 类（`class ... : public MathFunction` 声明行号） | `Evaluate` 委托（行号） |
|---|---|
| `Sin.hpp:36` | `GmatMathUtil::Sin`（`Sin.cpp:127`） |
| `Cos.hpp:36` | `GmatMathUtil::Cos`（`Cos.cpp:128`） |
| `Tan.hpp:36` | `GmatMathUtil::Tan`（`Tan.cpp:128`） |
| `Asin.hpp:36` | `GmatMathUtil::ASin`（`Asin.cpp:128`） |
| `Acos.hpp:36` | `GmatMathUtil::ACos`（`Acos.cpp:128`） |
| `Atan.hpp:36` | `GmatMathUtil::ATan`（`Atan.cpp:128`） |
| `Atan2.hpp:36` | 直接 `atan2(left, right)`（`Atan2.cpp:160`，C 标准库，双参） |
| `Sinh.hpp:37` | `GmatMathUtil::Sinh`（`Sinh.cpp:151`） |
| `Cosh.hpp:37` | `GmatMathUtil::Cosh`（`Cosh.cpp:154`） |
| `Tanh.hpp:37` | `GmatMathUtil::Tanh`（`Tanh.cpp:151`） |
| `Asinh.hpp:37` | `GmatMathUtil::ASinh`（`Asinh.cpp:151`） |
| `Acosh.hpp:37` | `GmatMathUtil::ACosh`（`Acosh.cpp:151`） |

补充：`Atan2`（`Atan2.hpp:36`）是唯一双参反三角，数学为四象限反正切 $\mathrm{atan2}(y,x)$，返回 $(-\pi,\pi]$，`Evaluate`（`Atan2.cpp:158-161`）直接调 `<math.h>` 的 `atan2`，`ValidateInputs`（`:137-146`）要求左右子都存在且为标量。

### 2.6 初等函数与取整（MathFunction 系）

| 类（声明行号） | `Evaluate` 委托（行号） | 数学/说明 |
|---|---|---|
| `Exp.hpp:35` | `GmatMathUtil::Exp`（`Exp.cpp:128`） | $e^x$ |
| `Log.hpp:36` | `GmatMathUtil::Log`（`Log.cpp:128`） | 自然对数 $\ln x$ |
| `Log10.hpp:35` | `GmatMathUtil::Log10`（`Log10.cpp:128`） | 常用对数 $\log_{10}x$ |
| `Sqrt.hpp:35` | `GmatMathUtil::Sqrt`（`Sqrt.cpp:127`） | $\sqrt{x}$ |
| `Abs.hpp:37` | `GmatMathUtil::Abs`（`Abs.cpp:128`） | 绝对值 $|x|$ |
| `Ceil.hpp:36` | `GmatMathUtil::Ceiling`（`Ceil.cpp:128`） | 向上取整 $\lceil x\rceil$ |
| `Floor.hpp:36` | `GmatMathUtil::Floor`（`Floor.cpp:128`） | 向下取整 $\lfloor x\rfloor$ |
| `Fix.hpp:36` | `GmatMathUtil::Fix`（`Fix.cpp:128`） | 向零取整（truncate） |

说明：这些函数全部委托 `GmatMathUtil`（`RealUtilities.hpp:106-131`），后者对 `Log/Log10/Pow/Exp` 提供 `base` 重载、`Pow` 有 `(Real,Real)` 与 `(Real,Integer)` 两个版本（整数指数用快速幂/二分幂）。`Fix` 与 `Floor` 的差异在于负数：`Fix(-1.5)=-1`（向零），`Floor(-1.5)=-2`（向负无穷）。

### 2.7 单位换算（MathFunction 系）

#### DegToRad.hpp / DegToRad.cpp、RadToDeg.hpp / RadToDeg.cpp

- 数学：$\theta_{\mathrm{rad}}=\theta_{\mathrm{deg}}\cdot\frac{\pi}{180}$，逆变换乘 $\frac{180}{\pi}$。
- `Evaluate` 分别委托 `GmatMathUtil::DegToRad`（`DegToRad.cpp:128`）与 `GmatMathUtil::RadToDeg`（`RadToDeg.cpp:126`）；`GmatMathUtil` 版本带 `modBy2Pi/modBy360` 可选折返（`RealUtilities.hpp:82-83`）。声明行号 `DegToRad.hpp:37`、`RadToDeg.hpp:37`。
- 脚本别名：`MathFactory.cpp:209-212` 同时注册 `DegToRad`/`Deg2Rad`、`RadToDeg`/`Rad2Deg` 两套名字。

### 2.8 随机数（MathFunction 系）

#### Rand.hpp / Rand.cpp —— [0,1) 均匀分布

- 数学：$X\sim U(0,1)$。`Evaluate`（`Rand.cpp:186-208`）`GmatMathUtil::Rand(0.0, 1.0)`；`MatrixEvaluate`（`:219-247`）生成 `N×N` 矩阵逐元素填充。
- `GetOutputDimension`（`Rand.cpp:258-315`）把实参解释为**正整数**（`fabs(rval-round(rval))<1e-6`），`rand()` 无参等价 `rand(1)`（`Rand.cpp:157-161` 注释）。声明见 `Rand.hpp:35`。

#### Randn.hpp / Randn.cpp —— 标准正态分布

- 数学：$X\sim \mathcal N(0,1)$。结构与 `Rand` 完全同构，`Evaluate`（`Randn.cpp:186-208`）`GmatMathUtil::Randn(0.0, 1.0)`。底层高斯随机数（Box–Muller 或类似变换）在 `RealUtilities.cpp` 的 `GmatMathUtil::Randn` 实现中，本节点仅做维度/整性校验与分发。声明见 `Randn.hpp:35`。

### 2.9 字符串函数（StringFunctionNode 系）

| 类（声明行号） | 求值函数 | 语义与实现要点（行号） |
|---|---|---|
| `Sprintf.hpp:35` | `EvaluateString`（`Sprintf.cpp:137`） | C `sprintf` 风格格式化：首个实参为格式串，逐 `%` 解析 spec，`sprintf(outBuffer,...)` 后 `ReplaceFirst` 回填。输出缓冲上限 `MAX_OUTPUT_LENGTH=30000`（`:139`）；只允许 `%a A e E f F g G s`，`%c d i o u x X p n` 被显式拒绝（`:181-237` 大段注释）。支持 `*` 宽/精度动态实参。 |
| `Strcat.hpp:35` | `EvaluateString`（`Strcat.cpp:106`） | 字符串拼接：循环 `result += wrapper->EvaluateString()`（`:116-126`）。 |
| `Strcmp.hpp:35` | `Evaluate`（`Strcmp.cpp:134`，返回 Real） | 比较两串，相等返回 1（真）否则 0（假）；`GetOutputInfo` 覆写为 `REAL_TYPE`（`Strcmp.cpp:111`）。 |
| `Strfind.hpp:35` | `Evaluate`（`Strfind.cpp:133`，返回 Real） | `str.find(pattern)` 返回首现下标，未找到返回 -1（`Strfind.cpp:127-129` 注释、`:148-158`）；输出 `REAL_TYPE`（`:111`）。 |
| `Strlen.hpp:34` | `EvaluateString`（`Strlen.cpp`，约 :170 取 `s1` 后求长） | 返回串长；`GetOutputInfo` 覆写为 `REAL_TYPE`（`Strlen.cpp:136`）。 |
| `Strrep.hpp:35` | `EvaluateString`（`Strrep.cpp:108`） | 替换子串：`GmatStringUtil::Replace(str, oldStr, newStr, 0)`（`:130`），要求 3 个实参。 |
| `Substr.hpp:34` | `EvaluateString`（`Substr.cpp:126`） | 取子串 `substr(s, start, end)`，`end` 缺省为串长（`:165-166`）；`start/end` 接受 `INTEGER_TYPE` 或 `REAL_TYPE`（`:149-163`）。 |

## 三、关键设计模式与数据流

### 3.1 继承体系（本章范围内的类层次）

```
GmatBase
├─ MathNode (抽象：Evaluate/MatrixEvaluate/GetOutputInfo/ValidateInputs/SetChildren)
│  ├─ MathElement            (叶节点，绑定 Parameter/Array/字面量)
│  ├─ MathFunction           (二叉 leftNode/rightNode 运算符节点)
│  │  ├─ Add/Subtract/Multiply/Divide/Negate/Power/Atan2/… (34 个二元/一元运算)
│  │  └─ FunctionRunner      (表达式内联调用 GmatFunction)
│  └─ BuiltinFunctionNode    (多参 wrapper 风格节点)
│     ├─ NumericFunctionNode → Cross3/Diag/Min/Mod
│     └─ StringFunctionNode  → Sprintf/Strcat/Strcmp/Strfind/Strlen/Strrep/Substr
├─ BaseException → MathException
└─ ElementWrapper → EquationWrapper   (不在 MathNode 体系内)
```

### 3.2 两代实现的并存（关键设计观察）

目录内同时存在**两套**函数节点实现风格，这是历史演进的痕迹：

1. **2006 年一代（`MathFunction` 系，作者多为 LaMont Ruley / Allison Greene）**：把一切运算都建模为**二叉树**（`leftNode`/`rightNode`）。二元运算符（`+ - * / ^`）自然契合，但一元函数（`sin(x)`）也硬套「左子为参数、右子为空」的约定，多参数函数（如 `atan2(y,x)`、`min(a,b,c)`）则无法优雅表达。
2. **2016 年二代（`BuiltinFunctionNode` 系，作者 Linda Jun）**：改用**实参列表 + ElementWrapper 数组**（`inputNames`/`inputArgWrappers`），在构造期直接解析 `FuncName(arg1,arg2,…)` 文本，天然支持任意多参数与向量实参 `[1 2 3]`。新增的 `Cross3/Diag/Min/Mod` 及全部字符串函数都走这条路。

两代在求值协议上统一于 `MathNode` 的虚接口，`MathTree` 无需知道具体是哪种节点，从而可以渐进迁移而不破坏旧脚本。

### 3.3 工厂模式与注册

- 实例化不靠 `new Sin(...)` 直接写，而是统一经 `MathFactory::CreateMathNode(ofType, withName)`（`src\base\factory\MathFactory.cpp:117-234`）：`Capitalize` 首字母后进入 if/else 链，把脚本函数名映射到具体类（如 `"cross"`→`Cross3`、`"det"`→`Determinant`、`"inv"`→`Inverse`、`"transpose"`→`Transpose`、`"Deg2Rad"`→`DegToRad`）。
- `BuildCreatables`（`MathFactory.cpp:334-397`）把可建类型清单注册进 `Factory`（`Gmat::MATH_NODE`），供对象创建与自省使用。**注意**：`MathFactory` 本身位于 `src\base\factory\`，不在本章目录，但它是本章全部类的唯一实例化入口，故在此说明。

### 3.4 数据流 / 调用链

**脚本表达式求值链（本章类的主路径）**：

```
脚本文本 "x = sin(y) + a(1,2)"
  → Interpreter (src/base/interpreter/)
  → MathParser 解析出运算符/函数名
  → MathFactory::CreateMathNode 实例化 MathNode 树（Sin、Add、MathElement...）
  → MathTree (src/base/interpreter/MathTree.cpp) 持有树根、下发 WrapperMap
  → Assignment / RHSEquation 命令 (src/base/command/) 在执行期触发
  → 根节点 Evaluate() 递归求值
       ├─ MathElement::Evaluate → ElementWrapper::EvaluateReal 取 Sandbox 实时值
       ├─ Sin::Evaluate → GmatMathUtil::Sin (src/gmatutil/util/RealUtilities.cpp)
       └─ Add::Evaluate → left + right
  → 结果写回左侧 Variable/Array
```

关键依赖（经 grep `#include` 确认）：

- `src\base\interpreter\MathTree.cpp`（`:33-34`）包含 `MathElement.hpp`、`FunctionRunner.hpp`——树的组装与叶节点绑定。
- `src\base\interpreter\MathParser.cpp`（`:36`）包含 `FunctionRunner.hpp`——解析期识别函数调用。
- `src\base\command\Assignment.cpp`（`:42`）、`src\base\command\RHSEquation.cpp`（`:33`）、`src\base\executive\Sandbox.cpp`（`:36`）包含 `MathTree.hpp`——命令与沙箱持有/运行数学树。
- `src\base\factory\MathFactory.cpp` 包含本章几乎全部头文件——工厂实例化。
- `src\UnitTests\TestMath\TestMath.cpp`、`TestMathParser.cpp` 包含 `MathElement.hpp`——单元测试。

**与任务书设想的 forcemodel / propagator / solver / estimation 的关系（真实情况）**：

- `forcemodel`、`propagator`、`solver`、`estimation` 这些上层数值模块**并不直接消费本章的表达式节点**。它们直接依赖的是：
  - `src\gmatutil\util\` 的 `Rmatrix`/`Rvector`（矩阵-向量代数内核）与 `RealUtilities.cpp` 的 `GmatMathUtil`（标量数学内核）——本章的 `Sin/Inverse/Transpose` 等节点最终也委托到这些同一底层。
  - `src\base\propagator\` 的 `RungeKutta`/`RungeKutta89` 等积分器（其 Butcher 表与步长控制见对应章节，不在本章）。
- 唯一的交叉点是 `EquationWrapper`：它把方程字符串包装成 `ElementWrapper`，供 **CSALT/最优控制** 及优化类求解器通过 `RHSEquation` 求值/求导使用，是「脚本层表达式」进入「数值求解层」的桥梁。

### 3.5 精度与性能考量

- **角度折返**：三角/双曲函数经 `GmatMathUtil` 做 $2\pi$ 周期折返后再调用底层实现，缓解大角度下的精度损失（见 2.5）。
- **容差比较**：`GmatMathUtil::IsEqual/IsZero` 以 `GmatRealConstants::REAL_EPSILON` 为默认精度（`RealUtilities.hpp:70-72`）；`Rand/GetOutputDimension` 用 $10^{-6}$ 判「整数」（`Rand.cpp:300-301`）。
- **维度/类型校验前置**：`GetOutputInfo` + `ValidateInputs` 在求值前完成维度检查，把错误尽早抛出（`MathException`），避免矩阵运算中途崩溃。
- **值缓存 vs 实时取值**：`MathNode` 的 `realValue`/`matrix` 只在 `SetRefObject` 时缓存初值（`MathElement.cpp:821`/`:833`），真正求值走 `ElementWrapper::EvaluateReal()` 取 Sandbox 实时值——保证循环/积分过程中参数变化能反映到表达式。
- **内存**：树节点由 `MathTree` 析构统一释放（各析构函数注释「all math nodes are deleted in MathTree destructor」），子类析构不 `delete` 子节点，避免双重释放。

### 3.6 模板与头文件内联说明

- 本章**没有任何模板类**。设计依赖**运行时多态**（`virtual Evaluate()/MatrixEvaluate()`），而非编译期模板展开。
- 头文件内联仅两处：`MathNode.hpp:49-60` 的属性访问器（`IsFunction/IsNumber/GetElementType/GetRealValue/GetMatrixValue/SetNumberFlag/SetFunctionInputFlag`，无副作用高频读取）与 `RealUtilities.hpp:148-163` 的 `IsNaN/IsInf`（`inline`，且被 `#ifndef _MSC_VER` 包裹，因 MSVC 下该写法不工作，注释见 `RealUtilities.hpp:138`）。
- `MathNode.hpp:87` 的 `DEFAULT_TO_NO_CLONES` 宏声明了 GmatBase 克隆协议，具体 `Clone()` 在叶子类里以 `new X(*this)` 实现（如 `MathElement.cpp:573-576`）。

## 四、文件清单附录

下表覆盖本章全部 108 个文件（每行一个 `.hpp`/`.cpp` 成对）。基类取自各 `.hpp` 的 `class ... : public ...` 声明（grep 确认）。

| 相对路径 | 职责 | 关键类 / 函数（基类） |
|---|---|---|
| `src/base/math/MathNode.hpp` `.cpp` | 表达式树节点抽象基类 | `MathNode`（GmatBase）：`Evaluate/MatrixEvaluate/GetOutputInfo/ValidateInputs/SetChildren` |
| `src/base/math/MathFunction.hpp` `.cpp` | 二元运算符节点基类 | `MathFunction`（MathNode）：`leftNode/rightNode`、`ValidateScalarInputs/ValidateMatrixInputs` |
| `src/base/math/MathElement.hpp` `.cpp` | 叶节点：参数/数组/字面量绑定 | `MathElement`（MathNode）：`SetWrapperObject/FindWrapper/RenameRefObject` |
| `src/base/math/MathException.hpp` `.cpp` | 本子系统异常 | `MathException`（BaseException） |
| `src/base/math/BuiltinFunctionNode.hpp` `.cpp` | 多参 wrapper 函数基类 | `BuiltinFunctionNode`（MathNode）：`inputArgWrappers/SetMathWrappers/ValidateWrappers` |
| `src/base/math/NumericFunctionNode.hpp` `.cpp` | 数值内置函数基类 | `NumericFunctionNode`（BuiltinFunctionNode） |
| `src/base/math/StringFunctionNode.hpp` `.cpp` | 字符串内置函数基类 | `StringFunctionNode`（BuiltinFunctionNode） |
| `src/base/math/FunctionRunner.hpp` `.cpp` | 表达式内联调用 GmatFunction | `FunctionRunner`（MathFunction）：委托 `FunctionManager::Evaluate` |
| `src/base/math/EquationWrapper.hpp` `.cpp` | 方程→ElementWrapper（CSALT 用） | `EquationWrapper`（ElementWrapper）：`ConstructTree/EvaluateEquation` |
| `src/base/math/Add.hpp` `.cpp` | 加法（含一元 +） | `Add`（MathFunction） |
| `src/base/math/Subtract.hpp` `.cpp` | 减法 | `Subtract`（MathFunction） |
| `src/base/math/Multiply.hpp` `.cpp` | 乘法（矩阵乘法语义） | `Multiply`（MathFunction） |
| `src/base/math/Divide.hpp` `.cpp` | 除法 | `Divide`（MathFunction） |
| `src/base/math/Negate.hpp` `.cpp` | 一元取负 | `Negate`（MathFunction） |
| `src/base/math/Power.hpp` `.cpp` | 幂 x^y | `Power`（MathFunction）：`GmatMathUtil::Pow` |
| `src/base/math/Mod.hpp` `.cpp` | 取模 a mod b | `Mod`（NumericFunctionNode）：`GmatMathUtil::Mod` |
| `src/base/math/Min.hpp` `.cpp` | 最小值（多参） | `Min`（NumericFunctionNode） |
| `src/base/math/Cross3.hpp` `.cpp` | 三维叉积 | `Cross3`（NumericFunctionNode）：`Cross(Rvector3,Rvector3)` |
| `src/base/math/Determinant.hpp` `.cpp` | 行列式 | `Determinant`（MathFunction）：`Rmatrix::Determinant` |
| `src/base/math/Diag.hpp` `.cpp` | 构造对角阵 | `Diag`（NumericFunctionNode） |
| `src/base/math/Inverse.hpp` `.cpp` | 矩阵/标量求逆 | `Inverse`（MathFunction）：`Rmatrix::Inverse` |
| `src/base/math/Norm.hpp` `.cpp` | 向量/标量范数 | `Norm`（MathFunction）：`Rvector::Norm` |
| `src/base/math/Transpose.hpp` `.cpp` | 转置 | `Transpose`（MathFunction）：`Rmatrix::Transpose` |
| `src/base/math/Sin.hpp` `.cpp` | 正弦 | `Sin`（MathFunction）：`GmatMathUtil::Sin` |
| `src/base/math/Cos.hpp` `.cpp` | 余弦 | `Cos`（MathFunction）：`GmatMathUtil::Cos` |
| `src/base/math/Tan.hpp` `.cpp` | 正切 | `Tan`（MathFunction）：`GmatMathUtil::Tan` |
| `src/base/math/Asin.hpp` `.cpp` | 反正弦 | `Asin`（MathFunction）：`GmatMathUtil::ASin` |
| `src/base/math/Acos.hpp` `.cpp` | 反余弦 | `Acos`（MathFunction）：`GmatMathUtil::ACos` |
| `src/base/math/Atan.hpp` `.cpp` | 反正切 | `Atan`（MathFunction）：`GmatMathUtil::ATan` |
| `src/base/math/Atan2.hpp` `.cpp` | 四象限反正切 | `Atan2`（MathFunction）：`atan2(left,right)` |
| `src/base/math/Sinh.hpp` `.cpp` | 双曲正弦 | `Sinh`（MathFunction）：`GmatMathUtil::Sinh` |
| `src/base/math/Cosh.hpp` `.cpp` | 双曲余弦 | `Cosh`（MathFunction）：`GmatMathUtil::Cosh` |
| `src/base/math/Tanh.hpp` `.cpp` | 双曲正切 | `Tanh`（MathFunction）：`GmatMathUtil::Tanh` |
| `src/base/math/Asinh.hpp` `.cpp` | 反双曲正弦 | `Asinh`（MathFunction）：`GmatMathUtil::ASinh` |
| `src/base/math/Acosh.hpp` `.cpp` | 反双曲余弦 | `Acosh`（MathFunction）：`GmatMathUtil::ACosh` |
| `src/base/math/Exp.hpp` `.cpp` | 指数 e^x | `Exp`（MathFunction）：`GmatMathUtil::Exp` |
| `src/base/math/Log.hpp` `.cpp` | 自然对数 ln x | `Log`（MathFunction）：`GmatMathUtil::Log` |
| `src/base/math/Log10.hpp` `.cpp` | 常用对数 log10 x | `Log10`（MathFunction）：`GmatMathUtil::Log10` |
| `src/base/math/Sqrt.hpp` `.cpp` | 平方根 | `Sqrt`（MathFunction）：`GmatMathUtil::Sqrt` |
| `src/base/math/Abs.hpp` `.cpp` | 绝对值 | `Abs`（MathFunction）：`GmatMathUtil::Abs` |
| `src/base/math/Ceil.hpp` `.cpp` | 向上取整 | `Ceil`（MathFunction）：`GmatMathUtil::Ceiling` |
| `src/base/math/Floor.hpp` `.cpp` | 向下取整 | `Floor`（MathFunction）：`GmatMathUtil::Floor` |
| `src/base/math/Fix.hpp` `.cpp` | 向零取整 | `Fix`（MathFunction）：`GmatMathUtil::Fix` |
| `src/base/math/DegToRad.hpp` `.cpp` | 度→弧度 | `DegToRad`（MathFunction）：`GmatMathUtil::DegToRad` |
| `src/base/math/RadToDeg.hpp` `.cpp` | 弧度→度 | `RadToDeg`（MathFunction）：`GmatMathUtil::RadToDeg` |
| `src/base/math/Rand.hpp` `.cpp` | [0,1) 均匀随机数 | `Rand`（MathFunction）：`GmatMathUtil::Rand` |
| `src/base/math/Randn.hpp` `.cpp` | 标准正态随机数 | `Randn`（MathFunction）：`GmatMathUtil::Randn` |
| `src/base/math/Sprintf.hpp` `.cpp` | sprintf 风格格式化输出 | `Sprintf`（StringFunctionNode）：`EvaluateString` |
| `src/base/math/Strcat.hpp` `.cpp` | 字符串拼接 | `Strcat`（StringFunctionNode） |
| `src/base/math/Strcmp.hpp` `.cpp` | 字符串比较（返 Real） | `Strcmp`（StringFunctionNode） |
| `src/base/math/Strfind.hpp` `.cpp` | 子串查找（返 Real） | `Strfind`（StringFunctionNode） |
| `src/base/math/Strlen.hpp` `.cpp` | 串长（返 Real） | `Strlen`（StringFunctionNode） |
| `src/base/math/Strrep.hpp` `.cpp` | 子串替换 | `Strrep`（StringFunctionNode）：`GmatStringUtil::Replace` |
| `src/base/math/Substr.hpp` `.cpp` | 取子串 | `Substr`（StringFunctionNode） |

（共 54 行 × 2 文件 = 108 文件，全部覆盖。）
