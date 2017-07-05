import csv

dorms = {}
with open('dorms.csv', 'r') as dormsFile:
	next(dormsFile)  # skip header line
	dormsReader = csv.reader(dormsFile)
	for row in dormsReader:
		dorms[row[0]] = True;

output = []
with open('outputs/locations.csv', 'r') as locationsFile:
	next(locationsFile)  # skip header line
	locationsReader = csv.reader(locationsFile)
	for row in locationsReader:
		if row[0] in dorms:
			output.append(row)

with open('outputs/dormsCount.csv', 'w') as dormsCountFile:
	dormsCountWriter = csv.writer(dormsCountFile)
	dormsCountWriter.writerow(['Address', 'Name', 'Latitude', 'Longitude', 'Total', 'Substances', 'Noise'])
	for row in output:
		dormsCountWriter.writerow(row)
