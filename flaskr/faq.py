import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('faq', __name__, url_prefix='/')

@bp.route('/faq', methods=('GET',))
def faq():
    return render_template('faq.html')
