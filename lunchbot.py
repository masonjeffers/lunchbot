import os, random, datetime, requests

REST_PATH = '/var/www/html/lunchbot/restaurants.txt'
DRIVER_PATH = '/var/www/html/lunchbot/drivers.txt'
LAST_DRIVER_PATH = '/var/www/html/lunchbot/driver_last.txt'
LAST_REST_PATH = '/var/www/html/lunchbot/restaurant_last.txt'
SANDBOX_URL_PATH = '/var/www/html/lunchbot/SANDBOX_URL.txt'
TFA_URL_PATH = '/home/ubuntu/PRIVATE/TFA_URL.txt'

### PROCESS COMMAND FROM HIPCHAT
def process_message(msg, room):

	# logic to be replaced with regex
	msg_arr = msg.split(" ")

	# ensure message contains a command
	if len(msg_arr) < 2: return __print_help(room)

	# list command requires 1 argument (list name)
	if msg_arr[1] == "list":

		if len(msg_arr) >= 3: 	return __print_list(msg_arr[2], room)
		else: 			return __print_list("no arguments", room)
		
	# add command requires 2 arguments (list name, list item)
	elif msg_arr[1] == "add":

		if len(msg_arr) >= 4:	return __add_command(msg_arr[2], ' '.join(msg_arr[3:]), room)
		else:			return __add_command("no", "arguments", room)

	# remove command requires 2 arguments (list name, list item)
	elif msg_arr[1] == "remove":

		if len(msg_arr) >= 4:	return __remove_command(msg_arr[2], ' '.join(msg_arr[3:]), room)
		else:			return __remove_command("no", "arguments", room)

	# vote command requires 2 arguments (list name, list item, value)
	elif (msg_arr[1] == "upvote") or (msg_arr[1] == "downvote"):

		if len(msg_arr) >= 4:
			
			if msg_arr[1] == "upvote": 	return __vote_command(msg_arr[2], ' '.join(msg_arr[3:]), 1, room)
			else:				return __vote_command(msg_arr[2], ' '.join(msg_arr[3:]), -1, room)

		else:	__vote_command('no', 'arguments', 1, room)

	# gross command requires 0 arguments
	elif msg_arr[1] == "gross":	return __gross("place holder", room)

	else: return __print_help(room)

def __get_path(name):

	if name.lower() == 'restaurant': return REST_PATH
	elif name.lower() == 'driver': return DRIVER_PATH
	else: return ''

def __vote_command(name, item, value, room):

	msg = ''
	val = int(value)

	path = __get_path(name)
	if (not path) or ((val != 1) and (val != -1)): return __post_to_hipchat(room, 'Proper usage: /lunchbot [upvote, downvote] [restaurant, driver] [name of restaurant/driver]', 'gray')

	if __search_for_item(path, item):
		
		__update_item(path, item, val)		
		msg = ('(upvote) ' if (val == 1) else '(downvote) ' ) + str(item).upper()

	else: msg = str(item).upper() + ' does not exist in list ' + str(name).upper()

	return __post_to_hipchat(room, msg, 'purple')

def __update_item(path, item, val):

	rest_list = []
	with open(path, 'r') as f:
		for line in f:
			rest_list.append(line)

	with open(path, 'w') as f:
		for rest in rest_list:
			restaurant = (rest.split(','))[0]
			if item.upper() == restaurant.upper():
				weight = int((rest.split(','))[1]) + val
				if (weight > 0) and (weight < 11):
					f.write(restaurant + ', ' + str(weight) + '\n')
					continue
			f.write(rest)

#Return all lines from a file in a list
def __get_lines(path):
	try:
		with open(path, 'r') as f:
			lines = f.readlines()
			return lines
	except Exception as e:
		print "COULD NOT READ FILE IN __get_lines()", e.message
		print "PATH: " + str(path) + "\n"
		return None		
 
#Write a list of lines to a file 
def __write_lines(path, lines):
	try:
		with open(path, 'w') as f:
			f.writelines(lines) 
	except Exception as e:
		print "COULD NOT WRITE TO FILE IN __write_lines(): " + e.message
		print "PATH : " + str(path) + "\n"
		print "LINES: " + str(lines) + "\n"


### RETURNS TRUE IF FOUND, FALSE IF NOT OR ERROR
def __search_for_item(path, item):

	try:
		with open(path, 'r') as f:
			for line in f:
				restaurant = (line.split(','))[0]
				if item.upper() == restaurant.upper():
					return True
	except:
		print "COULD NOT OPEN FILE IN __search_for_item()\n"
		print "PATH: " + str(path) + "\n"
		print "ITEM: " + str(item) + "\n"
		return False

