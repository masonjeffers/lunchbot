import json
from lunchbot import process_message
from flask import Flask, request, render_template

app = Flask(__name__)

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
		except (ValueError, KeyError) as e:
			return "Invalid JSON in request : " +   e.message, 400
	 
		return process_message(msg, user, room)

	# get index page
	else:
		return render_template('lunchbot.html')

if __name__ == '__main__':
	app.debug = True
	app.run(debug=True, host='0.0.0.0', port=80)
