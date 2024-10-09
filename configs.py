from typing import Any, Optional
from urllib.parse import quote_plus
from pydantic import Field, NonNegativeInt, PositiveInt, computed_field
from pydantic_settings import SettingsConfigDict,BaseSettings
import uuid

class PackagingInfo(BaseSettings):
    """
    Packaging build information
    """

    CURRENT_VERSION: str = Field(
        description='SunoAPI unoffical version',
        default='5.20.0',
    )

    COMMIT_SHA: str = Field(
        description="SHA-1 checksum of the git commit used to build the app",
        default='',
    )

class DeploymentConfig(BaseSettings):
    """
    Deployment configs
    """
    APPLICATION_NAME: str = Field(
        description='application name',
        default='lingfengchencn/sunoapi',
    )

    TESTING: bool = Field(
        description='',
        default=False,
    )

    EDITION: str = Field(
        description='deployment edition',
        default='SELF_HOSTED',
    )

    DEPLOY_ENV: str = Field(
        description='deployment environment, default to PRODUCTION.',
        default='PRODUCTION',
    )
class SunoClientConfig(BaseSettings):
    """
    Suno client configs
    """
    SUNO_ACCOUNT: str = Field(
        description='suno account',
        default='',
    )
    SESSION_ID: str = Field(
        description='session id',
        default='',
    )
    COOKIE: str = Field(
        description='suno cookie',
        default='',
    )
    SUNO_MAX_RUNNING_JOBS: int = Field(
        description='max running jobs',
        default=10,
    )
class LoggerColor:
    # ANSI 转义序列，用于颜色和样式
    COLOR_GREEN = '\033[92m'
    COLOR_RED = '\033[91m'
    STYLE_BOLD = '\033[1m'
    RESET = '\033[0m'

class LoggingConfig(BaseSettings):
    """
    Logging configs
    """

    LOG_LEVEL: str = Field(
        description='Log output level, default to INFO.'
                    'It is recommended to set it to ERROR for production.',
        default='INFO',
    )

    LOG_FILE: Optional[str] = Field(
        description='logging output file path',
        default=None,
    )

    LOG_FORMAT: str = Field(
        description='log format',
        default=f'{LoggerColor.STYLE_BOLD}[%(asctime)s.%(msecs)03d %(levelname)s]{LoggerColor.COLOR_GREEN}[%(request_id)s]{LoggerColor.RESET}{LoggerColor.STYLE_BOLD}[%(threadName)s] [%(filename)s:%(lineno)d]{LoggerColor.RESET}  - %(message)s',
    )

    LOG_DATEFORMAT: Optional[str] = Field(
        description='log date format',
        default=None,
    )

    LOG_TZ: Optional[str] = Field(
        description='specify log timezone, eg: America/New_York',
        default=None,
    )
    LOG_WHEN: str = Field(
        description='log rotate when, default to H',
        default='H',
    )
    LOG_INTERVAL: PositiveInt = Field(
        description='log rotate interval, default to 1',
        default=1,
    )
    LOG_BACKUPCOUNT: NonNegativeInt = Field(
        description='log backup count, default to 24',
        default=24,
    )
    LOG_MAXBYTES: NonNegativeInt = Field(
        description='log max bytes, default to 1GB',
        default=1*1024*1024*1024,
    )


