#!/usr/bin/env python3

from opc_lookup import Opc

class Dumper():
    def __init__(self):
        self.MEMR = (1<<15)
        self.NREG = 8

        self.mem = []

        self.opc = Opc()
        self.funcs = set()
        self.prints = {}
        self.strings = {}

        self.load_bin()
        self.find_prints()

    def load_bin(self, f_bin = "bin/challenge.bin"):
        code = open(f_bin, 'rb').read()
        for i in range(0, len(code), 2):
            val = code[i] + (code[i+1]<<8)
            assert val < self.MEMR + self.NREG
            self.mem.append(val)

    def isstringmem(self, pm):
        return False

    def gen_cmd(self):
        # iterate over all address pointers for mem
        mi = iter(range(len(self.mem)))
        for pm in mi:
            val = self.mem[pm]
            s = ""
            if val in self.opc.keys() and not self.isstringmem(pm):
                # read all arguments
                ret = [val]
                for i in range(self.opc.narg(val)):
                    ret.append(self.mem[next(mi)])
                yield ret
            else:
                yield val

    def find_prints(self):
        # this isn't quite working as yet
        # the memory space for strings seems to be encoded as well...
        # first (call   1458) to access a string is at mem[1064]
        prev = [None]*3
        for val in self.gen_cmd():
            if type(val) == list and val[0] == 17 and val[1] == 1458:
                # preceded by set, set, add?
                if [prev[0][0], prev[1][0], prev[2][0]] == [1, 1, 9]:
                    sptr = prev[0][2]
                    scyph = prev[1][2]
                    scode = prev[2][2] + prev[2][3]
                    if scyph != 1531:
                        print("unknown cypher!")
                    # to do
            prev.pop(0)
            prev.append(val)

    def isptr(self, n):
        return 0 <= n < self.MEMR

    def dump(self, fname="dump.txt", ptrs=None):
        f_out = open(fname, 'w')
        wrotelast = True

        # iterate over all address pointers for mem
        mi = iter(range(len(self.mem)))
        for p_cmd in mi:
            cmd = self.mem[p_cmd]
            s = ""
            if cmd in self.opc.keys():
                # read all arguments
                args = []
                for i in range(self.opc.narg(cmd)):
                    args.append(self.mem[next(mi)])

                # is it a function call?
                if cmd == 17 and self.isptr(args[0]): # call
                    self.funcs.add(args[0])

                # 'rmem', want to save the value at that address too
                if cmd == 15 and args[-1] < (1<<15):
                    rmem = "mem[{}] = {}".format(args[-1], self.mem[args[-1]])
                else:
                    rmem = ""
                # format the output string
                for i in range(len(args)):
                    if args[i] >= (1<<15):
                        args[i] = "<{}>".format(args[i]-(1<<15))
                    elif cmd == 19 and args[i] < (1<<7) :
                        args[i] = "'{}'".format(chr(args[i])).replace('\n', '\\n')
                    else:
                        args[i] = str(args[i])

                s = "{0:2d} = {1:4}\t{2}".format(cmd, self.opc.name(cmd), ' '.join(args))
                if rmem:
                    s += "                " + rmem
                
            else:
                s = "({})".format(cmd)

            # only write if no ptr filter, or filter on ptr positive
            if ptrs == None or (ptrs and p_cmd in ptrs):
                if not wrotelast:
                    f_out.write("...\n")
                f_out.write("{0:5d}| {1}\n".format(p_cmd, s))
                wrotelast = True
            else:
                wrotelast = False
        f_out.close()

if __name__ == '__main__':
    d = Dumper()
    d.dump()
    print("Some functions found at")
    print(sorted(d.funcs))
