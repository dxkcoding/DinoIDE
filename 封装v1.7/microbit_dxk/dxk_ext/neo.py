from mb import command,slot,gc
_=b'%c%c%c'
RING = 'R'
ARRAY = 'A'
BELT = 'B'
RAINBOW = 'N'
CHAMELEON = 'H'
CONFETTI = 'O'
def init(grps,addr=None):
	cmd=b'init%c'%len(grps)
	for t in grps:
		cmd+=b'%c'%t
	command(slot(addr,15),cmd,1)
def pixel(g,pos,c,addr=None):
	command(slot(addr,15),b'setP%c%c'%(g,pos)+_%c,1)
def pixel_range(g,pos,cs,addr=None):
	i,X=0,len(cs)
	while i<X:
		css=cs[i:i+8]
		cmd=b'setL'+_%(g,pos,len(css))
		for c in css:
			cmd+=_%c
		command(slot(addr,15),cmd,1)
		i+=8;pos+=8
def array_xy(g,x,y,c,addr=None):
	command(slot(addr,15),b'setX%c%c%c'%(g,x,y)+_%c,1)
def fill(g,c,addr=None):
	command(slot(addr,15),b'fill%c'%g+_%c,1)
def flash(g,t,x,n,addr=None):
	command(slot(addr,15),b'rnbl%c%c%c%c '%(g,t,x,n),1)
gc()