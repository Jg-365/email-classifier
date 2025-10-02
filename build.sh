# Build script for Render.com
#!/bin/bash

echo "Starting build process..."
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the React app
echo "Building React application..."
npm run build

echo "Build completed successfully!"