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

"""

from docopt import docopt

def main(arguments):
    return

if __name__ == '__main__':
    arguments = docopt(__doc__, version='OWL Watcher 0.1')
    main(arguments)