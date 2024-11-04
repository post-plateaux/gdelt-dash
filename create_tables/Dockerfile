# Use the official Python image.
FROM python:3.11-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file and install dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script files into the container.
COPY . .

# Command to run when the container starts.
CMD ["python", "create_tables.py"]
