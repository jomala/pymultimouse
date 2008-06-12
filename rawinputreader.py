# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/208699
# http://msdn.microsoft.com/en-us/library/ms645565(VS.85).aspx
# http://www.eventghost.org (the source code)

import win32con
import sys
from ctypes import *
from ctypes.wintypes import *

WNDPROC = WINFUNCTYPE(c_long, c_int, c_uint, c_int, c_int)

class WNDCLASS(Structure):
    _fields_ = [('style', c_uint),
                ('lpfnWndProc', WNDPROC),
                ('cbClsExtra', c_int),
                ('cbWndExtra', c_int),
                ('hInstance', c_int),
                ('hIcon', c_int),
                ('hCursor', c_int),
                ('hbrBackground', c_int),
                ('lpszMenuName', c_char_p),
                ('lpszClassName', c_char_p)]

class RECT(Structure):
    _fields_ = [('left', c_long),
                ('top', c_long),
                ('right', c_long),
                ('bottom', c_long)]

class PAINTSTRUCT(Structure):
    _fields_ = [('hdc', c_int),
                ('fErase', c_int),
                ('rcPaint', RECT),
                ('fRestore', c_int),
                ('fIncUpdate', c_int),
                ('rgbReserved', c_char * 32)]

class POINT(Structure):
    _fields_ = [('x', c_long),
                ('y', c_long)]
    
class MSG(Structure):
    _fields_ = [('hwnd', c_int),
                ('message', c_uint),
                ('wParam', c_int),
                ('lParam', c_int),
                ('time', c_int),
                ('pt', POINT)]

class RAWINPUTDEVICE(Structure):
    _fields_ = [
        ("usUsagePage", c_ushort),
        ("usUsage", c_ushort),
        ("dwFlags", DWORD),
        ("hwndTarget", HWND),
    ]

class RAWINPUTHEADER(Structure):
    _fields_ = [
        ("dwType", DWORD),
        ("dwSize", DWORD),
        ("hDevice", HANDLE),
        ("wParam", WPARAM),
    ]

class RAWMOUSE(Structure):
    class _U1(Union):
        class _S2(Structure):
            _fields_ = [
                ("usButtonFlags", c_ushort),
                ("usButtonData", c_ushort),
            ]
        _fields_ = [
            ("ulButtons", ULONG),
            ("_s2", _S2),
        ]

    _fields_ = [
        ("usFlags", c_ushort),
        ("_u1", _U1),
        ("ulRawButtons", ULONG),
        ("lLastX", LONG),
        ("lLastY", LONG),
        ("ulExtraInformation", ULONG),
    ]
    _anonymous_ = ("_u1", )


class RAWKEYBOARD(Structure):
    _fields_ = [
        ("MakeCode", c_ushort),
        ("Flags", c_ushort),
        ("Reserved", c_ushort),
        ("VKey", c_ushort),
        ("Message", UINT),
        ("ExtraInformation", ULONG),
    ]


class RAWHID(Structure):
    _fields_ = [
        ("dwSizeHid", DWORD),
        ("dwCount", DWORD),
        ("bRawData", BYTE),
    ]


class RAWINPUT(Structure):
    class _U1(Union):
        _fields_ = [
            ("mouse", RAWMOUSE),
            ("keyboard", RAWKEYBOARD),
            ("hid", RAWHID),
        ]

    _fields_ = [
        ("header", RAWINPUTHEADER),
        ("_u1", _U1),
        ("hDevice", HANDLE),
        ("wParam", WPARAM),
    ]
    _anonymous_ = ("_u1", )


def ErrorIfZero(handle):
    if handle == 0:
        raise WinError
    else:
        return handle

