import os, random, datetime, requests

REST_PATH = '/var/www/html/lunchbot/restaurants.txt'
DRIVER_PATH = '/var/www/html/lunchbot/drivers.txt'
LAST_REST_PATH = '/var/www/html/lunchbot/driver_last.txt'
LAST_DRIVER_PATH = '/var/www/html/lunchbot/restaurant_last.txt'
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

		if len(msg_arr) >= 4:	return __add_item(msg_arr[2], ' '.join(msg_arr[3:]), room)
		else:			return __add_item("no", "arguments", room)

	# remove command requires 2 arguments (list name, list item)
	elif msg_arr[1] == "remove":

		if len(msg_arr) >= 4:	return __remove_item(msg_arr[2], ' '.join(msg_arr[3:]), room)
		else:			return __remove_item("no", "arguments", room)

	# gross command requires 0 arguments
	elif msg_arr[1] == "gross":	return __gross("place holder", room)

	else: return __print_help(room)

def __get_single_line(path):
	try:
		with open(path, 'r') as f:
			return (f.readline()).rstrip()
	except:
		return None

def __overwrite_single_line(path, line):
	try:
		with open(path, 'w') as f:
			f.write(line)
	except:
		pass

### ADD ITEM TO LIST
def __add_item(name, item, room):

	path = ""

	if name.lower() == "restaurant": path = REST_PATH
	elif name.lower() == "driver": path = DRIVER_PATH
	else: return __post_to_hipchat(room, 'Proper usage: /lunchbot add [restaurant, driver] [name of restaurant/driver]', 'gray')
	
	return __post_to_hipchat(room, 'TODO: add ' + item + ' to ' + path, 'purple')

### REMOVE ITEM FROM LIST
def __remove_item(name, item, room):

	path = ""	

	if name.lower() == "restaurant": path = REST_PATH
	elif name.lower() == "driver": path = DRIVER_PATH
	else: return __post_to_hipchat(room, 'Proper usage: /lunchbot remove [restaurant, driver] [name of restaurant/driver]', 'gray')

	return __post_to_hipchat(room, 'TODO: add ' + item + ' to ' + path, 'purple')

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
def __get_random_item(path, last_item_file=None, save_results=False):

	f = open(path, 'r')

	arr = []

	#Check for previous item
	last_item = __get_single_line(last_item_file)

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
	__overwrite_single_line(last_item_file, choice[0])

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
