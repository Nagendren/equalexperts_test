FROM python:3.11-slim

WORKDIR /app

# Install runtime deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY . .

EXPOSE 8080

# Run uvicorn on port 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]