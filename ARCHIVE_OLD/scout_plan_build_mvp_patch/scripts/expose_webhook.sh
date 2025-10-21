#!/bin/bash
# Uses CLOUDFLARED_TUNNEL_TOKEN from .env
[ -f .env ] && export CLOUDFLARED_TUNNEL_TOKEN=$(grep CLOUDFLARED_TUNNEL_TOKEN .env | cut -d '=' -f2)
cloudflared tunnel run --token $CLOUDFLARED_TUNNEL_TOKEN
