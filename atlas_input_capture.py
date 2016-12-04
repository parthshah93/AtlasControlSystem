#!/usr/bin/env python

import socket, json, os, time
import threading, Queue
import pygame

class AtlasInputCapture(threading.Thread):
	def __init__(self, threadName, refresh_rate = 20):
		# self.output_buffer = output_buffer
		self.refresh_rate = refresh_rate
		pygame.init()
		pygame.display.set_caption('Keyboard Capture')
		size = [100, 100]
		screen = pygame.display.set_mode(size)
		super(AtlasInputCapture, self).__init__(name = threadName)
	def run(self):
		while True:
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					print event.key + "pressed"
				if event.type == pygame.KEYUP:
					print event.key + "released"
			time.sleep(1.0 / self.refresh_rate)

capture = AtlasInputCapture("keyboardtest", 20)

capture.start()
