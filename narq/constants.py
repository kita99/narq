import os

QUEUE_KEY_PREFIX = "narq:queue:"
DEFAULT_QUEUE: str = f"{QUEUE_KEY_PREFIX}default"
DELAY_QUEUE = f"{QUEUE_KEY_PREFIX}delay"
TASK_KEY = "narq:task"
WORKER_KEY = "narq:worker"
WORKER_KEY_LOCK = "narq:worker:lock"
WORKER_KEY_TIMER_LOCK = "narq:timer:lock"
WORKER_TASK_LOCK = "narq:task:lock:{task}"
WORKER_HEARTBEAT_SECONDS = 10
STATIC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER_DIR = os.getcwd()
JOB_TIMEOUT_UNLIMITED = object()
CHANNEL = "narq:channel"
