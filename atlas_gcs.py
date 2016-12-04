#!/usr/bin/env python

import socket, json, os, time
import threading, Queue
import atlas_parser, atlas_socket
import pygame
	

def putincommand(data):
	command_buffer_lock.acquire()
	command_buffer.put(data)
	command_buffer_lock.release()

socket_to_parser = Queue.Queue(maxsize = -1)
parser_to_socket = Queue.Queue(maxsize = -1)
command_buffer = Queue.Queue(maxsize = -1)
ui_buffer = Queue.Queue(maxsize = -1)

command_buffer_lock = threading.Lock()

target_ip = "127.0.0.1"
target_port = 10086
local_ip = "127.0.0.1"
local_port = 8469

socket_thread = atlas_socket.AtlasSocket("thread-socket", parser_to_socket, socket_to_parser, target_ip, target_port, local_ip, local_port, 5, 10)
parser_thread = atlas_parser.AtlasParser("thread-parser", socket_to_parser, parser_to_socket, command_buffer, command_buffer_lock, ui_buffer, 5)

socket_thread.start()
parser_thread.start()

socket_thread.socket_start()

# while True:
# 	if not ui_buffer.empty():
# 		dic = ui_buffer.get()
# 		if 'type' in dic:
# 			print dic['type']
# 	else:
# 		print "connection okay"
# 	time.sleep(2)

pygame.init()
pygame.display.set_caption('Keyboard Capture')
size = [100, 100]
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
done = False
mode = ''
speed_setting_toggle = True
speed_list = {'straightforward':[127,127], 'right':[127,255], 'backward':[255,255], 'left':[255,127]}
while done == False:
	for event in pygame.event.get(): # User did something
		if event.type == pygame.QUIT: # If user clicked close
			done=True # Flag that we are done so we exit this loop
			socket_thread.socket_destroy()
		# Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				mode = 'straightforward'
				speed_setting_toggle = True
				print "Forward pressed"
			elif event.key == pygame.K_d:
				mode = 'right'
				print "Right pressed"
				speed_setting_toggle = True
			elif event.key == pygame.K_s:
				mode = 'backward'
				print "Backward pressed"
				speed_setting_toggle = True
			elif event.key == pygame.K_a:
				mode = 'left'
				print "Left pressed"
				speed_setting_toggle = True
		if event.type == pygame.KEYUP:
			mode = ''
			print "Key released"
			speed_setting_toggle = True
	
	if speed_setting_toggle:
		send_data = []
		if not mode == '':
			send_data.append({'name': 'W/R Motor0', 'value': speed_list[mode][0]})
			send_data.append({'name': 'W/R Motor1', 'value': speed_list[mode][1]})
			putincommand(send_data)
		else:
			send_data.append({'name': 'W/R Motor0', 'value': 0})
			send_data.append({'name': 'W/R Motor1', 'value': 0})
			putincommand(send_data)
		speed_setting_toggle = False
	pygame.display.flip()
	clock.tick(60)

