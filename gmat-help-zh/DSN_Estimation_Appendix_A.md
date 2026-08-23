# 附录 A —— GMAT 消息窗口输出（DSN_Estimation_Appendix_A）

> 译自 GMAT R2026a 帮助文档 DSN_Estimation_Appendix_A.html

**附录 A —— GMAT 消息窗口输出**

以下为"使用 DSN 测距与多普勒数据进行轨道估计"教程运行期间 GMAT 消息窗口的完整输出（英文原文保留）：

```
Running mission...
Number of thrown records due to:
     .Invalid measurement value : 0
     .Record duplication or time order : 0
Data file '../output/Simulate DSN Range and Doppler Data 3 weeks.gmd' has 1348 of 1348 records used for estimation.
Total number of load records : 1348

List of tracking configurations (present in participant ID) for load records from data file '../output/Simulate DSN Range and Doppler Data 3 weeks.gmd':
   Config 0: {{22222,11111,22222},DSN_SeqRange}
   Config 1: {{22222,11111,22222},DSN_TCP}
   Config 2: {{33333,11111,33333},DSN_SeqRange}
   Config 3: {{33333,11111,33333},DSN_TCP}
   Config 4: {{44444,11111,44444},DSN_SeqRange}
   Config 5: {{44444,11111,44444},DSN_TCP}

****   No tracking configuration was generated because the tracking configuration is defined in the script.

Initializing new mat data writer
MATLAB file will be written to C:\Users\sslojkow\Documents\gmat\builds\LatestCompleteVersion\bin\..\output\Orbit Estimation using DSN Range and Doppler Data.mat
MATLAB Writer .mat version w5 invalid; defaulting to w6
********************************************************
*** Performing Estimation (using "bat")
*** 
********************************************************

a priori state:
   Estimation Epoch:
   27253.5004170646025158930570 A.1 modified Julian
   27253.5004166666661733004647 TAI modified Julian
   19 Aug 2015 00:00:00.000 UTCG
   Sat.SunMJ2000Eq.X = -126544963
   Sat.SunMJ2000Eq.Y = 61978518
   Sat.SunMJ2000Eq.Z = 24133225
   Sat.SunMJ2000Eq.VX = -13.789
   Sat.SunMJ2000Eq.VY = -24.673
   Sat.SunMJ2000Eq.VZ = -10.662

Number of Records Removed Due To:
   . No Computed Value Configuration Available : 0
   . Out of Ramp Table Range   : 0
   . Signal Blocked : 0
   . Initial RMS Sigma Filter  : 0
   . Outer-Loop Sigma Editor : 0
Number of records used for estimation: 1348

   WeightedRMS residuals for this iteration : 1459.96324774
   BestRMS residuals                        : 1459.96324774
   PredictedRMS residuals for next iteration: 0.977684716761

------------------------------------------------------
Iteration 1

Current estimated state:
   Estimation Epoch:
   27253.5004170646025158930570 A.1 modified Julian
   27253.5004166666661733004647 TAI modified Julian
   19 Aug 2015 00:00:00.000 UTCG
   Sat.SunMJ2000Eq.X = -126544964.083
   Sat.SunMJ2000Eq.Y = 61978520.0714
   Sat.SunMJ2000Eq.Z = 24133223.2424
   Sat.SunMJ2000Eq.VX = -13.789001388
   Sat.SunMJ2000Eq.VY = -24.6729990628
   Sat.SunMJ2000Eq.VZ = -10.662000523

Number of Records Removed Due To:
   . No Computed Value Configuration Available : 0
   . Out of Ramp Table Range   : 0
   . Signal Blocked : 0
   . Initial RMS Sigma Filter  : 0
   . Outer-Loop Sigma Editor : 1
Number of records used for estimation: 1347

   WeightedRMS residuals for this iteration : 0.974259069508
   BestRMS residuals                        : 0.974259069508
   PredictedRMS residuals for next iteration: 0.974224174165
This iteration is converged due to relative convergence criteria.


********************************************************
*** Estimation Completed in 2 iterations
********************************************************

Estimation converged!
      |1 - RMSP/RMSB| = | 1- 0.974224 / 0.974259| = 3.58173e-05 is less than RelativeTol, 0.0001

Final Estimated State:

   Estimation Epoch:
   27253.5004170646025158930570 A.1 modified Julian
   27253.5004166666661733004647 TAI modified Julian
   19 Aug 2015 00:00:00.000 UTCG
   Sat.SunMJ2000Eq.X = -126544963.637
   Sat.SunMJ2000Eq.Y = 61978520.6939
   Sat.SunMJ2000Eq.Z = 24133223.6628
   Sat.SunMJ2000Eq.VX = -13.7890015517
   Sat.SunMJ2000Eq.VY = -24.6729992038
   Sat.SunMJ2000Eq.VZ = -10.6620000077
```

