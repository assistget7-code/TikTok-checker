#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Install Playwright and Chromium
playwright install chromium

# Set correct permissions
chmod -R 777 /opt/render/.cache/ms-playwright

echo "✅ Build complete!"
