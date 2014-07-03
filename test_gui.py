from threading import Thread
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button

from Tkinter import Tk
from tkFileDialog import *

from pygame import mixer

from DataLogger import DataLogger
from physiology.SkinConductance import SkinConductance
from physiology.HeartRate import HeartRate

#have Tkinter-window not appearing
Tk().withdraw()

#init pygame mixer for music playback
mixer.init(frequency=44100)
mixer.music.playing = False

#start datalogger thread
datalogger = DataLogger(['A', 'B', 'F', 'G'])
t = Thread(target=datalogger.start)
t.start()


#initialize ANS real-time analysis modules
sc = SkinConductance(128, 16, -0.01, 64, 128)
hr = HeartRate(128, 1)



#animation parameters
y_length = 2560
fig = plt.figure()
fig.subplots_adjust(bottom=0.2)
ax = fig.add_subplot(311)
#time = []
#for i in range(y_length):
#	time.append(i/128)
data = [0]*y_length
line, = ax.plot(data)
rectangles = []
ax2 = fig.add_subplot(312)
data2 = [0]*y_length
line2, = ax2.plot(data2)
ax3 = fig.add_subplot(313)
data3 = [0]*y_length
line3, = ax3.plot(data3)

time_music = plt.figtext(0.35, 0.075, '00:00:00')
time_music.time = 0
time_data = plt.figtext(0.72, 0.075, '00:00:00')
time_data.time = 0
IBI_txt = plt.figtext(0.5, 0.5, 'IBI: 0')

#method for loading new data for analysis and updating 
def load_buffer(_data, _data2, _data3):
	buff = datalogger.get_buffer()
	
	l_buff = len(buff[2])
	del _data[:l_buff]
	_data.extend(buff[2])
	
	ekg = [a - b for (a, b) in zip(buff[0], buff[1])]
	
	del _data2[:len(ekg)]
	_data2.extend(ekg)
	
	del _data3[:len(buff[3])]
	_data3.extend(buff[3])
	
	beats = hr.add_data(ekg)
	if beats:
		IBI_txt.set_text("IBI: {0}".format(beats[-1]))
	
	update_rectangles(sc.add_data(buff[2]), l_buff)

#updates the rectangles that indicate responses in skin conductance plot
def update_rectangles(new_responses, l_new_data):
	for i in reversed(range(len(rectangles))):
		x = rectangles[i].get_x()
		x -= l_new_data
		if x < -rectangles[i].get_width():
			rectangles[i].remove()
			del rectangles[i]
		else:
			rectangles[i].set_x(x)
	if new_responses:
		l = len(new_responses)
		#print l
		for i in range(l):
			rectangles.append(Rectangle([y_length - (len(sc.filtered_data) - new_responses[i][0]), sc.filtered_data[new_responses[i][0]]], new_responses[i][1], new_responses[i][2], facecolor='None', edgecolor='red') )
			ax.add_patch(rectangles[-1])

#update lines and axes-limits for animation and check for music playback
def update(a):
	load_buffer(data, data2, data3)
	
	line.set_ydata(data)
	ax.set_ylim(min(data)-20, max(data)+20)

	line2.set_ydata(data2)
	ax2.set_ylim(min(data2)-20, max(data2)+20)
	
	line3.set_ydata(data3)
	ax3.set_ylim(min(data3)-20, max(data3)+20)
	
	if mixer.music.playing:
		if not mixer.music.get_busy():
			stop_music(None)
		else:
			time_music.time = int(mixer.music.get_pos()/1000)
	else:
		if time_music.time == 0:
			time_music.t0 = time.time()
		time_music.time = time.time() - time_music.t0
	time_music.set_text("{0:02}:{1:02}:{2:02}".format(int(time_music.time/3600), int(time_music.time/60)%60, int(time_music.time)%60))
	time_data.set_text("{0:02}:{1:02}:{2:02}".format(int(datalogger.t/3600), int(datalogger.t/60)%60, int(datalogger.t)%60))
		


	
#ani = animation.FuncAnimation(fig, update, fargs=(data, line, ax), interval=100)
ani = animation.FuncAnimation(fig, update, interval=50)


#buttons start

def load_music(event):
	print 'Load music'
	mixer.music.filename = askopenfilename()
	mixer.music.load(mixer.music.filename)
	
	b_music.label.set_text('Play music')
	b_music.disconnect(b_music.cid)
	b_music.cid = b_music.on_clicked(play_music)

def play_music(event):
	print 'Play music', mixer.music.filename
	mixer.music.play()
	mixer.music.playing = True
	datalogger.send_trigger(mixer.music.filename)
	
	b_music.label.set_text('Stop music')
	b_music.disconnect(b_music.cid)
	b_music.cid = b_music.on_clicked(stop_music)
	
def stop_music(event):
	print 'Stop music'
	if(event):
		mixer.music.stop()
	datalogger.send_trigger('stopped')
	mixer.music.playing = False
	time_music.time = 0
	
	b_music.label.set_text('Load music')
	b_music.disconnect(b_music.cid)
	b_music.cid = b_music.on_clicked(load_music)


def data_path(event):
	print 'Set data path'
	
	filename = asksaveasfilename()
	datalogger.set_filename(filename)
	
	b_data.label.set_text('Record data')
	b_data.color = 'red'
	b_data.disconnect(b_data.cid)
	b_data.cid = b_data.on_clicked(start_recording)

def start_recording(event):
	print 'Start recording'
	
	datalogger.start_logging()
	
	b_data.label.set_text('Stop recording')
	b_data.color = 'gray'
	b_data.disconnect(b_data.cid)
	b_data.cid = b_data.on_clicked(stop_recording)
	
def stop_recording(event):
	print 'Stop recording'
	
	datalogger.stop_logging()
	
	b_data.label.set_text('Data path')
	b_data.color = '0.85'
	b_data.disconnect(b_data.cid)
	b_data.cid = b_data.on_clicked(data_path)

ax_music = plt.axes([0.13, 0.05, 0.2, 0.075])
ax_data = plt.axes([0.5, 0.05, 0.2, 0.075])
b_music = Button(ax_music, 'Load music')
b_music.cid = b_music.on_clicked(load_music)
b_data = Button(ax_data, 'Data path')
b_data.cid = b_data.on_clicked(data_path)

#buttons end



plt.show()





