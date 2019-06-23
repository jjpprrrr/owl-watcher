#!/usr/bin/env python
# coding: utf-8

"""OWL Watcher.

Usage:
    owl-watcher.py [--open=<ot>] [--close=<ct>] [--mute]
    owl-watcher.py (-h | --help)
    owl-watcher.py --version

Options:
    -h --help       Show this screen.
    --version       Show version.
    --open=<ot>     How early to open the stream in seconds [default: 300].
    --close=<ct>    How late to close the stream in seconds [default: 1800].
    --mute          Enables automatically muting the stream upon opening.

"""

import os
import sys
import time
import datetime
import json
from sys import platform
from os.path import expanduser
from io import BytesIO
from urllib.request import urlopen
from lxml import html
from docopt import docopt
from zipfile import ZipFile
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from pyvirtualdisplay import Display

def main(arguments):
    # Download latest chromedriver
    download_chromedriver()

    # start virtual display
    disp = Display(visible=0, size=(1440, 900))
    disp.start()

    # Setup webdriver for proper platform
    if platform == "linux" or platform == "linux2":
        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=" + expanduser("~") + "/.config/google-chrome")
        #options.add_argument('--headless')
        options.add_argument('--mute-audio')
    elif platform == "darwin":
        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=" + expanduser("~") + "/Library/Application Support/Google/Chrome")
    elif platform == "win32":
        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=" + expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\User Data")
    else:
        print("Unsupported platform: %s" % platform)
        sys.exit(-1)

    # Get daily OWL schedule
    days = get_daily_start_end_times()

    # Process days in order
    for day in days:
        # Calculate open and close times for the day's stream
        openTime = day[0] - datetime.timedelta(0, int(arguments['--open']))
        closeTime = day[1] + datetime.timedelta(0, int(arguments['--close']))

        print('open time: ')
        print(openTime)
        print('close time: ')
        print(closeTime)
        print('current time: ')
        print(datetime.datetime.now())

        # Skip day if it is already over
        if closeTime <= datetime.datetime.now():
            continue

        # Check if too early to open stream
        if datetime.datetime.now() < openTime:
            # Calculate seconds until when to open stream
            waitTime = openTime - datetime.datetime.now()
            print('wait time: ')
            print(waitTime)
            waitSecs = waitTime.days * 86400 + waitTime.seconds

            # Sleep until time to open stream
            print('Too early for stream... Going to sleep...')
            time.sleep(waitSecs)

        # Open the stream
        print("Opening Overwatch League stream...")

        if platform == "linux" or platform == "linux2":
            driver = webdriver.Chrome('./chromedriver', chrome_options=options)
        elif platform == "darwin":
            driver = webdriver.Chrome('./chromedriver', chrome_options=options)
        elif platform == "win32":
            driver = webdriver.Chrome('./chromedriver.exe', chrome_options=options)
        else:
            print("Unsupported platform: %s" % platform)
            sys.exit(-1)

        driver.get("https://twitch.tv/overwatchleague")

        try:
            drops = driver.find_element_by_xpath('//span[@class="drops-campaign-details__drops-success tw-strong"]')
            print(drops)
        except:
            print('drop not found')


        # Mute stream if --muted argument was passed
        if bool(arguments['--mute']):
            # Get video element from page
            elem = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/main/div[2]/div[3]/div/div/div[2]/figure/div/div/div[1]/video')
            # Send PAGE_DOWN key to mute stream
            elem.send_keys(Keys.PAGE_DOWN)

        # Calculate seconds until when to close stream
        waitTime = closeTime - datetime.datetime.now()
        waitSecs = waitTime.days * 86400 + waitTime.seconds

        # Sleep until time to close stream
        time.sleep(waitSecs)

        # Close the stream
        print("Closing Overwatch League stream...")
        driver.close()

    sys.exit(0)

# Downloads latest version of ChromeDriver,
# which is required to control a Google Chrome session
def download_chromedriver():
    # Determine latest version of ChromeDriver
    page = urlopen('https://sites.google.com/a/chromium.org/chromedriver/downloads')
    tree = html.fromstring(page.read())
    version = str(tree.xpath('//*[@id="sites-canvas-main-content"]/table/tbody/tr/td/div/h2/b/a/text()')[0][13:])
    downloadPath = "https://chromedriver.storage.googleapis.com/" + str(version) + "/"

    # Download and unzip chromedriver
    if platform == "linux" or platform == "linux2":
        downloadPath += "chromedriver_linux64.zip"
        zipresp = urlopen(downloadPath)
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall('./')

        # enable execution of the binary
        os.chmod('./chromedriver', 755)
    elif platform == "darwin":
        downloadPath += "chromedriver_mac64.zip"
        zipresp = urlopen(downloadPath)
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall('./')

        # enable execution of the binary
        os.chmod('./chromedriver', 755)
    elif platform == "win32":
        downloadPath += "chromedriver_win32.zip"
        zipresp = urlopen(downloadPath)
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall('./')
    return

# Returns a list of datetime pairs to represent the start
# and end times for OWL matches for each day
def get_daily_start_end_times():
    # Fetch the latest schedule from the Overwatch League API
    request = urlopen('https://api.overwatchleague.com/schedule')
    fullSchedule = json.loads(request.read())

    day = None
    days = []

    # Loop through each stage
    for stage in fullSchedule["data"]["stages"]:
        # Loop through each match
        for match in stage["matches"]:
            # Only process non-completed matches
            if match["state"] == "PENDING":
                # Get match start and end times
                startTime = datetime.datetime.fromtimestamp(match["startDateTS"]/1000)
                endTime = datetime.datetime.fromtimestamp(match["endDateTS"]/1000)
                
                # Update daily start and end times
                if day is None:
                    day = [ startTime, endTime ]
                else:
                    # Calucate time difference in hours between match start time 
                    # and existing day start time
                    diffTime = startTime - day[0]
                    hours = diffTime.days * 24 + diffTime.seconds // 3600

                    # Consider match as starting on the next day if it starts at least
                    # 12 hours after the start of the previous day.
                    if hours >= 12:
                        # Store day times and start new day
                        days.append(day)
                        day = [ startTime, endTime ]
                    else:
                        # Update end time for the day
                        day[1] = endTime

    # Return daily info
    print(days)
    return days
                
if __name__ == '__main__':
    arguments = docopt(__doc__, version='OWL Watcher 0.1')
    main(arguments)
