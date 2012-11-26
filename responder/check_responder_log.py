#!/usr/bin/python

import responder_log_monitor
import pynsca
import sys
from optparse import OptionParser


# configuration
nagios_address = '10.0.7.201'
local_address = '10.0.7.213'
check_interval = 30
log_filename = '/home/tester/Responder/result'

pidfile = '/tmp/check_responder_log_process.pid'
stdin = '/dev/null'
stdout = '/home/nagios/check_resp_out.log'
stderr = '/home/nagios/check_resp_err.log'

logMonitor = responder_log_monitor.ResponderLogMonitor(local_address, nagios_address, log_filename, check_interval,\
        pidfile, stdin, stdout, stderr)

if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
        logMonitor.start()
    elif 'stop' == sys.argv[1]:
        logMonitor.stop()
    elif 'restart' == sys.argv[1]:
        logMonitor.restart()
    else:
        print 'Unknown command'
        sys.exit(2)
    sys.exit(0)
else:
    print 'usage: %s start|stop|restart' % sys.argv[0]
    sys.exit(2)  


