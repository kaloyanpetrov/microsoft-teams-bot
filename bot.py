import re
import sqlite3
import time
from datetime import datetime
from os import path
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

opt = Options()
opt.add_argument("--disable-infobars")
opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")
opt.add_argument("--start-maximized")
# Pass the argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", {
	"profile.default_content_setting_values.media_stream_mic": 1,
	"profile.default_content_setting_values.media_stream_camera": 1,
	"profile.default_content_setting_values.geolocation": 1,
	"profile.default_content_setting_values.notifications": 1
})

driver = None
URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?response_type=id_token&scope=openid%20profile&client_id=5e3ce6c0-2b1f-4285-8d4b-75ee78787346&redirect_uri=https%3A%2F%2Fteams.microsoft.com%2Fgo&state=eyJpZCI6ImVhMjNhNGQ1LTc3YzMtNGIyMC1hMGIzLTkzODY0NGE4MzY2OCIsInRzIjoxNjM4ODc5MjUwLCJtZXRob2QiOiJyZWRpcmVjdEludGVyYWN0aW9uIn0%3D&nonce=6ce60d0f-a7a3-45b7-ac40-aa4e78aea00b&client_info=1&x-client-SKU=MSAL.JS&x-client-Ver=1.3.4&client-request-id=5f95876f-139f-42d2-a841-a579aa77564f&response_mode=fragment"

# put your teams credentials here
info = {'email': 'kp62013275@edu.mon.bg', 'passwd': 'sistemata.ne.struva1111!'}


def login():
	global driver
	# login required
	WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="i0116"]'))).send_keys(info['email'])  # Enter email
	driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()  # Click next
	time.sleep(2)
	WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="i0118"]'))).send_keys(info['passwd'])  # Enter pass
	driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()  # Sign in
	time.sleep(2)
	driver.find_element_by_css_selector('div.table').click()
	print("--- LOGGGING SUCCESFULL")


def create_db():
	conn = sqlite3.connect('timetable.db')
	c = conn.cursor()
	# Create table
	c.execute('''CREATE TABLE timetable(class text, start_time text, end_time text, day text)''')
	conn.commit()
	conn.close()
	print("Created timetable Database")


def validate_input(regex, inp):
	if not re.match(regex, inp):
		return False
	return True


def validate_day(inp):
	days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

	if inp.lower() in days:
		return True
	else:
		return False


def add_timetable():
	if not (path.exists("timetable.db")):
		create_db()
	op = int(input("1. Add class\n2. Done adding\nEnter option : "))
	while op == 1:
		name = input("Enter class name : ")
		start_time = input("Enter class start time in 24 hour format: (HH:MM) ")
		while not validate_input("\d\d:\d\d", start_time):
			print("Invalid input, try again")
			start_time = input("Enter class start time in 24 hour format: (HH:MM) ")

		end_time = input("Enter class end time in 24 hour format: (HH:MM) ")
		while not validate_input("\d\d:\d\d", end_time):
			print("Invalid input, try again")
			end_time = input("Enter class end time in 24 hour format: (HH:MM) ")

		day = input("Enter day (Monday/Tuesday/Wednesday..etc) : ")
		while not (validate_day(day.strip())):
			print("Invalid input, try again")
			end_time = input("Enter day (Monday/Tuesday/Wednesday..etc) : ")

		conn = sqlite3.connect('timetable.db')
		c = conn.cursor()

		# Insert a row of data
		c.execute(f"INSERT INTO timetable VALUES {name, start_time, end_time, day}")

		conn.commit()
		conn.close()

		print("Class added to database\n")

		op = int(input("1. Add class\n2. Done adding\nEnter option : "))


def view_timetable():
	conn = sqlite3.connect('timetable.db')
	c = conn.cursor()
	for row in c.execute('SELECT * FROM timetable'):
		print(row)
	conn.close()


