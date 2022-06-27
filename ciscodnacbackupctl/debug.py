import logging
import sys
from http.client import HTTPConnection


class Debug:
    """Debug to Console"""

    def __init__(self) -> None:
        """Setup"""
        self.filename = "debug.txt"
        HTTPConnection.debuglevel = 2
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s: %(message)s",
            stream=sys.stdout,
        )
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
        pass

    @staticmethod
    def payload(data):
        """HTTP Payload"""
        logger = logging.getLogger(__name__)
        logger.debug(str(data))
