from usys import exit
from machine import Pin, I2C, ADC, PWM
from ssd1306 import SSD1306_I2C
import json
import utime

# I2C connection to the display
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

xAxis = ADC(Pin(26))
yAxis = ADC(Pin(27))
sens = ADC(Pin(28))
button = Pin(16, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(13))

# Setup display
oled = SSD1306_I2C(128, 64, i2c)
oled.contrast(255)
oled.fill(0)


# Setup buzzer
buzzer.freq(500)
buzzer.duty_u16(0)



SCREENWIDTH = 128
SCREENHEIGHT = 64


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


# Load textures
global menuart
with open("textures.json", "r") as f:
    menuart = json.load(f)

# Load sounds
with open("tones.json", "r") as f:
    tones = json.load(f)
song = ["E5", "P", "G5", "F5", "G5", "G5", "G5", "G5", "E5", "P", "E5", "F5", "G5", "A5", "G5", "F5", "E5", "P", "D6", "E6",
        "E5", "P", "G5", "F5", "G5", "G5", "G5", "G5", "E5", "P", "E5", "F5", "G5", "A5", "G5", "E5", "E5", "P", "D6", "E6"]

def playtone(frequency):
    buzzer.duty_u16(1000)
    buzzer.freq(frequency)
    
def bequiet():
    buzzer.duty_u16(0)
    
def playsong(mysong):
    for i in range(len(mysong)):
        if (mysong[i] == "P"):
            bequiet()
        else:
            playtone(tones[mysong[i]])
        utime.sleep(0.2)
    bequiet()
#playsong(song)

# Button object
def buttonObj(x, y, textin, selected):
    if selected == False:
        oled.text(textin, x, y, 1)
    elif selected == True:
        oled.fill_rect(x, y, len(textin)*8, 9, 1)
        oled.text(textin, x, y+1, 0)
    else:
        print("oops a fucksy wucksy")


def drawIMG(xpos, ypos, texture):
    for y in range(len(texture)):
        for x in range(len(texture[y])):
            oled.pixel(x+xpos, y+ypos, texture[y][x])
    return


# Draw menu artwork
drawIMG(0, 0, menuart["mainmenu"])

selected = "start"
duration = 69420
gameStatus = "start"

menuMove = 0

while True:
    # Start FPS counter
    start = utime.ticks_ms()

    # Setup controls
    xValue = xAxis.read_u16()
    yValue = yAxis.read_u16()
    buttonValue = button.value()
    xStatus, yStatus = "middle", "middle"
    buttonStatus = "not pressed"
    if xValue <= 600:
        xStatus = "left"
    elif xValue >= 60000:
        xStatus = "right"
    if yValue <= 600:
        yStatus = "up"
    elif yValue >= 60000:
        yStatus = "down"
    if buttonValue == 0:
        buttonStatus = "pressed"
#    print(f"X: {xStatus}, Y: {yStatus} -- button {buttonStatus} -- {1000/duration:.0f}")



    # Start screen
    if gameStatus == "start":

        # Clear non dynamic parts of the screen
        oled.fill_rect(64, 32, 64, 64, 0)
        oled.fill_rect(0, 0, 16, 8, 0)


        if menuMove == 0:
            oled.fill_rect(64, 12, 64, 20, 0)
            drawIMG(64, 14, menuart["crong"])
            menuMove += 1
        elif menuMove == 15:
            oled.fill_rect(64, 14, 64, 20, 0)
            drawIMG(64, 12, menuart["crong"])
            menuMove += 1
        elif menuMove == 30:
            oled.fill_rect(64, 12, 64, 20, 0)
            drawIMG(64, 10, menuart["crong"])
            menuMove += 1
        elif menuMove == 45:
            oled.fill_rect(64, 10, 64, 20, 0)
            drawIMG(64, 12, menuart["crong"])
            menuMove += 1
        elif menuMove == 60:
            menuMove = 0
        else:
            menuMove += 1
#        print(f"{menuMove}")


        if yStatus == "up":
            selected = "start"
        elif yStatus == "down":
            selected = "about"

        if selected == "start":
            buttonObj(64, 35, "Start", True)
            buttonObj(64, 45, "About", False)
            if buttonStatus == "pressed":
                gameStatus = "game"
                
        elif selected == "about":
            buttonObj(64, 35, "Start", False)
            buttonObj(64, 45, "About", True)
            if buttonStatus == "pressed":
                gameStatus = "about"

        # oled.text(f"{selected}:{yValue}",0,0,1)

        # button(64,30,"Start",True)
        # button(64,40,"About",False)

    # About screen
    elif gameStatus == "about":
        oled.fill(0)
        oled.text("About", 40, 20, 1)
        if buttonStatus == "pressed":
            gameStatus = "start"

    # Game screen
    elif gameStatus == "game":
        oled.fill(0)
        oled.text("Game", 40, 20, 1)
        if buttonStatus == "pressed":
            gameStatus = "start"
        # kod

    # Win screen
    elif gameStatus == "win":
        oled.fill(0)
        oled.text("WINNER", 40, 20, 1)
        if buttonStatus == "pressed":
            gameStatus = "start"

    # Loss screen
    elif gameStatus == "loss":
        oled.fill(0)
        oled.text("LOSER L", 40, 20, 1)
        if buttonStatus == "pressed":
            gameStatus = "start"

    # Calculate FPS
    if duration == 69420:  # If first frame, skip calculating FPS
        pass
    oled.text(f"{1000/duration:.0f}", 0, 0, 1)
    # time.sleep(0.1)
    oled.show()
    duration = utime.ticks_ms() - start
