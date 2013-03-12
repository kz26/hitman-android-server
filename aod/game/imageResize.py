from subprocess import Popen

def enlarge(fn):
    args = ['convert', fn, '-resize', '250%', fn]
    Popen(args).communicate()
