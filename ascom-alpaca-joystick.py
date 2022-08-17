import pygame
import time
import pygame.display
import pygame.joystick
from pygame.locals import *

# Import the Telescope class.
from alpaca import telescope
# Initialize a Telescope object with 0 as the device number.
t = telescope.Telescope('192.168.88.18:11111', 0)
print("At home", t.AtHome)
print("At park", t.AtPark)
print("At park", t.CanFindHome)
print("AxisRates axisPrimary", t.AxisRates(telescope.TelescopeAxes.axisPrimary)[0].maxv)
print("AxisRates axisSecondary", t.AxisRates(telescope.TelescopeAxes.axisSecondary)[0].maxv)

print("Tracking", t.Tracking)
print("Slewing", t.Slewing)

print("SupportedActions", t.SupportedActions)
print("Connected", t.Connected)
print("CommandString Get", t.CommandString(":GC#", True))

pygame.display.init()

pygame.joystick.init() #initialize joystick module
pygame.joystick.get_init() #verify initialization (boolean)

joystick_count = pygame.joystick.get_count()#get number of joysticks
print('%d joystick(s) connected' %joystick_count)#print number

joystick_object = pygame.joystick.Joystick(0)
#create an instance of a joystick
#first joystick is [0] in the list
#haven't had much luck with multiple joysticks

joystick_object.get_name()
print (joystick_object.get_name())
#grab joystick name - flightstick, gravis...
#can (and is in this case) be done before initialization

joystick_object.init()

joystick_object.get_init()
#verify initialization (maybe cool to do some
#error trapping with this so game doesn't crash

num_axes = joystick_object.get_numaxes()
num_buttons = joystick_object.get_numbuttons()

print ('Joystick has %d axes and %d buttons' %(num_axes,num_buttons))

pygame.event.pump()
#necessary for os to pass joystick events

xaxis = joystick_object.get_axis(0)
yaxis = joystick_object.get_axis(1)
print ('%f %f' %(xaxis, yaxis))

done = False
deadzone = 0.1
clock = pygame.time.Clock()
speedMode = 2
countParkPushDown = 0

Rate = {
    "0": 0,
    "1": 0,
    "2": 0,
    "3": 0,
}

Move = {
    "0": False,
    "1": False,
    "2": False,
    "3": False
}

def moving(axisint, TelescopeAxes, delay, addRate):
    axis = str(axisint)
    axis_pos = joystick_object.get_axis(axisint) * addRate

    if axis_pos < -1 * deadzone:
        # print('Throttle Up2', axis_pos)
        if  not t.AtPark and (not Move[axis] or abs(axis_pos ) != abs(Rate[axis])):
            Move[axis] = True
            Rate[axis] = axis_pos
            print('New Rate axis', axis, abs(Rate[axis]))
            t.MoveAxis(TelescopeAxes, Rate=0)
            time.sleep(delay)
            t.MoveAxis(TelescopeAxes, Rate=Rate[axis])
    elif axis_pos > deadzone:
        # print('Throttle Down2', axis_pos)
        if not t.AtPark and (not Move[axis] or abs(axis_pos) != abs(Rate[axis])):
            Move[axis] = True
            Rate[axis] = axis_pos
            print('New Rate axis', axis, abs(Rate[axis]))
            t.MoveAxis(TelescopeAxes, Rate=0)
            time.sleep(delay)
            t.MoveAxis(TelescopeAxes, Rate=Rate[axis])
    else:
        if Move[axis]:
            Move[axis] =  False
            Rate[axis] = 0
            print('Stop', axis)
            t.MoveAxis(TelescopeAxes, Rate=Rate[axis])

def buttonHome(buttonID):
    if joystick_object.get_button(buttonID) and t.CanFindHome:
        print("Find homee", t.FindHome())
        time.sleep(0.5)

def buttonPark(buttonID, count):
    if joystick_object.get_button(buttonID):
        if count > 4 and t.CanSetPark:
            if t.CanSetPark and not t.AtPark:
                print("SetPark", t.SetPark(), count)
                time.sleep(0.5)
                return 0
            else:
                print("SetPark problem")

        if t.AtPark:
            if t.CanUnpark:
                print("Unpark", t.Unpark(), count)
                time.sleep(0.5)
            else:
                print("Unpark problem")
        else: 
            if t.CanPark and not t.Slewing:
                print("Park", t.Park(), count)
                time.sleep(0.5)
                count += 1
            else:
                print("Park problem")
    return count
    


while not done:

    clock.tick(1000)
    delay = 0.01
    time.sleep(delay)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True


    buttonHome(8)
    countParkPushDown = buttonPark(9, countParkPushDown)

    

    if joystick_object.get_button(10):
        if speedMode == 2:
            print("LOW SPEED")
            speedMode = 0.25
            time.sleep(1)
        else:
            print("HIGH SPEED")
            speedMode = 2
            time.sleep(1)
    if t.CanMoveAxis:
        moving(0, telescope.TelescopeAxes.axisPrimary, delay, speedMode)
        moving(1, telescope.TelescopeAxes.axisSecondary, delay, speedMode)
    else:
        time.sleep(1)

    # moving(2, telescope.TelescopeAxes.axisPrimary, delay, 0.5)
    # moving(3, telescope.TelescopeAxes.axisSecondary, delay, 0.5)


joystick_object.quit()
#destroy objects and clean up
pygame.joystick.quit()
