import unicurses as curses

def getopt():
    ch = curses.getch()
    if   ch == curses.KEY_UP: return "move up"
    elif ch == curses.KEY_DOWN: return 'move down'
    elif ch == curses.KEY_LEFT: return 'move left'
    elif ch == curses.KEY_RIGHT: return 'move right'
    
    elif ch == ord('z') or ch == ord(' ') or ch == ord('\n') or ch == ord('\r') or ch == curses.KEY_ENTER: return 'reveal'
    elif ch == ord('x') or ch == ord('f'): return 'flag'
    elif ch == ord('a'): return 'item armor'
    elif ch == ord('s'): return 'item sledge'
    elif ch == ord('e'): return 'item eagle'
    elif ch == ord('q'): return 'quit'
    else: return None

def init():
    global stdscr
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    curses.keypad(stdscr, True)

def clear():
    curses.clear()
    put_str(">>> Minesweeper Roguelike <<<")
    put_str(1,0," v0.0.3         by sun123zxy ")

def flush():
    curses.refresh()

def newline():
    y,x = curses.getyx(stdscr)
    curses.wmove(stdscr,y+1,0)
    
def put_mat(mat):
    newline()
    for i, rows in enumerate(mat):
        for j, e in enumerate(rows):
            curses.mvaddstr(i+2,j,e)

def put_str(*args):
    newline()
    for arg in args:
        curses.addstr(arg)