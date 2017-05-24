Usage
=====

Browsing test histories
--------------------------
To browse test histories, open the URL specified by `BASE_URL` in `/path/to/web-server/test_history_server/test_history_server/site/settings.py`.

Uploading test reports
--------------------------
The following example illustrates how to add test reports to the database::

    import requests

    r = requests.post('<settings.BASE_URL>/rest/submit_report',
          data={
              'token': <test_server_token>,
              'repo_name': <repo_name>,
              'repo_owner': <repo_owner>,
              'repo_branch': <repo_branch>,
              'repo_revision': <repo_revision>,
              'build_num': <build_num>,
              'report_name': <extra textual label for individual reports within build, such as to indicate results from different versions of Python>,
          },
          files={
              'report': </path/to/junit-style-XML-test-report.xml>,
          })

    r_json = r.json()

    if not r_json['success']:
        raise BuildHelperError('Error uploading report to test history server: {}'.format(r_json['message']))
