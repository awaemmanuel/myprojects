from subscribable import *
from manager import *
#from dbwrapper import *
import time
import re
import os
import struct
import threading

class Locker(Subscribable):
    def __init__(self, max_c):
        '''
        Load configuration from file and load status of previous locker(if exists)
        '''
        # The check timer for expired lockers, default = 30 seconds
        Subscribable.__init__(self, max_c)
        self.check_time_period = 30
        # The reservation expired in 30 minutes
        self.default_expiration_time = 30 * 60
        self.load_configuration_file()
        self.current_user_timestamp = 0
        #self.current_user_id = ""
                
    def get_subscriber(self):
        '''
        Return a specified subscriber for a Locker Manager's request.
        '''
        return self.subscribable.get_applicants()
    
    def remove_subscriber(self):
        '''
        Remove a specified subscriber from the request of Locker Manager(The request usually
        comes from Users).
        Return bolean to indicate the status.  
        '''
        ###########################Need modification of parameters
        return self.subscribable.unbind(1)
    
    def init_configuration(self):
        '''
        Initialize the configuration for Lockers, the default setting is to store the status in file. 
        '''
        self.backup_config = 0
        print "First launch of the system or configuration file corrupted, please choose where to store the status of locker for backup."
        self.change_backup_configuration()
        
    def load_configuration_file(self):
        '''
        Load the configuration file from file system.
        If file does not exist, call init_configuration() to initialized the system.
        0 for store status in local file system.
        1 for store status onto database.
        '''
        reg_num = r"0|1"    
        e = os.path.exists('config')
        if e:
            file_config = open('config', 'r')
            config = file_config.read(1)
            if re.match(reg_num, config):
                self.backup_config = int(config)
            else:
                # In case of illegal user tamper.
                print "Bad configuration file, the backup plan will be save to file as default"
                self.backup_config = 0
                self.save_configuration_file()
            file_config.close()
        else:
            self.init_configuration()
            print "Configuration initialized."
        
    def save_configuration_file(self):
        '''
        Save the configuration file.
        '''
        file_conf = open('config', 'w')
        file_conf.write(str(self.backup_config))
        file_conf.close()
        
    def change_backup_configuration(self):
        '''
        Change the backup plan of where the status to be stored.
        0 for store status in local file system.
        1 for store status onto database.
        '''
        while(1):
            reg_num = r"0|1"
            print "Choose the way to save the lockers current status:"
            print "\"0\" for saving to local file."
            print "\"1\" for saving to Database."
            print "\"q\" to abort."
            config = raw_input("Change Config >")
            if re.match(reg_num, config) and len(config) == 1:
                self.backup_config = int(config)
                self.save_configuration_file()
                break
            elif config == 'q':
                break
            else:
                print "Wrong input."
                continue
    
    def load_status_from_db(self, init):
        # Not implemented
        '''
        Load the server status from DB when self.back_config == 1
        '''
        regex_confirm_yes = r"yes|y"
        regex_confirm_no = r"no|n"
        print "Load previous locker status from DB."
        print "All current status will be overrode."
        while(1):
            if not init:
                print "Yes or No?"
                confirmation = raw_input("Load DB >")
            if init or re.match(regex_confirm_yes, confirmation):
                #########################################query with SQL
                break
                pass
            elif re.match(regex_confirm_no, confirmation):
                print "Canceled"
                break
            else:
                continue
    
    def load_status_from_file(self, init, sid):
        '''
        Load the server status from file when self.backup_config == 0
        '''
        regex_confirm_yes = r"yes|y"
        regex_confirm_no = r"no|n"
        print "Load previous locker status from file." 
        while(1):
            if not init:
                print "All current status will be overrode."
                print "Yes or No?"
                confirmation = raw_input("Load File >")
            if init or re.match(regex_confirm_yes, confirmation):
                file_receipt = open(sid + '_status', 'r')
                queue = file_receipt.readlines()
                queue = queue[0].strip()
                queue = queue.split("\r")
                self.current_user_timestamp = float(queue[0])
                self.queue_applicants = queue[1:]
                file_receipt.close()
                print "Load successfully."
                break
            elif re.match(regex_confirm_no, confirmation):
                print "Load canceled"
                break
            else:
                continue
            
    def save_status_to_db(self, sid, silent):
        '''
        Save the status to database, Not implemented
        '''
        pass
    
    def save_status_to_file(self, sid, silent = False):
        '''
        Save status_to_file
        silent mode will exclude user interaction
        '''
        abort = 0
        if os.path.exists(sid + '_status') and not silent:
            print "Previous status exist, do you want to override it?"
            regex_confirm_yes = r"yes|y"
            regex_confirm_no = r"no|n"
            while(1):
                print "Yes or No?"
                confirmation = raw_input("Save Status >")
                if re.match(regex_confirm_yes, confirmation):
                    self.delete_status_file()
                    break
                elif re.match(regex_confirm_no, confirmation):
                    abort = 1
                    print "Save aborted."
                    break
                else:
                    continue
                
        if os.path.exists(sid + '_status') and silent:
            self.delete_status_file(sid)
                
        if abort == 0:
            file_status = open(sid + '_status', 'w+')
            file_status.write(str(self.current_user_timestamp) + "\r")
            queue = ["123","321","421","321","4","12"]
            for uid in queue:
                file_status.write(uid + "\r")
            file_status.close()
    
    def is_status_file_exists_in_DB(self):
        '''
        Check whether status saved in Database, not implemented.
        '''
        pass
    
    
    def init_status_from_DB(self):
        '''
        Initialize if the status exists in database.
        ''' 
        regex_confirm_yes = r"yes|y"
        regex_confirm_no = r"no|n"
        if self.is_status_file_exists_in_DB():
            print "The previous locker status exists in database."
            print "Do you want to load the previous locker status from database?"
            while(1):
                print "Yes or No?"
                confirmation = raw_input("Load Status >")
                if re.match(regex_confirm_yes, confirmation):
                    self.load_status_from_db(True)
                    break
                elif re.match(regex_confirm_no, confirmation):
                    print "Cancelled."
                    break
                else:
                    continue
                    
    def delete_status_file(self, sid):
        '''
        Delete status file for maintainance.
        '''
        if os.path.exists(sid + '_status'):
            os.remove(sid + '_status')
            print "Previous status file deleted."
        else:
            print "No status file."
            
    def check_expiration(self):
        '''
        Check the expiration for user every 1 minute
        This check run in a new thread
        The program will notify user when the remaining time is less than 10 min, 5 min and 60 secs.
        '''
        
        current_time = time.time()
        time_diff = int(current_time - self.current_user_timestamp)
        if time_diff >= self.default_expiration_time:
            self.queue_applicants.pop()
            self.unbind(self.bind_uid)
        t = threading.Timer(self.check_time_period, self.check_expiration())    
        t.start()
            
    def delete_status_database(self):
        '''
        Delete status in database for maintainance.
        '''
        pass
    
    def clear(self, locker):
        self.uid = ''
        self.queue_applicants = []
        print "Locker cleared."
        
    def save_status(self, sid, silent):
        if self.backup_config == 0:
            self.save_status_to_file(sid, silent)
        else:
            self.save_status_to_db(sid, silent)
        
