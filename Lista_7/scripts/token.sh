TOKEN=$(curl --header "Content-Type: application/json"   --request POST   --data "{\"username\":\"$1\",\"password\":\"$2\"}"   https://www.example.org/api/login --cacert ../certs/ca.cer --key ../certs/client.key --cert ../certs/client.cer | jq -r '.access_token')
echo $TOKEN
