"0 0"
import psutil
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
    lambda: writetocachefile(__doc__) if not cachefileexists() else ""
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
        except:
            time.sleep(1)


def limitprogramruntime(processname, limit):
    try:
        process = getprogramprocess(processname)
    except IndexError:
        time.sleep(1)
        limitprogramruntime(processname, limit)
    cache = parseepsilonconf()
    runtime = time.time() - process.create_time()
    extratime = cache[1] if needstobecontinued(runtime, cache) else 0
    runtime = runtime + extratime
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
    ensurecachedirexists()
    ensurecachefileexists()
    try:
        limitprogramruntime("telegram-desktop", 3400)
    except KeyboardInterrupt:
        sys.exit(1)
