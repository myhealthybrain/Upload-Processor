import os,time,subprocess

pidfile = "/tmp/filecopier.pid"

def check_pid(pid):
    try: os.kill(pid,0)
    except OSError:
        return False
    else:
        return True

def runProgram():
    python_script = "/Processing/scripts/main.py"
    subprocess.Popen(["python",python_script])
    return


while 1:
    time.sleep(300)
    if os.path.isfile(pidfile):
        pid_string = open(pidfile, 'r').read()
        pid_int = int(pid_string)
        pid_is_running = check_pid(pid_int)
        if pid_is_running:
            print "Program is running."
        else:
            print "Program is not running"
            runProgram()
    else:
        print "No PID file found."

