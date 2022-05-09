from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def dash_board():
    return render_template('')


@app.route('/find_by_do')
def find_by_do():
    return False

