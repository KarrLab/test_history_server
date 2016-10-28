from django import forms


class SubmitReportForm(forms.Form):
    ''' Form for uploading test report '''
    token = forms.CharField(
        required=True,
        widget=forms.TextInput,
        label='Token',
        help_text='Enter the secret token'
    )
    repo_name = forms.CharField(
        required=True,
        widget=forms.TextInput,
        label='Repository name',
        help_text='Enter the name of the repository'
    )
    repo_owner = forms.CharField(
        required=True,
        widget=forms.TextInput,
        label='Repository owner',
        help_text='Enter the owner of the repository'
    )
    repo_branch = forms.CharField(
        required=True,
        widget=forms.TextInput,
        label='Repository branch',
        help_text='Enter the branch name'
    )
    repo_revision = forms.CharField(
        required=True,
        widget=forms.TextInput,
        label='Repository revision',
        help_text='Enter the sha key for the revision'
    )
    build_num = forms.IntegerField(
        required=True,
        widget=forms.TextInput,
        label='Build number',
        help_text='Enter the build number'
    )
    report_name = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label='Report name',
        help_text='Enter the report name (e.g. Python version)'
    )
    report = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput,
        label='JUnit-style XML unit test report',
        help_text='Select an XML unit test results file to import'
    )
