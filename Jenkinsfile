pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        PYTHON = 'C:/Users/Tasya/AppData/Local/Programs/Python/Python314/python.exe'
        DEPLOY_DIR = 'C:\\JenkinsDeploy\\mini-library-fastapi'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                bat 'if not exist .venv "%PYTHON%" -m venv .venv'
                bat '.venv\\Scripts\\python.exe -m pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                bat '.venv\\Scripts\\python.exe -m compileall -q library'
                bat '.venv\\Scripts\\python.exe -c "from library.main import app; assert sum(len(r.methods) for r in app.routes if r.path.startswith(\'/api/\')) == 20"'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }

            steps {
                bat '''
                    if not exist "%DEPLOY_DIR%" mkdir "%DEPLOY_DIR%"

                    robocopy "%WORKSPACE%" "%DEPLOY_DIR%" /E /XD .git .venv __pycache__ /XF library.db *.pyc Jenkinsfile .gitignore

                    if %ERRORLEVEL% GEQ 8 exit /b %ERRORLEVEL%

                    if not exist "%DEPLOY_DIR%\\.venv" "%PYTHON%" -m venv "%DEPLOY_DIR%\\.venv"

                    "%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" -m pip install -r "%DEPLOY_DIR%\\requirements.txt"
                '''
            }
        }
    }
}