class LockerManager(Manager):
    def __init__(self, dict_locker):
        Manager.__init__(self, dict_locker)
        self.quit = 0
        self.get_input()
    
    def show_help(self):
        '''
        Show help for user
        '''
        print "\"\\h\" or \"help\" for help."
        print "\"\\st\" or \"start\" to start locker system."
        print "\"\\sp\" or \"stop\" to stop the server."
        print "\"\\sh\" or \"show\" to show all lockers. "
        print "\"\\sq [sid]\" or \"queue [sid]\" show the queue of people waiting."
        print "\"\\sv [sid]\ or \"save [sid]\" to save a specified locker."
        print "\"\\sa\" or \"saveall\" to save all the lockers status."
        print "\"\u [sid] [uid]\" or \"unsub [sid] [uid]\" to unsubscribe one specified user from locker"
        print "\"\\cl [sid]\" or \"clearlocker [sid]\" to release one specified locker mandatory."
        print "\"\\ca\" or \"clearall\" to clear all lockers manadatory."
        print "\"\\b [sid]\" or \"backup [sid]\" to change one locker's backup way(in database or in file)."
        print "\"\\q\" or \"quit\" to quit this program and save status."
        
    def input_command(self, input_str):
        '''
        Check command that a user input
        '''
        reg_help = r"\\h|help"
        reg_show_lockers = r"\\sh|show"
        reg_quit = r"\\q|quit"
        reg_unsubscribe = r"(\\u|unsub)\s+\d+\s+\d+"
        reg_show_queue = r"(\\sq|queue)\s+\d+"
        reg_clear_locker = r"(\\cl|clearlocker)\s+\d+"
        reg_backup = r"(\\b|backup)\s+\d+"
        reg_start = r"\\st|start"
        reg_stop = r"\\sp|stop"
        reg_save_locker = r"(\\sv|save)\s+\d+"
        reg_save_lockers = r"\\sa|saveall"
        reg_clear_lockers = r"\\ca|clearall"
        
        if re.match(reg_help, input_str):
            self.show_help()
        # Start Service   
        elif re.match(reg_start, input_str):
            #not implemented
            self.start_service()
        # Stop Service
        elif re.match(reg_stop, input_str):
            #not implemented
            self.stop_server()
        # Save one specified locker's status
        elif re.match(reg_save_locker, input_str):
            sid = input_str.split()[1]
            self.save_locker_status(sid)
        # Save all lockers status
        elif re.match(reg_save_lockers, input_str):
            self.save_lockers()
        # Quit
        elif re.match(reg_quit, input_str):
            self.quit = 1;
        # Show all lockers
        elif re.match(reg_show_lockers, input_str):
            self.show_lockers()
        # Show one locker's waiting queue
        elif re.match(reg_show_queue, input_str):
            sid = input_str.split()[1]
            self.show_queue(sid)
        # Change one locker's backup plan
        elif re.match(reg_backup, input_str):
            sid = input_str.split()[1]
            self.change_locker_configuration(sid)
        # Clear one specified locker
        elif re.match(reg_clear_locker, input_str):
            sid = input_str.split()[1]
            self.clear_locker(sid)
        # Clear all lockers
        elif re.match(reg_clear_lockers, input_str):
            self.clear_lockers()
        # Unsubscribe one specified user
        elif re.match(reg_unsubscribe, input_str):
            sid = input_str.split[1]
            uid = input_str.split[2]
            self.unsubscribe(uid, sid)
        # Show help
        else:
            self.show_help()
    
    def clear_lockers(self):
        '''
        Clear all lockers.
        '''
        keys = self.dict_subscribables.keys()
        for key in keys:
            self.dict_subscribables.get(key).clear()
        
            
    def clear_locker(self, sid):
        '''
        Clear one specified locker.
        '''
        locker = self.dict_subscribables.get(sid)
        locker.clear()
        
    def save_locker_status(self, sid):
        '''
        Save one specified locker by it's sid in manager.
        '''
        self.dict_subscribables.get(sid).save_status(sid, False)
        
    
    def save_lockers(self):
        '''
        Save all lockers status
        '''
        keys = self.dict_subscribables.keys()
        for key in keys:
            self.dict_subscribables.get(key).save_status(key, True)
        
    def get_input(self):
        '''
        Interactive input from Administrator.
        '''
        while(1):
            self.input = raw_input("Locker Server >")
            self.input_command(self.input)
            if self.quit == 1:
                self.on_quit()
                break
            
    def show_queue(self, sid):
        locker = self.dict_subscribables.get(sid)
        print locker.get_applicants()
        
    def show_lockers(self):
        keys = self.dict_subscribables.keys()
        i = 0
        key_str = ""
        for key in keys:
            key_str = key_str + str(key) + "   "
            if i % 5 == 0:
                print key_str
                key_str = ""
            i = i + 1
        if str != "":
            print key_str
            
    def change_locker_backup(self, sid):
        self.dict_subscribables.get(sid).change_backup_configuration()
        
    def start_service(self):
        self.run()
        
    def on_quit(self):
        print "Do you want to save all the lockers status?"
        while(1):
            print "Yes or No?"
            regex_confirm_yes = r"yes|y"
            regex_confirm_no = r"no|n"
            confirmation = raw_input("Quit System >")
            if re.match(regex_confirm_yes, confirmation):
                keys = self.dict_subscribables.keys()
                for key in keys:
                    self.dict_subscribables.get(key).save_status(True, key)
                break
            elif re.match(regex_confirm_no, confirmation):
                print "Cancel all status."
                break
            else:
                continue

l1 = Locker(10)
l2 = Locker(10)
l1.queue_applicants = ['123','234','456','678']
l2.queue_applicants = ['123','234','413','678']
a = {'123':l1, '234':l2}
lm = LockerManager(a)
