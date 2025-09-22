FROM rasa/rasa-sdk:3.6.0

USER root

WORKDIR /app

# Copy requirements first for better layer caching
COPY actions/requirements.txt ./
RUN pip install -r requirements.txt

# Copy actions directory contents but preserve the entrypoint.sh
COPY actions/actions.py ./actions.py

USER 1001