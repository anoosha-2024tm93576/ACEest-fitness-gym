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
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('Lint') {
            steps {
                echo 'Running lint...'
                sh 'pip3 install flake8 && flake8 app.py --max-line-length=120 --ignore=E501'
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'python3 -m pytest -v'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t aceest-fitness:latest .'
            }
        }

        stage('Docker Test') {
            steps {
                echo 'Running tests inside Docker...'
                sh 'docker run --rm aceest-fitness:latest pytest -v'
            }
        }

    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the logs above.'
        }
    }
}