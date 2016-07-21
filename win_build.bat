@echo off

REM Batch file to automate build with PyInstaller

REM Assumes CIFellipsoid.exe is being MERGED with distellipsoid_gui.exe;
REM all files are then copied into the `distellipsoid_win` folder.

echo 
echo BEWARE: This script will overwrite the dist\distellipsoid_win\ directory
echo
pause

REM ******* 64-bit Version *********
REM Remove existing distellipsoid_win folder, to prevent old files hanging around
echo **********************
echo Freezing 64-bit python
echo **********************

RMDIR /S /Q dist\distellipsoid_win
REM Run 64-bit PyInstaller, copy CIFellipsoid files across and then move entire directory to 64-bit folder
C:\Users\JCC\AppData\Local\enthought\Canopy\User\Scripts\pyinstaller.exe -y win_build.spec
copy /Y dist\CIFellipsoid\CIFellipsoid.exe dist\distellipsoid_win\CIFellipsoid.exe
copy /Y dist\CIFellipsoid\CIFellipsoid.exe.manifest dist\distellipsoid_win\CIFellipsoid.exe.manifest
move /Y dist\distellipsoid_win dist\distellipsoid_win64

pause

REM ******* 32-bit Version *********
REM Remove existing distellipsoid_win folder, to prevent old files hanging around
echo **********************
echo Freezing 32-bit python
echo **********************
RMDIR /S /Q dist\distellipsoid_win
REM Run 64-bit PyInstaller, copy CIFellipsoid files across and then move entire directory to 64-bit folder
C:\Users\JCC\AppData\Local\enthought\Canopy32\User\Scripts\pyinstaller.exe -y win_build.spec
copy /Y dist\CIFellipsoid\CIFellipsoid.exe dist\distellipsoid_win\CIFellipsoid.exe
copy /Y dist\CIFellipsoid\CIFellipsoid.exe.manifest dist\distellipsoid_win\CIFellipsoid.exe.manifest
move /Y dist\distellipsoid_win dist\distellipsoid_win32

pause

echo
echo **************************************************************
echo Finished PyInstaller freeze; now compiling InnoSetup installer
echo **************************************************************

"C:\Program Files (x86)\Inno Setup 5\ISCC.exe" PIE_win_installer.iss

pause