from handlers.simple import IndexHandler
from handlers.jobs import MainJobTable
from handlers.shelltest import ShellHandler
from handlers.queueStats import QueueStatsHandler
from handlers.quotas import QuotaHandler

url_patterns = [
    (r"/", IndexHandler),
    (r"/jobs", MainJobTable),
    (r"/shell", ShellHandler),
    (r"/queueStats", QueueStatsHandler),
    (r"/quotas", QuotaHandler),
]
