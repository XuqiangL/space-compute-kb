# 第16章 文档体系、数据内核与 prototype

本章负责四大板块：(1) `doc/` 文档体系（`help/`、`DevelopersDocs/`、`SystemDocs/`、`ProcessDocs/`、`PapersAndPresentations/`、`styleexample/`、`training/`、`build/`，共 8183 个文件）；(2) `application/data/` 数据内核（行星历表、EOP、大气模型、行星系数等 302 个文件）；(3) `prototype/` 原型与实验代码（全部 1909 个文件）；(4) `ThirdParty/` 与 `Metrics/`（外部依赖与 SLOC 统计）。`doc/` 有 8000+ 文件、`prototype/` 有 1909 个文件，本章采用「目录级说明 + 代表性文件深读 + 表格清单」的覆盖策略，不逐文件讲解。

> 说明：本章范围中的 `application/data/` 行星引力场文件为 `.cof` 格式（GMAT 自定义系数文件），**仓库中不存在 `.grv` 文件**（已用 `glob **/*.grv` 验证为空）；行星引力场与形状系数均以 `.cof` 承载。

## 一、本章目录树

```
L:\gmat888
├── doc/                                          (8183 文件, 514 子目录)
│   ├── .gitignore
│   ├── help/                                     (955 文件)   —— GMAT 用户指南/训练手册 (DocBook XML 源)
│   │   ├── README.txt / README.mac / Makefile / .gitignore
│   │   ├── config/      fop.xconf               —— FOP PDF 排版配置
│   │   ├── files/       images/                 —— 帮助插图
│   │   ├── src/         189 个 DocBook XML + files/{scripts,images}
│   │   └── xform/       fo.xsl, htmlhelp.xsl, 标题页模板 —— XSLT 转换样式
│   ├── DevelopersDocs/                           (151 文件, 8 子目录) —— 开发者文档
│   │   ├── GmatCppStyleGuide.docx               —— C++ 编码规范
│   │   ├── CompilingGMATwithVS2010/             —— 构建流程 (LaTeX)
│   │   ├── GmatBestPractices/                   —— 最佳实践 (Sphinx)
│   │   ├── GenericsAndMethods/                  —— 泛型与方法 (Sphinx)
│   │   ├── UsingCInterface/                     —— C 接口 (LaTeX)
│   │   ├── CSALT/  AddingPhysicalModels/  AddingMeasurementModels/  AddPhysicalModelImages/
│   ├── SystemDocs/                               (985 文件, 11 子目录) —— 系统设计文档
│   │   ├── ArchitecturalSpecification/          —— 架构规格 (LaTeX → PDF)
│   │   ├── MathematicalSpecification/           —— 数学规格 (LaTeX → PDF)
│   │   ├── EstimationSpecification/             —— 估计规格 (LaTeX → PDF)
│   │   ├── ComponentDesigns/ (17 组件)          —— 组件级设计
│   │   ├── APICookbook/  Tools/  PluginDevelopment/  Common/  Requirements/  Test/  Temp/
│   ├── ProcessDocs/                              (7 文件)     —— 项目管理与需求
│   │   ├── ProjectPlanning/ (含 Estimates/)
│   │   └── Requirements/
│   ├── PapersAndPresentations/                   (64 文件, 4 子目录) —— 论文与演讲
│   ├── styleexample/                             (19 文件)    —— DocBook 样式示例
│   ├── training/                                 (4 文件)     —— 训练手册 (DocBook)
│   └── build/                                    (5997 文件)  —— 文档构建工具链
│       └── contrib/  docbook, docbook-xsl-ns-1.78.1, fop-1.1, jing, xalan-j
├── application/
│   └── data/                                     (302 文件, 14 子目录) —— 运行时数据内核
│       ├── api/ atmosphere/ emtg/ graphics/ gravity/ gui_config/ hardware/
│       ├── icrf/ IonosphereData/ misc/ planetary_coeff/ planetary_ephem/ time/ vehicle/
│       └── .gitignore
├── prototype/                                    (1909 文件, 17 子目录) —— 原型/实验代码
│   ├── Attitude/ Auto-NGC/ ccsdsAEM/ ccsdsOEM/ CSALTMatlab/ FiniteBurn/
│   ├── GroundTrackPlot/ interp/ MATLABUtils/ Navigation/ NuMin/ OD/
│   ├── ODPrototype/ OptimalControl/ StateConv/ STMprop/ TAT-C/
├── ThirdParty/  Gmat3rdPartyLinux64.tar.gz       (1 文件)      —— 外部依赖打包
└── Metrics/     R2018a/*.txt                     (3 文件)      —— SLOC 代码量统计
```

---

## 二、逐目录讲解

### 2.1 `doc/help/` —— DocBook 单源发布式帮助系统

GMAT 的用户文档不是手写 HTML，而是用 **DocBook 5.0 XML** 作为单一来源（single-source），再通过 XSLT 工具链同时生成 HTML 帮助（CHM/单页/分块）与 PDF。这一结构从目录布局即可读出：`src/` 存放 DocBook 源，`xform/` 存放转换样式（XSL），`config/` 存放 FOP 排版配置，`files/` 存放运行时复制到输出目录的图片与 CSS，`build/contrib/`（见 2.8）存放第三方工具链。

**目录清单：**

| 相对路径 | 内容 | 数量 |
|---|---|---|
| `doc/help/src/` | DocBook 5.0 XML 源（根文档 + 分章节文件） | 189 个 XML |
| `doc/help/src/files/images/` | 帮助插图（含 `relnotes/` 各版本发布说明截图） | 732 张 |
| `doc/help/src/files/scripts/` | 教程脚本（`.script`/`.m`）与示例数据 | 21 个 |
| `doc/help/src/files/` | `style.css`、`style-chm.css` | 2 个 |
| `doc/help/config/` | `fop.xconf`（Apache FOP PDF 排版配置） | 1 个 |
| `doc/help/xform/` | `fo.xsl`、`htmlhelp.xsl` 及两个标题页模板 | 4 个 |
| `doc/help/` 顶层 | `README.txt`、`README.mac`、`Makefile`、`.gitignore` | 4 个 |

#### 根文档 `help.xml` 的组织方式

`doc/help/src/help.xml`（52 行）是唯一的入口文档，通过 XInclude 组装整本书：

```xml
<book version="5.0" xmlns="http://docbook.org/ns/docbook" ...>
  <info>
    <title>General Mission Analysis Tool (GMAT)</title>
    <subtitle>
      <phrase condition="ug">User Guide</phrase>
      <phrase condition="tm">Training Manual</phrase>
    </subtitle>
    <edition>R2026a</edition>
  </info>
  <xi:include href="Preface.xml"/>
  <xi:include href="Part_UsingGmat.xml"/>
  <xi:include href="Part_Tutorials.xml"/>
  <xi:include href="Part_RefGuide.xml"/>
  <appendix condition="ug" xml:id="ReleaseNotes"> ... 13 个 ReleaseNotes_R20xx.xml ... </appendix>
  <index condition="ug" xml:id="BookIndex" />
</book>
```

要点：
- **单一源、双产出版本**：`<phrase condition="ug">`/`<phrase condition="tm">` 用 DocBook profiling 区分「用户指南（ug）」与「训练手册（tm）」。Makefile 中分别用 `profile.condition ug` 与 `profile.condition tm` 跑 Xalan 预处理器（`profiling/profile.xsl`），产出 `help-pre.xml` 与 `training-pre.xml` 两个中间文档，再各自转 HTML/PDF。
- **四大部分**：`Preface`（前言）、`Part_UsingGmat`（使用 GMAT）、`Part_Tutorials`（教程）、`Part_RefGuide`（参考指南），外加仅用户指南包含的 `ReleaseNotes` 附录与索引。
- **版本号即文档名**：`<edition>R2026a</edition>` 与仓库主版本同步，发布说明从 `ReleaseNotes_R2011a.xml` 一直累积到 `ReleaseNotes_R2026a.xml`（13 个）。

#### 帮助主题组织：三类前缀的 189 个 XML

`src/` 下的 189 个 XML 按文件名前缀组织成清晰的帮助主题树（已统计）：

