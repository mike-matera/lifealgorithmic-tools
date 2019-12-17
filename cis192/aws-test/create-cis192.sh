#! /bin/bash

# This is for gcloud

INTERNAL_VPC_NAME=cis192-internal-vpc
INTERNAL_SUBNET_NAME=internal
INTERNAL_RANGE=10.192.0.0/24

echo "Creating VPCs"
gcloud compute networks create ${INTERNAL_VPC_NAME} --subnet-mode custom
gcloud compute networks create cis191-external --subnet-mode custom

echo "Creating Subnets"
gcloud compute networks subnets create ${INTERNAL_SUBNET_NAME} --network=${INTERNAL_VPC_NAME} --range=${INTERNAL_RANGE}
gcloud compute networks subnets create external-subnet --network=cis191-external --range=10.192.1.0/24

echo "Allowing SSH into the external network."
gcloud compute firewall-rules create ssh-to-external --description="Allow SSH to the external network" --direction=INGRESS --priority=1000 --network=cis191-external --action=ALLOW --rules=tcp:22 --source-ranges=0.0.0.0/0

echo "Allowing SSH to internal VMs."
gcloud compute firewall-rules create ssh-to-internal --description="Allow SSH to the internal network" --direction=INGRESS --priority=1000 --network=${INTERNAL_VPC_NAME} --action=ALLOW --rules=tcp:22 --source-ranges=0.0.0.0/0

echo "Allowing internal VMs to communicate."
gcloud compute firewall-rules create cis192-internal-allow --description="Allow internal VMs to communicate." --direction=INGRESS --priority=1000 --network=${INTERNAL_VPC_NAME} --action=ALLOW --rules=all --source-ranges=${INTERNAL_RANGE}

echo "Creating Router"
gcloud compute instances create router --zone=us-west1-b --machine-type=f1-micro --image=ubuntu-minimal-1804-bionic-v20190628 --image-project=ubuntu-os-cloud --boot-disk-size=10GB --boot-disk-type=pd-standard --boot-disk-device-name=instance-1 --network-interface=network=cis191-external,subnet=external-subnet --network-interface=network=${INTERNAL_VPC_NAME},subnet=${INTERNAL_SUBNET_NAME}

echo "Creating App Server"
gcloud compute instances create app-server --zone=us-west1-b --machine-type=f1-micro --image=ubuntu-minimal-1804-bionic-v20190628 --image-project=ubuntu-os-cloud --boot-disk-size=10GB --boot-disk-type=pd-standard --network-interface=network=cis191-internal,subnet=internal-subnet,noaddress,private-network-ip=10.192.0.100

