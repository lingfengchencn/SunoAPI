
from datetime import datetime, timedelta

from requests import request
from sqlalchemy import not_, select
from extentions.ext_app import app
from extentions.ext_database import get_db
from models import SunoJobTypeEnum, SunoJobs
from suno.entities import ClipStatusEnum
import logging
from configs import config
logger = logging.getLogger(__name__)


class MusicService:

    def create(self, request: dict, db=next(get_db())) -> list[SunoJobs]:
        client = app.state.suno
        result = client.gen_music(request)
        jobs = []
        for clip in result.clips:
            job = SunoJobs(
                job_type=SunoJobTypeEnum.MUSIC.value,
                status=ClipStatusEnum.QUEUED.value,
                account=config.SUNO_ACCOUNT,
                request=request,
                created_at=datetime.now()
            )
            job.job_id = clip.id
            job.response = clip.to_json()
            db.add(job)
            jobs.append(job)

        db.commit()

        return jobs

    def get(self, job_id: str, db=next(get_db())) -> SunoJobs:
        stmt = select(SunoJobs).where(
            SunoJobs.job_type == SunoJobTypeEnum.MUSIC.value,
            SunoJobs.id == job_id
        )
        job = db.execute(stmt).scalar_one_or_none()

        return job

    def get_list(self, job_ids: list, db=next(get_db())) -> list[SunoJobs]:
        stmt = select(SunoJobs).where(
            SunoJobs.job_type == SunoJobTypeEnum.MUSIC.value,
            SunoJobs.id.in_(job_ids)
        )
        jobs = db.execute(stmt).scalars().all()

        return jobs

    def get_running_jobs(self, job_type: SunoJobTypeEnum, created_duration: int = 60*5, db=next(get_db())):
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

    def mq_fetch_suno(self, db=next(get_db())):
        stmt = select(SunoJobs).where(
            SunoJobs.job_type == SunoJobTypeEnum.MUSIC.value,
            not_(SunoJobs.status.in_(
                [ClipStatusEnum.COMPLETE.value, ClipStatusEnum.ERROR.value])),
            SunoJobs.account == config.SUNO_ACCOUNT
        ).limit(20)
        jobs = db.execute(stmt).scalars().all()

        if not jobs:
            return []

        client = app.state.suno
        ids = [str(clip.job_id) for clip in jobs]
        logger.info(f"get suno music ids : {ids}")
        music_list = client.get_music(ids)

        logger.info(
            f"get suno music data : {[music.to_json() for music in music_list]}")

        clip_exception = None
        for clip in music_list:
            db_clips = [db_c for db_c in jobs if str(db_c.job_id) == clip.id]
            db_clip = db_clips[0] if db_clips else None
            if db_clip:
                db_clip.response = clip.to_json()
                # if clip.status in [ClipStatusEnum.COMPLETE,ClipStatusEnum.ERROR]:
                db_clip.status = clip.status.value
                db.add(db_clip)
            db.commit()
        return jobs
