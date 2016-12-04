import threading, time, random
class Counter(threading.Thread):
	def __init__(self, lock, threadName):


		super(Counter, self).__init__(name = threadName)
		self.lock = lock
		self.c = 0
		self.s = True;
	
	def run(self):
		self.lock.acquire()
		while self.s:
			self.c += 1;
			print self.c
			if self.c > 50:
				break;
			time.sleep(1)
		self.lock.release()
	def aha(self):
		self.s = False
lock = threading.Lock()

count = Counter(lock, "test")
count.start()
time.sleep(5)
count.aha()

lock.acquire()
print "threading executes complete"

lock.release()