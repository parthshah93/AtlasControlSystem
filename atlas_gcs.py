#!/usr/bin/env python

import socket, json, os, time
import threading, Queue
import atlas_parser, atlas_socket
import pygame
	

def putincommand(data):
	if not connection_break:
		command_buffer_lock.acquire()
		command_buffer.put(data)
		command_buffer_lock.release()

def linear_remap_signed(dead_zone, input_data):
	if input_data > -dead_zone and input_data < dead_zone:
		return 127
	if input_data > 0:
		return (input_data - dead_zone) * 127 / (1000 - dead_zone) + 127
	if input_data < 0:
		return 127 - (-input_data - dead_zone) * 127 / (1000 - dead_zone)

# while True:
# 	if not ui_buffer.empty():
# 		dic = ui_buffer.get()
# 		if 'type' in dic:
# 			print dic['type']
# 	else:
# 		print "connection okay"
# 	time.sleep(2)

# Program Initialization
socket_to_parser = Queue.Queue(maxsize = -1)
parser_to_socket = Queue.Queue(maxsize = -1)
command_buffer = Queue.Queue(maxsize = -1)
ui_buffer = Queue.Queue(maxsize = -1)

command_buffer_lock = threading.Lock()

target_ip = "192.168.1.121"
target_port = 10010
local_ip = "192.168.1.100"
local_port = 10010

connection_break = False

socket_thread = atlas_socket.AtlasSocket("thread-socket", parser_to_socket, socket_to_parser, target_ip, target_port, local_ip, local_port, 30, 10)
parser_thread = atlas_parser.AtlasParser("thread-parser", socket_to_parser, parser_to_socket, command_buffer, command_buffer_lock, ui_buffer, 20)

socket_thread.start()
parser_thread.start()

socket_thread.socket_start()

# look at the ethernet connection condition
# if(connection breaks)
# 	socket.socket_destroy;
# if(connection recovered)
# 	socket.start();
# PyGame Initialization
pygame.init()
pygame.joystick.init()
pygame.display.set_caption('Keyboard Capture')
size = [100, 100]
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

# Variable Initialization
done = False
mode = ''
keyboard_speed_setting_toggle = False
joystick_speed_setting_toggle = False
speed_list = {'straightforward':[255,255], 'right':[255,0], 'backward':[0,0], 'left':[0,255]}
dead_zone_joystick = 150
axis_change_th = 20
x_axis_pre = 0
y_axis_pre = 0
x_axis_raw = 0
y_axis_raw = 0
x_axis_remapped = 0
y_axis_remapped = 0
x_axis_home = False
y_axis_home = False

# Main loop
while done == False:
	if not ui_buffer.empty():
		ui_data = ui_buffer.get()
		if ui_data['type'] == "connection_break":
			connection_break = True
		else:
			connection_break = False
	for event in pygame.event.get(): # User did something
		if event.type == pygame.QUIT: # If user clicked close
			done=True # Flag that we are done so we exit this loop
			socket_thread.socket_destroy() # Destroy socket_thread to ensure opened port be closed properly
		# Get keyboard input
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				mode = 'straightforward'
				keyboard_speed_setting_toggle = True
				print "Forward pressed"
			elif event.key == pygame.K_d:
				mode = 'right'
				print "Right pressed"
				keyboard_speed_setting_toggle = True
			elif event.key == pygame.K_s:
				mode = 'backward'
				print "Backward pressed"
				keyboard_speed_setting_toggle = True
			elif event.key == pygame.K_a:
				mode = 'left'
				print "Left pressed"
				keyboard_speed_setting_toggle = True
		if event.type == pygame.KEYUP:
			mode = ''
			print "Key released"
			keyboard_speed_setting_toggle = True
		# Get joystick number
		joystick_count = pygame.joystick.get_count()
		# print joystick_count
		if joystick_count:
			joystick = pygame.joystick.Joystick(0)
			joystick.init()
			x_axis_raw = -1000 * joystick.get_axis(0)
			y_axis_raw = -1000 * joystick.get_axis(1)
			# print x_axis_raw, " ", y_axis_raw
			if not int(linear_remap_signed(dead_zone_joystick, x_axis_raw)) and not x_axis_home:
				joystick_speed_setting_toggle = True
				keyboard_speed_setting_toggle = False
				x_axis_home = True
				x_axis_remapped = 0
			elif abs(x_axis_raw - x_axis_pre) > axis_change_th:
				joystick_speed_setting_toggle = True
				keyboard_speed_setting_toggle = False
				x_axis_home = False
				x_axis_remapped = int(linear_remap_signed(dead_zone_joystick, x_axis_raw))
			if not int(linear_remap_signed(dead_zone_joystick, y_axis_raw)) and not y_axis_home:
				joystick_speed_setting_toggle = True
				keyboard_speed_setting_toggle = False
				y_axis_home = True
				y_axis_remapped = 0
			elif abs(y_axis_raw - y_axis_pre) > axis_change_th:
				joystick_speed_setting_toggle = True
				keyboard_speed_setting_toggle = False
				y_axis_home = False
				y_axis_remapped = int(linear_remap_signed(dead_zone_joystick, y_axis_raw))
			x_axis_pre = x_axis_raw
			y_axis_pre = y_axis_raw
	if joystick_speed_setting_toggle:
		send_data = []
		send_data.append({'name': 'W/R Motor0', 'value': x_axis_remapped})
		send_data.append({'name': 'W/R Motor1', 'value': y_axis_remapped})
		putincommand(send_data)
		joystick_speed_setting_toggle = False
	if keyboard_speed_setting_toggle:
		send_data = []
		if not mode == '':
			send_data.append({'name': 'W/R Motor0', 'value': speed_list[mode][0]})
			send_data.append({'name': 'W/R Motor1', 'value': speed_list[mode][1]})
			putincommand(send_data)
		else:
			send_data.append({'name': 'W/R Motor0', 'value': 127})
			send_data.append({'name': 'W/R Motor1', 'value': 127})
			putincommand(send_data)
		keyboard_speed_setting_toggle = False
	pygame.display.flip()
	clock.tick(60)
