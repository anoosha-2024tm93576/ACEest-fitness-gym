pipeline {
    agent any

    environment {
        IMAGE_NAME = "2024tm93576anoosha/aceest-fitness"
        IMAGE_TAG = "v4.1.${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }

        stage('Install, Lint, Test') {
            steps {
                echo 'Running inside Python container...'
                sh '''
                    docker run --rm -v $(pwd):/app -w /app python:3.11-slim \
                    sh -c "
                    pip install -r requirements.txt &&
                    python -m flake8 app.py --max-line-length=120 --ignore=E501 &&
                    python -m pytest -v
                    "
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG .'
            }
        }

        stage('Login to Docker Hub') {
            steps {
                echo 'Logging into Docker Hub...'
                withCredentials([usernamePassword(
                credentialsId: 'dockerhub-credentials',
                usernameVariable: 'DOCKER_USER',
                passwordVariable: 'DOCKER_PASS'
                )]) {
                sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                echo 'Pushing Docker image...'
                sh 'docker push $IMAGE_NAME:$IMAGE_TAG'
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