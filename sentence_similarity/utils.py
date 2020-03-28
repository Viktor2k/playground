import time
import logging

logger = logging.getLogger(__name__)

def timer(f, *args, **kwargs):
    start = time.time()
    out = f(*args, **kwargs)
    logger.info(f"Took {round(time.time() - start , 3)} to execute {f.__name__}")
    return out
#end def