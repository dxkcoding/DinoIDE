from mb import command,slot,gc
def on(addr=None):
	command(slot(addr,3),b'set_led_on')
def off(addr=None):
	command(slot(addr,3),b'set_led_off')
def color(r,g,b,addr=None):
	command(slot(addr,3),b'setC%c%c%c'%(r,g,b))
gc()