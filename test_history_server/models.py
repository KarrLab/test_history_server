from django.db.models import Model, CharField, DateTimeField, ForeignKey, IntegerField

STATUS_CHOICES = (
    ('failure', 'Failure'),
    ('success', 'Success'),
    )


class Repository(Model):
    ''' Represents a repository '''

    name = CharField(max_length=255, verbose_name='Name')
    owner = CharField(max_length=255, verbose_name='Owner')

    class Meta:
        verbose_name='Repository'
        verbose_name_plural = 'Repositories'
        ordering = ['name']
        get_latest_by = 'reports__date'


class Report(Model):
    ''' Represents a test report '''

    name = CharField(max_length=255, blank=True, default='', verbose_name='Name')
    repository = ForeignKey('Repository', related_name='reports', verbose_name='Repository')
    repository_branch = CharField(max_length=255, verbose_name='Repository branch')
    repository_revision = CharField(max_length=255, verbose_name='Repository revision')
    build_number = IntegerField(verbose_name='Build number')
    status = CharField(max_length=255, verbose_name='Status', choices = STATUS_CHOICES)
    date = DateTimeField(auto_now=True, auto_now_add=True, verbose_name='Date')

    class Meta:
        verbose_name='Report'
        verbose_name_plural = 'Reports'
        ordering = ['-build_number', '-date']
        get_latest_by = 'status_date'
