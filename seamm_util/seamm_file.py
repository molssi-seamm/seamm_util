# -*- coding: utf-8 -*-

"""A class for wrapping output from the MolSSI Framework and plugins.
Initially it is a thin wrapper around a dictionary to store the output,
using JSON to serialize and deserialize the data.

It presents the dict api with the addition of methods to serialize and
deserialize the contents.
"""

import bz2
import gzip
import logging
import os.path

logger = logging.getLogger(__name__)


class File:
    def __init__(
        self,
        filename,
        mode,
        compression=None,
        organization="MolSSI",
        filetype=None,
        version=None,
    ):
        self.filename = filename
        self.mode = mode

        # Depending on the mode, may require filetype and version
        if self.mode == "w":
            if filetype is None:
                raise ValueError("Filetype must be given for writable files!")
            if version is None:
                raise ValueError("Version must be given for writable files!")
        elif self.mode == "a":
            if os.path.isfile(self.filename):
                # Get the header and decipher
                fd = self.__enter__()
                try:
                    line = next(fd)
                except:  # noqa: E722
                    raise RuntimeError("problem reading header line!")

                fd.close()

                # if line[0] == '!' and len(line.split()) == 3:
                #     organization, filetype, version = line[1:].split()
            else:
                logger.warning(
                    "reading '{}', expected a header line but got\n\t'{}'".format(
                        self.filename, line
                    )
                )

                if filetype is None:
                    raise ValueError("Filetype must be given to create a file!")
                if version is None:
                    raise ValueError("Version must be given to create file!")

        # Determine the type of the file
        if compression is not None:
            if compression not in ("text", "bz2", "gzip"):
                raise ValueError("Invalid compression: '{}'".format(compression))
        else:
            extension = os.path.splitext(self.filename)[1].strip().lower()
            if extension == ".bz2":
                compression = "bzip2"
            elif extension == ".gz":
                compression = "gzip"
            else:
                compression = "text"
        self.compression = compression

    def __enter__(self):
        if self.compression == "bzip2":
            self.file_descriptor = bz2.open(self.filename, self.mode + "t")
        elif self.compression == "gzip":
            self.file_descriptor = gzip.open(self.filename, self.mode + "t")
        else:
            self.file_descriptor = open(self.filename, self.mode)

        return self.file_descriptor

    def __exit__(self, *args):
        self.file_descriptor.close()

    def read_header(self):
        if self.compression == "bzip2":
            with bz2.open(self.filename, "rt") as fd:
                line = next(fd)
        elif self.compression == "gzip":
            with gzip.open(self.filename, "rt") as fd:
                line = next(fd)
        else:
            with open(self.filename, "r"):
                line = next(fd)

        if line[0] == "!" and len(line.split()) == 3:
            organization, filetype, version = line[1:].split()
            logger.info(
                "reading '{}', a {} file from {}, version {}".format(
                    self.filename, filetype, organization, version
                )
            )
        else:
            raise RuntimeError(
                "reading '{}', expected a header line but got\n\t'{}'".format(
                    self.filename, line
                )
            )
