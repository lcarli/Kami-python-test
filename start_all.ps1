# Script PowerShell para iniciar o Kami Bot e servidor web
# start_all.ps1

Write-Host "🚀 KAMI BOT LAUNCHER - PowerShell" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan

# Verificar se os arquivos existem
if (-not (Test-Path "app.py")) {
    Write-Host "❌ app.py file not found!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "start_web_client.py")) {
    Write-Host "❌ start_web_client.py file not found!" -ForegroundColor Red
    exit 1
}

# Function to stop processes
function Stop-Services {
    Write-Host "🛑 Stopping services..." -ForegroundColor Yellow
    
    if ($botJob) {
        Stop-Job $botJob -ErrorAction SilentlyContinue
        Remove-Job $botJob -ErrorAction SilentlyContinue
        Write-Host "✅ Bot parado" -ForegroundColor Green
    }
    
    if ($webJob) {
        Stop-Job $webJob -ErrorAction SilentlyContinue
        Remove-Job $webJob -ErrorAction SilentlyContinue
        Write-Host "✅ Servidor web parado" -ForegroundColor Green
    }
    
    # Matar processos Python se ainda estiverem rodando
    Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Configurar handler para Ctrl+C
$null = Register-EngineEvent PowerShell.Exiting -Action {
    Stop-Services
}

try {
    Write-Host "🤖 Iniciando servidor do bot..." -ForegroundColor Blue
    $botJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        python app.py
    }
    
    Start-Sleep -Seconds 3
    
    Write-Host "🌐 Iniciando servidor web do cliente..." -ForegroundColor Blue
    $webJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        python start_web_client.py
    }
    
    Start-Sleep -Seconds 2
    
    Write-Host "⏳ Waiting for services to become available..." -ForegroundColor Yellow
    
    # Testar conectividade
    $botReady = $false
    $webReady = $false
    
    for ($i = 1; $i -le 30; $i++) {
        try {
            $null = Invoke-WebRequest -Uri "http://localhost:3978" -TimeoutSec 1 -ErrorAction SilentlyContinue
            $botReady = $true
            Write-Host "✅ Bot is responding!" -ForegroundColor Green
            break
        }
        catch {
            Write-Host "⏳ Aguardando bot... ($i/30)" -ForegroundColor Yellow
            Start-Sleep -Seconds 1
        }
    }
    
    for ($i = 1; $i -le 10; $i++) {
        try {
            $null = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 1 -ErrorAction SilentlyContinue
            $webReady = $true
            Write-Host "✅ Web server is responding!" -ForegroundColor Green
            break
        }
        catch {
            Write-Host "⏳ Aguardando servidor web... ($i/10)" -ForegroundColor Yellow
            Start-Sleep -Seconds 1
        }
    }
    
    if ($botReady -and $webReady) {
        Write-Host ""
        Write-Host "=" * 60 -ForegroundColor Green
        Write-Host "🎉 KAMI BOT - ALL SERVICES STARTED!" -ForegroundColor Green
        Write-Host "=" * 60 -ForegroundColor Green
        Write-Host ""
        Write-Host "🤖 Bot: ✅ RODANDO em http://localhost:3978" -ForegroundColor Green
        Write-Host "🌐 Web: ✅ RODANDO em http://localhost:8080" -ForegroundColor Green
        Write-Host ""
        Write-Host "🔗 LINKS DE ACESSO:" -ForegroundColor Cyan
        Write-Host "• Cliente Web: http://localhost:8080/voice-client.html" -ForegroundColor White
        Write-Host "• API do Bot: http://localhost:3978/api/messages" -ForegroundColor White
        Write-Host ""
        Write-Host "🎯 AVAILABLE FEATURES:" -ForegroundColor Cyan
        Write-Host "• 🎤 Voice recognition in English" -ForegroundColor White
        Write-Host "• 🔊 Voice synthesis in responses" -ForegroundColor White
        Write-Host "• 🧠 IA GPT-4o da Azure" -ForegroundColor White
        Write-Host "• 💬 Chat em tempo real" -ForegroundColor White
        Write-Host ""
        Write-Host "📋 COMANDOS:" -ForegroundColor Cyan
        Write-Host "• Ctrl+C: Stop all services" -ForegroundColor White
        Write-Host "• Enter: Check service status" -ForegroundColor White
        Write-Host ""
        
        # Abrir navegador automaticamente
        Write-Host "🌐 Abrindo navegador..." -ForegroundColor Blue
        Start-Process "http://localhost:8080/voice-client.html"
        
        Write-Host "💡 Pressione Enter para verificar status ou Ctrl+C para sair" -ForegroundColor Yellow
        
        # Loop principal
        while ($true) {
            $userInput = Read-Host
            
            # Verificar status dos jobs
            $botStatus = Get-Job $botJob | Select-Object -ExpandProperty State
            $webStatus = Get-Job $webJob | Select-Object -ExpandProperty State
            
            Write-Host ""
            Write-Host "📊 STATUS ATUAL:" -ForegroundColor Cyan
            Write-Host "🤖 Bot Job: $botStatus" -ForegroundColor $(if ($botStatus -eq "Running") { "Green" } else { "Red" })
            Write-Host "🌐 Web Job: $webStatus" -ForegroundColor $(if ($webStatus -eq "Running") { "Green" } else { "Red" })
            
            # Testar conectividade
            try {
                $null = Invoke-WebRequest -Uri "http://localhost:3978" -TimeoutSec 2 -ErrorAction SilentlyContinue
                Write-Host "🤖 Bot HTTP: ✅ Respondendo" -ForegroundColor Green
            }
            catch {
                Write-Host "🤖 Bot HTTP: ❌ Not responding" -ForegroundColor Red
            }
            
            try {
                $null = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 2 -ErrorAction SilentlyContinue
                Write-Host "🌐 Web HTTP: ✅ Respondendo" -ForegroundColor Green
            }
            catch {
                Write-Host "🌐 Web HTTP: ❌ Not responding" -ForegroundColor Red
            }
            
            Write-Host ""
        }
    }
    else {
        Write-Host "❌ Not all services are ready" -ForegroundColor Red
        if (-not $botReady) {
            Write-Host "❌ Bot is not responding" -ForegroundColor Red
        }
        if (-not $webReady) {
            Write-Host "❌ Web server is not responding" -ForegroundColor Red
        }
    }
}
catch {
    Write-Host "❌ Error during execution: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Stop-Services
    Write-Host "👋 Kami Bot Launcher finished" -ForegroundColor Cyan
}