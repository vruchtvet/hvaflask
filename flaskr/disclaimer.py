import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('disclaimer', __name__, url_prefix='/')

@bp.route('/disclaimer', methods=('GET',))
def disclaimer():
    return render_template('disclaimer.html')
