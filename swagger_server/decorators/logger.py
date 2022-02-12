import json
import logging
import inspect
from collections.abc import Callable
from flask import has_request_context, request
from http import HTTPStatus


def logger(log_input=True, log_output=True) -> Callable:
    """Decorator function to log extra information including
    the function and file name that it's being called, and extra data about the
    request that it's being handled.

    :param log_input: bool
    :param log_output: bool

    :return: Callable
    """

    def decorator(func: Callable) -> Callable:
        def func_wrapper(*args, **kwargs) -> Callable:
            filename = inspect.stack()[1].filename
            # Get the filname from the stack

            logger = logging.getLogger(func.__name__)
            message: dict = {}

            if has_request_context():
                # If it has request context then log the request origin and
                # the request url
                message["Request"] = f"* Request URL {request.url}"
                message[
                    "Request Origin"
                ] = f"* Request remote address {request.remote_addr}"

            name = filename.split("/usr/src/app/swagger_server/").pop()
            # Get the name without the actual path

            message[
                "Filename"
            ] = f"* Calling the {func.__name__} function from the {name} file"

            if log_input:
                message["Arguments"] = f"* Calling with the arguments: {args}"
                message[
                    "Keyword Arguments"
                ] = f"* Calling with the keyword arguments: {kwargs}"
            result = func(*args, **kwargs)

            if log_output:
                message["Output"] = f"* Result value: {result}"

            status = result[-1]

            json_message = json.dumps(message)
            if status == HTTPStatus.OK or status == HTTPStatus.CREATED:
                logger.info(json_message)
            else:
                logger.error(json_message)

            return result

        return func_wrapper

    return decorator
