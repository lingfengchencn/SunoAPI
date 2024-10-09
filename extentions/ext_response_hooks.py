from flask import Flask, request, jsonify, g
import logging

from suno.exceptions import NotFoundException, ServiceUnavailableException, TooManyRequestsException
logger = logging.getLogger(__name__)
from contextvars import ContextVar

request_id_ctx_var = ContextVar("request_id", default=None)

def register_response_hook(app):
    @app.before_request
    def add_request_id(response):
        """在响应中添加请求 ID"""
        response.headers["X-Request-ID"] = g.request_id
        return response

    @app.errorhandler(TooManyRequestsException)
    def handle_too_many_requests(e):
        return jsonify(message=str(e), code=429), 429

    @app.errorhandler(ServiceUnavailableException)
    def handle_service_unavailable(e):
        return jsonify(message=str(e), code=503), 503

    @app.errorhandler(NotFoundException)
    def handle_not_found(e):
        return jsonify(message=str(e), code=404), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(e)
        return jsonify(message=str(e), code=500), 500