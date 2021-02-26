from mb import command,slot,gc
def angle(val,addr=None):
    if val >= 270:val = 270
    elif val <= 0:val = 0
    command(slot(addr,37),b'conA%c'%(int(val/1.5)))
    return 0
gc()