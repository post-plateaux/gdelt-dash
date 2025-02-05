# Use the official Python image.
FROM python:3.11-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file and install dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script files into the container.
COPY . .

# Create flags directory and copy entrypoint script
RUN mkdir -p /flags && chmod 777 /flags
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set entrypoint with unbuffered output
ENTRYPOINT ["python", "-u", "/app/fetch_gdelt_and_upload.py"]
