from util import Singleton
from datetime import datetime

'''
Logging to file.

version: 1.0
author: Daniel O'Grady
'''

T_ERROR = "ERROR"
T_NOTICE = "NOTICE"
T_WARNING = "WARNING"

@Singleton
class Logger(object):
    
    def __init__(self):
        self.handle = open('goodmorning.log', 'a')
    
    def write(self, message, message_type = None):
        written = False
        if self.handle:
            if not message_type:
                message_type = T_NOTICE
            self.handle.write("%s %s: %s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message_type, message))
            self.handle.flush()
            written = True
        return written
            
        
    def close(self):
        if self.handle:
            self.handle.close()
            self.handle = None

def log(message, message_type = None):
    Logger.instance.write(message, message_type)
