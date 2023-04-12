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
from unittest.mock import patch
from archcraftsman.options import Languages

from archcraftsman.utils import from_iec, generate_translations, print_supported, to_iec


class TestUtils(unittest.TestCase):
    """
    Test the utils module.
    """

    def test_generate_translations(self):
        """
        Test the generate_translations function.
        """
        with patch("archcraftsman.utils.execute") as mock_execute:
            generate_translations(Languages.FRENCH)
            mock_execute.assert_called()

    def test_generate_translations_with_invalid_language(self):
        """
        Test the generate_translations function with an invalid language.
        """
        with patch("archcraftsman.utils.execute") as mock_execute:
            generate_translations("invalid")
            mock_execute.assert_not_called()

    def test_to_iec(self):
        """
        Test the to_iec function.
        """
        self.assertEqual("1,0K", to_iec(1024))

    def test_to_iec_with_negative_value(self):
        """
        Test the to_iec function with a negative value.
        """
        self.assertEqual("", to_iec(-1))

    def test_from_iec(self):
        """
        Test the from_iec function.
        """
        self.assertEqual(1024, from_iec("1,0K"))

    def test_from_iec_with_invalid_value(self):
        """
        Test the from_iec function with an invalid value.
        """
        self.assertEqual(from_iec("invalid"), 0)

    def test_from_iec_with_negative_value(self):
        """
        Test the from_iec function with a negative value.
        """
        self.assertEqual(from_iec("-1,0K"), 0)

    def test_print_supported(self):
        """
        Test the print_supported function.
        """
        with (
            patch("archcraftsman.utils.print_step") as mock_print_step,
            patch("archcraftsman.utils.print_sub_step") as mock_print_sub_step,
        ):
            print_supported("test", ["test1", "test2"], "test1")
            mock_print_step.assert_called()
            mock_print_sub_step.assert_called()
