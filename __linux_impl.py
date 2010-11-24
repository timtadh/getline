'''
Getline - A library to get text from the console
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: __linux_impl
Purpose: The linux implementation of getline
'''


import os, sys, termios, fcntl, struct, subprocess
from tempfile import mkstemp as tmpfile

up = chr(27)+chr(91)+chr(65)
down = chr(27)+chr(91)+chr(66)
left = chr(27)+chr(91)+chr(68)
right = chr(27)+chr(91)+chr(67)
backspace = left + ' ' + left

class Getlines(object):

    def __init__(self, histfile=None):
        self.histfile = histfile
        self.fd = sys.stdin.fileno()
        self.curpos = [0, 0, 0]
        self.history = self.__loadhist()
        self.__init()

    def __init(self):
        winsz = fcntl.ioctl(self.fd, termios.TIOCGWINSZ, "        ")
        rows, cols, xpixel, ypixel = struct.unpack('HHHH', winsz)
        self.old = termios.tcgetattr(self.fd)
        new = termios.tcgetattr(self.fd)
        new[3] = new[3] & ~ termios.ICANON
        new[3] = new[3] & ~ termios.ECHOCTL
        termios.tcsetattr(self.fd, termios.TCSADRAIN, new)
        self.rows = rows
        self.cols = cols

    def __del__(self):
        import termios
        self.__savehist(self.history)
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    def __loadhist(self):
        if not self.histfile: return list()
        try:
            f = open(self.histfile, 'r')
        except:
            return list()
        hist = list()
        for l in f:
            l = list(l[:-1])
            if not l: continue
            hist.append(l)
        f.close()
        if len(hist) > 50: return hist[-50:]
        return hist

    def __savehist(self, hist):
        if not self.histfile: return
        try:
            f = open(self.histfile, 'w')
        except:
            return
        for l in hist:
            if not l: continue
            f.write(''.join(l) + '\n')
        f.close()

    def __clear_block(self, top):
        self.__mvcur((top+1, 0))
        for x in xrange(top+1):
            sys.stdout.write(down)
            self.__clear_line()

    def __clear_line(self):
        sys.stdout.flush()
        sys.stdout.write(left*self.cols)
        sys.stdout.write(' '*self.cols)
        sys.stdout.write(left*self.cols)
        sys.stdout.flush()

    def __moveleft(self, curpos, inpt):
        if curpos[2] == 0 and curpos[1] == 0:
            return
        elif curpos[2] > 0  and curpos[1] == 0:
            curpos[1] = self.cols - 1
            curpos[0] += 1
        elif curpos[1] > 0:
            curpos[1] -= 1
        if curpos[0] > curpos[2]: curpos[0] = curpos[2]

    def __moveright(self, curpos, inpt, prompt):
        old2 = curpos[2]
        old1 = curpos[1]
        if (len(inpt) + len(prompt))/self.cols > curpos[2]:
            curpos[2] = (len(inpt) + len(prompt))/self.cols
        if curpos[1] < self.cols - 1:
            curpos[1] += 1
        elif curpos[1] >= self.cols -1:
            curpos[1] = 0
            if curpos[0] > 0: curpos[0] -= 1
        if old2 != curpos[2] and old1 != self.cols-1:
            curpos[0] += 1
        if curpos[2] > old2:
            sys.stdout.write('\n')
            self.__clear_line()

    def __reset(self, curpos, prompt):
        curpos[0] = 0
        curpos[1] = len(prompt)
        curpos[2] = 0

    def __setcur(self, curpos, inpt, prompt):
        self.__reset(curpos, prompt)
        if len(inpt) < self.cols-len(prompt)+1:
            curpos[1] += len(inpt)
        else:
            curpos[2] = (len(inpt) + len(prompt))/self.cols
            curpos[1] = (len(inpt) + len(prompt))%self.cols

    def __mvcur(self, curpos):
        for x in xrange(self.rows): sys.stdout.write(down)
        for x in xrange(self.cols): sys.stdout.write(left)
        for x in xrange(curpos[0]): sys.stdout.write(up)
        for x in xrange(curpos[1]): sys.stdout.write(right)
        sys.stdout.flush()

    def getline(self, prompt=''):
        histpos = -1
        curpos = self.curpos
        self.__reset(curpos, prompt)
        self.__mvcur((0,0))
        sys.stdout.write(prompt)
        sys.stdout.flush()
        inpt = list()
        inptpos = 0
        x = ''
        while 1:
            try:
                x = os.read(self.fd, 1)
            except KeyboardInterrupt:
                sys.stdout.write('\n')
                self.__clear_line()
                print 'exit'
                sys.exit(1)
            #print x, ord(x)
            #continue
            if ord(x) == 127:
                if inpt == list(): continue
                if curpos[2] == curpos[0] and curpos[1] == len(prompt):
                    continue
                inptpos -= 1
                del inpt[inptpos]
                self.__moveleft(curpos, inpt)
            elif ord(x) == 1: ## crtl a
                inptpos = 0
                curpos[0] = curpos[2]
                curpos[1] = len(prompt)
            elif ord(x) == 5: ## ctrl e
                #print 'move end'
                inptpos = len(inpt)
                curpos[0] = 0
                curpos[1] = (len(inpt) + len(prompt))%self.cols
            elif ord(x) == 27:
                os.read(self.fd, 1)
                z = os.read(self.fd, 1)
                if ord(z) == 65: #up
                    sys.stdout.write(down)
                    if self.history: inpt = list(self.history[histpos])
                    if histpos == -1: histpos = len(self.history) - 1
                    histpos -= 1
                    inptpos = len(inpt)
                    self.__setcur(curpos, inpt, prompt)
                elif ord(z) == 66: #down
                    histpos = -1
                    inpt = list()
                    inptpos = 0
                    self.__reset(curpos, prompt)
                elif ord(z) == 67: #right
                    if inptpos < len(inpt):
                        inptpos += 1
                        self.__moveright(curpos, inpt, prompt)
                    else:
                        sys.stdout.write(left)
                elif ord(z) == 68: #left
                    if inptpos > 0:
                        inptpos -= 1
                        self.__moveleft(curpos, inpt)
                    else:
                        sys.stdout.write(right)
                else:
                    print ord(z)
            else:
                if x == '\n': break
                inpt.insert(inptpos, x)
                inptpos += 1
                self.__moveright(curpos, inpt, prompt)

            self.__clear_block(curpos[2])
            self.__mvcur((curpos[2], 0))
            self.__clear_line()
            sys.stdout.write(prompt)
            r = 0
            l = min(self.cols-len(prompt), len(inpt))
            sys.stdout.write(''.join(inpt[r:l]))
            sys.stdout.flush()
            while l < len(inpt):
                sys.stdout.write(down)
                self.__clear_line()
                sys.stdout.flush()
                r = l
                l = min(l+self.cols, len(inpt))
                sys.stdout.write(''.join(inpt[r:l]))
                sys.stdout.flush()
            if curpos[0] < curpos[2] and curpos[1] == 0:
                sys.stdout.write(down)
                self.__clear_line()
                sys.stdout.flush()
            sys.stdout.flush()
            self.__mvcur(curpos)

        if inpt and (not self.history or not ''.join(self.history[-1]) == ''.join(inpt)):
            self.history.append(inpt)
        histpos = -1
        return ''.join(inpt)

getline = Getlines().getline
