# 2018-03-31


def list2file(lst, out_file):  # 80321 Turtle-8 - 80330 moved here from .utl.utl
    string = ''
    for i,line in enumerate(lst):
        if i > 0: string += '\n'
        for j,x in enumerate(line):
            if isinstance(x, (list, set, tuple)):
                z = ' '.join(str(y) for y in x)
            else:
                try: z = str(x)
                except TypeError: z = 'ERROR'
            if j > 0: string += '\t'
            string += z
    with open (out_file, 'w') as f: f.write(string)
    return string


# 2018-03-31 moved here from .utl.py
