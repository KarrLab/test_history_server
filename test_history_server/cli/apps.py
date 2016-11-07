""" CLI app configuration
:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2016-11-06
:Copyright: 2016, Karr Lab
:License: MIT
"""

from __future__ import unicode_literals

from django.apps import AppConfig


class CliConfig(AppConfig):
    name = 'CLI'
    verbose_name = 'CLI'
