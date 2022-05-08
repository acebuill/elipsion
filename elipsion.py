"""
elipsion
    
Usage:
    elipsion <processname> <limit>

Options:
  -h --help     Show this screen.
"""
import psutil
import docopt
from datetime import datetime
import time
from pathlib import Path
import os
import sys

CACHEDIR = "/home/" + os.getlogin() + "/.cache/elipsion"

cachefilepath = lambda procname : f"{CACHEDIR}/{procname}.txt"

ensurecachedirexists = lambda: Path(CACHEDIR).mkdir(
    parents=True, exist_ok=True
)

cachefileexists = lambda procname: os.access(f"{CACHEDIR}/{procname}.txt", os.F_OK)

ensurecachefileexists = (
    lambda cachepath: writetofile(cachepath, "0 0") if not cachefileexists(cachepath) else ""
)

getprogramprocess = lambda programname: [
    programprocess
    for programprocess in psutil.process_iter()
    if programprocess.name() == programname
][0]

writetofile = lambda fname, str_: open(fname, "w").write(str_)

parseepsiloncache = lambda cachefilepath: list(
    map(lambda i: abs(float(i)), open(cachefilepath, "r").read().split(" "))
)

needstobecontinued = (
    lambda processruntime, cache: True
    if cache[0] == datetime.now().day and cache[1] >= processruntime
    else False
)

exceedslimit = lambda runtime, limit: True if runtime > limit else False


def startprocessblock(processname):
    while True:
        try:
            os.kill(getprogramprocess(processname).pid, 9)
        except IndexError:
            time.sleep(1)


def limitprogramruntime(processname, limit, cachepath):
    try:
        process = getprogramprocess(processname)
    except IndexError:
        time.sleep(1)
        limitprogramruntime(processname, limit, cachepath)
    cache = parseepsiloncache(cachepath)
    rawruntime = time.time() - process.create_time()
    extratime = cache[1] if needstobecontinued(rawruntime, cache) else 0
    runtime = rawruntime + extratime
    if exceedslimit(runtime, limit):
        startprocessblock(processname)
    while not exceedslimit(runtime, limit):
        try:
            _ = getprogramprocess(processname)
            runtime += 1
            writetofile(cachepath, f"{datetime.now().day} {runtime}")
        except IndexError:
            limitprogramruntime(processname, limit, cachepath)
        finally:
            time.sleep(1)
    startprocessblock(processname)


if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    CACHE_FILE_PATH = cachefilepath(args["<processname>"])
    ensurecachedirexists()
    ensurecachefileexists(CACHE_FILE_PATH)
    limitprogramruntime(args["<processname>"], int(args["<limit>"]), CACHE_FILE_PATH)
