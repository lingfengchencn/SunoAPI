import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from configs import config
import pika


# flask_rabbitmq.py
import pika

class RabbitMQ:
    def __init__(self):
        self.public_connection = None
        self.public_music_connection = None
        self.consume_connection = None
        self.public_channel = None
        self.public_music_channel = None
        self.consume_channel = None

    def get_public_channel(self):
        if not self.public_connection or self.public_connection.is_closed:
            self.public_connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=config.RABBITMQ_PUBLIC_HOST,
                port=config.RABBITMQ_PUBLIC_PORT,
                credentials=pika.PlainCredentials(config.RABBITMQ_PUBLIC_USERNAME, config.RABBITMQ_PUBLIC_PASSWORD)
            ))
        if not self.public_channel or self.public_channel.is_closed:
            self.public_channel = self.public_connection.channel()
            self.public_channel.queue_declare(queue=config.RABBITMQ_PUBLIC_QUEUE, durable=config.RABBITMQ_PUBLIC_DURABLE)  # 设置durable为True
        return self.public_channel
    
    def get_public_music_channel(self):
        if not self.public_music_connection or self.public_music_connection.is_closed:
            self.public_music_connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=config.RABBITMQ_PUBLIC_MUSIC_HOST,
                port=config.RABBITMQ_PUBLIC_MUSIC_PORT,
                credentials=pika.PlainCredentials(config.RABBITMQ_PUBLIC_MUSIC_USERNAME, config.RABBITMQ_PUBLIC_MUSIC_PASSWORD)
            ))
        if not self.public_music_channel or self.public_music_channel.is_closed:
            self.public_music_channel = self.public_music_connection.channel()
            self.public_music_channel.queue_declare(queue=config.RABBITMQ_PUBLIC_MUSIC_QUEUE, durable=config.RABBITMQ_PUBLIC_MUSIC_DURABLE)  # 设置durable为True
        return self.public_music_channel
    def get_consume_channel(self):
        if not self.consume_connection or self.consume_connection.is_closed:
            self.consume_connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=config.RABBITMQ_CONSUME_HOST,
                port=config.RABBITMQ_CONSUME_PORT,
                credentials=pika.PlainCredentials(config.RABBITMQ_CONSUME_USERNAME, config.RABBITMQ_CONSUME_PASSWORD)
            ))
        if not self.consume_channel or self.consume_channel.is_closed:
            self.consume_channel = self.consume_connection.channel()
            self.consume_channel.queue_declare(queue=config.RABBITMQ_CONSUME_QUEUE, durable=config.RABBITMQ_CONSUME_DURABLE)  # 设置durable为True
        return self.consume_channel

    def close(self):
        if self.consume_connection and not self.consume_connection.is_closed:
            self.consume_connection.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    from services.mq_service import MQSerivce
    service = MQSerivce()
    
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(loop.run_in_executor(None, service.consume))
    yield
    loop.stop()
    # app.router.lifespan_context = lifespan

rabbitmq = RabbitMQ()
