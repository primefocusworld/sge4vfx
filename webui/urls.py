from handlers.simple import IndexHandler
from handlers.jobs import MainJobTable

url_patterns = [
    (r"/", IndexHandler),
    (r"/jobs", MainJobTable),
]
