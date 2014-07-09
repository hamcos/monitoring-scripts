import os
from hamcos import *

send_path = '/usr/bin/sendsms'
if not os.path.exists(send_path):
    send_path = '/usr/local/bin/sendsms'
    if not os.path.exists(send_path):
        print "SMS Tools not found"
        os._exit(1)

def send_sms(cust_info = False):
    """ if cust_info == True: add customer information """
    critc = return_criti()

    max_len = 160
    message = critc[0] + ": " + os.environ['NOTIFY_HOSTNAME'] + " "

    if os.environ['NOTIFY_WHAT'] == 'SERVICE':
        message += os.environ['NOTIFY_SERVICESTATE'][:2] + " "
        avail_len = max_len - len(message)
        message += os.environ['NOTIFY_SERVICEDESC'][:avail_len] + " "
        avail_len = max_len - len(message)
        message += os.environ['NOTIFY_SERVICEOUTPUT'][:avail_len]

    else:
        message += "is " + os.environ['NOTIFY_HOSTSTATE']

    if cust_info == True:
        message += '\n%s' % open('/etc/check_mk/customer-short').read()

    empf = os.environ['NOTIFY_CONTACTPAGER']
    os.system("sudo %s %s '%s'" % (send_path, empf, message[:160]))
