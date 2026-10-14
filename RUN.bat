
@echo off
setlocal
cd /d "%~dp0"

title ONEPAGE STUDY - Editorials Daily

echo.
echo ========================================================================
echo ONEPAGE STUDY - EDITORIALS DAILY
echo ========================================================================
echo.

REM PYTHON ENVIRONMENT
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found.
    echo Expected:
    echo %CD%\.venv\Scripts\python.exe
    echo.
    pause
    exit /b 1
)

set "PYTHON=%CD%\.venv\Scripts\python.exe"

REM STEP 1
echo [1/6] Converting INPUT_DATA.txt to INPUT.json...
echo.

"%PYTHON%" "input_processing\text_to_json_converter.py"

if errorlevel 1 (
    echo.
    echo ERROR: Input conversion failed.
    goto :FAILED
)

echo.
echo Conversion PASSED.
echo.

REM STEP 2
echo [2/6] Validating INPUT.json...
echo.

"%PYTHON%" "input_processing\validator.py"

if errorlevel 1 (
    echo.
    echo ERROR: Input validation failed.
    goto :FAILED
)

echo.
echo Validation PASSED.
echo.

REM STEP 3
echo [3/6] Generating daily PDF...
echo.

"%PYTHON%" -m src.main

if errorlevel 1 (
    echo.
    echo ERROR: Daily PDF generation failed.
    goto :FAILED
)

echo.
echo Daily PDF generation PASSED.
echo.

REM STEP 4
echo [4/6] Building GS repository...
echo.

"%PYTHON%" -m repository.manager.editorial_repository

if errorlevel 1 (
    echo.
    echo ERROR: GS repository generation failed.
    goto :FAILED
)

echo.
echo GS repository generation PASSED.
echo.

REM STEP 5
echo [5/6] Organising daily PDF by year and month...
echo.

"%PYTHON%" -m repository.manager.output_manager

if errorlevel 1 (
    echo.
    echo ERROR: Daily output organisation failed.
    goto :FAILED
)

echo.
echo Daily output organisation PASSED.
echo.

REM STEP 6
echo [6/6] Generating social media image...
echo.

"%PYTHON%" -m repository.manager.social_image_generator

if errorlevel 1 (
    echo.
    echo ERROR: Social image generation failed.
    goto :FAILED
)

echo.
echo Social image generation PASSED.
echo.

REM OPEN SOCIAL IMAGE
echo Opening social media image...
echo.

"%PYTHON%" -c "import json,os,pathlib,datetime; root=pathlib.Path.cwd(); d=datetime.datetime.strptime(json.loads((root/'input_processing'/'INPUT.json').read_text(encoding='utf-8'))['publication_date'],'%%d %%B %%Y'); p=root/'output'/str(d.year)/d.strftime('%%m_%%B')/('UAK_Editorials_Social_'+d.strftime('%%y%%m%%d')+'.png'); assert p.is_file(),f'Social image not found: {p}'; os.startfile(str(p))"

if errorlevel 1 (
    echo.
    echo ERROR: Could not open social media image.
    goto :FAILED
)

REM SUCCESS
echo.
echo ========================================================================
echo PRODUCTION COMPLETE
echo ========================================================================
echo.
echo Input conversion      : PASSED
echo Input validation      : PASSED
echo Daily PDF             : GENERATED
echo GS repository         : GENERATED
echo Output organisation   : PASSED
echo Social image          : GENERATED
echo.
echo Daily output:
echo %CD%\output
echo.
echo GS repository:
echo %CD%\repository
echo.
echo ========================================================================
echo.
pause
exit /b 0

:FAILED
echo.
echo ========================================================================
echo PRODUCTION FAILED
echo ========================================================================
echo.
echo The pipeline stopped because one of the production steps failed.
echo Check the error shown above.
echo.
pause
exit /b 1
