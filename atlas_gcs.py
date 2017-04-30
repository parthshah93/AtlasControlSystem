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

def linear_remap(input_data):
	if input_data >= 0:
		return (input_data / 1000.0) * 126 + 127
	if input_data < 0:
		return 127 + (input_data / 1000.0) * 126

def dead_zone_remove(dead_zone, input_data):
	if input_data > -dead_zone and input_data < dead_zone:
		return 0
	if input_data > 0:
		return ((input_data - dead_zone) / (1000.0 - dead_zone)) * 1000
	if input_data < 0:
		return (-(-input_data - dead_zone) / (1000.0 - dead_zone)) * 1000

def restrict_range(n):
	if n >= 1000:
		return 1000
	elif n <= -1000:
		return -1000
	else:
		return n

def mix_control(x_axis, y_axis, wheel):
	x_processed = dead_zone_remove(dead_zone_joystick, x_axis)
	y_processed = dead_zone_remove(dead_zone_joystick, y_axis)
	if wheel == 0 or wheel == 1:
		return int(linear_remap(restrict_range(x_processed + y_processed) * motor_reverse_bit[wheel]))
	if wheel == 2 or wheel == 3:
		return int(linear_remap(-restrict_range(x_processed - y_processed) * motor_reverse_bit[wheel]))

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

#target_ip = "192.168.1.120"
#target_port = 10010
#local_ip = "192.168.1.100"
#local_port = 10010

target_ip = "127.0.0.1"
target_port = 10086
local_ip = "127.0.0.1"
local_port = 8469

connection_break = False

socket_thread = atlas_socket.AtlasSocket("thread-socket", 
											parser_to_socket, 
											socket_to_parser, 
											target_ip, 
											target_port, 
											local_ip, 
											local_port, 30, 10)
parser_thread = atlas_parser.AtlasParser("thread-parser", 
											socket_to_parser, 
											parser_to_socket, 
											command_buffer, 
											command_buffer_lock, 
											ui_buffer, 20)

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
belt_mode = ''
scissor_mode = ''
keyboard_speed_setting_toggle = False
joystick_speed_setting_toggle = False
digging_setting_toggle = False
belt_setting_toggle = False
scissor_setting_toggle = False
speed_list = {'straightforward':[255,255,255,255], 'right':[0,0,255,255], 
		'backward':[0,0,0,0], 'left':[255,255,0,0], 'digging':[0,255,255,0], 
		'stop':[127,127,127,127], 'scissor_up':26, 'scissor_down':228, 'scissor_stop': 127, 
		'belt_fwd': 255, 'belt_bwd': 0, 'belt_stop': 127}