| 前缀 | 数量 | 含义 | 代表文件 |
|---|---|---|---|
| `Resource_*` | 73 | 资源参考（每个 GMAT 资源一个 refentry） | `Resource_Propagator.xml`、`Resource_Spacecraft.xml`、`Resource_SolarSystem.xml` |
| `Command_*` | 43 | 命令参考 | `Command_Propagate.xml`、`Command_Target.xml`、`Command_Optimize.xml` |
| `Tut_*` | 24 | 教程 | `Tut_SimulatingAnOrbit.xml`、`Tut_LunarTransfer.xml` |
| `Using_*` | 13 | 用户指南章节 | `Using_Welcome.xml`、`Using_Installation.xml`、`Using_ScriptEditor.xml` |
| `ReleaseNotes_*` | 13 | 发布说明 | `ReleaseNotes_R2026a.xml` |
| `System_*` | 12 | 系统级参考 | `System_StartupFile.xml`、`System_ScriptLanguage.xml`、`System_CommandLineUsage.xml` |
| `CommonTask_*` | 4 | 通用任务 | `CommonTask_PropagatingASpacecraft.xml` |
| `Part_*` | 3 | 分部（part）容器 | `Part_UsingGmat.xml`、`Part_Tutorials.xml`、`Part_RefGuide.xml` |
| 其他 | 4 | `help.xml`、`Preface.xml`、`OCFunction_PatchedConicLaunch.xml`、`ToolbarFeatureSpec.xml` | |

#### 代表性文件深读

**① `Part_UsingGmat.xml`（82 行）—— 导航骨架。** 它是「Using GMAT」这一 part 的容器，`<partintro>` 用交叉引用（`<xref>`）串起 Welcome、GettingStarted、TourOfGmat、ConfiguringGmat 等章节，随后用 `<xi:include>` 把各 `Using_*.xml` 挂到对应 `<chapter>` 下。例如 `GettingStarted` 章由 `Using_Installation.xml`、`Using_RunningGmat.xml`、`Using_SampleMissions.xml`、`Using_GettingHelp.xml` 四节组成（第 53–63 行）。这层「part → chapter → 细粒度 XML」的 XInclude 嵌套正是整个帮助体系的可维护性来源：作者只改小文件，导航树在容器文件里维护。

**② `Using_Welcome.xml`（551 行）—— 「欢迎/GMAT 概览」页。** 顶层是 `Welcome to GMAT` 章，第 6–13 行给出项目定位（"the world's only enterprise, multi-mission, open source software system for space mission design, optimization, and navigation"），随后按特性分组（Dynamics and Environment Modeling、Spacecraft Modeling、Optimization 等）以 `<itemizedlist>` 列举能力。它对应任务描述中的「GettingStarted 帮助页」：实际「Getting Started」章节内容在 `Part_UsingGmat.xml` 中由 4 个 `Using_*.xml` 组成，而 `Using_Welcome.xml` 是 Overview 页。

**③ `Resource_Propagator.xml`（3693 行）—— 资源参考页的典型结构。** 它采用 DocBook `refentry` 结构：`<refmeta>`（来源/手册名）、`<refnamediv>`（名称 + 一句话职责「A propagator models spacecraft motion」）、随后多个 `<refsection>`（Overview of Propagator Components、NumericalPropagator、SPKPropagator 等）。第 31–43 行说明 Propagator 分「数值积分型」与「星历型」两类，并指出可配置 SPICE 内核与 Code500/STK/CCSDS 星历文件。这是 73 个 `Resource_*` 页的统一模板。

**④ `Part_RefGuide.xml`（268 行）—— 参考指南导航。** 用 `<partintro>` 说明参考指南按 Resources / Commands / System 三类组织，`<xref>` 交叉引用到每个资源/命令/系统主题。它是从「浏览」进入「查语法」的枢纽。

**⑤ `src/files/scripts/` 教程脚本（21 个）。** 每个教程都配有可运行的 `.script` 脚本（如 `ForceModelsTutorial.script`、`MarsBPlaneTutorial.script`、`Tut_MultipleShootingTutorial_Step1..5.script`），以及 MATLAB 接口示例 `runMatlabToGMAT.m`、`runMatlabToGMATsimple.m`。这些脚本在帮助里以代码块形式被 `<xi:include>` 或复制引用，保证文档示例与实际可运行脚本一致。

#### 构建链与 GUI 帮助按钮的关联

`doc/help/README.txt` 列出生成帮助所需工具：MSYS（MinGW）、Java、HTML Help Workshop（Windows CHM 输出）。`doc/help/Makefile` 定义完整工具链（第 13–22 行）：

- `docbookxsldir = ../build/contrib/docbook-xsl-ns-1.78.1` —— DocBook XSL 样式表；
- `fopdir = ../build/contrib/fop-1.1` —— Apache FOP（XML → PDF）；
- `JING` 用 `jing.jar` 做 RELAX NG 校验（`docbookxi.rng`）；
- `XALAN` 用 `org.apache.xalan.xslt.Process` 做 XSLT 转换。

Makefile 目标（`README.txt` 第 33–41 行）：`all`/`chm`/`html`/`pdf`/`help`/`training`/`clean`/`validate`；`html` 产出 `help.html`（单页）与 `html/index.html`（分块 chunked），`pdf` 产出 `help-letter.pdf` 与 `help-a4.pdf`。

**GUI 帮助按钮的接线在 `gmat_startup_file.txt` 中显式给出**（第 198–201 行）：

```
HELP_PATH                  = ROOT_PATH/docs/help
HELP_HTML_USING_GMAT_FILE  = HELP_PATH/html/UsingGmat.html
HELP_HTML_TUTORIALS_FILE   = HELP_PATH/html/Tutorials.html
HELP_HTML_FILE             = HELP_PATH/help.html
```

即：GUI 的「帮助」菜单/按钮指向构建产物 `docs/help/` 下的 HTML（`UsingGmat.html`、`Tutorials.html`、`help.html`）。`Part_UsingGmat.xml` 的 `xml:id="UsingGmat"` 与 `Part_Tutorials.xml` 的 `xml:id` 经 `use.id.as.filename` 参数（Makefile 第 132、146 行）映射为对应 HTML 文件名，从而 XML 的 id 与 GUI 要打开的 HTML 文件名一一对应。`docs/` 目录是构建产物目录，不在仓库源码中（仓库只保留 `doc/` 源 + `build/` 工具链）。

---

### 2.2 `doc/DevelopersDocs/` —— 开发者文档

| 子目录 | 文件数 | 格式 | 内容 |
|---|---|---|---|
| `GmatCppStyleGuide.docx` | 1 | Word | C++ 编码风格规范（顶层文件） |
| `CompilingGMATwithVS2010/` | 22 | LaTeX + EPS/PNG | VS2010 下编译 GMAT 的图文流程（含 `CompilingGMATwithVS2010.pdf`、`README.txt`、`Makefile.nmake`） |
| `GmatBestPractices/` | 10 | Sphinx RST | 开发者最佳实践（Development/Configuration/Repositories/Testing） |
| `GenericsAndMethods/` | 10 | Sphinx RST | 脚本对象上的泛型与方法接口说明 |
| `UsingCInterface/` | 7 | LaTeX | 使用 C 接口的文档（`UsingCInterface.tex` + 示例 `CInterfaceFunctions.hpp`、`defaultConfig.script`） |
| `AddingPhysicalModels/` | 5 | LaTeX | 新增物理模型的指南（`AddingPhysicalModel.tex` + 图） |
| `AddingMeasurementModels/` | 2 | PDF/PPTX | 新增测量模型的指南（`GMAT-MeasurementModelRefactoring-110315-1145-40.pdf`） |
| `AddPhysicalModelImages/` | 1 | PNG | 物理模型子系统图 |
| `CSALT/` | 93 | 混合 | CSALT（最优控制配点法求解器）设计/构建/测试文档（见下） |

**深读：**

**① `GmatBestPractices/source/index.rst`（25 行）—— Sphinx 骨架。** 用 `toctree` 挂 Development、Configuration、Repositories、Testing 四个 RST。该目录是 Sphinx 项目（`conf.py` + `Makefile`/`make.bat`），代表 GMAT 2019 年后将开发者文档迁往 Sphinx/reST 的趋势（与 `SystemDocs/APICookbook`、`SystemDocs/Tools` 同构）。

