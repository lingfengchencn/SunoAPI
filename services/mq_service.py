import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools
import threading
import time
import json

import pika
from extentions.ext_database import db
from extentions.ext_rabbitmq import rabbitmq
from configs import config

import logging
from models import SunoJobTypeEnum
from services.music_service import MusicService
from suno.entities import ClipStatusEnum
from suno.exceptions import ReachedMaxJobsException, TooManyRequestsException
logger = logging.getLogger(__name__)
from flask import current_app

def ack_message(ch, delivery_tag):
    if ch.is_open:
        ch.basic_ack(delivery_tag)
def nack_message(ch, delivery_tag,requeue):
    if ch.is_open:
        ch.basic_nack(delivery_tag,requeue)

class MQSerivce():


    def consume(self):
        logger.debug("MQService: Initialize")
        self.consume_channel = rabbitmq.get_consume_channel()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        with ThreadPoolExecutor() as executor:
            # Schedule the two consuming functions to run in separate threads
            loop.run_in_executor(executor, self.start_consuming)
            loop.run_in_executor(executor, self.start_music_consuming)

            # Run the event loop
            loop.run_forever()

    @staticmethod
    def gen_lyrics(ch, delivery_tag, body):
        from services.lyrics_service import LyricsService
        service = LyricsService()
        data = json.loads(body)

        running_jobs = LyricsService.get_running_jobs(
            job_type=SunoJobTypeEnum.LYRICS)
        

        if len(running_jobs) >= 1:
            logger.debug('MQService: Reached max running jobs')
            time.sleep(2)
            raise TooManyRequestsException("Reached max running jobs")


        job = LyricsService.create(data)
        task_type = data.get('type', 'lyrics')
        task_id = data.get('id')

        if job.job_id:
            # 说明任务添加成功
            job_result = None
            for _ in range(0, 10):
                time.sleep(2)
                job_result = LyricsService.get(job.id)
                if job_result.status == ClipStatusEnum.ERROR.value or job_result.status == ClipStatusEnum.COMPLETE.value:
                    break
            # public job.response to public queue
            data = json.dumps({
                "id": task_id,
                "type": task_type,
                "response": job_result.to_json()
            }, ensure_ascii=True).encode('utf-8')
            rabbitmq.get_public_channel().basic_publish(
                exchange='',
                routing_key=config.RABBITMQ_PUBLIC_QUEUE,
                body=data)
            # 任务成功，发送ack
            cb = functools.partial(ack_message, ch, delivery_tag)
            ch.connection.add_callback_threadsafe(cb)

        else:
            # 任务失败，重试
            logger.debug('MQService: Received unknown request')
            cb = functools.partial(nack_message, ch, delivery_tag, requeue=True)
            ch.connection.add_callback_threadsafe(cb)

    @staticmethod
    def gen_music(ch, delivery_tag, body):
        service = MusicService()
        data = json.loads(body)
        request = data.get("prompt")
        task_type = data.get('type', 'lyrics')
        id = data.get('id')
        # try:

        # 查询db，查看当前account在运行的任务数量
        running_jobs = MusicService.get_running_jobs(
            job_type=SunoJobTypeEnum.MUSIC)

        if len(running_jobs) >= config.SUNO_MAX_RUNNING_JOBS:
            logger.debug('MQService: Reached max running jobs')
            cb = functools.partial(nack_message, ch, delivery_tag, requeue=True)
            ch.connection.add_callback_threadsafe(cb)
            raise ReachedMaxJobsException("Reached max running jobs")

        jobs = MusicService.create(request)

        # 发布任务到 suno music queue
        for job in jobs:
            data = json.dumps({
                "id": id,
                "type": task_type,
                "job_id": str(job.id)
            }, ensure_ascii=True).encode('utf-8')
            rabbitmq.get_public_music_channel().basic_publish(
                exchange='',
                routing_key=config.RABBITMQ_PUBLIC_MUSIC_QUEUE,
                body=data
            )
        # 任务成功，返回ack
        logger.info(f"任务添加成功，id={id} ,type={task_type}")
        cb = functools.partial(ack_message, ch, delivery_tag)
        ch.connection.add_callback_threadsafe(cb)


    def _start_consume(self):
        self.consume_channel = rabbitmq.get_consume_channel()
        def do_work(ch, delivery_tag, body):
            logger.info(f"Received message: {body}")
            data = json.loads(body)
            task_type = data.get('type', 'lyrics')
            
            cb = functools.partial(nack_message, ch, delivery_tag, requeue=True)
            try:
                from extentions.ext_app import app
                with app.app_context():
                    if task_type == 'lyrics':
                        MQSerivce.gen_lyrics(ch, delivery_tag, body)
                    else:
                        MQSerivce.gen_music(ch, delivery_tag, body)
            except TooManyRequestsException:
                logger.error("Too many requests, retrying...")
                time.sleep(5)
                ch.connection.add_callback_threadsafe(cb)
            except ReachedMaxJobsException as ex:
                logger.error(f"Reached max running jobs, retrying...")
                time.sleep(20)
                ch.connection.add_callback_threadsafe(cb)
                
        def on_message(ch, method_frame, _header_frame, body, args):
            _,thrds = args
            delivery_tag = method_frame.delivery_tag
            t = threading.Thread(target=do_work, args=(ch, delivery_tag, body))
            t.start()
            thrds.append(t)

        threads = []
        on_message_callback = functools.partial(on_message, args=(rabbitmq.consume_connection, threads))
        self.consume_channel.basic_qos(prefetch_count=config.SUNO_MAX_RUNNING_JOBS)
        self.consume_channel.basic_consume(queue=config.RABBITMQ_CONSUME_QUEUE,
                                           on_message_callback=on_message_callback,
                                           auto_ack=False,
                                           consumer_tag=config.RABBITMQ_CONSUME_TAG)
        self.consume_channel.start_consuming()


    def start_consuming(self):
        logger.info("MQService: Start consuming")
        # self.consume_channel = rabbitmq.get_consume_channel()
        while True:
            # try:
            self._start_consume()
            # except Exception as ex:
            #     logger.error(f"MQService: Consume error: {str(ex)}")
            #     time.sleep(5)


    def start_music_consuming(self):
        logger.info("MQService: Start consuming music")

        from extentions.ext_app import app
        while True:

            with app.app_context():
                try:
                    self.music_channel = rabbitmq.get_public_music_channel()
                    # self.consume_channel = rabbitmq.get_consume_channel()

                    def music_callback(ch, method, properties, body):
                        logger.info(f"Received message: {body}")
                        data = json.loads(body)
                        
                        # 整体获取一下所有music状态
                        # 获取当前任务状态，如果任务完成/失败，添加任务到public队列
                        jobs = MusicService.mq_fetch_suno()
                        try:
                            job = MusicService.get(data.get('job_id'))
                            if job and (job.status == ClipStatusEnum.ERROR.value or job.status == ClipStatusEnum.COMPLETE.value):
                                data = json.dumps({
                                    "id": data.get('id'),
                                    "type": data.get('type'),
                                    "response": job.to_json()
                                }, ensure_ascii=True).encode('utf-8')
                                rabbitmq.get_public_channel().basic_publish(
                                    exchange='',
                                    routing_key=config.RABBITMQ_PUBLIC_QUEUE,
                                    body=data
                                )
                                ch.basic_ack(delivery_tag=method.delivery_tag)
                            else:
                                ch.basic_nack(
                                    delivery_tag=method.delivery_tag, requeue=True)
                                time.sleep(10)
                        except Exception as ex:
                            logger.error(
                                f"任务失败，id={data.get('id')} ,type={data.get('type')} ,ex={str(ex)}")
                            ch.basic_nack(
                                delivery_tag=method.delivery_tag, requeue=True)
                            time.sleep(10)
                    self.music_channel.basic_qos(prefetch_count=1)
                    self.music_channel.basic_consume(queue=config.RABBITMQ_PUBLIC_MUSIC_QUEUE,
                                                    on_message_callback=music_callback,
                                                    auto_ack=False,
                                                    consumer_tag=config.RABBITMQ_PUBLIC_MUSIC_CONSUME_TAG
                                                    )
                    self.music_channel.start_consuming()
                except (pika.exceptions.ConnectionClosedByBroker,
                        pika.exceptions.AMQPChannelError,
                        pika.exceptions.AMQPConnectionError) as e:
                    logger.error(f"Connection error: {e}")
                    self.music_channel.close()
                    time.sleep(5)  # 等待5秒后重试连接
                except Exception as e:
                    logger.error(f"Unexpected error occurred: {e}")
                    self.music_channel.close()
                    time.sleep(5)  # 等待5秒后重试连接
                finally:
                    pass

    def stop_consuming(self):
        if self.consume_channel:
            self.consume_channel.stop_consuming()
        if self.music_channel:
            self.music_channel.stop_consuming()
