#!/usr/bin/env python
# encoding: utf-8

import os, re, sys, subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email import Charset
from email.generator import Generator
import smtplib
from hamcos import *

critc = return_criti()
hc_subject = 'hamcos Monitoring (%s):' % critc[1]
tmpl_host_subject = '%s $HOSTNAME$ - $NOTIFICATIONTYPE$' % hc_subject

tmpl_host_txt = '''Host:     $HOSTNAME$ ($HOSTALIAS$)
Address:  $HOSTADDRESS$

State:    $HOSTSTATE$ ($NOTIFICATIONTYPE$)
Hosttags: $HOSTTAGS$
Output:   $HOSTOUTPUT$
Perfdata: $HOSTPERFDATA$
$LONGHOSTOUTPUT$
'''

#
# SERVICE TEMPLATES
#

tmpl_service_subject = '%s $HOSTNAME$/$SERVICEDESC$ $NOTIFICATIONTYPE$' % hc_subject

tmpl_service_txt = '''Host:     $HOSTNAME$ ($HOSTALIAS$)
Address:  $HOSTADDRESS$

Service:  $SERVICEDESC$
State:    $SERVICESTATE$ ($NOTIFICATIONTYPE$)
Hosttags: $HOSTTAGS$
Output:   $SERVICEOUTPUT$
Perfdata: $SERVICEPERFDATA$
$LONGSERVICEOUTPUT$
'''
opt_debug = '-d' in sys.argv


def send_mail(m, subject, target, crici_state):

    # Example address data
    # from_address = [u'⌘Tomek Kopczuk⌘', 'icinga@cteam.de']
    # recipient = [u'Those #!@', 'robin.schneider@hamcos.de']

    # Example body
    # text = u'Unicode°\nTest⏎'

    # Default encoding mode set to Quoted Printable. Acts globally!
    Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')

    # 'alternative’ MIME type – HTML and plain text bundled in one e-mail message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "%s" % Header(subject, 'utf-8')
    # Only descriptive part of recipient and sender shall be encoded, not the email address
    # msg['From'] = "\"%s\" <%s>" % (Header(from_address[0], 'utf-8'), from_address[1])
    msg['To'] = target

    # Attach both parts
    textpart = MIMEText(m.encode('utf-8'), _charset='utf-8')
    msg.attach(textpart)

    # print str_io.getvalue()
    # print msg.as_string()

    if (critc[0] == 'GK' and crici_state):
        msg['Importance'] = 'High'
    p = subprocess.Popen(['/usr/sbin/sendmail', '-t' ], stdin = subprocess.PIPE)
    p.communicate(msg.as_string())
    return True

def prepare_contents(context):
    if context['WHAT'] == 'HOST':
        tmpl_txt  = tmpl_host_txt
    else:
        tmpl_txt  = tmpl_service_txt

    return substitute_context(tmpl_txt, context)

def substitute_context(template, context):
    # First replace all known variables
    for varname, value in context.items():
        template = template.replace('$'+varname+'$', value)

    # Remove the rest of the variables and make them empty
    template = re.sub("\$[A-Z_][A-Z_0-9]*\$", "", template)
    return template

def main(cust_info = False):
    """ if cust_info == True: add customer information """
    # gather all options from env
    context = dict([
        (var[7:], value.decode("utf-8"))
        for (var, value)
        in os.environ.items()
        if var.startswith("NOTIFY_")])


    # Compute the subject of the mail
    if context['WHAT'] == 'HOST':
        subject = substitute_context(tmpl_host_subject, context)
        crici_state = True if context['HOSTSTATE'] == 'CRITICAL' else False
    else:
        subject = substitute_context(tmpl_service_subject, context)
        crici_state = True if context['SERVICESTATE'] == 'CRITICAL' else False

    m = prepare_contents(context)
    m += open('/etc/check_mk/hamcos_and_customer').read()
    if cust_info == True:
        m += open('/etc/check_mk/customer').read()

    # Create the mail and send it
    send_mail(m, subject, context['CONTACTEMAIL'], crici_state)
