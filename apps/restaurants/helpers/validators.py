import re
from functools import wraps
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import NotFound, APIException


class ServiceErrorHandler:
    """Decorators for common service-layer errors."""

    @staticmethod
    def handle_integrity_error(constraint_map=None):
        """Catch IntegrityError → ValidationError with field‑specific messages."""
        constraint_map = constraint_map or {}

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except IntegrityError as e:
                    msg = str(e)
                    for name, detail in constraint_map.items():
                        if name in msg:
                            raise serializers.ValidationError(detail)
                    match = re.search(r'constraint "([^"]+)"', msg)
                    if match and match.group(1) in constraint_map:
                        raise serializers.ValidationError(constraint_map[match.group(1)])
                    raise serializers.ValidationError({"non_field_errors": "Duplicate entry."})
            return wrapper
        return decorator

    @staticmethod
    def handle_does_not_exist(message=None, model_name=None):
        """Catch ObjectDoesNotExist → NotFound."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except ObjectDoesNotExist:
                    if message:
                        raise NotFound(message)
                    if model_name:
                        raise NotFound(f"{model_name} not found.")
                    raise NotFound("Object not found.")
            return wrapper
        return decorator

    @staticmethod
    def handle_all_exceptions(user_message=None):
        user_message = user_message or "An unexpected error occurred. Please try again."

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except APIException:
                    raise  # DRF exceptions pass through
                except DjangoValidationError as e:
                    # Convert Django validation error to DRF ValidationError
                    if hasattr(e, 'message_dict'):
                        raise serializers.ValidationError(e.message_dict)
                    elif hasattr(e, 'message'):
                        raise serializers.ValidationError({"non_field_errors": e.message})
                    else:
                        raise serializers.ValidationError({"non_field_errors": str(e)})
                except Exception as e:
                    # Unexpected error – log if needed
                    raise serializers.ValidationError({"non_field_errors": user_message})
            return wrapper
        return decorator
    
    @staticmethod
    def validate_positive(value):
        if value <= 0:
            raise serializers.ValidationError("Must be greater than 0.")