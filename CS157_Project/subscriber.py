import sys
import threading
import socket
import signal


##  Remove mng parameters and simply send requests via socks to Manager
class Subscriber(threading.Thread):
    uid = ''
    bind_sid = ''
    def __init__(self, id='', mode='socket'):
        self.uid = id
        self.bind_sid = ''
        self.mode = mode
        self.sock = '127.0.0.1'
        self.addr = 7700
        
        
    def apply(self, sid, mng=None):
        """
        ask the manager to subscribe a subscribable, using sid as the subscribable's id 
        """
        if self.mode == 'socket':
            self.client_sock = socket.socket()
            self.client_sock.connect((self.sock, self.addr))
            self.client_sock.send('subscribe '+ str(self.uid) + ' ' + str(sid))
            print self.client_sock.recv(1024)
            self.client_sock.send('ok')
            response = self.client_sock.recv(1024).split()
            if int(response[1]) == 1: self.bind_sid = response[0]
            self.cleanup()
            return int(response[1])
        else:
            result = mng.subscribe(self.uid, sid)
            if result[1]: self.bind_sid = result[0]
        
    
    def free(self, sid, mng=None):
        """
        ask the manager to unsubscribe a subscribable, using sid as the subscribable's id
        """
        if self.mode == 'socket':
            self.client_sock = socket.socket()
            self.client_sock.connect((self.sock, self.addr))
            self.client_sock.send('unsubscribe '+ str(self.uid) + ' '+ str(sid))
            response = self.client_sock.recv(1024)
            print response
            self.client_sock.send('ok')
            response = self.client_sock.recv(1024).split()
            if int(response[1]): self.bind_sid = ''
            #print response[2]
            self.cleanup()
            return int(response[1])
        else:
            result = mng.unsubscribe(self.uid, sid)
            if result[1]: self.bind_sid = ''
    
    
    def check(self, sid, mng=None):
        """
        ask the server about the information of a subscribable with the sid as its id
        """
        if self.mode == 'socket':
            self.client_sock = socket.socket()
            self.client_sock.connect((self.sock, self.addr))
            self.client_sock.send('check '+ str(sid))
            response = self.client_sock.recv(1024)
            print response
            self.client_sock.send('ok')
            response = self.client_sock.recv(1024)
            #print response[0]
            self.cleanup()
            return response
        else:
            return mng.get_subscriber(sid)


    def cleanup(self, *args):
        """ Close and clean up server connections """
        global client_sock
        self. client_sock.close()
        self.client_sock = None
        #sys.exit(0) 
        
    def inquire(self):
        """ Check sid of a subscribable """
        if self.mode == 'socket':
            self.client_sock = socket.socket()
            self.client_sock.connect((self.sock, self.addr))
            self.client_sock.send('inquire ')
            response = self.client_sock.recv(1024)
            print response
            self.client_sock.send('ok')
            response = self.client_sock.recv(1024)
            self.cleanup()
            return response
        
    def validate(self):
        """ Validate a local receipt with server """
        if self.mode == 'socket':
            self.client_sock = socket.socket()
            self.client_sock.connect((self.sock, self.addr))
            self.client_sock.send('validate '+ str(self.uid) + ' '+ str(self.bind_sid))
            response = self.client_sock.recv(1024)
            self.client_sock.send('ok')
            response = self.client_sock.recv(1024).split()
            self.cleanup()
            return response[0]
    
    def wait(self, uid, sid):
        """ Checks if user is in the waiting list or not """
        if self.mode == 'socket':
            self.client_sock = socket.socket()
            self.client_sock.connect((self.sock, self.addr))
            self.client_sock.send('wait '+ str(self.uid) + ' '+ str(sid))
            response = self.client_sock.recv(1024)
            print response
            self.client_sock.send('ok')
            response = self.client_sock.recv(1024)
            self.cleanup()
            return response