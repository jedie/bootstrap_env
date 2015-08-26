@echo off

title "%~0"

set python=C:\Python34\python.exe
if NOT exist %python% (
    set python=C:\Python27\python.exe
    if NOT exist %python% (
        echo ERROR: can't find 'python.exe' !
        echo Please edit this file: "%~dp0"
        pause
        exit 1
    )
)

set boot_script=boot.py
if NOT exist %boot_script% (
    echo ERROR: '%boot_script%' doesn't exists?!?
    echo Please edit this file: "%~dp0"
    pause
    exit 1
)

set destination=%APPDATA%\bootstrap_env
mkdir %destination%
if NOT exist %destination% (
    echo ERROR: '%destination%' doesn't exists?!?
    echo Please edit this file: "%~dp0"
    pause
    exit 1
)

echo on
%python% %boot_script% --install_type=pypi %destination%
explorer.exe %destination%
@pause