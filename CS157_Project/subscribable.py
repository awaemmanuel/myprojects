class Subscribable:
    # the list of waiting applicants    
    queue_applicants = []
    max_queue = 10
    is_full = False
    # the id of the subscriber who is occupying this subscribable
    bind_uid = ''
    
    
    def __init__(self, max_c):
        self.queue_applicants = []
        self.is_full = False
        self.max_queue = max_c
        self.bind_uid = ''
    
    
    def accept_app(self, uid):
        """
        take in an id of a subscriber,
        will return 1 when the subscriber has occupied/occupies this subscribable successfully;
        will return 2 when the subscriber is enlisted in the waiting queue;
        will return 0 when this subscribable is occupied and the waiting queue is full (max length reached)
        """
        print self.queue_applicants
        if self.bind_uid == uid:
            return 1
        if uid in self.queue_applicants:
            return 2
        if len(self.queue_applicants) < self.max_queue:
            if self.bind_uid == '':
                self.bind_uid = uid
                return 1
            else:
                self.queue_applicants.append(uid)
                return 2
        return 0
    
    
    def unbind(self, uid):
        """
        stops the requiring for this subscribable from a subscriber with the uid;
        will return the id of the subscriber occupying this subscribable
        """
        if self.bind_uid == uid:
            self.bind_uid = ''
            if len(self.queue_applicants) > 0:
                self.queue_applicants.reverse()
                self.bind_uid = self.queue_applicants.pop()
                self.queue_applicants.reverse()
        else:
            if uid in self.queue_applicants:
                self.queue_applicants.remove(uid)
        return self.bind_uid
        
        
    def get_applicants(self):
        return self.queue_applicants
    
    
    def get_binder(self):
        return self.bind_uid
