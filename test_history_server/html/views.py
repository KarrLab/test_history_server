""" HTML GUI views
:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2016-11-01
:Copyright: 2016, Karr Lab
:License: MIT
"""

from collections import OrderedDict
from datetime import datetime
from django.db.models import Avg, Count, Max, Sum, Q
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
    ''' Returns HTML for home page which displays a list of repositories

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP request

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with HTML for home page
    '''
    owners = Repository.objects\
        .order_by('owner')\
        .values('owner')\
        .annotate(repositories=Count('name', distinct=True))

    repos = Repository.objects.all()
    statistics = {
        'repositories': repos.count(),
        'builds': repos.aggregate(builds=Count('reports__build_number', distinct=True))['builds'],
        'reports': repos.aggregate(reports=Count('reports'))['reports'],
        'classes': repos.values('name', 'reports__test_suite__test_cases__classname').distinct().count(),
        'cases': repos.values('name', 'reports__test_suite__test_cases__classname', 'reports__test_suite__test_cases__name').distinct().count(),
        'last_report': repos.aggregate(date=Max('reports__date'))['date'],
        }

    return render_template(request, 'index.html',
        context={
            'owners': owners,
            'statistics': statistics,
            }
        )

def owner(request, owner):
    ''' Returns HTML for owner page which displays a list of repositories

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP request
        owner (:obj:`str`): name of owner

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with HTML for home page
    '''
    repos = Repository.objects.filter(owner=owner)
    statistics = {
        'builds': repos.aggregate(builds=Count('reports__build_number', distinct=True))['builds'],
        'reports': repos.aggregate(reports=Count('reports'))['reports'],
        'classes': repos.values('name', 'reports__test_suite__test_cases__classname').distinct().count(),
        'cases': repos.values('name', 'reports__test_suite__test_cases__classname', 'reports__test_suite__test_cases__name').distinct().count(),
        'last_report': repos.aggregate(date=Max('reports__date'))['date'],
        }

    repositories = []
    for repo in Repository.objects.filter(owner=owner):
        report = repo.reports.order_by('-date')[0]
        repositories.append({
            'name': repo.name,
            'owner': repo.owner,
            'status_is_pass': \
                report.test_suite.test_cases.filter(result='error').count() == 0 and \
                report.test_suite.test_cases.filter(result='failure').count() == 0,
            'build_number': report.build_number,
            'report_name': report.name,
            'report_date': report.date,
        })

    return render_template(request, 'owner.html',
        context={
            'owner': owner,
            'statistics': statistics,
            'repositories': repositories
            }
        )

