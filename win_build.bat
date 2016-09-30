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

MKDIR dist\distellipsoid_win64
RMDIR /S /Q dist\distellipsoid_win64
REM Run 64-bit PyInstaller, copy CIFellipsoid files across and then move entire directory to 64-bit folder
C:\Users\JCC\AppData\Local\enthought\Canopy\User\Scripts\pyinstaller.exe -y win_build64.spec
copy /Y dist\CIFellipsoid64\CIFellipsoid.exe dist\distellipsoid_win64\CIFellipsoid.exe
copy /Y dist\CIFellipsoid64\CIFellipsoid.exe.manifest dist\distellipsoid_win64\CIFellipsoid.exe.manifest
REM move /Y dist\distellipsoid_win dist\distellipsoid_win64

REM pause

REM ******* 32-bit Version *********
REM Remove existing distellipsoid_win folder, to prevent old files hanging around
echo **********************
echo Freezing 32-bit python
echo **********************

MKDIR dist\distellipsoid_win32
RMDIR /S /Q dist\distellipsoid_win32
REM Run 64-bit PyInstaller, copy CIFellipsoid files across and then move entire directory to 64-bit folder
C:\Users\JCC\AppData\Local\enthought\Canopy32\User\Scripts\pyinstaller.exe -y win_build32.spec
copy /Y dist\CIFellipsoid32\CIFellipsoid.exe dist\distellipsoid_win32\CIFellipsoid.exe
copy /Y dist\CIFellipsoid32\CIFellipsoid.exe.manifest dist\distellipsoid_win32\CIFellipsoid.exe.manifest
REM move /Y dist\distellipsoid_win dist\distellipsoid_win32

REM pause

echo
echo **************************************************************
echo Finished PyInstaller freeze; now compiling InnoSetup installer
echo **************************************************************

"C:\Program Files (x86)\Inno Setup 5\ISCC.exe" PIE_win_installer.iss

pause