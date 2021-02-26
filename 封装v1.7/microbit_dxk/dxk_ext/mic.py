from mb import command,slot,gc
def value(addr=None):
	val = command(slot(addr,6),b'get_mic_val',2)
	if val != None:
		return val
	else:
		return 0
gc()