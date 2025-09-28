FROM rasa/rasa:3.6.0-full

# Install system dependencies
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install SQLAlchemy with version constraint
RUN pip install --no-cache-dir "sqlalchemy<2.0"

# Set working directory and environment variables
WORKDIR /app
ENV PORT=5775
ENV PYTHONPATH=/app

# Copy project files
COPY . .

# Switch back to non-root user for security
USER 1001

# Expose the port
EXPOSE ${PORT}

# Run RASA
CMD ["run", "--enable-api", "--cors", "*", "--port", "5775"]
