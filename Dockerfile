# Use Python 3.10 image as base
FROM python:3.10

# Set working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose necessary ports
EXPOSE 443
EXPOSE 8000

# Run the Python script
CMD ["python", "mnMFA.py"]
