pipeline {
    agent any
    
    triggers {
        cron('0 2 * * *')  // 2 AM daily
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pip install pytest pytest-html pytest-json-report'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'pytest --html=report.html --json-report --json-report-file=report.json --junit-xml=results.xml'
            }
            post {
                always {
                    junit 'results.xml'
                    publishHTML([reportDir: '.', reportFiles: 'report.html', reportName: 'Test Report'])
                }
            }
        }
        
        stage('Build') {
            steps {
                sh 'python setup.py build'
            }
        }
        
        stage('Archive Results') {
            steps {
                sh 'python scripts/archive_results.py'
            }
        }
    }
    
    post {
        always {
            emailext(
                subject: "Nightly Build ${currentBuild.result}",
                body: "Build ${env.BUILD_NUMBER} - ${currentBuild.result}",
                to: "manager@company.com"
            )
        }
    }
}