**② `GenericsAndMethods/source/Overview.rst`（9 行）—— 文档摘要。** 说明 GMAT 允许在脚本对象上设置「方法」，方法参数可编码为有限集合的任意类型，简化脚本接口。

**③ `CompilingGMATwithVS2010/`**：`README.txt` 与 `CompilingGMATwithVS2010.tex` 配合 `RawImages/*.PNG`（编译为 EPS 供 LaTeX 引用）图文并茂说明 VS2010 编译步骤——文件夹结构、包含/库路径、Matlab 文件夹设置、DLL Release 配置等。是历史构建流程的权威记录（当前构建已迁移到 CMake，参见 `build/` 与 CMake 相关章节）。

**④ `CSALT/`**：93 个文件覆盖 CSALT 全生命周期——`Building CSALT.docx`、`BuildingCSALTonLinux.pdf`、`IntegratedCsaltBuildInstructions.txt`（构建）、`AddingATestCase.docx`、`CSALT_Test_System.pdf`（测试）、`CollocationPDR.pptx`、`DesignOnePager.docx`（设计）、`Benchmarking/`（基准测试 TeX/图）、`uml/`（UML 类图 .uxf）、`VisParadigm/`（Visual Paradigm 设计图）。CSALT 是 GMAT 最优控制的配点法（collocation）求解器，本章后文 `prototype/CSALTMatlab/` 是其 MATLAB 原型。

---

### 2.3 `doc/SystemDocs/` —— 系统设计文档

| 子目录 | 文件数 | 格式 | 内容 |
|---|---|---|---|
| `ArchitecturalSpecification/` | 412 | LaTeX → PDF | GMAT 架构规格说明书（权威架构文档） |
| `MathematicalSpecification/` | 152 | LaTeX → PDF | 数学规格说明书（`GMATMathSpec.pdf`） |
| `EstimationSpecification/` | 141 | LaTeX → PDF | 估计/定轨规格（`GMATEstimationSpecification.pdf`） |
| `ComponentDesigns/` | 133 | 混合 | 17 个组件级设计文档 |
| `Tools/` | 88 | Sphinx | API/CSALT 工具文档 |
| `APICookbook/` | 19 | Sphinx | API 使用手册（Python 示例） |
| `PluginDevelopment/` | 13 | LaTeX + 代码 | 插件开发指南（`PluginDevelopment.pdf` + 太阳帆示例代码） |
| `Common/` | 7 | LaTeX | 共享表格/封面 |
| `Test/` | 14 | 混合 | 测试规程、需求-测试矩阵 |
| `Requirements/` | 1 | xlsx | GMAT 需求表 |
| `Temp/` | 5 | 混合 | 临时测量规格草稿 |

**深读：**

**① `ArchitecturalSpecification/` —— 架构规格（本章核心参考资料）。** 这是 GMAT 最权威的架构文档，LaTeX 源按主题拆成 50+ 个 `.tex`（`TopLevel.tex`、`CoreClasses.tex`、`Factories.tex`、`FactoryManager.tex`、`Moderator.tex`、`Sandbox.tex`、`SolarSystem.tex`、`Propagators.tex`、`Solvers.tex`、`SpacecraftDesign.tex`、`GmatGui.tex`、`GmatWorkFlow.tex`、`DesignPatterns.tex`、`ExtendingGMAT.tex`、`GmatGlossary.tex` 等），由 `GMAT-Architectural-Specification.tex` 汇总编译为 `GMAT-Architectural-Specification.pdf`。

- `Philosophy.tex`（9 行）是设计哲学章，小节只有标题（Approach to Meeting Requirements / Design Philosophy / Extendability Considerations / Platform Considerations），是半成稿。
- `CoreClasses.tex`（1045 行）是重量级章节，第 2 行标题点明「The GmatBase Class, Constants, and Defined Types」。第 8–36 行给出 `gmatdefs.hpp` 中定义的类型别名表（`Real=double`、`Integer=int`、`Byte=unsigned char`、`RealArray=std::vector<Real>`、`ObjectArray=std::vector<GmatBase*>` 等）；第 46–53 行说明所有资源与命令对象都是 `GmatBase` 派生类，工厂（见 `Factories.tex`）生成它们，`GmatBase` 定义了一组统一的构建/配置/维护/存储接口；第 61–67 行把 `GmatBase` 的方法分类为构造/析构/静态方法、对象管理接口、脚本/GUI/外部通信接口、引用与自有对象属性、属性管理接口、以及 Real/Integer/String/其他属性类型的读写接口。该章与源码 `src/base/` 中的 `GmatBase` 一一对应，是理解整个对象模型的第一入口（交叉引用：核心类详解见 base 相关章节）。

**② `MathematicalSpecification/` —— 数学规格。** `GMATMathSpec.pdf` 由 40+ 个 `.tex` 组成，覆盖 `NBodyGravity.tex`、`CoordinateSystems.tex`、`Attitude.tex`、`EnvironmentModels.tex`、`DynamicsModelling.tex`、`Events.tex`、`NumericalAlgorithms.tex`、`MeasurementModels.tex`、`MeasurementErrorModeling.tex` 等，是力模型/坐标系/姿态/测量模型背后的公式依据。

**③ `EstimationSpecification/` —— 估计规格。** `GMATEstimationSpecification.pdf` 与 `Images/*.eps`（BatchEstimator、EventLocation、Measurement 类图等）对应定轨/滤波子系统。

**④ `APICookbook/` 与 `Tools/API/` —— Sphinx API 文档。** `APICookbook/source/` 含 `propagation.rst`、`stmpropagation.rst`、`finiteBurn.rst`、`commandfunctions.rst` 等食谱式说明，配套 `source/code/*.py` 可运行 Python 示例（`Propagation.py`、`STMPropagation.py`）。`Tools/source/API/` 是更大的 API 文档工程，`source/` 下分 `intro/`、`design/`、`userguide/`、`referenceguide/`、`appendix/`。

**⑤ `PluginDevelopment/` —— 插件开发指南。** `PluginDevelopment.tex`/`.pdf` 配合 `Code/GmatPluginFunctions.{hpp,cpp}`、`SailFactory.{hpp,cpp}`、`SolarSailForce.{hpp,cpp}` 给出一个完整的太阳帆力模型插件示例，是插件作者（工厂注册、力模型派生）的官方模板。

---

### 2.4 `doc/ProcessDocs/` —— 过程文档

7 个文件，两级目录：

| 相对路径 | 内容 |
|---|---|
| `ProjectPlanning/ProductionReleasePlan.doc` | 生产发布计划 |
| `ProjectPlanning/GMATNavVer1.xlsx` / `NavHighLevelSchedule.xls` / `FiniteBurnSolarSystem.xlsx` | 导航/有限推力排期 |
| `ProjectPlanning/Template_FeatureAreaPlanning.docx` | 特性区规划模板 |
| `ProjectPlanning/Estimates/R2012aM3/EventLocator_R2012aM3.xlsx` | R2012a M3 事件定位器工作量估算 |
| `Requirements/Build1Requirements.doc` | 构建 1 需求文档 |

属于历史项目过程产物，反映 GMAT 在 NASA 体系下的发布排期与需求管理方式。

---

### 2.5 `doc/PapersAndPresentations/` —— 论文与演讲

| 子目录 | 内容 |
|---|---|
| `AIAA Astro Specialist ACE Ops Cert Paper/` | AIAA Space 2014 论文（ACE 运行认证）—— Qureshi/Rizwan docx+pdf+投稿确认 |
| `AIAA Astro Specialist V&V Paper/` | GMAT V&V（验证与确认）论文/演讲 + ScholarOne 投稿页快照 |
| `DeveloperTalks/` | 开发者讲座：`GMAT Architecture.ppt`、`Compiling GMAT.pptx`、`PluginWalkthroughForVS2010/`（含 `PluginWalkthrough.tex`/`.pdf`） |
| `MadridFY10-ICATT/` | 2010 年马德里 ICATT 会议论文（Conway & Hughes），LaTeX 源（`ConwayHughes.tex`、`SystemOverview.tex`、`plugin.tex` 等） |

