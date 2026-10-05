from ctypes import POINTER, cast

import comtypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

MIN_PERCENT = 0
MAX_PERCENT = 100


def _endpoint_volume():
    try:
        comtypes.CoInitialize()
    except OSError:
        pass  # поток уже инициализирован
    speakers = AudioUtilities.GetSpeakers()
    if hasattr(speakers, "EndpointVolume"):  # новые версии pycaw
        return speakers.EndpointVolume
    interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


def get_volume_percent() -> int:
    return round(_endpoint_volume().GetMasterVolumeLevelScalar() * 100)


def set_volume_percent(percent: int) -> int:
    clamped = max(MIN_PERCENT, min(MAX_PERCENT, percent))
    _endpoint_volume().SetMasterVolumeLevelScalar(clamped / 100, None)
    return clamped


def set_muted(muted: bool) -> None:
    _endpoint_volume().SetMute(int(muted), None)
