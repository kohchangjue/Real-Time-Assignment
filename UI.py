import tkinter as Tkinter
from tello_sim import Simulator
import sys
from time import sleep
import Schedular2 as schedular
import threading

root = Tkinter.Tk()
move_by = 10
drone = schedular.drone
root.title("GUI Example")
task_id=5000
rms=schedular.RMS()
# Functions
def increase_movement_speed():
	global move_by
	move_by  += 2
	print("New speed : " + str(move_by))

def decrease_movement_speed():
	global move_by
	if move_by <= 5:
		pass
	else:
		move_by -= 2
	print("New speed : " + str(move_by))

def take_off():
	global task_id
	print("Taking off")
	rms.insertInterruptTask(rms.current_time,task_id,["takeoff"])
	task_id=task_id+1
	sleep(3)

def land():
	global task_id
	print("Landing")
	rms.insertInterruptTask(rms.current_time,task_id,["land"])
	task_id=task_id+1
	# sys.exit()

def go_up():
	global task_id
	print("Going Up")
	rms.insertInterruptTask(rms.current_time,task_id,["up", 20])
	task_id=task_id+1

def go_down():
	global task_id
	print("Going Down")
	rms.insertInterruptTask(rms.current_time,task_id,["down", 20])
	task_id=task_id+1

def go_left():
	global task_id
	print("Going Left")
	rms.insertInterruptTask(rms.current_time,task_id,["left", move_by])
	rms.insertInterruptTask(rms.current_time,task_id,["right", round(move_by/10)])
	task_id=task_id+1

def go_right():
	global task_id
	print("Going Right")
	rms.insertInterruptTask(rms.current_time,task_id,["right", move_by])
	rms.insertInterruptTask(rms.current_time,task_id,["left", round(move_by/10)])
	task_id=task_id+1

def go_forward():
	global task_id
	print("Going Forward")
	rms.insertInterruptTask(rms.current_time,task_id,["forward", move_by])
	task_id=task_id+1

def go_backward():
	global task_id
	print("Going Backward")
	rms.insertInterruptTask(rms.current_time,task_id,["backward", move_by])
	task_id=task_id+1

def rotate_clockwise():
	global task_id
	print("Rotating clockwise")
	rms.insertInterruptTask(rms.current_time,task_id,["cw", move_by])
	task_id=task_id+1

def rotate_counter_clockwise():
	global task_id
	print("Rotating counter clockwise")
	rms.insertInterruptTask(rms.current_time,task_id,["ccw", move_by])
	task_id=task_id+1

def predefined_route():
	rms.buildSchedule()


def build_predefined_route():
	rms.build_predefined_route(rms.current_time)

# GUI
lbl_op = Tkinter.Label(root, text="Flight Control")
lbl_op.pack()


# Increase Speed
btn_increase_speed = Tkinter.Button(root, text="Increase", command=increase_movement_speed)
btn_increase_speed.pack()

# Increase Speed
btn_decrease_speed = Tkinter.Button(root, text="Decrease", command=decrease_movement_speed)
btn_decrease_speed.pack()

# Take off
btn_take_off = Tkinter.Button(root, text="TakeOff", command=take_off)
btn_take_off.pack()

# Land
btn_land = Tkinter.Button(root, text="Land", command=land)
btn_land.pack()

# Up
btn_go_up = Tkinter.Button(root, text="Go Up", command=go_up)
btn_go_up.pack()

# Down
btn_go_down = Tkinter.Button(root, text="Go Down", command=go_down)
btn_go_down.pack()

# Left
btn_go_left = Tkinter.Button(root, text="Go Left", command=go_left)
btn_go_left.pack()

# Right
btn_go_right = Tkinter.Button(root, text="Go Right", command=go_right)
btn_go_right.pack()

# CW
btn_go_cw = Tkinter.Button(root, text="Rotate Clockwise", command=rotate_clockwise)
btn_go_cw.pack()

# CCW
btn_go_ccw = Tkinter.Button(root, text="Rotate Counter Clockwise", command=rotate_counter_clockwise)
btn_go_ccw.pack()


# Forward
btn_go_forward = Tkinter.Button(root, text="Go forward", command=go_forward)
btn_go_forward.pack()

# Forward
btn_go_backward = Tkinter.Button(root, text="Go Backward", command=go_backward)
btn_go_backward.pack()

# Run Predefined Route
btn_predefined = Tkinter.Button(root, text="Predefined Route", command=build_predefined_route)
btn_predefined.pack()


threading.Thread(target=predefined_route).start()
root.mainloop()

