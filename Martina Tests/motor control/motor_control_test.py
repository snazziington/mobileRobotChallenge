# Motor control Test

import picar_4wd as fc
import sys
import tty
import termios

speed = 10
key = 'status'
print("If you want to quit.Please press q")

objectPos = 160
target = 180

def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65)

def motor_control():
    while True:
        global speed
        global objectPos
        print("Object X-Position: ", objectPos)
        key=readkey()
        if key=='s':
            print("robot stops")
            fc.stop()
        elif key=='i':
            objectPos = int(input())
        if objectPos >= 170:
            print("turn right")
            
            fc.turn_right(speed)
            objectPos -= 15
        elif objectPos <= 150:
            print("turn left")
            fc.turn_left(speed)
            objectPos += 15
        else: 
            print("object in front")
            fc.forward(speed)

if __name__ == '__main__':
    try:
        motor_control()
    except KeyboardInterrupt:
        print("robot stops")
        fc.stop()






