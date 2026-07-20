@echo off
setlocal
set PY=C:\Users\rdft1\AppData\Local\Programs\Python\Python312\python.exe
cd /d C:\MyApp\altium-mcp

echo === Altium MCP: install dependencies ===
if exist server\.venv (
  echo Removing old partial venv...
  rmdir /s /q server\.venv
)
echo Creating venv...
"%PY%" -m venv server\.venv
if errorlevel 1 goto :fail

echo Installing from Tsinghua mirror...
server\.venv\Scripts\pip.exe install "mcp[cli]==1.5.0" "pillow>=11.1.0" "pywin32>=310" -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
  echo Mirror failed, trying default PyPI...
  server\.venv\Scripts\pip.exe install "mcp[cli]==1.5.0" "pillow>=11.1.0" "pywin32>=310"
  if errorlevel 1 goto :fail
)

echo Verifying imports...
server\.venv\Scripts\python.exe -c "import mcp, PIL, win32gui; print('IMPORTS OK')"
if errorlevel 1 goto :fail

echo.
echo ============================================
echo   SUCCESS - dependencies installed.
echo   Now in Claude: Settings - Extensions -
echo   altium-mcp: toggle Enabled OFF then ON.
echo ============================================
pause
exit /b 0

:fail
echo.
echo INSTALL FAILED - see messages above.
pause
exit /b 1
