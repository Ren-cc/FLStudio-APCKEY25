# name=Akai APC Key 25
# Author: Ren-cc
# C:\Users\[user]\OneDrive\Documents\Image-Line\FL Studio\Settings\Hardware\AKAI APC-KEY25
import device
import midi
import time

# Modes
MODE_USER = 0
MODE_LED = 1
controllerMode = MODE_USER

SHIFT_BUTTON = 98
shiftModifier = 0

USER_MODE_BUTTON = 81
LED_MODE_BUTTON = 86

# Knobs
KNOB_START = 48
KNOB_END = 55
knobValues = [64]*8

currentColor = [0]
colorGridState = [0] * 40

# NEW: Track behavior per LED
behaviorGridState = [0] * 40  # Each entry stores an index into behaviorPalette for that pad.

# Color and behavior palettes
colorPalette = [   
    0, # black
    3, # white
    4, # light pink
    5, # red
    9, # yellow
    13, # yellow-ish green
    17, # green
    19, # dark green
    20, # teal
    26, # dark teal 
    33, # light blue
    37, # darker blue
    41, # deep blue
    49, # purple
    50, # dark purple
    52, # light magenta
    53, # magenta
    57, # pink
    60, # orange
    72, # red 
    37, # nice light green
    106, # muted red
    125, # snot yellow
    127, # brown
    ]

currentColorIndex = 0

# Behavior palette: different brightness/blink modes
behaviorPalette = [
    0x90, # 10% brightness
    0x91, # 25%
    0x92, # 50%
    0x93, # 65%
    0x94, # 75%
    0x95, # 90%
    0x96, # 100% brightness solid
    0x97, # Pulsing 1/16
    0x98, # Pulsing 1/8
    0x99,  # Pulsing 1/4
    0x9A,  # Pulsing 1/2
    0x9B,  # Blinking 1/24
    0x9C,  # Blinking 1/16
    0x9D,  # Blinking 1/8
    0x9E,  # Blinking 1/4
    0x9F,  # Blinking 1/2

]
currentBehaviorIndex = 6  # default to solid 100% brightness

raindropMode = False
dimMode = False

class LedControl:
    def __init__(self):
        pass

    def setLedOff(self, note):
        self.sendLedMessage(note, 0, behaviorIndex=0)  # Use a default behavior (like first in palette)
    
    def setLedColor(self, note, color):
        # Use the stored behavior for this pad
        bIndex = behaviorGridState[note]
        self.sendLedMessage(note, color, behaviorIndex=bIndex)
    
    def setBehavioralLedColor(self, note, color, behaviorIndex):
        # Use the stored behavior for this pad
        bIndex = behaviorGridState[note]
        self.sendLedMessage(note, color, behaviorIndex)

    def sendLedMessage(self, note, colorCode, behaviorIndex=None):
        if behaviorIndex is None:
            behaviorIndex = 6  # Default to solid 100% brightness
        status = behaviorPalette[behaviorIndex]
        device.midiOutMsg(status + (note << 8) + (colorCode << 16))

    def clearAllLeds(self):
        for i in range(40):
            colorGridState[i] = 0
            behaviorGridState[i] = 0
            self.setLedOff(i)
        self.setLedOff(USER_MODE_BUTTON)
        self.setLedOff(LED_MODE_BUTTON)
        self.setLedOff(82)
        self.setLedOff(83)

    def clearGridPads(self):
        for i in range(40):
            colorGridState[i] = 0
            behaviorGridState[i] = 0
            self.setLedOff(i)

    def cycleUpAnimation(self):
        for x in range(40):
            time.sleep(0.005)
            self.setBehavioralLedColor(x, currentColor[0], 6)
        self.resetGridState()

    def cycleDownAnimation(self):
        for x in range(40):
            time.sleep(0.005)
            self.setBehavioralLedColor(39 - x, currentColor[0], 6)
        self.resetGridState()

    def RaindropAnimation(self, note):
        """
        Creates a 'raindrop' LED effect centered around the given note, lighting up rings
        of pads at increasing distances in a manhattan sense.

        Note: This function is a bit slow because it sleeps for 0.01 seconds after each ring. 
        Seems like FL does not support multitthreading, so that's out of the picture.
        I think i can find a work around for this, but for now, this is how the cookie will crumble. 
        """

        # Light up the original note at solid brightness first.
        self.setBehavioralLedColor(note, currentColor[0], 6)
        time.sleep(0.01)
        self.resetGridState()

        rowLen = 8
        row = note // rowLen
        col = note % rowLen

        def ringNeighbors(r, c, dist):
            """
            Returns all pads at exactly manhattan distance 'dist' from (r, c).
            """
            results = []
            for nr in range(5):
                for nc in range(rowLen):
                    if abs(nr - r) + abs(nc - c) == dist:
                        results.append(nr * rowLen + nc)
            return results

        # Expand rings up to the maximum distance possible in a 5x8 grid.
        maxDist = 4 + 7  # worst-case (top-left to bottom-right)
        for dist in range(1, maxDist + 1):
            ring = ringNeighbors(row, col, dist)
            if not ring:
                break
            for n in ring:
                self.setBehavioralLedColor(n, currentColor[0], 6)
            time.sleep(0.1)
            self.resetGridState()
    def dimOnPress(self, note):
        # self.setBehavioralLedColor(note, colorGridState[note], 0)
        self.setLedOff(note)
        time.sleep(0.01)
        self.individualResetGridState(note)

    def resetGridState(self):
        for i in range(40):
            cColor = colorGridState[i]
            # setLedColor uses behaviorGridState to set correct behavior
            self.setLedColor(i, cColor)
        # time.sleep(0.01)
    def individualResetGridState(self, note):
        cColor = colorGridState[note]
        # setLedColor uses behaviorGridState to set correct behavior
        self.setLedColor(note, cColor)
        # time.sleep(0.01)
    

