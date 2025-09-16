"""Queues router."""

from faststream.confluent import KafkaBroker
from faststream.confluent.fastapi import KafkaRouter
from haolib.middlewares.faststream_opentelemetry import get_kafka_telemetry_middleware

mq_router = KafkaRouter(middlewares=(get_kafka_telemetry_middleware(),))


def get_broker() -> KafkaBroker:
    """Broker."""
    return mq_router.broker
