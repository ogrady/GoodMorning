import socket
import logger as l
from threading import Thread

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
CONNECTION_TIMEOUT = 2
BUFFER_SIZE = 64

class NetworkListener(Thread):
    def __init__(self, host, port, max_connections = 2, connection_timeout = 2):
        Thread.__init__(self, target = self.listen)
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(connection_timeout)
        self.max_connections = max_connections
        self.running = False
        
    def stop(self):
        self.running = False

    def listen(self):
        if not self.running:
            self.running = True
            self.socket.bind((self.host, self.port))
            self.socket.listen(self.max_connections)
            l.log("Now listening to %s:%d" % (self.host, self.port))
            while self.running:
                try:
                    connection, address = self.socket.accept()
                    connection.settimeout(CONNECTION_TIMEOUT)
                    try:
                        l.log("Received connection from %s" % (address,))
                        buf = connection.recv(BUFFER_SIZE)
                        if len(buf) > 0:
                            l.log("Input '%s' received from %s" % (buf, address))
                            print (buf)
                    except:
                        pass
                        # ignore - recv() time out
                    connection.close()
                except:
                    pass
                    # ignore - accept() timed out
