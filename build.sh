#!/bin/bash
set -e

echo "Building FIX Dictionary UI..."

# Build the UI
cd ui
npm run build
cd ..

# Copy built files to public directory for Vercel static serving
echo "Copying static files to public directory..."
cp api/static/single-spa-entry.js public/
cp api/static/assets/style.css public/ui-styles.css
cp api/static/test-ui.html public/

echo "Build complete! Files ready for Vercel deployment."
