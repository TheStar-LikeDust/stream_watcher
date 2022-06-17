import unittest

from stream_watcher.controller import WatcherController
from tests.config_for_test import test_rtsp_url


def mock_callback(*args, **kwargs):
    pass


class ControllerTestCase(unittest.TestCase):
    def test_thread(self):
        """注册一个线程"""
        controller = WatcherController()

        with self.subTest('register_thread_watcher'):
            watcher = controller.register_thread_watcher(
                watcher_name='test_watch',
                rtsp_connect=test_rtsp_url,
            )

            watcher_info = controller.registered_watcher_info.get('test_watch')

            assert watcher is watcher_info.watcher
            assert watcher.is_alive()

        with self.subTest('exit_watcher'):
            controller.exit_watcher('test_thread')

    def test_process(self):
        """注册一个进程"""
        controller = WatcherController()

        with self.subTest('register_thread_watcher'):
            watcher = controller.register_process_watcher(
                watcher_name='test_watch',
                rtsp_connect=test_rtsp_url,
                check_callback=mock_callback,
                image_callback=mock_callback,
            )

            watcher_info = controller.registered_watcher_info.get('test_watch')

            assert watcher is watcher_info.watcher
            assert watcher.is_alive()

        with self.subTest('exit_watcher'):
            controller.exit_watcher('test_thread')


if __name__ == '__main__':
    unittest.main()
