"""
The generic bundle blueprint module
"""
class Bundle:
    """
    A class to represent a bootloader.
    """
    name: str

    def __init__(self, name: str):
        self.name = name

    def packages(self, system_info: {}) -> [str]:  # pylint: disable=unused-argument
        """
        Bundle's packages retrieving method.
        """
        return []

    def prompt_extra(self):
        """
        Bundle's extra options prompting method.
        """

    def print_resume(self):
        """
        Bundle's print resume method.
        """

    def configure(self, system_info, pre_launch_info, partitioning_info):
        """
        Bundle configuration method.
        :param system_info:
        :param pre_launch_info:
        :param partitioning_info:
        """