**中文说明**：消息窗口首先报告读入的 1348 条记录全部有效（无因无效测量值或时间乱序被丢弃的记录），列出 6 种跟踪配置（3 个地面站 × 2 种测量类型 DSN_SeqRange/DSN_TCP）。先验状态为 2015 年 8 月 19 日 00:00 UTCG 历元下的日心惯性系位置/速度。第 0 次迭代的加权 RMS 残差约 1460（很大，因为先验状态有偏差），第 1 次迭代降到约 0.974，满足相对收敛准则（|1 − RMSP/RMSB| = 3.58e-05 < RelativeTol = 0.0001），估计在 2 次迭代后收敛。最终估计状态给出修正后的位置/速度。

```
Final Covariance Matrix:

         6.568631977218e+00         1.044777728608e+01         3.117063688646e+00        -2.346661054173e-06         4.986079628477e-07         1.614625814366e-06
         1.044777710993e+01         2.043036379635e+01        -4.249227712186e+00        -3.704711284679e-06         1.982306082751e-07         3.981551919217e-06
         3.117064114026e+00        -4.249226952008e+00         2.371354504010e+01        -1.180689659682e-06         1.672460285882e-06        -2.645600028262e-06
        -2.346661055323e-06        -3.704711349403e-06        -1.180689508343e-06         8.389295488954e-13        -1.640460214611e-13        -6.093050987987e-13
         4.986079968962e-07         1.982306774906e-07         1.672460265672e-06        -1.640460335201e-13         1.032410080241e-12        -2.192341045550e-12
         1.614625733805e-06         3.981551830454e-06        -2.645600161576e-06        -6.093050697768e-13        -2.192341060048e-12         5.785215030292e-12

Final Correlation Matrix:

             1.000000000000             0.901879241925             0.249752571898            -0.999655028427             0.191467746900             0.261923625542
             0.901879226720             1.000000000000            -0.193051736939            -0.894856861497             0.043162495440             0.366230559395
             0.249752605981            -0.193051702403             1.000000000000            -0.264712696708             0.338011482643            -0.225873973518
            -0.999655028917            -0.894856877130            -0.264712662778             1.000000000000            -0.176269364287            -0.276574613248
             0.191467759975             0.043162510510             0.338011478559            -0.176269377245             1.000000000000            -0.897061553257
             0.261923612473             0.366230551230            -0.225873984900            -0.276574600074            -0.897061559189             1.000000000000

********************************************************



Writing Estimator MATLAB File...
Finished Writing Estimator MATLAB File.

Mission run completed.
===> Total Run Time: 220.532 seconds

========================================
```

**中文说明**：最终协方差矩阵给出 6 个估计状态（X、Y、Z、VX、VY、VZ）的估计不确定度——位置方差约 6.6–23.7 km²，速度方差约 1e-12 (km/s)² 量级。相关矩阵显示位置分量之间、以及 X 与 VX 之间存在强相关（如 X-VX 相关系数约 -0.9997）。最后写出估计器 MATLAB 文件，任务运行完成，总耗时约 220.5 秒。
