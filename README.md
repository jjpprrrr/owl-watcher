# OWL Watcher

OWL Watcher is meant to run in the background and automatically opens the official Overwatch League live stream on [Twitch.tv](https://twitch.tv) shortly before the first match of the day is supposed to start. 

This can be a good method to collect viewership rewards such as in-game Overwatch League Tokens (information available [here](https://overwatchleague.com/en-us/news/21497938/watch-overwatch-league-get-league-tokens)).

The program uses the offical [Overwatch League API](https://api.overwatchleague.com) to fetch the offical schedule. This schedule is fetched on launch of the program to ensure it uses the latest version of the schedule.

Through optional arguments that can be passed to the program, the user can control how early before a scheduled match the stream open and enable automatically muting the stream upon opening.

## Requirements

* Google Chrome
* Python 3.6+
* The following Pip packages:
  * docopt
  * lxml
  * selenium

## Setup and Usage

Clone or download the repo as a zip and extract it to its own folder.

Ensure that you are logged into [Twitch.tv](https://twitch.tv) on Google Chrome with an account linked to a Battle.net account.

Install the required Pip packages:

```
$ pip install docopt lxml selenium
```

Follow the below usage guide to execute the script from the terminal:

```
Usage:
    $ python owl-watcher.py [--open=<ot>] [--close=<ct>] [--mute]
    $ python owl-watcher.py (-h | --help)
    $ python owl-watcher.py --version
    
Options:
    -h --help       Show this screen.
    --version       Show version.
    --open=<ot>     How early to open the stream in seconds [default: 300].
    --close=<ct>    How late to close the stream in seconds [default: 1800].
    --mute          Enables automatically muting the stream upon opening.
```
