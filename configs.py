from typing import Any, Optional
from urllib.parse import quote_plus
from pydantic import Field, NonNegativeInt, PositiveInt, computed_field
from pydantic_settings import SettingsConfigDict,BaseSettings

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
    SESSION_ID: str = Field(
        description='session id',
        default='',
    )
    COOKIE: str = Field(
        description='suno cookie',
        default='',
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

class DatabaseConfig(BaseSettings):
    """
    Database configs
    """
    DB_URL: str = Field(
        description='database url',
        default='',
    )


class SunoConfig(
    PackagingInfo,
    DeploymentConfig,
    SunoClientConfig,
    LoggingConfig,
    DatabaseConfig
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