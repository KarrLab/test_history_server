from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from junit2htmlreport.parser import Junit as JunitParser
from nose2unitth.core import Converter as Nose2UnitthConverter
from test_history_server import settings
from test_history_server.forms import SubmitReportForm
from test_history_server.models import Repository, Report
from unitth.core import UnitTH
from xml.dom import minidom
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
    return render_template('index.html', request,
        data = {
            'repositories': Repository.objects.all()
            }
        )

@csrf_exempt
def submit_report(request):
    ''' Save test report and returns result in JSON

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP POST request with these arguments
            * `token` (string): secret token used to authenticate with server
            * `repo_owner` (string): user or organization which owns the GitHub repository
            * `repo_name` (string): the name of the GitHub repository
            * `repo_branch` (string):  the name of the branch of the repository that was tested
            * `repo_revision` (string): the SHA1 key of the revision that was tested
            * `build_num` (integer): the build number that was tested
            * `report_name` (string, optional): textual label for individual reports within build, such as to indicate results from different versions of Python
            * `report` (file): JUnit-style XML test report

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with result in JSON format
            * status (:obj:`bool`): indicates success/failure
            * message (:obj:`str`): summary of results
            * details (:obj:`dict`): dictionary of form validation errors
    '''
    if not request.method == 'POST':
        return json_response(False, 'Invalid method: {}. Only POST is allowed.'.format(request.method))

    form = SubmitReportForm(request.POST, request.FILES)

    if not form.is_valid():
        return json_response(False, 'Invalid form', form.errors)

    if not form.cleaned_data['token'] == os.getenv('TOKEN'):
        return json_response(False, 'Invalid token')

    #get info from form
    repo_name = form.cleaned_data['repo_name']
    repo_owner = form.cleaned_data['repo_owner']
    repo_branch = form.cleaned_data['repo_branch']
    repo_revision = form.cleaned_data['repo_revision']
    build_num = form.cleaned_data['build_num']
    report_name = form.cleaned_data['report_name']

    #setup file and directory names
    repo_dir = os.path.join(settings.STATIC_ROOT, 'repo', repo_owner, repo_name)
    repo_dir_xml = os.path.join(repo_dir, 'xml')
    repo_dir_unitth = os.path.join(repo_dir, 'unitth')
    repo_dir_html = os.path.join(repo_dir, 'html')
    report_filename_xml = os.path.join(repo_dir_xml, '{:d}.{:s}.xml'.format(build_num, report_name))
    report_dir_unitth = os.path.join(repo_dir_unitth, '{:d}.{:s}'.format(build_num, report_name))
    report_filename_html = os.path.join(report_dir_unitth, 'index.html')

    if not os.path.isdir(repo_dir):
        os.makedirs(repo_dir)
    if not os.path.isdir(repo_dir_xml):
        os.makedirs(repo_dir_xml)
    if not os.path.isdir(repo_dir_unitth):
        os.makedirs(repo_dir_unitth)
    if not os.path.isdir(repo_dir_html):
        os.makedirs(repo_dir_html)

    #save report
    with open(report_filename_xml, 'w') as fid:
        for chunk in request.FILES['report'].chunks():
            fid.write(chunk)

    #get report status
    report = minidom.parse(report_filename_xml)
    suite = report.getElementsByTagName("testsuite")[0]
    if float(suite.getAttribute('errors')) == 0 and float(suite.getAttribute('failures')) == 0:
        report_status = 'success'
    else:
        report_status = 'failure'

    #convert report to unitth style
    Nose2UnitthConverter.run(report_filename_xml, report_dir_unitth)

    #generate html for report
    with open(report_filename_html, 'wb') as html_file:
        html_file.write(JunitParser(report_filename_xml).html().encode('utf-8'))

    #update history report
    UnitTH.run(os.path.join(repo_dir_unitth, '*'),
           xml_report_filter='',
           html_report_path='.',
           generate_exec_time_graphs=True,
           html_report_dir=repo_dir_html,
           initial_java_heap_size='16m',
           maximum_java_heap_size='64m')

    #add repo and report to database
    repo, created = Repository.objects.get_or_create(name=repo_name, owner=repo_owner)
    report, created = Report.objects.get_or_create(
        repository=repo,
        repository_branch=repo_branch,
        repository_revision=repo_revision,
        build_number=build_num,
        name=report_name,
        status=report_status)
    report.date = datetime.now()
    report.save()

    return json_response(True, 'Report successfully uploaded')

def json_response(success, message, details=None):
    data = {
        'success': success,
        'message': message,
        'details': details,
        }
    return HttpResponse(
        simplejson.dumps(data, ensure_ascii=False, encoding='utf-8'),
        mimetype = "application/json; charset=UTF-8",
        content_type = "application/json; charset=UTF-8")

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
    return render_template('sitemap.xml', request,
        data = {
            'ROOT_URL': settings.ROOT_URL,
            'repositories': Repository.objects.all(),
            },
        mimetype='application/xml')

def robots(request):
    ''' Returns robots.txt file

    Args:
        request (:obj:`django.http.request.HttpRequest`): HTTP request

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with robots.txt file
    '''
    return render_template('robots.txt', request,
        data = {
            'ROOT_DOMAIN': settings.ROOT_DOMAIN,
            'ROOT_URL': settings.ROOT_URL,
            },
        mimetype='plain/text')

###################
### helper functions
###################
def render_template(templateFile, request, data = {}, mimetype = 'text/html'):
    ''' Returns rendered template

    Args:
        templateFile (:obj:`str`): path to template to render_template
        request (:obj:`django.http.request.HttpRequest`): HTTP request
        data (:obj:`dict`, optional): dictionary of data needed to render template
        mimetype (:obj:`str`, optional): mime type

    Returns:
        :obj:`django.http.HttpResponse`: HTTP response with XML site map
    '''

    #add data
    data['request'] = request
    data['last_updated_date'] = datetime.fromtimestamp(os.path.getmtime(os.path.join(settings.TEMPLATE_DIRS[0], templateFile)))

    #render
    return render_to_response(templateFile, data, context_instance = RequestContext(request), mimetype = mimetype)
