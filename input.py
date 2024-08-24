from msvcrt import getch as _getch

def getch():
    ch = _getch()
    if ch == b'\xe0':
        ch = _getch()
        if ch == b'H': return 'up'
        elif ch == b'P': return 'down'
        elif ch == b'K': return 'left'
        elif ch == b'M': return 'right'
    else:
        return ch.decode("utf-8")

def getopt():
    ch = getch()
    if ch == 'up' or ch == 'down' or ch == 'left' or ch == 'right':
        return 'move ' + ch
    elif ch == 'z' or ch == '\r' or ch == ' ': return 'reveal'
    elif ch == 'x' or ch == 'f': return 'flag'
    elif ch == 'a': return 'item armor'
    elif ch == 's': return 'item sledge'
    elif ch == 'e': return 'item eagle'
    elif ch == 'q': return 'quit'
    else: return None