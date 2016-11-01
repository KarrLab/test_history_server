from collections import OrderedDict
from datetime import datetime
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from test_history_server.site import settings
from test_history_server.core.models import Repository, Report, TestSuite, TestCase
import os

###################
### pages
###################
def index(request):
    ''' Returns HTML for home page

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP request

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with HTML for home page
    '''
    repositories = []
    for repo in Repository.objects.all():
        report = repo.reports.order_by('-date')[0]
        repositories.append({
            'name': repo.name,
            'owner': repo.owner,
            'status_is_pass': report.test_suite.test_cases.exclude(result='pass').count() == 0,
            'build_number': report.build_number,
            'report_name': report.name,
            'report_date': report.date,
        })

    return render_template(request, 'index.html',
        context={
            'repositories': repositories
            }
        )

def repo(request, owner, repo):
    repo = Repository.objects.get(owner=owner, name=repo)

    # reports
    reports = []
    for report in repo.reports.order_by('-build_number', 'name').annotate(time=Sum('test_suite__test_cases__time')):
        suite = report.test_suite

        tests = suite.test_cases.count()
        passes = suite.test_cases.filter(result='pass').count()
        skips = suite.test_cases.filter(result='skip').count()
        failures = suite.test_cases.filter(result='failure').count()
        errors = suite.test_cases.filter(result='error').count()
        time = report.time

        reports.append({
            'build_number': report.build_number,
            'repository_branch': report.repository_branch,
            'repository_revision': report.repository_revision,
            'date': report.date,
            'name': report.name,
            'tests': tests,
            'passes': passes,
            'skips': skips,
            'failures': failures,
            'errors': errors,
            'time': time,
            'percent_pass': passes / (passes + failures + errors) * 100,
            'percent_fail': (1 - passes / (passes + failures + errors)) * 100,
        })

    # modules
    cases = TestCase.objects.filter(test_suite__report__repository=repo).order_by('classname')
    modules = cases.values('classname').annotate(
        cases=Count('name', distinct=True),
        builds=Count('test_suite__report__build_number', distinct=True),
        reports=Count('test_suite__report', distinct=True),
        )

    return render_template(request, 'repo.html',
        context={
            'repo': repo,
            'reports': reports,
            'modules': modules,
            }
        )

def classname(request, owner, repo, classname):
    repo = Repository.objects.get(owner=owner, name=repo)

    # reports
    reports = []
    for report in TestCase.objects\
        .filter(test_suite__report__repository=repo, classname=classname)\
        .order_by('-test_suite__report__build_number', 'test_suite__report__name')\
        .values(
            'test_suite',
            'test_suite__report__repository_branch',
            'test_suite__report__repository_revision',
            'test_suite__report__build_number',
            'test_suite__report__date',
            'test_suite__report__name')\
        .annotate(time=Sum('time'), tests=Count('id')):

        cases = TestCase.objects\
            .filter(
                test_suite__report__repository=repo,
                test_suite=report['test_suite'],
                classname=classname)
        passes = cases.filter(result='pass').count()
        skips = cases.filter(result='skip').count()
        failures = cases.filter(result='failure').count()
        errors = cases.filter(result='error').count()

        reports.append({
            'repository_branch': report['test_suite__report__repository_branch'],
            'repository_revision': report['test_suite__report__repository_revision'],
            'build_number': report['test_suite__report__build_number'],
            'date': report['test_suite__report__date'],
            'name': report['test_suite__report__name'],
            'tests': report['tests'],
            'passes': passes,
            'skips': skips,
            'failures': failures,
            'errors': errors,
            'time': report['time'],
            'percent_pass': passes / (passes + failures + errors) * 100,
            'percent_fail': (1 - passes / (passes + failures + errors)) * 100,
        })

    # cases
    cases = TestCase.objects\
        .filter(test_suite__report__repository=repo, classname=classname)\
        .order_by('name')\
        .values('name')\
        .annotate(
            builds=Count('test_suite__report__build_number', distinct=True),
            reports=Count('test_suite__report', distinct=True),
            )

    return render_template(request, 'classname.html',
        context={
            'repo': repo,
            'classname': classname,
            'reports': reports,
            'cases': cases,
            }
        )

