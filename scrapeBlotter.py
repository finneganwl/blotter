from lxml import etree
import requests, bs4, csv

# column may have children tags, e.g. <td><b>text</b><td>
# but if column has <br> tag, just ignore it
def getTextRecur(item):
	if len(list(item)) > 0:
		if item[0].tag == 'br':
			return item.text
		for child in item:
			return getTextRecur(child)
	else:
		return item.text

months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

def fetchAndScrape(url):
	res = requests.get(url)
	if res.status_code == requests.codes.ok:
		parsed = bs4.BeautifulSoup(res.text,"html.parser")
		s = str(parsed.find_all("table")[0])

		table = etree.HTML(s).find("body/table")
		in_rows = iter(table)
		out_row = []
		out_i = 0
		for in_row in in_rows:
			header = getTextRecur(in_row[0])
			value = getTextRecur(in_row[1])
			if value != u'\xc2\xa0': # skip blanks
				if out_i < 9:
					# common name was added for only some months, leave blank if not present
					if out_i == 5 and header != 'Common Name:': 
						out_row.append('')
						out_i += 1
					out_row.append(value)
					out_i += 1
				else:
					writer.writerow(out_row)
					out_row = [value]
					out_i = 1
	else:
		print 'Error fetching', url


with open('blotter.csv', 'wb') as csvfile:
	writer = csv.writer(csvfile)
	# http://www.northwestern.edu/up/blotter/blotter_ev-mar2006.html
	for year in range(2012,2017+1):
		for month in months:
			print month, str(year)
			url = 'http://www.northwestern.edu/up/blotter/blotter_ev-' + month + str(year) + '.html'
			fetchAndScrape(url)
	fetchAndScrape('http://www.northwestern.edu/up/blotter/blotter_ev.html') # current month
    