pipeline {
	agent any
    environment {
        VERSION = sh '''cat vropscli.py | grep 'VERSION=' | cut -b 9- | tr -d '"'''
        VROPSCLI_USER = credentials('vropscli_user')
        VROPSCLI_PASSWORD = credentials('vropscli_password')
    }
    stages {
        stage('Run parallel scripts'){
            parallel{
                stages ('Linux'){
                    agent {
                        label "linux && docker"
                    }
                    stage('Checkout SCM') {
                        steps {
                            checkout scm
                        }
                    }
                    stage('Run linux build script') {
                        steps {
                            sh '''./build.sh'''
                        }
                    }
                    stage('Test linux build commands') {
                        steps {
                            sh '''./artifacts/vropscli_linux_v$VERSION --user $VROPSCLI_USER --password VROPSCLI_PASSWORD --host vropscli-ci.bluemedora.localnet'''
                        }
                    }
                }
                stages ('Windows'){
                    agent {
                        label "windows"
                    }
                    stage('Checkout SCM') {
                        steps {
                            checkout scm
                        }
                    }
                    stage('Run windows build script') {
                        steps {
                            bat '''python -m pip install --upgrade pip

                            pip install pipenv

                            pipenv --python 3.7
                            pipenv lock --pre
                            pipenv sync

                            pipenv install pyinstaller
                            pipenv run pyinstaller -F vropscli.py'''
                        }
                    }
                    stage('Test windows build commands') {
                        steps {
                            bat '''dist\\vropscli --user $VROPSCLI_USER --password VROPSCLI_PASSWORD --host vropscli-ci.bluemedora.localnet'''
                        }
                    }
                }           
            }
        }
    }
}
