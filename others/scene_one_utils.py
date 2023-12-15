def time2db_field(time):
    if time == "0:00-6:00":
        return "one"
    elif time == "6:00-12:00":
        return "two"
    elif time == "12:00-18:00":
        return "three"
    elif time == "18:00-24:00":
        return "four"
    return None

def time2json_field(time):
    if time == "0:00-6:00":
        return "midnight"
    elif time == "6:00-12:00":
        return "morning"
    elif time == "12:00-18:00":
        return "afternoon"
    elif time == "18:00-24:00":
        return "evening"
    return None

def trans_freq(arg):
    arr = arg.split("-")
    for i,freq in enumerate(arr):
        arr[i] = int(freq)
    return arr
