#!/bin/bash
if [ -f "../tac-5/.env" ]; then
    cp ../tac-5/.env .env && echo "Copied ../tac-5/.env -> .env"
else echo "Warning: ../tac-5/.env missing"; fi
if [ -f "../tac-5/app/server/.env" ]; then
    mkdir -p app/server
    cp ../tac-5/app/server/.env app/server/.env && echo "Copied server .env"
else echo "Error: ../tac-5/app/server/.env missing"; exit 1; fi
