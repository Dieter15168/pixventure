# media/jobs/dispatcher.py
from celery import group, chain
from media.tasks import run_version_task, run_duplicate_detection
import logging

logger = logging.getLogger(__name__)

def dispatch(task_name, media_item_id, config, regenerate=False):
    """
    Return an immutable task signature for the generic run_version_task.
    """
    return run_version_task.si(task_name, media_item_id, config, regenerate)

def dispatch_concurrent(task_list):
    """
    Accepts a list of task dictionaries and dispatches them concurrently.
    Each dictionary should contain: task_name, media_item_id, config, regenerate.
    """
    tasks = [
        dispatch(t['task_name'], t['media_item_id'], t['config'], t.get('regenerate', False))
        for t in task_list
    ]
    result = group(tasks).apply_async(ignore_result=True)
    logger.info("Dispatched group with %d tasks.", len(tasks))
    return result

def dispatch_chain(task_list):
    """
    Accepts a list of task dictionaries and dispatches them in sequence (chain).
    """
    tasks = [
        dispatch(t['task_name'], t['media_item_id'], t['config'], t.get('regenerate', False))
        for t in task_list
    ]
    result = chain(*tasks).apply_async(ignore_result=True)
    logger.info("Dispatched chain with %d tasks.", len(tasks))
    return result

def dispatch_fuzzy_hash(media_item_version_id, hash_type, regenerate=False):
    """
    Returns a task signature for computing the fuzzy hash.
    """
    config = {"hash_type": hash_type}
    return dispatch("fuzzy_hash", media_item_version_id, config, regenerate)

def dispatch_duplicate_detection():
    """
    Returns the signature for the duplicate detection task.
    Note that this task will accept the output (context) of the fuzzy hash task.
    By using .s() (not .si()), we allow the chain output to be passed as an argument.
    """
    return run_duplicate_detection.s()