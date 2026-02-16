import subprocess


class distInfo:
    '''distInfo is a python object that contains utility data about a git repo.

    This utility information is useful for version tagging and passing additional resource
    data along to any automation services that are running on top of TD automation repos.
    '''

    def __init__(self):
        self.commit: str
        self.semver: str
        self.major: str
        self.minor: str
        self.patch: str
        self.branch: str
        self.remoteOrigin: str
        self.remoteSource: str

        self._updateVersionInfo()
        self._updateRemoteInfo()

    def _updateRemoteInfo(self) -> None:
        '''Pulls info about the remote URL directly from git.

        remoteOrigin will contain the the https prefix
        remoteSource has both the https prefix and .git suffix stripped out
        '''

        git_branch_process = subprocess.run(
            "git remote get-url origin", shell=True, capture_output=True)
        remote = str(git_branch_process.stdout, 'utf-8').strip()
        print(remote)

        # TODO check to see if remote ends in .git - remove this if it exists, otherwise leave it
        self.remoteOrigin = remote
        self.remoteSource = remote[8:]

    def _updateVersionInfo(self) -> None:
        '''Pulls version info from the latest version tag off of the repo itself
        '''

        # 1. Get the latest tag name (matching your vX.Y pattern)
        # Using the same logic as your GitHub Action
        tag_cmd = ['git', 'describe', '--tags', '--abbrev=0', '--match', 'v[0-9]*.[0-9]*']
        latest_tag = subprocess.check_output(tag_cmd, text=True).strip()

        major_minor_patch = latest_tag.split('.')
        major_minor = '.'.join([major_minor_patch[0], major_minor_patch[1]])        

        # 2. Get the count of commits from that tag to the current HEAD
        count_cmd = ['git', 'rev-list', '--count', f'{major_minor}..HEAD']
        num_commits = subprocess.check_output(count_cmd, text=True).strip()

        # get the branch
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
            text=True).strip()

        commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], text=True).strip()

        semver = f"{major_minor}.{num_commits}"
        print(f'semver logged as {semver}')

        self.commit = commit
        self.semver = semver
        self.major = major_minor_patch[0].strip('v')
        self.minor = major_minor_patch[1]
        self.patch = num_commits
        self.branch = branch

    @property
    def asDict(self) -> dict:
        '''Returns the info object as a dictionary'''

        info_dict = {
            "commit": self.commit,
            "semver": self.semver,
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "branch": self.branch,
            "remoteUrl": self.remoteOrigin
        }

        return info_dict

# if __name__ == __name__:
#     print(distInfo().asDict)
