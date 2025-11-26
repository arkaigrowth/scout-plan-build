# Start the application

## Variables

PORT: 5173

## Workflow

Check to see if a process is already running on port PORT.

If it is just open it in the browser with `open http://localhost:PORT`.

If there is no process running on port PORT, run these commands:

Run `nohup sh ./scripts/start.sh > /dev/null 2>&1 &`
Run `sleep 3`
Run `open http://localhost:PORT`

Let the user know that the application is running and the browser is open.