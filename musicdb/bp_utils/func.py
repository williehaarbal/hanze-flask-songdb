import math

############################################################
# Time in sec represented in a string format
############################################################
def sec_to_str(time: int) -> str:
    if time == -1:
        return 'E:RR'

    sec = time % 60
    sec = math.floor(sec)
    sec = str(sec).zfill(2)
    min = math.floor(time / 60)
    return f"{min}:{sec}"