def setMode(newMode):
    global controllerMode
    controllerMode = newMode
    updateModeLeds()
    modeName = "USER" if newMode == MODE_USER else "LED"
    print("Controller mode set to:", modeName)

def updateModeLeds():
    ledCtrl = LedControl()
    if controllerMode == MODE_USER:
        # Just set USER_MODE_BUTTON to a visible color
        ledCtrl.sendLedMessage(USER_MODE_BUTTON, 3, behaviorIndex=6)  # White, full brightness
        ledCtrl.setLedOff(LED_MODE_BUTTON)
    else:
        ledCtrl.sendLedMessage(LED_MODE_BUTTON, 3, behaviorIndex=6)
        ledCtrl.setLedOff(USER_MODE_BUTTON)

def OnInit():
    print("APC Key 25 Script Loaded. Starting in USER mode.")
    ledCtrl = LedControl()
    ledCtrl.clearAllLeds()
    setMode(MODE_USER)

def OnDeInit():
    ledCtrl = LedControl()
    ledCtrl.clearAllLeds()
    print("APC Key 25 Script Unloaded.")

def OnMidiMsg(event):
    global shiftModifier, controllerMode, currentColor, colorGridState, knobValues
    global currentColorIndex, currentBehaviorIndex
    global raindropMode, dimMode

    print("MIDI data: data1: {}, data2: {}, midiChan: {}, midiID: {}".format(
        event.data1, event.data2, event.midiChan, event.midiId))
    print(currentColor[0])

    if event.midiChan != 0:
        return

    # SHIFT logic
    if event.data1 == SHIFT_BUTTON:
        if event.midiId == midi.MIDI_NOTEON:
            shiftModifier = 1
            event.handled = True
        elif event.midiId == midi.MIDI_NOTEOFF:
            shiftModifier = 0
            event.handled = True
        return

    # Mode switching
    if shiftModifier == 1 and event.midiId == midi.MIDI_NOTEON:
        if event.data1 == USER_MODE_BUTTON:
            setMode(MODE_USER)
            event.handled = True
            return
        elif event.data1 == LED_MODE_BUTTON:
            setMode(MODE_LED)
            event.handled = True
            return

    # Knobs
    if 48 <= event.data1 <= 55 and event.midiId == midi.MIDI_CONTROLCHANGE:
        knobIndex = event.data1 - 48
        increment = 0
        if event.data2 < 64:
            increment = event.data2
        elif event.data2 > 64:
            increment = (event.data2 - 128)

        knobValues[knobIndex] = max(0, min(127, knobValues[knobIndex] + increment))
        event.data2 = knobValues[knobIndex]
        event.handled = False
        return

    ledCtrl = LedControl()

    # In LED mode, use specific buttons for color/behavior control
    # 64 = next color
    # 65 = prev color
    # 66 = next behavior
    # 67 = prev behavior


    if controllerMode == MODE_USER and event.midiId == midi.MIDI_NOTEON:
        if raindropMode:
            ledCtrl.RaindropAnimation(event.data1)
        if dimMode:
            ledCtrl.dimOnPress(event.data1)
            


    if controllerMode == MODE_LED and event.midiId == midi.MIDI_NOTEON:

        if event.data1 == 82 and not raindropMode:
            ledCtrl.sendLedMessage(82, 5, 1) #doesn't matter what the behavior and color is, defaults to 100% green
            raindropMode = True
            event.handled = True
            return
        if event.data1 == 82 and raindropMode:
            ledCtrl.setLedOff(82)
            raindropMode = False
            event.handled = True
            return
        if event.data1 == 83 and not dimMode:
            ledCtrl.sendLedMessage(83, 5, 1) #doesn't matter what the behavior and color is, defaults to 100% green
            dimMode = True
            event.handled = True
            return
        if event.data1 == 83 and dimMode:
            ledCtrl.setLedOff(83)
            dimMode = False
            event.handled = True
            return

        
        if event.data1 == 64:  # Next color
            currentColorIndex = (currentColorIndex + 1) % len(colorPalette)
            currentColor[0] = colorPalette[currentColorIndex]
            ledCtrl.cycleUpAnimation()
            applyCurrentColorToPads(ledCtrl)
            event.handled = True
            return

        elif event.data1 == 65: # Prev color
            currentColorIndex = (currentColorIndex - 1) % len(colorPalette)
            currentColor[0] = colorPalette[currentColorIndex]
            ledCtrl.cycleDownAnimation()
            applyCurrentColorToPads(ledCtrl)
            event.handled = True
            return

        elif event.data1 == 66: # Next behavior
            currentBehaviorIndex = (currentBehaviorIndex + 1) % len(behaviorPalette)
            applyCurrentColorToPads(ledCtrl)
            event.handled = True
            return

        elif event.data1 == 67: # Prev behavior
            currentBehaviorIndex = (currentBehaviorIndex - 1) % len(behaviorPalette)
            applyCurrentColorToPads(ledCtrl)
            event.handled = True
            return

        # SHIFT + pad = turn that pad off
        if shiftModifier == 1:
            ledCtrl.setLedOff(event.data1)
            if event.data1 < 40:
                colorGridState[event.data1] = 0
                behaviorGridState[event.data1] = 0
            event.handled = True
            return

        # If pressing pad 64 or 65 below this line was for animations,
        # Adjust your logic as needed. We'll remove the conflicting animation logic
        # because we re-purposed these buttons for color changes.

        if event.data1 == LED_MODE_BUTTON:
            for i in range(40):
                colorGridState[i] = 0
                behaviorGridState[i] = 0
                ledCtrl.setLedOff(i)
            currentBehaviorIndex = 6
            currentColorIndex = 0
            currentColor=[0]; 
            event.handled = True
            return

        elif event.data1 < 40:
            if raindropMode == True:
                ledCtrl.RaindropAnimation(event.data1)
                event.handled = True
            if dimMode == True:
                ledCtrl.dimOnPress(event.data1)
                event.handled = True
            else:
                # Set the pad color and behavior to the current selections
                chosenColor = currentColor[0]
                chosenBehavior = currentBehaviorIndex
                colorGridState[event.data1] = chosenColor
                behaviorGridState[event.data1] = chosenBehavior
                ledCtrl.setLedColor(event.data1, chosenColor)
                event.handled = True
            
            return
        else:
            event.handled = True
            

def applyCurrentColorToPads(ledCtrl):
    # Re-apply colors and behaviors to all pads
    for i in range(40):
        ledCtrl.setLedColor(i, colorGridState[i])
    time.sleep(0.01)
