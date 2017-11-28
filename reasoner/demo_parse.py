def print_dict(d):
    for k,v in d.items():
        print(k)
        for k2,v2 in v.items():
            print('    ' + k2 + ': ' + str(v2))
        print()
