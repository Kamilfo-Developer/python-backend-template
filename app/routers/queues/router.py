"""Queues router."""

from faststream.confluent import KafkaBroker
from faststream.confluent.fastapi import KafkaRouter

mq_router = KafkaRouter()


def get_broker() -> KafkaBroker:
    """Broker."""
    return mq_router.broker
