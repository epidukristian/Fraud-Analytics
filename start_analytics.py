import os, signal, subprocess, sys, time

BRANCHES_CLOSED = "branches_closed.flag"
EOD_COMPLETE = "eod_complete.flag"
PRIORITY = "priority_task.flag"
CHECK_EVERY, MAX_WAIT = 3, 120

def ready():
    return os.path.exists(BRANCHES_CLOSED) and os.path.exists(EOD_COMPLETE)

waited = 0
while not ready():
    missing = [f for f in (BRANCHES_CLOSED, EOD_COMPLETE) if not os.path.exists(f)]
    print("Waiting for:", ", ".join(missing))
    time.sleep(CHECK_EVERY)
    waited += CHECK_EVERY
    if waited >= MAX_WAIT:
        print("Conditions not met. Job stays queued for tomorrow night.")
        sys.exit(1)

print("Branches closed and end-of-day batch complete. Starting analytics job.")
job = subprocess.Popen([sys.executable, "fraud_scan.py"], env={**os.environ, "DELAY": "1"})
paused = False
while job.poll() is None:
    if os.path.exists(PRIORITY) and not paused:
        print(">> Priority task arrived: pausing analytics")
        job.send_signal(signal.SIGSTOP); paused = True
    elif not os.path.exists(PRIORITY) and paused:
        print(">> Priority task finished: resuming analytics")
        job.send_signal(signal.SIGCONT); paused = False
    time.sleep(1)
print("Analytics job finished. Results saved for the fraud team.")
