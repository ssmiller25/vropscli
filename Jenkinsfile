pipeline {
	agent any
    environment {
        //VERSION = sh '''cat vropscli.py | grep 'VERSION=' | cut -b 9- | tr -d '"'''
        VROPSCLI_USER = credentials('vropscli_user')
        VROPSCLI_PASSWORD = credentials('vropscli_password')
    }
    stages {
        stage('Run parallel scripts'){
            parallel{
                stage ('Linux'){
                    agent {
                        label "linux && docker"
                    }
                    stages{
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

                            //withCredentials([usernamePassword(credentialsId: 'vropscli_user', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                            steps {
                                //withCredentials([string(credentialsId: 'vropscli_user', variable: 'VROPSCLI_USER'), string(credentialsId: 'vropscli_password', variable: 'VROPSCLI_PASSWORD')]) {
                                sh '''
                                echo ${VROPSCLI_USER} 
                                echo ${VROPSCLI_PASSWORD}
                                ./artifacts/vropscli_linux_v1.2.2 --user ${VROPSCLI_USER} --password ${VROPSCLI_PASSWORD} --host vropscli-ci.bluemedora.localnet'''
                                //}
                            }
                        }
                    }
                }
                stage ('Windows'){
                    agent {
                        label "windows"
                    }
                    stages {
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
                                bat '''dist\\vropscli --user ${env.VROPSCLI_USER_PSW} --password ${env.VROPSCLI_PASSWORD_PSW} --host vropscli-ci.bluemedora.localnet'''
                            }
                        }
                    }
                }           
            }
        }
    }
}
