//==============================================================================
// device.hpp — CPU/CUDA 共用编译标记
// GMATH_DEVICE：nvcc 下展开为 __host__ __device__（同一份公式源码同时编译进
// CPU golden 与 GPU 内核），其余编译器为空。
//==============================================================================
#pragma once

#ifndef GMATH_DEVICE
#ifdef __CUDACC__
#define GMATH_DEVICE __host__ __device__
#else
#define GMATH_DEVICE
#endif
#endif