class DatabaseConfig:
    DB_HOST: str = Field(
        description="db host",
        default="localhost",
    )

    DB_PORT: PositiveInt = Field(
        description="db port",
        default=5432,
    )

    DB_OUT_PORT: PositiveInt = Field(
        description="db out port",
        default=5433,
    )

    DB_USERNAME: str = Field(
        description="db username",
        default="postgres",
    )

    DB_PASSWORD: str = Field(
        description="db password",
        default="",
    )

    DB_DATABASE: str = Field(
        description="db database",
        default="dify",
    )

    DB_CHARSET: str = Field(
        description="db charset",
        default="",
    )

    DB_EXTRAS: str = Field(
        description="db extras options. Example: keepalives_idle=60&keepalives=1",
        default="",
    )

    SQLALCHEMY_DATABASE_URI_SCHEME: str = Field(
        description="db uri scheme",
        default="postgresql",
    )

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        db_extras = (
            f"{self.DB_EXTRAS}&client_encoding={self.DB_CHARSET}" if self.DB_CHARSET else self.DB_EXTRAS
        ).strip("&")
        db_extras = f"?{db_extras}" if db_extras else ""
        return (
            f"{self.SQLALCHEMY_DATABASE_URI_SCHEME}://"
            f"{quote_plus(self.DB_USERNAME)}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
            f"{db_extras}"
        )

    SQLALCHEMY_POOL_SIZE: NonNegativeInt = Field(
        description="pool size of SqlAlchemy",
        default=30,
    )

    SQLALCHEMY_MAX_OVERFLOW: NonNegativeInt = Field(
        description="max overflows for SqlAlchemy",
        default=10,
    )

    SQLALCHEMY_POOL_RECYCLE: NonNegativeInt = Field(
        description="SqlAlchemy pool recycle",
        default=3600,
    )

    SQLALCHEMY_POOL_PRE_PING: bool = Field(
        description="whether to enable pool pre-ping in SqlAlchemy",
        default=False,
    )

    SQLALCHEMY_ECHO: bool | str = Field(
        description="whether to enable SqlAlchemy echo",
        default=False,
    )

    @computed_field
    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> dict[str, Any]:
        return {
            "pool_size": self.SQLALCHEMY_POOL_SIZE,
            "max_overflow": self.SQLALCHEMY_MAX_OVERFLOW,
            "pool_recycle": self.SQLALCHEMY_POOL_RECYCLE,
            "pool_pre_ping": self.SQLALCHEMY_POOL_PRE_PING,
            "connect_args": {"options": "-c timezone=UTC"},
        }

