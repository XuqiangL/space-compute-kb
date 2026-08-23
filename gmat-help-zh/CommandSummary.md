# 命令摘要（CommandSummary）

> 译自 GMAT R2026a 帮助文档 CommandSummary.html

**Command Summary（命令摘要）** 是命令执行后轨道和航天器状态信息的摘要。例如，如果命令是 `Propagate` 命令，**Command Summary** 包含传播执行后的状态数据。

要查看 **Command Summary**，右键点击所需命令并选择 **Command Summary（命令摘要）**；或者双击所需命令，然后点击面板左下角附近的 **Command Summary** 图标。查看 **Command Summary** 数据之前必须先运行任务。

> [图：示例 Command Summary 截图]

## 数据可用性

要查看 **Command Summary**，必须先运行任务。如果在当前会话中尚未运行任务，**Command Summary** 将为空。如果对配置做了更改，必须重新运行任务，这些更改才能在 **Command Summary** 中生效。

## 数据内容

**Command Summary** 包含多种类型的数据。轨道状态表示包括笛卡尔（Cartesian）、球坐标（Spherical）和开普勒（Keplerian）元素。对于双曲线轨道，提供 B 平面坐标、DLA 和 RLA。星体测地信息包括经度和纬度等。对于 `Maneuver` 命令，`Maneuver` 属性以 `ImpulsiveBurn` 资源上指定的 CoordinateSystem 显示。关于某些数据未定义时命令摘要内容的更多信息，见下文"坐标系"小节。

当轨道接近奇异圆锥曲线和/或任何开普勒元素未定义时，会显示简略的 **Command Summary**，如下文"坐标系"小节所示。

你可以点击 **Save As...（另存为）** 并指定要保存到的文件，把数据保存到文本文件。

## 支持的命令

出于性能原因，单步模式下的传播不会写出命令摘要。此外，如果命令嵌套在控制逻辑中且因此未执行，则没有可用的命令摘要数据。

## 坐标系

**Command Summary** 对话框顶部的 **Coordinate System（坐标系）** 菜单允许你为状态数据选择所需的坐标系。当 **Coordinate System** 以某天体为原点时，**Command Summary** 显示所有支持的数据，包括笛卡尔、球坐标、开普勒、其他轨道数据（Other OrbitData）和星体测地属性，如上方 GUI 截图所示。当 **Coordinate System** 不以天体为原点时，**CommandSummary** 只包含简略的命令摘要，如下所示。

注意：GMAT 目前要求所选的 **CoordinateSystem** 不能引用航天器。

```
Propagate Command: Propagate1
        Spacecraft       : DefaultSC
        Coordinate System: EarthMJ2000Eq

        Time System   Gregorian                     Modified Julian  
        --------------------------------------------------------------------    
        UTC Epoch:    01 Jan 2000 15:19:28.000      21545.1385185185
        TAI Epoch:    01 Jan 2000 15:20:00.000      21545.1388888889
        TT  Epoch:    01 Jan 2000 15:20:32.184      21545.1392613889
        TDB Epoch:    01 Jan 2000 15:20:32.184      21545.1392613881

        Cartesian State                       Spherical State 
        ---------------------------           ------------------------------ 
        X  =   7047.3574396928 km             RMAG =   7195.1179781105 km
        Y  =  -821.00373455465 km             RA   =  -6.6448962577676 deg 
        Z  =   1196.0053110175 km             DEC  =   9.5683789596091 deg 
        VX =   0.8470865225276 km/sec         VMAG =   7.4415324037805 km/s
        VY =   7.3062391027010 km/sec         AZI  =   81.377585410118 deg
        VZ =   1.1303623817297 km/sec         VFPA =   88.583915406742 deg  
                                              RAV  =   83.386645244484 deg
                                              DECV =   8.7370006427902 deg

        Spacecraft Properties 
        ------------------------------
        Cd                    =   2.200000
        Drag area             =   15.00000 m^2
        Cr                    =   1.800000
        Reflective (SRP) area =   1.000000 m^2
        Dry mass              =   850.00000000000 kg
        Total mass            =   850.00000000000 kg
```

说明：以上为简略命令摘要示例，包含各时间系统历元、笛卡尔与球坐标状态，以及航天器物理属性（阻力系数 Cd、阻力面积、反射系数 Cr、SRP 面积、干质量与总质量）。