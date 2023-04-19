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
Tests for the base module.
"""
import subprocess
import unittest
from io import StringIO
from unittest.mock import patch

from archcraftsman.base import (
    CYAN,
    GRAY,
    GREEN,
    NOCOLOR,
    ORANGE,
    RED,
    ExecutionResult,
    elevate,
    execute,
    glob_completer,
    input_str,
    is_bios,
    is_root,
    log,
    pause,
    print_error,
    print_help,
    print_step,
    print_sub_step,
    prompt,
    prompt_ln,
    prompt_passwd,
    sudo_exist,
)


class TestBase(unittest.TestCase):
    """
    Tests for the base module.
    """

    @patch("glob.glob", return_value=["toto", "tata", "titi"])
    @patch("os.path.isdir", return_value=False)
    def test_glob_completer_first(self, _mock_glob, _mock_isdir):
        """
        Test the glob completer.
        """
        self.assertEqual(glob_completer("t", 0), "toto")

    @patch("glob.glob", return_value=["toto", "tata", "titi"])
    @patch("os.path.isdir", return_value=False)
    def test_glob_completer_second(self, _mock_glob, _mock_isdir):
        """
        Test the glob completer.
        """
        self.assertEqual(glob_completer("t", 1), "tata")

    @patch("glob.glob", return_value=["toto", "tata", "titi"])
    @patch("os.path.isdir", return_value=False)
    def test_glob_completer_third(self, _mock_glob, _mock_isdir):
        """
        Test the glob completer.
        """
        self.assertEqual(glob_completer("t", 2), "titi")

    @patch("os.path.exists", return_value=False)
    def test_is_bios(self, _mock_is_bios):
        """
        Test the is_bios function.
        """
        self.assertTrue(is_bios())

    def test_execute(self):
        """
        Test the execute function.
        """
        with patch("subprocess.run") as mock_subprocess_run:
            mock_subprocess_run.side_effect = [
                subprocess.CompletedProcess(args="echo A", returncode=0, stdout=b"A"),
                subprocess.CompletedProcess(args="echo B", returncode=0, stdout=b"B"),
                subprocess.CompletedProcess(args="echo C", returncode=0, stdout=b"C"),
                subprocess.CompletedProcess(args="echo D", returncode=0, stdout=b"D"),
            ]
            result1 = execute("echo A")
            result2 = execute("echo B")
            self.assertEqual(result1.command, "echo A")
            self.assertEqual(result1.returncode, 0)
            self.assertEqual(result1.output, "A")
            self.assertTrue(bool(result1))
            self.assertEqual(str(result1), "A")
            self.assertEqual(repr(result1), "A")
            self.assertFalse(result1 == result2)
            self.assertTrue(result1 != result2)
            self.assertEqual(
                hash(result1),
                hash(result1.command) ^ hash(result1.returncode) ^ hash(result1.output),
            )
            with (
                patch("sys.stdout", new_callable=StringIO) as mock_stdout,
                patch("archcraftsman.arguments.test", return_value=True),
            ):
                execute("echo C")
                self.assertTrue(mock_stdout.getvalue())
            with (
                patch("archcraftsman.base.sudo_exist", return_value=False),
                patch("archcraftsman.base.is_root", return_value=False),
            ):
                self.assertRaises(PermissionError, lambda: execute("echo D", sudo=True))
            with (
                patch("archcraftsman.base.sudo_exist", return_value=True),
                patch("archcraftsman.base.is_root", return_value=False),
            ):
                self.assertTrue("sudo" in execute("echo D", sudo=True).command)

    @patch(
        "archcraftsman.base.execute",
        return_value=ExecutionResult(
            "whoami",
            subprocess.CompletedProcess(args="whoami", returncode=0, stdout=b"root"),
        ),
    )
    def test_is_root(self, _mock_is_root):
        """
        Test the is_root function.
        """
        self.assertTrue(is_root())

    @patch(
        "archcraftsman.base.execute",
        return_value=ExecutionResult(
            "which sudo",
            subprocess.CompletedProcess(
                args="which sudo", returncode=0, stdout=b"/usr/bin/sudo"
            ),
        ),
    )
    def tests_sudo_exist(self, _mock_sudo_exist):
        """
        Test the sudo_exist function.
        """
        self.assertTrue(sudo_exist())

    @patch("archcraftsman.base.execute")
    def test_evelate(self, _mock_execute):
        """
        Test the elevate function.
        """
        with patch("archcraftsman.base.is_root", return_value=True):
            self.assertTrue(elevate())
        with patch("archcraftsman.base.sudo_exist", return_value=True):
            self.assertTrue(elevate())
        with (
            patch("archcraftsman.base.is_root", return_value=False),
            patch("archcraftsman.base.sudo_exist", return_value=False),
        ):
            self.assertFalse(elevate())

    @patch("archcraftsman.base.execute")
    def test_pause(
        self,
        _mock_execute,
    ):
        """
        Test the pause function.
        """
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            pause()
            self.assertEqual(
                mock_stdout.getvalue(),
                f"{ORANGE}Press any key to continue...{NOCOLOR}\n",
            )

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            pause(start_newline=True)
            self.assertEqual(
                mock_stdout.getvalue(),
                f"\n{ORANGE}Press any key to continue...{NOCOLOR}\n",
            )

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            pause(end_newline=True)
            self.assertEqual(
                mock_stdout.getvalue(),
                f"{ORANGE}Press any key to continue...{NOCOLOR}\n\n",
            )

    @patch("archcraftsman.base.pause")
    def test_print_error(self, _mock_pause):
        """
        Test the print_error function.
        """
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            print_error("Error")
            self.assertEqual(
                mock_stdout.getvalue(),
                f"\n{RED}  /!\\ Error{NOCOLOR}\n\n",
            )

    @patch("archcraftsman.base.execute")
    def test_print_step(self, _mock_execute):
        """
        Test the print_step function.
        """
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            print_step("Step")
            self.assertEqual(
                mock_stdout.getvalue(),
                f"\n{GREEN}Step{NOCOLOR}\n",
            )

    @patch("archcraftsman.base.execute")
    def test_print_sub_step(self, _mock_execute):
        """
        Test the print_sub_step function.
        """
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            print_sub_step("Sub step")
            self.assertEqual(
                mock_stdout.getvalue(),
                f"{CYAN}  * Sub step{NOCOLOR}\n",
            )

    @patch("archcraftsman.arguments.test", return_value=True)
    def test_log(self, _mock_test):
        """
        Test the log function.
        """
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            log("Log")
            self.assertEqual(mock_stdout.getvalue(), f"{GRAY}> Log{NOCOLOR}\n")

    @patch("archcraftsman.base.pause")
    def test_print_help(self, _mock_pause):
        """
        Test the print_help function.
        """
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            print_help("Test message", do_pause=True)
            self.assertEqual(
                mock_stdout.getvalue(),
                f"\n{GREEN}Help :{NOCOLOR}\n{CYAN}  * Test message{NOCOLOR}\n",
            )

    def test_input_str(self):
        """
        Test the input_str function.
        """
        with patch("archcraftsman.base.input", return_value="toto"):
            self.assertEqual(input_str("Enter:"), "toto")
        with patch("archcraftsman.base.getpass.getpass", return_value="titi"):
            self.assertEqual(input_str("Enter:", password=True), "titi")

    @patch("sys.stdout", new_callable=StringIO)
    @patch("archcraftsman.base.pause")
    def test_prompt(self, _mock_pause, _mock_stdout):
        """
        Test the prompt function.
        """
        with patch("archcraftsman.base.input_str") as mock_input:
            mock_input.return_value = "Titi"
            self.assertEqual(prompt("Enter:", default="Toto", help_msg="Help"), "Titi")
        with patch("archcraftsman.base.input_str") as mock_input:
            mock_input.return_value = ""
            self.assertEqual(prompt("Enter:", default="Toto", help_msg="Help"), "Toto")
        with patch("archcraftsman.base.input_str") as mock_input:
            mock_input.side_effect = ["?", ""]
            self.assertEqual(prompt("Enter:", default="Toto", help_msg="Help"), "Toto")
        with patch("archcraftsman.base.input_str") as mock_input:
            mock_input.side_effect = ["", "Tata"]
            self.assertEqual(prompt("Enter:", help_msg="Help", required=True), "Tata")

    def test_prompt_ln(self):
        """
        Test the prompt_ln function.
        """
        with patch("archcraftsman.base.prompt", return_value="Titi"):
            self.assertEqual(
                prompt_ln("Enter:", default="Toto", help_msg="Help"), "Titi"
            )

    def test_prompt_password(self):
        """
        Test the prompt_password function.
        """
        with patch("archcraftsman.base.prompt", return_value="Titi"):
            self.assertEqual(prompt_passwd("Enter:"), "Titi")
