# ArchCraftsman, The careful yet very fast Arch Linux Craftsman.
# Copyright (C) 2023 Rawleenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Test the utils module.
"""
import unittest
import unittest.mock

import archcraftsman.options
import archcraftsman.utils


class TestUtils(unittest.TestCase):
    """
    Test the utils module.
    """

    def test_generate_translations(self):
        """
        Test the generate_translations function.
        """
        with unittest.mock.patch("archcraftsman.base.execute") as mock_execute:
            archcraftsman.utils.generate_translations(
                archcraftsman.options.Languages.FRENCH
            )
            mock_execute.assert_called()

    def test_generate_translations_with_invalid_language(self):
        """
        Test the generate_translations function with an invalid language.
        """
        with unittest.mock.patch("archcraftsman.base.execute") as mock_execute:
            archcraftsman.utils.generate_translations("invalid")
            mock_execute.assert_not_called()

    def test_to_iec(self):
        """
        Test the to_iec function.
        """
        self.assertEqual(archcraftsman.utils.to_iec(10240), "10K")

    def test_to_iec_with_negative_value(self):
        """
        Test the to_iec function with a negative value.
        """
        self.assertEqual(archcraftsman.utils.to_iec(-1), "")

    def test_from_iec(self):
        """
        Test the from_iec function.
        """
        self.assertEqual(archcraftsman.utils.from_iec("1K"), 1024)

    def test_from_iec_with_invalid_value(self):
        """
        Test the from_iec function with an invalid value.
        """
        self.assertEqual(archcraftsman.utils.from_iec("invalid"), 0)

    def test_from_iec_with_negative_value(self):
        """
        Test the from_iec function with a negative value.
        """
        self.assertEqual(archcraftsman.utils.from_iec("-1K"), 0)

    def test_print_supported(self):
        """
        Test the print_supported function.
        """
        with (
            unittest.mock.patch("archcraftsman.base.print_step") as mock_print_step,
            unittest.mock.patch(
                "archcraftsman.base.print_sub_step"
            ) as mock_print_sub_step,
        ):
            archcraftsman.utils.print_supported("test", ["test1", "test2"], "test1")
            mock_print_step.assert_called()
            mock_print_sub_step.assert_called()
