""" REST API app configuration
:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2016-11-01
:Copyright: 2016, Karr Lab
:License: MIT
"""

from __future__ import unicode_literals

from django.apps import AppConfig


class RestConfig(AppConfig):
    name = 'rest'
    verbose_name = 'REST'
