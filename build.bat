@echo off

title Build Results

measure.py start

echo.

echo.

echo ----------------------------------------------------

echo Program Finished With Exit Code %ERRORLEVEL%

measure.py stop

echo ----------------------------------------------------

echo.

pause
