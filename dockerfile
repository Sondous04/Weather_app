# Base image: small official Python image
FROM python:3.11-slim

# Folder inside the container where the app will live
WORKDIR /app

# Install dependencies first (Docker caches this layer if requirements.txt doesn't change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Run as a normal user instead of root (safer)
RUN useradd --create-home appuser
USER appuser

# The app listens on port 8000 inside the container
EXPOSE 8000

# Start the app with gunicorn (a production server, unlike "python app.py")
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]