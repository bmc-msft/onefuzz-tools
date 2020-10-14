#!/usr/bin/env python

import argparse
import subprocess
import tempfile
from os import environ
import os

import requests
from github import Github


class Downloader:
    def __init__(self):
        self.gh = Github(login_or_token=environ["GITHUB_ISSUE_TOKEN"])

    def get_artifact(
        self, repo: str, workflow: str, branch: str, name: str, filename: str
    ) -> None:
        print(f"getting {name}")
        zip_file_url = self.get_artifact_url(repo, workflow, branch, name)

        (code, resp, _) = self.gh._Github__requester.requestBlob(
            "GET", zip_file_url, {}
        )
        if code != 302:
            raise Exception(f"unexpected response: {resp}")

        with open(filename, "wb") as handle:
            for chunk in requests.get(resp["location"], stream=True).iter_content(
                chunk_size=1024 * 16
            ):
                handle.write(chunk)

    def get_artifact_url(
        self, repo_name: str, workflow_name: str, branch: str, name: str
    ) -> str:
        repo = self.gh.get_repo(repo_name)
        workflow = repo.get_workflow(workflow_name)

        for run in workflow.get_runs(branch=branch, status="completed"):
            response = requests.get(run.artifacts_url).json()
            for artifact in response["artifacts"]:
                if artifact["name"] == name:
                    return artifact["archive_download_url"]
        raise Exception(f"no archive url for {branch} - {name}")


class Deployer:
    def __init__(self, *, branch: str, instance: str, region: str):
        self.downloader = Downloader()
        self.branch = branch
        self.instance = instance
        self.region = region

    def deploy(self, filename: str) -> None:
        print(f"deploying {filename} to {self.instance}")

        venv = "deploy-venv"
        commands = [
            f"unzip {filename}",
            "unzip onefuzz-deployment*.zip",
            f"python -mvenv {venv}",
            f"./{venv}/bin/pip install wheel",
            f"./{venv}/bin/pip install -r requirements.txt",
            (
                f"./{venv}/bin/python deploy.py {self.region} "
                f"{self.instance} {self.instance} cicd"
            ),
        ]
        for cmd in commands:
            subprocess.check_call(cmd, shell=True)

    def test(self) -> None:
        venv = "test-venv"
        script = "~/projects/onefuzz/onefuzz/src/cli/examples/integration-test.py"
        inputs = "/home/bcaswell/projects/onefuzz/built-samples/"
        endpoint = f"https://{self.instance}.azurewebsites.net"
        commands = [
            f"python -mvenv {venv}",
            f"./{venv}/bin/pip install wheel",
            f"./{venv}/bin/pip install sdk/*.whl",
            (
                f"./{venv}/bin/python {script} test {inputs} "
                f"--region {self.region} --endpoint {endpoint}"
            ),
        ]
        for cmd in commands:
            subprocess.check_call(cmd, shell=True)

    def cleanup(self) -> None:
        subprocess.check_call(["az", "group", "delete", "-n", self.instance, "--yes"])

    def run(self) -> None:
        dist = "onefuzz.zip"
        self.downloader.get_artifact(
            "microsoft/onefuzz", "ci.yml", self.branch, "release-artifacts", dist
        )
        self.deploy(dist)
        self.test()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("branch")
    parser.add_argument("instance")
    parser.add_argument("--region", default="eastus2")
    parser.add_argument("--skip_cleanup", action="store_true")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as directory:
        os.chdir(directory)
        print(f"running from within {directory}")

        d = Deployer(branch=args.branch, instance=args.instance, region=args.region)
        try:
            d.run()
        finally:
            if not args.skip_cleanup:
                d.cleanup()


if __name__ == "__main__":
    main()
