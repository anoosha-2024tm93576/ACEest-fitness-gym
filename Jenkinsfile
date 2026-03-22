pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                sh 'pip3 install -r requirements.txt --break-system-packages'
            }
        }

        stage('Lint') {
            steps {
                echo 'Running lint...'
                sh 'python3 -m flake8 app.py --max-line-length=120 --ignore=E501'
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'python3 -m pytest -v'
            }
        }
    }

    post {
        success {
            echo 'Pipeline passed.'
        }
        failure {
            echo 'Pipeline failed. Check the logs above.'
        }
    }
}