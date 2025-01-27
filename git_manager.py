import sys
import os
import re
import subprocess


class GitManager:
    def __init__(self):
        self.git = 'git'
        self.prefix = ''

    def run_git(self, args):
        plat = sys.platform
        cmd = [self.git] + args
        cwd = self.getcwd()
        if plat == "win32":
            # make sure console does not come up
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 cwd=cwd,startupinfo=startupinfo)
        else:
            my_env = os.environ.copy()
            my_env["PATH"] = "/usr/local/bin:/usr/bin:" + my_env["PATH"]
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 cwd=cwd,env=my_env)
        p.wait()
        stdoutdata, _ = p.communicate()
        return (p.returncode, stdoutdata.decode('utf-8'))

    def getcwd(self):
        f = self.filename
        cwd = None
        if f:
            cwd = os.path.dirname(f)
        return cwd

    def branch(self):
        (exit_code, output) = self.run_git(["status", "-u", "no"])
        if exit_code != 0:
            return ''
        m = re.search(r"(?:at|branch)\s(.*?)\n",output)
        return m.group(1)

    def is_dirty(self):
        (exit_code, output) = self.run_git(["diff-index", "--quiet", "HEAD"])
        
        return exit_code == 1

    def unpushed_info(self, branch):
        if branch:
            (exit_code, output) = self.run_git(['rev-list', '--left-right', '--count', f'master...{branch}'])
            m = re.search(r"(\d+)\s+(\d+)", output)
            return (int(m.group(1)), int(m.group(2)))
        return (0,0)

    def badge(self, filename):
        self.filename = filename
        if not self.filename:
            return ""

        branch = self.branch()
        if not branch:
            return ""
        ret = branch
        if self.is_dirty():
            ret = ret + "*"
        a, b = self.unpushed_info(branch)
        return f'{ret} ({a},{b})'

