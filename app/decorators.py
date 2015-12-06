from functools import wraps

from flask import abort
from flask.ext.login import current_user
from .models import Permission


def permission_required(permission):
    """Restrict a view to users with the given permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)


def some_permission_required(permissions):
    """Given a list of permissions, restrict a view to
    users with at least one of the permissions in the
    list"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for p in permissions:
                if current_user.can(p):
                    return f(*args, **kwargs)
            abort(403)
        return decorated_function
    return decorator


def admin_or_agency_required(f):
    return some_permission_required([Permission.ADMINISTER,
                                    Permission.AGENCY_WORKER])(f)
