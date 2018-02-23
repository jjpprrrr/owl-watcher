#!/usr/bin/env python
# coding: utf-8

"""OWL Watcher.

Usage:
    owl-watcher.py [--open=<ot>] [--close=<ct>] [--update=<ut>] [--mute]
    owl-watcher.py (-h | --help)
    owl-watcher.py --version

Options:
    -h --help       Show this screen.
    --version       Show version.
    --open=<ot>     How early to open the stream in seconds [default: 300].
    --close=<ct>    How late to close the stream in seconds [default: 1800].
    --update=<ut>   How often to check whether to open or close the stream in seconds [default: 300].
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

def main(arguments):
    # Download latest chromedriver
    download_chromedriver()

    # Set webdriver for proper platform
    if platform == "linux" or platform == "linux2":
        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=" + expanduser("~") + "/.config/google-chrome")
        driver = webdriver.Chrome('./chromedriver', chrome_options=options)
    elif platform == "darwin":
        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=" + expanduser("~") + "/Library/Application Support/Google/Chrome")
        driver = webdriver.Chrome('./chromedriver', chrome_options=options)
    elif platform == "win32":
        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=" + expanduser("~") + "\AppData\Local\Google\Chrome\User Data")
        driver = webdriver.Chrome('./chromedriver.exe', chrome_options=options)

    # Get daily OWL schedule
    days = get_daily_start_end_times()

    # Loop
    while True:
        # Test if time to open stream has passed
        if days[0][0] - datetime.timedelta(0, int(arguments['--open'])) < datetime.datetime.now():
            driver.get("https://twitch.tv/overwatchleague")
            assert "OverwatchLeague" in driver.title

        # Test if time to close stream has passed
        elif days[0][1] + datetime.timedelta(0, int(arguments['--close'])) < datetime.datetime.now():
            del days[0]
            driver.close()

        # Sleep for specified update interval
        time.sleep(float(arguments['--update']))

    return

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
    return days
                
if __name__ == '__main__':
    arguments = docopt(__doc__, version='OWL Watcher 0.1')
    main(arguments)