node {
    withEnv([
        'PYTHON=C:/Users/Tasya/AppData/Local/Programs/Python/Python314/python.exe',
        'DEPLOY_DIR=C:\\JenkinsDeploy\\mini-library-fastapi'
    ]) {
        stage('Checkout') {
            checkout scm
        }

        stage('Build') {
            bat 'if not exist .venv "%PYTHON%" -m venv .venv'
            bat '.venv\\Scripts\\python.exe -m pip install -r requirements.txt'
        }

        stage('Test') {
            bat '.venv\\Scripts\\python.exe -m pytest -q'
        }

        if (env.BRANCH_NAME == 'main') {
            stage('Deploy') {
                bat '''
                    if not exist "%DEPLOY_DIR%" mkdir "%DEPLOY_DIR%"

                    powershell -NoProfile -ExecutionPolicy Bypass -Command "$pidFile = Join-Path $env:DEPLOY_DIR 'server.pid'; if (Test-Path $pidFile) { $serverId = Get-Content $pidFile -ErrorAction SilentlyContinue; if ($serverId) { Stop-Process -Id ([int]$serverId) -Force -ErrorAction SilentlyContinue }; Remove-Item $pidFile -Force -ErrorAction SilentlyContinue }; Get-NetTCPConnection -State Listen -LocalPort 8001 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

                    robocopy "%WORKSPACE%" "%DEPLOY_DIR%" /E /XD .git .venv __pycache__ .pytest_cache /XF library.db *.pyc Jenkinsfile .gitignore

                    if %ERRORLEVEL% GEQ 8 exit /b %ERRORLEVEL%

                    if not exist "%DEPLOY_DIR%\\.venv" "%PYTHON%" -m venv "%DEPLOY_DIR%\\.venv"

                    "%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" -m pip install -r "%DEPLOY_DIR%\\requirements.txt"

                    set JENKINS_NODE_COOKIE=dontKillMe
                    powershell -NoProfile -ExecutionPolicy Bypass -Command "$env:JENKINS_NODE_COOKIE='dontKillMe'; $server = Start-Process -FilePath (Join-Path $env:DEPLOY_DIR '.venv\\Scripts\\python.exe') -ArgumentList '-m','uvicorn','library.main:app','--host','127.0.0.1','--port','8001' -WorkingDirectory $env:DEPLOY_DIR -WindowStyle Hidden -RedirectStandardOutput (Join-Path $env:DEPLOY_DIR 'server.log') -RedirectStandardError (Join-Path $env:DEPLOY_DIR 'server-error.log') -PassThru; Set-Content -Path (Join-Path $env:DEPLOY_DIR 'server.pid') -Value $server.Id"

                    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ready = $false; for ($i = 0; $i -lt 20; $i++) { try { $response = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8001/' -TimeoutSec 2; if ($response.StatusCode -eq 200) { $ready = $true; break } } catch {}; Start-Sleep -Seconds 1 }; if (-not $ready) { throw 'Сайт не запустился на порту 8001' }"

                    echo Site started at http://127.0.0.1:8001
                '''
            }
        }
    }
}
