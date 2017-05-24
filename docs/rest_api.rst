REST API documentation
======================

* Endpoint: `<settings.BASE_URL>/rest/submit_report`
* Method: POST
* Arguments:

  * `token` (string): secret token used to authenticate with server
  * `repo_owner` (string): user or organization which owns the GitHub repository
  * `repo_name` (string): the name of the GitHub repository
  * `repo_branch` (string):  the name of the branch of the repository that was tested
  * `repo_revision` (string): the SHA1 key of the revision that was tested
  * `build_num` (integer): the build number that was tested
  * `report_name` (string, optional): textual label for individual reports within build, such as to indicate results from different versions of Python
  * `report` (file): JUnit-style XML test report
