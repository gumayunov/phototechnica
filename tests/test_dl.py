import unittest

from tools.dl import local_name


class LocalNameTest(unittest.TestCase):
    def test_local_name(self):
        self.assertEqual(local_name('Focal length f17mm.jpg'), 'focal-length-f17mm.jpg')
        self.assertEqual(local_name('Kew fountain (short exposure).JPG'), 'kew-fountain-short-exposure.jpg')
        self.assertEqual(local_name('Camera_focal length.GIF'), 'camera-focal-length.gif')
