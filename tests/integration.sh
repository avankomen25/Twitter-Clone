set -ex
curl -sfS http://127.0.0.1:8080/ > /dev/null
curl -sfS http://127.0.0.1:8080/login > /dev/null
curl -sfS http://127.0.0.1:8080/logout > /dev/null
curl -sfS http://127.0.0.1:8080/create_message > /dev/null
curl -sfS http://127.0.0.1:8080/create_user > /dev/null