class RabbitMQSettings(BaseSettings):
    """
    RabbitMQ Configuration Settings
    """
    RABBITMQ_CONSUME_HOST: str = Field(
        description='RabbitMQ server IP or hostname',
        default='localhost'
    )
    RABBITMQ_CONSUME_PORT: int = Field(
        description='RabbitMQ server port',
        default=5672
    )
    RABBITMQ_CONSUME_USERNAME: str = Field(
        description='Username to authenticate with RabbitMQ server',
        default='guest'
    )
    RABBITMQ_CONSUME_PASSWORD: str = Field(
        description='Password to authenticate with RabbitMQ server',
        default='guest'
    )
    RABBITMQ_CONSUME_QUEUE: str = Field(
        description='RabbitMQ queue name',
        default='default_queue'
    )
    RABBITMQ_CONSUME_DURABLE: bool =  Field(
        description='RabbitMQ durable',
        default=True
    )
    RABBITMQ_CONSUME_TAG: str = Field(
        description='RabbitMQ conusme tag',
        default=uuid.uuid4().hex
    )
    RABBITMQ_CONSUME_CONNECTION_ATTEMPS: int = Field(
        description='RabbitMQ connection attempts',
        default=10
    )
    RABBITMQ_CONSUME_RETRY_DELAY: int = Field(
        description='RabbitMQ retry delay',
        default=5
    )
    RABBITMQ_CONSUME_SOCKET_TIMEOUT: int = Field(
        description='RabbitMQ socket timeout',
        default=10
    )
    RABBITMQ_CONSUME_BLOCKED_CONNECTION_TIMEOUT: int = Field(
        description='RabbitMQ blocked connection timeout',
        default=30
    )
    RABBITMQ_CONSUME_CHANNEL_MAX: int = Field(
        description='RabbitMQ channel max',
        default=10
    )
    RABBITMQ_CONSUME_HEARTBEAT: int = Field(
        description='RabbitMQ heartbeat',
        default=1000
    )









    RABBITMQ_PUBLIC_HOST: str = Field(
        description='RabbitMQ server IP or hostname',
        default='localhost'
    )
    RABBITMQ_PUBLIC_PORT: int = Field(
        description='RabbitMQ server port',
        default=5672
    )
    RABBITMQ_PUBLIC_USERNAME: str = Field(
        description='Username to authenticate with RabbitMQ server',
        default='guest'
    )
    RABBITMQ_PUBLIC_PASSWORD: str = Field(
        description='Password to authenticate with RabbitMQ server',
        default='guest'
    )
    RABBITMQ_PUBLIC_QUEUE: str = Field(
        description='RabbitMQ queue name',
        default='default_queue'
    )
    RABBITMQ_PUBLIC_DURABLE: bool =  Field(
        description='RabbitMQ durable',
        default=True
    )
    RABBITMQ_PUBLIC_CONNECTION_ATTEMPS: int = Field(
        description='RabbitMQ connection attempts',
        default=10
    )
    RABBITMQ_PUBLIC_RETRY_DELAY: int = Field(
        description='RabbitMQ retry delay',
        default=5
    )
    RABBITMQ_PUBLIC_SOCKET_TIMEOUT: int = Field(
        description='RabbitMQ socket timeout',
        default=10
    )
    RABBITMQ_PUBLIC_BLOCKED_CONNECTION_TIMEOUT: int = Field(
        description='RabbitMQ blocked connection timeout',
        default=30
    )
    RABBITMQ_PUBLIC_CHANNEL_MAX: int = Field(
        description='RabbitMQ channel max',
        default=10
    )
    RABBITMQ_PUBLIC_HEARTBEAT: int = Field(
        description='RabbitMQ heartbeat',
        default=1000
    )


    ## --------- RABBIT MQ ----------
    RABBITMQ_PUBLIC_MUSIC_HOST: str = Field(
        description='RabbitMQ server IP or hostname',
        default='localhost'
    )
    RABBITMQ_PUBLIC_MUSIC_PORT: int = Field(
        description='RabbitMQ server port',
        default=5672
    )
    RABBITMQ_PUBLIC_MUSIC_USERNAME: str = Field(
        description='Username to authenticate with RabbitMQ server',
        default='guest'
    )
    RABBITMQ_PUBLIC_MUSIC_PASSWORD: str = Field(
        description='Password to authenticate with RabbitMQ server',
        default='guest'
    )
    RABBITMQ_PUBLIC_MUSIC_QUEUE: str = Field(
        description='RabbitMQ queue name',
        default='default_queue'
    )
    RABBITMQ_PUBLIC_MUSIC_DURABLE: bool =  Field(
        description='RabbitMQ durable',
        default=True
    )
    RABBITMQ_PUBLIC_MUSIC_CONSUME_TAG: str = Field(
        description='RabbitMQ music conusme tag',
        default=uuid.uuid4().hex
    )
    RABBITMQ_PUBLIC_MUSIC_CONNECTION_ATTEMPS: int = Field(
        description='RabbitMQ connection attempts',
        default=10
    )
    RABBITMQ_PUBLIC_MUSIC_RETRY_DELAY: int = Field(
        description='RabbitMQ retry delay',
        default=5
    )
    RABBITMQ_PUBLIC_MUSIC_SOCKET_TIMEOUT: int = Field(
        description='RabbitMQ socket timeout',
        default=10
    )
    RABBITMQ_PUBLIC_MUSIC_BLOCKED_CONNECTION_TIMEOUT: int = Field(
        description='RabbitMQ blocked connection timeout',
        default=30
    )
    RABBITMQ_PUBLIC_MUSIC_CHANNEL_MAX: int = Field(
        description='RabbitMQ channel max',
        default=10
    )
    RABBITMQ_PUBLIC_MUSIC_HEARTBEAT: int = Field(
        description='RabbitMQ heartbeat',
        default=1000
    )



class SunoConfig(
    PackagingInfo,
    DeploymentConfig,
    SunoClientConfig,
    LoggingConfig,
    DatabaseConfig,
    RabbitMQSettings
):
    model_config = SettingsConfigDict(
        # read from dotenv format config file
        env_file='.env',
        env_file_encoding='utf-8',
        frozen=True,
        # ignore extra attributes
        extra='ignore',
    )
    DEBUG: bool = Field(default=False, description='whether to enable debug mode.')


config = SunoConfig()