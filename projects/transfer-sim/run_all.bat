@echo off
rem run_all.bat — run CPU tests, CPU golden sim, GPU compare; produce reports
setlocal
if not exist data mkdir data
echo == 1/4 unit tests (CPU golden) ==
build\test_formulas.exe
if errorlevel 1 ( echo [FAIL] unit tests & exit /b 1 )
echo.
echo == 2/4 CPU transfer simulation ==
build\main_cpu.exe --out data
if errorlevel 1 ( echo [FAIL] cpu sim & exit /b 1 )
echo.
echo == 3/4 GPU per-formula compare + batch ==
build\main_gpu.exe --M 256 --out data
if errorlevel 1 ( echo [FAIL] gpu & exit /b 1 )
echo.
echo == 4/4 outputs in data\ ==
dir data
endlocal
