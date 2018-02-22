# OWL Watcher

OWL Watcher is meant to run in the background and automatically opens the official Overwatch League live stream on [Twitch.tv](https://twitch.tv) shortly before the first match of the day is supposed to start. 

This can be a good method to collect viewership rewards such as in-game Overwatch League Tokens (information available [here](https://overwatchleague.com/en-us/news/21497938/watch-overwatch-league-get-league-tokens)).

The program uses the offical [Overwatch League API](https://api.overwatchleague.com) to fetch the offical schedule. This schedule is fetched on launch of the program to ensure it uses the latest version of the schedule.

Through optional arguments that can be passed to the program, the user can control how early before a scheduled match the stream open and enable automatically muting the stream upon opening.