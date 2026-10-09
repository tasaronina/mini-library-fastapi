
node {
    def branch = (env.BRANCH_NAME ?: 'unknown')
        .replaceAll('[^A-Za-z0-9_.-]', '-')

    def image = "localhost:5000/mini-library-fastapi:${branch}-${env.BUILD_NUMBER}"

    stage('Checkout') {
        checkout scm
    }

    stage('Build') {
        bat "docker build -t ${image} ."
    }

    stage('Test') {
        bat "docker run --rm ${image} python -m pytest -q"
    }

    stage('Push') {
        bat "docker push ${image}"
    }

    if (env.BRANCH_NAME == 'main') {

        stage('Deploy') {
            withEnv(["APP_IMAGE=${image}"]) {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $deployDir = "C:/JenkinsDeploy/mini-library-docker"
                    $nginxDir = Join-Path $deployDir "nginx"

                    New-Item -ItemType Directory -Path $nginxDir -Force |
                        Out-Null

                    Copy-Item `
                        -LiteralPath (Join-Path $env:WORKSPACE "compose.yaml") `
                        -Destination (Join-Path $deployDir "compose.yaml") `
                        -Force

                    Copy-Item `
                        -LiteralPath (Join-Path $env:WORKSPACE "nginx/nginx.conf") `
                        -Destination (Join-Path $nginxDir "nginx.conf") `
                        -Force

                    $composeFile = Join-Path $deployDir "compose.yaml"

                    docker compose -f $composeFile up -d --no-build --force-recreate api nginx

                    if ($LASTEXITCODE -ne 0) {
                        throw "Docker Compose deployment failed"
                    }
                '''
            }
        }

        stage('Smoke Test') {
            powershell '''
                $ErrorActionPreference = "Stop"
                $url = "http://127.0.0.1:8081/"
                $ready = $false

                for ($i = 1; $i -le 20; $i++) {
                    try {
                        $response = Invoke-WebRequest `
                            -UseBasicParsing `
                            -Uri $url `
                            -TimeoutSec 3

                        if ($response.StatusCode -eq 200) {
                            $ready = $true
                            break
                        }
                    }
                    catch {
                        Start-Sleep -Seconds 1
                    }
                }

                if (-not $ready) {
                    throw "Application is not available"
                }

                Write-Output "Application is available at $url"
            '''
        }
    }
}
