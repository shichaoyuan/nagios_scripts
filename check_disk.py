#!/usr/bin/python
import commands, sys
import pynsca
from optparse import OptionParser

nagios_address = "10.0.7.201"
service_description = "Disk_Status"
return_code = pynsca.UNKNOWN
plugin_output = ""

cmd_parser = OptionParser(version="%prog 0.1")
cmd_parser.add_option("-H", "--local address", type="string", action="store", dest="local_address", help="Local IP addresss", metavar="10.0.77.6 or .7 or .8 or .9")
cmd_parser.add_option("-P", "--mountpoint", action="store", type="string", dest="mount_point", help="Which Disk to be Check", metavar="/ or /cluster")
cmd_parser.add_option("-w", "--warning", type="int", action="store", dest="warning_per", help="Exit with WARNING status if higher than the PERCENT of Disk Usage", metavar="Warning Percentage")
cmd_parser.add_option("-c", "--critical", type="int", action="store", dest="critical_per", help="Exit with CRITICAL status if higher than the PERCENT of Disk Usage", metavar="Critical Percentage")
(cmd_options, cmd_args) = cmd_parser.parse_args()

if not (cmd_options.local_address and cmd_options.mount_point and cmd_options.warning_per and cmd_options.critical_per):
    cmd_parser.print_help()
    sys.exit(3)

# get disk status
disk_status = commands.getstatusoutput("df -h " + cmd_options.mount_point)

usage_per= disk_status[1].split()[11]
usage_per_number = int(usage_per[:-1])

# Check if CPU Usage is Critical/Warning/OK
if usage_per_number >= cmd_options.critical_per:
    return_code = pynsca.CRITICAL
    plugin_output = 'STATISTICS CRITICAL : '
elif  usage_per_number >= cmd_options.warning_per:
    return_code = pynsca.WARNING
    plugin_output = 'STATISTICS WARNING : '
else:
    return_code = pynsca.OK
    plugin_output = 'STATISTICS OK : '

plugin_output += '"MOUNT' + cmd_options.mount_point + '"Usage=' + usage_per + ' | "MOUNT' + cmd_options.mount_point + '"Usage=' + usage_per + ';' + str(cmd_options.warning_per) + ';' + str(cmd_options.critical_per) +';;'

#print plugin_output
nscaClient = pynsca.NSCANotifier(nagios_address)
nscaClient.svc_result(cmd_options.local_address, service_description, return_code, plugin_output)

