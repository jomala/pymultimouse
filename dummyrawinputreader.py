class rawinputreader:
    def __init__(self):
        self.raw_mouse_events = []

    def pollEvents(self):
        return_list = self.raw_mouse_events
        self.raw_mouse_events = []
        return return_list
    
    def __del__(self):
        pass

    def stop(self):
        pass

def eventTupleToButton(event_tuple):
    id, usflags, ulbuttons, usbuttonflags, usbuttondata, ulrawbuttons, x, y, extra = event_tuple
    if usbuttonflags == 0x400:
        if usbuttondata & 0x8000:
            return (SCROLL, SCROLL_DOWN)
        else:
            return (SCROLL, SCROLL_UP)
    if usbuttonflags != 0:
        button = 1
        while usbuttonflags != 0:
            if usbuttonflags & 1:
                return (BUTTON_DOWN, button)
            elif usbuttonflags & 2:
                return (BUTTON_UP, button)
            usbuttonflags >>= 2
            button += 1
    return (NO_BUTTON, NO_BUTTON)

LEFT_BUTTON = 1
RIGHT_BUTTON = 2
MIDDLE_BUTTON = 5
NO_BUTTON = 0
SCROLL_UP = -1
SCROLL_DOWN = -2

BUTTON_DOWN = 1
BUTTON_UP = 2
SCROLL = 3

if __name__=='__main__':
    print "I will show all events for 5 seconds, polled once a second"
    import time
    import pprint
    rir = rawinputreader()
    for i in range(5):
        time.sleep(1)
        print i
        pprint.pprint(rir.pollEvents())
    rir.stop()

