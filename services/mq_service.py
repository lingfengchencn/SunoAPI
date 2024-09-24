import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import json

import pika
from extentions.ext_database import get_db
from extentions.ext_rabbitmq import rabbitmq
from configs import config

import logging

from models import SunoJobTypeEnum
from services.music_service import MusicService
from suno.entities import ClipStatusEnum
logger = logging.getLogger(__name__)
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
    def gen_lyrics(ch, method, properties, body):
        from services.lyrics_service import LyricsService
        service = LyricsService()
        db = next(get_db())
        data = json.loads(body)
        job = service.create(data,db)
        task_type = data.get('type','lyrics')
        task_id = data.get('id')
        
        if job.job_id:
            # 说明任务添加成功
            job_result = None
            for _ in range(0, 10):
                time.sleep(2)
                job_result = service.get(job.id,db)
                if job_result.status == ClipStatusEnum.ERROR.value or job_result.status == ClipStatusEnum.COMPLETE.value:
                    break
            # public job.response to public queue
            data = json.dumps({
                "id":task_id,
                "type": task_type,
                "response": job.to_json()
            },ensure_ascii=True).encode('utf-8')
            rabbitmq.get_public_channel().basic_publish(
                exchange='', 
                routing_key=config.RABBITMQ_PUBLIC_QUEUE, 
                body=data)
            # 任务成功，发送ack
            ch.basic_ack(delivery_tag=method.delivery_tag)

        else:
            # 任务失败，重试
            logger.debug('MQService: Received unknown request')
            ch.basic_nack(delivery_tag=method.delivery_tag)
    
    @staticmethod
    def gen_music(ch, method, properties, body):
        service = MusicService()
        db = next(get_db())
        data = json.loads(body)
        request = data.get("prompt")
        task_type = data.get('type','lyrics')
        id = data.get('id')
        try:

            # 查询db，查看当前account在运行的任务数量
            running_jobs = service.get_running_jobs(job_type=SunoJobTypeEnum.MUSIC, db=db)

            if len(running_jobs) >= config.SUNO_MAX_RUNNING_JOBS:
                logger.debug('MQService: Reached max running jobs')
                raise Exception("Reached max running jobs")


            jobs = service.create(request,db)

            # 发布任务到 suno music queue
            for job in jobs:
                data = json.dumps({
                    "id":id,
                    "type": task_type,
                    "job_id": str(job.id)
                },ensure_ascii=True).encode('utf-8')
                rabbitmq.get_public_music_channel().basic_publish(
                    exchange='', 
                    routing_key=config.RABBITMQ_PUBLIC_MUSIC_QUEUE, 
                    body=data
                )
            # 任务成功，返回ack
            logger.info(f"任务添加成功，id={id} ,type={task_type}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as ex:
            logger.error(f"任务添加失败，id={id} ,type={task_type} ,ex={str(ex)}")
            time.sleep(5) # 失败稍等在执行
            ch.basic_nack(delivery_tag=method.delivery_tag,requeue=True)
        

    def start_consuming(self):
        logger.info("MQService: Start consuming")
        # self.consume_channel = rabbitmq.get_consume_channel()
        def callback(ch, method, properties, body):
            logger.info(f"Received message: {body}")
            data = json.loads(body)
            task_type = data.get('type','lyrics')

            if task_type == 'lyrics':
                MQSerivce.gen_lyrics(ch, method, properties, body)
            else:
                MQSerivce.gen_music(ch, method, properties, body)


        self.consume_channel.basic_consume(queue=config.RABBITMQ_CONSUME_QUEUE, on_message_callback=callback,auto_ack=False)
        self.consume_channel.start_consuming()

    def start_music_consuming(self):
        logger.info("MQService: Start consuming music")
        while True:
            try:
                self.music_channel = rabbitmq.get_public_music_channel()
                # self.consume_channel = rabbitmq.get_consume_channel()
                def music_callback(ch, method, properties, body):
                    logger.info(f"Received message: {body}")
                    data = json.loads(body)
                    db = next(get_db())
                    # 整体获取一下所有music状态
                    # 获取当前任务状态，如果任务完成/失败，添加任务到public队列
                    service = MusicService()
                    service.mq_fetch_suno(db)
                    try:
                        job = service.get(data.get('job_id'),db)
                        if job and ( job.status == ClipStatusEnum.ERROR.value or job.status == ClipStatusEnum.COMPLETE.value):
                            data = json.dumps({
                                "id":data.get('id'),
                                "type": data.get('type'),
                                "response": job.to_json()
                            },ensure_ascii=True).encode('utf-8')
                            rabbitmq.get_public_channel().basic_publish(
                                exchange='', 
                                routing_key=config.RABBITMQ_PUBLIC_QUEUE, 
                                body=data
                            )
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                        else:
                            ch.basic_nack(delivery_tag=method.delivery_tag,requeue=True )
                            time.sleep(10)
                    except Exception as ex:
                        logger.error(f"任务失败，id={data.get('id')} ,type={data.get('type')} ,ex={str(ex)}")
                        ch.basic_nack(delivery_tag=method.delivery_tag,requeue=True )
                self.music_channel.basic_consume(queue=config.RABBITMQ_PUBLIC_MUSIC_QUEUE, on_message_callback=music_callback,auto_ack=False)
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