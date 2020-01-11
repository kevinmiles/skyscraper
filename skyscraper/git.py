import os
import subprocess

from . import config


class RepositoryException(Exception):
    pass


class DeclarativeRepository(object):
    def __init__(self, repo_path, workdir, subfolder='', branch='master'):
        self.repo_path = repo_path
        self.workdir = workdir
        self.spiderdir = os.path.join(self.workdir, subfolder)
        self.branch = branch

        self.update()

    def iterate_spiders(self, project=None):
        """Iterates all spiders and yields pairs of (project, spider)"""

        if project is None:
            for project in self._iterate_project_folders(self.spiderdir):
                for project, spider in self.iterate_spiders(project):
                    yield project, spider
        else:
            project_dir = os.path.join(self.spiderdir, project)
            for filename in next(os.walk(project_dir))[2]:
                if not filename.endswith('.py'):
                    continue

                spider = os.path.splitext(filename)[0]

                if self._validate_spider(project, spider):
                    yield (project, spider)

    def get_config(self, project, spider):
        configfile = os.path.join(self.spiderdir, project, spider + '.yml')

        with open(configfile, 'r') as f:
            return config.load(f, project, spider)

    def get_all_configs(self):
        configs = [self.get_config(project, spider)
                   for project, spider in self.iterate_spiders()]
        return configs

    def update(self):
        # If the folder is empty, clone the repository
        # otherwise check whether this actually is a clone of the
        # defined source repository or something entirely different
        if len(os.listdir(self.workdir)) == 0:
            subprocess.call(
                ['git', 'clone', '--single-branch', '--branch', self.branch,
                    self.repo_path, self.workdir],
                stdout=subprocess.DEVNULL)

            # Do not use TOR proxy (http_proxy env variable) for git
            # TODO: We should allow the user to set a custom proxy here, too,
            # e.g. for company networks
            subprocess.call(
                ['git', 'config', '--add', 'remote.origin.proxy', '""'],
                cwd=self.workdir,
                stdout=subprocess.DEVNULL)
        elif not self._check_remote():
            raise RepositoryException(
                'It seems this is not a repository cloned from {}'.format(
                    self.repo_path))

        # only switch branch if we are on a different branch
        # otherwise we get "Already on [branch]" on stderr
        if self._current_branch() != self.branch:
            subprocess.call(
                ['git', 'checkout', self.branch], cwd=self.workdir,
                stdout=subprocess.DEVNULL)

        subprocess.call(
            ['git', 'pull'], cwd=self.workdir,
            stdout=subprocess.DEVNULL)

    def _validate_spider(self, project, spider):
        configfile = os.path.join(self.spiderdir, project, spider + '.yml')

        return os.path.isfile(configfile)

    def _iterate_project_folders(self, directory):
        for candidate in os.listdir(directory):
            if os.path.isdir(os.path.join(directory, candidate)) \
                    and candidate != '.git':

                yield candidate

    def _check_remote(self):
        p = subprocess.Popen(
            ['git', 'remote', '-v'],
            stdout=subprocess.PIPE,
            cwd=self.workdir)
        output, err = p.communicate()

        return self.repo_path in output.decode('utf-8')

    def _current_branch(self):
        p = subprocess.Popen(
            ['git', 'symbolic-ref', '--short', 'HEAD'],
            stdout=subprocess.PIPE,
            cwd=self.workdir)
        output, err = p.communicate()

        return output.decode('utf-8').strip()
