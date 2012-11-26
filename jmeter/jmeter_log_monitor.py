import random, time, threading
import pynsca
import log_watcher



class JMeterLogMonitor(threading.Thread):

    def __init__(self, localIP=None, nagiosIP=None, logfileName=None, interval=None):
        self.latencyRatio = 0.95
        self.label_result_map = {}
        self.localIP = localIP
        self.nscaSender = pynsca.NSCANotifier(nagiosIP)
        self.interval = interval
        self.warning_map = {"latency" : 0, "failrate" : 0}
        self.critical_map = {"latency" : 0, "failrate" : 0}
        self.logfileName = logfileName
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        
    def run(self):
        self.logWatcher = log_watcher.LogWatcher(self.logfileName, self.statistic)
        while not self.stopped():
            start = time.time()
            self.logWatcher.loop(async=True)
            self.label_result_map.clear()
            end = time.time()
            if self.interval > (end - start):
                time.sleep(self.interval-(end-start))
            else:
                pass
    
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def statistic(self, logname, records):
        for record in records:
            #print record
            label, success, latency = self.parseRecord(record.strip())
            if label in self.label_result_map:
                self.label_result_map[label]["latency"].append(latency)
                self.label_result_map[label]["success"].append(success)
            else:
                self.label_result_map[label] = {"latency": [latency], "success": [success]}

        for label in self.label_result_map:
            latency = self.selectLatency(self.label_result_map[label]["latency"])
            failrate = self.calculateFailrate(self.label_result_map[label]["success"])
            latency_output = "latency=%d | latency=%d;%d;%d;0;" %\
                (latency, latency, self.warning_map["latency"], self.critical_map["latency"])
            return_code = pynsca.OK
            if self.critical_map["latency"] != 0 and latency > self.critical_map["latency"]:
                return_code = pynsca.CRITICAL
            elif self.warning_map["latency"] != 0 and latency > self.warning_map["latency"]:
                return_code = pynsca.WARNING
            self.nscaSender.svc_result(self.localIP, "Latency", return_code, latency_output)
            print latency_output

            failrate_output = "failrate=%.2f%% | failrate=%.2f%%;%d;%d;0; " %\
                (failrate, failrate, self.warning_map["failrate"], self.critical_map["failrate"])
            return_code = pynsca.OK
            if self.critical_map["failrate"] != 0 and failrate > self.critical_map["failrate"]:
                return_code = pynsca.CRITICAL
            elif self.warning_map["failrate"] != 0 and failrate > self.warning_map["failrate"]:
                return_code = pynsca.WARNING
            self.nscaSender.svc_result(self.localIP, "Failrate", return_code, failrate_output)
            print failrate_output

    def parseRecord(self, record):
        tokens = record.split(",")
        if len(tokens) == 6 and \
             tokens[0].isdigit() and tokens[5].isdigit():
            return tokens[1], tokens[4], int(tokens[5])
        else:
            return None

    def selectLatency(self, latencies):
        if len(latencies) > 1:
            index = int(len(latencies) * self.latencyRatio)
            return self._quickSelect(latencies, 0, len(latencies)-1, index-1)
        else:
            return latencies[0]

    def calculateFailrate(self, results):
        failnum = results.count("false")
        return float(failnum*100)/ len(results)
         
    def _quickSelect(self, array, left, right, k):
        while True:
            pivotIndex = random.randint(left, right)
            pivotNewIndex = self._partition(array, left, right, pivotIndex)
            if pivotNewIndex == k:
                return array[pivotNewIndex]
            elif pivotNewIndex > k:
                right = pivotNewIndex - 1
            else:
                left = pivotNewIndex + 1
            #print "round", left, "---", right

    def _partition(self, array, left, right, pivotIndex):
        pivotValue = array[pivotIndex]
        array[pivotIndex], array[right] = array[right], array[pivotIndex]
        storeIndex = left
        for i in range(left, right):
            if array[i] <= pivotValue:
                array[i], array[storeIndex] = array[storeIndex], array[i]
                storeIndex += 1        
        array[right], array[storeIndex] = array[storeIndex], array[right]
        return storeIndex
