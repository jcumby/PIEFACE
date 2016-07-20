@echo off

REM Batch file to automate build with PyInstaller

REM Assumes CIFellipsoid.exe is being MERGED with distellipsoid_gui.exe;
REM all files are then copied into the `distellipsoid_win` folder.

echo 
echo BEWARE: This script will overwrite the dist\distellipsoid_win\ directory
pause

REM Remove existing distellipsoid_win folder, to prevent old files hanging around
RMDIR /S /Q dist\distellipsoid_win

pyinstaller -y win_build.spec
copy /Y dist\CIFellipsoid\CIFellipsoid.exe dist\distellipsoid_win\CIFellipsoid.exe

copy /Y dist\CIFellipsoid\CIFellipsoid.exe.manifest dist\distellipsoid_win\CIFellipsoid.exe.manifest

pause