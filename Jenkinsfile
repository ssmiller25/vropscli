pipeline {
    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }
        stage('Run build script') {
            steps {
                sh '''./build.sh'''
            }
        }
    }
    post {
        echo currentBuild.result
    }
} 
