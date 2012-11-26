import os
import time
import errno
import stat
import datetime


class LogWatcher(object):

    def __init__(self, filename, callback):
        self.filename = os.path.realpath(filename)
        self.callback = callback
        self.file = None

    def __del__(self):
        self.file.close()

    def loop(self):
        self._checkfile()
        if self.file:
            try:
                lines = self.file.readlines()
                print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "==", str(len(lines)), "==\n"
                if lines:
                    self.callback(self.filename, lines)
            except EnvironmentError, err:
                print "read log file failed\n"
                self.file = None

    def _checkfile(self):
        if os.path.isfile(self.filename):
            if self.file:
                pass
            else:
                try:
                    fileb = open(self.filename, "r")
                    fileb.seek(os.path.getsize(self.filename))
                except EnvironmentError, err:
                    print "open log file faild\n"
                    self.file = None
                else:
                    self.file = fileb
                    print "open log file success\n"
            #try:
            #    fileb = open(self.filename, "r")
            #    #fileb.seek(os.path.getsize(self.filename))
            #except EnvironmentError, err:
            #    print "open log file failed\n"
            #    self.file = None
            #else:
            #    if self.file:
            #        #if self.file.fileno() != fileb.fileno():
            #        #    self.file.close()
            #        #    self.file = fileb
            #        #    self.file.seek(os.path.getsize(self.filename))
            #        #    print "log file moved"
            #        #else:
            #        #    print "close tmp file"
            #        #    fileb.close()
            #    else:
            #        self.file = fileb
            #        self.file.seek(os.path.getsize(self.filename))
            #        print "log file removed"
        else:
            if self.file:
                self.file.close()
                self.file = None
            print "no log file\n"

