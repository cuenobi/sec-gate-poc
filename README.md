# sec-gate-poc

Two FastAPI services used to try SonarQube (and later Strix) as a security gate for Flowen's Python services.
`main` is the clean baseline; `planted-vulns` adds known issues. `docs/findings.md` records what each tool caught.

## Local

```bash
sh scripts/sonar-bootstrap.sh            # SonarQube on http://localhost:9000, writes .env
sh scripts/verify.sh services/user-service
sh scripts/sonar-scan.sh services/user-service
```

`scripts/verify.sh` expects `jenkins-library` next to this repository; set `KHAOJAI_CI` otherwise.
The admin password is in `.env` (`SONAR_ADMIN_PASSWORD`).

Simulate a pull request analysis:

```bash
CHANGE_ID=1 CHANGE_BRANCH=planted-vulns CHANGE_TARGET=main sh scripts/sonar-scan.sh services/user-service
```

## Jenkins

The `Jenkinsfile` runs the scan in `khaojai-ci`'s `integration` closure with the Secret text credential `sonar-token`.

## Use the shared SonarQube from another repository

SonarQube runs at https://sonarqube.khaojai.it for every project (deployment notes: "SonarQube" in the argocd-apps README).
A repository built with `khaojai-ci` starts scanning with three changes:

1. A `sonar-project.properties` in each service directory, like `services/user-service/sonar-project.properties`, with a
   `sonar.projectKey` of the form `<repo>_<service>`. Add `relative_files = true` under `[tool.coverage.run]` and
   `pythonpath = ["src"]` under `[tool.pytest.ini_options]` so coverage resolves.
2. `scripts/sonar-scan.sh` copied from this repository.
3. The `integration` closure from this repository's `Jenkinsfile`, with its own service list.

The first scan of a branch creates the project. SonarQube names the project's main branch `main`; for a repository
whose long-lived branch is `develop`, rename the main branch to `develop` in Project Settings > Branches and Pull
Requests after that first scan, so pull requests are compared with the right branch. To see a private project, ask a
SonarQube admin to add you or your group to it.
