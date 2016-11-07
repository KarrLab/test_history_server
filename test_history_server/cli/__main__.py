from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_history_server.site.settings")
django.setup()

from test_history_server.core import models
import test_history_server


class BaseController(CementBaseController):
    """ Base controller for command line application """

    class Meta:
        label = 'base'
        description = "Test history server command line interface"

    @expose(help='Get version')
    def get_version(self):
        """ Get version """
        print(test_history_server.__version__)


class RenameRepoController(CementBaseController):
    class Meta:
        label = 'rename-repository'
        description = 'Rename repository from old_name to new_name'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['old_name'], dict(type=str, help='Old repository name')),
            (['new_name'], dict(type=str, help='New repository name')),
        ]

    @expose(hide=True)
    def default(self):
        args = self.app.pargs
        repo = models.Repository.objects.get(name=args.old_name)
        repo.name = args.new_name
        repo.save()


class AddRepoAliasController(CementBaseController):
    class Meta:
        label = 'add-repository-alias'
        description = 'Add alias to repository'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['name'], dict(type=str, help='Repository name')),
            (['alias'], dict(type=str, help='Repository alias')),
        ]

    @expose(hide=True)
    def default(self):
        args = self.app.pargs
        repo = models.Repository.objects.get(name=args.name)
        alias = repo.aliases.create(name=args.alias)
        alias.save()


class MergeRepoReportsController(CementBaseController):
    class Meta:
        label = 'merge-repository-reports'
        description = 'Merge reports from repository src to dst'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['src'], dict(type=str, help='Repository name')),
            (['dst'], dict(type=str, help='Repository alias')),
        ]

    @expose(hide=True)
    def default(self):
        args = self.app.pargs
        src_repo = models.Repository.objects.get(name=args.src)
        dst_repo = models.Repository.objects.get(name=args.dst)
        for report in src_repo.reports.all():
            report.repository = dst_repo
            report.save()


class DeleteRepoController(CementBaseController):
    class Meta:
        label = 'delete-repository'
        description = 'Delete repository'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['name'], dict(type=str, help='Repository name')),
        ]

    @expose(hide=True)
    def default(self):
        args = self.app.pargs
        repo = models.Repository.objects.get(name=args.name)
        repo.delete()


class App(CementApp):
    """ Command line application """
    class Meta:
        label = 'test-history-server-cli'
        base_controller = 'base'
        handlers = [
            BaseController,
            RenameRepoController,
            AddRepoAliasController,
            MergeRepoReportsController,
            DeleteRepoController,
        ]


def main():
    with App() as app:
        app.run()

if __name__ == '__main__':
    main()
