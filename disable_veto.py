import lunchbot, datetime

def main():

	day = datetime.datetime.today().weekday()

	if day in [0, 2, 4]:
		lunchbot.__set_vote_enable(False)
		lunchbot.__post_to_hipchat('Rogue One', 'It has been decided! Go forth and lunch..', 'green')

if __name__ == "__main__": main()
