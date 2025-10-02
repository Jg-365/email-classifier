# Start script for Render.com
#!/bin/bash

echo "Starting static file server..."
echo "Serving from ./dist directory"

# Install a simple static file server
npm install -g serve

# Serve the built React app
serve -s dist -l 10000