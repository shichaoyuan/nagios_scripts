"""
Real time log files watcher supporting log rotation.

Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
License: MIT

Modify: monitor only one dedicated log file. by Shichao Yuan
"""

import os
import time
import errno
import stat


class LogWatcher(object):
    """Looks for changes in one log file.
    This is useful for watching log file changes in real-time.
    """

    def __init__(self, filename, callback):
        """Arguments:

        (str) @filename:
            the log file to watch

        (callable) @callback:
            a function which is called every time a new line in a 
            file being watched is found; 
            this is called with "filename" and "lines" arguments.

        """
        filename = os.path.realpath(filename)
        self.callback = callback
        assert callable(callback)
        # wait log file
        while not os.path.isfile(filename):
            time.sleep(5)
        # open log file
        self.loadfile(filename)

    def __del__(self):
        self.file.close()

    def loadfile(self, filename):
        while not os.path.isfile(filename):
            time.sleep(1)
        # open log file
        try:
            file = open(filename, "r")
        except EnvironmentError, err:
            #if err.errno != errno.ENOENT: raise
            print "open file failed"
        else:
            self.file = file
            self.file.seek(os.path.getsize(self.file.name))


    def loop(self, interval=0.1, async=False):
        """Start the loop.
        If async is True make one loop then return.
        """
        while True:
            if not os.path.isfile(self.file.name):
                self.loadfile(self.file.name)
            if os.fstat(self.file.fileno()).st_nlink < 1:
                self.loadfile(self.file.name)
            self.readfile(self.file)
            if async:
                return
            time.sleep(interval)

    def readfile(self, file):
        lines = file.readlines()
        if lines:
            self.callback(file.name, lines)

