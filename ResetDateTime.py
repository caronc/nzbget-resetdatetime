#!/usr/bin/env python3
#
# Reset the dates of downloaded files for NZBGet.
#
# Copyright (C) 2013-2014 Clinton Hall
#
# Changed in 2026 to run on Python 3 and as an NZBGet v23+ extension.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

##############################################################################
### NZBGET POST-PROCESSING SCRIPT                                          ###

# Reset the Date Modified for downloaded files.
#
# This is useful for sorting "newly added" media.
# This should run before other scripts (move it to the top of the
# Extension Manager's Order list).
#
# NOTE: This script requires Python 3.8 or newer.

### NZBGET POST-PROCESSING SCRIPT                                          ###
##############################################################################
"""
Sets the modified date of every downloaded file to now.

Files inside a download keep the dates they were given when they were
packed, which can be months or years ago. Media players that sort by
"recently added" then bury your new downloads. Running this first fixes
that.
"""
import os
import sys

# Exit codes NZBGet understands
POSTPROCESS_SUCCESS = 93
POSTPROCESS_ERROR = 94
POSTPROCESS_NONE = 95


def download_ok():
    """
    Return True if the download worked, otherwise log why not.
    """
    total_status = os.environ.get('NZBPP_TOTALSTATUS')
    if total_status is not None:
        # NZBGet v13 and newer sum it up for us
        if total_status != 'SUCCESS':
            print(
                '[INFO] Download failed with status '
                f'{os.environ.get("NZBPP_STATUS", total_status)}.')
            return False

        return True

    # Older NZBGet versions: check the repair and unpack results ourselves
    par_status = os.environ.get('NZBPP_PARSTATUS', '0')
    unpack_status = os.environ.get('NZBPP_UNPACKSTATUS', '0')

    if par_status in ('1', '4'):
        print('[INFO] Par-repair failed.')
        return False

    if unpack_status == '1':
        print('[INFO] Unpack failed.')
        return False

    if par_status == '0' and unpack_status == '0' \
            and int(os.environ.get('NZBPP_HEALTH', '1000')) < 1000:
        # Nothing was repaired or unpacked, and pieces are missing
        print(
            '[INFO] Download health is compromised and Par-check/repair '
            'is disabled or no .par2 files were found.')
        return False

    return True


def reset_dates(directory):
    """
    Set the modified date of every file below directory to now.

    Returns the number of files that couldn't be changed.
    """
    changed = 0
    failed = 0

    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            try:
                # No times given means "now"
                os.utime(path, None)
                changed += 1
                print(f'[DETAIL] Reset the date of {path}')

            except OSError as error:
                # Keep going; one stubborn file shouldn't stop the rest
                failed += 1
                print(f'[ERROR] Could not reset the date of {path}: {error}')

    print(f'[INFO] Reset the date of {changed} file(s).')
    return failed


def main():
    """Reset the dates and return the exit code."""
    if 'NZBOP_SCRIPTDIR' not in os.environ:
        # Not started by NZBGet
        print('This script can only be called from NZBGet (11.0 or later).')
        return 1

    if not download_ok():
        # Nothing to do for a failed download
        return POSTPROCESS_NONE

    directory = os.environ.get('NZBPP_DIRECTORY', '')
    if not os.path.isdir(directory):
        # This can happen when a history item is processed again
        print(
            f'[INFO] Nothing to do: the folder {directory} does not exist.')
        return POSTPROCESS_NONE

    if reset_dates(os.path.normpath(directory)):
        return POSTPROCESS_ERROR

    return POSTPROCESS_SUCCESS


if __name__ == '__main__':
    sys.exit(main())
