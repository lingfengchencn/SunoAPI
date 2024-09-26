
from datetime import datetime, timedelta

from requests import HTTPError
from extentions.ext_app import app
from models import SunoJobTypeEnum, SunoJobs
from suno.entities import ClipStatusEnum, SunoLyricGenerageStatusEnum
from models import SunoJobs, SunoJobTypeEnum
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.sql.expression import not_
from extentions.ext_database import get_db

import logging
from configs import config

from suno.exceptions import NotFoundException, ServiceUnavailableException
logger = logging.getLogger(__name__)

class LyricsService:

    def create(self,request:dict, db = next(get_db())) -> SunoJobs:
        client = app.state.suno
        try:
            job = SunoJobs(
                job_type=SunoJobTypeEnum.LYRICS.value,
                status=ClipStatusEnum.QUEUED.value,
                account=config.SUNO_ACCOUNT,
                request= request,
                created_at=datetime.now()
            )
            try:
                lyrics_id = client.gen_lyrics(request.get("prompt"))
                # 更新工作状态
                job.job_id = lyrics_id
                job.status = ClipStatusEnum.SUBMITTED.value
                db.add(job)
                db.commit()
            except Exception as ex:
                logger.error(f"gen lyrics exception:{str(ex)}")
                raise ex
            return job
        except ServiceUnavailableException as ex:
            logger.error(f"suno service unavailable:{str(ex)}")
            raise ex
    
    def get(self,job_id:str, db = next(get_db()),fetech_suno:bool = True) -> SunoJobs:
        client = app.state.suno
        try:
            stmt = select(SunoJobs).where(SunoJobs.id == job_id)
            # 执行查询
            result = db.execute(stmt)
            job = result.scalar_one_or_none()
            if job  and job.status in [ClipStatusEnum.COMPLETE.value ,ClipStatusEnum.ERROR.value]:
                pass
            elif fetech_suno:
                suno_lyrics = client.get_lyrics(job.job_id)
                if suno_lyrics.status == SunoLyricGenerageStatusEnum.COMPLETE:
                    job.status = ClipStatusEnum.COMPLETE.value
                    job.response = suno_lyrics.to_json()
                    db.add(job)
                    db.commit()
        except HTTPError as e:
            # 如果为404 说明 id不存在
            job.status = ClipStatusEnum.ERROR.value
            job.response = suno_lyrics.to_json()
            db.add(job)
            db.commit()
            if e.response.status_code == 404:
                raise NotFoundException("lyrics id is invalid or expired")

        return job
    
    def get_running_jobs(self, job_type: SunoJobTypeEnum = SunoJobTypeEnum.LYRICS, created_duration: int = 60*5, db=next(get_db())):
        """
        获取运行中任务
        job_type: 任务类型
        created_duration  int : 创建时间间隔,单位：秒

        """
        stmt = select(SunoJobs).where(
            not_(SunoJobs.status.in_(
                [ClipStatusEnum.COMPLETE.value, ClipStatusEnum.ERROR.value])),
            SunoJobs.account == config.SUNO_ACCOUNT
        )
        if job_type:
            stmt = stmt.where(SunoJobs.job_type == job_type.value)

        if created_duration:
            time_delta = timedelta(seconds=created_duration)
            stmt = stmt.where(SunoJobs.created_at >=
                              datetime.now() - time_delta)

        jobs = db.execute(stmt).scalars().all()

        logger.info(
            f"get suno jobs number: {len(jobs)}, job info : {','.join( [str(job.id)  for job in jobs])}")

        return jobs
