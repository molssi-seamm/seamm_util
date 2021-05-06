# -*- coding: utf-8 -*-

"""Context manager for extending file reading to handle include's"""

import bz2
import collections
import gzip
import logging
import os
import os.path

module_logger = logging.getLogger(__name__)


def splitext(filename):
    """
    Get the extension of a file, ignoring .gz or .bz2 on the end

    Args:
        filename ('str'): the name, including any path, of the file
    """
    name, ext = os.path.splitext(filename)
    if ext in (".gz", ".bz2"):
        name, ext = os.path.splitext(name)
    return ext


class Open(object):
    def __init__(self, filename, mode="r", logger=None, include=None, history=10):
        """Open a file, automatically handling 'include'

        Args:
            filename ('str'): The path to the file
            mode ('str', optional): The mode to open the file. Defaults to
                read-only.
            logger (obj, optional): The logging object to use
            include ('str', optional): The keyword that triggers an include
            history (integer, optional): Length of history to keep
        """
        if not isinstance(filename, str):
            raise RuntimeError("Filename must be a string path")
        self._filename = filename
        self.mode = mode
        if logger:
            self.logger = logger
        else:
            self.logger = module_logger
        self.include = include
        self._history = history
        self._depth = -1

        self._deque = collections.deque(maxlen=history)

        self._total_lines = 0
        self._linenos = []
        self._files = []
        self._paths = []
        self._fds = []
        self._cwd = None

    def __enter__(self):
        """Handle the enter event for the context manager by opening the file"""
        self.logger.debug("in __enter__")
        self._cwd = os.getcwd()
        self._linenos.append(0)
        self._files.append(self._filename)
        filepath = os.path.join(self._cwd, self._filename)
        path = os.path.dirname(filepath)
        self._paths.append(path)

        self._fds.append(self._open(filepath))

        self.logger.debug("   opened {}".format(self._filename))
        return self

    def __exit__(self, *args, **kwargs):
        """Close any open files as we exit the context"""
        self.logger.debug("in __exit__")
        while len(self._fds) > 0:
            fd = self._fds.pop()
            self._close(fd, *args, **kwargs)
        self.logger.debug("   closed all files")

    def __next__(self):
        """Iterator to get the next line"""
        self.logger.log(0, "__next__")

        if self._depth >= 0:
            line = self._deque[self._depth]
            self._depth -= 1
            return line

        line = self._next()
        words = line.split()
        if self.include and len(words) > 0 and words[0] == self.include:
            filename = line.split()[1]
            self.logger.debug("   opening include file {}".format(filename))
            self._linenos.append(0)
            self._files.append(filename)
            filepath = os.path.join(self._paths[-1], filename)
            path = os.path.dirname(filepath)
            self._paths.append(path)

            self._fds.append(self._open(filepath))

            self.logger.debug("   opened it")
            line = self.__next__()
        self.logger.log(0, line)

        self._deque.appendleft(line)
        return line

    def __iter__(self):
        """Need to be an iterator"""
        self.logger.log(0, "__iter__")
        return self

    def __getattr__(self, attr):
        """Pass any attribute requests to the actual file handle"""
        self.logger.debug("attr = '{}'".format(attr))
        return getattr(self._fds[-1], attr)

    @property
    def path(self):
        if len(self._paths) > 0:
            return self._paths[-1]
        else:
            return None

    @property
    def filename(self):
        if len(self._files) > 0:
            return self._files[-1]
        else:
            return None

    @property
    def lineno(self):
        if len(self._linenos) > 0:
            return self._linenos[-1]
        else:
            return 0

    @property
    def total_lines(self):
        return self._total_lines

    @property
    def depth(self):
        return self._depth

    def push(self, n=1):
        """
        push the n last lines back onto the device (virtually)
        """
        if self._depth + n > len(self._deque):
            raise RuntimeError("Exceeded the currently available history")
        self._depth += n

    def stack(self):
        """Provide the traceback of the included files"""
        result = []
        for i in range(len(self._paths) - 1, 0, -1):
            path = self._paths[i]
            filename = self._files[i]
            filepath = os.path.join(path, filename)
            lineno = self._linenos[i]
            result.append("{}:{}".format(filepath, lineno))
        return result

    def _close(self, fd, *args, **kwargs):
        """Helper routine to close a file handle"""
        exit = getattr(fd, "__exit__", None)
        if exit is not None:
            self.logger.debug("   closing fd using its __exit__ method")
            return exit(*args, **kwargs)
        else:
            exit = getattr(fd, "close", None)
            if exit is not None:
                self.logger.debug("   closing fd using its close method")
                exit()

    def _next(self):
        """Helper routine to get the next line, handling EOF and errors"""
        try:
            line = self._fds[-1].__next__()
        except StopIteration:
            fd = self._fds.pop()
            self._close(fd)
            self._files.pop()
            self._paths.pop()
            n = self._linenos.pop()
            self.logger.info("   read {} lines from fd".format(n))
            if len(self._fds) <= 0:
                raise StopIteration()
            return self._next()
        except:  # noqa: E722
            raise
        self._linenos[-1] += 1
        self._total_lines += 1
        return line

    def _open(self, filename):
        """Open 'filename' using gzip or bzip if needed

        Args:
            filename ('str'): the name, including any path, of the file
        """
        if not isinstance(filename, str):
            raise RuntimeError("Filename must be a string to open")
        name, ext = os.path.splitext(filename.strip().lower())
        if ext == ".bz2":
            fd = bz2.open(filename, self.mode + "t")
        elif ext == ".gz":
            fd = gzip.open(filename, self.mode + "t")
        else:
            fd = open(filename, self.mode)
        return fd
