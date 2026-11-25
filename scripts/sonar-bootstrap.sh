#!/bin/sh
# Starts local SonarQube and writes .env with generated passwords and an analysis token.
set -eu
cd "$(dirname "$0")/.."
url=http://localhost:9000

if [ ! -f .env ]; then
    umask 077
    printf 'SONAR_DB_PASSWORD=%s\nSONAR_ADMIN_PASSWORD=%sA!\n' \
        "$(openssl rand -hex 16)" "$(openssl rand -hex 16)" > .env
fi
. ./.env

docker compose -f compose.sonarqube.yml up -d
until curl -fs "$url/api/system/status" | grep -q '"status":"UP"'; do sleep 5; done

if curl -fs -u admin:admin "$url/api/authentication/validate" | grep -q '"valid":true'; then
    curl -fs -u admin:admin -X POST "$url/api/users/change_password" \
        -d login=admin -d previousPassword=admin --data-urlencode "password=$SONAR_ADMIN_PASSWORD"
fi
auth="admin:$SONAR_ADMIN_PASSWORD"

for svc in user-service contact-service; do
    key=sec-gate-poc_$svc
    if ! curl -fs -u "$auth" "$url/api/projects/search?projects=$key" | grep -q "\"key\":\"$key\""; then
        curl -fs -u "$auth" -X POST "$url/api/projects/create" \
            -d project="$key" -d name="sec-gate-poc $svc" -d mainBranch=main > /dev/null
    fi
    curl -fs -u "$auth" -X POST "$url/api/new_code_periods/set" \
        -d project="$key" -d type=REFERENCE_BRANCH -d value=main
done

if ! grep -q '^SONAR_TOKEN=' .env; then
    token=$(curl -fs -u "$auth" -X POST "$url/api/user_tokens/generate" \
        -d name=local-scan -d type=GLOBAL_ANALYSIS_TOKEN | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')
    printf 'SONAR_TOKEN=%s\n' "$token" >> .env
fi
echo "SonarQube ready on $url (admin password in .env)"
