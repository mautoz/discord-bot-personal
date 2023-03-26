#!/usr/bin/env python3

from datetime import datetime, timedelta


class Session:
    def __init__(self, expiration_time=timedelta(minutes=5)):
        self.expiration_time = expiration_time
        self.start_time = datetime.now()

    def _check_expired(self):
        elapsed_time = datetime.now() - self.start_time
        if elapsed_time > self.expiration_time:
            return True

        return False
