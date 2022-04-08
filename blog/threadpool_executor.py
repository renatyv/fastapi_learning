import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor

thread_pool = ThreadPoolExecutor()


async def run_asynchonously(func, *args, **kwargs):
    """Run function in a threadpool. Note, that threads are ineffective for CPU-bound tasks.
    ProcessPoolExecutor can be used instead for CPU-bound tasks.
    :returns whatever func returns"""
    current_event_loop = asyncio.get_running_loop()
    get_posts_partial = functools.partial(func, *args, **kwargs)
    result = await current_event_loop.run_in_executor(thread_pool, get_posts_partial)
    return result


def teardown():
    """shutdown the threadpool"""
    thread_pool.shutdown(wait=False)