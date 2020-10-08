#!/usr/bin/env python

from onefuzz.api import Onefuzz
from onefuzz.backend import wait


def main():
    o = Onefuzz()

    build = o.info.get().versions["onefuzz"]

    def wait_func():
        info = o.info.get()

        return (
            info.versions["onefuzz"] != build,
            info.versions["onefuzz"].json(),
            None,
        )

    wait(wait_func)


if __name__ == "__main__":
    main()
