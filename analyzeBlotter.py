import re, csv, json, requests, dateutil.parser, datetime, config

topics = ['Substances', 'Noise']
topicKeywords = {'Substances': ['Alcohol', 'Cannabis', 'Consumption', 'Drug', 'Drunkeness', 'Liquor', 'Possession', 'Fraudulent ID'], 'Noise' : ['Noise', 'False Alarm Activation', 'Fire']}
regexes = {topic: [r'.*' + keyword + r'.*' for keyword in topicKeywords[topic]] for topic in topics}
locations = {}

NUM_MONTHS = 65
hourCounts = [0 for i in range(24)]
dayCounts = [0 for i in range(7)]
monthCounts = [0 for i in range(12)]
yearCounts = [0 for i in range(6)]
monthLine = [0 for i in range(NUM_MONTHS)]

MONTHS_WO_STUDENTS = [2, 5, 6, 7, 11] # zero indexed, 11 is december
NUM_YEARS = 6
monthComparison = [[0 for j in range(12)] for i in range(NUM_YEARS)]
yesStudents = [0 for i in range(NUM_YEARS)]
noStudents = [0 for i in range(NUM_YEARS)]

WEEKENDS = [4, 5]
weekdayComparison = [[0 for j in range(7)] for i in range(NUM_MONTHS)]
weekends = [0 for i in range(NUM_MONTHS)]
weekdays = [0 for i in range(NUM_MONTHS)]

FOSTER_LAT = 42.053846 # divides north and south
north = [0 for i in range(NUM_MONTHS)]
south = [0 for i in range(NUM_MONTHS)]

#Dillo 2017 (5/20), Dillo 2016 (5/21). Dillo 2015 (5/30), Dillo 2014 (5/31), Dillo 2013 (6/1), Dillo 2012 (5/26)
DILLOS = [dateutil.parser.parse(date, fuzzy = True) for date in ['May 20 2017', 'May 21 2016', 'May 30 2015', 'May 31 2014', 'June 1 2013', 'May 26 2012']]
dillos = [0 for i in range(NUM_YEARS)]

API_KEY = config.GEOCODING_API_KEY
ACTUALLY_QUERY = False # don't wanna waste those queries
def getCoords(location):
	# returns [lat, lng], [0, 0] if not found
	if ACTUALLY_QUERY:
		locQuery = "+".join(location.split())
		url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + locQuery + '+Evanston+IL&key=' + API_KEY
		res = requests.get(url)
		if res.status_code == requests.codes.ok:
			parsed = json.loads(res.text)
			if parsed['status'] == 'OK' and location != 'NA': #NA, Evanston is a valid address
				lat = parsed['results'][0]['geometry']['location']['lat']
				lng = parsed['results'][0]['geometry']['location']['lng']
				return [lat, lng]
			else:
				print 'ERROR in Google Geocoding Response:'
				print parsed['status']
				print 'for query:', locQuery
		else:
			print 'Error fetching url:', url
	return [0, 0]

EARLIEST_DATE = dateutil.parser.parse('Jan 01 2012 12:00:01am', fuzzy = True)
def monthsSinceStart(dt):
    return (dt.year - EARLIEST_DATE.year) * 12 + dt.month - EARLIEST_DATE.month

dorms = {}
dormsRegression = [[0, 0, 0, 0] for i in range(NUM_MONTHS)] # N-weekend, S-weekend, N-weekday, S-weekday
with open('dorms.csv', 'r') as dormsFile:
	next(dormsFile)  # skip header line
	dormsReader = csv.reader(dormsFile)
	for row in dormsReader:
		dorms[row[0]] = {'isNorth': float(row[2]) > FOSTER_LAT, 'name': row[1]}


with open('blotter.csv', 'r') as csvfile:
	reader = csv.reader(csvfile)
	for row in reader:
		dt = dateutil.parser.parse(row[2].replace(':000',''), fuzzy = True)
		month = monthsSinceStart(dt) # number of months since EARLIEST DATE
		if month >= 0: # some crimes backdated before start of experimental period
			# count total occurances as function of different time periods
			hourCounts[dt.hour] += 1
			dayCounts[dt.weekday()] += 1
			monthCounts[month % 12] += 1
			yearCounts[month / 12] += 1
			monthLine[month] += 1

			# months in which students are on campus
			monthComparison[month / 12][month % 12] += 1
			if (month % 12) in MONTHS_WO_STUDENTS:
				noStudents[month / 12] += 1
			else:
				yesStudents[month / 12] += 1

			# weekends
			weekdayComparison[month][dt.weekday()] += 1
			if dt.weekday() in WEEKENDS:
				weekends[month] += 1
				isWeekday = False
			else:
				weekdays[month] += 1
				isWeekday = True

			# locations
			location = row[4]
			if location in locations:
				locations[location]['total'] += 1
				if locations[location]['name'] == '':
					locations[location]['name'] = row[5]
			else:
				locations[location] = dict(zip(topics, [0 for topic in topics]))
				locations[location]['total'] = 1
				locations[location]['name'] = row[5]
				coords = getCoords(location)
				locations[location]['lat'] = coords[0]
				locations[location]['lng'] = coords[1]

			# north vs south
			if locations[location]['lat'] != 0:
				if locations[location]['lat'] > FOSTER_LAT:
					north[month] += 1
				else:
					south[month] += 1

			if location in dorms:
				if dorms[location]['isNorth']:
					if isWeekday:
						dormsRegression[month][2] += 1
					else:
						dormsRegression[month][0] += 1
				else:
					if isWeekday:
						dormsRegression[month][3] += 1
					else:
						dormsRegression[month][1] += 1



			# dillo
			if datetime.datetime(dt.year, dt.month, dt.day, 0, 0) in DILLOS:
				dillos[month / 12] += 1

			# keyword matches for topics
			for topic in topics:
				for i, keyword in enumerate(topicKeywords[topic]):
					searchObj = re.search(regexes[topic][i], row[6], re.IGNORECASE)
					searchObj2 = re.search(regexes[topic][i], row[7], re.IGNORECASE)
					if searchObj or searchObj2:
						locations[location][topic] += 1
		
		#a = raw_input('enter to continue')
		#if a == 'break':
		#	break