其中 `DeveloperTalks/GMAT Architecture.ppt` 与 `MadridFY10-ICATT/ConwayHughes.pdf` 是理解 GMAT 早期架构（工厂子系统、力模型类、任务树）的历史资料，与 `ArchitecturalSpecification` 互补。

---

### 2.6 `doc/styleexample/` —— DocBook 样式示例

19 个文件，是一个最小化的 DocBook 工程，作用是**给帮助文档作者演示规范写法**：

```
styleexample/
├── Makefile
├── config/fop.xconf
├── src/
│   ├── GmatStyleExample.xml          —— 样式示例主文档（book 根）
│   ├── HowTo-ReportingData.xml        —— "How-to" 示例
│   ├── HowTo-SampleElements.xml       —— 元素用法示例
│   ├── Tut_PropSpacecraft.xml         —— 教程示例
│   └── media/img/*.png|jpeg           —— 示例插图
└── xform/fo.xsl
```

`GmatStyleExample.xml`（46 行）用 `<part>`/`<partintro>` 组织 How-tos 与 Tutorials 两个 part，`<xi:include ... xpointer="element(/1)">` 方式引入各示例文件。它与 `doc/help/` 使用完全相同的 DocBook 5.0 + XInclude 约定，是作者模仿的样板。

---

### 2.7 `doc/training/` —— 训练手册

4 个文件：`Makefile`、`config/fop.xconf`、`src/GmatTrainingManual.xml`、`xform/fo.xsl`。与 help 共享同一套 DocBook 工具链，但 `GmatTrainingManual.xml` 是训练手册的独立入口（对应 help 中 `profile.condition tm` 分支的训练版）。

---

### 2.8 `doc/build/` —— 文档构建工具链（第三方，勿改）

5997 个文件全部在 `contrib/` 下，是文档构建所需的第三方工具，随仓库打包以便离线构建：

| 子目录 | 文件数 | 用途 |
|---|---|---|
| `fop-1.1/` | 4075 | Apache FOP 1.1（XML-FO → PDF）及其自带文档 |
| `docbook-xsl-ns-1.78.1/` | 1859 | DocBook XSL 1.78.1 样式表（namespaced） |
| `jing/` | 56 | Jing RELAX NG 校验器 |
| `xalan-j/` | 6 | Apache Xalan-J XSLT 处理器 |
| `docbook/` | 1 | DocBook schema（`docbookxi.rng`） |

这些目录不是 GMAT 代码，也不是最终交付物；`doc/help/Makefile` 与 `doc/styleexample/Makefile`、`doc/training/Makefile` 通过 `contribdir = ../build/contrib` 引用它们。

---

### 2.9 `application/data/` —— 数据内核（本章重点）

`application/data/` 是 GMAT 运行时读取的全部科学数据，共 302 个文件、14 个顶层目录。这些文件**不是**可执行代码，而是行星历表、地球定向参数、引力场系数、大气模型系数、时间尺度数据等，由 GMAT 内核按 `gmat_startup_file.txt` 声明的路径在启动时定位。

#### 启动加载流程：`gmat_startup_file.txt`

启动文件位于 `application/bin/gmat_startup_file.txt`（`application/debug/` 下另有一份同内容副本）。它的核心约定（第 1–30 行注释）：
- 路径属性以 `_PATH` 结尾、文件名属性以 `_FILE` 结尾；
- 相对路径相对于 GMAT 可执行文件（Linux/OS X 为 app bundle）；
- 势函数文件属性以天体名 + `_POT_FILE` 结尾、纹理以 `_TEXTURE_FILE` 结尾；
- 同一 `_FILE` 多次出现取最后一条；
- 插件按 `PLUGIN =` 行声明并按顺序加载（第 48–83 行）。

数据相关的关键映射（行号已核实）：

| 行 | 变量 | 值 | 用途 |
|---|---|---|---|
| 94 | `ROOT_PATH` | `../` | 安装根目录锚点 |
| 114 | `DATA_PATH` | `ROOT_PATH/data/` | 数据根 |
| 117–118 | `PLANETARY_EPHEM_SPK_PATH` / `PLANETARY_SPK_FILE` | `data/planetary_ephem/spk/` + `DE421AllPlanets.bsp` | 默认 SPK 行星历表内核 |
| 120–123 | `DE405_FILE` / `DE421_FILE` / `DE424_FILE` | `planetary_ephem/de/leDE1941.405` / `leDE1900.421` / `leDE18002100.424` | ASCII DE 历表 |
| 128–136 | `PLANETARY_COEFF_PATH` 组 | `EOP_FILE=eopc04_08.62-now`、`NUTATION_COEFF_FILE=NUTATION.DAT`、`PLANETARY_PCK_FILE=SPICEPlanetaryConstantsKernel.tpc`、`EARTH_LATEST_PCK_FILE=earth_latest_high_prec.bpc`、`EARTH_PCK_PREDICTED/CURRENT`、`LUNA_PCK_CURRENT`、`LUNA_FRAME_KERNEL_FILE` | 行星系数、EOP、章动、SPICE 行星常数/地球月球定向内核 |
| 138–140 | `TIME_PATH` / `LEAP_SECS_FILE` / `LSK_FILE` | `time/tai-utc.dat`、`time/SPICELeapSecondKernel.tls` | 跳秒表 |
| 142–153 | `EARTH/LUNA/MARS/VENUS/OTHER_POT_PATH` + `EGM96_FILE`、`JGM2_FILE`、`JGM3_FILE`、`MARS50C_FILE`、`MGNP180U_FILE`、`LP165P_FILE` | 各天体引力场系数路径 | 引力场 `.cof` |
| 155–156 | `GUI_CONFIG_PATH` / `PERSONALIZATION_FILE` | `gui_config/MyGmat.ini` | GUI 个性化配置 |
| 158–182 | `ICON_PATH`、`SPLASH_PATH`、`TEXTURE_PATH`（`SUN_TEXTURE_FILE`…`PLUTO_TEXTURE_FILE`）、`STAR_PATH`（`STAR_FILE`、`CONSTELLATION_FILE`、`BORDER_FILE`） | 图标/闪屏/行星纹理/星表 | 可视化资源 |
| 184–188 | `VEHICLE_MODEL_PATH`（`aura.3ds`）、`SPAD_PATH`（`SphericalModel.spo`） | 航天器模型与太阳光压板模型 | |
| 190–196 | `ATMOSPHERE_PATH` 组 | `CSSI_FLUX_FILE=SpaceWeather-All-v1.2.txt`、`SCHATTEN_FILE`、`MARINI_TROPO_FILE`、`EARTH/MARS_EXPONENTIAL_FILE` | 大气模型数据 |
| 198–201 | `HELP_PATH` 组 | `docs/help/...` | GUI 帮助 HTML（见 2.1） |
| 203 | `ICRF_FILE` | `data/icrf/ICRF_Table.txt` | ICRF 参考架表 |

加载语义：GMAT 启动时解析此文件，把 `_PATH`/`_FILE` 变量灌入配置系统；随后按需（而非一次性）读取各数据文件——例如建 `SolarSystem` 时读取行星常数与 DE 历表、启用章动时读 `NUTATION.DAT`、做 UTC↔TAI 换算时读 `tai-utc.dat`、用 JGM/EGM 引力模型时读对应 `.cof`。

#### 2.9.1 `planetary_ephem/` —— 行星历表内核

| 文件 | 大小 | 说明 |
|---|---|---|
| `spk/DE421AllPlanets.bsp` | 22.4 MB | 默认 SPK 内核（启动文件第 118 行），DE421 系列，含全部行星 |
| `spk/DE405AllPlanets.bsp` | 19.4 MB | DE405 系列 SPK（由 JPL 的 de405 + 行星卫星内核合并，见其 Readme） |
| `spk/DE424AllPlanets.bsp` | 22.3 MB | DE424 系列 SPK |
| `spk/de421.bsp` | 16.8 MB | 独立 DE421 内核 |
| `spk/ceres_1900_2100.bsp` | 1.1 MB | 谷神星（矮行星）星历 |
| `spk/Readme-DE40xAllPlanets.txt` ×3 | 26–29 KB | 每个内核的摘要（用 SPICE `spaceit` 生成的分段清单） |
| `de/leDE1941.405` | 24.2 MB | ASCII DE405（1941 起） |
| `de/leDE1900.421` | 14.0 MB | ASCII DE421 |
| `de/leDE18002100.424` | 37.2 MB | ASCII DE424（1800–2100） |

