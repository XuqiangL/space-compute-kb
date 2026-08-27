@echo off
rem build_cpu.bat — compile CPU golden + unit tests (MSVC via BuildTools)
setlocal
if not exist "C:\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
  echo [ERROR] BuildTools not found at C:\BuildTools
  exit /b 1
)
call "C:\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
if not exist build mkdir build

echo == compiling unit tests ==
cl /nologo /O2 /std:c++17 /EHsc /utf-8 /I include tests\test_formulas.cpp /Fe:build\test_formulas.exe
if errorlevel 1 exit /b 1

echo == compiling main_cpu (golden transfer sim) ==
cl /nologo /O2 /std:c++17 /EHsc /utf-8 /I include src\main_cpu.cpp /Fe:build\main_cpu.exe
if errorlevel 1 exit /b 1

echo OK
endlocal
