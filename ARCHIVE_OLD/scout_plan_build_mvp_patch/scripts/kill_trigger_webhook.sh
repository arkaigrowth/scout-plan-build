#!/bin/bash
echo "Stopping trigger_webhook.py server..."
if pgrep -f "trigger_webhook.py" > /dev/null; then pkill -f "trigger_webhook.py"; echo "✓ Webhook server stopped"; else echo "⚠ No webhook server process found"; fi
if lsof -i :8001 > /dev/null 2>&1; then echo "Killing port 8001"; lsof -ti :8001 | xargs kill -9 2>/dev/null; fi