两类内核并存：**SPK（`.bsp`）是二进制 SPICE 内核**，**`de/` 下的 `leDE*.xxx` 是 ASCII DE 历表**（JPL 传统格式，GMAT 有自己的 DE 读取器）。`spk/.gitignore`（36 行）揭示了一个关键事实：`.bsp` 体积大、随发行包分发时被选择性包含——文件列出 30+ 个「忽略」的内核（`jup230-long.bsp`、`sat288.bsp`、`plu017.bsp`、各小行星/彗星内核、`*.bsp` 通配），说明仓库只提交少数核心内核，其余按需从 NAIF/JPL 下载。`Readme-DE405AllPlanets.txt` 第 1–26 行显示内核分段信息：`Target Body=MARS, Center Body=MARS BARYCENTER, Frame=J2000, SPK Data Type=Type 2 (Fixed Width Chebyshev), 时间跨度 1990–2050`。

#### 2.9.2 `planetary_coeff/` —— 行星系数、EOP、章动

| 文件 | 大小 | 说明 |
|---|---|---|
| `eopc04_08.62-now` | 3.7 MB | **EOP 文件**（IERS C04 系列，旧格式），启动文件 `EOP_FILE` |
| `NUTATION.DAT` | 34.9 KB | IAU 2000 章动理论 106 项系数（`NUTATION_COEFF_FILE`） |
| `SPICEPlanetaryConstantsKernel.tpc` | 135 KB | SPICE 行星常数文本内核（PCK） |
| `earth_latest_high_prec.bpc` | 5.0 MB | 地球高精度二进制 PCK（最新） |
| `SPICEEarthCurrentKernel.bpc` | 12.1 MB | 地球当前定向二进制 PCK |
| `SPICEEarthPredictedKernel.bpc` | 19.2 MB | 地球预测定向二进制 PCK |
| `SPICELunaCurrentKernel.bpc` | 1.8 MB | 月球当前定向二进制 PCK |
| `SPICELunaFrameKernel.tf` | 22 KB | 月球参考架定义内核（FK） |

**EOP 文件深读：** `eopc04_08.62-now` 头部（第 1–13 行）标明来源（Paris Observatory / IERS）、格式 `FORMAT(3(I4),I7,2(F11.6),...)`，列含义为 `Date MJD x y UT1-UTC LOD dPsi dEps xErr yErr ...`；数据从 1962-1-1 起每日一行（共 23647 行），文件名中的 `now` 表示它持续更新到最新（IERS 提供「从 1962 到 now」的连续序列）。这是 GMAT 计算地球自转（UT1、极移 x/y、LOD、章动偏差 dPsi/dEps）的原始数据，用于把 J2000 惯性系与地球固连系（ITRF）互转。

**章动系数深读：** `NUTATION.DAT` 第 1 行说明是「2000 IAU Theory of Nutation (106 term)」，第 3 行起每行给出 5 个倍率 `a2 a3 a4 a5`、系数 `A B C D E F`（单位 0.0001"）与项序号——这是标准 IAU2000 章动序列的 ASCII 表，GMAT 的章动计算直接查此表。

**PCK/TF 内核：** `.tpc` 是文本行星常数内核（行星半径、自转周期、重力常数等），`.bpc` 是二进制行星常数/定向内核（高精度地球/月球定向），`.tf` 是参考架定义内核。`SPICELunaFrameKernel.tf`（607 行）头部说明它是 NAIF/JPL 月球参考架规范，与月球二进制 PCK（`moon_pa_de421_1900-2050.bpc`）配套，定义 MOON_ME / MOON_PA 等月固连参考架。

#### 2.9.3 `time/` —— 跳秒表

| 文件 | 说明 |
|---|---|
| `tai-utc.dat`（41 行） | GMAT 自用跳秒表（`LEAP_SECS_FILE`）。格式 `1961 JAN 1 =JD ... TAI-UTC=...`，覆盖 1961–2017 全部跳秒（2017-1-1 为 37 秒），含 1972 年前的速率项 `+(MJD-...)*X 0.001296` |
| `SPICELeapSecondKernel.tls`（152 行） | SPICE 跳秒内核（`LSK_FILE`）。含完整修改历史注释与 `DELTET/DELTA_AT`（1972-1-1 起整秒跳秒表）、`DELTA_T_A=32.184`、`K=1.657e-3`、`EB`、`M0/M1` 等 ET↔UTC 换算参数 |

两份跳秒表并存：`tai-utc.dat` 供 GMAT 内部时间系统（`TimeSystemConverter` 等）使用，`SPICELeapSecondKernel.tls` 供 SPICE 接口做 UTC↔ET 换算（`DELTA_ET = ET - UTC`，见该文件第 50–112 行 Moyer 公式说明）。

#### 2.9.4 `gravity/` —— 引力场系数（`.cof`）

| 目录/文件 | 天体 | 说明 |
|---|---|---|
| `earth/EGM96.cof`（3.98 MB） | 地球 | EGM96 360×360 引力场（`EGM96_FILE`） |
| `earth/EGM96low.cof` | 地球 | EGM96 低阶截断版 |
| `earth/JGM2.cof` / `JGM3.cof`（154 KB） | 地球 | JGM2/JGM3 70×70 引力场（`JGM2_FILE`/`JGM3_FILE`） |
| `earth/JGM2F70.cof` | 地球 | JGM2 70 阶固定截断版 |
| `luna/LP165P.cof`（842 KB） | 月球 | LP165P 165 阶引力场（`LP165P_FILE`） |
| `luna/grgm900c.cof`（3.99 MB） | 月球 | GRAIL GRGM900C 高阶引力场 |
| `luna/grgm900c.tide` | 月球 | GRGM900C 潮汐参数（113 字节） |
| `mars/Mars50c.cof`（80 KB） | 火星 | Mars50c 50 阶引力场（`MARS50C_FILE`） |
| `mars/GMM1.cof` / `GMM2B.cof` | 火星 | 早期 Goddard Mars Model |
| `venus/MGNP180U.cof`（154 KB） | 金星 | MGNP180U 引力场（`MGNP180U_FILE`） |
| `venus/MGN75HSAAP.cof` | 金星 | MGN 系列引力场 |

**`.cof` 格式深读：** `earth/EGM96.cof` 第 1–7 行是 `COMMENT 5` 头 + 注释块（来源 `egm96_to360.ascii`，360×360，epoch 1986），随后 `POTFIELD360360  1  3.986004415e+14  6.3781363e+06  1.0` 一行给出阶次、归一化标志、GM（m³/s²）、参考半径（m），再后每行 `RECOEF n m Cnm Snm` 给出（归一化）球谐系数对。这是 GMAT 自定义的 ASCII 引力系数格式（首字母 `POTFIELD` + 阶数 + `RECOEF` 记录），由 `GravityFile`/`HarmonicGravity` 读取。

#### 2.9.5 `atmosphere/` —— 大气模型数据

| 目录/文件 | 说明 |
|---|---|
| `earth/EarthExponentialAtmosphereData.txt`（28 行） | 地球指数大气密度模型表（`EARTH_EXPONENTIAL_FILE`），格式 `高度(km), 密度(kg/m³), 标高(km)`，覆盖 0–1000 km |
| `earth/marini.dat`（5.7 KB） | Marini 对流层延迟模型系数（`MARINI_TROPO_FILE`） |
| `earth/SchattenPredict.txt`（25.8 KB） | Schatten 太阳活动预测（`SCHATTEN_FILE`） |
| `earth/SpaceWeather-All-v1.2.txt`（3.49 MB） | CSSI 空间天气历史序列（`CSSI_FLUX_FILE`，F10.7 等） |
| `earth/SpaceWeather-v1.2.txt`（486 KB） | 空间天气数据（较小子集） |
| `mars/MarsExponentialAtmosphereData.txt`（6.5 KB） | 火星指数大气模型表（`MARS_EXPONENTIAL_FILE`） |
| `Msise86_Data/msis86.dat`（19.9 KB） | MSIS-86 大气模型系数（供 `libMsise86` 专用插件使用） |

