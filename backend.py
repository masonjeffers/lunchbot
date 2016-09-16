from lunchbot import process_message
from coffeebot import start_brew
from celery import Celery
from flask import Flask, request, render_template

import json

app = Flask(__name__)

app.config.update(
	CELERY_BROKER_URL='redis://localhost:6379',
	CELERY_RESULT_BACKEND='redis://localhost:6379',
	PROPAGATE_EXCEPTIONS=True
)

def make_celery(app):
	celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
			broker=app.config['CELERY_BROKER_URL'])
	celery.conf.update(app.config)
	TaskBase = celery.Task
	class ContextTask(TaskBase):
		abstract = True
		def __call__(self, *args, **kwargs):
			with app.app_context():
				return TaskBase.__call__(self, *args, **kwargs)
	celery.Task = ContextTask
	return celery

make_celery(app)

@app.route('/')
def index():
	return render_template('index.html')
	# 'Welcome to the homepage!\nFor lunchbot, navigate to <a href="/lunchbot">/lunchbot</a>!'

@app.route('/lunchbot', methods=['GET', 'POST'])
def lunchbot():

	#  process message from hipchat
	if request.method == 'POST':

		try:
			json_dict = json.loads(request.data)
			msg = json_dict['item']['message']['message']
			user = json_dict['item']['message']['from']['name']
			room = json_dict['item']['room']['name']

		except ValueError as e: return "Invalid JSON in request : " + e.message, 400
	
		return process_message(msg, user, room)

	# get index page
	else:	return render_template('lunchbot.html')

@app.route('/coffeebot', methods=['GET', 'POST'])
def coffeebot():

	if request.method == 'POST':
		try:
			start_brew()
			return '200'
		except:
			return '400' 

	else: return render_template('coffeebot.html')

if __name__ == '__main__':
	app.debug = True
	app.run(debug=True, host='0.0.0.0', port=80)