def repo(request, owner, repo):
    ''' Returns HTML for repository page which displays tables of builds/reports
    and test classes.

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP request
        owner (:obj:`str`): name of repository owner
        repo (:obj:`str`): name of repository

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with HTML for home page
    '''
    repo = Repository.objects.get(owner=owner, name=repo)

    #statistics
    reports = repo.reports
    last_report = reports.order_by('-build_number')[0]

    passes = reports.exclude(Q(test_suite__test_cases__result='failure') | Q(test_suite__test_cases__result='error')).order_by('-build_number')
    if passes.count() > 0:
        last_pass = passes[0]
        last_pass_build = last_pass.build_number
        last_pass_date = last_pass.date
    else:
        last_pass_build = None
        last_pass_date = None

    fails = reports.filter(Q(test_suite__test_cases__result='failure') | Q(test_suite__test_cases__result='error')).order_by('-build_number')
    if fails.count() > 0:
        last_fail = fails[0]
        last_fail_build = last_fail.build_number
        last_fail_date = last_fail.date
    else:
        last_fail_build = None
        last_fail_date = None

    statistics = {
        'builds': reports.aggregate(builds=Count('build_number', distinct=True))['builds'],
        'reports': reports.count(),
        'classes': reports.values('test_suite__test_cases__classname').distinct().count(),
        'cases': reports.values('test_suite__test_cases__classname', 'test_suite__test_cases__name').distinct().count(),
        'last_report_build': last_report.build_number,
        'last_report_date': last_report.date,
        'last_pass_build': last_pass_build,
        'last_pass_date': last_pass_date,
        'last_fail_build': last_fail_build,
        'last_fail_date': last_fail_date,
        }

    #trends
    reports = repo.reports\
        .order_by('build_number', '-name')\
        .annotate(
            time=Sum('test_suite__test_cases__time'),
            classes=Count('test_suite__test_cases__classname', distinct=True),
            cases=Count('test_suite__test_cases'),
            )

    trends = {
        'report': [],
        'pass_rate': [],
        'time': [],
        'classes': [],
        'cases': [],
    }
    for report in reports:
        passes = report.test_suite.test_cases.filter(result='pass').count()
        failures = report.test_suite.test_cases.filter(result='failure').count()
        errors = report.test_suite.test_cases.filter(result='error').count()

        if passes + failures + errors > 0:
            pass_rate = passes / (passes + failures + errors) * 100.
        else:
            pass_rate = float('nan')

        trends['report'].append({'build_number': report.build_number, 'name': report.name})
        trends['pass_rate'].append(pass_rate)
        trends['time'].append(report.time)
        trends['classes'].append(report.classes)
        trends['cases'].append(report.cases)

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

        if passes + failures + errors > 0:
            percent_pass = passes / (passes + failures + errors) * 100
            percent_fail = 100 - percent_pass
        else:
            percent_pass = float('nan')
            percent_fail = float('nan')

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
            'percent_pass': percent_pass,
            'percent_fail': percent_fail,
        })

    # modules
    cases = TestCase.objects.filter(test_suite__report__repository=repo).order_by('classname')
    modules = cases.values('classname').annotate(
        cases=Count('name', distinct=True),
        builds=Count('test_suite__report__build_number', distinct=True),
        reports=Count('test_suite__report', distinct=True),
        )
    modules_html = []
    for module in modules:
        last_case = TestCase.objects.filter(test_suite__report__repository=repo, classname=module['classname'])\
            .order_by('-test_suite__report__build_number', 'test_suite__report__name')[0]

        modules_html.append({
            'classname': module['classname'],
            'repository_revision': last_case.test_suite.report.repository_revision,
            'file': last_case.file,
            'cases': module['cases'],
            'builds': module['builds'],
            'reports': module['reports'],
        })

    return render_template(request, 'repo.html',
        context={
            'repo': repo,
            'statistics': statistics,
            'trends': trends,
            'reports': reports,
            'modules': modules_html,
            }
        )

