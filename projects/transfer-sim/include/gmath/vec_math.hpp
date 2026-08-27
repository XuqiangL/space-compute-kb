//==============================================================================
// vec_math.hpp — 三维向量基础运算（MD-06 线性代数 / MD-14 表达式引擎对应公式）
//
// 每函数一个公式；全部实现为 constexpr/inline，CPU 与 CUDA(__host__ __device__)
// 共用同一份源码（通过 GMATH_DEVICE 宏标记，保证 CPU golden 与 GPU 内核逐字一致）。
//==============================================================================
#pragma once
#include <cmath>
#include "device.hpp"

namespace gmath {

//------------------------------------------------------------------------------
// dot(a, b) — 向量点积
// 公式：a·b = Σ_{i=1..3} a_i b_i
// 代码对应：gmatutil/util/Rvector 的 operator*（元素乘累加，MD-06 §6.2）
//------------------------------------------------------------------------------
GMATH_DEVICE inline double dot(const double a[3], const double b[3])
{
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
}

//------------------------------------------------------------------------------
// cross(a, b) — 向量叉积（右手系）
// 公式：c = a×b = (a_y b_z - a_z b_y,  a_z b_x - a_x b_z,  a_x b_y - a_y b_x)
// 用途：轨道角动量 h = r×v、面法向、旋转矩阵生成
//------------------------------------------------------------------------------
GMATH_DEVICE inline void cross(const double a[3], const double b[3], double c[3])
{
    c[0] = a[1]*b[2] - a[2]*b[1];
    c[1] = a[2]*b[0] - a[0]*b[2];
    c[2] = a[0]*b[1] - a[1]*b[0];
}

//------------------------------------------------------------------------------
// norm(v) — 欧氏范数
// 公式：||v|| = sqrt(v_x² + v_y² + v_z²)
// 代码对应：Rvector::GetMagnitude（MD-06 §6.2）
//------------------------------------------------------------------------------
GMATH_DEVICE inline double norm(const double v[3])
{
    return std::sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
}

//------------------------------------------------------------------------------
// norm6(s) — 六维状态范数（位置/速度分量加权开方）
// 公式：||s|| = sqrt(Σ_{i=1..6} s_i²)
//------------------------------------------------------------------------------
GMATH_DEVICE inline double norm6(const double s[6])
{
    double acc = 0.0;
    for (int i = 0; i < 6; ++i) acc += s[i]*s[i];
    return std::sqrt(acc);
}

//------------------------------------------------------------------------------
// vadd / vsub / scale / saxpy — 向量加减与数乘（MD-06 元素级运算）
// 公式：c = a + b；c = a - b；c = s·a；c = s·a + b
//------------------------------------------------------------------------------
GMATH_DEVICE inline void vadd(const double a[3], const double b[3], double c[3])
{ c[0]=a[0]+b[0]; c[1]=a[1]+b[1]; c[2]=a[2]+b[2]; }

GMATH_DEVICE inline void vsub(const double a[3], const double b[3], double c[3])
{ c[0]=a[0]-b[0]; c[1]=a[1]-b[1]; c[2]=a[2]-b[2]; }

GMATH_DEVICE inline void scale(const double s, const double a[3], double c[3])
{ c[0]=s*a[0]; c[1]=s*a[1]; c[2]=s*a[2]; }

GMATH_DEVICE inline void saxpy(const double s, const double a[3], const double b[3], double c[3])
{ c[0]=s*a[0]+b[0]; c[1]=s*a[1]+b[1]; c[2]=s*a[2]+b[2]; }

} // namespace gmath
