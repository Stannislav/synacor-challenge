#!/usr/bin/env python3

ops = {
    '*': lambda x, y: x*y,
    '+': lambda x, y: x+y,
    '-': lambda x, y: x-y}

lock = [
    ['*',   8, '-',   1],
    [  4, '*',  11, '*'],
    ['+',   4, '-',  18],
    [ 22, '-',   9, '*']]

start = (0, 3)
end = (3, 0)

def gen_next(pos):
    x, y = pos
    if x < 3: yield (x+1, y)
    if y > 0: yield (x, y-1)
    if x > 0:
        p = (x-1, y)
        if p != start:
            yield p
    if y < 3:
        p = (x, y+1)
        if p != start:
            yield p

def dfs(pos, val, target, max_l, op=None):
    if max_l == 0:
        if val == target and pos == end:
            return [pos]
        else:
            return None
    elif pos == end: # reached the end earlier than needed
        return None
    else:
        for npos in gen_next(pos):
            lock_val = lock[npos[1]][npos[0]]
            if (npos[0]+npos[1])%2: # room with a number
                newval = ops[op](val, lock_val)
                res = dfs(npos, newval, target, max_l-1)
            else: # room with an op
                res = dfs(npos, val, target, max_l-1, lock_val)
            if res: # success
                return [pos] + res
        return None

# Start with the minimal possible length
i = len(lock)-1 + len(lock[0])-1
while True:
    # Do a DFS search
    result = dfs(start, 22, 30, i)
    if result:
        # Found, print the result and exit loop
        print("{} steps:".format(i))
        prev = result[0]
        val = 22
        op = None
        print("  START", prev, 22)
        for pos in result[1:]:
            d = {
                (1,0): "east",
                (-1,0): "west",
                (0,1): "south",
                (0,-1): "north"
            }[(pos[0]-prev[0], pos[1]-prev[1])]

            if (pos[0]+pos[1])%2 == 1:
                val = ops[op](val, lock[pos[1]][pos[0]])
            else:
                op = lock[pos[1]][pos[0]]
            tot = 0
            print("  {0:5s} {1} {2} {3}".format(d, pos, str(lock[pos[1]][pos[0]]), "= " + str(val) if (pos[0]+pos[1])%2 else ""))
            prev = pos
        break
    # No solutions at that lengths, try the next possible one
    i += 2