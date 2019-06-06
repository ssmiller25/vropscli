pipeline {
	agent any
    environment {
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
                            steps {
                                sh '''./artifacts/vropscli* --user ${VROPSCLI_USER} --password ${VROPSCLI_PASSWORD} --host vropscli-ci.bluemedora.localnet'''
                            }
                        }
                        stage('Downlaod oracle pack'){
                            steps {
                                sh '''wget https://s3.amazonaws.com/products.bluemedora.com/vrops_production_builds/oracle_database/1.2.0/OracleDatabase-6.3_1.2.0_b20180319.144115.pak'''
                            }
                        }
                        stage('Install oracle pack'){
                            steps {
                                sh '''./artifacts/vropscli* \
                                --user ${VROPSCLI_USER} \
                                --password ${VROPSCLI_PASSWORD} \
                                --host vropscli-ci.bluemedora.localnet \
                                uploadPak OracleDatabase-6.3_1.2.0_b20180319.144115.pak'''
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
                                bat '''dist\\vropscli --user %VROPSCLI_USER% --password %VROPSCLI_PASSWORD% --host vropscli-ci.bluemedora.localnet'''
                            }
                        }
                    }
                }           
            }
        }
    }
}
