#!/usr/bin/env python3

import re

class Opc():
    def __init__(self):
        self.opc = {}

        with open("info/opcodes.txt", 'r') as f:
            for line1 in f:
                line2 = f.readline().strip()
                m1 = re.match('([a-z]+): (\d+)(.*)', line1.strip())
                l1 = m1.groups()
                self.opc[int(l1[1])] = {
                    'name': l1[0],
                    'narg': len(l1[2])//2,
                    'usage': l1[1] + l1[2],
                    'desc': line2.strip()
                }
    def keys(self):
        return self.opc.keys()

    def name(self, n):
        if n in self.opc:
            return self.opc[n]['name']
        else:
            return "unknown"

    def narg(self, n):
        if n in self.opc:
            return self.opc[n]['narg']
        else:
            return "unknown"

    def desc(self, n):
        if n in self.opc:
            return self.opc[n]['desc']
        else:
            return "-"

    def usage(self, n):
        if n in self.opc:
            return self.opc[n]['usage']
        else:
            return ""

    def full(self, n):
        if n in self.opc:
            return "\n" + "> " + self.usage(n) + "\n" \
                + "> '" + self.name(n) + "' (" \
                + str(self.narg(n)) + ") " \
                + self.desc(n)    
        else:
            return "unknown"

if __name__ == '__main__':
    opc = Opc()
    while True:
        inp = input("code (q=quit): ")
        if inp in "quitQ":
            break
        else:
            print(opc.full(int(inp)))
            print()
