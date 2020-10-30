import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('helpp', __name__, url_prefix='/')

@bp.route('/help', methods=('GET',))
def help():
    return render_template('help.html')
