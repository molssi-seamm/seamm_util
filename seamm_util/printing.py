"""
The Printer class provides control over printing output, based
on the Python logging module. The levels a translated to more reasonable
names for output, rather than debugging:

        Level        Logger Level    Numeric value
        --------     ------------    -------------
        JOB          CRITICAL	           50
        IMPORTANT    ERROR	           40
        TERSE        WARNING	           30
        NORMAL       INFO                  20
        VERBOSE      DEBUG                 10
        ALL          ALL                    0

By default, JOB level output is mirrored in the main log for the job
as well as the local log for the stage. All output from the cutoff level
up, which is NORMAL by default, is placed in the local stage log. Optionally,
output from a cutoff level and up is also written to the standard output.
"""

import inspect
import logging
import os
import sys
import textwrap

try:
    import thread
    import threading
except ImportError:
    thread = None

# ---------------------------------------------------------------------------
#   Level related stuff
# ---------------------------------------------------------------------------
#
# Default levels and level names, these can be replaced with any positive set
# of values having corresponding names. There is a pseudo-level, ALL, which
# is only really there as a lower limit for user-defined levels. Handlers and
# loggers are initialized with ALL so that they will log all messages, even
# at user-defined levels.
#

JOB = 50
IMPORTANT = 40
TERSE = 30
NORMAL = 20
VERBOSE = 10
ALL = 0

_levelNames = {
    JOB: "JOB",
    IMPORTANT: "IMPORTANT",
    TERSE: "TERSE",
    NORMAL: "NORMAL",
    VERBOSE: "VERBOSE",
    ALL: "ALL",
    "JOB": JOB,
    "IMPORTANT": IMPORTANT,
    "TERSE": TERSE,
    "NORMAL": NORMAL,
    "VERBOSE": VERBOSE,
    "ALL": ALL,
}


def getLevelName(lvl):
    """
    Return the textual representation of printing level 'lvl'. If the level is
    one of the predefined levels (JOB, IMPORTANT, TERSE, NORMAL, VERBOSE) then
    you get the corresponding string. If you have associated levels with names
    using addLevelName then the name you have associated with 'lvl' is
    returned. Otherwise, the string "Level %s" % lvl is returned.
    """
    return _levelNames.get(lvl, "Level {}".format(lvl))


def addLevelName(lvl, levelName):
    """
    Associate 'levelName' with 'lvl'. This is used when converting levels
    to text during message formatting.
    """
    _acquireLock()
    try:  # unlikely to cause an exception, but you never know...
        _levelNames[lvl] = levelName
        _levelNames[levelName] = lvl
    finally:
        _releaseLock()


# ---------------------------------------------------------------------------
#   Thread-related stuff
# ---------------------------------------------------------------------------

#
# _lock is used to serialize access to shared data structures in this module.
# This needs to be an RLock because fileConfig() creates Handlers and so
# might arbitrary user threads. Since Handler.__init__() updates the shared
# dictionary _handlers, it needs to acquire the lock. But if configuring,
# the lock would already have been acquired - so we need an RLock.
# The same argument applies to Loggers and Manager.loggerDict.
#

_lock = None


def _acquireLock():
    """
    Acquire the module-level lock for serializing access to shared data.
    This should be released with _releaseLock().
    """
    global _lock
    if (not _lock) and thread:
        _lock = threading.RLock()
    if _lock:
        _lock.acquire()


def _releaseLock():
    """
    Release the module-level lock acquired by calling _acquireLock().
    """
    if _lock:
        _lock.release()


# ---------------------------------------------------------------------------
#   Manager classes and functions
# ---------------------------------------------------------------------------


class PlaceHolder(object):
    """
    PlaceHolder instances are used in the Manager printer hierarchy to take
    the place of nodes for which no printers have been defined [FIXME add
    example].
    """

    def __init__(self, aprinter):
        """
        Initialize with the specified printer being a child of this
        placeholder.
        """
        self.printers = [aprinter]

    def append(self, aprinter):
        """
        Add the specified printer as a child of this placeholder.
        """
        if aprinter not in self.printers:
            self.printers.append(aprinter)


#
#   Determine which class to use when instantiating printers.
#
_printerClass = None


