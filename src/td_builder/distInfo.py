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

        # grab git information...
        git_branch_process = subprocess.run(
            "git rev-parse --abbrev-ref HEAD", shell=True, capture_output=True)
        branch = str(git_branch_process.stdout, 'utf-8').strip()
        # replace any / characters from branch
        branch = branch.replace("/", "-")
        git_tag_process = subprocess.run(
            "git describe --tags", shell=True, capture_output=True)
        last_full_tag = str(git_tag_process.stdout, 'utf-8').strip()

        tag_parts = last_full_tag.split('-')
        major_minor = tag_parts[0]
        major = major_minor.split('.')[0][1:]
        minor = major_minor.split('.')[1]

        num_commits = "0"

        current_commit_hash = None

        if len(major_minor.split('.')) > 2:
            num_commits = major_minor.split('.')[2]

        semver = f"{major_minor}.{num_commits}"

        if branch != "main":
            if current_commit_hash is not None:
                semver = f"{semver}+{branch}-{current_commit_hash}"

            else:
                semver = f"{semver}+{branch}"

        self.commit = "unknown" if current_commit_hash == None else current_commit_hash
        self.semver = semver
        self.major = major
        self.minor = minor
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
