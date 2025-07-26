import threading
from typing import Optional


class RelationalThread(threading.Thread):
    _parent_thread: Optional[int] = None

    def __init__(self, *args, **kwargs):
        self._collect_parent_thread()
        threading.Thread.__init__(self, *args, **kwargs)

    def _collect_parent_thread(self) -> None:
        self._parent_thread = threading.get_ident()

    def get_parent_thread(self) -> Optional[int]:
        return self._parent_thread