def setPrinterClass(klass):
    """
    Set the class to be used when instantiating a printer. The class should
    define __init__() such that only a name argument is required, and the
    __init__() should call Printer.__init__()
    """
    if klass != Printer:
        if not isinstance(klass, object):
            raise TypeError("setPrinterClass is expecting a class")
        if not issubclass(klass, Printer):
            raise TypeError(
                "printer not derived from printer.Printer: " + klass.__name__
            )
    global _printerClass
    _printerClass = klass


class Manager(object):
    """
    There is [under normal circumstances] just one Manager instance, which
    holds the hierarchy of printers.
    """

    def __init__(self, print_root):
        """
        Initialize the manager with the root node of the printer hierarchy.
        """
        self.print_root = print_root
        self.disable = 0
        self.emittedNoHandlerWarning = 0
        self.printerDict = {}

    def getPrinter(self, name):
        """
        Get a printer with the specified name (channel name), creating it
        if it doesn't yet exist. If a PlaceHolder existed for the specified
        name [i.e. the printer didn't exist but a child of it did], replace
        it with the created printer and fix up the parent/child references
        which pointed to the placeholder to now point to the printer.
        """
        rv = None
        _acquireLock()
        try:
            if name in self.printerDict:
                rv = self.printerDict[name]
                if isinstance(rv, PlaceHolder):
                    ph = rv
                    rv = _printerClass(name)
                    rv.manager = self
                    self.printerDict[name] = rv
                    self._fixupChildren(ph, rv)
                    self._fixupParents(rv)
            else:
                rv = _printerClass(name)
                rv.manager = self
                self.printerDict[name] = rv
                self._fixupParents(rv)
        finally:
            _releaseLock()
        return rv

    def _fixupParents(self, aprinter):
        """
        Ensure that there are either printers or placeholders all the way
        from the specified printer to the root of the printer hierarchy.
        """
        name = aprinter.name
        i = name.rfind(".")
        rv = None
        while (i > 0) and not rv:
            substr = name[:i]
            if substr not in self.printerDict:
                self.printerDict[substr] = PlaceHolder(aprinter)
            else:
                obj = self.printerDict[substr]
                if isinstance(obj, Printer):
                    rv = obj
                else:
                    assert isinstance(obj, PlaceHolder)
                    obj.append(aprinter)
            i = name.rfind(".", 0, i - 1)
        if not rv:
            rv = self.print_root
        aprinter.parent = rv

    def _fixupChildren(self, ph, aprinter):
        """
        Ensure that children of the placeholder ph are connected to the
        specified printer.
        """
        for c in ph.printers:
            if aprinter.name in c.parent.name:
                aprinter.parent = c.parent
                c.parent = aprinter


