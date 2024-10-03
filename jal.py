import os
import datetime

DEBUG = -1
INFO = 0
NOTICE = 1
WARN = 2
ERROR = 3
CRITICAL = 4

class Logger:
    def __init__(self) -> None:
        pass

    def setup(self, type = INFO, filenameDirectory = "./", filename = f"{str(datetime.date.today())}.log"):
        self.LogType = type
        self.filename = filename
        self.filenameDirectory = filenameDirectory
        currentfilenum = 0
        if not os.path.exists(self.filenameDirectory):
            os.makedirs(self.filenameDirectory)

        while os.path.exists(self.filenameDirectory+self.filename) == True:
            currentfilenum +=1
            self.filename = f"{str(datetime.date.today())}_{str(currentfilenum)}.log"

        self.strtype = _determineLogType(self.LogType)
        if self.strtype == 8:
            return 8

        with open(self.filenameDirectory+self.filename, "a") as f:
            f.write(f"[{datetime.datetime.now()}][LOGGER] Started Logger...")
            f.write("\n")
            f.write(f"[{datetime.datetime.now()}][LOGGER] Error Level set to {self.strtype}")
            f.write("\n")
        return 0

    def log(self, type, message):
        if type < self.LogType:
            return 7
        
        self.strtype = _determineLogType(type)
        if self.strtype == 8:
            return 8
        
        try:
            logString = f"[{datetime.datetime.now()}][{self.strtype}] "+message
            print(logString)
            with open(self.filenameDirectory+self.filename, "a") as f:
                f.write(logString)
                f.write("\n")
                f.close()
            return 0
        except:
            print("Failed to save log to file, exiting...")
            return 9
        

def _determineLogType(type):
    try:
        if type == DEBUG:
            strtype = "DEBUG"
        elif type == INFO:
            strtype = "INFO"
        elif type == NOTICE:
            strtype = "NOTICE"
        elif type == WARN:
            strtype = "WARN"
        elif type == ERROR:
            strtype = "ERROR"
        elif type == CRITICAL:
            strtype = "CRITICAL"
        return strtype
    except:
        print("Cannot determine log error type, exiting...")
        return 8