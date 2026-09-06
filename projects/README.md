# 工程仿真项目群（projects/）

> "发射前怎么知道行不行？"——靠这套可运行、可测试的仿真器。每个项目对应知识库模块的公式，每个测试锁定书中的一个数值算例。**测试失败 = 书或代码有一方错了**（本库已借此修正 4 处数值错误）。

## 项目清单

| 项目 | 对应模块 | 功能 | 测试数 |
|---|---|---|---|
| p1_orbit | 02 轨道力学 | 活力公式/霍曼转移/J2-SSO 求解/大气阻力寿命/相位漂移/火箭方程 | 14 |
| p2_thermal | 01+05 热环境 | 平衡温度/辐射器 sizing/热阻网络/瞬态 RC/PCM/焊点疲劳 | 17 |
| p3_link | 07 通信 | Friis 链路预算/DVB-S2 门限/激光链路/提前瞄准角/站址分集 | 12 |
| p4_radiation | 04+06 辐射 | Weibull 拟合/SEU 率/TID 屏蔽/Young checkpoint/可靠性框图 | 15 |
| p5_scheduler | 09 运营调度 | SAA/地面窗口表/四维约束调度/下行容量 | 10 |
| p6_mission | 12 全流程 | **端到端任务仿真**：发射→升轨→电源/热/辐射闸门→运营→离轨 | 9 |
| p7_solarsim | 02 轨道力学(深空) | **太阳系工程仿真器 v2**：JPL 星历/21 颗卫星/小行星带 Kirkwood 空隙/柯伊伯带/哈雷彗星/真实星空/土星环/拉格朗日点/SOI/KSP 式机动节点/双曲线逃逸/ISS+算星一号，与真实 UTC 时钟对齐 | 38 |
| transfer-sim | 02 轨道力学 + GMAT math-deep-dive | **地月转移轨道 C++/CUDA 仿真**：GMAT 公式逐函数迁移、CPU golden（47 单元测试）、CUDA kernel 对照、真实 GMAT 交叉验证（≤15 m） | 47 |
| p8_orbitlab | 02 轨道力学(教学) | **OrbitLab 卫星轨道动力学教学仿真器**：六根数滑块实时联动 3D 轨道/半透明轨道面/i·Ω·ω·ν 角度弧、五大摄动（J2/阻力/日月第三体/光压）真实建模、Cowell 传播、世界地图贴图地球+星下点轨迹、时间轴播放，与 UTC 时钟对齐；附 exe | 21 |

## 运行方法

```bash
# 任一 Python 项目目录下
py -m unittest test_orbit -v      # p1 示例

# 运行端到端任务仿真（输出完整 JSON 报告）
cd projects/p6_mission
py mission_sim.py
```

### transfer-sim（C++/CUDA，需 VS2022 + CUDA 12.9）

```bat
cd projects\transfer-sim
build_cpu.bat
build\test_formulas.exe           :: 47/47 单元测试
build\main_cpu.exe --out data     :: CPU golden 地月转移
build_gpu.bat
build\main_gpu.exe --M 256 --out data
```

详见 [transfer-sim/README.md](transfer-sim/README.md) 与 [transfer-sim/docs/TRANSFER_SIMULATION.md](transfer-sim/docs/TRANSFER_SIMULATION.md)。

## 端到端仿真输出解读（算星一号默认配置）

| 阶段 | 关键输出 | 闸门 |
|---|---|---|
| launch | 升轨 Δv 83.5 m/s、推进剂 7.0 kg | - |
| power | EOL 1785 W vs 负载 925 W（余量 93%） | EOL ≥ 负载×1.15 |
| thermal | 排散 1371 W vs 热耗 1113 W；降额结温 83.4°C | 能力 ≥ 热耗×1.2 且结温 ≤85°C |
| radiation | 任务期 TID 10.7 krad；SEU 2.8 万次/天/8GB；checkpoint 3220 s | TID < 20 krad |
| operations | 任务成功率 100%；日下行 0.83 TB vs 日产出 0.01 TB | 成功率 >95% 且下行 > 产出 |
| deorbit | 离轨 Δv 98.9 m/s、推进剂 6.7 kg | - |
| **mission_go** | **true** | 全部闸门通过 |

## 设计原则

1. **零依赖**：纯 Python 标准库，任何机器可跑
2. **测试即验证**：每个 assert 对应书中一个数字——改书必须改测试，改测试必须改书
3. **参数即配置**：`mission_sim.CONFIG` 就是算星一号的总体参数表，改参数即做方案权衡（trade study）
4. **闸门即评审**：`mission_go` 模拟 PDR/CDR 的"go/no-go"逻辑

## 已捕获的知识库勘误（测试的价值证明）

| 位置 | 原值 | 正确值 | 发现者 |
|---|---|---|---|
| 模块 02 霍曼 400→550 km | 67 m/s | 83.5 m/s | test_hohmann_400_to_550 |
| 模块 02 离轨 Δv | 40 m/s | 98.9 m/s | test_deorbit_dv |
| 模块 02 阻力衰减 | −58 m/天 | −5 m/天 | test_decay_550km |
| 模块 01 白漆平衡温度 | 265 K | 270 K | test_white_paint |
| 模块 07 X 频段 FSPL | 157 dB | 169 dB | test_fspl_xband |

