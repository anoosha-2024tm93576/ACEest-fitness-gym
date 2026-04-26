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

        stage('Install Dependencies') {
            steps {
                sh 'pip3 install -r requirements.txt --break-system-packages'
            }   
        }

        stage('Lint') {
            steps {
                sh 'python3 -m flake8 app.py --max-line-length=120 --ignore=E501'
            }
        }

        stage('Test') {
            steps {
                sh 'python3 -m pytest -v'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube analysis...'
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        sonar-scanner \
                            -Dsonar.projectKey=aceest-fitness \
                            -Dsonar.projectName="ACEest Fitness & Gym" \
                            -Dsonar.projectVersion=3.2.4 \
                            -Dsonar.sources=. \
                            -Dsonar.exclusions=tests/**,**/__pycache__/**,*.db,k8s/**,postman/** \
                            -Dsonar.python.version=3 \
                            -Dsonar.host.url=http://host.docker.internal:9000 \
                            -Dsonar.token=$SONAR_TOKEN
                    '''
                }
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

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying to Kubernetes...'
                sh 'kubectl set image deployment/aceest-fitness aceest-fitness=$IMAGE_NAME:$IMAGE_TAG'
                sh 'kubectl rollout status deployment/aceest-fitness'
            }
        }
    }

    post {
        success {
            echo 'Pipeline passed successfully.'
        }
        failure {
            echo 'Pipeline failed. Rolling back to last stable version...'
            sh 'kubectl rollout undo deployment/aceest-fitness'
        }
    }
}