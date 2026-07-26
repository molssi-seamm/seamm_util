#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_util.zenodo`, against the real, live SEAMM package-list
record on Zenodo (the same public record `seamm_installer.util.find_packages`
depends on) -- there is no mock/sandbox layer for this in the codebase, and
the whole point of `get_latest_public_record` is to verify it against the
actual public-records API response shape.
"""

from seamm_util import Zenodo

# The SEAMM_packages.json record. Passing the (older, non-"concept")
# version id on purpose, to confirm Zenodo resolves either id in the same
# family to the latest version -- see get_latest_public_record's docstring.
SEAMM_PACKAGES_RECORD_ID = 7789854


def test_get_latest_public_record_resolves_to_latest():
    zenodo = Zenodo()
    record = zenodo.get_latest_public_record(SEAMM_PACKAGES_RECORD_ID)

    assert "SEAMM_packages.json" in record.files()


def test_get_latest_public_record_accepts_concept_id_too():
    # 7789853 is the conceptrecid for the same record family as 7789854.
    zenodo = Zenodo()
    a = zenodo.get_latest_public_record(SEAMM_PACKAGES_RECORD_ID)
    b = zenodo.get_latest_public_record(7789853)

    assert a["id"] == b["id"]


def test_get_file_on_public_record():
    zenodo = Zenodo()
    record = zenodo.get_latest_public_record(SEAMM_PACKAGES_RECORD_ID)

    text = record.get_file("SEAMM_packages.json")

    assert len(text) > 0
    assert "packages" in text


def test_download_file_on_public_record(tmp_path):
    zenodo = Zenodo()
    record = zenodo.get_latest_public_record(SEAMM_PACKAGES_RECORD_ID)

    out_path = record.download_file("SEAMM_packages.json", tmp_path)

    assert out_path.exists()
    assert out_path.read_text() == record.get_file("SEAMM_packages.json")


def test_files_lists_public_record_filenames():
    zenodo = Zenodo()
    record = zenodo.get_latest_public_record(SEAMM_PACKAGES_RECORD_ID)

    files = record.files()

    assert isinstance(files, list)
    assert "SEAMM_packages.json" in files
