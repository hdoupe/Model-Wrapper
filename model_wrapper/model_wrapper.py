import subprocess as sp
import os
import time
import argparse


def proc_lite(cmd, logfile=None, wait=True):
    """
    Run commandline instructions
    TODO: add logging
    """
    print("running", cmd)
    proc = sp.Popen([cmd], shell=True)
    if wait is False:
        return None
    proc.wait()
    assert proc.poll() == 0


def put(pem, ip, logfile, local, rmt, aws_pref='ubuntu', wait=True):
    """
    Use scp to copy local file to node
    """
    proc_lite(
        'scp -i {} {} {}@{}:{}'.format(pem, os.path.abspath(local),
                                       aws_pref, ip, rmt),
        logfile,
        wait=wait
    )


def run(pem, ip, logfile, cmd, aws_pref='ubuntu', wait=True):
    """
    ssh into node and run cmd
    """
    proc_lite('ssh -i {} {}@{} "{}"'.format(pem, aws_pref, ip, cmd), logfile,
              wait=wait)


def get_repo(handle, repo, branch, remote, logfile):
    """
    Clone repo, checkout branch, and zip repo (excluding .git files)
    """
    proc_lite("git clone https://github.com/{}/{}".format(handle, repo))
    fetch = "git fetch"
    checkout = "git checkout -b {} {}/{}".format(branch, remote, branch)
    proc_lite("cd {} && {} && {}".format(repo, fetch, checkout))
    proc_lite("zip -r {}.zip {} -x *.git*".format(repo, repo, repo))


def wrap_model(handle, repo, branch, remote, logfile, pem, ip):
    """
    This function performs the high level logic of running the model.
        1. Get the GitHub repo
        2. Send the zipped repo to the AWS node
        3. Setup environment in the node
        4. Run the model
    """
    # get github repo
    get_repo(handle, repo, branch, remote, logfile)

    rmt_dir = "/home/ubuntu/"
    rmt_zip = os.path.join(rmt_dir, "{}.zip".format(repo))
    rmt_ogusa = os.path.join(rmt_dir, repo)
    local = "{}.zip".format(repo)
    # copy zipped repo to AWS box and unzip
    put(pem, ip, logfile, local, rmt_dir)
    run(pem, ip, logfile, "unzip {}".format(rmt_zip))

    # set up environment according to env_setup.sh
    put(pem, ip, logfile, "./env_setup.sh", rmt_ogusa)
    run(pem, ip, logfile, "cd {} && ./env_setup.sh".format(rmt_ogusa))

    # run model according to run_model.sh
    put(pem, ip, logfile, "./run_model.sh", rmt_dir)
    run(pem, ip, logfile, "./run_model.sh", wait=False)


if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("--handle", default=None, help="Github handle")
    parser.add_argument("--repo", default=None, help="Github repo name")
    parser.add_argument("--branch", default=None, help="Github branch")
    parser.add_argument("--remote", default=None, help="Github remote")
    parser.add_argument("--logfile", default=None, help="File for output")
    parser.add_argument("--pem", default=None, help="Path to AWS pem file")
    parser.add_argument("--ip", default=None, help="IP for node")
    args = parser.parse_args()

    # read arguments from commandline or get from envrionement
    handle = args.handle or os.environ.get("HANDLE")
    repo = args.repo or os.environ.get("REPO")
    branch = args.branch or os.environ.get("BRANCH")
    remote = args.remote or os.environ.get("REMOTE")
    logfile = args.logfile or os.environ.get("LOGFILE")
    pem = args.pem or os.environ.get("PEM")
    ip = args.ip or os.environ.get("IP")

    wrap_model(handle, repo, branch, remote, logfile, pem, ip)
