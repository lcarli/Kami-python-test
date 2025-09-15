@echo off
REM Script Batch para iniciar o Kami Bot e servidor web
REM start_all.bat

title KAMI BOT LAUNCHER
color 0B

echo.
echo ========================================
echo         KAMI BOT LAUNCHER - BATCH
echo ========================================
echo.

REM Verificar se os arquivos existem
if not exist "app.py" (
    echo [ERROR] Arquivo app.py nao encontrado!
    pause
    exit /b 1
)

if not exist "start_web_client.py" (
    echo [ERROR] Arquivo start_web_client.py nao encontrado!
    pause
    exit /b 1
)

echo [INFO] Iniciando servidor do bot...
start "Kami Bot Server" /min cmd /c "python app.py"

echo [INFO] Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

echo [INFO] Iniciando servidor web do cliente...
start "Kami Web Client" /min cmd /c "python start_web_client.py"

echo [INFO] Aguardando 2 segundos...
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo       SERVICOS INICIADOS!
echo ========================================
echo.
echo Bot:        http://localhost:3978
echo Web Client: http://localhost:8080/voice-client.html
echo.
echo [INFO] Abrindo navegador...
start "" "http://localhost:8080/voice-client.html"

echo.
echo ========================================
echo          RECURSOS DISPONIVEIS
echo ========================================
echo.
echo * Reconhecimento de voz em portugues
echo * Sintese de voz nas respostas  
echo * IA GPT-4o da Azure
echo * Chat em tempo real
echo.
echo ========================================
echo            INSTRUCOES
echo ========================================
echo.
echo 1. Use o navegador que foi aberto
echo 2. Clique no microfone para falar
echo 3. Digite mensagens no campo de texto
echo 4. Para parar: feche esta janela ou Ctrl+C
echo.
echo Pressione qualquer tecla para sair...
pause >nul

echo.
echo [INFO] Parando servicos...
taskkill /f /im python.exe >nul 2>&1
echo [INFO] Servicos parados.
echo.
echo Obrigado por usar o Kami Bot!
timeout /t 2 /nobreak >nul