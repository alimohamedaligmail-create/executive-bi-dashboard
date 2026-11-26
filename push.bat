@echo off
:loop
cls
echo ====================================
echo      Git Push
echo ====================================

git add .

echo.
for /f "tokens=*" %%a in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd hh:mm:ss tt'"') do set commit_msg=%%a

git commit -m "%commit_msg%"

echo.
echo Pushing to GitHub automatically...

git push https://alimohamedaligmail-create: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@github.com/alimohamedaligmail-create/executive-bi-dashboard.git

echo.
echo ====================================
echo        Done!
echo ====================================

echo.
echo Press any key to run the script again...
pause >nul
goto loop