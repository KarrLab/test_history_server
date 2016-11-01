""" Core app (models) configuration
:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2016-11-01
:Copyright: 2016, Karr Lab
:License: MIT
"""

from __future__ import unicode_literals

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'Core'
