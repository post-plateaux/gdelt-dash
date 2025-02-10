FROM python:3.9-slim

WORKDIR /app

# Copy all files from the summerizer directory into the container
COPY . .

# Install dependencies
RUN pip install openai requests kafka-python psycopg2-binary

CMD ["python", "-u", "summerizer.py"]
