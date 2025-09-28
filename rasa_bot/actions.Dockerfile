FROM rasa/rasa-sdk:3.6.0

WORKDIR /app

COPY actions /app/actions
COPY data /app/data
COPY actions/requirements.txt /app

USER root
RUN python -m pip install --no-cache-dir -r requirements.txt

# Set default port
ENV PORT=5855

EXPOSE ${PORT}

USER 1001
CMD ["start", "--actions", "actions", "--port", "5855"]
