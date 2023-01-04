open('res.zip','wb').write(bytes.fromhex(open('res.txt','r').read().split('False')[1]))
