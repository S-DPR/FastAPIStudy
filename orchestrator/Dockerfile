FROM python:3.13

WORKDIR /app

COPY ./orchestrator /app/orchestrator

COPY ./kafka_common /app/kafka_common

RUN pip install -r /app/orchestrator/requirements.txt

RUN pip install -e /app/kafka_common

RUN chmod +x /app/orchestrator/entrypoint.sh

CMD ["/app/orchestrator/entrypoint.sh"]