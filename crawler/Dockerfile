FROM python:3.10-slim

# Install necessary system dependencies for Chromium/Playwright and Node.js
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libgbm1 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxi6 \
    libxrandr2 \
    libxtst6 \
    libpangocairo-1.0-0 \
    libxss1 \
    nodejs \
    npm \
    git \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definitions first (to leverage layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install additional browser dependencies with Playwright
RUN playwright install-deps
RUN playwright install chromium
RUN npm install -g @postlight/parser

# Then copy the rest of the project code
COPY . /app

# Copy and prepare start.sh
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Use start.sh as the container's entrypoint
CMD ["/app/start.sh"]
