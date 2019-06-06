pipeline {
	agent any
    environment {
        VERSION = sh '''cat vropscli.py | grep 'VERSION=' | cut -b 9- | tr -d '"'''
        VROPSCLI_USER = credentials('vropscli_user')
        VROPSCLI_PASSWORD = credentials('vropscli_password')
    }
    stages {
        stage('Run build script'){
            parallel{
                stage('Run linux build script') {
                    agent {
                        label "linux && docker"
                    }
                    steps {
                        checkout scm
                        sh '''./build.sh'''
                    }
                    steps {
                        sh '''./artifacts/vropscli_linux_v$VERSION --user $VROPSCLI_USER --password VROPSCLI_PASSWORD --host vropscli-ci.bluemedora.localnet'''
                    }
                }
                stage ('Run windows build script'){
                    agent {
                        label "windows"
                    }
                    steps{
                        checkout scm
                        bat '''python -m pip install --upgrade pip

                        pip install pipenv

                        pipenv --python 3.7
                        pipenv lock --pre
                        pipenv sync

                        pipenv install pyinstaller
                        pipenv run pyinstaller -F vropscli.py'''
                    }
                    steps {
                        bat '''dist\\vropscli --user $VROPSCLI_USER --password VROPSCLI_PASSWORD --host vropscli-ci.bluemedora.localnet'''
                    }
                }
            }
	}
    }
} 
