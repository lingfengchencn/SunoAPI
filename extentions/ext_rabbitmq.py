import asyncio
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
                credentials=pika.PlainCredentials(config.RABBITMQ_PUBLIC_USERNAME, config.RABBITMQ_PUBLIC_PASSWORD),
                connection_attempts=config.RABBITMQ_PUBLIC_CONNECTION_ATTEMPS, # 尝试连接次数
                retry_delay=config.RABBITMQ_PUBLIC_RETRY_DELAY,          # 每次重试前等待（单位：秒）
                socket_timeout=config.RABBITMQ_PUBLIC_SOCKET_TIMEOUT,      # 远程过程调用超时（单位：秒）
                blocked_connection_timeout=config.RABBITMQ_PUBLIC_BLOCKED_CONNECTION_TIMEOUT, #连接阻塞超时时间（单位：秒）
                channel_max=config.RABBITMQ_PUBLIC_CHANNEL_MAX,         # 最大通道数
                heartbeat=config.RABBITMQ_PUBLIC_HEARTBEAT            # 心跳超时

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
                credentials=pika.PlainCredentials(config.RABBITMQ_PUBLIC_MUSIC_USERNAME, config.RABBITMQ_PUBLIC_MUSIC_PASSWORD),
                connection_attempts=config.RABBITMQ_PUBLIC_MUSIC_CONNECTION_ATTEMPS, # 尝试连接次数
                retry_delay=config.RABBITMQ_PUBLIC_MUSIC_RETRY_DELAY,          # 每次重试前等待（单位：秒）
                socket_timeout=config.RABBITMQ_PUBLIC_MUSIC_SOCKET_TIMEOUT,      # 远程过程调用超时（单位：秒）
                blocked_connection_timeout=config.RABBITMQ_PUBLIC_MUSIC_BLOCKED_CONNECTION_TIMEOUT, #连接阻塞超时时间（单位：秒）
                channel_max=config.RABBITMQ_PUBLIC_MUSIC_CHANNEL_MAX,         # 最大通道数
                heartbeat=config.RABBITMQ_PUBLIC_MUSIC_HEARTBEAT            # 心跳超时
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
                credentials=pika.PlainCredentials(config.RABBITMQ_CONSUME_USERNAME, config.RABBITMQ_CONSUME_PASSWORD),
                connection_attempts=config.RABBITMQ_CONSUME_CONNECTION_ATTEMPS, # 尝试连接次数
                retry_delay=config.RABBITMQ_CONSUME_RETRY_DELAY,          # 每次重试前等待（单位：秒）
                socket_timeout=config.RABBITMQ_CONSUME_SOCKET_TIMEOUT,      # 远程过程调用超时（单位：秒）
                blocked_connection_timeout=config.RABBITMQ_CONSUME_BLOCKED_CONNECTION_TIMEOUT, #连接阻塞超时时间（单位：秒）
                channel_max=config.RABBITMQ_CONSUME_CHANNEL_MAX,         # 最大通道数
                heartbeat=config.RABBITMQ_CONSUME_HEARTBEAT            # 心跳超时
            ))
        if not self.consume_channel or self.consume_channel.is_closed:
            self.consume_channel = self.consume_connection.channel()
            self.consume_channel.queue_declare(queue=config.RABBITMQ_CONSUME_QUEUE, durable=config.RABBITMQ_CONSUME_DURABLE)  # 设置durable为True
        return self.consume_channel

    def close(self):
        if self.consume_connection and not self.consume_connection.is_closed:
            self.consume_connection.close()
        if self.public_connection and not self.public_connection.is_closed:
            self.public_connection.close()
        if self.public_music_connection and not self.public_music_connection.is_closed:
            self.public_music_connection.close()

# @asynccontextmanager
# def lifespan(app):
#     # On startup
#     from services.mq_service import MQSerivce
#     loop = asyncio.get_event_loop()
#     asyncio.ensure_future(loop.run_in_executor(None, MQSerivce.consume))
#     yield
#     loop.stop()
#     # app.router.lifespan_context = lifespan


def init_mq(app):
    from services.mq_service import MQSerivce
    # 在此处启动你的 MQService
    loop = asyncio.get_event_loop()
    service = MQSerivce()
    # 将任务放入事件循环
    asyncio.ensure_future(loop.run_in_executor(None, service.consume))


rabbitmq = RabbitMQ()