`EarthExponentialAtmosphereData.txt` 每行 `高度, 密度, 标高` 三列，从海平面 1.225 kg/m³ 到 1000 km 的 3.019e-15 kg/m³，是 GMAT 内置「指数大气模型」的插值表。`msis86.dat`（293 行）是 MSIS-86 的裸浮点系数表，无注释头，由 `Msise86` 插件读取（MSISE-00 已内置，MSIS-86 作为专用插件 `libMsise86` 保留）。

#### 2.9.6 `icrf/` 与 `IonosphereData/`

- `icrf/ICRF_Table.txt`（4.16 MB，49063 行）：ICRF 参考架表（`ICRF_FILE`）。格式为 4 列逗号分隔（`MJD, X, Y, Z`，见第 1 行 `6935.000000397937, 2.679e-8, ...`），给出地球在 ICRF 中随时间的状态向量，供深空参考架转换使用。
- `IonosphereData/`（45 个文件）：国际参考电离层（IRI）模型系数——`ccir*.asc`（CCIR 系数 11–22 月）、`ursi*.asc`（URSI 系数）、`igrf*.dat`/`dgrf*.dat`（国际/确定性地磁参考场系数，含 1900–2010 各年代）、`ig_rz.dat`（太阳黑子数）、`ap.dat`（Ap 指数）。这些是 `IonosphereData`/电离层延迟模型的输入。

#### 2.9.7 其余数据目录（逐目录要点）

| 目录 | 内容 |
|---|---|
| `graphics/icons/`（约 150 个 PNG/ICO/ICNS/XPM/JPG） | GUI 图标（`rt_*` 资源树、`mt_*` 任务树、`mtc_*` 任务控制、各天体图标、`GMATWin32.ico`、`GMATIcon.icns` 等） |
| `graphics/splash/` | 启动闪屏 `GMATSplashScreen.png/.tif` + BETA 版 |
| `graphics/texture/`（12 张 JPG） | 各行星纹理（`ModifiedBlueMarble.jpg` 地球、`Mars_JPLCaltechUSGS.jpg` 等，对应启动文件 `*_TEXTURE_FILE`） |
| `graphics/stars/` | 星表 `inp_StarCatalog.txt`（1.1 MB）、星座 `inp_Constellation.txt`、星座边界 `inp_Border.txt` |
| `graphics/models/` | 彗星模型 `Comet_Hartley_Green.3ds` |
| `vehicle/ephem/ccsds/` | CCSDS 星历示例（`.oem` 轨道、`.aem` 姿态） |
| `vehicle/ephem/spk/` | 航天器 SPK 内核（`GEOSat.bsp`、`MoonTransfer.bsp`、`MarsExpress_*`） |
| `vehicle/ephem/code500/` | Code500 格式 `sat_leo.ephem` |
| `vehicle/ephem/stk/` | STK 格式 `SampleSTKEphem.e` |
| `vehicle/models/` | 航天器模型 `aura.3ds` + 贴图 `aura_map.jpg` |
| `vehicle/spad/` | 太阳光压板模型 `SphericalModel.spo`（`SPAD_SRP_FILE`）、`JWST-10cm1R.spo`（JWST 光学遮阳模型） |
| `gui_config/`（10 个 .ini） | GUI 各资源面板配置（`MyGmat.ini`、`SNOPT.ini`、`Yukon.ini`、`VF13ad.ini`、`ChemicalTank.ini`、`Antenna.ini`、`Receiver/Transmitter/Transponder.ini`、`GroundTrackPlot.ini`、`ElectricTank.ini`） |
| `api/GmatHelp.rst`（412 行） | GMAT API 的 reST 帮助文本（`TopLevel`/`ScriptUsage`/`Commands`/`Groups`/`Objects` 等标签，供 Python/Java/MATLAB API 的 `Help()` 查询） |
| `emtg/`（8 个文件） | EMTG（进化任务轨迹生成器）配置：`*.emtg_spacecraftopt`、`*.emtg_launchvehicleopt`、`*.ThrottleTable` |
| `hardware/ConeClockAngles` | 天线锥形/时钟角硬件数据 |
| `misc/` | 最优控制历史 `*.och`（`EarthToMars_Solution.och` 等）、`SNOPTSPECfile.txt`（SNOPT 规格示例） |

---

### 2.10 `prototype/` —— 原型与实验代码

`prototype/` 是 1909 个文件、17 个顶层子目录的**研发原型/实验代码集合**，与 `src/` 生产代码分离。扩展名分布印证其性质：**`.m`（MATLAB）1106 个**、`.truth` 93 个、`.cpp` 78 个、`.MissionPlan` 78 个、`.txt` 74 个、`.hpp` 71 个、`.py` 69 个、`.AsStateCalc` 39 个、`.mat` 33 个、其余为 `.sa`/`.script`/`.aem`/`.oem`/`.fig` 等。即：**主体是 MATLAB 原型 + 少量 C++/Python 移植 + 大量真值数据（`.truth`）与 GMAT 脚本产物**，用于在进入生产代码前验证算法，并与生产实现做真值对比。

#### 各子目录讲解

| 子目录 | 文件数 | 内容与定位 |
|---|---|---|
| `CSALTMatlab/` | 460 | CSALT（最优控制配点法）的 MATLAB 原型，含 `+collutils`/`+userfunutils`/`+ephemfileutils`/`+exec` 包、`TestProblems/`（233 个测试问题）、`PhysicalModels/`、`UnitTest/`。与 `doc/DevelopersDocs/CSALT/`、生产代码 CSALT 对应 |
| `StateConv/` | 429 | 轨道状态转换函数库（Cart↔Keplerian/Equinoctial/Delaunay 等）+ `test/truth/` 大量 STK 真值对比数据 |
| `OptimalControl/` | 265 | 最优控制原型（低推力、动力学、边界函数），含 `PythonPrototypes2019/`、`docs/BoundaryFunctionUserGuide` |
| `TAT-C/` | 231 | Tradespace Analysis Tool for Constellations（GSFC 星座权衡分析工具），含 `cpp/`（`src`/`GMATsrc`/`test`）与 `matlab/` 两版 |
| `NuMin/` | 198 | 数值最小化（NLP）求解器 MATLAB 原型：`solvers/`（`MiNLPClass.m`、`MinQP.m`、`Uncmin.m`、`UncTrust.m`、`WolfeLineSearch.m` 等）+ `doc/` + `test/` |
| `Navigation/` | 97 | 导航原型（`TDRSS_Doppler/` 含 `constants`/`dynamics`/`measurements`/`math`/`time` 等子目录） |
| `OD/` | 80 | 轨道确定 MATLAB 原型（`src/@BatchEstimator`、`@Spacecraft`、`@Propagator`、`@Measurement` 等类 + `scripts/`），依赖 Vallado 天文动力学工具 |
| `STMprop/` | 51 | 状态转移矩阵传播原型（`FM_Earth_*.m` 力模型配置 + `deriv_*.m` 导数 + `dynfunc.m`） |
| `ccsdsAEM/` | 34 | CCSDS 姿态星历消息（AEM）MATLAB 类（`@AttitudeEphemeris`、`@QuaternionSegment` 等） |
| `Attitude/` | 14 | 姿态 DCM 计算原型（对齐约束坐标系） |
| `ccsdsOEM/` | 14 | CCSDS 轨道星历消息（OEM）MATLAB 类（`@Ephemeris`、`@EphemerisSegment`） |
| `ODPrototype/` | 12 | 轨道确定原型脚本（`RunEstimator.m`、`RunPrototype.m`、`TheBigPicture.m` 等） |
| `Auto-NGC/` | 7 | 自动化导航地面接触（Next Generation Contact）配置/驱动/输出 |
| `FiniteBurn/` | 7 | 有限推力机动原型（`TankModels/` 推进剂箱模型） |
| `GroundTrackPlot/` | 5 | 地面轨迹绘图原型（`GroundTrack.m` + `.script` + 真值） |
| `interp/` | 3 | 插值器类原型（`@Interpolator`、`@LagrangeInterpolator`） |
| `MATLABUtils/` | 2 | MATLAB 工具（`EOPFileWriter.m` 写 EOP 文件 + 测试） |

#### 代表性文件深读（8 个）