def classname(request, owner, repo, classname):
    ''' Returns HTML for test class page which displays a list of builds/reports
    which includes the test class and the test cases within the class.

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP request
        owner (:obj:`str`): name of repository owner
        repo (:obj:`str`): name of repository
        classname (:obj:`str`): name of test class

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with HTML for home page
    '''

    if classname == '__None__':
        classname = ''

    repo = Repository.objects.get(owner=owner, name=repo)

    #statistics
    reports = repo.reports.filter(test_suite__test_cases__classname=classname)
    last_report = reports.order_by('-build_number')[0]

    passes = reports.exclude(Q(test_suite__test_cases__result='failure') | Q(test_suite__test_cases__result='error')).order_by('-build_number')
    if passes.count() > 0:
        last_pass = passes[0]
        last_pass_build = last_pass.build_number
        last_pass_date = last_pass.date
    else:
        last_pass_build = None
        last_pass_date = None

    fails = reports.filter(Q(test_suite__test_cases__result='failure') | Q(test_suite__test_cases__result='error')).order_by('-build_number')
    if fails.count() > 0:
        last_fail = fails[0]
        last_fail_build = last_fail.build_number
        last_fail_date = last_fail.date
    else:
        last_fail_build = None
        last_fail_date = None

    statistics = {
        'builds': reports.aggregate(builds=Count('build_number', distinct=True))['builds'],
        'reports': reports.distinct().count(),
        'cases': reports.values('test_suite__test_cases__classname', 'test_suite__test_cases__name').distinct().count(),
        'last_report_build': last_report.build_number,
        'last_report_date': last_report.date,
        'last_pass_build': last_pass_build,
        'last_pass_date': last_pass_date,
        'last_fail_build': last_fail_build,
        'last_fail_date': last_fail_date,
        }

    #trends
    reports = repo.reports\
        .filter(test_suite__test_cases__classname=classname)\
        .order_by('build_number', '-name')\
        .annotate(
            time=Sum('test_suite__test_cases__time'),
            cases=Count('test_suite__test_cases'),
            )

    trends = {
        'report': [],
        'pass_rate': [],
        'time': [],
        'classes': [],
        'cases': [],
    }
    for report in reports:
        passes = report.test_suite.test_cases.filter(result='pass').count()
        failures = report.test_suite.test_cases.filter(result='failure').count()
        errors = report.test_suite.test_cases.filter(result='error').count()

        if passes + failures + errors > 0:
            pass_rate = passes / (passes + failures + errors) * 100.
        else:
            pass_rate = float('nan')

        trends['report'].append({'build_number': report.build_number, 'name': report.name})
        trends['pass_rate'].append(pass_rate)
        trends['time'].append(report.time)
        trends['cases'].append(report.cases)

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

        if passes + failures + errors > 0:
            percent_pass = passes / (passes + failures + errors) * 100
            percent_fail = 100 - percent_pass
        else:
            percent_pass = float('nan')
            percent_fail = float('nan')

        reports.append({
            'repository_branch': report['test_suite__report__repository_branch'],
            'repository_revision': report['test_suite__report__repository_revision'],
            'file': cases[0].file,
            'build_number': report['test_suite__report__build_number'],
            'date': report['test_suite__report__date'],
            'name': report['test_suite__report__name'],
            'tests': report['tests'],
            'passes': passes,
            'skips': skips,
            'failures': failures,
            'errors': errors,
            'time': report['time'],
            'percent_pass': percent_pass,
            'percent_fail': percent_fail,
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

    cases_html = []
    for case in cases:

        last_case = TestCase.objects\
            .filter(test_suite__report__repository=repo, classname=classname, name=case['name'])\
            .order_by('-test_suite__report__build_number', 'test_suite__report__name')[0]

        cases_html.append({
            'name': case['name'],
            'repository_revision': last_case.test_suite.report.repository_revision,
            'file': last_case.file,
            'line': last_case.line,
            'builds': case['builds'],
            'reports': case['reports'],
        })


    return render_template(request, 'classname.html',
        context={
            'repo': repo,
            'classname': classname,
            'statistics': statistics,
            'trends': trends,
            'reports': reports,
            'cases': cases_html,
            }
        )

def case(request, owner, repo, classname, case):
    ''' Returns HTML for test case page which displays a list of builds/reports
    which include the test case.

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP request
        owner (:obj:`str`): name of repository owner
        repo (:obj:`str`): name of repository
        classname (:obj:`str`): name of test class
        case (:obj:`str`): name of test case

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with HTML for home page
    '''

    if classname == '__None__':
        classname = ''

    repo = Repository.objects.get(owner=owner, name=repo)

    #statistics
    reports = repo.reports.filter(test_suite__test_cases__classname=classname, test_suite__test_cases__name=case)
    last_report = reports.order_by('-build_number')[0]

    passes = reports.exclude(Q(test_suite__test_cases__result='failure') | Q(test_suite__test_cases__result='error')).order_by('-build_number')
    if passes.count() > 0:
        last_pass = passes[0]
        last_pass_build = last_pass.build_number
        last_pass_date = last_pass.date
    else:
        last_pass_build = None
        last_pass_date = None

    fails = reports.filter(Q(test_suite__test_cases__result='failure') | Q(test_suite__test_cases__result='error')).order_by('-build_number')
    if fails.count() > 0:
        last_fail = fails[0]
        last_fail_build = last_fail.build_number
        last_fail_date = last_fail.date
    else:
        last_fail_build = None
        last_fail_date = None

    statistics = {
        'builds': reports.aggregate(builds=Count('build_number', distinct=True))['builds'],
        'reports': reports.distinct().count(),
        'last_report_build': last_report.build_number,
        'last_report_date': last_report.date,
        'last_pass_build': last_pass_build,
        'last_pass_date': last_pass_date,
        'last_fail_build': last_fail_build,
        'last_fail_date': last_fail_date,
        }

    #trends
    reports = TestCase.objects\
        .filter(
            test_suite__report__repository=repo,
            classname=classname,
            name=case)\
        .order_by('test_suite__report__build_number', '-test_suite__report__name')
    trends = {
        'report': [],
        'time': [],
    }
    for report in reports:
        trends['report'].append({'build_number': report.test_suite.report.build_number, 'name': report.test_suite.report.name})
        trends['time'].append(report.time)

    #cases
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
            'statistics': statistics,
            'trends': trends,
            'case': case,
            'cases': cases,
            }
        )

