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
