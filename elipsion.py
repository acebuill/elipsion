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
CACHEFILE = CACHEDIR + "/elipsion.txt"

ensurecachedirexists = lambda: Path(CACHEDIR).mkdir(
    parents=True, exist_ok=True
)

cachefileexists = lambda: os.access(CACHEFILE, os.F_OK)

ensurecachefileexists = (
    lambda: writetocachefile("0 0") if not cachefileexists() else ""
)

getprogramprocess = lambda programname: [
    programprocess
    for programprocess in psutil.process_iter()
    if programprocess.name() == programname
][0]

writetocachefile = lambda str_: open(CACHEFILE, "w").write(str_)

parseepsilonconf = lambda: list(
    map(lambda i: abs(float(i)), open(CACHEFILE, "r").read().split(" "))
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


def limitprogramruntime(processname, limit):
    try:
        process = getprogramprocess(processname)
    except IndexError:
        time.sleep(1)
        limitprogramruntime(processname, limit)
    cache = parseepsilonconf()
    rawruntime = time.time() - process.create_time()
    extratime = cache[1] if needstobecontinued(rawruntime, cache) else 0
    runtime = rawruntime + extratime
    if exceedslimit(runtime, limit):
        startprocessblock(processname)
    while not exceedslimit(runtime, limit):
        try:
            _ = getprogramprocess(processname)
            runtime += 1
            writetocachefile(str(datetime.now().day) + " " + str(runtime))
        except IndexError:
            limitprogramruntime(processname, limit)
        finally:
            time.sleep(1)
    startprocessblock(processname)


if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    ensurecachedirexists()
    ensurecachefileexists()
    limitprogramruntime(args["<processname>"], int(args["<limit>"]))