motor_reverse_bit = [1, 1, -1, -1]
dead_zone_joystick = 150
axis_change_th = 20
x_axis_pre = 0
y_axis_pre = 0
belt_button_pre = 0
scissor_button_pre = 0
dig_button_pre = 0
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
			elif event.key == pygame.K_q:
				mode = 'digging'
				print "Digging pressed"
				digging_setting_toggle = True
		if event.type == pygame.KEYUP and (event.key == pygame.K_w or event.key == pygame.K_a or event.key == pygame.K_s 
							or event.key == pygame.K_d or event.key == pygame.K_q):
			mode = ''
			print "Key released"
			keyboard_speed_setting_toggle = True
		# Get joystick number
		joystick_count = pygame.joystick.get_count()
		# print joystick_count
		if joystick_count:
			joystick = pygame.joystick.Joystick(0)
			joystick.init()
			x_axis_raw = 1000 * joystick.get_axis(0)
			y_axis_raw = 1000 * joystick.get_axis(1)
			dig_button = joystick.get_button(0)
			belt_button, scissor_button = joystick.get_hat(0)
			# print x_axis_raw, " ", y_axis_raw
			if dig_button == 0 and dig_button_pre == 0:
				if int(linear_remap_signed(dead_zone_joystick, x_axis_raw)) == 127 and not x_axis_home:
					joystick_speed_setting_toggle = True
					keyboard_speed_setting_toggle = False
					x_axis_home = True
					x_axis_remapped = 0
				elif abs(x_axis_raw - x_axis_pre) > axis_change_th and int(linear_remap_signed(dead_zone_joystick, x_axis_raw)) != 127:
					joystick_speed_setting_toggle = True
					keyboard_speed_setting_toggle = False
					x_axis_home = False
					x_axis_remapped = x_axis_raw
					# x_axis_remapped = int(linear_remap_signed(dead_zone_joystick, x_axis_raw))
				if int(linear_remap_signed(dead_zone_joystick, y_axis_raw)) == 127 and not y_axis_home:
					joystick_speed_setting_toggle = True
					keyboard_speed_setting_toggle = False
					y_axis_home = True
					y_axis_remapped = 0
				elif abs(y_axis_raw - y_axis_pre) > axis_change_th and int(linear_remap_signed(dead_zone_joystick, y_axis_raw)) != 127:
					joystick_speed_setting_toggle = True
					keyboard_speed_setting_toggle = False
					y_axis_home = False
					y_axis_remapped = y_axis_raw
					# y_axis_remapped = int(linear_remap_signed(dead_zone_joystick, y_axis_raw))
				if belt_button != belt_button_pre:
					if belt_button == 1:
						belt_mode = 'belt_fwd'
					elif belt_button == -1:
						belt_mode = 'belt_bwd'
					elif belt_button == 0:
						belt_mode = 'belt_stop'
					belt_setting_toggle = True
				if scissor_button_pre != scissor_button:
					if scissor_button == 1:
						scissor_mode = 'scissor_up'
					elif scissor_button == -1:
						scissor_mode = 'scissor_down'
					elif scissor_button == 0:
						scissor_mode = 'scissor_stop'
					scissor_setting_toggle = True

			elif dig_button == 1 and dig_button_pre == 0:
				mode = 'digging'
				joystick_speed_setting_toggle = False
				keyboard_speed_setting_toggle = False
				digging_setting_toggle = True
			elif dig_button == 0 and dig_button_pre == 1:
				mode = 'stop'
				joystick_speed_setting_toggle = False
				keyboard_speed_setting_toggle = False
				digging_setting_toggle = True
			scissor_button_pre = scissor_button
			belt_button_pre = belt_button
			dig_button_pre = dig_button
			x_axis_pre = x_axis_raw
			y_axis_pre = y_axis_raw
	if joystick_speed_setting_toggle or keyboard_speed_setting_toggle \
		or digging_setting_toggle or belt_setting_toggle or scissor_setting_toggle:
		send_data = []
		if joystick_speed_setting_toggle:
			send_data.append({'name': 'W/R Motor0', 'value': mix_control(x_axis_remapped, y_axis_remapped, 0)})
			send_data.append({'name': 'W/R Motor1', 'value': mix_control(x_axis_remapped, y_axis_remapped, 1)})
			send_data.append({'name': 'W/R Motor2', 'value': mix_control(x_axis_remapped, y_axis_remapped, 2)})
			send_data.append({'name': 'W/R Motor3', 'value': mix_control(x_axis_remapped, y_axis_remapped, 3)})
			joystick_speed_setting_toggle = False
		if keyboard_speed_setting_toggle:
			if not mode == '':
				send_data.append({'name': 'W/R Motor0', 'value': speed_list[mode][0]})
				send_data.append({'name': 'W/R Motor1', 'value': speed_list[mode][1]})
				send_data.append({'name': 'W/R Motor2', 'value': speed_list[mode][2]})
				send_data.append({'name': 'W/R Motor3', 'value': speed_list[mode][3]})
			else:
				send_data.append({'name': 'W/R Motor0', 'value': 127})
				send_data.append({'name': 'W/R Motor1', 'value': 127})
				send_data.append({'name': 'W/R Motor2', 'value': 127})
				send_data.append({'name': 'W/R Motor3', 'value': 127})
			keyboard_speed_setting_toggle = False
		if digging_setting_toggle:
			send_data.append({'name': 'W/R Motor0', 'value': speed_list[mode][0]})
			send_data.append({'name': 'W/R Motor1', 'value': speed_list[mode][1]})
			send_data.append({'name': 'W/R Motor2', 'value': speed_list[mode][2]})
			send_data.append({'name': 'W/R Motor3', 'value': speed_list[mode][3]})
			digging_setting_toggle = False
		if belt_setting_toggle:
			send_data.append({'name': 'W/R Servo1', 'value': speed_list[belt_mode]})
			belt_setting_toggle = False
		if scissor_setting_toggle:
			send_data.append({'name': 'W/R Servo0', 'value': speed_list[scissor_mode]})
			scissor_setting_toggle = False
		putincommand(send_data)
	pygame.display.flip()
	clock.tick(60)
pygame.quit ()
