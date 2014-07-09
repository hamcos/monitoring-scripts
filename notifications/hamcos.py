import os, re
criticality = {
    'critical' : [ 'GK', 'Business critical' ],
    'prod'     : [ 'PS', 'Productive system' ],
    'test'     : [ 'TS', 'Test system' ],
}

def exit_if_hosttag():
    hosttags = ' %s ' % os.environ['NOTIFY_HOSTTAGS']
    if os.environ.get( 'NOTIFY_PARAMETERS' ):
        for tag in os.environ['NOTIFY_PARAMETERS'].split():
            match = re.search(r'\A!(.*)', tag)
            if match: # this tag must not exist in NOTIFY_HOSTTAGS or we exit
                print 'Tag: %s must not exist in HOSTTAGS' % match.group(1)
                if re.search(r'\s%s\s' % match.group(1), hosttags):
                    os._exit(0)
            else: # this tag must exist in NOTIFY_HOSTTAGS or we exit
                print 'Tag: %s must exist in HOSTTAGS' % tag
                if not re.search(r'\s%s\s' % tag, hosttags):
                    os._exit(0)

def return_criti():
    """ Returns list with acronym and expanded form """
    for tag in os.environ['NOTIFY_HOSTTAGS'].split():
        if tag in criticality:
            return criticality[tag]
