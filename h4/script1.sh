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
echo "THE SERVICE ADDRESS IS $1"
ip=$1
sudo apt-get install jq -y
#sleep 5
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
#curl -i -v -H "Content-Type: application/json" -d "$(authen_json)" http://$ip/identity/v3/auth/tokens > token.json
# get the token
#TOKEN=$(cat token.json | grep -Fi X-Subject-Token)
TOKEN=$(curl -i -v -H "Content-Type: application/json" -d "$(authen_json)" http://$ip/identity/v3/auth/tokens | grep -Fi X-Subject-Token)
#TOKEN=${TOKEN[@]/#X-Subject-Token/X-Auth-Token} # replace
TOKEN=${TOKEN[@]/#X-Subject-Token:/ } # replace
TOKEN=${TOKEN//$'\015'}
echo "=========finish creating token=========="
echo $TOKEN
echo "========================"
create_network_json()
{
    cat<<EOF
    {
        "network": 
        {
            "port_security_enabled": true,
            "name": "$name",
            "admin_state_up": true,
            "mtu": 1450,
            "shared": false,
            "router:external": false,
            "provider:network_type": "vxlan"
        }
    }   
EOF
}
echo "==================create network BLUE================"
#
#
#
name="BLUE"
echo "$(create_network_json)"
#curl -v POST http://$ip:9696/v2.0/networks -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(create_network_json)"  >blue.json
# IDp=$(cat pub.json | jq .network.id)
# IDp=$( echo $IDp|sed s/\"//g)
IDb=$(curl -v POST http://$ip:9696/v2.0/networks -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(create_network_json)" | jq .network.id | sed s/\"//g)
#
#
#
echo "==================create network RED================"
name="RED"
echo "$(create_network_json)"
# curl -v POST http://$ip:9696/v2.0/networks -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(create_network_json)"  >red.json
IDr=$(curl -v POST http://$ip:9696/v2.0/networks -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(create_network_json)" | jq .network.id | sed s/\"//g)
#
#
#
echo "==================create network PUB================"
name="PUBLIC"
echo "$(create_network_json)"
IDp=$(curl -v POST http://$ip:9696/v2.0/networks -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(create_network_json)" | jq .network.id | sed s/\"//g)
# curl -v POST http://$ip:9696/v2.0/networks -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(create_network_json)"  >pub.json
# IDb=$(cat blue.json | jq .network.id)
# IDb=$( echo $IDb|sed s/\"//g)
echo $IDb
# IDr=$(cat red.json | jq .network.id)
# IDr=$( echo $IDr|sed s/\"//g)
echo $IDr
echo $IDp
echo "==================================create subnet"
subnet_json()
{
    cat<<EOF
    {
        "subnet": 
        {
            "name": "$subnet_name",
            "network_id": "$network_id",
            "ip_version": 4,
            "cidr": "$ip_range"
        }
    }   
EOF
}
#
#   create the subnet
#
echo "==================================create subnet BLUE"
subnet_name="blue-subnet1"
network_id=$IDb
ip_range="10.0.0.0/24"
echo "$(subnet_json)"
#curl -v -X POST http://$ip:9696/v2.0/subnets -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(subnet_json)"  >subnet_blue.json
sn_blue=$(curl -v -X POST http://$ip:9696/v2.0/subnets -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(subnet_json)" | jq .subnet.id)
echo "==================================create subnet RED"
subnet_name="red-subnet1"
network_id=$IDr
ip_range="192.168.1.0/24"
echo "$(subnet_json)"
# curl -v -X POST http://$ip:9696/v2.0/subnets -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(subnet_json)"  >subnet_red.json
sn_red=$(curl -v -X POST http://$ip:9696/v2.0/subnets -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(subnet_json)" | jq .subnet.id)
echo "==================================create subnet PUBLIC"
subnet_name="pub-subnet1"
network_id=$IDp
ip_range="172.24.4.0/24"
echo "$(subnet_json)"
#curl -v -X POST http://$ip:9696/v2.0/subnets -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(subnet_json)"  >subnet_pub.json
sn_pub=$(curl -v -X POST http://$ip:9696/v2.0/subnets -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(subnet_json)" | jq .subnet.id)
##
# extract the subnet id
#
#sn_blue=$(cat subnet_blue.json | jq .subnet.id)
#sn_red=$(cat subnet_red.json | jq .subnet.id)
#sn_pub=$(cat subnet_pub.json | jq .subnet.id)
echo $sn_blue
echo $sn_red
echo $sn_pub
echo "===========================finishing creating subnet"
#
#   create the router
#
echo "===========================adding router to the network"
curl -v -X POST http://$ip:9696/v2.0/routers -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d '{ "router": {   "name": "router1",   "admin_state_up": true  }}' >router.json
router=$(cat router.json | jq .router.id| sed s/\"//g)
echo "router is $router"
#
#   adding the interface to each subnet
#
#
echo "===========================adding interface to subnet"
interface_json()
{
    cat<<EOF
    {
    "subnet_id": $subnet
    }
EOF
}
subnet=$sn_blue
echo "$(interface_json)"
curl -v -X PUT http://$ip:9696/v2.0/routers/$router/add_router_interface -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(interface_json)"
subnet=$sn_red
echo "$(interface_json)"
curl -v -X PUT http://$ip:9696/v2.0/routers/$router/add_router_interface -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(interface_json)"
subnet=$sn_pub
echo "$(interface_json)"
curl -v -X PUT http://$ip:9696/v2.0/routers/$router/add_router_interface -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(interface_json)"
#
#   find the imageref and flavorref
#
echo "==================================get the image information============="
#curl -v -X PUT http://$ip/compute/v2.1/images -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" 
###
### work here
###
flavor=$(curl -v -X GET http://$ip/compute/v2.1/flavors -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" | jq '.flavors[] | select (.name=="m1.nano")| .id')
image_id=$(curl -v -X GET http://$ip/compute/v2.1/images -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(interface_json)" | jq .images[0].id)
#
#   end flavor
#
#
#flavor="42"
flavor=$( echo $flavor|sed s/\"//g)
#image_id="aaab4dfd-8d9c-409e-a821-a0137e49e869"
image_id=$( echo $image_id|sed s/\"//g)
#
# create port for each subnet
#
echo "====================================create port for each subnet"
port_json()
{
    cat<<EOF
    {
        "port": 
        {
            "admin_state_up": true,
            "name": "$port_name",
            "network_id": "$network_id",
            "port_security_enabled": true
        }
    }
EOF
}
network_id=$IDb
port_name="port_blue"
curl -v -X POST http://$ip:9696/v2.0/ports -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(port_json)"
network_id=$IDr
port_name="port_red"
curl -v -X POST http://$ip:9696/v2.0/ports -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(port_json)"
network_id=$IDp
port_name="port_public"
curl -v -X POST http://$ip:9696/v2.0/ports -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(port_json)"
#
#
# create new security group, the name is myrule
#
#
sec_group_name="myrule$RANDOM"
secury_grp_json()
{
    cat<<EOF
    {
        "security_group": 
        {
            "name": "$sec_group_name",
            "description": "i do what i want here"
        }
    }
EOF
}
echo "===================================create security group"
# curl -v -X POST http://$ip:9696/v2.0/security-groups -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(secury_grp_json)" >sec.json
# sec_id=$(cat sec.json | jq .security_group.id)
# sec_id=$( echo $sec_id|sed s/\"//g)
sec_id=$( curl -v -X POST http://$ip:9696/v2.0/security-groups -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(secury_grp_json)" | jq .security_group.id | sed s/\"//g)
echo $sec_id
#
#   adding rules
#
echo "===================================adding rules to security group"
ingress()
{
    cat<<EOF
    {
    "security_group_rule": 
        {
            "direction": "ingress",
            "ethertype": "IPv4",
            "protocol": "icmp",
            "security_group_id": "$sec_id"
        }
    }
EOF
}
echo "$(ingress)"
curl -v -X POST http://$ip:9696/v2.0/security-group-rules -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(ingress)"
egress()
{
    cat<<EOF
    {
        "security_group_rule": 
        {
            "direction": "egress",
            "ethertype": "IPv4",
            "protocol": "icmp",
            "security_group_id": "$sec_id"
        }
    }
EOF
}
curl -v -X POST http://$ip:9696/v2.0/security-group-rules -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(egress)"
#
#   create servers
#
#
echo "=============================================create servers"
json_servers()
{
    cat<<EOF
    {
    "server": 
        {
            "name": "$server_name",
            "imageRef": "$image_id",
            "flavorRef": "$flavor",
            "availability_zone": "nova",
            "OS-DCF:diskConfig": "AUTO",
            "security_groups": [
                {
                    "name": "$sec_group_name"
                }
            ],
            "networks": [
                {
                    "uuid": "$network_id"
                }
            ]
        }
    }
EOF
}
# for RED
server_name="VM2"
network_id=$IDr
echo "$(json_servers)"
curl -v -X POST http://$ip/compute/v2.1/servers -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(json_servers)"
#
# for blue
server_name="VM1"
network_id=$IDb
curl -v -X POST http://$ip/compute/v2.1/servers -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(json_servers)"
# for PUBLIC
server_name="VM3"
network_id=$IDp
curl -v -X POST http://$ip/compute/v2.1/servers -H 'Content-Type: application/json' -H "X-Auth-Token:$TOKEN" -d "$(json_servers)"
echo "==========================FINISH+======================================"
printf "${RED}======FINISH===========${NC}\n"