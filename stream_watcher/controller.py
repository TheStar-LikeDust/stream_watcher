# -*- coding: utf-8 -*-
"""Watcher管理器

"""
import time
import os, sys
from logging import getLogger
from threading import Thread
from typing import Dict, Callable, Union

from .watcher import ThreadWatcher, ProcessWatcher

logger = getLogger(__name__)
"""日志类"""


class WatcherController(Thread):
    """取流类Watcher的控制器，可以统一管理取流类。

    能够在主进程中管理基于线程/进程的取流类，并且可以自动检查取流类状况，能够自动启停取流类。

    """

    registered_infos: Dict[str, dict]
    """Watcher类的启动参数。"""
    registered_watcher = Dict[str, Union[ThreadWatcher, ProcessWatcher]]
    """保存Watcher类的字典。"""

    def __init__(self, check_cycle: int = 10, **kwargs):
        """初始化时自动执行，并且固定为守护进程。

        Args:
            check_cycle (int, optional): 检查周期，间隔多少秒执行一次检查. Defaults to 10.
        """

        super(WatcherController, self).__init__(daemon=True, **kwargs)

        self.registered_infos: Dict[str, dict] = {}
        self.registered_watcher: Dict[str, Union[ThreadWatcher, ProcessWatcher]] = {}
        self.check_cycle = check_cycle
        self.start()

    def run(self) -> None:
        """
        取流控制器主要逻辑::

            无限循环:
                1. 等待check_cycle秒
                2. 遍历检查Watcher类:
                    case: alive为True - Watcher正常
                    case: alive为False - Watcher退出，根据之前保存的参数重新启动此Watcher。

        """
        while True:
            time.sleep(self.check_cycle)

            for watcher_name, watcher in self.registered_watcher.items():
                if not watcher.is_alive():
                    logger.info(f'rebuilding.. {watcher_name}')

                    watcher_kwargs = self.registered_infos.pop(watcher_name)
                    watcher = self.registered_watcher.pop(watcher_name)

                    if isinstance(watcher, ThreadWatcher):
                        self.register_thread_watcher(watcher_name, **watcher_kwargs)
                    else:
                        self.register_process_watcher(watcher_name, **watcher_kwargs)

    def register_thread_watcher(self,
                                watcher_name: str,
                                rtsp_connect,
                                image_callback: Callable = None,
                                check_callback: Callable = None,
                                image_callback_limit: int = 10,
                                check_callback_limit: int = 10,
                                **kwargs) -> ThreadWatcher:
        """创建取流线程"""

        watcher_kwargs = {
            'rtsp_connect': rtsp_connect,
            'image_callback': image_callback,
            'check_callback': check_callback,
            'image_callback_limit': image_callback_limit,
            'check_callback_limit': check_callback_limit,
            **kwargs,
        }

        watcher = ThreadWatcher(**watcher_kwargs)
        self.registered_infos[watcher_name] = watcher_kwargs
        self.registered_watcher[watcher_name] = watcher

        return watcher

    def register_process_watcher(self,
                                 watcher_name,
                                 rtsp_connect,
                                 image_callback: Callable = None,
                                 check_callback: Callable = None,
                                 image_callback_limit: int = 10,
                                 check_callback_limit: int = 10,
                                 **kwargs) -> ProcessWatcher:
        """创建取流进程"""

        watcher_kwargs = {
            'rtsp_connect': rtsp_connect,
            'image_callback': image_callback,
            'check_callback': check_callback,
            'image_callback_limit': image_callback_limit,
            'check_callback_limit': check_callback_limit,
            **kwargs,
        }

        watcher = ProcessWatcher(**watcher_kwargs)
        self.registered_infos[str(watcher_name)] = watcher_kwargs
        self.registered_watcher[str(watcher_name)] = watcher

        return watcher

    def exit_watcher(self, watcher_name: str):
        """手动退出一个watcher"""

        watcher = self.registered_watcher.get(watcher_name)

        if watcher:
            watcher.exit_watcher()
            self.registered_watcher.pop(watcher_name)

    def __del__(self):
        watcher = self.registered_watcher.values()
        [_.exit_watcher() for _ in watcher]
