#!/usr/bin/env python3
#
# Tests for the ResetDateTime extension.
#
# Run them with:
#   python3 tests.py
#
"""Tests for ResetDateTime (ResetDateTime.py)."""
import os
import subprocess
import sys
import tempfile
import time
import unittest

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(ROOT_DIR, 'ResetDateTime.py')

# Exit codes NZBGet understands
POSTPROCESS_SUCCESS = 93
POSTPROCESS_ERROR = 94
POSTPROCESS_NONE = 95

# A date well in the past (Jan 1st, 2020)
OLD_TIME = 1577836800


def run(**env):
    """
    Run ResetDateTime.py like NZBGet would, with these NZBPP_* values set.

    Returns (exit code, output).
    """
    environ = {
        key: value for key, value in os.environ.items()
        if not key.startswith('NZB')}
    environ.update(env)

    result = subprocess.run(
        [sys.executable, SCRIPT], env=environ, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    return result.returncode, result.stdout


class TestResetDateTime(unittest.TestCase):
    """ResetDateTime behaviour."""

    def setUp(self):
        """Make a download folder full of old files."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.download = self.tmpdir.name
        os.makedirs(os.path.join(self.download, 'Subs'))

        self.files = [
            os.path.join(self.download, 'Movie.mkv'),
            os.path.join(self.download, 'Subs', 'Movie.en.srt'),
        ]
        for path in self.files:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('data')
            os.utime(path, (OLD_TIME, OLD_TIME))

        # What NZBGet passes to a post-processing script
        self.env = {
            'NZBOP_SCRIPTDIR': ROOT_DIR,
            'NZBOP_VERSION': '26.0',
            'NZBPP_DIRECTORY': self.download,
            'NZBPP_TOTALSTATUS': 'SUCCESS',
            'NZBPP_STATUS': 'SUCCESS/ALL',
        }

    def tearDown(self):
        self.tmpdir.cleanup()

    def assertReset(self, path):
        """The file's modified date is now."""
        self.assertGreater(os.stat(path).st_mtime, time.time() - 60)

    def assertUntouched(self, path):
        """The file still has its old date."""
        self.assertEqual(int(os.stat(path).st_mtime), OLD_TIME)

    def test_resets_every_file(self):
        """Every file, including ones in subfolders, gets today's date."""
        code, output = run(**self.env)
        self.assertEqual(code, POSTPROCESS_SUCCESS)
        self.assertIn('[INFO] Reset the date of 2 file(s).', output)
        for path in self.files:
            self.assertReset(path)

    def test_failed_download_is_skipped(self):
        """A failed download is left alone."""
        self.env['NZBPP_TOTALSTATUS'] = 'FAILURE'
        self.env['NZBPP_STATUS'] = 'FAILURE/PAR'

        code, output = run(**self.env)
        self.assertEqual(code, POSTPROCESS_NONE)
        self.assertIn('FAILURE/PAR', output)
        for path in self.files:
            self.assertUntouched(path)

    def test_missing_folder_is_skipped(self):
        """A download folder that's gone is skipped, not an error."""
        self.env['NZBPP_DIRECTORY'] = os.path.join(self.download, 'gone')

        code, output = run(**self.env)
        self.assertEqual(code, POSTPROCESS_NONE)
        self.assertIn('does not exist', output)

    def test_one_bad_file_does_not_stop_the_rest(self):
        """The other files are still reset, and the run reports a failure."""
        # A link to a file that doesn't exist can't have its date changed
        os.symlink(
            os.path.join(self.download, 'missing'),
            os.path.join(self.download, 'broken-link'))

        code, output = run(**self.env)
        self.assertEqual(code, POSTPROCESS_ERROR)
        self.assertIn('[ERROR] Could not reset the date of', output)
        for path in self.files:
            self.assertReset(path)

    def test_older_nzbget_with_poor_health(self):
        """Older NZBGet versions are checked by repair and health status."""
        del self.env['NZBPP_TOTALSTATUS']
        self.env.update({
            'NZBPP_PARSTATUS': '0',
            'NZBPP_UNPACKSTATUS': '0',
            'NZBPP_HEALTH': '850',
        })

        code, output = run(**self.env)
        self.assertEqual(code, POSTPROCESS_NONE)
        self.assertIn('health is compromised', output)
        self.assertNotIn('Traceback', output)

    def test_older_nzbget_with_good_download(self):
        """A good download on an older NZBGet version is reset."""
        del self.env['NZBPP_TOTALSTATUS']
        self.env.update({
            'NZBPP_PARSTATUS': '2',
            'NZBPP_UNPACKSTATUS': '2',
            'NZBPP_HEALTH': '1000',
        })

        code, _ = run(**self.env)
        self.assertEqual(code, POSTPROCESS_SUCCESS)
        for path in self.files:
            self.assertReset(path)

    def test_not_started_by_nzbget(self):
        """Running it by hand explains what it's for."""
        code, output = run()
        self.assertEqual(code, 1)
        self.assertIn('can only be called from NZBGet', output)


if __name__ == '__main__':
    unittest.main(verbosity=2)
