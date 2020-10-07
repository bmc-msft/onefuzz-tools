#!/bin/bash

set -e

cd /home/bcaswell/projects/onefuzz/onefuzz/src/api-service/
eval $(direnv export bash)
black ./__app__ ./tests
mypy __app__ tests
flake8 __app__ tests
isort --profile black __app__ tests

cd /home/bcaswell/projects/onefuzz/onefuzz/src/cli
eval $(direnv export bash)
black ./onefuzz ./tests ./examples
isort --profile black onefuzz tests examples
mypy onefuzz tests examples
flake8 onefuzz tests examples

cd /home/bcaswell/projects/onefuzz/onefuzz/src/pytypes
eval $(direnv export bash)
black ./onefuzztypes
isort --profile black onefuzztypes
mypy onefuzztypes
flake8 onefuzztypes
