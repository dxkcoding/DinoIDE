from mb import command,slot,gc
def value(addr=None):
	val = command(slot(addr,4),b'get_poten_val',2)
	if val != None:
		return val
	else:
		return 0
gc()