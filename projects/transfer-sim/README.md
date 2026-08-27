# transfer-sim — 地月转移轨道仿真（GMAT 公式逐函数迁移 + CPU golden + CUDA + 对比）

以 `gmat-architecture-docs/math-deep-dive/` 的公式解析为基础，把 GMAT 源码中的
公式封装**逐公式迁移**为独立函数（每个函数注释含公式与讲解），并给出：

- **CPU golden**（`main_cpu.exe` + 47 个单元测试）
- **CUDA 版本**（每个公式函数对应 kernel；GPU 与 CPU 共用**同一份公式头文件**）
- **CPU/GPU 数值对比**（逐公式 + 定步权威对比 + 轨迹对比）
- **真实 GMAT 交叉验证**（GmatConsole 同场景对照，1 天传播位置差 ≤ 15 m）

## 目录结构

```
transfer-sim/
├── include/gmath/           公式库（CPU/CUDA 共用，__host__ __device__）
│   ├── device.hpp           GMATH_DEVICE 宏
│   ├── constants.hpp        μ⊕/R⊕/μ☾/J2/时间基准（GmatDefaults.hpp 数值）
│   ├── vec_math.hpp         dot/cross/norm/…（MD-06）
│   ├── time_math.hpp        儒略日/A.1 MJD/TT-TAI（MD-01）
│   ├── elements.hpp         要素↔状态、近点角、SOI、活力公式（MD-03）
│   ├── accelerations.hpp    点质量/J2/第三体/ODE 右手边（MD-08）
│   ├── burns.hpp            ṁ/火箭方程/有限推力（MD-10）
│   ├── integrators.hpp      PD45（系数逐字取自 PrinceDormand45.cpp）+ 自适应步长（MD-04）
│   └── tensors.hpp          轨迹张量布局与索引公式（2D/3D/4D）
├── src/
│   ├── main_cpu.cpp         CPU golden：patched-conic 地月转移 + --ref 交叉验证模式
│   └── main_gpu.cu          CUDA 主程序：逐公式对比 + 定步权威对比 + 批量传播
├── cuda/kernels.cu          每个公式函数的 kernel（复用同一公式源码）
├── tests/test_formulas.cpp  47 个单元测试（每公式一个用例，解析参照值）
├── scripts/compare_trajectories.py  CPU/GPU 轨迹逐点对比
├── gmat/reference_1day.script       真实 GMAT 参照脚本
├── docs/TRANSFER_SIMULATION.md      完整链路讲解（输入→公式→输出→张量问题）
├── data/                   输出：轨迹 CSV、summary、gpu_compare.csv
├── build_cpu.bat / build_gpu.bat / run_all.bat
```

## 快速开始

```bat
build_cpu.bat                     :: 需 VS2022 BuildTools（C:\BuildTools）
build\test_formulas.exe           :: 47/47 通过
build\main_cpu.exe --out data     :: 转移轨道 golden
build_gpu.bat                     :: 需 CUDA 12.9 + nvcc（I:\bin）
build\main_gpu.exe --M 256 --out data
```

## 关键结果（本次运行实测）

- 转移：TLI +3.14 km/s → SOI 进入 2.93 天 → 近月点 7798.4 km（alt 6060 km），vp=1.438 km/s
- 单元测试 **47/47**；逐公式 CPU/GPU max|diff| ≤ 5.8e-11
- 定步 20000 步 CPU/GPU 位置差 **2.9e-8 km**；真实 GMAT 交叉验证位置差 ≤ **15 m**
- GPU 批量吞吐 1308 轨迹/秒（RTX 3080，256 轨迹 196 ms）

详见 `docs/TRANSFER_SIMULATION.md`。
