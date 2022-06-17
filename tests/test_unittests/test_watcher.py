import unittest

from stream_watcher.watcher import ThreadWatcher

from tests.config_for_test import test_rtsp_url

current_rtsp = test_rtsp_url


class Mock:
    count = 0

    def count_callback(self, image):
        self.count += 1
        print(image.shape)


class WatcherTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mock = Mock()
        self.mock.count = 0

    def test_image_callback(self):
        """Watcher初始化"""

        watch = ThreadWatcher(rtsp_connect=current_rtsp, image_callback=self.mock.count_callback)

    # def test_thread_exit(self):
    #     """线程退出"""
    #     watch = ThreadWatcher(rtsp_connect=current_rtsp, image_callback=self.mock.count_callback)

    def test_watch_arguments(self):
        rtsp_url = 1

        check_callback = lambda x: True

        watch = ThreadWatcher(
            rtsp_connect=rtsp_url,

            image_callback=self.mock.count_callback,
            check_callback=check_callback,

            image_callback_limit=5,
            check_callback_limit=15,

            name='the_name_1153')

        with self.subTest('connect'):
            assert watch.connect == rtsp_url

        with self.subTest('image_callback'):
            assert watch.image_callback == self.mock.count_callback

        with self.subTest('check_callback'):
            assert watch.check_callback == check_callback

        with self.subTest('image_callback_limit'):
            assert watch.image_callback_limit == 5

        with self.subTest('check_callback_limit'):
            assert watch.check_callback_limit == 15

        with self.subTest('thread: name'):
            assert watch.name == 'the_name_1153'

        with self.subTest('thread: Daemon is fixed. True'):
            assert watch.daemon is True


if __name__ == '__main__':
    unittest.main()