**① `TAT-C/README.txt`（22 行）—— 项目级说明。** 声明 TAT-C 是 MATLAB 工具（R2015b 测试），配置脚本 `SystemConfigurationScript.m` 设置 `installDir`，测试驱动 `TATC_APITestDriver_Minimal.m` / `TATC_APITestDriver_Analysis.m` 展示 API 与覆盖率统计。

**② `Attitude/ComputeAlignConstrainedDCM.m`（40 行）—— 姿态算法。** 用欧拉轴/角法分两步计算对齐约束 DCM：第 19–28 行先绕 `cross(aVec2Hat,aVec1Hat)` 旋转使对齐轴重合，第 31–37 行再绕对齐轴旋转满足约束轴条件，最后 `R=(R2*R1)'`（第 40 行）转置得到「从 2 系到 1 系」的矩阵。是 GMAT `AxisSystem` 中 `Spinner`/对齐约束坐标系算法的 MATLAB 参考实现。

**③ `StateConv/Cart2Equinoctial.m`（67 行）—— 状态转换。** 把笛卡尔状态转等分点（equinoctial）根数：默认 `mu=398600.4415`（地球 GM，第 5 行），由能量算半长轴 `a=-mu/2/Energy`（第 24–25 行），用 `f/g` 向量算 `h/k/p/q`，最后算真经度 `lambda`（第 60 行）。含近奇异保护（第 17、27 行对 e→1 与近地半径报错）。对应生产代码 `src/base/` 的状态转换工具。

**④ `ccsdsOEM/@Ephemeris/Ephemeris.m`（27 行）—— MATLAB OO 类。** `classdef Ephemeris < handle` 声明 CCSDS OEM 文件类，属性含 `Segments`（`EphemerisSegment.empty()`）、`StateTolerance=1e-3/86400`（1 ms）、`numSegments`、`firstEpochOnFile=inf`/`lastEpochOnFile=-inf`；方法 `GetSegmentNumberByUseableStartTime`、`GetState`、`ParseEphemeris`。是 GMAT 生产代码 CCSDS OEM 读取器（`FileReader`/`CcsdsEphemerisFile`）的 MATLAB 原型。

**⑤ `STMprop/FM_Earth_AllPlanets_0_0_DE405.m`（6 行）—— 力模型配置。** 用结构体配置力模型：`CentralBody='Earth'`、`PointMasses={地球+日月五星}`、`SRP='Off'`、`EphemerisSource='DE405'`。该目录其余 `FM_*.m` 是不同力模型组合（TwoBody/EarthMoon/多行星），`deriv_*.m` + `dynfunc.m` 算 STM 与状态导数——是 GMAT 力模型/变分方程求解的 MATLAB 对照实现。

**⑥ `OD/src/ReadMe.txt`（13 行）—— 依赖与用法。** 说明这是「拟并入 GMAT 的轨道确定功能 MATLAB 原型」，依赖 David Vallado 的 MATLAB 天文动力学工具（celestrak），把 `OD/src` 加入路径后 `TestCase1` 跑通。揭示了 prototype 与生产代码的转换路径。

**⑦ `StateConv/test/README.txt`（38 行）—— 单元测试约定。** 声明用 MATLAB xUnit 测试框架（File Exchange #22846），`runtests` 跑全部、`runtests testMee` 跑单个套件、`runtests testMee:testCart2MeeCircularEqPro` 跑单测；说明测试真值目录 `truth/` 与 STK 对比的验证方法。

**⑧ `NuMin/solvers/MiNLPClass.m`（目录级代表）—— NLP 求解器。** `NuMin/solvers/` 提供 MATLAB 版非线性规划求解器族：`MiNLPClass.m`（SQP 类）、`MinQP.m`/`MinQPClass.m`（二次规划）、`Uncmin.m`/`UncTrust.m`（无约束/信赖域）、`WolfeLineSearch.m`（线搜索）、`FindTrustStep.m`（信赖域步）、`Numdiff.m`（数值微分）、`NLPFunctionGenerator.m`/`UserProblemTemplate.m`（用户问题模板）。是 GMAT 生产代码 `src/base/solver/` 中 SQP/优化器族（`SNOPT`/`VF13`/`fmincon` 接口）的 MATLAB 原型。

---

### 2.11 `ThirdParty/` —— 外部依赖

仅 1 个文件：`Gmat3rdPartyLinux64.tar.gz`。它是 Linux x64 平台第三方依赖的打包归档（预编译的 wxWidgets、SPICE/NAIF 库、或其他链接库），用于在没有系统包的环境下离线构建 Linux 版 GMAT。仓库不直接提交第三方**源码**（那会极大膨胀体积），而是以平台压缩包形式放置；Windows/OS X 平台的第三方依赖在构建文档与 CMake 脚本中另行指定（参见构建相关章节）。许可信息通常随各依赖包自述或位于 `README`/`license` 文件，本归档内未解包故不展开。

### 2.12 `Metrics/` —— SLOC 代码量统计

`Metrics/R2018a/` 下 3 个 `.txt`，是 R2018a 版用 `sloccount`（SLOC 计数工具）跑出的代码量统计：

| 文件 | 内容 |
|---|---|
| `GmatSrcSlocCount.txt` | 主源码 SLOC：`base 209468`、`gui 98241`、`gmatutil 43444`、`UnitTests 18048`、`TestDrivers 9906`、`console ...`（按目录/语言分列） |
| `GmatPluginsSlocCount.txt` | 插件 SLOC 统计 |
| `GmatInternalPluginsSlocCount.txt` | 内部插件 SLOC 统计 |

> 交叉引用：若 `Metrics/` 已在[第1章]中覆盖，本节可跳过；此处仅作 3 行清单级收录，避免遗漏。

---

## 三、关键设计模式与数据流

### 3.1 文档：单源发布（single-source publishing）

```
DocBook 5.0 XML (src/*.xml)
   │  XInclude 组装：help.xml → Part_*.xml → Using_*/Tut_*/Resource_*/Command_*/*.xml
   ▼
Xalan profiling (profile.condition ug | tm)  ──►  help-pre.xml / training-pre.xml
   ▼
Jing RELAX NG 校验 (docbookxi.rng)
   ▼
┌─────────────────────────────┬──────────────────────────────┐
│ Xalan + docbook-xsl-ns      │ Xalan + fo.xsl → FOP 1.1     │
│   html/docbook.xsl          │   (fo.xsl, fop.xconf)         │
│   chunkfast.xsl             ▼                              ▼
│ help.html / html/index.html │ help-letter.pdf / help-a4.pdf │
└─────────────────────────────┴──────────────────────────────┘
GUI 帮助按钮 → docs/help/html/{UsingGmat,Tutorials}.html / help.html
```

核心思想：**一个 XML 源、多条件、多输出**。`condition="ug"`/`"tm"` 用 profiling 区分用户指南与训练手册；同一源经不同 XSL（HTML vs FO）产出 HTML 与 PDF。帮助页的 XML `xml:id` 通过 `use.id.as.filename` 直接成为 HTML 文件名，从而 GUI 里写死的 `UsingGmat.html`/`Tutorials.html` 路径与 DocBook 结构严格对齐。

### 3.2 数据：启动文件驱动 + 按需加载

```
gmat_startup_file.txt
   │  解析 _PATH/_FILE 变量
   ▼
配置系统（ConfigManager / FileManager）
   │
   ├─ 时间： tai-utc.dat / SPICELeapSecondKernel.tls ──► UTC↔TAI↔ET 换算
   ├─ 历表： DE421AllPlanets.bsp / leDE*.405|.421|.424 ──► 行星位置（SolarSystem）
   ├─ 定向： eopc04_08.62-now + NUTATION.DAT ──► 地球自转/章动/岁差（ITRF↔J2000）
   ├─ 行星： SPICE*.tpc/.bpc/.tf ──► 行星常数与定向（SPICE 接口）
   ├─ 引力： EGM96/JGM/LP165P/Mars50c/MGNP180U.cof ──► 谐波引力场
   ├─ 大气： SpaceWeather / Schatten / marini / Exponential ──► 阻力与对流层延迟
   ├─ 可视化： icons/splash/texture/stars/models ──► GUI 与 OrbitView
   └─ 星历文件： ccsds/ code500/ spk/ stk ──► EphemerisPropagator / FileInterface
```

