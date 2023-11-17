from gi.repository import GLib
from concurrent.futures import ThreadPoolExecutor

thread_pool = ThreadPoolExecutor(max_workers=None, thread_name_prefix="swm")


def threaded_timeout(milliseconds: int, callable, *args, **kwargs):
    def timeout_callback() -> bool:
        thread_pool.submit(callable, *args, **kwargs)
        return True

    GLib.timeout_add(
        milliseconds,
        timeout_callback,
    )
