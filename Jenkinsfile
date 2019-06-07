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
                            artifact_artifact_path = './artifacts/vropscli* --user ${VROPSCLI_USER} --password ${VROPSCLI_PASSWORD} --host vropscli-ci.bluemedora.localnet'
                            license = "4/trialparticipant/06-06-2019-23:01:59/BM-VREALIZE-ORACLE-DB/enterprise/no-expiration/MP/accumulating/BM-VREALIZE-ORACLE-DB/50/2F90B289C5A81305CAB089F840118E01B0E77C59"
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
                                sh '''${artifact_path}'''
                            }
                        }
                        stage('Downlaod oracle pack'){
                            steps {
                                sh '''wget https://s3.amazonaws.com/products.bluemedora.com/vrops_production_builds/oracle_database/1.2.0/OracleDatabase-6.3_1.2.0_b20180319.144115.pak'''
                            }
                        }
                        stage('Install oracle pack'){
                            steps {
                                sh '''${artifact_path} uploadPak OracleDatabase-6.3_1.2.0_b20180319.144115.pak'''
                            }
                        }
                        stage('Track install progress'){
                            steps {
                                // Tacking if install finished
                                // If overtime, timeout
                                // #!/bin/bash
                                sh "SECONDS=0"
                                sh '''while [ 1 ]
                                do
                                    ${artifact_path} getCurrentActivity | grep 'is_upgrade_orchestrator_active:          false

                                    if [ echo $?  == 0 ]
                                    then
                                        echo "Install finished, or have never started"
                                        done
                                    elif [ $SECONDS -lt > 1800 ]
                                    then
                                        echo "30 Miniues has passed, the install is taking too long"
                                        exit 1
                                    fi
                                '''
                            }
                        }
                        stage('Get solution id'){
                            steps {
                                sh '''${artifact_path} getSolution | grep \
                                'OracleDatabase,Oracle Database,1.2.0.20180319.144115,OracleDBAdapter'

                                if [ echo $?  == 0 ]
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
                                sh '''${artifact_path} setSolutionLicense OracleDatabase ${license} | \
                                xargs | grep 'license key installed True'

                                if [ echo $?  == 0 ]
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
                                sh '''${artifact_path} getSolutionLicense OracleDatabase | \
                                cut -b 19- | jq .[0].licenseKey | tr -d '"' | grep '${license}'

                                if [ echo $?  == 0 ]
                                then
                                    echo "License Key correct"
                                else
                                    echo "License Key incorrect"
                                    exit 1
                                fi
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
