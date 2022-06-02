import sched, time


s = sched.scheduler()


def foobar(a="default"):
    print("hello")

s.enter(10, 1, foobar)