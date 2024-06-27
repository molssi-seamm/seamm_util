# -*- coding: utf-8 -*-

"""Context manager for extending file reading to handle include's"""

import bz2
import collections
import gzip
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# logger.setLevel(logging.DEBUG)


def default_uri_handler(path):
    """Do nothing! Just return the path"""
    return Path(path)


def splitext(path):
    """
    Get the extension of a file, ignoring .gz or .bz2 on the end

    Parameters
    ----------
    path : str or pathlib.Path
     The name or path of the file
    """
    if not isinstance(path, Path):
        path = Path(path)

    ext = path.suffix
    if ext in (".gz", ".bz2"):
        ext = path.with_suffix("").suffix
    return ext


class Open(object):
    def __init__(
        self,
        path,
        mode="r",
        logger=logger,
        include="#include",
        history=10,
        uri_handler=None,
    ):
        """Open a file, automatically handling 'include'

        Parameters
        ----------
        path : str or pathlib.Path
            The path to the file
        mode : str (optional)
            The mode to open the file. Defaults to read-only.
        logger : logging.Logger (optional)
            The logging object to use
        include : str (optional)
            The keyword that triggers an include. Defaults to "#include"
        history : int (optional)
            Length of history to keep
        uri_handler : function (optional)
            A method to handle any URIs, like 'local:'. Defaults to None.
        """
        if not isinstance(path, Path):
            path = Path(path)
        self.mode = mode
        self.logger = logger
        self.include = include
        self._history = history
        self._depth = -1
        if uri_handler is None:
            self._uri_handler = default_uri_handler
        else:
            self._uri_handler = uri_handler

        self._deque = collections.deque(maxlen=history)

        self._total_lines = 0
        self._linenos = []
        self._files = []
        self._paths = [self._uri_handler(path).expanduser().resolve()]
        self._visited = [("", self.path)]
        self._fds = []
        self._cwd = Path.cwd()

    def __enter__(self):
        """Handle the enter event for the context manager by opening the file"""
        self.logger.debug("in __enter__")
        self._linenos.append(0)
        self._fds.append(self._open(self.path))

        self.logger.debug(f"   opened {self.path}")
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
        if self.include is not None and len(words) > 0 and words[0] == self.include:
            if len(words) > 2:
                filename, tmp = words[1:3]
                missing_ok = tmp.lower() == "missing_ok"
            else:
                filename = words[1]
                missing_ok = False
            self.logger.debug("   opening include file {}".format(filename))
            self._linenos.append(0)
            try:
                path = self.path.parent / self._uri_handler(filename)
            except FileNotFoundError:
                self.logger.debug("   URI handler did not find the file")
                if not missing_ok:
                    raise
            else:
                # only use a file once
                if path not in self.visited:
                    # Check that the file exists in case the URI handler doesn't
                    if path.exists():
                        self._paths.append(path.expanduser().resolve())
                        self._fds.append(self._open(self.path))
                        self.logger.debug("   opened it")
                        self.visited.append((filename, path))
                    elif missing_ok:
                        pass
                    else:
                        raise FileNotFoundError(str(path))
            line = self.__next__()
        self.logger.log(0, line)

        self._deque.appendleft(line)
        return line

    def __iter__(self):
        """Need to be an iterator"""
        return self

    def __getattr__(self, attr):
        """Pass any attribute requests to the actual file handle"""
        self.logger.debug("attr = '{}'".format(attr))
        return getattr(self._fds[-1], attr)

    @property
    def depth(self):
        """The depth of the current line stack"""
        return self._depth

    @property
    def path(self):
        """The path of the current working file"""
        if len(self.paths) > 0:
            return self.paths[-1]
        else:
            return None

    @property
    def paths(self):
        """The paths of all the opened files."""
        return self._paths

    @property
    def lineno(self):
        """THe line number in the current file."""
        if len(self._linenos) > 0:
            return self._linenos[-1]
        else:
            return 0

    @property
    def total_lines(self):
        return self._total_lines

    @property
    def visited(self):
        """The set of files used"""
        return self._visited

    def push(self, n=1):
        """Push the n last lines back onto the device (virtually)"""
        if self._depth + n > len(self._deque):
            raise RuntimeError("Exceeded the currently available history")
        self._depth += n

    def stack(self):
        """Provide the traceback of the included files"""
        result = []
        for path, lineno in zip(reversed(self.paths), reversed(self._linenos)):
            result.append(f"{path}:{lineno}")
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
            # Get the next line from the current file
            line = self._fds[-1].__next__()
        except StopIteration:
            # Hit EOF, so go back to previous file, if any
            fd = self._fds.pop()
            self._close(fd)
            self.paths.pop()
            n = self._linenos.pop()
            self.logger.info("   read {} lines from fd".format(n))
            if len(self._fds) <= 0:
                # At the end of the first file, so all done
                raise StopIteration()
            # and get the next line from the previous file
            return self._next()

        self._linenos[-1] += 1
        self._total_lines += 1

        return line

    def _open(self, path):
        """Open 'filename' using gzip or bzip if needed

        Parameters
        ----------
        path : pathlib.Path
            The path to the file
        """
        if not isinstance(path, Path):
            raise RuntimeError("path must be a pathlib.Path")
        ext = path.suffix
        if ext == ".bz2":
            fd = bz2.open(path, self.mode + "t")
        elif ext == ".gz":
            fd = gzip.open(path, self.mode + "t")
        else:
            fd = open(path, self.mode)
        return fd