class Printer(logging.Filterer):
    """Provide controlled printing for plugins for the MolSSI
    Framework.
    """

    def __init__(self, name, level=ALL):
        """Create the Printer object"""

        super().__init__()

        if name == "print_root":
            self.logger = logging.getLogger(name)
        else:
            self.logger = logging.getLogger("print_root." + name)
        self.logger.setLevel(level)

    @property
    def name(self):
        return self.logger.name

    @name.setter
    def name(self, value):
        self.logger.name = value

    @property
    def level(self):
        return self.logger.level

    @property
    def parent(self):
        return self.logger.parent

    @parent.setter
    def parent(self, value):
        self.logger.parent = value

    @property
    def propagate(self):
        return self.logger.propagate

    @propagate.setter
    def propagate(self, value):
        self.logger.propagate = value

    @property
    def handlers(self):
        return self.logger.handlers

    @property
    def disabled(self):
        return self.logger.disabled

    @disabled.setter
    def disabled(self, value):
        self.logger.disabled = value

    def setLevel(self, lvl):
        """
        Set the printing level of this printer.
        """
        self.logger.level = lvl

    def verbose(self, msg, *args, **kwargs):
        """Logs a message with level VERBOSE on this printer.
        The msg is the message format string, and the args are the arguments
        which are merged into msg using the string formatting
        operator. (Note that this means that you can use keywords in the
        format string, together with a single dictionary argument.)
        """
        self.print(10, msg, *args, **kwargs)

    def normal(self, msg, *args, **kwargs):
        """Logs a message with level NORMAL on this printer.
        The msg is the message format string, and the args are the arguments
        which are merged into msg using the string formatting
        operator. (Note that this means that you can use keywords in the
        format string, together with a single dictionary argument.)
        """
        self.print(20, msg, *args, **kwargs)

    def terse(self, msg, *args, **kwargs):
        """Logs a message with level TERSE on this printer.
        The msg is the message format string, and the args are the arguments
        which are merged into msg using the string formatting
        operator. (Note that this means that you can use keywords in the
        format string, together with a single dictionary argument.)
        """
        self.print(30, msg, *args, **kwargs)

    def important(self, msg, *args, **kwargs):
        """Logs a message with level IMPORTANT on this printer.
        The msg is the message format string, and the args are the arguments
        which are merged into msg using the string formatting
        operator. (Note that this means that you can use keywords in the
        format string, together with a single dictionary argument.)
        """
        self.print(40, msg, *args, **kwargs)

    def job(self, msg, *args, **kwargs):
        """Logs a message with level JOB on this printer.
        The msg is the message format string, and the args are the arguments
        which are merged into msg using the string formatting
        operator. (Note that this means that you can use keywords in the
        format string, together with a single dictionary argument.)
        """
        self.print(50, msg, *args, **kwargs)

    def print(self, lvl, msg, *args, **kwargs):
        """Prints a message with integer level lvl on this logger.
        The other arguments are interpreted as for verbose().
        """
        # print('print: lvl={}, msg={}, args={}, kwargs={}'.format(
        #     lvl, msg, args, kwargs
        # ))
        self.logger.log(lvl, msg, *args, **kwargs)

    def findCaller(self):
        """
        Find the stack frame of the caller so that we can note the source
        file name and line number.
        """
        rv = (None, None)
        frame = inspect.currentframe().f_back
        while frame:
            sfn = inspect.getsourcefile(frame)
            if sfn:
                sfn = os.path.normcase(sfn)
            if sfn != _srcfile:  # noqa: F821
                # print frame.f_code.co_code
                lineno = inspect.getlineno(frame)
                rv = (sfn, lineno)
                break
            frame = frame.f_back
        return rv

    def makeRecord(self, name, lvl, fn, lno, msg, args, exc_info):
        """
        A factory method which can be overridden in subclasses to create
        specialized LogRecords.
        """
        return self.logger.makeRecord(name, lvl, fn, lno, msg, args, exc_info)

    def _log(self, lvl, msg, args, exc_info=None):
        """
        Low-level logging routine which creates a LogRecord and then calls
        all the handlers of this logger to handle the record.
        """
        self.logger._log(self, lvl, msg, args, exc_info)

    def handle(self, record):
        """
        Call the handlers for the specified record. This method is used for
        unpickled records received from a socket, as well as those created
        locally. Logger-level filtering is applied.
        """
        self.logger.handle(record)

    def addHandler(self, hdlr):
        """
        Add the specified handler to this printer.
        """
        self.logger.addHandler(hdlr)

    def removeHandler(self, hdlr):
        """
        Remove the specified handler from this printer.
        """
        self.logger.removeHandler(hdlr)

    def callHandlers(self, record):
        """
        Loop through all handlers for this printer and its parents in the
        printer hierarchy. If no handler was found, output a one-off error
        message to sys.stderr. Stop searching up the hierarchy whenever a
        printer with the "propagate" attribute set to zero is found - that
        will be the last printer whose handlers are called.
        """
        self.logger.callHandlers(record)

    def getEffectiveLevel(self):
        """
        Loop through this printer and its parents in the printer hierarchy,
        looking for a non-zero logging level. Return the first one found.
        """
        return self.logger.getEffectiveLevel()

    def isEnabledFor(self, lvl):
        """
        Is this printer enabled for level lvl?
        """
        return self.logger.isEnabledFor(lvl)


class RootPrinter(Printer):
    """
    A root printer is not that different to any other printer, except that
    it must have a printing level and there is only one instance of it in
    the hierarchy.
    """

    def __init__(self, lvl):
        """
        Initialize the printer with the name "print_root".
        """
        super().__init__("print_root", lvl)

        # Turn of propagation and set up handler
        # so that we are separate from the loggers
        self.logger.propagate = False


