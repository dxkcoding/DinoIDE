from mb import command,slot,gc
def value(addr=None):
    val = command(slot(addr,9),b'get_touch',1)
    if val != None:
        return val
    else:
        return 0
gc()