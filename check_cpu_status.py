#!/usr/bin/python
import sys, time
import pynsca
from optparse import OptionParser

nagios_address = "10.0.7.201"
service_description = "CPU_Status"
return_code = pynsca.UNKNOWN
plugin_output = ""

sample_interval = 5

cpu_stat_var_array = ('user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal_time', 'guest')


cmd_parser = OptionParser(version="%prog 0.1")
cmd_parser.add_option("-H", "--local address", action="store", type="string", dest="local_address", help="Local IP addresss", metavar="10.0.77.6 or .7 or .8 or .9")
cmd_parser.add_option("-C", "--CPU", action="store", type="string", dest="cpu_name", help="Which CPU to be Check", metavar="cpu or cpu0 or cpu1")
cmd_parser.add_option("-w", "--warning", type="int", action="store", dest="warning_per", help="Exit with WARNING status if higher than the PERCENT of CPU Usage", metavar="Warning Percentage")
cmd_parser.add_option("-c", "--critical", type="int", action="store", dest="critical_per", help="Exit with CRITICAL status if higher than the PERCENT of CPU Usage", metavar="Critical Percentage")
(cmd_options, cmd_args) = cmd_parser.parse_args()

if not (cmd_options.local_address and cmd_options.cpu_name and cmd_options.warning_per and cmd_options.critical_per):
    cmd_parser.print_help()
    sys.exit(3)

class CollectStat:
    """Object to Collect CPU Statistic Data"""
    def __init__(self,cpu_name):
        for line in open("/proc/stat"):
            line = line.strip()
            if line.startswith(cpu_name):
                cpustat=line.split()
                cpustat.pop(0)                  # Remove the First Array of the Line 'cpu'
                cpustat=map(float, cpustat)     # Convert the Array to Float
                self.cpu_stat_dict = {}
                for i in range(len(cpustat)):
                    self.cpu_stat_dict[cpu_stat_var_array[i]] = cpustat[i]
                self.total = 0
                for i in cpustat:
                    self.total += i
                break

initial_stat = CollectStat(cmd_options.cpu_name)
time.sleep(sample_interval)
final_stat = CollectStat(cmd_options.cpu_name)

cpu_total_stat = final_stat.total - initial_stat.total

cpu_stat_map = {}

for cpu_stat_var,cpu_stat in final_stat.cpu_stat_dict.items():
    cpu_stat_map[cpu_stat_var] = ((final_stat.cpu_stat_dict[cpu_stat_var] - initial_stat.cpu_stat_dict[cpu_stat_var])/cpu_total_stat)*100 

cpu_usage_percent = cpu_stat_map['user'] + cpu_stat_map['nice'] + cpu_stat_map['system'] + cpu_stat_map['iowait'] + cpu_stat_map['irq'] + cpu_stat_map['softirq'] + cpu_stat_map['steal_time']


# Check if CPU Usage is Critical/Warning/OK
if cpu_usage_percent >= cmd_options.critical_per:
    return_code = pynsca.CRITICAL
    plugin_output = 'STATISTICS CRITICAL : '
elif  cpu_usage_percent >= cmd_options.warning_per:
    return_code = pynsca.WARNING
    plugin_output = 'STATISTICS WARNING : '
else:
    return_code = pynsca.OK
    plugin_output = 'STATISTICS OK : '

plugin_output += 'user=%(user).2f%% system=%(system).2f%% iowait=%(iowait).2f%% stealed=%(steal_time).2f%% idle=%(idle).2f%% | user=%(user).2f%%;;;; system=%(system).2f%%;;;; iowait=%(iowait).2f%%;;;; stealed=%(steal_time).2f%%;;;; idle=%(idle).2f%%;;;;' % cpu_stat_map

#print plugin_output
nscaClient = pynsca.NSCANotifier(nagios_address)
nscaClient.svc_result(cmd_options.local_address, service_description, return_code, plugin_output)