_printerClass = Printer

print_root = RootPrinter(NORMAL)
Printer.print_root = print_root
Printer.manager = Manager(Printer.print_root)

# ---------------------------------------------------------------------------
# Configuration classes and functions
# ---------------------------------------------------------------------------

BASIC_FORMAT = "{message:s}"


def basicConfig():
    """
    Do basic configuration for the printing system by creating a
    StreamHandler with a default Formatter and adding it to the
    root logger.
    """
    if len(print_root.handlers) == 0:
        hdlr = logging.StreamHandler()
        fmt = logging.Formatter(BASIC_FORMAT, style="{")
        hdlr.setFormatter(fmt)
        print_root.addHandler(hdlr)


_handlers = {}  # repository of handlers (for flushing when shutdown called)


def fileConfig(fname):
    """
    Read the printing configuration from a ConfigParser-format file. This can
    be called several times from an application, allowing an end user the
    ability to select from various pre-canned configurations (if the
    developer provides a mechanism to present the choices and load the chosen
    configuration).
    In versions of ConfigParser which have the readfp method [typically
    shipped in 2.x versions of Python], you can pass in a file-like object
    rather than a filename, in which case the file-like object will be read
    using readfp.
    """
    import ConfigParser

    cp = ConfigParser.ConfigParser()
    if hasattr(cp, "readfp") and hasattr(fname, "read"):
        cp.readfp(fname)
    else:
        cp.read(fname)
    # first, do the formatters...
    flist = cp.get("formatters", "keys")
    if len(flist):
        flist = flist.split(",")
        formatters = {}
        for form in flist:
            sectname = "formatter_%s" % form
            opts = cp.options(sectname)
            if "format" in opts:
                fs = cp.get(sectname, "format", 1)
            else:
                fs = None
            if "datefmt" in opts:
                dfs = cp.get(sectname, "datefmt", 1)
            else:
                dfs = None
            f = logging.Formatter(fs, dfs)
            formatters[form] = f
    # next, do the handlers...
    # critical section...
    _acquireLock()
    try:
        try:
            # first, lose the existing handlers...
            _handlers.clear()
            # now set up the new ones...
            hlist = cp.get("handlers", "keys")
            if len(hlist):
                hlist = hlist.split(",")
                handlers = {}
                fixups = []  # for inter-handler references
                for hand in hlist:
                    sectname = "handler_%s" % hand
                    klass = cp.get(sectname, "class")
                    opts = cp.options(sectname)
                    if "formatter" in opts:
                        fmt = cp.get(sectname, "formatter")
                    else:
                        fmt = ""
                    klass = eval(klass)
                    args = cp.get(sectname, "args")
                    args = eval(args)
                    h = klass(args)
                    if "level" in opts:
                        lvl = cp.get(sectname, "level")
                        h.setLevel(_levelNames[lvl])
                    if len(fmt):
                        h.setFormatter(formatters[fmt])
                    # temporary hack for FileHandler and MemoryHandler.
                    if klass == logging.FileHandler:
                        maxsize = 0
                        if "maxsize" in opts:
                            ms = cp.getint(sectname, "maxsize")
                            if ms > 0:
                                maxsize = ms
                        if maxsize:
                            backcount = 0
                            if "backcount" in opts:
                                bc = cp.getint(sectname, "backcount")
                                if bc > 0:
                                    backcount = bc
                            h.setRollover(maxsize, backcount)
                    elif klass == logging.MemoryHandler:
                        if "target" in opts:
                            target = cp.get(sectname, "target")
                        else:
                            target = ""
                        if len(target):  # the target handler may not be loaded yet,
                            # so keep for later...
                            fixups.append((h, target))
                    handlers[hand] = h
                # now all handlers are loaded, fixup inter-handler references..
                for fixup in fixups:
                    h = fixup[0]
                    t = fixup[1]
                    h.setTarget(handlers[t])
            # at last, the loggers...first the root...
            llist = cp.get("loggers", "keys")
            llist = llist.split(",")
            llist.remove("root")
            sectname = "printer_root"
            log = print_root
            opts = cp.options(sectname)
            if "level" in opts:
                lvl = cp.get(sectname, "level")
                log.setLevel(_levelNames[lvl])
            for h in print_root.handlers:
                print_root.removeHandler(h)
            hlist = cp.get(sectname, "handlers")
            if len(hlist):
                hlist = hlist.split(",")
                for hand in hlist:
                    log.addHandler(handlers[hand])
            # and now the others...
            # we don't want to lose the existing loggers,
            # since other threads may have pointers to them.
            # existing is set to contain all existing loggers,
            # and as we go through the new configuration we
            # remove any which are configured. At the end,
            # what's left in existing is the set of loggers
            # which were in the previous configuration but
            # which are not in the new configuration.

            existing = print_root.manager.printDict.keys()

            # now set up the new ones...
            for log in llist:
                sectname = "printer_%s" % log
                qn = cp.get(sectname, "qualname")
                opts = cp.options(sectname)
                if "propagate" in opts:
                    propagate = cp.getint(sectname, "propagate")
                else:
                    propagate = 1
                printer = getPrinter(qn)
                if qn in existing:
                    existing.remove(qn)
                if "level" in opts:
                    lvl = cp.get(sectname, "level")
                    printer.setLevel(_levelNames[lvl])
                for h in printer.handlers:
                    printer.removeHandler(h)
                printer.propagate = propagate
                printer.disabled = 0
                hlist = cp.get(sectname, "handlers")
                if len(hlist):
                    hlist = hlist.split(",")
                    for hand in hlist:
                        printer.addHandler(handlers[hand])
            # Disable any old loggers. There's no point deleting
            # them as other threads may continue to hold references
            # and by disabling them, you stop them doing any printing.

            for log in existing:
                print_root.manager.printerDict[log].disabled = 1
        except Exception:  # noqa: E722
            import traceback

            ei = sys.exc_info()
            traceback.print_exception(ei[0], ei[1], ei[2], None, sys.stderr)
            del ei
    finally:
        _releaseLock()


