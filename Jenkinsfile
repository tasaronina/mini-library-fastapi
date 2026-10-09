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
                powershell '''
            $ErrorActionPreference = "Stop"

            $deployDir = $env:DEPLOY_DIR
            $port = 8001
            $siteUrl = "http://127.0.0.1:$port/"
            $venvDir = Join-Path $deployDir ".venv"
            $deployPython = Join-Path $venvDir "Scripts\\python.exe"

            New-Item `
                -ItemType Directory `
                -Path $deployDir `
                -Force |
                Out-Null

            $oldConnections = Get-NetTCPConnection `
                -State Listen `
                -LocalPort $port `
                -ErrorAction SilentlyContinue

            foreach ($connection in $oldConnections) {
                Stop-Process `
                    -Id $connection.OwningProcess `
                    -Force `
                    -ErrorAction SilentlyContinue
            }

            robocopy `
                $env:WORKSPACE `
                $deployDir `
                /E `
                /XD .git .venv __pycache__ .pytest_cache `
                /XF library.db *.pyc Jenkinsfile .gitignore

            if ($LASTEXITCODE -ge 8) {
                throw "Не удалось скопировать файлы"
            }

            if (-not (Test-Path $deployPython)) {
                & $env:PYTHON -m venv $venvDir

                if ($LASTEXITCODE -ne 0) {
                    throw "Не удалось создать виртуальное окружение"
                }
            }

            & $deployPython `
                -m pip install `
                -r (Join-Path $deployDir "requirements.txt")

            if ($LASTEXITCODE -ne 0) {
                throw "Не удалось установить зависимости"
            }

            $env:JENKINS_NODE_COOKIE = "dontKillMe"

            $server = Start-Process `
                -FilePath $deployPython `
                -ArgumentList `
                    "-m",
                    "uvicorn",
                    "library.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "$port" `
                -WorkingDirectory $deployDir `
                -WindowStyle Hidden `
                -PassThru

            $siteIsReady = $false

            for ($attempt = 1; $attempt -le 20; $attempt++) {
                try {
                    $response = Invoke-WebRequest `
                        -UseBasicParsing `
                        -Uri $siteUrl `
                        -TimeoutSec 2

                    if ($response.StatusCode -eq 200) {
                        $siteIsReady = $true
                        break
                    }
                }
                catch {
                    Start-Sleep -Seconds 1
                }
            }

            if (-not $siteIsReady) {
                if (-not $server.HasExited ) {
                    Stop-Process `
                        -Id $server.Id `
                        -Force `
                        -ErrorAction SilentlyContinue
                }

                throw "Сайт не запустился на порту $port"
            }

            Write-Output "Site started at $siteUrl"
                '''
            }
        }
    }
}