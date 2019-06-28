import cement
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_history_server.site.settings")
django.setup()

from test_history_server.core import models
import test_history_server


class BaseController(cement.Controller):
    """ Base controller for command line application """

    class Meta:
        label = 'base'
        description = "Test history server command line interface"
        help = "Test history server command line interface"
        arguments = [
            (['-v', '--version'], dict(action='version', version=test_history_server.__version__)),
        ]

    @cement.ex(hide=True)
    def _default(self):
        self._parser.print_help()


class RenameRepoController(cement.Controller):
    class Meta:
        label = 'rename-repository'
        description = 'Rename repository from old_name to new_name'
        help = 'Rename repository from old_name to new_name'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['old_name'], dict(type=str, help='Old repository name')),
            (['new_name'], dict(type=str, help='New repository name')),
        ]

    @cement.ex(hide=True)
    def _default(self):
        args = self.app.pargs
        repo = models.Repository.objects.get(name=args.old_name)
        repo.name = args.new_name
        repo.save()


class AddRepoAliasController(cement.Controller):
    class Meta:
        label = 'add-repository-alias'
        description = 'Add alias to repository'
        help = 'Add alias to repository'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['name'], dict(type=str, help='Repository name')),
            (['alias'], dict(type=str, help='Repository alias')),
        ]

    @cement.ex(hide=True)
    def _default(self):
        args = self.app.pargs
        repo = models.Repository.objects.get(name=args.name)
        alias = repo.aliases.create(name=args.alias)
        alias.save()


class MergeRepoReportsController(cement.Controller):
    class Meta:
        label = 'merge-repository-reports'
        description = 'Merge reports from repository src to dst'
        help = 'Merge reports from repository src to dst'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['src'], dict(type=str, help='Repository name')),
            (['dst'], dict(type=str, help='Repository alias')),
        ]

    @cement.ex(hide=True)
    def _default(self):
        args = self.app.pargs
        src_repo = models.Repository.objects.get(name=args.src)
        dst_repo = models.Repository.objects.get(name=args.dst)
        for report in src_repo.reports.all():
            report.repository = dst_repo
            report.save()


class DeleteRepoController(cement.Controller):
    class Meta:
        label = 'delete-repository'
        description = 'Delete repository'
        help = 'Delete repository'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['name'], dict(type=str, help='Repository name')),
        ]

    @cement.ex(hide=True)
    def _default(self):
        args = self.app.pargs
        repo = models.Repository.objects.get(name=args.name)
        repo.delete()


class App(cement.App):
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
