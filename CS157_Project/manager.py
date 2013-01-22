import threading
import socket
import sys
import signal
import random
from subscribable import *

class Manager(threading.Thread):
    dict_subscribables = {}
    def __init__(self, d):
        self.dict_subscribables = d
        self.dict_subscribables.update((str(x), Subscribable(10)) for x in xrange(5))
        self.max_c = 10
        self.threads = []
        threading.Thread.__init__(self)
        
    def subscribe(self, uid, sid):
        return self.dict_subscribables[sid].accept_app(uid) 
    
    def get_subscriber(self, sid):
        return self.dict_subscribables[sid]
        
    
    def unsubscribe(self, uid, sid):
        return self.dict_subscribables[sid].unbind(uid)
        

    def add_subscribables(self, Subscribable):
        self.dict_subscribables[Subscribable.get_id] = Subscribable

    def get_subscribables_ids(self):
        return self.dict_subscribables.keys()

    def get_ids(self):
        return [str(key) for key in self.get_subscribables_ids()]

    def cleanup(self, server, threads):
        """ Clean up socket connections """
        self.server.close()
        self.server = None
        for t in self.threads:
            t.join()
        sys.exit(0)


    def process_requests(self, channel, details):
        print self.getName(), '- Received connection: ', details[0]
        request_info = channel.recv(1024).split()
        channel.send('Processing request....')
        #   Try and fulfill request
        if request_info[0] == 'subscribe':
            print request_info
            try:
                print self.getName(), ' is trying to ', request_info[0]
                channel.recv(1024)
                response =  self.subscribe(request_info[1], request_info[2])
                if response == 1:
                    channel.send(str(request_info[2]) + ' 1 Successful.')
                    print 'Successful'
                elif response == 2:
                    channel.send(str(request_info[2]) + ' 2 On_waiting_list.')
                    print 'On Waiting list'
                elif response == 0:
                    channel.send(str(request_info[2]) + ' 0 Unsuccessful.')
                    print 'Unsuccessful'
            except socket.error, msg:
                    print 'Failed to subscribe'
                    channel.send('Unable to subscribe for %s', str(request_info[2]))
        if request_info[0] == 'unsubscribe':
                try:
                    print self.getName(), ' is trying to ', request_info[0]
                    channel.recv(1024)
                    response =  self.unsubscribe(request_info[1], request_info[2])
                    print request_info[1]
                    print request_info[2]
                    print response
                    channel.send(str(request_info[2]) + ' 1  Successful') 
                    print 'Done'
                except:
                    print 'Failed to unsubscribe'
                    channel.send('Unable to subscribe for %s', str(request_info[2]))
        if request_info[0] == 'check':
            try:
                print self.getName(), ' is trying to get status of subscriber'
                channel.recv(1024)
                locker = self.get_subscriber(request_info[1])
                response = ""
                if locker.is_full:
                    response = response + "True\r"
                else:
                    response = response + "False\r"
                response = response + str(locker.max_queue) + "\r"
                response = response + str(len(locker.queue_applicants)) + "\r" 
                print 'Check Request Successful.'
                channel.send(response)
            except:
                print 'Failed to get subscribable'
                channel.send('Unable to get subscribable for %s', str(request_info[1]))
        if request_info[0] == 'wait':
            try:
                print self.getName(), ' is trying to request waiting list.'
                channel.recv(1024)
                locker = self.get_subscriber(request_info[2])
                bind_uid = locker.bind_uid
                if bind_uid == request_info[1]:
                    response = 'True'
                else:
                    response = 'False'
                channel.send(response)
            except:
                print 'Failed to check the statue of a user.'
                channel.send('Unable to check the status of waiting list.')
        if request_info[0] == 'inquire':
            try:
                print self.getName(), ' is trying to request all lockers\' ids.'
                channel.recv(1024)
                keys = self.dict_subscribables.keys()
                response = ''
                for key in keys:
                    response = response + str(key) + "\r"
                channel.send(response)
            except:
                print 'Failed to inquire lockers.'
                channel.send('Unable to inquire the lockers\' ids.')
        if request_info[0] == 'validate':
            try:
                print self.getName(), ' is trying to check validity.'
                channel.recv(1024)
                locker = self.get_subscriber(request_info[2])
                queue = locker.get_applicants()
                if request_info[1] in queue:
                    response = "True"
                else:
                    response = "False"
                channel.send(response)
            except:
                print 'Failed to check user validity.'
                channel.send('Unable to check the lockers.')
                
                
    def run(self):
        #   Using SO_REUSEADDR for faster rebinding of connections.
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('', 7700))
        server.listen(20)
        while True:
            print 'waiting'
            channel, details = server.accept()
            request = self.process_requests(channel, details)
            t = threading.Thread(target=request)
            t.daemon = True
            t.start()
            t.join
            self.threads.append(t)
        self.cleanup()
    
