import unittest

from tools.dl import credit_entry, local_name


class LocalNameTest(unittest.TestCase):
    def test_local_name(self):
        self.assertEqual(local_name('Focal length f17mm.jpg'), 'focal-length-f17mm.jpg')
        self.assertEqual(local_name('Kew fountain (short exposure).JPG'), 'kew-fountain-short-exposure.jpg')
        self.assertEqual(local_name('Camera_focal length.GIF'), 'camera-focal-length.gif')


class CreditEntryTest(unittest.TestCase):
    II = {'descriptionurl': 'https://commons.wikimedia.org/wiki/File:A.jpg',
          'extmetadata': {'LicenseShortName': {'value': 'CC BY 2.0'},
                          'Artist': {'value': '<a href="x">Ivan  Petrov</a>\nsecond line'}}}

    def test_new_entry_copies_artist_to_author(self):
        e = credit_entry('A.jpg', self.II)
        self.assertEqual(e, {'title': 'A.jpg', 'page': 'https://commons.wikimedia.org/wiki/File:A.jpg',
                             'license': 'CC BY 2.0', 'artist': 'Ivan  Petrov', 'author': 'Ivan  Petrov'})

    def test_existing_author_is_kept(self):
        e = credit_entry('A.jpg', self.II, old={'author': 'I. Petrov', 'artist': 'старое'})
        self.assertEqual(e['author'], 'I. Petrov')
        self.assertEqual(e['artist'], 'Ivan  Petrov')
