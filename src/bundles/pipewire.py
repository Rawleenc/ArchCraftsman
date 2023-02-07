"""
The pipewire bundle module
"""
from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.utils import print_sub_step

_ = I18n().gettext


class PipeWire(Bundle):
    """
    The PipeWire class.
    """

    def packages(self, system_info: dict[str, any]) -> list[str]:
        return ["pipewire", "pipewire-alsa", "pipewire-audio", "pipewire-jack", "pipewire-media-session",
                "pipewire-pulse", "pipewire-v4l2", "pipewire-x11-bell", "pipewire-zeroconf"]

    def print_resume(self):
        print_sub_step(_("Install PipeWire."))
