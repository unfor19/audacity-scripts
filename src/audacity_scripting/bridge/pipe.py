import json
import os
import sys
from time import sleep
from ..utils.logger import logger


def send_command(TOFILE, EOL, command):
    """Send a single command."""
    full_command = command + EOL
    logger.debug(f"Send: >>> '{full_command}'")
    TOFILE.write(full_command)
    TOFILE.flush()
    TOFILE.close()


def get_response(FROMFILE, EOL):
    """Return the command response."""
    result = ''
    line = ''
    while True:
        result += line
        line = FROMFILE.readline()
        if line == '\n' and len(result) > 0:
            break
    logger.debug(f"Result: {result}")
    FROMFILE.close()
    return result


def do_command(command, retry_max_count=20, sleep_seconds=0.05):
    TONAME = ''
    FROMNAME = ''
    EOL = ''
    """Send one command, and return the response."""
    # Based on the official pipe_test.py - https://github.com/audacity/audacity/blob/master/scripts/piped-work/pipe_test.py
    if sys.platform == 'win32':
        logger.debug("pipe-test.py, running on windows")
        TONAME = '\\\\.\\pipe\\ToSrvPipe'
        FROMNAME = '\\\\.\\pipe\\FromSrvPipe'
        EOL = '\r\n\0'
    else:
        logger.debug("pipe-test.py, running on linux or mac")
        TONAME = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
        FROMNAME = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
        EOL = '\n'
    retry_count = 0
    while retry_count < retry_max_count:
        logger.debug(
            f'EOL:{json.dumps(EOL)}, TONAME:{TONAME}, FROMNAME:{FROMNAME}')
        if not os.path.exists(TONAME):
            logger.debug(
                f"'{TONAME}' does not exist.  Ensure Audacity is running with mod-script-pipe.")
            if retry_count == retry_max_count:
                sys.exit()

        logger.debug("Read from \"" + FROMNAME + "\"")
        if not os.path.exists(FROMNAME):
            logger.debug(
                f"'{FROMNAME}' does not exist. Ensure Audacity is running with mod-script-pipe.")
            if retry_count == retry_max_count:
                sys.exit()
        logger.debug("-- Both pipes exist.  Good.")

        retry_count += 1
        sleep(sleep_seconds)

    TOFILE = open(TONAME, 'w')
    logger.debug("-- File to write to has been opened")
    FROMFILE = open(FROMNAME, 'r')
    logger.debug("-- File to read from has now been opened too\r\n")
    send_command(TOFILE, EOL, command)
    response = get_response(FROMFILE, EOL=EOL)
    return response
