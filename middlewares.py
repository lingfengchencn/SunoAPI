import json
import uuid
from fastapi import FastAPI, Request
from uuid import uuid4
import logging

from suno.exceptions import NotFoundException, ServiceUnavailableException, TooManyRequestsException

logger = logging.getLogger(__name__)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextvars import ContextVar

request_id_ctx_var = ContextVar("request_id", default=None)

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request_id_ctx_var.set(request_id)
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# 统一处理异常
class ResponseExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response: Response = await call_next(request)
            return response
        except TooManyRequestsException as e:
            content = json.dumps({"message":str(e),
                                     "code":429
                                     })
            return Response(content=content, status_code=429)
        except ServiceUnavailableException as e:
            content = json.dumps({"message":str(e),
                                     "code":503
                                     })
            return Response(content=content, status_code=503)
        except NotFoundException as e:
            content = json.dumps({"message":str(e),
                                     "code":404
                                     })
            return Response(content=content, status_code=404)
        except Exception as e:
            logger.error(e)
            content = json.dumps({"message":str(e),
                                     "code":500
                                     })
            return Response(content=content, status_code=500)