import util
import config
import logger as l

'''
Network commands.

version: 1.0
author: Daniel O'Grady  
'''

class CommandDispatcher(object):
    def __init__(self):
        self.lullabies = config.read_lullabies(util.ALARMS_FILE)
    
    def execute(self, command_string):
        def _validate_args(cmd, args, min_args):
            if len(args) < min_args:
                raise util.CommandException("Command '%s' requires at least %d arguments, only %d were passed (%d)" % (cmd, min_args, len(args), args))
        
        toks = command_string.split(' ')
        cmd = toks[0]
        args = toks[1:] if len(toks) > 0 else []
        
        if cmd == "lullaby":
                _validate_args(cmd, args, 1)
                l.log("Manually executing '%s' with arguments '%s'" % (cmd, args))
                lullaby = self.lullabies[args[0]]
                lullaby.ring()
        else:
            l.log("Skipping invalid command '%s'" % (command_string,))
