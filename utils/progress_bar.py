import sys

barChar = "█"

bufferedString = ""
total = 0
msg = ""

def setMaxLimit(max, set_msg="Total Progress"):
    global total, msg
    total = max
    msg = set_msg


def progressBar(current):
    completed = 100 * (current / float(total))
    barProgress = "=" * int(completed / 2) + "-" * (50 - int(completed / 2))
    sys.stdout.write(f"\r{msg}: |{barProgress}| {completed:.0f}%\n")
    sys.stdout.flush()
    if completed >= 100.0:
        print("\nProcessing complete!")

