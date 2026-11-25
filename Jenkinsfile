@Library('khaojai-ci@v1') _

khaojaiPipeline(
    project: 'sec-gate-poc',
    pushBranches: [],
    services: [
        [name: 'user-service', path: 'services/user-service', lang: 'python', build: false],
        [name: 'contact-service', path: 'services/contact-service', lang: 'python', build: false],
    ],
    integration: {
        withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
            for (svc in ['user-service', 'contact-service']) {
                // The plugin records one analysis per block, from the first report-task.txt in the workspace.
                withSonarQubeEnv('sonarqube') {
                    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE', message: "SonarQube quality gate failed: ${svc}") {
                        sh "sh scripts/sonar-scan.sh services/${svc}"
                    }
                }
                sh "rm -rf services/${svc}/.scannerwork"
            }
        }
    },
    notify: [channel: 'none'],
)
