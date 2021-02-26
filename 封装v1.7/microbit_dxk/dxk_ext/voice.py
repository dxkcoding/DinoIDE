from mb import command,slot,gc
def get_voice_id(addr):
	val = command(slot(addr,33),b'get_command',1)
	if val != None:
		return val
	else:
		return 0
gc()