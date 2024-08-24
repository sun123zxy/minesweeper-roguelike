import numpy as np
import time
import math
import threading
from collections import deque

import screen, input

dir4 = {
    "up": (1,0),
    "down": (-1,0),
    "left": (0,-1),
    "right": (0,1)
}

max_log_buffer = 5
max_height = 10000
start_height = 5
visual_height = 30
visual_width = 14
visual_shape = (visual_height, visual_width)

bomb_prob = 0.12
wall_prob = 0.12
speed_rate = 0.1

start_credit = 40

item_price = {
    'armor': 40,
    'eagle': 15,
    'sledge': 5
}
default_item = 'armor'

sweep_bonus = 1
misflag_punish = 3

def count_around_value(mat, pos, val, range = 1):
    R, C = mat.shape
    r, c = pos
    return np.count_nonzero(mat[max(0, r-range):min(r+range,R)+1,max(0,c-range):min(c+range,C)+1] == val)

def gen_visual_mat(bomb_mat, view_mat):
    visual_mat = np.full_like(bomb_mat, ' ', str)
    R,C = view_mat.shape
    for r in range(0, R):
        for c in range(0, C):
            ch = ' '
            if view_mat[r,c] == ' ':
                if(bomb_mat[r,c] == 'B'): ch = 'B'
                elif(bomb_mat[r,c] == ' '):
                    cnt_bomb = count_around_value(bomb_mat, (r,c), 'B')
                    cnt_view = count_around_value(view_mat, (r,c), ' ')
                    ch = chr(ord('0') + cnt_bomb) if cnt_bomb or cnt_view < 9 else ' '
                elif(bomb_mat[r,c] == '#'):
                    ch = '#'
            else:
                ch = view_mat[r,c]
            visual_mat[r,c] = ch
    return visual_mat

