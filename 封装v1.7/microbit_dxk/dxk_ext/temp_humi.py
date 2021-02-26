from mb import command,slot,gc
def temp(addr=None):
	val = command(slot(addr,2),b'get_temp',1)
	if val != None:
		return val
	else:
		return 0
def humi(addr=None):
	val = command(slot(addr,2),b'get_humi',1)
	if val != None:
		return val
	else:
		return 0
def temp_humi(addr=None):
	res1=command(slot(addr,2),b'get_temp',1)
	res2=command(slot(addr,2),b'get_humi',1)
	if res1==None:res1=0
	if res2==None:res2=0
	return tuple((res1,res2))
def value_t(addr=None):
	return temp(addr)
def value_h(addr=None):
	return humi(addr)
def value_th(addr=None):
	return temp_humi(addr)
gc()