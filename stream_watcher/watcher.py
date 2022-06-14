# -*- coding: utf-8 -*-
"""Watcher - 取流主进程.

"""
import ctypes

from abc import abstractmethod
from logging import getLogger
from threading import Thread
from typing import Callable
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor

from threading import Barrier as ThreadBarrier
from multiprocessing import Barrier as ProcessBarrier

from cv2 import VideoCapture

THREADPOOL_LIMIT: int = 10
"""取流线程池的最大线程数量"""


class BaseWatcher(object):
    """基于Opencv的基础取流类，实现了Thread、Process类的若干接口，可以像一个正常线程类一样使用

    Note::

        真实情况需要使用ThreadWatcher或ProcessThread。
    """
    connect: str
    """流的地址"""

    image_callback: Callable = None
    """图像帧处理回调"""

    image_callback_limit: int = 10
    """执行image_callback回调的间隔帧数"""

    check_callback: Callable = None
    """检查回调"""

    check_callback_limit: int = 10
    """执行check回调的间隔帧数"""

    # inner property:
    _video: VideoCapture = None
    """opencv 连接对象"""
    _pool: ThreadPoolExecutor = None
    """运行回调函数线程池"""

    def __init__(self,
                 rtsp_connect,
                 image_callback: Callable = None,
                 check_callback: Callable = None,

                 image_callback_limit: int = 10,
                 check_callback_limit: int = 10,
                 **kwargs):
        """
        Args:
            rtsp_connect (Any): 流的连接地址
            image_callback (Callable, optional): 图片处理回调函数. Defaults to None.
            check_callback (Callable, optional): 图片检查回调函数. Defaults to None.
            image_callback_limit (int, optional): 图片处理函数执行的间隔帧数. Defaults to 10.
            check_callback_limit (int, optional): 图片检查执行的间隔帧数. Defaults to 10.

        """
        # Fixed daemon
        super(BaseWatcher, self).__init__(daemon=True, **kwargs)

        self.connect = rtsp_connect

        self.image_callback = image_callback if image_callback else lambda x: None
        self.check_callback = check_callback if check_callback else lambda x: None

        self.image_callback_limit = image_callback_limit
        self.check_callback_limit = check_callback_limit

        # overdrive
        self.logger = getLogger(self.__class__.__name__)
        self.logger.info(f'watcher {rtsp_connect} start.')
        self.start()

    def run(self) -> None:
        """
        Watcher的主要逻辑::

            1. 开启Opencv视频流连接
            2. 循环读取帧
            2.1 间隔image_callback_limit帧执行一次image_callback
            2.2 间隔check_callback_limit帧执行一次check_callback
        """

        self._video = VideoCapture(self.connect)
        self._pool = ThreadPoolExecutor(10)

        # 帧检查数
        count = 0
        while self._video.isOpened():
            _, image = self._video.read()

            assert _, 'read() status is False.'

            # TODO: check
            # if count % self.check_callback_limit == 0:
            #     assert self.check(image)

            if count % self.image_callback_limit == 0:
                f = self._pool.submit(self.image_callback, image)

            count += 1

    @abstractmethod
    def exit_watcher(self):
        pass


class ThreadWatcher(BaseWatcher, Thread):
    """基于线程的Watcher"""

    barrier: ThreadBarrier

    def __init__(self, rtsp_connect,
                 image_callback: Callable = None,
                 check_callback: Callable = None,
                 check_callback_limit: int = 10,
                 image_callback_limit: int = 10,
                 **kwargs):
        BaseWatcher.__init__(self, rtsp_connect, image_callback, check_callback, check_callback_limit,
                             image_callback_limit, **kwargs)
        self.barrier = ThreadBarrier(2)

    def exit_watcher(self):
        """线程退出"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, ctypes.py_object(SystemExit))


class ProcessWatcher(BaseWatcher, Process):
    """基于进程的Watcher, lambda等无法pickle的函数无法进入子进程"""

    barrier = ProcessBarrier

    def __init__(self, rtsp_connect,
                 image_callback: Callable,
                 check_callback: Callable,
                 check_callback_limit: int = 10,
                 image_callback_limit: int = 10,
                 **kwargs):
        BaseWatcher.__init__(self, rtsp_connect, image_callback, check_callback, check_callback_limit,
                             image_callback_limit, **kwargs)
        self.barrier = ProcessBarrier(2)

    def exit_watcher(self):
        """退出进程"""
        self.terminate()
