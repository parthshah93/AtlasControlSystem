#!/usr/bin/env python

import socket, json, os, time
import threading, Queue
import struct

class AtlasParser(threading.Thread):
	def __init__(self, threadName, input_buffer, output_buffer, command_buffer, command_buffer_lock, UI_buffer):
		self.input_buffer = input_buffer
		self.output_buffer = output_buffer
		self.command_buffer = command_buffer
		self.command_buffer_lock = self.command_buffer_lock
		self.UI_buffer = UI_buffer
		super(AtlasParser, self).__init__(name = threadName)
	def run(self):
		