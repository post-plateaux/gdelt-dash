# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install PostgreSQL driver
RUN pip install psycopg2-binary

# Run the placeholder Python script
CMD ["python", "queries.py"]