def build(request, owner, repo, build):
    ''' Returns HTML for build page which displays a list of reports which
    includes build and the test classes included in the build.

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP request
        owner (:obj:`str`): name of repository owner
        repo (:obj:`str`): name of repository
        build (:obj:`int`): number of build

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with HTML for home page
    '''

    repo = Repository.objects.get(owner=owner, name=repo)

    #statistics
    reports = repo.reports.filter(build_number=build)

    passes = reports.filter(test_suite__test_cases__result='pass').count()
    failures = reports.filter(test_suite__test_cases__result='failure').count()
    errors = reports.filter(test_suite__test_cases__result='error').count()

    if passes + failures + errors > 0:
        pass_rate = passes / (passes + failures + errors) * 100
    else:
        pass_rate = float('nan')

    statistics = {
        'reports': reports.distinct().count(),
        'classes': reports.values('test_suite__test_cases__classname').distinct().count(),
        'cases': reports.values('test_suite__test_cases__name').distinct().count(),
        'pass_rate': pass_rate,
        'time': reports.aggregate(time=Sum('test_suite__test_cases__time'))['time'] / reports.count(),
    }

    #reports
    reports = []
    for report in repo.reports.filter(build_number=build).order_by('name').annotate(time=Sum('test_suite__test_cases__time')):
        suite = report.test_suite

        tests = suite.test_cases.count()
        passes = suite.test_cases.filter(result='pass').count()
        skips = suite.test_cases.filter(result='skip').count()
        failures = suite.test_cases.filter(result='failure').count()
        errors = suite.test_cases.filter(result='error').count()
        time = report.time

        if passes + failures + errors > 0:
            percent_pass = passes / (passes + failures + errors) * 100
            percent_fail = 100 - percent_pass
        else:
            percent_pass = float('nan')
            percent_fail = float('nan')

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
            'percent_pass': percent_pass,
            'percent_fail': percent_fail,
        })

    cases = []
    for case in TestCase.objects\
        .filter(test_suite__report__repository=repo, test_suite__report__build_number=build)\
        .order_by('name')\
        .values('classname', 'name', 'file', 'line', 'test_suite__report__repository_revision')\
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

        if passes + failures + errors > 0:
            percent_pass = passes / (passes + failures + errors) * 100
            percent_fail = 100 - percent_pass
        else:
            percent_pass = float('nan')
            percent_fail = float('nan')

        cases.append({
            'classname': case['classname'],
            'name': case['name'],
            'repository_revision': case['test_suite__report__repository_revision'],
            'file': case['file'],
            'line': case['line'],
            'tests': tests,
            'passes': passes,
            'skips': skips,
            'failures': failures,
            'errors': errors,
            'time': case['time'],
            'percent_pass': percent_pass,
            'percent_fail': percent_fail,
        })

    return render_template(request, 'build.html',
        context={
            'repo': repo,
            'statistics': statistics,
            'reports': reports,
            'cases': cases,
            }
        )


def report(request, owner, repo, build, report):
    ''' Returns HTML for report page which displays a list of test classes
    included in the report.

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP request
        owner (:obj:`str`): name of repository owner
        repo (:obj:`str`): name of repository
        build (:obj:`int`): number of build
        report (:obj:`name`): name of the report

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with HTML for home page
    '''

    repo = Repository.objects.get(owner=owner, name=repo)
    report = repo.reports.get(build_number=build, name=report)


    #statistics
    cases = report.test_suite.test_cases

    passes = cases.filter(result='pass').count()
    failures = cases.filter(result='failure').count()
    errors = cases.filter(result='error').count()

    if passes + failures + errors > 0:
        pass_rate = passes / (passes + failures + errors) * 100
    else:
        pass_rate = float('nan')

    statistics = {
        'classes': cases.values('classname').distinct().count(),
        'cases': cases.count(),
        'pass_rate': pass_rate,
        'time': cases.aggregate(time=Sum('time'))['time'],
    }

    #cases
    cases = report.test_suite.test_cases.order_by('name')

    return render_template(request, 'report.html',
        context={
            'repo': repo,
            'report': report,
            'statistics': statistics,
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