def case(request, owner, repo, classname, case):
    repo = Repository.objects.get(owner=owner, name=repo)

    cases = TestCase.objects\
        .filter(
            test_suite__report__repository=repo,
            classname=classname,
            name=case)\
        .order_by('-test_suite__report__build_number', 'test_suite__report__name')

    return render_template(request, 'case.html',
        context={
            'repo': repo,
            'classname': classname,
            'case': case,
            'cases': cases,
            }
        )

def build(request, owner, repo, build):
    repo = Repository.objects.get(owner=owner, name=repo)

    reports = []
    for report in repo.reports.filter(build_number=build).order_by('name').annotate(time=Sum('test_suite__test_cases__time')):
        suite = report.test_suite

        tests = suite.test_cases.count()
        passes = suite.test_cases.filter(result='pass').count()
        skips = suite.test_cases.filter(result='skip').count()
        failures = suite.test_cases.filter(result='failure').count()
        errors = suite.test_cases.filter(result='error').count()
        time = report.time

        reports.append({
            'build_number': build,
            'repository_branch': report.repository_branch,
            'repository_revision': report.repository_revision,
            'date': report.date,
            'name': report.name,
            'tests': tests,
            'passes': passes,
            'skips': skips,
            'failures': failures,
            'errors': errors,
            'time': time,
            'percent_pass': passes / (passes + failures + errors) * 100,
            'percent_fail': (1 - passes / (passes + failures + errors)) * 100,
        })

    cases = []
    for case in TestCase.objects\
        .filter(test_suite__report__repository=repo, test_suite__report__build_number=build)\
        .order_by('name')\
        .values('classname', 'name')\
        .annotate(time=Sum('time')):

        temp = TestCase.objects.filter(
                test_suite__report__repository=repo,
                test_suite__report__build_number=build,
                classname=case['classname'],
                name=case['name'])
        tests = temp.count()
        passes = temp.filter(result='pass').count()
        skips = temp.filter(result='skip').count()
        failures = temp.filter(result='failure').count()
        errors = temp.filter(result='error').count()

        cases.append({
            'classname': case['classname'],
            'name': case['name'],
            'tests': tests,
            'passes': passes,
            'skips': skips,
            'failures': failures,
            'errors': errors,
            'time': case['time'],
            'percent_pass': passes / (passes + failures + errors) * 100,
            'percent_fail': (1 - passes / (passes + failures + errors)) * 100,
        })

    return render_template(request, 'build.html',
        context={
            'repo': repo,
            'reports': reports,
            'cases': cases,
            }
        )


def report(request, owner, repo, build, report):
    repo = Repository.objects.get(owner=owner, name=repo)
    report = repo.reports.get(build_number=build, name=report)
    cases = report.test_suite.test_cases.order_by('name')

    return render_template(request, 'report.html',
        context={
            'repo': repo,
            'report': report,
            'cases': cases,
            }
        )

###################
### sitemap
###################
def sitemap(request):
    ''' Returns site map in XML

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP request

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with XML site map
    '''
    return render_template(request, 'sitemap.xml',
        context={
            'BASE_URL': BASE_URL.ROOT_URL,
            'repositories': Repository.objects.all(),
            },
        content_type='application/xml')

def robots(request):
    ''' Returns robots.txt file

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP request

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with robots.txt file
    '''
    return render_template(request, 'robots.txt',
        context={
            'BASE_DOMAIN': settings.BASE_DOMAIN,
            'BASE_URL': settings.BASE_URL,
            },
        content_type='plain/text')

###################
### helper functions
###################
def render_template(request, template, context={}, content_type='text/html'):
    ''' Returns rendered template

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP request
        template (:obj:`str`): path to template to render_template
        context (:obj:`dict`, optional): dictionary of data needed to render template
        content_type (:obj:`str`, optional): mime type

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response
    '''

    #add data
    context['request'] = request
    context['last_updated_date'] = datetime.fromtimestamp(os.path.getmtime(os.path.join(settings.TEMPLATES[0]['DIRS'][0], template)))

    #render
    return render(request, template, context=context, content_type=content_type)