def join_class(class_name, start_time, end_time):
	global driver

	try_time = int(start_time.split(":")[1]) + 15
	try_time = start_time.split(":")[0] + ":" + str(try_time)

	time.sleep(2)

	classes_available = driver.find_elements_by_class_name("name-channel-type")

	for i in classes_available:
		if class_name.lower() in i.get_attribute('innerHTML').lower():
			print(f"--- JOINING CLASS - {class_name}")
			i.click()
			break

	time.sleep(3)

	try:
		joinbtn = driver.find_element_by_class_name("ts-calling-join-button")
		joinbtn.click()

	except:
		# join button not found
		# refresh every minute until found
		k = 1
		while k <= 15:
			print("Join button not found, trying again")
			time.sleep(60)
			driver.refresh()
			join_class(class_name, start_time, end_time)
			# schedule.every(1).minutes.do(join_class,class_name,start_time,end_time)
			k += 1
		print("Seems like there is no class today.")

	time.sleep(3)
	webcam = driver.find_element_by_xpath(
		'//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[2]/toggle-button[1]/div/button/span[1]')
	if webcam.get_attribute('title') == 'Turn camera off':
		webcam.click()
	time.sleep(1)

	microphone = driver.find_element_by_xpath('//*[@id="preJoinAudioButton"]/div/button/span[1]')
	if (microphone.get_attribute('title') == 'Mute microphone'):
		microphone.click()

	time.sleep(1)
	joinnowbtn = driver.find_element_by_xpath(
		'//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[1]/div/div/button')
	joinnowbtn.click()

	# now schedule leaving class
	tmp = "%H:%M"

	class_running_time = datetime.strptime(end_time, tmp) - datetime.strptime(start_time, tmp)

	time.sleep(class_running_time.seconds)

	driver.find_element_by_class_name("ts-calling-screen").click()

	driver.find_element_by_xpath('//*[@id="teams-app-bar"]/ul/li[3]').click()  # come back to homepage
	time.sleep(1)

	driver.find_element_by_xpath('//*[@id="hangup-button"]').click()
	print("--- CLASS LEFT")


def start_browser():
	global driver
	driver = webdriver.Chrome(options=opt, service_log_path='NUL')

	driver.get(URL)

	WebDriverWait(driver, 10000).until(ec.visibility_of_element_located((By.TAG_NAME, 'body')))

	if "login.microsoftonline.com" in driver.current_url:
		login()


def sched():
	conn = sqlite3.connect('timetable.db')
	c = conn.cursor()
	for row in c.execute('SELECT * FROM timetable'):
		# schedule all classes
		name = row[0]
		start_time = row[1]
		end_time = row[2]
		day = row[3]

		if day.lower() == "monday":
			schedule.every().monday.at(start_time).do(join_class, name, start_time, end_time)
			print(f"Scheduled class {name} on {day} at {start_time}")
		if day.lower() == "tuesday":
			schedule.every().tuesday.at(start_time).do(join_class, name, start_time, end_time)
			print(f"Scheduled class {name} on {day} at {start_time}")
		if day.lower() == "wednesday":
			schedule.every().wednesday.at(start_time).do(join_class, name, start_time, end_time)
			print(f"Scheduled class {name} on {day} at {start_time}")
		if day.lower() == "thursday":
			schedule.every().thursday.at(start_time).do(join_class, name, start_time, end_time)
			print(f"Scheduled class {name} on {day} at {start_time}")
		if day.lower() == "friday":
			schedule.every().friday.at(start_time).do(join_class, name, start_time, end_time)
			print(f"Scheduled class {name} on {day} at {start_time}")
		if day.lower() == "saturday":
			schedule.every().saturday.at(start_time).do(join_class, name, start_time, end_time)
			print(f"Scheduled class {name} on {day} at {start_time}")
		if day.lower() == "sunday":
			schedule.every().sunday.at(start_time).do(join_class, name, start_time, end_time)
			print(f"Scheduled class {name} on {day} at {start_time}")

	# Start browser
	start_browser()
	while True:
		# Checks whether a scheduled task
		# is pending to run or not
		schedule.run_pending()
		time.sleep(1)


if __name__ == "__main__":
	op = int(input("1. Modify Timetable\n2. View Timetable\n3. Start Bot\nEnter option : "))

	if op == 1:
		add_timetable()
	if op == 2:
		view_timetable()
	if op == 3:
		sched()