关键点：启动文件只做「路径声明」，不立即读数据；各子系统（时间换算、历表、引力、大气）在对象初始化时才通过 `_PATH`/`_FILE` 变量按需打开文件。`ROOT_PATH=../` 让整套数据可整体搬迁——这也是 Windows 上偶发找不到 DE 文件时可在启动文件里改 `ROOT_PATH` 为绝对路径的原因（第 89–94 行注释）。

### 3.3 prototype → 生产代码的演进路径

prototype 不是独立产品，而是生产代码的「算法孵化器」，演进路径清晰：
- `StateConv/`（MATLAB 状态转换）→ `src/base/` 状态转换/坐标系；
- `ccsdsAEM/`+`ccsdsOEM/`（MATLAB CCSDS 类）→ 生产 CCSDS 星历/姿态文件读取器；
- `NuMin/`（MATLAB NLP 求解器）→ `src/base/solver/` 优化器族；
- `CSALTMatlab/`（MATLAB 配点法）→ 生产 CSALT（`libCsaltInterface` 插件）；
- `OD/`+`ODPrototype/`（MATLAB 定轨）→ `libGmatEstimation` 估计子系统；
- `TAT-C/`（GSFC 星座权衡）→ 独立工具（含 C++ 版）；
- `Attitude/`、`STMprop/`、`OptimalControl/` → 对应生产姿态/变分方程/最优控制模块。
验证方式：`StateConv/test/truth/` 与 `GroundTrackPlot/*TruthData` 保留 STK 真值，作为 MATLAB 原型与后续生产实现回归对比的基准。

---

## 四、文件清单附录

### 表 A：doc/ 各子目录（目录级）

| 相对路径 | 文件数 | 子目录数 | 职责 | 关键文件/格式 |
|---|---|---|---|---|
| `doc/help/` | 955 | 15 | 用户指南+训练手册 DocBook 源与构建配置 | `help.xml`、`Resource_*.xml`(73)、`Command_*.xml`(43)、`Tut_*.xml`(24)、`Makefile`、`fo.xsl` |
| `doc/DevelopersDocs/` | 151 | 20 | 开发者指南 | `GmatCppStyleGuide.docx`、`GmatBestPractices/`、`CompilingGMATwithVS2010/`、`CSALT/` |
| `doc/SystemDocs/` | 985 | 101 | 系统设计规格 | `ArchitecturalSpecification/`(412)、`MathematicalSpecification/`(152)、`EstimationSpecification/`(141)、`ComponentDesigns/`(133)、`APICookbook/`、`Tools/` |
| `doc/ProcessDocs/` | 7 | 4 | 项目计划与需求 | `ProductionReleasePlan.doc`、`Build1Requirements.doc` |
| `doc/PapersAndPresentations/` | 64 | 8 | 论文与演讲 | AIAA 论文、`DeveloperTalks/`、`MadridFY10-ICATT/` |
| `doc/styleexample/` | 19 | 5 | DocBook 样式示例 | `GmatStyleExample.xml`、`HowTo-*.xml`、`Tut_PropSpacecraft.xml` |
| `doc/training/` | 4 | 3 | 训练手册 | `GmatTrainingManual.xml` |
| `doc/build/` | 5997 | 350 | 文档构建工具链 | `contrib/{fop-1.1,docbook-xsl-ns-1.78.1,jing,xalan-j,docbook}` |

### 表 B：application/data/ 各子目录（目录级）

| 相对路径 | 要点 | 关键文件 |
|---|---|---|
| `data/planetary_ephem/de/` | ASCII DE 历表 | `leDE1941.405`、`leDE1900.421`、`leDE18002100.424` |
| `data/planetary_ephem/spk/` | 二进制 SPK 内核 | `DE421AllPlanets.bsp`、`DE405AllPlanets.bsp`、`DE424AllPlanets.bsp`、`ceres_1900_2100.bsp`、`Readme-*.txt` |
| `data/planetary_coeff/` | EOP/章动/行星常数 | `eopc04_08.62-now`、`NUTATION.DAT`、`SPICE*.tpc/.bpc/.tf` |
| `data/time/` | 跳秒表 | `tai-utc.dat`、`SPICELeapSecondKernel.tls` |
| `data/gravity/{earth,luna,mars,venus,other}/` | 引力场系数 | `EGM96.cof`、`JGM2/JGM3.cof`、`LP165P.cof`、`grgm900c.cof`、`Mars50c.cof`、`MGNP180U.cof` 等 |
| `data/atmosphere/{earth,mars,Msise86_Data}/` | 大气模型 | `SpaceWeather-All-v1.2.txt`、`SchattenPredict.txt`、`marini.dat`、`*ExponentialAtmosphereData.txt`、`msis86.dat` |
| `data/icrf/` | ICRF 参考架 | `ICRF_Table.txt` |
| `data/IonosphereData/` | 电离层/地磁模型 | `ccir*.asc`、`ursi*.asc`、`igrf*.dat`、`dgrf*.dat`、`ig_rz.dat`、`ap.dat` |
| `data/graphics/{icons,splash,texture,stars,models}/` | 可视化资源 | 图标 PNG、闪屏、行星纹理、`inp_StarCatalog.txt`、`Comet_Hartley_Green.3ds` |
| `data/vehicle/{ephem,models,spad}/` | 航天器星历/模型/光压板 | `ccsds/*.oem|aem`、`spk/*.bsp`、`code500/*.ephem`、`stk/*.e`、`aura.3ds`、`SphericalModel.spo`、`JWST-10cm1R.spo` |
| `data/gui_config/` | GUI 面板配置 | `MyGmat.ini`、`SNOPT.ini`、`Yukon.ini`、`VF13ad.ini` 等 10 个 |
| `data/api/` | API 帮助 | `GmatHelp.rst` |
| `data/emtg/` | EMTG 配置 | `*.emtg_spacecraftopt`、`*.ThrottleTable` |
| `data/hardware/` | 硬件数据 | `ConeClockAngles` |
| `data/misc/` | 最优控制历史/SNOPT 规格 | `*.och`、`SNOPTSPECfile.txt` |

### 表 C：prototype/ 各子目录（目录级）

| 相对路径 | 文件数 | 子目录数 | 内容 |
|---|---|---|---|
| `prototype/CSALTMatlab/` | 460 | 66 | CSALT 配点法 MATLAB 原型 |
| `prototype/StateConv/` | 429 | 27 | 状态转换函数库 + STK 真值 |
| `prototype/OptimalControl/` | 265 | 84 | 最优控制原型 |
| `prototype/TAT-C/` | 231 | 22 | 星座权衡分析工具（cpp+matlab） |
| `prototype/NuMin/` | 198 | 7 | NLP 求解器 MATLAB 原型 |
| `prototype/Navigation/` | 97 | 13 | 导航原型（TDRSS Doppler） |
| `prototype/OD/` | 80 | 26 | 轨道确定 MATLAB 原型 |
| `prototype/STMprop/` | 51 | 0 | STM 传播原型 |
| `prototype/ccsdsAEM/` | 34 | 5 | CCSDS AEM MATLAB 类 |
| `prototype/Attitude/` | 14 | 3 | 姿态 DCM 原型 |
| `prototype/ccsdsOEM/` | 14 | 5 | CCSDS OEM MATLAB 类 |
| `prototype/ODPrototype/` | 12 | 0 | 定轨原型脚本 |
| `prototype/Auto-NGC/` | 7 | 3 | 自动化导航接触 |
| `prototype/FiniteBurn/` | 7 | 1 | 有限推力/推进剂箱原型 |
| `prototype/GroundTrackPlot/` | 5 | 0 | 地面轨迹绘图原型 |
| `prototype/interp/` | 3 | 2 | 插值器类原型 |
| `prototype/MATLABUtils/` | 2 | 0 | EOP 文件写入工具 |

### 表 D：ThirdParty / Metrics

| 相对路径 | 文件数 | 内容 |
|---|---|---|
| `ThirdParty/` | 1 | `Gmat3rdPartyLinux64.tar.gz` |
| `Metrics/R2018a/` | 3 | `GmatSrcSlocCount.txt`、`GmatPluginsSlocCount.txt`、`GmatInternalPluginsSlocCount.txt` |
