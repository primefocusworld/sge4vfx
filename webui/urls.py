from handlers.simple import IndexHandler
from handlers.jobs import MainJobTable
from handlers.oneJob import OneJobTable
from handlers.queueStats import QueueStatsHandler
from handlers.quotas import QuotaHandler
from handlers.workers import WorkersHandler
from handlers.changePriority import ChangePriority
from handlers.deleteComplete import DeleteComplete
from handlers.deleteErrors import DeleteErrors
from handlers.deleteJob import DeleteJob
from handlers.reschedule import Reschedule
from handlers.retry import Retry
from handlers.readLog import ReadLog

url_patterns = [
    (r"/", IndexHandler),
    (r"/jobs", MainJobTable),
    (r"/queueStats", QueueStatsHandler),
    (r"/quotas", QuotaHandler),
    (r"/workers", WorkersHandler),
    (r"/oneJob", OneJobTable),
    (r"/changePriority", ChangePriority),
    (r"/deleteComplete", DeleteComplete),
    (r"/deleteErrors", DeleteErrors),
    (r"/deleteJob", DeleteJob),
    (r"/reschedule", Reschedule),
    (r"/retry", Retry),
    (r"/readLog", ReadLog),
]
