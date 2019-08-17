from functools import wraps

from flask import redirect, request, session
from flask import url_for


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_name') is None:
            return redirect(url_for('signin', next=request.url))
        return f(*args, **kwargs)

    return decorated_function
