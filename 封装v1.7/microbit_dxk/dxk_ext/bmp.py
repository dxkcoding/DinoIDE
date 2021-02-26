from mb import command,slot,gc
def value_p(addr = None):
	val = command(slot(addr,26),b'getP',2)
	if val != None:
		return val
	else:
		return 0
def value_t(addr = None):
	val = command(slot(addr,26),b'getT',2)
	if val != None:
		return val
	else:
		return 0
def value_a(addr = None):
	val = command(slot(addr,26),b'getA',2)
	if val != None:
		return val
	else:
		return 0
gc()