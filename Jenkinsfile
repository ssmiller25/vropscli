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
                    environment {
                            artifact_path_and_creds = "./artifacts/vropscli* --user ${env.VROPSCLI_USER} --password ${env.VROPSCLI_PASSWORD} --host vropscli-ci.bluemedora.localnet"
                            license = credentials('vropscli_ci_license')
                            //adapter = ''
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
                                sh '''${artifact_path_and_creds}'''
                            }
                        }
                        stage('Downlaod oracle pack'){
                            steps {
                                sh '''wget https://s3.amazonaws.com/products.bluemedora.com/vrops_production_builds/oracle_database/1.2.0/OracleDatabase-6.3_1.2.0_b20180319.144115.pak'''
                            }
                        }
                        stage('Install oracle pack'){
                            steps {
                                sh '''${artifact_path_and_creds} uploadPak OracleDatabase-6.3_1.2.0_b20180319.144115.pak'''
                            }
                        }
                        stage('Track install progress'){
                            steps {
                                // Tacking if install finished
                                // If overtime, timeout
                                // #!/bin/bash
                                sh '''SECONDS=0
                                while [ 1 ]
                                do
                                    ${artifact_path_and_creds} getCurrentActivity | grep 'is_upgrade_orchestrator_active:          false' && break

                                if [ $SECONDS -gt 1800 ]
                                    then
                                        echo "30 Miniues has passed, the install is taking too long"
                                        exit 1
                                    fi
                                done
                                '''
                            }
                        }
                        stage('Get solution id'){
                            steps {
                                sh '''${artifact_path_and_creds} getSolution | grep \
                                'OracleDatabase,Oracle Database,1.2.0.20180319.144115,OracleDBAdapter'

                                if [ $?  == 0 ]
                                    then
                                        echo "Solution id corrected"
                                    else
                                        echo "Solution id incorrect"
                                        exit 1
                                    fi
                                '''
                            }
                        }
                        stage('Set solution license') {
                            steps{
                                sh '''${artifact_path_and_creds} setSolutionLicense OracleDatabase ${license} | \
                                xargs | grep 'license key installed True'

                                if [ $?  == 0 ]
                                then
                                    echo "License Key install success"
                                else
                                    echo "License Key install error"
                                    exit 1
                                fi
                                '''
                            }
                        }
                        stage('Get current licenses installed'){
                            steps {
                                sh '''${artifact_path_and_creds} getSolutionLicense OracleDatabase | \
                                cut -b 19- | jq .[0].licenseKey | tr -d '"' | grep ${license}

                                if [ $?  == 0 ]
                                then
                                    echo "License Key correct"
                                else
                                    echo "License Key incorrect"
                                    exit 1
                                fi
                                '''
                            }
                        }
                        stage('Get adapter instance'){
                            steps {
                                // Get the first adapter
                                script {
                                    env.adapter = sh (
                                        script: '${artifact_path_and_creds} getAdapters \
                                        | sed '1d' | sort | sed -n 1p | tr ',' '\n' | sed -n 1p', 
                                            returnStdout: true
                                    ).trim()
                                } 
                            }
                        }
                        stage('Stop adapter instance'){
                            steps {
                                sh '''${artifact_path_and_creds} stopAdapterInstance ${adapter} \
                                | grep 'Adapter Stopped'

                                if [ $?  == 0 ]
                                then
                                    echo "Adapter stopped"
                                else
                                    echo "Error with stopping the adapter"
                                    exit 1
                                fi

                                SECONDS=0
                                while [ 1 ]
                                do
                                    ${artifact_path_and_creds} getAdapterCollectionStatus ${adapter} \
                                    | grep 'The adapter is powered off' && break

                                if [ $SECONDS -gt 60 ]
                                    then
                                        echo "The adapter is taking too long to stop"
                                        exit 1
                                    fi
                                done
                                '''
                            }
                        }
                        stage('Start adapter instance'){
                            steps {
                                sh '''${artifact_path_and_creds} startAdapterInstance ${adapter} \
                                | grep 'Adapter Started'

                                if [ $?  == 0 ]
                                then
                                    echo "Adapter started"
                                else
                                    echo "Error with starting the adapter"
                                    exit 1
                                fi

                                SECONDS=0
                                while [ 1 ]
                                do
                                    ${artifact_path_and_creds} getAdapterCollectionStatus ${adapter} \
                                    | grep 'The adapter is on' && break

                                if [ $SECONDS -gt 120 ]
                                    then
                                        echo "The adapter is taking too long to start"
                                        exit 1
                                    fi
                                done
                                '''
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
