from flask import Blueprint, render_template
from flask import render_template

bp_main = Blueprint('main', __name__)


@bp_main.route("/")
@bp_main.route("/home")
def home():
    return render_template('home.html')



