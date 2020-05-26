"""
Module that handles decorators used in request validation
"""
from functools import wraps

from flask import request, abort


def validate_form_with(validation_schema):
    """
    validates the form params with the marshmallow schema given as parameter
    :param validation_schema: schema to use for validation
    """

    def wrap(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            validation_errors = validation_schema().validate(request.form)
            if validation_errors:
                abort(400, str(validation_errors))

            return func(*args, **kwargs)

        return wrapped_func

    return wrap


def validate_url_params_with(validation_schema):
    """
    validates the url params with the marshmallow schema given as parameter
    :param validation_schema: schema to use for validation
    """

    def wrap(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            validation_errors = validation_schema().validate(kwargs)
            if validation_errors:
                abort(400, str(validation_errors))

            return func(*args, **kwargs)

        return wrapped_func

    return wrap
