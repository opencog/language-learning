# 2018-03-30


def UTC():
    import datetime
    return str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))


def round_float(x, n_digits):
    if type(x) == float:
        if abs(x) < 0.5*10**(-n_digits): return 0.0
        else: return round(x, n_digits)
    else: return x

def round1(x): return round_float(x, 1)
def round2(x): return round_float(x, 2)
def round3(x): return round_float(x, 3)
def round4(x): return round_float(x, 4)
def round5(x): return round_float(x, 5)


# 2018-03-30: code restructured, smth ⇒ read_files.py, write_files.py
