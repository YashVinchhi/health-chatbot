FROM python:3.9-slim

WORKDIR /app

# Copy frontend files
COPY . /app

# Install Python dependencies (for the simple HTTP server)
# No additional packages needed for basic HTTP server

# Expose port
EXPOSE 3001

# Start the server
CMD ["python", "server.py"]
