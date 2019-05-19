#!/bin/bash
#
#
#   color
#
RED='\033[0;31m'
NC='\033[0m' # No Color
#
#
#
if [ -z "$1" ]
  then
    printf  "${RED}Service address must be provided${NC} \n"
    exit 1
fi
echo "The second script - checking the status of everything"
echo "THE SERVICE ADDRESS IS $1"
ip=$1
# get the token
sudo apt-get install jq -y
authen_json()
{
cat <<EOF
{
    "auth": {
        "identity": {
            "methods": [
                "password"
            ],
            "password": {
                "user": {
                    "name": "admin",
                    "domain": {
                        "id": "default"
                    },
                    "password": "secret"
                }
            }
        },
        "scope": {
            "project": {
                "name": "admin",
                "domain": {
                    "id": "default"
                }
            }
        }
    }
}
EOF
}
#
# get the authen token
echo "$(authen_json)"
echo $ip
# get the token
TOKEN=$(curl -i  -H "Content-Type: application/json" -d "$(authen_json)" http://$ip/identity/v3/auth/tokens | grep -Fi X-Subject-Token)
TOKEN=${TOKEN[@]/#X-Subject-Token:/ }
TOKEN=${TOKEN//$'\015'}
echo "=========finish getting the token=========="
echo $TOKEN
echo "========================"
#
# status of the networks
#curl  -X GET http://$ip:9696/v2.0/networks.json  -H "Content-Type: application/json" -H "X-Auth-Token:$TOKEN" >networks_status.json
#curl -v -X GET "http://$ip:9696/v2.0/networks.json?fields=id&fileds=name&fileds=status" -H "Content-Type: application/json" -H "X-Auth-Token:$TOKEN" >t.json
curl -v -X GET "http://$ip:9696/v2.0/networks?name=RED&fields=id&fields=name&fields=status" -H "Content-Type: application/json" -H "X-Auth-Token:$TOKEN" >network_red.json
curl -v -X GET "http://$ip:9696/v2.0/networks?name=BLUE&fields=id&fields=name&fields=status" -H "Content-Type: application/json" -H "X-Auth-Token:$TOKEN" >network_blue.json
curl -v -X GET "http://$ip:9696/v2.0/networks?name=PUBLIC&fields=id&fields=name&fields=status&provider:network_type=vxlan" -H "Content-Type: application/json" -H "X-Auth-Token:$TOKEN" >network_public.json
#
#
#status of the virtual machines
echo "==================checking status of the VM1"
curl -X GET http://$ip/compute/v2.1/servers/detail?name=VM1 -H "Content-Type: application/json" -H "X-Auth-Token:$TOKEN" >vm1_status.json
status=$(cat vm1_status.json | jq .servers[0].status)
echo "VM1 is $status"
#
#
echo "==================checking status of the VM2"
curl -X GET http://$ip/compute/v2.1/servers/detail?name=VM2 -H "Content-Type: application/json" -H "X-Auth-Token:$TOKEN" >vm2_status.json
status=$(cat vm2_status.json | jq .servers[0].status)
echo "VM2 is $status"
#
#
#
echo "==================checking status of the VM3"
curl -X GET http://$ip/compute/v2.1/servers/detail?name=VM3 -H "Content-Type: application/json" -H "X-Auth-Token:$TOKEN" >vm3_status.json
status=$(cat vm3_status.json | jq .servers[0].status)
echo "VM3 is $status"
#
# status of the router interfaces
curl -X GET   http://$ip:9696/v2.0/ports/   -H 'Content-Type: application/json'   -H "X-AUTH-TOKEN:$TOKEN" >ports.json
# get the ide of each port by name
blue_port_id=$(cat ports.json | jq '.ports[] | select (.name=="port_blue") | .id')
blue_port_id=$(echo $blue_port_id|sed s/\"//g)
echo $blue_port_id
#
red_port_id=$(cat ports.json | jq '.ports[] | select (.name=="port_red")| .id')
red_port_id=$(echo $red_port_id|sed s/\"//g)
echo $red_port_id
#
public_port_id=$(cat ports.json | jq '.ports[] | select (.name=="port_public")| .id')
public_port_id=$(echo $public_port_id|sed s/\"//g)
echo $public_port_id
#
#

echo "=========================port blue============"
curl -X GET   http://$ip:9696/v2.0/ports/$blue_port_id   -H 'Content-Type: application/json'   -H "X-AUTH-TOKEN:$TOKEN" >port_blue.json
cat port_blue.json | jq
echo "=========================port red============"
curl -X GET   http://$ip:9696/v2.0/ports/$red_port_id   -H 'Content-Type: application/json'   -H "X-AUTH-TOKEN:$TOKEN" >port_red.json
cat port_red.json | jq
curl -X GET   http://$ip:9696/v2.0/ports/$public_port_id   -H 'Content-Type: application/json'   -H "X-AUTH-TOKEN:$TOKEN" >port_public.json
echo "=========================port public============"
cat port_public.json | jq
#curl -v -X GET http://$ip:9696/v2.0/ports -H "Content-Type: application/json" -H "X-Auth-Token:$TOKEN" >interface_status.json
#cat interface_status.json | jq

#everything is in json
printf "${RED}======FINISH===========${NC}\n"