### ADD ITEM TO LIST
def __add_command(name, item, room):

	msg = ''

	path = __get_path(name)
	if not path: return __post_to_hipchat(room, 'Proper usage: /lunchbot add [restaurant, driver] [name of restaurant/driver]', 'gray')

	if not __search_for_item(path, item):
		__add_item(path, item)
		msg = str(item).upper() + ' added to ' + str(name).upper() + ' list!'
	else:
		msg = str(item).upper() + ' already exists in ' + str(name).upper() + ' list!'
	
	return __post_to_hipchat(room, msg, 'purple')

def __add_item(path, item):

	try:
		with open(path, 'a') as f:
			f.write(str(item) + ", 1")
	except:
		print "ERROR OPENING/APPENDING TO PATH IN __add_item()\n"
		print "PATH: " + str(path) + "\n"
		print "ITEM: " + str(item) + "\n"
		
def __remove_item(path, item):
	try:
		item = item.lower().strip()
		lines = [l for l in __get_lines(path) if not l.lower().startswith(item)]
		__write_lines(path, lines)
	except:
		print "ERROR OPENING/APPENDING TO PATH IN __remove_item()\n" 
		print "PATH: " + str(path) + "\n"
		print "ITEM: " + str(item) + "\n"		

### REMOVE ITEM FROM LIST
def __remove_command(name, item, room):

	path = __get_path(name)
	if not path: return __post_to_hipchat(room, 'Proper usage: /lunchbot remove [restaurant, driver] [name of restaurant/driver]', 'gray')
	
	if __search_for_item(path, item):
		__remove_item(path,item)
		msg = str(item).upper() + ' removed from ' + str(name).upper() + ' list!'
	else:
		msg = str(item).upper() + ' doesn\'t exists in ' + str(name).upper() + ' list!'	
	
	return __post_to_hipchat(room, msg, 'purple')

### ADD USER TO VETO LIST
def __gross(user, room): __post_to_hipchat(room, 'TODO: add veto function', 'purple')

### POSTS PROPER USAGE MESSAGE TO HIPCHAT
def __print_help(room):

	msg = "Proper usage: /lunchbot [command (i.e. list, add, remove, gross)] [option 1] [option 2]"

	return __post_to_hipchat(room, msg, "gray")

### POSTS LIST TO HIPCHAT
def __print_list(name, room):

	msg = __get_list_msg(name)

	return __post_to_hipchat(room, msg, "gray")

### RETURNS LIST AS A MESSAGE FORMATTED FOR HIPCHAT
def __get_list_msg(name):

	msg = ""
	f = None

	if (name.lower() == "restaurants"):

		msg += "RESTAURANTS, WEIGHT\n"
		f = open(REST_PATH, 'r')

	elif (name.lower() == "drivers"):

		msg += "DRIVERS, WEIGHT\n"
		f = open(DRIVER_PATH, 'r')

	else: return "Proper usage: /lunchbot list [restaurants, drivers]"

	msg += f.read()

	return msg

### RETURNS A RANDOM ITEM FROM A LIST
def __get_random_item(path, last_item_file=None):

	f = open(path, 'r')

	arr = []

	#Check for previous item
	last_item = __get_lines(last_item_file)[0] if last_item_file is not None else None

	for line in f:
		
		# first item is restaurant, second is weight
		split_line = line.split(',')

		restaurant = split_line[0]
		weight = split_line[1]

		# add restaurant to list "weight" times if not
		# previously chosen item
		if restaurant != last_item:
			for i in range(0, int(weight)):
				arr.append(line)

	f.close()

	choice = (arr[random.randrange(0, len(arr))]).split(',')

	#Write this item to the last file
	__write_lines(last_item_file, choice[0])

	return choice[0].strip().upper()

### POSTS MESSAGE TO HIPCHAT
def __post_to_hipchat(room, message, color = "green", notify = False, message_format = "text"):

	url = ''
	if room == 'The Force Awakens': url = __get_single_line(TFA_URL_PATH)
	elif room == 'sandy lunchbox': url = __get_single_line(SANDBOX_URL_PATH)

        r = requests.post(url, json={"color":color,"message":message,"notify":notify,"message_format":message_format})

	return "OK"

### POSTS LUNCH RECOMMENDATION
def __post_lunch(room, day = datetime.datetime.today().weekday(), rest = __get_random_item(REST_PATH, LAST_REST_PATH), driver = __get_random_item(DRIVER_PATH)):

	msg = ""

	# monday, wednesday, friday
	if day in [0, 2, 4]:	msg = "(chef) Hello there children! Today we're going on a field trip to " + rest + " and " + driver + " is driving!"
	# tuesday
	elif day == 1:		msg = "Today for lunch is KNOWLEDGE (mindblown)"
	# thursday
	elif day == 3:		msg = "Today is LOGIC PUZZLE GROUP"

	# make post request
	return __post_to_hipchat(room, msg, "green", True, "text")

### POSTS LUNCH SUGGESTION TO HIPCHAT
def main(room):
	
	__post_lunch(room)

if __name__ == "__main__": main('sandy lunchbox')
