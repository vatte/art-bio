import pynexus
import time

class DataLogger:
	def __init__(self, _channels):
		self.btaddress = "00:07:80:40:89:F6"
		self.Fs = 128
		self.channels = _channels		
		self.buffer = []
		for i in range(len(_channels)):
			self.buffer.append([])
		self.f = None
		self.logging = False
		self.trigger = None
		self.t = 0
		self.t_start = 0

	def start(self):
		try:
			self.dev = pynexus.Nexus(self.btaddress)
			print "SAMPLE RATE:", self.dev.setFs(self.Fs)
			#doesn't seem to affect the samples received which are always 512 /s, but only 1/4 valid...
		
			for sample in self.dev:
				#t=time.time()
				#print sample
				if sample.get('Battery') > 1: #t-t2 > 0.001: #to find the real sample
					#t2 = t
					
					#writing to log file and filling buffer
					if self.logging:
						self.t=time.time()-self.t_start
						self.f.write(str(self.t) + '\t')
				
					buff_i = 0
					for name in self.channels:
						value = sample.get(name)
						if value:
							#print name, ' ', value
							if self.logging:
								self.f.write(str(value) + '\t')
							self.buffer[buff_i].append(value)
							buff_i += 1
					if self.logging:
						if self.trigger:
							self.f.write(self.trigger)
							self.trigger = None
						self.f.write('\n')
					#print sample
		except KeyboardInterrupt:
			self.quit()
	
	def get_buffer(self):
		return_buffer = self.buffer[:]
		for i in range(len(self.buffer)):
			self.buffer[i] = []
		return return_buffer 
	
	def set_filename(self, _filename):
		self.f = open(_filename, 'w')
		
		self.f.write('time\t')
		for name in self.channels:
			if name in self.dev.chan_names:
				self.f.write(name + '\t')
		self.f.write('trigger')
		self.f.write('\n')
	
	def start_logging(self):	
		self.t_start = time.time()
		self.t = 0
		self.logging = True
	
	def stop_logging(self):
		self.logging = False
		self.f.close()
		
	def send_trigger(self, label):
		self.trigger = label
		
	def quit(self):
		self.dev.close()
		self.f.close()

#	if __name__ == "__main__":
#		try:
#			main()
#		except KeyboardInterrupt:
#			print "Interrupted by user."
#			quit()


