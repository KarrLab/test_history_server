from django.db.models import Model, CharField, DateTimeField, FloatField, ForeignKey, IntegerField, OneToOneField, PositiveIntegerField, TextField

RESULT_CHOICES = (
    ('pass', 'Pass'),
    ('failure', 'Failure'),
    ('error', 'Error'),
    ('skipped', 'Skipped'),
)


class Repository(Model):
    ''' Represents a repository '''

    name = CharField(max_length=255, verbose_name='Name')
    owner = CharField(max_length=255, verbose_name='Owner')

    class Meta:
        verbose_name='Repository'
        verbose_name_plural = 'Repositories'
        ordering = ['name']
        get_latest_by = 'test_suites__date'


class Report(Model):
    ''' Represents a report '''
    name = CharField(max_length=255, blank=True, default='', verbose_name='Name')
    repository = ForeignKey('Repository', related_name='reports', verbose_name='Repository')
    repository_branch = CharField(max_length=255, verbose_name='Repository branch')
    repository_revision = CharField(max_length=255, verbose_name='Repository revision')
    build_number = IntegerField(verbose_name='Build number')
    date = DateTimeField(auto_now=True, verbose_name='Date')

    class Meta:
        verbose_name='Report'
        verbose_name_plural = 'Reports'
        ordering = ['-build_number', '-date']
        get_latest_by = 'date'


class TestSuite(Model):
    report = OneToOneField('Report', related_name='test_suite', verbose_name='Report')

    class Meta:
        verbose_name='Test suite'
        verbose_name_plural = 'Test suites'
        ordering = ['-report__build_number', '-report__date']
        get_latest_by = 'report__date'


class TestCase(Model):
    ''' Represents a test case '''
    test_suite = ForeignKey('TestSuite', related_name='test_cases', verbose_name='Test suites')
    classname = TextField(verbose_name='Class name')
    name = TextField(verbose_name='Name')
    file = TextField(verbose_name='File', blank=True, default='')
    line = PositiveIntegerField(verbose_name='Line', null=True, blank=True)
    time = FloatField(verbose_name='Time')
    stdout = TextField(verbose_name='Standard output', blank=True, default='')
    stderr = TextField(verbose_name='Standard error', blank=True, default='')
    result = CharField(verbose_name='Result', max_length=10, choices = RESULT_CHOICES)
    result_type = TextField(verbose_name='Result type', blank=True, default='')
    result_message = TextField(verbose_name='Result message', blank=True, default='')
    result_details = TextField(verbose_name='Result details', blank=True, default='') #not for skip

    class Meta:
        verbose_name='Test case'
        verbose_name_plural = 'Test cases'
        ordering = ['name']
        get_latest_by = 'test_suite__date'
