"""
Locating and launching the external command-line tools (ffmpeg, mkvmerge).

Everything that shells out to those binaries should go through here so the
PyInstaller environment fixes stay in one place.
"""

import os
import sys
import shutil

# Resolve the tools once at import time so subprocess always gets the full path
FFMPEG = shutil.which('ffmpeg') or '/usr/bin/ffmpeg'
FFPROBE = shutil.which('ffprobe') or '/usr/bin/ffprobe'
MKVMERGE = shutil.which('mkvmerge') or '/usr/bin/mkvmerge'


def subprocess_env():
    """
    Return an environment dict safe for launching external processes from a
    PyInstaller bundle.

    The bootloader points LD_LIBRARY_PATH at its temp extraction dir so the
    bundled shared libs are found.  That leaks into every subprocess — ffmpeg
    then loads the bundled libz/libstdc++/libfreetype instead of the system
    ones it was linked against and dies in the dynamic linker with exit
    code 127.

    Some bootloader versions stash the pre-launch value in LD_LIBRARY_PATH_ORIG;
    where they do, restore it.  PyInstaller 6.22 does not set it, so the common
    path is dropping the injected value entirely, which is what an unbundled
    run would have had anyway.
    """
    env = os.environ.copy()
    if hasattr(sys, '_MEIPASS'):
        lp_key = 'LD_LIBRARY_PATH'
        original = env.get(lp_key + '_ORIG')   # saved by PyInstaller bootloader
        if original is not None:
            env[lp_key] = original
        else:
            env.pop(lp_key, None)   # no original → remove the injected value
    return env
