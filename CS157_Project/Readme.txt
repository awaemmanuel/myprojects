The subscribable.py, subscriber.py and manager.py is three core functional parts of a 
subscribable system. For example, Subscribable could be something like locker, subscriber 
is the one who want subscribe the locker and manager is the one who manage all the lockers


The server.py, users.py is a real locker system which extended the three core function 
parts.

dbwrapper.py is a single function module that is used in the locker system which enable 
the locker system backup its status into database for backup.

The server contains locker and the locker manager and it could start a socket listening 
for users request as in our system.

The users is just one client who want to subscribe a locker.

One locker is one object which instantialized on server. One locker has a waiting 
queue for users who applied it, there is only one person who is using the locker, and that
guy will expire after 30 minutes as we set, so that the next user in the waiting queue 
could use the locker and it goes on like that.

The manager could manage many locker objects in a dictionary in our system. Each locker in
that dictionary has been assigned an sid for user to inquire and subscribe.

And when users start their client, they could subscribe and unsubscribe.
There would be a receipt for users when they make a subscription.
When users start the client, the client will load and check the receipt.
The users also have a time to notify them the expiration of the locker.
If the users is put into a waiting list on server, the client will notify the users when 
they became the owner of the locker.

The extensibility of our system is dwelling in the fact that the three core classes: manager, 
subscriber and subscribible can be easily re-used through class inheritance. Any application
system can adapt these classes easily just by creating sub-classes of them.

#####################################################################
To use our system, simply run server.py and users.py in command line.

server.py:

There are two lockers as test example in the system, each locker has a waiting queue of 
maximun 10 users.

Type "\st" to start the socket listening for user requests.
Type "\h" to show the help list for administrator to use.

Note some function of the server is still under testing.

users.py:

Type "\h" to show the help list.
Type "\sh" to show the number(sid) of locker to subscribe.
Type "\su [sid]" to subscribe the specified locker by locker number.
Type "\u" to unsubscribe a locker that the user has subscribed.


