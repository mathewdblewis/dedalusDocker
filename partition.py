#!/home/mdbl/miniconda3/bin/python

from sys import argv; import os

try: _,m,s,ins,out = argv
except:
    print('input format: mode [a or p], size, input, output')
    exit(1)
try:
        s = [int(x) for x in s.split('.')]
        assert(s[0]>0 and s[1]>=0)
        s = s[0]*10**s[1]
except:
        print('size must be of the form x.y which denotes x*10**y, with x>0 and y>=0')
        exit(1)


if m == 'p':
        os.mkdir(out)
        x = open(ins,'rb').read()
        for i in range(len(x)//s+1): open(out+'/%d'%i,'wb').write(x[i*s:i*s+s])

elif m == 'a':
        try: x,i = open(ins+'/0','rb').read(),1
        except:
                print('"%s" does not exist' % ins)
                exit(1)
        while True:
            try: x += open(ins+'/%d'%i,'rb').read()
            except: break
            i+=1
        open(out,'wb').write(x)

else:
        print('mode must be p (partition) or a (assemble)')
        exit(1)

