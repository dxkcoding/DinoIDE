from mb import command,slot,gc
def power(val,addr=None):
    if val >= 1023:val = 1023
    elif val <= -1023:val = -1023
    command(slot(addr,20),b'get%s%c'%('bf'[val>0],abs(val)//4))
    return 0
gc()