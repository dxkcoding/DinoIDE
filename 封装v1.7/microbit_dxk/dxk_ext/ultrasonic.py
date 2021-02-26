from mb import command,slot,gc
def value(addr=None):
	val = command(slot(addr,8),b'get_distance_val',2)
	if val != None:
		return val
	else:
		return 0
gc()