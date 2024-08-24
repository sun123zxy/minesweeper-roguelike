import os

def flush():
    os.system('cls')
    print(">>> Minesweeper Roguelike <<<")
    print("version 20240824 by sun123zxy")

def put_mat(mat):
    for rows in mat:
        for e in rows:
            print(e,end='')
        print()

def put_str(*args):
    print(*args)