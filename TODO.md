# TODO
***
## Summary

List of planned additions or interesting things that could be added in the future.

## Short-Term

- 1.7.*:
    - `elan_utils.audio_loader` and `elan_utils.sound_wave` will also take `ELAN_Data` and use its audio and filename.
        - Raises `TypeError` if either audio or filename do not exist.

    - Make `df_status = False` wipe the current `ELAN_Data.tier_data` `pd.DataFrame`.

    - Better refine the behavior of methods in `ELAN_Data` which have an optional `**kwargs` argument (i.e. what to do if an element is `None` or is not a viable attribute name).

    - Add `author` and `date` fields to `ELAN_Data` and appropriate logic if they are not available.

    - Add more information in the `ELAN_Data.tier_data` DataFrame.

    - Add more properties to `ELAN_Data` (e.g. `beginning` and `end` of audio, if available).

    - Make a `stop` time greater than the audio's stop time a `ValueError` for `ELAN_Data.add_segment()`.

## Long-Term

- Separate the `elan_data.ELAN_Data.tier_data` logic into its own class, `elan_data.Tier_Data` which inherits from `pd.DataFrame`.
    - Stricter control of editing the DataFrame.
    - More functionality since we'll know exactly what it can and cannot contain.
    - Decouple `pd.DataFrame` dependence from `elan_data.ELAN_Data` and make `elan_data.tier_data` completely optional.

- Add the option to *return* (*not yield*) an `np.ndarray` from `elan_data.elan_utils.audio_loader`.
