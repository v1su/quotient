name: Generate Quote Image

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      # Checkout the code
      - name: Checkout code
        uses: actions/checkout@v2
        
      # Set up Python environment
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'

      # Install dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pillow python-telegram-bot

      # Add font to the system (optional step if you want to use system-wide fonts)
      - name: Add font file
        run: |
          mkdir -p ~/.fonts
          cp assets/fonts/font.otf ~/.fonts/font.otf
          fc-cache -f -v  # Refresh the font cache

      # Run the post.py script to generate the quote image and post it to Telegram
      - name: Run post script to generate and send quote image
        run: |
          python post.py  # Make sure 'post.py' is the name of the script
