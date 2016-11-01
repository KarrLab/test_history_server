from datetime import datetime
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from test_history_server.core.models import Repository, Report, TestSuite, TestCase
from test_history_server.rest.forms import SubmitReportForm
from test_history_server.site import settings
from xml.dom import minidom
import os

@csrf_exempt
def submit_report(request):
    ''' Save a report and returns result in JSON

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

    if not form.cleaned_data['token'] == settings.REST_API_TOKEN:
        return json_response(False, 'Invalid token')

    #get info from form
    repo_name = form.cleaned_data['repo_name']
    repo_owner = form.cleaned_data['repo_owner']
    repo_branch = form.cleaned_data['repo_branch']
    repo_revision = form.cleaned_data['repo_revision']
    build_num = form.cleaned_data['build_num']
    report_name = form.cleaned_data['report_name']

    #setup file and directory names
    xml_reports_dir = os.path.join(settings.XML_REPORTS_DIR, repo_owner, repo_name)
    report_filename = os.path.join(xml_reports_dir, '{:d}.{:s}.xml'.format(build_num, report_name))

    if not os.path.isdir(xml_reports_dir):
        os.makedirs(xml_reports_dir)

    #save report
    with open(report_filename, 'wb') as fid:
        for chunk in request.FILES['report'].chunks():
            fid.write(chunk)

    #get report status
    doc_xml = minidom.parse(report_filename)
    report_xml = doc_xml.getElementsByTagName("testsuite")[0]

    #add repo, report, test suite, and test cases to database
    repo, created = Repository.objects.get_or_create(name=repo_name, owner=repo_owner)

    report, created = Report.objects.get_or_create(
        repository=repo,
        repository_branch=repo_branch,
        repository_revision=repo_revision,
        build_number=build_num,
        name=report_name,
        )
    report.date = datetime.now()
    report.save()

    try:
        test_suite = report.test_suite
    except ObjectDoesNotExist:
        test_suite = TestSuite(report=report)
    test_suite.save()

    test_suite.test_cases.all().delete()

    for case_xml in report_xml.getElementsByTagName('testcase'):
        kwargs = {}

        #classname and name
        kwargs['classname'] = case_xml.getAttribute('classname')
        kwargs['name'] = case_xml.getAttribute('name')

        #file and line
        if case_xml.hasAttribute('file'):
            kwargs['file'] = case_xml.getAttribute('file')
        if case_xml.hasAttribute('line'):
            kwargs['line'] = int(float(case_xml.getAttribute('line')))

        #time
        kwargs['time'] = float(case_xml.getAttribute('time'))

        #stdout, stderr
        stdout_xml = case_xml.getElementsByTagName('system-out')
        if stdout_xml:
            kwargs['stdout'] = "".join([child.nodeValue for child in stdout_xml[0].childNodes])

        stderr_xml = case_xml.getElementsByTagName('system-err')
        if stderr_xml:
            kwargs['stderr'] = "".join([child.nodeValue for child in stderr_xml[0].childNodes])

        #skip, error, failure
        skipped_xml = case_xml.getElementsByTagName('skipped')
        failure_xml = case_xml.getElementsByTagName('failure')
        error_xml = case_xml.getElementsByTagName('error')
        if skipped_xml:
            kwargs['result'] = 'skipped'
            kwargs['result_type'] = skipped_xml[0].getAttribute('type')
            kwargs['result_message'] = skipped_xml[0].getAttribute('message')
            kwargs['result_details'] = "".join([child.nodeValue for child in skipped_xml[0].childNodes])
        elif failure_xml:
            kwargs['result'] = 'failure'
            kwargs['result_type'] = failure_xml[0].getAttribute('type')
            kwargs['result_message'] = failure_xml[0].getAttribute('message')
            kwargs['result_details'] = "".join([child.nodeValue for child in failure_xml[0].childNodes])
        elif error_xml:
            kwargs['result'] = 'error'
            kwargs['result_type'] = error_xml[0].getAttribute('type')
            kwargs['result_message'] = error_xml[0].getAttribute('message')
            kwargs['result_details'] = "".join([child.nodeValue for child in error_xml[0].childNodes])
        else:
            kwargs['result'] = 'pass'

        test_suite.test_cases.create(**kwargs)

    return json_response(True, 'Test report successfully uploaded')

def json_response(success, message, details=None):
    return JsonResponse({
        'success': success,
        'message': message,
        'details': details,
        })
