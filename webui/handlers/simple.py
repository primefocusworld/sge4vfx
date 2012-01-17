from handlers.base import BaseHandler

import logging
logger = logging.getLogger('theq2.' + __name__)


class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")
