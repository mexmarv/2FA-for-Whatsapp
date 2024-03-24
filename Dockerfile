# Use Python 3.8 image as base
FROM python:3.8

# Set working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn waitress flask requests

# Expose necessary ports
EXPOSE 80
EXPOSE 8000

# Run the Python script
CMD ["python", "mnMFA.py"]
