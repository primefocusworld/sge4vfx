from handlers.simple import IndexHandler
from handlers.jobs import MainJobTable
from handlers.oneJob import OneJobTable
from handlers.queueStats import QueueStatsHandler
from handlers.quotas import QuotaHandler
from handlers.workers import WorkersHandler

url_patterns = [
    (r"/", IndexHandler),
    (r"/jobs", MainJobTable),
    (r"/queueStats", QueueStatsHandler),
    (r"/quotas", QuotaHandler),
    (r"/workers", WorkersHandler),
    (r"/oneJob", OneJobTable),
]
