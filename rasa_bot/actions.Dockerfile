FROM rasa/rasa-sdk:3.6.0

USER root

WORKDIR /app

COPY actions/requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

USER 1001