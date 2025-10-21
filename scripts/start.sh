#!/bin/bash

# Port configuration
SERVER_PORT=8000
CLIENT_PORT=5173

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Natural Language SQL Interface...${NC}"

# Function to kill process on port
kill_port() {
    local port=$1
    local process_name=$2
    
    # Find process using the port
    local pid=$(lsof -ti:$port 2>/dev/null)
    
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Found $process_name running on port $port (PID: $pid). Killing it...${NC}"
        kill -9 $pid 2>/dev/null
        sleep 1
        echo -e "${GREEN}$process_name on port $port has been terminated.${NC}"
    fi
}

# Kill any existing processes on our ports
kill_port $SERVER_PORT "backend server"
kill_port $CLIENT_PORT "frontend server"

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# Check if .env exists in server directory
if [ ! -f "$PROJECT_ROOT/app/server/.env" ]; then
    echo -e "${RED}Warning: No .env file found in app/server/.${NC}"
    echo "Please:"
    echo "  1. cd app/server"
    echo "  2. cp .env.sample .env"
    echo "  3. Edit .env and add your API keys"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    
    # Kill all child processes
    jobs -p | xargs -r kill 2>/dev/null
    
    # Wait for processes to terminate
    wait
    
    echo -e "${GREEN}Services stopped successfully.${NC}"
    exit 0
}

# Trap EXIT, INT, and TERM signals
trap cleanup EXIT INT TERM

# Start backend
echo -e "${GREEN}Starting backend server...${NC}"
cd "$PROJECT_ROOT/app/server"
uv run python server.py &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Backend failed to start!${NC}"
    exit 1
fi

# Start frontend
echo -e "${GREEN}Starting frontend server...${NC}"
cd "$PROJECT_ROOT/app/client"
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}Frontend failed to start!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Services started successfully!${NC}"
echo -e "${BLUE}Frontend: http://localhost:$CLIENT_PORT${NC}"
echo -e "${BLUE}Backend:  http://localhost:$SERVER_PORT${NC}"
echo -e "${BLUE}API Docs: http://localhost:$SERVER_PORT/docs${NC}"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for user to press Ctrl+C
wait