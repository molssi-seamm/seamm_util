#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update encrypted deploy password in Travis config file."""


from __future__ import print_function
import base64
import json
import os
from getpass imp