# ---------------------------------------------------------------------------
# Utility functions at module level.
# Basically delegate everything to the root printer.
# ---------------------------------------------------------------------------


def getPrinter(name=None):
    """
    Return a printer with the specified name, creating it if necessary.
    If no name is specified, return the root printer.
    """
    if name:
        return Printer.manager.getPrinter(name)
    else:
        return print_root


def job(msg, *args, **kwargs):
    """
    Log a message with severity 'JOB' on the root printer.
    """
    if len(print_root.handlers) == 0:
        basicConfig()
    print_root.job(msg, args, kwargs)


def important(msg, *args, **kwargs):
    """
    Log a message with severity 'IMPORTANT' on the root printer.
    """
    if len(print_root.handlers) == 0:
        basicConfig()
    print_root.important(msg, args, kwargs)


def terse(msg, *args, **kwargs):
    """
    Log a message with severity 'TERSE' on the root printer.
    """
    if len(print_root.handlers) == 0:
        basicConfig()
    print_root.terse(msg, args, kwargs)


def normal(msg, *args, **kwargs):
    """
    Log a message with severity 'NORMAL' on the root printer.
    """
    if len(print_root.handlers) == 0:
        basicConfig()
    print_root.normal(msg, args, kwargs)


def verbose(msg, *args, **kwargs):
    """
    Log a message with severity 'VERBOSE' on the root printer.
    """
    if len(print_root.handlers) == 0:
        basicConfig()
    print_root.verbose(msg, args, kwargs)


def disable(level):
    """
    Disable all printing calls less severe than 'level'.
    """
    print_root.manager.disable = level


def shutdown():
    """
    Perform any cleanup actions in the printing system (e.g. flushing
    buffers). Should be called at application exit.
    """
    for h in _handlers.keys():
        h.flush()
        h.close()


#
# Did not bring the socket listener code over yet
#
#


