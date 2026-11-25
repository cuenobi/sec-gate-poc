# Findings

Filled in from real runs. "Caught" means the issue appears in the SonarQube analysis of the `planted-vulns` pull request
and the quality gate fails because of it.

| Service | Planted issue | Expected rule | Caught by SonarQube | Caught by Strix |
| --- | --- | --- | --- | --- |
| user-service | Hardcoded `JWT_SECRET` | S6418 / S2068 | No | |
| user-service | MD5 password hash | S4790 | Yes, S4790 (Security, High), line 24 | |
| user-service | `/me` decodes JWT without verifying the signature | S5659 | No | |
| contact-service | Search query built with an f-string (SQL injection) | S2077 | No | |
| contact-service | `verify=False` on the call to user-service | S4830 | Yes, S4830 (Security, High), line 29 | |
| contact-service | `GET /contacts/{id}` returns any owner's contact (IDOR) | none (SAST cannot see it) | No (expected) | |

## Baseline (`main`)

2026-11-25, SonarQube 26.10.0.133078 Community Build + branch plugin 26.10.0, scanner 12.5.0.4351, quality gate Sonar way.

| Project | Gate | Coverage | Vulnerabilities | Hotspots | Bugs | Code smells |
| --- | --- | --- | --- | --- | --- | --- |
| sec-gate-poc_user-service | PASSED | 100.0% | 0 | 0 | 0 | 0 |
| sec-gate-poc_contact-service | PASSED | 100.0% | 0 | 0 | 0 | 0 |

Coverage from `reports/coverage.xml` resolved with no path warnings (`relative_files = true`, `<source>src</source>`).
The scanner image's default work dir `/tmp/.scannerwork` is root-owned, so `scripts/sonar-scan.sh` sets
`SCANNER_WORKDIR_PATH=/tmp/scannerwork`; without it every scan fails with "Unable to create root temp directory".

## Pull request analysis (`planted-vulns`)

Run locally as pull request 1 (`planted-vulns` → `main`) with `CHANGE_ID=1 CHANGE_BRANCH=planted-vulns CHANGE_TARGET=main`.
Verify passed on the branch (4 tests per service), so only the security gate stops these changes.

| Project | Gate | Scanner exit | Failed condition | Other conditions |
| --- | --- | --- | --- | --- |
| sec-gate-poc_user-service | FAILED | 3 | `new_violations` = 1 | new coverage 100.0 OK, new duplication 0.0 OK |
| sec-gate-poc_contact-service | FAILED | 3 | `new_violations` = 1 | new duplication 0.0 OK |

Each project reported exactly one issue and no security hotspots. All seven related rules (S6418, S2068, S6437, S5659,
S2077, S4790, S4830) are active in the Sonar way profile, so the three misses are detection gaps on this code,
not profile settings:

- S6418 / S2068 / S6437: `JWT_SECRET = "flowen-poc-jwt-secret-2026"` was not flagged. S6418 needs a high-entropy value
  and S2068 looks for password-like names; a readable secret under a `*_SECRET` name passes both.
- S5659: `jwt.decode(token, options={"verify_signature": False})` was not flagged.
- S2077: an f-string passed to `sqlite3.Connection.execute` was not flagged. Exploiting it needs taint analysis
  (S3649), which is Developer edition only.

The gate fails on any new issue (`new_violations`), so one caught issue per service was enough to block the PR. A
change that only added the three missed patterns would have passed.

## Open questions answered by this run

- Does S2077 fire on `sqlite3.Connection.execute`? No.
- Does S4830 cover `httpx`? Yes (`httpx.get(..., verify=False)`).
- Does the first analysis of `main` pass the gate? It passed, but the baseline had no issues, so this run does not show
  whether a first analysis treats existing issues as new.
- The scanner exits with code 3 when the gate fails (`sonar.qualitygate.wait=true`), which fails a Jenkins `sh` step.

## Jenkins (shared SonarQube)

2026-11-25, job `sec-gate-poc` on https://jenkins.khaojai.it (Multibranch, GitHub source `cuenobi/sec-gate-poc`), scanning
into https://sonarqube.khaojai.it as the user `jenkins`.

| Build | Result | Gates |
| --- | --- | --- |
| `main` #1 | SUCCESS | both PASSED; projects created by the first scan |
| `PR-1` #1, #2 | SUCCESS (false pass) | both PASSED with `WARN Could not find ref 'main'` |
| `PR-1` #3 | FAILURE | both FAILED, Integration stage message `SonarQube quality gate failed: <service>` |

The pull request build checks out only the PR head, so the scanner had no `main` to diff against, found no new code and
passed. `scripts/sonar-scan.sh` now fetches `refs/heads/$CHANGE_TARGET` before a PR scan (commit 169d8eb); the PR picked
it up after `main` was merged into `planted-vulns`, because this job builds the PR head, not the PR merged with its target.

Not working yet:
- Jenkins posts no status to the GitHub PR: the `github-token` credential can read `cuenobi/sec-gate-poc` but not write
  commit statuses, so GitHub cannot block the merge on this result.
- Jenkins' Coverage plugin cannot resolve source files (`Source file 'user_service/main.py' not found`), because
  `coverage.xml` paths are relative to the service directory. Coverage numbers are recorded; source highlighting is not.
