@echo off
setlocal
cd /d "%~dp0"
title ONEPAGE STUDY - Editorials Daily

echo.
echo ========================================================================
echo ONEPAGE STUDY - EDITORIALS DAILY
echo ========================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found.
    echo Expected: %CD%\.venv\Scripts\python.exe
    goto :FAILED
)
set "PYTHON=%CD%\.venv\Scripts\python.exe"

echo.
echo [1/6] Converting INPUT_DATA.txt to INPUT.json...
"%PYTHON%" "input_processing\text_to_json_converter.py"
if errorlevel 1 goto :FAILED

echo.
echo [2/6] Validating INPUT.json...
"%PYTHON%" "input_processing\validator.py"
if errorlevel 1 goto :FAILED

echo.
echo [3/6] Generating daily PDF...
"%PYTHON%" -m src.main
if errorlevel 1 goto :FAILED

echo.
echo [4/6] Building GS repository...
"%PYTHON%" -m repository.manager.editorial_repository
if errorlevel 1 goto :FAILED

echo.
echo [5/6] Generating social media image...
"%PYTHON%" -m repository.manager.social_image_generator
if errorlevel 1 goto :FAILED

echo.
echo [6/6] Archiving original daily input data...
"%PYTHON%" -m repository.manager.input_archive
if errorlevel 1 goto :FAILED

REM Resolve the publication date and find both actual output files.
REM Prefer the standard 10_October folder; support legacy October files for opening.
REM Do not open anything until both files have been confirmed to exist.
echo.
echo Checking generated PDF and image...
"%PYTHON%" -c "import json,pathlib,datetime,sys; r=pathlib.Path.cwd(); j=json.loads((r/'input_processing'/'INPUT.json').read_text(encoding='utf-8')); d=datetime.datetime.strptime(j['publication_date'],'%%d %%B %%Y'); base=r/'output'/str(d.year); folders=[base/d.strftime('%%m_%%B'),base/d.strftime('%%B')]; code=d.strftime('%%y%%m%%d'); pdf=next((p for f in folders for p in [f/('UAK_Editorials_Daily_'+code+'.pdf')] if p.is_file()),None); png=next((p for f in folders for p in [f/('UAK_Editorials_Social_'+code+'.png'),f/('UAK_Editorials_Daily_'+code+'.png')] if p.is_file()),None); print('PDF:',pdf or 'NOT FOUND'); print('Image:',png or 'NOT FOUND'); sys.exit(0 if pdf and png else 1)"
if errorlevel 1 (
    echo ERROR: One or both generated files were not found in the expected year/month folders.
    echo Check the output location configured in social_image_generator.py.
    goto :FAILED
)

echo.
echo Opening generated PDF and image...
"%PYTHON%" -c "import json,pathlib,datetime,os; r=pathlib.Path.cwd(); j=json.loads((r/'input_processing'/'INPUT.json').read_text(encoding='utf-8')); d=datetime.datetime.strptime(j['publication_date'],'%%d %%B %%Y'); base=r/'output'/str(d.year); fs=[base/d.strftime('%%m_%%B'),base/d.strftime('%%B')]; code=d.strftime('%%y%%m%%d'); pdf=next(p for f in fs for p in [f/('UAK_Editorials_Daily_'+code+'.pdf')] if p.is_file()); png=next(p for f in fs for p in [f/('UAK_Editorials_Social_'+code+'.png'),f/('UAK_Editorials_Daily_'+code+'.png')] if p.is_file()); os.startfile(str(pdf)); os.startfile(str(png))"
if errorlevel 1 (
    echo ERROR: Could not open one or both files.
    goto :FAILED
)

echo.
echo ========================================================================
echo PRODUCTION COMPLETE
echo ========================================================================
echo Input conversion      : PASSED
echo Input validation      : PASSED
echo Daily PDF             : GENERATED AND OPENED
echo GS repository         : GENERATED
echo Social image          : GENERATED AND OPENED
echo Input data archive    : SAVED
echo.
echo Daily output: %CD%\output
echo GS repository: %CD%\repository
echo Input data repository: %CD%\repository\input_data
echo ========================================================================
echo.
pause
exit /b 0

:FAILED
echo.
echo ========================================================================
echo PRODUCTION FAILED
echo ========================================================================
echo Check the error above. PDF and image are opened only after successful generation.
echo.
pause
exit /b 1
