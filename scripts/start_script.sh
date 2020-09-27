#!/bin/bash

## Kill all pm2 processes
cd /var/app/
sudo pkill -f pm2

## Star pm2 service

export MONGODB_SECRET=$(aws ssm get-parameters --region us-east-1 --names /elo-discord-bot/MONGODB_SECRET --query Parameters[0].Value) 
export MONGODB_SECRET=$(echo "$MONGODB_SECRET"|tr -d '"')  

export DISCORD_TOKEN=$(aws ssm get-parameters --region us-east-1 --names /elo-discord-bot/DISCORD_TOKEN --query Parameters[0].Value) 
export DISCORD_TOKEN=$(echo "$DISCORD_TOKEN"|tr -d '"')  

MONGODB_SECRET=$MONGODB_SECRET \
DISCORD_TOKEN=$DISCORD_TOKEN \
pm2 start botApp.py --interpreter=python3 > log.txt
