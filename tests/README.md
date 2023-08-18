# Testing Documentation
***
Created by [Alejandro Ciuba](https://alejandrociuba.github.io), alc307@pitt.edu
***
## Introduction
This subdirectory contains the entire test suite needed to more properly test the `elan_data` Python package and is needed to contribute to the project in the future. The required development modules are as follows:

- `flake8>=5.0.4`
- `tox>=4.7.0`
- `pytest>=7.4.0`
- `pytest-cov>=4.1.0`
- `pytest-mock>=3.11.1`
- `pytest-lazy-fixture>=0.6.3`
- `mypy>=1.4.1`

All of which can be downloaded through `pip install -r requirements-dev.txt`

To run, use either `pytest [optional args]` or the premade `run-checks.sh` script in the main directory.
***
## Directory
### Folders
- `created/`: Contains any files/folders created during the testing process. None of these *should* be necessary to run tests beforehand.
- `keys/`: Contains the "answer key" files needed to compare outputs for various methods and functions.
### Files
- `__init__.py`: Literally nothing, it's just sort of there.
- `conftest.py`: Stores all fixtures needed to run test suites.
- `old_tests.py`: Tests which were originally ran in the (deprecated) `if __name__ == "__main__"` statement in each module of the `elan_data` package. Kept for future reference.
- `README.md`: This thing that you are reading now!
#### Test Suites
- `test_elan_data.py`: Test functionality in the main `elan_data` (`__init__.py`) module.
- `test_elan_utils.py`: Test functionality in the `elan_data.elan_utils` module.

**NOTE:** Other files will get created during the testing process (e.g. `test_writing.wav`) these are created as a consequence of the behavior of certain packages, functions, or methods and are *not* necessary to run the tests.
