
import pynsca
import log_watcher
import daemon
import time

class ResponderLogMonitor(daemon.Daemon):
    def __init__(self, localIP, nagiosIP, logfilename, interval,\
            pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        daemon.Daemon.__init__(self, pidfile, stdin, stdout, stderr)
        self.localIP = localIP
        self.interval = interval
        self.logfilename = logfilename
        self.nscaSender = pynsca.NSCANotifier(nagiosIP)
        self.label_result_map = {}

    def _run(self):
        self.logWatcher = log_watcher.LogWatcher(self.logfilename, self.statistic)
        while True:
            start = time.time()
            self.logWatcher.loop()
            self.label_result_map.clear()
            end = time.time()
            if self.interval > (end - start):
                time.sleep(self.interval-(end-start))
            else:
                print "error: timeout ", end-start, "\n"
    
    def statistic(self, logname, records):
        for i in range(len(records)-1, -1, -1):
            label, tps = self.parseRecord(records[i].strip())
            if label:
                if label in self.label_result_map:
                    self.label_result_map[label] = tps
                else:
                    self.label_result_map[label] = tps
        for label in self.label_result_map:
            output1 = "TPS_" + label + "=%(" + label + ")s, "
            output2 = "TPS_" + label + "=%(" + label + ")s;;;0; "
            output = (output1 + "| " + output2) % self.label_result_map
            return_code = pynsca.OK
            self.nscaSender.svc_result(self.localIP, label, return_code, output)
            print output

    def parseRecord(self, record):
        tokens = record.split(" ")
        #label, nu = tokens[2].split(":")
        if len(tokens) >= 6:
            return tokens[2], tokens[5]
        else:
            return None, None
