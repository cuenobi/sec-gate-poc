# Findings

Filled in from real runs. "Caught" means the issue appears in the SonarQube analysis of the `planted-vulns` pull request
and the quality gate fails because of it.

| Service | Planted issue | Expected rule | Caught by SonarQube | Caught by Strix |
| --- | --- | --- | --- | --- |
| user-service | Hardcoded `JWT_SECRET` | S6418 / S2068 | | |
| user-service | MD5 password hash | S4790 | | |
| user-service | `/me` decodes JWT without verifying the signature | S5659 | | |
| contact-service | Search query built with an f-string (SQL injection) | S2077 | | |
| contact-service | `verify=False` on the call to user-service | S4830 | | |
| contact-service | `GET /contacts/{id}` returns any owner's contact (IDOR) | none (SAST cannot see it) | | |

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

## Open questions answered by this run
