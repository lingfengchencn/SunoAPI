from datetime import datetime, timezone
from enum import Enum
import uuid
from sqlalchemy import Column, String, JSON ,DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from suno.entities import SunoLyricGenerageStatusEnum

# 创建基础模型类，所有模型将继承自这个类
Base = declarative_base()

class SunoJobTypeEnum(Enum):
    MUSIC = "music"
    LYRICS = "lyrics"

    @classmethod
    def value_of(cls, value):
        for item in cls:
            if item.value == value:
                return item

class SunoJobs(Base):
    __tablename__ = "suno_jobs"
    id = Column(UUID(as_uuid=True),primary_key=True, default=uuid.uuid4, index=True) # 任务id
    job_id = Column(UUID(as_uuid=True), index=True) #suno music id
    job_type = Column(String(10)) # 任务类型
    status = Column(String) # 任务状态
    request = Column(JSON) # 请求参数
    response = Column(JSON) # 响应参数
    created_at = Column(DateTime, default=datetime.now(timezone.utc)) #   创建时间

    @property
    def job_type_enum(self):
        return SunoJobTypeEnum.value_of(self.job_type)
    @job_type_enum.setter
    def job_type_enum(self, value: SunoJobTypeEnum):
        self.job_type = value.value


    def to_json(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "job_type": self.job_type,
            "status": self.status,
            "request": self.request,
            "response": self.response,
            "created_at": self.created_at
        }
