@echo off
rem build_gpu.bat — compile CUDA version (nvcc + MSVC host compiler)
setlocal
if not exist "C:\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
  echo [ERROR] BuildTools not found at C:\BuildTools
  exit /b 1
)
call "C:\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
if not exist build mkdir build

rem locate cl.exe for -ccbin
for /f "delims=" %%i in ('where cl') do set CLPATH=%%i
echo host compiler: %CLPATH%

echo == compiling main_gpu (CUDA) ==
nvcc -O3 -std=c++17 -arch=sm_86 -ccbin "%CLPATH%" -Xcompiler "/utf-8" -I include src\main_gpu.cu cuda\kernels.cu -o build\main_gpu.exe
if errorlevel 1 exit /b 1

echo OK
endlocal
