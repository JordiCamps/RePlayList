@echo off
echo Starting RePlayList...
echo.
echo Make sure you have configured config.json with your API credentials!
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak > nul
start http://localhost:5000
echo.
echo Starting backend server...
replaylist-backend.exe
pause
