#!/usr/bin/env python

import argparse
from os import environ

import requests
from github import Github


class Deployer:
    def __init__(self):
        self.gh = Github(login_or_token=environ["GITHUB_ISSUE_TOKEN"])
        self.repo = self.gh.get_repo("microsoft/onefuzz")
        self.ci = self.repo.get_workflow("ci.yml")

    def get_artifact(self, branch, name, filename):
        zip_file_url = self.get_artifact_url(branch, name)

        (code, resp, _) = self.gh._Github__requester.requestBlob(
            "GET", zip_file_url, {}
        )
        if code != 302:
            raise Exception("unexpected response: %s" % resp)

        with open(filename, "wb") as handle:
            for chunk in requests.get(resp["location"], stream=True).iter_content(
                chunk_size=1024 * 16
            ):
                handle.write(chunk)

    def get_artifact_url(self, branch, name) -> str:
        for run in self.ci.get_runs(branch=branch, status="completed"):
            response = requests.get(run.artifacts_url).json()
            for artifact in response["artifacts"]:
                if artifact["name"] == name:
                    return artifact["archive_download_url"]
        raise Exception(f"no archive url for {branch} - {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("branch")
    parser.add_argument("filename")
    args = parser.parse_args()

    d = Deployer()
    d.get_artifact(args.branch, "release-artifacts", args.filename)


if __name__ == "__main__":
    main()
