from ctripcrawler import CtripCrawler
from ctripsearcher import CtripSearcher
from rebuilder import Rebuilder
import civilaviation
import sys
import time

class Log():
    def __init__(self, logfile: str):
        self.terminal = sys.stdout
        self.log = open(logfile, "a", encoding = 'UTF-8',)
 
    def write(self, message):
        self.terminal.write(message)
        if message.startswith("\n") or message.endswith("\n"):
            self.log.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n")
        self.log.write(message)
    def flush(self):
        pass