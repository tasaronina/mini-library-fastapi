node {
    stage('Checkout') {
        checkout scm
    }

    stage('Build catalog image') {
        bat 'docker build -t mini-library-catalog:lab3 -f backend-catalog/Dockerfile .'
    }

    stage('Build loans image') {
        bat 'docker build -t mini-library-loans:lab3 -f backend-loans/Dockerfile .'
    }

    stage('Build frontend image') {
        bat 'docker build -t mini-library-frontend:lab3 -f frontend/Dockerfile .'
    }

    stage('Test') {
        bat 'docker run --rm mini-library-catalog:lab3 python -c "import catalog.main"'
        bat 'docker run --rm mini-library-loans:lab3 python -c "import loans.main"'
    }

    if (env.BRANCH_NAME == 'main' || env.GIT_BRANCH == 'origin/main') {
        withEnv(['KUBECONFIG=C:\\Users\\Tasya\\.kube\\config']) {
            stage('Deploy to Kubernetes') {
                bat 'kubectl --context docker-desktop apply -f k8s'
                bat 'kubectl --context docker-desktop rollout restart deployment/backend-catalog-deployment'
                bat 'kubectl --context docker-desktop rollout restart deployment/backend-loans-deployment'
                bat 'kubectl --context docker-desktop rollout restart deployment/frontend-deployment'
            }

            stage('Verify deployment') {
                bat 'kubectl --context docker-desktop rollout status deployment/backend-catalog-deployment --timeout=180s'
                bat 'kubectl --context docker-desktop rollout status deployment/backend-loans-deployment --timeout=180s'
                bat 'kubectl --context docker-desktop rollout status deployment/frontend-deployment --timeout=180s'
                bat 'kubectl --context docker-desktop get deployments'
                bat 'kubectl --context docker-desktop get pods'
                bat 'kubectl --context docker-desktop get svc'
            }
        }
    }
}