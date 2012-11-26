#!/usr/bin/env python

import jmeter_log_monitor
import pynsca
from optparse import OptionParser


cmd_parser = OptionParser()
cmd_parser.add_option("-I", "--check_interval", action="store", type="int", dest="check_interval", help="Log check interval", metavar="60 or 120 second")
cmd_parser.add_option("-F", "--log_filename", action="store", type="string", dest="log_filename", help="Log file name", metavar="result")
(cmd_options, cmd_args) = cmd_parser.parse_args()

if not (cmd_options.check_interval and cmd_options.log_filename):
    cmd_parser.print_help()
    sys.exit(3)


LOG_FILENAME = cmd_options.log_filename 
NAGIOS_ADDRESS = "10.0.7.201"
LOCAL_ADDRESS = "10.0.7.214"

CHECKE_INTERVAL = cmd_options.check_interval

logMonitor = jmeter_log_monitor.JMeterLogMonitor(LOCAL_ADDRESS, NAGIOS_ADDRESS, LOG_FILENAME, CHECKE_INTERVAL)

logMonitor.start()

# some event to stop monitor
# logMonitor.stop()
