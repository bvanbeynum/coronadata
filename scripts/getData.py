import pymongo
import requests
import json
import re
import datetime
import sys

client = pymongo.MongoClient("mongodb://corona:covid19@172.17.0.2:27017/?authSource=corona")
db = client["corona"]
countryDB = db["countries"]

countriesToday = countryDB.count_documents({ "date": datetime.datetime.today().strftime("%Y-%m-%d") })

if countriesToday > 0:
	print(datetime.datetime.today().strftime("%Y-%m-%d") + " - " + str(countriesToday) + " countries already loaded for today")
	sys.exit()

def LoadState(url):
	response = requests.get(url)
	data = json.loads(response.text)
	html = data["parse"]["text"]["*"]
	
	match = re.search("<tbody", html, flags = re.IGNORECASE)
	start = match.span()[0]
	match = re.search("</tbody>", html, flags = re.IGNORECASE)
	end = match.span()[1]
	
	dataTable = html[start:end]
	rows = re.split("<tr", dataTable, flags = re.IGNORECASE)
	
	stateData = []
	
	for index, row in enumerate(rows):
		if re.search("_county,", row, flags = re.IGNORECASE) is not None:
			cells = re.split("<t[h|d]", row, flags = re.IGNORECASE)
			
			match = re.search(">([^<]+)<", cells[1], flags = re.IGNORECASE)
			county = match.group(1).replace("&amp;", "&")
			
			match = re.search(">([\d,]+)[\r\n ]*<", cells[2], flags = re.IGNORECASE)
			if match is not None:
				cases = int(match.group(1).replace(",", ""))
			else:
				cases = -1
			
			match = re.search(">([\d,]+)[\r\n ]*<", cells[3], flags = re.IGNORECASE)
			if match is not None:
				deaths = int(match.group(1).replace(",", ""))
			else:
				deaths = -1
			
			stateData.append({ "date": datetime.datetime.today().strftime("%Y-%m-%d"), "county": county, "cases": cases, "deaths": deaths })
	
	return stateData

# ************************** Load SC

scData = LoadState("https://en.wikipedia.org/w/api.php?action=parse&prop=text&format=json&page=Template:COVID-19_pandemic_data/South_Carolina_medical_cases_by_county")
ncData = LoadState("https://en.wikipedia.org/w/api.php?action=parse&prop=text&format=json&page=COVID-19_pandemic_in_North_Carolina&section=6")
waData = LoadState("https://en.wikipedia.org/w/api.php?action=parse&prop=text&format=json&page=COVID-19_pandemic_in_Washington_(state)")

# ************************** Load States

response = requests.get("https://en.wikipedia.org/w/api.php?action=parse&prop=text&format=json&page=Template:COVID-19_pandemic_data/United_States_medical_cases_by_state&section=0")
data = json.loads(response.text)
html = data["parse"]["text"]["*"]

match = re.search("<tbody", html, flags = re.IGNORECASE)
start = match.span()[0]
match = re.search("</tbody>", html, flags = re.IGNORECASE)
end = match.span()[1]

dataTable = html[start:end]
rows = re.split("<tr", dataTable, flags = re.IGNORECASE)

stateData = []

for index, row in enumerate(rows):
	if re.search("flag_of", row, flags = re.IGNORECASE) is not None:
		cells = re.split("<t[h|d]", row, flags = re.IGNORECASE)
		
		match = re.search(">([^<]+)<", cells[2], flags = re.IGNORECASE)
		state = match.group(1).replace("&amp;", "&")
		
		match = re.search(">([\d,]+)[\r\n ]*<", cells[3], flags = re.IGNORECASE)
		if match is not None:
			cases = int(match.group(1).replace(",", ""))
		else:
			cases = -1
		
		match = re.search(">([\d,]+)[\r\n ]*<", cells[4], flags = re.IGNORECASE)
		if match is not None:
			deaths = int(match.group(1).replace(",", ""))
		else:
			deaths = -1
		
		match = re.search(">([\d,]+)[\r\n ]*<", cells[5], flags = re.IGNORECASE)
		if match is not None:
			recovered = int(match.group(1).replace(",", ""))
		else:
			recovered = -1
		
		match = re.search(">([\d,]+)[\r\n ]*<", cells[6], flags = re.IGNORECASE)
		if match is not None:
			hospitalized = int(match.group(1).replace(",", ""))
		else:
			hospitalized = -1
		
		stateData.append({ "date": datetime.datetime.today().strftime("%Y-%m-%d"), "state": state, "cases": cases, "deaths": deaths, "recovered": recovered, "hospitalized": hospitalized })

# ************************** Load Countries

response = requests.get("https://en.wikipedia.org/w/api.php?action=parse&prop=text&format=json&page=COVID-19_pandemic_by_country_and_territory&section=1")
data = json.loads(response.text)
html = data["parse"]["text"]["*"]

match = re.search("<tbody", html, flags = re.IGNORECASE)
start = match.span()[0]
match = re.search("</tbody>", html, flags = re.IGNORECASE)
end = match.span()[1]

dataTable = html[start:end]
rows = re.split("<tr", dataTable, flags = re.IGNORECASE)

countryData = []

for index, row in enumerate(rows):
	
	if re.search("Flag_of", row, flags = re.IGNORECASE) is not None:
		cells = re.split("<t[h|d]", row, flags = re.IGNORECASE)

		match = re.search(">([^<]+)<", cells[2], flags = re.IGNORECASE)
		country = match.group(1).replace("&amp;", "&")

		match = re.search(">([\d,]+)[\n\r ]*<", cells[3], flags = re.IGNORECASE)
		if match is not None:
			cases = int(match.group(1).replace(",", ""))
		else:
			cases = -1
		
		match = re.search(">([\d,]+)[\n\r ]*<", cells[4], flags = re.IGNORECASE)
		if match is not None:
			deaths = int(match.group(1).replace(",", ""))
		else:
			deaths = -1
		
		match = re.search(">([\d,]+)[\n\r ]*<", cells[5], flags = re.IGNORECASE)
		if match is not None:
			recovered = int(match.group(1).replace(",", ""))
		else:
			recovered = -1
		
		countryData.append({ "date": datetime.datetime.today().strftime("%Y-%m-%d"), "country": country, "cases": cases, "deaths": deaths, "recovered": recovered})

client = pymongo.MongoClient("mongodb://corona:covid19@172.17.0.2:27017/?authSource=corona")
db = client["corona"]
	
if len(countryData) > 0:
	countryDB = db["countries"]
	countryDB.insert_many(countryData)
	
if len(stateData) > 0:
	stateDB = db["states"]
	stateDB.insert_many(stateData)

if len(scData) > 0:
	scDB = db["sc"]
	scDB.insert_many(scData)

if len(ncData) > 0:
	ncDB = db["nc"]
	ncDB.insert_many(ncData)

if len(waData) > 0:
	waDB = db["wa"]
	waDB.insert_many(waData)

print(datetime.datetime.today().strftime("%Y-%m-%d") + " - country: " + str(len(countryData)) + ", state: " + str(len(scData)) + ", SC: " + str(len(countryData)) + ", NC: " + str(len(ncData)) + ", WA: " + str(len(waData)))
