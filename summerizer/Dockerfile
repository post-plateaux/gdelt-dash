FROM python:3.9-slim

WORKDIR /app

# Copy summerizer.py into the container
COPY summerizer.py .

# Install dependencies
RUN pip install requests kafka-python psycopg2-binary

CMD ["python", "-u", "summerizer.py"]
