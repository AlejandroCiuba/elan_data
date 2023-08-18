# Helper functions for tests in all units
# Created by Alejandro Ciuba, alc307@pitt.edu
from pathlib import Path
from typing import Union

import filecmp


def compare_to_key(ans: Union[str, Path], key: Path) -> bool:
    """
    Compare the created file to the key.rttm file.
    """
    filecmp.clear_cache()
    return filecmp.cmp(ans, key)