def gen_screen_mat(visual_mat, cursor_pos):
    R, C = visual_mat.shape
    screen_mat = np.full((R, C * 2 + 1), ' ', str)
    for r in range(0, R): 
        for c in range(0, C * 2 + 1):
            ch = ' '
            if r == 0:
                ch = '^'
            elif r == R-1: ch = '-'
            elif c % 2 == 1: ch = visual_mat[r,c//2]
            elif (r, c//2) == cursor_pos: ch = '['
            elif (r, c//2 - 1) == cursor_pos: ch = ']'
            screen_mat[r,c] = ch
    return screen_mat

bomb_mat = np.vstack([np.full((start_height, visual_width), ' ', str),
              np.random.choice([' ', 'B','#'], size = (max_height - start_height, visual_width), p = [1 - bomb_prob - wall_prob, bomb_prob, wall_prob]
              )]
            )
bomb_mat[:,0].fill('#')
bomb_mat[:,-1].fill('#')

view_mat = np.full((max_height, visual_width), '*', str)
# view_mat = np.random.choice([' ' ,'*'], size = (max_height, visual_width), p = [visible_prob, 1 - visible_prob])

for r in range(0, bomb_mat.shape[0]):
    for c in range(0, bomb_mat.shape[1]):
        if bomb_mat[r,c] == '#':
            view_mat[r,c] = ' '

cur_height = 0
cursor_pos = (2,1)
cur_credit = start_credit
cur_item = default_item
def try_use(item_name):
    global cur_credit, cur_item
    if cur_item == item_name:
        if cur_credit >= item_price[cur_item]:
            cur_credit -= item_price[cur_item]
            logs.append(item_name + "! credit -= " + str(item_price[cur_item]))
            cur_item = default_item # switch back to default
            return True
        else:
            logs.append("insufficient credit")
            return False
    else: return False

def t_next_scroll():
    return 1 / (speed_rate * math.log(cur_height + math.e))

logs = deque([])
def flush():
    global cur_height,cursor_pos
    cursor_relative_pos = (cursor_pos[0] - cur_height, cursor_pos[1])
    screen.flush()
    # print('-' * (visual_width * 2 + 1))
    visual_mat = gen_visual_mat(bomb_mat[cur_height : cur_height + visual_height, :], view_mat[cur_height : cur_height + visual_height, :])
    screen_mat = gen_screen_mat(visual_mat, cursor_relative_pos)
    screen.put_mat(screen_mat[::-1,:])
    # print('^' * (visual_width * 2 + 1))
    print(cur_item, "\t\tcredit:", cur_credit)
    print("height:", cur_height, "\tnext scroll:", format(t_next_scroll(), '.2f') + "s")
    # print("cursor:", cursor_relative_pos)
    print("----- logs -----")
    while len(logs) > max_log_buffer:
        logs.popleft()
    for log in reversed(logs):
        print(log)

def opt_item_switch(item_name):
    global cur_item
    cur_item = item_name

def end_game(info):
    logs.append("game over: " + info)
    view_mat.fill(' ')
    flush()
    global keep_threads_running
    keep_threads_running = False
    quit()

def opt_cursor_move(dir):
    global cursor_pos, cur_credit
    movement = dir4[dir]
    cur_pos = tuple(np.array(cursor_pos) + np.array(movement))
    if (0 < cur_pos[0] - cur_height < visual_height-1 and 0 < cur_pos[1] < visual_width-1)and count_around_value((view_mat == ' ') & (bomb_mat == ' '), cur_pos, True, 2):
        if bomb_mat[cur_pos] == '#':
            if try_use('sledge'):
                bomb_mat[cur_pos] = view_mat[cur_pos] = ' '
                cursor_pos = cur_pos
        else:
            cursor_pos = cur_pos

def reveal(pos, invincible = False):
    global cur_credit
    if view_mat[pos] == '*':
        view_mat[pos] = ' '
        if bomb_mat[pos] == 'B' and not invincible:
            logs.append("bomb triggered")
            if try_use('armor'):
                pass
            else:
                end_game('explosion')
        if count_around_value(bomb_mat, pos, 'B') == 0:
            R, C = bomb_mat.shape
            px, py = pos
            for x in range(max(px-1,0), min(px+1,R)+1):
                for y in range(max(py-1,0), min(py+1,C)+1):
                    reveal((x,y))

def opt_reveal():
    pos = cursor_pos
    is_area = False
    is_eagle = False
    is_reveal = True
    if view_mat[pos] == '*':
        if cur_item == 'eagle':
            if try_use('eagle'):
                is_area = True
                is_eagle = True
            else:
                is_reveal = False
        else:
            logs.append("reveal")
    elif view_mat[pos] == ' ' and bomb_mat[pos] == ' ' and count_around_value(bomb_mat, pos, 'B') == count_around_value(view_mat, pos, 'X') + count_around_value((view_mat == ' ') & (bomb_mat == 'B'), pos, True):
        logs.append("infer")
        is_area = True

    if is_reveal:
        if is_area:
            R, C = bomb_mat.shape
            px, py = cursor_pos
            for x in range(max(px-1,0), min(px+1,R)+1):
                for y in range(max(py-1,0), min(py+1,C)+1):
                    reveal((x,y), invincible=is_eagle)
        else:
            reveal(pos)

def opt_toogle_flag():
    if view_mat[cursor_pos] == '*':
        view_mat[cursor_pos] = 'X'
        logs.append("flag")
    elif view_mat[cursor_pos] == 'X':
        view_mat[cursor_pos] = '*'
        logs.append("unflag")

def scroll():
    global cur_height, cur_credit
    sweeped = np.count_nonzero((bomb_mat[cur_height,:] == 'B') & (view_mat[cur_height,:] == 'X'))
    misflagged = np.count_nonzero((bomb_mat[cur_height,:] == ' ') & (view_mat[cur_height,:] == 'X'))
    logs.append(str(sweeped) + " mines sweeped, " + str(misflagged) + " misflags")
    cur_credit = max(0, cur_credit + sweep_bonus * sweeped - misflag_punish * misflagged)
    cur_height += 1
    if cursor_pos[0] - cur_height < 1:
        end_game('left behind')


reveal((2,1))
flush()
thlock = threading.Lock()

def thready_input():
    while True:
        opt = input.getopt()
        if not keep_threads_running: break
        with thlock:
            if(opt):
                opt = opt.split(' ')
                if opt[0] == 'move':
                    opt_cursor_move(opt[1])
                elif opt[0] == 'reveal':
                    opt_reveal()
                elif opt[0] == 'flag':
                    opt_toogle_flag()
                elif opt[0] == 'item':
                    opt_item_switch(opt[1])
                elif opt[0] == 'quit':
                    end_game('quit')
                flush()

def thready_scroll():
    while True:
        time.sleep(t_next_scroll())
        if not keep_threads_running: break
        with thlock:
            scroll()
            flush()


keep_threads_running = True
thread_input = threading.Thread(target=thready_input)
thread_input.start()
thready_scroll = threading.Thread(target=thready_scroll)
thready_scroll.start()