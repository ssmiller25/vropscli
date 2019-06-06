pipeline {
	agent any
    
    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }
        stage('Run build script'){
            parallel{
                stage('Run linux build script') {
                    agent {
                        label "linux && docker"
                    }
                    steps {
                        sh '''./build.sh'''
                    }
                }
                stage ('Run windows build script'){
                    agent {
                        label "windows"
                    }
                    steps{
                    bat '''python -m pip install --upgrade pip
                        pip install --upgrade pip

                        pip install pipenv


                        pipenv --python 3.7
                        pipenv lock --pre
                        pipenv sync

                        pipenv install pyinstaller
                        pipenv run pyinstaller -F vropscli.py'''
                    }
                }
            }
	}
    }
} 