with open('outputs/counts.csv', 'w') as countsFile:
	countsWriter = csv.writer(countsFile)
	countsWriter.writerow(['Hours after midnight'])
	countsWriter.writerow([i for i in range(24)])
	countsWriter.writerow(hourCounts)
	countsWriter.writerow([''])

	countsWriter.writerow(['Days after Monday'])
	countsWriter.writerow([i for i in range(7)])
	countsWriter.writerow(dayCounts)
	countsWriter.writerow([''])

	countsWriter.writerow(['Months after January'])
	countsWriter.writerow([i for i in range(12)])
	countsWriter.writerow(monthCounts)
	countsWriter.writerow([''])

	countsWriter.writerow(['Years after 2012'])
	countsWriter.writerow([i for i in range(NUM_YEARS)])
	countsWriter.writerow(yearCounts)
	countsWriter.writerow([''])

	countsWriter.writerow(['Individual months after January 2012'])
	countsWriter.writerow([i for i in range(NUM_MONTHS)])
	countsWriter.writerow(monthLine)


if ACTUALLY_QUERY:
	with open('outputs/northSouth.csv', 'w') as northSouthFile:
		northSouthWriter = csv.writer(northSouthFile)
		northSouthWriter.writerow(['Months since Jan 2012', 'Number of Occurances North of Foster', 'Number of Occurances South of Foster'])
		for i in range(NUM_MONTHS):
			northSouthWriter.writerow([i, north[i], south[i]])

with open('outputs/studentsAway.csv', 'w') as studentsAwayFile:
	studentAwayWriter = csv.writer(studentsAwayFile)
	studentAwayWriter.writerow(['Years since 2012', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec','Number of Occurances during Months that Students are Away (' + str(len(MONTHS_WO_STUDENTS)) + ' months total)', 'Number of Occurances during Months that Students are Here (' + str(12 - len(MONTHS_WO_STUDENTS)) + ' months total)'])
	for i in range(NUM_YEARS):
		studentAwayWriter.writerow([i] + monthComparison[i] + [noStudents[i], yesStudents[i]])

with open('outputs/weekends.csv', 'w') as weekendsFile:
	weekendsWriter = csv.writer(weekendsFile)
	weekendsWriter.writerow(['Months since Jan 2012', 'Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun', 'Number of Occurances on Weekends (' + str(len(WEEKENDS)) + ' days total)', 'Number of Occurances on Weekdays (' + str(7 - len(WEEKENDS)) + ' days total)'])
	for i in range(NUM_MONTHS):
		weekendsWriter.writerow([i] + weekdayComparison[i] + [weekends[i], weekdays[i]])

if ACTUALLY_QUERY:
	with open('outputs/locations.csv', 'w') as locationsFile:
		locationsWriter = csv.writer(locationsFile)
		locationsWriter.writerow(['Address', 'Common Name', 'Latitude', 'Longitude', 'Total'] + [topic for topic in topics])
		for location in locations:
			row = [location, locations[location]['name'], locations[location]['lat'], locations[location]['lng'], locations[location]['total']] + [locations[location][topic] for topic in topics]
			locationsWriter.writerow(row)

with open('outputs/dillos.csv', 'w') as dillosFile:
	dillosWriter = csv.writer(dillosFile)
	dillosWriter.writerow(['Years since 2012', 'Number of Occurances on Dillo Day'])
	for i in range(NUM_YEARS):
		dillosWriter.writerow([i, dillos[i]])

with open('outputs/dormsRegression.csv', 'w') as dormsRegressionFile:
	dormsRegressionWriter = csv.writer(dormsRegressionFile)
	dormsRegressionWriter.writerow(['Months since Jan 2012', 'North, Weekends', 'South, Weekends', 'North, Weekdays', 'South, Weekdays', 'Students Present?'])
	for i in range(NUM_MONTHS):
		dormsRegressionWriter.writerow([i] + dormsRegression[i] + [i % 12 not in MONTHS_WO_STUDENTS])
