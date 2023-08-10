from elan_data import ELAN_Data
from elan_data.elan_utils import audio_loader, soundwave


def _main():

    obj = ELAN_Data.create_eaf("test.eaf", "test_recording.wav", ["test", "test_2"])

    transcription = "Hello - This is a test recording . for the ELAN Data Object ."
    obj.add_segment("test", 0, 6880, transcription)
    obj.add_segment("test_2", 400, 6580, transcription)

    df = obj.init_dataframe()

    obj.add_tier("THE FINAL TIER")

    print(obj)

    print("Filename:", obj.file.name)
    print(f"Tiers: {obj.tier_names}\n")

    print(obj.tier_data.info())

    print(f"\nTier Dataframe:\n{obj.tier_data}")

    print(f"\nFirst Row:\n{df.iloc[0]}")

    print(f"\nSegment 'a2' overlaps with:\n{obj.overlaps('a2', tiers=['test'])}")

    print(f"\nSegment 'a2' overlaps with (ignoring suprasegments):\n{obj.overlaps('a2', tiers=['test'], suprasegments=False)}")

    print(f"\nSegment 'a1' overlaps with (ignoring suprasegments):\n{obj.overlaps('a1', tiers=['test_2'], suprasegments=False)}")

    print(f"\nRemoving the second segment:\n{obj.get_segment('a2')}")
    obj.remove_segment("a2")

    print("Renaming tier")
    obj.rename_tier("test", "creator")

    print("Adding participant")
    obj.add_participant("creator", "Myself")

    print("\nAudio File Absolute Filepath:\n\t", obj.audio.absolute())
    print(f"\nInformation for {obj.audio.name}:")

    obj.tier_data["DURATION"] = obj.tier_data.STOP - obj.tier_data.START

    print(obj.tier_data)

    with audio_loader(obj, 'rb') as src:
        print("\tChannels:", src.getnchannels())
        print("\tSample Width:", src.getsampwidth())
        print("\tFrame Rate:", src.getframerate())
        print("\tNumber of Frames:", src.getnframes())
        print(f"\tDuration: {src.getnframes() / src.getframerate():.2f}")

    print(f"Length of .eaf: {len(obj)}") 

    fig = sound_wave(obj, blue=1, gold=2)
    plt.show()

    print("Splitting the segment in the creator tier into 4 parts")
    obj.split_segment([500, 3000, 6000], seg_id="a1")

    print(f"Length of .eaf after splitting: {len(obj)}")

    obj.save_ELAN()

if __name__ == '__main__':
    _main()
    