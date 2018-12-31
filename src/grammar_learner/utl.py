# language-learning/src/grammar_learner/utl.py                          # 81231
import datetime, time


def UTC():
    return str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))


def round_float(x, n_digits):
    if type(x) == float:
        if abs(x) < 0.5 * 10 ** (-n_digits):
            return 0.0
        else:
            return round(x, n_digits)
    else:
        return x

def round1(x): return round_float(x, 1)
def round2(x): return round_float(x, 2)
def round3(x): return round_float(x, 3)
def round4(x): return round_float(x, 4)
def round5(x): return round_float(x, 5)


def timer(string, t0 = 0):
    t1 = time.time()
    if t0 < 0.01:
        print(UTC(), '::', string)
        dt = 0
    else:
        dt = t1 - t0
        if dt < 1:
            dt = round(dt, 2)
            print(UTC(), '::', string, 'in', dt, 'seconds')
        elif dt < 300:
            dt = int(round(dt, 0))
            print(UTC(), '::', string, 'in', dt, 'seconds')
        else:
            dt = int(round(dt, 0))
            print(UTC(), '::', string, 'in', int(round(dt / 60, 0)), 'minutes')
    return t1, dt


def kwa(v, k, **kwargs):
    return kwargs[k] if k in kwargs else v


def sec2string(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)


def test_stats(log):
    return 'Cleaned dictionary: ' + str(log['cleaned_words']) \
           + ' words, grammar learn time: ' + log['grammar_learn_time'] \
           + ', test time: ' + log['grammar_test_time'] + ' (hh:mm:ss)'


# Notes

# 81231 cleanup
