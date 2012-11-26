#!/usr/bin/python

from optparse import OptionParser
import sys
import pynsca

nagios_address = "10.0.7.201"
service_description = "Memory_Status"
return_code = pynsca.UNKNOWN

checkmemver = '0.1'

# Parse commandline options:
parser = OptionParser(usage="%prog -w <warning threshold> -c <critical threshold> [ -h ]",version="%prog " + checkmemver)
parser.add_option("-H", "--local_address",
    action="store", type="string", dest="local_address", help="Local IP address")
parser.add_option("-w", "--warning",
    action="store", type="int", dest="warn_threshold", help="Warning threshold in percentage")
parser.add_option("-c", "--critical",
    action="store", type="int", dest="crit_threshold", help="Critical threshold in percentage")
(options, args) = parser.parse_args()



memTotal = 0
memFree = 0
with open('/proc/meminfo') as f:
    for line in f.readlines():
        tokens = line.split()
        if tokens[0] == 'MemTotal:':
            memTotal = tokens[1]
        if tokens[0] == 'MemFree:':
            memFree = tokens[1]
memUsed = int(memTotal) - int(memFree)
memUsedPer = float(memUsed) * 100 / float(memTotal)

memUsed = memUsed / 1024

if memUsedPer > options.crit_threshold:
    plugin_output = "CRITICAL: Used memory percentage is " + str(memUsedPer) + "% (" + str(memUsed) + " MiB)"
    return_code = pynsca.CRITICAL
elif memUsedPer > options.warn_threshold:
    plugin_output = "WARNING: Used memory percentage is " + str(memUsedPer) + "% (" + str(memUsed) + " MiB)"
    return_code = pynsca.WARNING
else:
    plugin_output = "OK: Used memory percentage is " + str(memUsedPer) + "% (" + str(memUsed) +" MiB)"
    return_code = pynsca.OK

plugin_output +=  " | usedMemory=" + str(memUsedPer) + "%;" + str(options.warn_threshold) + ";" + str(options.crit_threshold) + ";;"
#print plugin_output

nscaClient = pynsca.NSCANotifier(nagios_address)
nscaClient.svc_result(options.local_address, service_description, return_code, plugin_output)
