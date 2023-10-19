#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Load the config file into variables
eval "$(jq -r 'to_entries[] | "export \(.key)=\(.value | @sh)"' /root/join_swarm.json)"

if [[ $(docker info | grep Swarm | awk '{print $2}') == "inactive" ]]; then
    docker swarm join --token $SWARM_TOKEN [$SWITCH_IP_ADDRESS]:$SWITCH_PORT
else
    echo "This node is already part of a swarm"
    docker info -f json | jq .Swarm
fi
