FROM rasa/rasa:3.6.0

WORKDIR /app
COPY . /app

# Pin SQLAlchemy to a 1.x release to avoid SQLAlchemy 2.0 incompatible warnings
# (Rasa currently logs compatibility warnings with SQLAlchemy 2.0)
# Install into the Rasa virtualenv explicitly for reliability
RUN /opt/venv/bin/pip install "sqlalchemy<2.0"

CMD ["run", "--enable-api", "--cors", "*"]