class rawinputreader:
    def __init__(self):
        CreateWindowEx = windll.user32.CreateWindowExA
        CreateWindowEx.argtypes = [c_int, c_char_p, c_char_p, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int]
        CreateWindowEx.restype = ErrorIfZero

        # Define Window Class
        wndclass = WNDCLASS()
        wndclass.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wndclass.lpfnWndProc = WNDPROC(lambda h, m, w, l: self.WndProc(h, m, w, l))
        wndclass.cbClsExtra = wndclass.cbWndExtra = 0
        wndclass.hInstance = windll.kernel32.GetModuleHandleA(c_int(win32con.NULL))
        wndclass.hIcon = windll.user32.LoadIconA(c_int(win32con.NULL), c_int(win32con.IDI_APPLICATION))
        wndclass.hCursor = windll.user32.LoadCursorA(c_int(win32con.NULL), c_int(win32con.IDC_ARROW))
        wndclass.hbrBackground = windll.gdi32.GetStockObject(c_int(win32con.WHITE_BRUSH))
        wndclass.lpszMenuName = None
        wndclass.lpszClassName = "MainWin"
        # Register Window Class
        if not windll.user32.RegisterClassA(byref(wndclass)):
            raise WinError()
        # Create Window
        HWND_MESSAGE = -3
        hwnd = CreateWindowEx(0,
                          wndclass.lpszClassName,
                          "Python Window",
                          win32con.WS_OVERLAPPEDWINDOW,
                          win32con.CW_USEDEFAULT,
                          win32con.CW_USEDEFAULT,
                          win32con.CW_USEDEFAULT,
                          win32con.CW_USEDEFAULT,

                          #HWND_MESSAGE, 
                          win32con.NULL,

                          win32con.NULL,
                          wndclass.hInstance,
                          win32con.NULL)
        # Show Window
        #windll.user32.ShowWindow(c_int(hwnd), c_int(win32con.SW_SHOWNORMAL))
        #windll.user32.UpdateWindow(c_int(hwnd))

        # Register for raw input
        Rid = (1 * RAWINPUTDEVICE)()
        Rid[0].usUsagePage = 0x01
        Rid[0].usUsage = 0x02
        RIDEV_INPUTSINK = 0x00000100 # Get events even when not focused
        Rid[0].dwFlags = RIDEV_INPUTSINK 
        Rid[0].hwndTarget = hwnd

        RegisterRawInputDevices = windll.user32.RegisterRawInputDevices
        RegisterRawInputDevices(Rid, 1, sizeof(RAWINPUTDEVICE))
        self.hwnd = hwnd
        self.raw_mouse_events = []

    """
    def MainLoop(self):
        # Pump Messages
        msg = MSG()
        pMsg = pointer(msg)
        NULL = c_int(win32con.NULL)
    
        while windll.user32.GetMessageA( pMsg, self.hwnd, 0, 0) != 0:
            print 'yo'
            windll.user32.TranslateMessage(pMsg)
            windll.user32.DispatchMessageA(pMsg)

        return msg.wParam
    """
    
    def pollEvents(self):
        # Pump Messages
        msg = MSG()
        pMsg = pointer(msg)
        NULL = c_int(win32con.NULL)
    
        PM_REMOVE = 1
        while windll.user32.PeekMessageA(pMsg, self.hwnd, 0, 0, PM_REMOVE) != 0:
            windll.user32.DispatchMessageA(pMsg)

        return_list = self.raw_mouse_events
        self.raw_mouse_events = []
        return return_list
    
    def __del__(self):
        pass
        """
        I can't get this to work. It is too late to destroy the window here. 
        Maybe I have to call UnregisterClassA also? 
        windll.user32.DestroyWindow(self.hwnd)
        """

    def stop(self):
        windll.user32.DestroyWindow(self.hwnd)

    """
    import inspect
    messageId2Name = dict([(value, key) for key, value in inspect.getmembers(win32con) if key.startswith('WM_')])
    WM_INPUT = 255
    messageId2Name[WM_INPUT] = 'WM_INPUT'
    keyId2Name = dict([(value, key) for key, value in inspect.getmembers(win32con) if key.startswith('VK_')])
    """

    def WndProc(self, hwnd, message, wParam, lParam):
        #global messageId2Name
        ps = PAINTSTRUCT()
        rect = RECT()
    
        #print messageId2Name.get(message, '?:'+str(message))
        WM_INPUT = 255
        if message == win32con.WM_DESTROY:
            windll.user32.PostQuitMessage(0)
            return 0
        elif message == WM_INPUT:
            GetRawInputData = windll.user32.GetRawInputData
            NULL = c_int(win32con.NULL)
            dwSize = c_uint()
            RID_INPUT = 0x10000003
            GetRawInputData(lParam, RID_INPUT, NULL, byref(dwSize), sizeof(RAWINPUTHEADER))
            if dwSize.value == 40:
                # Mouse
                raw = RAWINPUT()
                if GetRawInputData(lParam, RID_INPUT, byref(raw), byref(dwSize), sizeof(RAWINPUTHEADER)) == dwSize.value:
                    RIM_TYPEMOUSE = 0x00000000
                    RIM_TYPEKEYBOARD = 0x00000001
            
                    if raw.header.dwType == RIM_TYPEMOUSE:
                        self.raw_mouse_events.append((raw.header.hDevice, 
                                          raw.mouse.usFlags, raw.mouse.ulButtons, 
                                          raw.mouse._u1._s2.usButtonFlags, 
                                          raw.mouse._u1._s2.usButtonData, 
                                          raw.mouse.ulRawButtons, 
                                          raw.mouse.lLastX, 
                                          raw.mouse.lLastY, 
                                          raw.mouse.ulExtraInformation))

        return windll.user32.DefWindowProcA(c_int(hwnd), c_int(message), c_int(wParam), c_int(lParam))

LEFT_BUTTON = 1
RIGHT_BUTTON = 2
MIDDLE_BUTTON = 5
NO_BUTTON = 0
SCROLL_UP = -1
SCROLL_DOWN = -2

BUTTON_DOWN = 1
BUTTON_UP = 2
SCROLL = 3

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

"""
def reportMouseChange(hDevice, usFlags, ulButtons, usButtonFlags, 
                      usButtonData, ulRawButtons, lLastX, lLastY, 
                      ulExtraInformation):
    print 'raw.header.hDevice', hDevice
    print 'usFlags', usFlags
    print 'ulButtons', ulButtons
    print 'usButtonFlags', usButtonFlags
    print 'usButtonData', usButtonData
    print 'ulRawButtons', ulRawButtons
    print 'lLastX', lLastX
    print 'lLastY', lLastY
    print 'ulExtraInformation', ulExtraInformation
    if usButtonFlags == 8:
        windll.user32.PostQuitMessage(0)
"""

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

