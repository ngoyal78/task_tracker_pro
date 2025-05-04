@echo off
echo ===================================
echo Ollama Setup for Task Tracker Pro
echo ===================================
echo.

REM Check if Ollama is installed
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Ollama is not installed on your system.
    echo.
    echo Please install Ollama from https://ollama.ai/download
    echo After installation, run this script again.
    echo.
    pause
    exit /b 1
)

echo Ollama is installed. Checking if Ollama service is running...
echo.

REM Check if Ollama service is running
curl -s http://localhost:11434/api/version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Ollama service is not running.
    echo.
    echo Starting Ollama service...
    start /b ollama serve
    echo Waiting for Ollama to start...
    timeout /t 5 /nobreak >nul
    
    REM Check again if service is running
    curl -s http://localhost:11434/api/version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to start Ollama service.
        echo Please start it manually with 'ollama serve' in a separate terminal.
        echo.
        pause
        exit /b 1
    )
    echo Ollama service started successfully.
) else (
    echo Ollama service is running.
)
echo.

REM Check available models
echo Checking available models...
ollama list

echo.
echo Recommended model for Task Tracker Pro: mistral
echo.

REM Check if mistral model is available
ollama list | findstr "mistral" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo The recommended model 'mistral' is not available.
    echo.
    set /p INSTALL_MODEL=Would you like to pull the mistral model now? (y/n): 
    if /i "%INSTALL_MODEL%"=="y" (
        echo.
        echo Pulling mistral model (this may take a few minutes)...
        ollama pull mistral
        echo.
        echo Model downloaded successfully.
    ) else (
        echo.
        echo You can pull the model later with 'ollama pull mistral'
        echo Or use a different model by updating your .env file.
    )
) else (
    echo The recommended model 'mistral' is already available.
)

echo.
echo ===================================
echo Setup Complete!
echo ===================================
echo.
echo You can now use the GenAI task creation feature.
echo Make sure your .env file has the following settings:
echo.
echo OLLAMA_BASE_URL=http://localhost:11434
echo OLLAMA_MODEL=mistral
echo.
echo To test your setup, run: python test_ollama.py
echo.
pause
