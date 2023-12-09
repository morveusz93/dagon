def get_playback_url(info):
    formats = [
        x for x in info["formats"] if x["resolution"].lower() == "audio only"
    ]
    defaults = [d for d in formats if "medium" in d["format"]]
    if not defaults:
        defaults = [d for d in formats if d.get("format_note") == "Default"]
    if not defaults:
        defaults = formats
    try:
        return defaults[0].get("url")
    except KeyError:
        print("No playback found,", info)