class FormattedText(object):
    """
    Class for wrapping, formatting and indenting text to make textual output
    from the MolSSI Framework and its plugins easier

    The __str__ method returns the formatted text, so e.g. print(<object>)
    formats the text and prints it as expected.

    Example:
    -----------------------------------------------------------------------
        ft = FormattedText('''\
        This is the first line.
        And the second.
        And a very, very, very, very, very, very, very, very, very, very, very, very long line.
        And i = '{i}' and j = '{j}' followed by a line break

        Ending with the last line. Which can of course also be wrapped
        if we want it to be.

            What about a list:     1

            With a second item:    2

        Does that work?''', i=1, j=2, indent='--->', line_length=70)

        print(ft)
    -----------------------------------------------------------------------
    Will print the following:

        --->This is the first line. And the second. And a very, very, very,
        --->very, very, very, very, very, very, very, very, very long line.
        --->And i = '1' and j = '2' followed by a line break

        --->Ending with the last line. Which can of course also be wrapped if
        --->we want it to be.

        --->    What about a list:     1

        --->    With a second item:    2

        --->Does that work?

    where the start of each arrow is aligned to the left (not indented as in
    this string).
    """  # noqa: E501

    def __init__(
        self,
        text,
        dedent=True,
        indent="",
        indent_initial=True,
        indent_all=False,
        wrap=True,
        line_length=80,
        *args,
        **kwargs
    ):
        """
        Handle the text <text>, which usually from either a simple string
        or a triple-quoted string.

        The <dedent> option uses textwrap.dedent to remove consistent initial
        spaces so that the string can be nicely lined up in the source code.

        <indent> provides an optional string to prefix each line of output

        <indent_all> indicates that empty line of those containing only white
        space also be indented. By the default the are not.

        <indent_initial> indicates that the first line shoud be indented.
        defaults to True.

        <wrap> asks that lines of text not starting with a blank be wrapped
        at <line_length>.

        <*args> and <**kwargs> are additional arguments for {}-type formatting
        in the text. This is done after dedenting but before wrapping the text.

        Empty lines separate 'paragraphs'. Each paragraph is wrapped by itself,
        which is the behavior that most people expect.

        Since lines starting with blanks (after dedent'ing) are not wrapped,
        this can be used for e.g. tables and lists.
        """

        self.text = text
        self.args = args
        self.kwargs = kwargs
        self.dedent = dedent
        self.indent = indent
        self.indent_initial = indent_initial
        self.indent_all = indent_all
        self.wrap = wrap
        self.line_length = line_length

    def __str__(self):
        """Turn into a formatted, wrapped string as requested.

        NB. If there are no extra args or kwargs, don't format the
        string. This avoids problems with strings that have, e.g.
        braces internally.
        """
        if self.dedent:
            if len(self.args) == 0 and len(self.kwargs) == 0:
                text = textwrap.dedent(self.text)
            else:
                text = textwrap.dedent(self.text.format(*self.args, **self.kwargs))
        else:
            if len(self.args) == 0 and len(self.kwargs) == 0:
                text = self.text
            else:
                text = self.text.format(*self.args, **self.kwargs)

        if self.wrap:
            wrapped_text = ""
            buffer = []
            if not self.indent_initial:
                initial_indent = ""
            else:
                initial_indent = self.indent
            for line in text.splitlines():
                if line.strip() == "" or line[0] == " ":
                    if len(buffer) > 0:
                        wrapped_text += textwrap.fill(
                            "\n".join(buffer),
                            self.line_length,
                            initial_indent=initial_indent,
                            subsequent_indent=self.indent,
                        )
                        wrapped_text += "\n"
                        buffer = []
                    if line.strip() == "":
                        if self.indent_all:
                            wrapped_text += self.indent + "\n"
                        else:
                            wrapped_text += "\n"
                elif line.strip() != "" and line[0] != " ":
                    buffer.append(line)
                if line.strip() != "" and line[0] == " ":
                    wrapped_text += self.indent + line + "\n"
            if len(buffer) > 0:
                wrapped_text += textwrap.fill(
                    "\n".join(buffer),
                    self.line_length,
                    initial_indent=initial_indent,
                    subsequent_indent=self.indent,
                )

            return wrapped_text
        else:
            if self.indent_all:
                return textwrap.indent(text, self.indent, lambda line: True)
            else:
                return textwrap.indent(text, self.indent)


if __name__ == "__main__":
    print(__doc__)
