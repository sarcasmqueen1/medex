pipeline {
    agent any
    stages {
        stage('Prepare Python venv') {
            steps {
                sh '''
                    python3 -m venv venv
                    . ./venv/bin/activate
                    pip install pipenv
                    pipenv install --dev
                '''
            }

        }
        stage('Python Linting') {
            steps {
                sh '''
                    . ./venv/bin/activate
                    flake8 medex webserver.py --max-line-length 140
                '''
            }
        }
        stage('Python Testing') {
            steps {
                sh '''
                    . ./venv/bin/activate
                    export PYTHONPATH=$(pwd)
                    pytest --junitxml results.xml tests --cov=medex --cov-report xml
                '''
            }
        }
        stage('Setup NodeJS') {
            steps {
                sh '''
                    # Npm will fail due to BeeGFS's hardlink limitation
                    # (see https://doc.beegfs.io/latest/architecture/overview.html#limitations)
                    # in combination with an npm bug
                    # (see https://github.com/npm/cli/issues/5951).
                    # So we need a file system with unrestricted hard links.
                    # We use /tmp.
                    set -e -u
                    if [ -L ~/.npm ]
                    then
                        tmp_dir="$(readlink ~/.npm)"
                        [ -d "$tmp_dir" ] && rm -rf "$tmp_dir"
                    fi
                    rm -rf ~/.npm || true
                    ln -s $(mktemp -d /tmp/jenkins_medex_XXXXXXXXXX) ~/.npm
                    npm install --save-dev
                '''
            }
        }
        stage('Test TypeScript') {
            steps {
                sh '''
                    export PATH="$PATH:$(pwd)/node_modules/typescript/bin"
                    npm run test
                '''
            }
        }
        stage('Check TypeScript Test Coverage') {
            steps {
                clover(
                    cloverReportDir: 'coverage', cloverReportFileName: 'clover.xml',
                    healthyTarget: [methodCoverage: 70, conditionalCoverage: 80, statementCoverage: 80],
                    unhealthyTarget: [methodCoverage: 50, conditionalCoverage: 50, statementCoverage: 50],
                    failingTarget: [methodCoverage: 0, conditionalCoverage: 0, statementCoverage: 0]
                )
            }
        }
    }
    post {
        always {
            junit 'results.xml'
            cobertura coberturaReportFile: 'coverage.xml'
            sh '''
                    if [ -L ~/.npm ]
                    then
                        tmp_dir="$(readlink ~/.npm)"
                        [ -d "$tmp_dir" ] && rm -rf "$tmp_dir"
                    fi
            '''
        }
        failure {
            emailext to: "medex@dieterichlab.org",
            subject: "jenkins build:${currentBuild.currentResult}: ${env.JOB_NAME}",
            body: "${currentBuild.currentResult}: Job ${env.JOB_NAME}\nMore Info can be found here: ${env.BUILD_URL}"
        }
    }
}
