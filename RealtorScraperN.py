import csv
from bs4 import BeautifulSoup
import requests
import time

def write_row(agent_full):
	with open('results.csv', 'a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow([agent_full["agent_name"], agent_full["agent_agency"], agent_full["agent_location"], agent_full["agent_page_link"], agent_full["agent_phone_number"], agent_full["agent_picture"]])
		file.close()

def get_result_urls():
	urls = []
	with open("results.csv", "r") as file:
		reader = csv.reader(file)
		next(reader, None)
		for row in reader:
			urls.append(row[3])
	file.close()
	return(urls)

def write_page_number(page_info):
	with open("pagenumber.txt", "w") as file:
		file.write(str(page_info))
		file.close()

def get_page_info():
	with open("pagenumber.txt", "r") as file:
		page_info = file.read()
		file.close()
	return(page_info.split(","))

finished = False
base_url = 'https://www.har.com/HOUSTON/real_estate_agents?search_type=member&officecity=HOUSTON&page='
page_info = get_page_info()
page_number = int(page_info[0])
agent_number = int(page_info[1])
agent_urls = []
agent_urls = agent_urls + get_result_urls()

while finished == False:
	time.sleep(0.1)
	print(f"Starting page number: {page_number}")
	response = requests.get(base_url+str(page_number))
	soup = BeautifulSoup(response.content, "lxml")
	try:
		page_agents = soup.findAll('div', {'class': 'agent_box'})
	except:
		print("Finished.")
	for agent in page_agents:
		agent_number = agent_number + 1
		write_page_number(f"{page_number}, {agent_number}")
		agent_info = agent.find('div', {'class': 'ab_info'})
		agent_info_name_agency = agent_info.findAll('a')
		agent_picture_string = agent.find('a', {'class': 'ab_img_link'}).get('style')
		agent_picture = agent_picture_string.split("(")[1].split(")")[0]
		agent_name = agent_info_name_agency[0].getText()
		agent_agency = agent_info_name_agency[1].getText()
		agent_location = agent_info.find('div').getText()
		agent_page_link = f"https://www.har.com{agent_info_name_agency[0]['href']}"
		agent_page_response = requests.get(agent_page_link)
		agent_page_soup = BeautifulSoup(agent_page_response.content, "lxml")
		try:
			agent_phone_number_string = agent_page_soup.find(id='har_agentphone').get('onclick')
			agent_phone_number = agent_phone_number_string.split(",")[1].strip("'")
		except:
			agent_phone_number = "N/A"
		agent_full = {"agent_name":agent_name, "agent_agency":agent_agency, "agent_location":agent_location, "agent_page_link":agent_page_link, "agent_phone_number":agent_phone_number, "agent_picture":agent_picture}
		if agent_page_link in agent_urls:
			print(f"Skipped agent {agent_name}: already in results.")
			continue
		else:
			write_row(agent_full)
	agent_number = 0
	page_number = page_number + 1
	write_page_number(f"{page_number}, {agent_number}")



