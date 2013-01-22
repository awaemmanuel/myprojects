from subscriber import *
import re
import time
import os
import threading
import random

class User(Subscriber):
    def __init__(self):
        Subscriber.__init__(self, str(random.randint(1,10000))) 
        #The reservation expired in 30 minutes
        self.default_expiration_time = 30 * 60
        # Time period for check the expiration, default = 60 seconds, used in check_expiration()
        self.check_time_period = 60
        self.quit = 0
        self.request_time_stamp = 0
        self.check_user_validity()
        self.get_user_input()
    
    def check_expiration(self):
        '''
        Check the expiration for user every 1 minute
        This check run in a new thread
        The program will notify user when the remaining time is less than 10 min, 5 min and 60 sec.
        '''
        current_time = time.time()
        time_diff = current_time - self.request_time_stamp
        time_remains = self.default_expiration_time - time_diff
        t = threading.Timer(self.check_time_period, self.check_expiration)
        if self.request_time_stamp == 0:
            self.delete_receipt()
            self.bind_sid = ''
            t.cancel()
        else:
            t.start()
            if int(time_remains) <= 0:
                print "You locker has expired."
                t.cancel()
            elif 0 < int(time_remains) <= 60:
                print "Remaining time: 60 seconds."
            elif 301 <= int(time_remains) <= 360:
                print "Remaining time:" + str(int(time_remains / 60)) + " minutes."
            elif 600 <= int(time_remains) <= 660:
                print "Remaining time:" + str(int(time_remains / 60)) + " minutes."
    
    def check_user_validity(self):
        '''
        Check a users validity from the receipt and server, calls function: is_server_status_valid() and
        is_local_status_valid()
        if receipt exist, check receipt.
        if receipt is valid, check the receipt with server.
        '''
        if self.is_receipt_exist():
            if self.is_local_status_valid():
                ##############################Not tested#############################
                if self.is_server_status_valid():
                    print "valid receipt!"
    
    def is_receipt_exist(self):
        return os.path.exists('receipt')
    
    def is_server_status_valid(self):
        '''
        Check for a user's validity in case of local user tamper that leads program collapse.
        '''
        status = self.validate()
        if status != "True":
            print "Invalid previous receipt."
            self.delete_receipt()
            self.clear_status(True)
            return False
        return True

    
    def is_local_status_valid(self):
        '''
        Check whether the receipt file exists, if there is a receipt, perform a expiration check
        return true if the receipt is valid and not expired
        '''
        status = False
        if os.path.exists('receipt'):
            self.load_status()
            if not self.is_from_restart_expired():
                status = True
        return status
    
    def is_from_restart_expired(self):
        '''
        Check user reservation status when they start this program after they have a subscription and closed this client 
        '''
        status = False
        current_time = time.time()
        sub_time = int(current_time - self.request_time_stamp)
        if sub_time > self.default_expiration_time:
            self.delete_receipt()
            self.request_time_stamp = 0
            status = True
        return status
            
    def delete_receipt(self):
        '''
        Delete the receipt
        '''
        if os.path.exists('receipt'):
            os.remove('receipt')
            
    def request_locker(self, sid):
        '''
        Request a locker
        '''
        if self.request_time_stamp == 0:
            status = self.apply(sid)
            if status == 1:
                self.request_time_stamp = time.time()
                self.save_status()
                self.check_expiration()
                print "Locker subscribed."
            elif status == 2:
                print "You are on Waiting list."
                self.check_waiting_list()
            else:
                print "Sorry, error occurred."
        else:
            print "You already have subscribed a locker."
        
    def release_locker(self):
        '''
        Release a locker that the user previously subscribed.
        '''
        if self.request_time_stamp == 0:
            print "You don't have any subscription now."
        else:
            status = self.free(self.bind_sid)
            if status == 1:
                self.delete_receipt()
                self.request_time_stamp = 0
                self.bind_sid = ''
                print "Successfully unsubscribed."
            else:
                print "Error occurred, you can use \"\\d\"."
                
    def check_waiting_list(self):
        '''
        Check the waiting list if the user have to wait, default timer = 60s
        '''
        t = threading.Timer(60, self.check_waiting_list)
        response = self.wait(self.uid, self.request_sid)
        if response[0] == "True":
            self.request_time_stamp = time.time()
            self.check_expiration()
            print "You are now using the locker."
            t.cancel()
        else:
            t.start()
        
    def inquire_locker(self):
        '''
        To give users how many lockers are available now.
        '''
        response = self.inquire()
        locker_no = response.strip().split("\r")
        locker_no.sort()
        i = 0
        if len(locker_no) == 0:
            print "Sorry, no locker now."
        else:
            print "The available lockers IDs are:"
            output = ""
            for no in locker_no:
                i = i + 1
                output = output + no + "     "    
                if i % 5 == 0:
                    print output
                    output = ""
            if output != "":
                print output
        
    def save_status(self):
        '''
        Save a receipt that the user could shut down this program and load the reservation later.
        '''
        time_stamp = self.request_time_stamp
        file_receipt = open("receipt", "w+")
        file_receipt.write(str(time_stamp) + "\r")
        file_receipt.write(str(self.bind_sid) + "\r")
        file_receipt.write(str(self.uid))
        file_receipt.close()
    
    def check_subscription(self):
        '''
        Check the subscription status for user.
        '''
        if self.request_time_stamp == 0:
            print "You don't have any subscription now."
        else:
            print "Your uid:" + str(self.uid)
            print "The locker sid:" + str(self.bind_sid)
            self.check_time()
    
    def check_time(self):
        '''
        Return the subscription time for user.
        '''
        if self.request_time_stamp == 0:
            str_time_status = "You don't have any subscription or your locker has expired."
        else:
            current_time = time.time()
            time_diff = current_time - self.request_time_stamp
            time_remains = self.default_expiration_time - time_diff
            time_remains = int(time_remains / 60.0)
            if time_remains == 0:
                str_time_status = "Your locker has expired"
            else:
                str_time_status = "Your locker has:" + str(time_remains) + "minute(s) remaining."
        print str_time_status
    
    def load_status(self):
        '''
        Load the receipt.
        '''
        try:
            file_receipt = open('receipt', 'r')
            lines = file_receipt.readlines()
            lines = lines[0].split("\r")
            self.request_time_stamp = float(lines[0])
            self.bind_sid = lines[1]
            self.uid = lines[2]
            file_receipt.close()
        except:
            print "File Corrupted."
    
    def check_server(self, sid):
        '''
        Check a specified locker's status
        '''
        
        try:
            response = self.check(sid).split("\r")
            if response[0] == "True":
                print "This locker is full of users."
            else:
                print "This locker's full content is:" + response[1] + "."
                print response[2] + " of the locker has been occupied."
                print str(int(response[1]) - int(response[2])) + " empty slots in the waiting queue."
        except:
            print "Server error."
            
    def clear_status(self, silent = False):
        '''
        Clear the status of user on local.
        '''
        if silent != True:
            print "All status will be cleared, are you sure?"
        while(1):
            regex_confirm_yes = r"yes|y"
            regex_confirm_no = r"no|n"
            if silent != True:
                print "Yes or No?"
                confirmation = raw_input("Clear Status >")
            if silent or (regex_confirm_yes, confirmation):
                #if self.bind_sid != '':
                #    self.free(self.bind_sid)
                self.delete_receipt()
                self.request_time_stamp = 0
                self.bind_sid = ''
                break
            elif (regex_confirm_no, confirmation):
                print "Aborted"
                break
            else:
                continue
            
    def show_help(self):
        '''
        Show help for user.
        '''
        print "\"\\h\" or \"help\" for help."
        print "\"\\su [sid]\" or \"sub [sid]\" to subscribe a locker."
        print "\"\\sh\" or \"show\" to show empty lockers. "
        print "\"\\p [str]\" or \"put [str]\" put things onto locker. "
        print "\"\\q\" or \"quit\" to quit this program and all the status will be stored."
        print "\"\\u\" or \"unsub\" to release the locker."
        print "\"\\d\" or \"delete\" to delete the receipt."
        print "\"\\t\" or \"time\" to check the remaining time."
        print "\"\\ch\" or \check\" to check the current subscription."
        print "\"\\cl\" or \clear\" to clear all the status in system."
        print "\"\\cs [sid]\" or \checkserver [sid]\" to check the status of server."
    
    def input_command(self, input_str):
        '''
        Check command that a user input
        '''
        reg_help = r"\\h|help"
        reg_subscribe = r"(\\su|sub)\s+\d+"
        reg_show = r"\\sh|show"
        reg_quit = r"\\q|quit"
        reg_unsubscribe = r"\\u|unsub"
        reg_time = r"\\t|time"
        reg_delete = r"\\d|delete"
        reg_check = r"\\ch|check"
        reg_clear = r"\\cl|clear"
        reg_check_server = r"(\\cs|checkserver)\s+\d+"
        
        # For help
        if re.match(reg_help, input_str):
            self.show_help()
        # For user's subscription
        elif re.match(reg_subscribe, input_str):
            sid = input_str.split()[1]
            self.request_locker(sid)
        # Show show all the lockers sid
        elif re.match(reg_show, input_str):
            self.inquire_locker()
        # Quit
        elif re.match(reg_quit, input_str):
            self.quit = 1;
        # For user's unsubscription
        elif re.match(reg_unsubscribe, input_str):
            self.release_locker()
        # For user's time check
        elif re.match(reg_time, input_str):
            self.check_time()
        # Delete user's receipt by user
        elif re.match(reg_delete, input_str):
            self.delete_receipt()
        # Users can check their subscription themselves
        elif re.match(reg_check, input_str):
            self.check_subscription()
        # Check a specified locker's queue
        elif re.match(reg_check_server, input_str):
            sid = input_str.split()[1]
            self.check_server(sid)
        # Clear users all status by users themselves
        elif re.match(reg_clear, input_str):
            self.clear_status()
        else:
            self.show_help()
            
    def get_user_input(self):
        '''
        Interactive reader from user.
        '''
        while(1):
            self.input = raw_input("I want locker >")
            self.input_command(self.input)
            if self.quit == 1:
                break
a = User()