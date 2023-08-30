# ELAN Data
***
Created by [Alejandro Ciuba](https://alejandrociuba.github.io), alc307@pitt.edu through the Computational Sociolinguistics Laboratory at the University of Pittsburgh, under the direction of Dr. Dan Villarreal.
***
## Summary

Repository for the `elan_data` python package, a useful tool which allows anyone to create, edit, and explore the (meta) data of *ELAN* transcription files (`*.eaf` extension). 

### Example Code

```python
from elan_data import ELAN_Data

if __name__ == "__main__":

    # Either load an .eaf file or create one and edit it via code
    eaf = ELAN_Data.from_file("your/file/here.eaf")

    print(eaf)

    new_eaf = ELAN_Data.create_eaf("new.eaf", audio="optional.wav",
                                   tiers=["multiple", "tier", "support"],
                                   remove_default=True)

    new_eaf.add_segment("tier", start=500, stop=1500,
                        annotation="adding tiers, segments, and metadata is easy!")

    # All tier information is stored neatly in a premade pd.DataFrame
    print(new_eaf.tier_data)

    # Don't forget to save your work!
    new_eaf.save_ELAN()
```
***
## Introduction

The `elan_data` package comes with the main `ELAN_Data` object as well as several helper functions contained within `elan_utils`. The requirements to run the package are as follows:

### Requirements

- `Python 3.7.16-3.10.*`
- `pandas>=1.3.5`
- `numpy>=1.21.6`
- `matplotlib>=3.5.0`

### Installation

Currently, this package is unavaible via the *Python Package Index* (`PyPi`); therefore:

1. Clone this repository locally via `git clone git@github.com:AlejandroCiuba/elan_data.git` or your own fork.
2. Navigate to the top of the git repository.
3. (Ideally through a `conda` and/or `venv` environment) Run: `pip install -e .` to create a local, editable install.
