#!/usr/bin/env python3


class Synacor_VM():
    def __init__(self, progfile, ROFF=(1 << 15), NREG=8, r7=0):
        self.ROFF = ROFF  # address of reg0
        self.NREG = NREG
        self.stack = []
        self.reg = [0] * NREG
        self.mem = [0] * ROFF
        self.ptr = 0
        self.running = False
        self.buffer = ""
        self.reg[7] = r7

        self.load_file(progfile)
        self.load_buffer("input_buffer.txt")
        self.remove_r7_zero_check()
        self.activate_teleporter_check_bypass()

    def load_file(self, f):
        code = open(f, 'rb').read()
        for i in range(0, len(code), 2):
            val = code[i] + (code[i + 1] << 8)
            assert val < self.ROFF + self.NREG
            self.mem[i // 2] = val

    def load_buffer(self, f_buf):
        self.buffer = open(f_buf, 'r').read()

    def remove_r7_zero_check(self):
        # for the first time the eighth register is checked
        # at mem[5451] we could monitor memory reading and
        # set reg[7] as soon as we get there. Instead it's better
        # to just remove the check in the self-test.
        self.mem[521] = self.mem[522] = self.mem[523] = 21  # noop

    def activate_teleporter_check_bypass(self):
        # the code relevant for checking is
        # 5483|  1 = set     <0> 4
        # 5486|  1 = set     <1> 1
        # 5489| 17 = call    6027
        # 5491|  4 = eq      <1> <0> 6
        # 5495|  8 = jf      <1> 5579
        # the routine at mem[6027] is the one that needs to be re-implemented
        # the result of the check is stored in <0>
        # to pass the test we need <0> == 6
        # to bypass we remove the function call and just set <0> = 6
        self.mem[5485] = 6
        self.mem[5489] = self.mem[5490] = 21

    # Check eighth register with native binary code. Returning r0
    def cr7nat(self, r0=4, r1=1):
        self.reg[0] = r0
        self.reg[1] = r1
        self.reg[7] = self.reg[7]
        self.ptr = 6027
        self.run()
        return self.reg[0]

    # Check eighth register by re-implementing binary code. Returning r0
    def cr7(self, r0=4, r1=1):  # = mem[6027]
        if r0:
            if r1:
                return self.cr7(r0-1, self.cr7(r0, r1-1))
            else:
                return self.cr7(r0-1, self.reg[7])
        else:
            return r1+1

    def find_r7(self):
    # Thanks to github.com/NiXXeD for the cache implementation
        def cr7cache(r7):
            cache = {}
            for r1 in range(1<<15):
                cache[(0, r1)] = (r1+1) % (1<<15)
            for r0 in range(1, 5):
                cache[(r0, 0)] = cache[(r0-1, r7)]
                for r1 in range(1, 1<<15):
                    cache[(r0, r1)] = cache[(r0-1, cache[(r0, r1-1)] % (1<<15))]
            return cache[(4, 1)]

        print("Starting brute-force search for correct r7...")
        perc = [int((1<<15)/100*(i+1)) for i in range(100)]
        for r7 in range(1<<15):
            if r7 in perc:
                print("{}% ({}/{})".format((perc.index(r7)+1), r7, 1<<15))
            c = cr7cache(r7)
            if c == 6:
                print("Found! Returning")
                return r7
        print("Nothing found.")
        return None

    def decode_str_at(self, sptr, x): # = mem[1458]
        # Strings in the synacor challange are encoded with
        # xor with varying value. A typical call in the bin file is
        # push    <0>
        # push    <1>
        # push    <2>
        # set     <0> 26851
        # set     <1> 1531
        # add     <2> 8117 13102
        # call    1458
        # pop     <2>
        # pop     <1>
        # pop     <0>
        # r0 contains the location of the string, r1 is the xoring method
        # and r2 contains the xor code
        # one can get some example strings by running:
        # self.decode_str_at(26851, 8117+13102)
        # self.decode_str_at(28844, 6121+19961)
        # self.decode_str_at(29014, 11522+8051)
        # self.decode_str_at(29245, 16131+11506)
        # self.decode_str_at(29400, 362+24979)
        # self.decode_str_at(29545, 1969+1102)
        l = self.mem[sptr]
        print("{}|{}".format(sptr, self.mem[sptr]))
        for i in range(l):
            sptr += 1
            print(chr(self.mem[sptr]^x), end='')
        print('')

    def readn(self):
        """ Read the next value in memory """
        if self.ptr >= self.ROFF:
            self.running = False
            return
        val = self.mem[self.ptr]
        self.ptr += 1
        return val

    def getreg(self, n=None):
        """ Convert a value to a register index """
        if n == None:
            n = self.readn()
        return n-(1<<15)

    def getval(self, n=None):
        """ Decide whether the value provided is a number
        or a register value. In the latter case read the value
        of the register and return it, in the former just return
        the value
        """
        if n == None:
            n = self.readn()
        if n < (1<<15):
            return n
        else: 
            return self.reg[self.getreg(n)]

    def jump(self, n=None):
        """ Jump to the memory address provided """
        if n == None:
            n = self.getval()
        self.ptr = n

    def run(self):
        """ Main function to run the binary code loaded into memory """
        if len(self.mem) == 0:
            print("> Memory is empty. Nothing to run.")
        else:
            self.running = True
            while self.running:
                try:
                    cmd = self.readn()
# halt: 0
#   stop execution and terminate the program
                    if cmd == 0:
                        self.running = False 
# set: 1 a b
#   set register <a> to the value of <b>
                    elif cmd == 1:
                        a, b = self.getreg(), self.getval()
                        self.reg[a] = b
# push: 2 a
#   push <a> onto the stack
                    elif cmd == 2:
                        val = self.getval()
                        self.stack.append(val)
# pop: 3 a
#   remove the top element from the stack and write it into <a>; empty stack = error
                    elif cmd == 3:
                        r = self.getreg()
                        if len(self.stack) == 0:
                            print("> error pop {}: stack empty".format(r))
                        else:
                            self.reg[r] = self.stack.pop()
# eq: 4 a b c
#   set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
                    elif cmd == 4:
                        a, b, c = self.getreg(), self.getval(), self.getval()
                        if b == c:
                            self.reg[a] = 1
                        else:
                            self.reg[a] = 0
# gt: 5 a b c
#   set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
                    elif cmd == 5:
                        a, b, c = self.getreg(), self.getval(), self.getval()
                        if b > c:
                            self.reg[a] = 1
                        else:
                            self.reg[a] = 0
# jmp: 6 a
#   jump to <a>
                    elif cmd == 6:
                        self.jump()
# jt: 7 a b
#   if <a> is nonzero, jump to <b>
                    elif cmd == 7:
                        a, b = self.getval(), self.getval()
                        if a:
                            self.jump(b)
# jf: 8 a b
#   if <a> is zero, jump to <b>
                    elif cmd == 8:
                        a, b = self.getval(), self.getval()
                        if not a:
                            self.jump(b)
# add: 9 a b c
#   assign into <a> the sum of <b> and <c> (modulo 32768)
                    elif cmd == 9:
                        a, b, c = self.getreg(), self.getval(), self.getval()
                        self.reg[a] = (b+c)%(1<<15)
# mult: 10 a b c
#   store into <a> the product of <b> and <c> (modulo 32768)
                    elif cmd == 10:
                        a, b, c = self.getreg(), self.getval(), self.getval()
                        self.reg[a] = (b*c)%(1<<15)
# mod: 11 a b c
#   store into <a> the remainder of <b> divided by <c>
                    elif cmd == 11:
                        a, b, c = self.getreg(), self.getval(), self.getval()
                        self.reg[a] = b%c
# and: 12 a b c
#   stores into <a> the bitwise and of <b> and <c>
                    elif cmd == 12:
                        a, b, c = self.getreg(), self.getval(), self.getval()
                        self.reg[a] = b&c
# or: 13 a b c
#   stores into <a> the bitwise or of <b> and <c>
                    elif cmd == 13:
                        a, b, c = self.getreg(), self.getval(), self.getval()
                        self.reg[a] = b|c
# not: 14 a b
#   stores 15-bit bitwise inverse of <b> in <a>
                    elif cmd == 14:
                        a, b = self.getreg(), self.getval()
                        self.reg[a] = b^((1<<15)-1)
# rmem: 15 a b
#   read memory at address <b> and write it to <a>
                    elif cmd == 15:
                        a, b = self.getreg(), self.getval()
                        self.reg[a] = self.mem[b]
# wmem: 16 a b
#   write the value from <b> into memory at address <a>
                    elif cmd == 16:
                        a, b = self.getval(), self.getval()
                        self.mem[a] = b
# call: 17 a
#   write the address of the next instruction to the stack and jump to <a>
                    elif cmd == 17:
                        a = self.getval()
                        self.stack.append(self.ptr)
                        self.jump(a)
# ret: 18
#   remove the top element from the stack and jump to it; empty stack = halt
                    elif cmd == 18:
                        if len(self.stack) == 0:
                            self.running = False
                        else:
                            # print(self.stack)
                            self.jump(self.stack.pop())
# out: 19 a
#   write the character represented by ascii code <a> to the terminal
                    elif cmd == 19:
                        c = self.getval()
                        print(chr(c), end='')
# in: 20 a
#   read a character from the terminal and write its ascii code to <a>; it can be assumed that once input starts, it will continue until a newline is encountered; this means that you can safely read whole lines from the keyboard and trust that they will be fully read
                    elif cmd == 20:
                        a = self.getreg()
                        while len(self.buffer) == 0:
                            self.buffer = input("\ninput: ") + '\n'
                        self.reg[a] = ord(self.buffer[0])
                        self.buffer = self.buffer[1:]
# noop: 21
#   no operation
                    elif cmd == 21:
                        pass

# unknown command
#   raise an error
                    else:
                        raise Exception("--- UNKNOWN CMD: {} ---".format(cmd))
                except:
                    print()
                    print("> ERROR!")
                    for i in range(self.NREG):
                        print("> reg{} = {}".format(i, self.reg[i]))
                    print("> stack = ", self.stack)
                    raise

def test_r7_checks(vm):
    tmp = vm.reg[7]
    vm.reg[7] = 7
    print(vm.cr7nat(r0=3, r1=1))
    print(vm.cr7(r0=3, r1=1))
    vm.reg[7] = tmp

if __name__ == '__main__':
    vm = Synacor_VM("bin/challenge.bin", ROFF = (1<<15), NREG = 8, r7 = 25734)
    # vm.reg[7] = 29127
    # test_r7_checks(vm)
    # print(vm.find_r7())
    vm.run()

