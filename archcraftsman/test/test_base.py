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
import io
import subprocess
import unittest.mock

import archcraftsman.base


class TestBase(unittest.TestCase):
    """
    Tests for the base module.
    """

    @unittest.mock.patch("glob.glob", return_value=["toto", "tata", "titi"])
    @unittest.mock.patch("os.path.isdir", return_value=False)
    def test_glob_completer_first(self, _mock_glob, _mock_isdir):
        """
        Test the glob completer.
        """
        self.assertEqual(archcraftsman.base.glob_completer("t", 0), "toto")

    @unittest.mock.patch("glob.glob", return_value=["toto", "tata", "titi"])
    @unittest.mock.patch("os.path.isdir", return_value=False)
    def test_glob_completer_second(self, _mock_glob, _mock_isdir):
        """
        Test the glob completer.
        """
        self.assertEqual(archcraftsman.base.glob_completer("t", 1), "tata")

    @unittest.mock.patch("glob.glob", return_value=["toto", "tata", "titi"])
    @unittest.mock.patch("os.path.isdir", return_value=False)
    def test_glob_completer_third(self, _mock_glob, _mock_isdir):
        """
        Test the glob completer.
        """
        self.assertEqual(archcraftsman.base.glob_completer("t", 2), "titi")

    @unittest.mock.patch("os.path.exists", return_value=False)
    def test_is_bios(self, _mock_is_bios):
        """
        Test the is_bios function.
        """
        self.assertTrue(archcraftsman.base.is_bios())

    def test_execute(self):
        """
        Test the execute function.
        """
        with unittest.mock.patch("subprocess.run") as mock_subprocess_run:
            mock_subprocess_run.side_effect = [
                subprocess.CompletedProcess(args="echo A", returncode=0, stdout=b"A"),
                subprocess.CompletedProcess(args="echo B", returncode=0, stdout=b"B"),
                subprocess.CompletedProcess(
                    args="arch-chroot /mnt /bin/bash <<END\necho C\nEND",
                    returncode=0,
                    stdout=b"C",
                ),
                subprocess.CompletedProcess(args="echo D", returncode=0, stdout=b"D"),
                subprocess.CompletedProcess(args="echo E", returncode=0, stdout=b"E"),
            ]
            result1 = archcraftsman.base.execute("echo A")
            result2 = archcraftsman.base.execute("echo B")
            result3 = archcraftsman.base.execute("echo C", chroot=True)
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
            self.assertEqual(result3.output, "C")
            self.assertEqual(result3.returncode, 0)
            self.assertEqual(
                result3.command,
                "arch-chroot /mnt /bin/bash <<END\necho C\nEND",
            )
            with (
                unittest.mock.patch(
                    "sys.stdout", new_callable=io.StringIO
                ) as mock_stdout,
                unittest.mock.patch("archcraftsman.arguments.test", return_value=True),
            ):
                archcraftsman.base.execute("echo D")
                self.assertTrue(mock_stdout.getvalue())
            with (
                unittest.mock.patch(
                    "archcraftsman.base.sudo_exist", return_value=False
                ),
                unittest.mock.patch("archcraftsman.base.is_root", return_value=False),
            ):
                self.assertRaises(
                    PermissionError,
                    lambda: archcraftsman.base.execute("echo E", sudo=True),
                )
            with (
                unittest.mock.patch("archcraftsman.base.sudo_exist", return_value=True),
                unittest.mock.patch("archcraftsman.base.is_root", return_value=False),
            ):
                self.assertTrue(
                    "sudo" in archcraftsman.base.execute("echo E", sudo=True).command
                )

    @unittest.mock.patch(
        "archcraftsman.base.execute",
        return_value=archcraftsman.base.ExecutionResult(
            "whoami",
            subprocess.CompletedProcess(args="whoami", returncode=0, stdout=b"root"),
        ),
    )
    def test_is_root(self, _mock_is_root):
        """
        Test the is_root function.
        """
        self.assertTrue(archcraftsman.base.is_root())

    @unittest.mock.patch(
        "archcraftsman.base.execute",
        return_value=archcraftsman.base.ExecutionResult(
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
        self.assertTrue(archcraftsman.base.sudo_exist())

    @unittest.mock.patch("archcraftsman.base.execute")
    def test_evelate(self, _mock_execute):
        """
        Test the elevate function.
        """
        with unittest.mock.patch("archcraftsman.base.is_root", return_value=True):
            self.assertTrue(archcraftsman.base.elevate())
        with unittest.mock.patch("archcraftsman.base.sudo_exist", return_value=True):
            self.assertTrue(archcraftsman.base.elevate())
        with (
            unittest.mock.patch("archcraftsman.base.is_root", return_value=False),
            unittest.mock.patch("archcraftsman.base.sudo_exist", return_value=False),
        ):
            self.assertFalse(archcraftsman.base.elevate())

    @unittest.mock.patch("archcraftsman.base.execute")
    def test_pause(
        self,
        _mock_execute,
    ):
        """
        Test the pause function.
        """
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            archcraftsman.base.pause()
            self.assertEqual(
                mock_stdout.getvalue(),
                f"{archcraftsman.base.ORANGE}Press any key to continue...{archcraftsman.base.NOCOLOR}\n",
            )

        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            archcraftsman.base.pause(start_newline=True)
            self.assertEqual(
                mock_stdout.getvalue(),
                f"\n{archcraftsman.base.ORANGE}Press any key to continue...{archcraftsman.base.NOCOLOR}\n",
            )

        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            archcraftsman.base.pause(end_newline=True)
            self.assertEqual(
                mock_stdout.getvalue(),
                f"{archcraftsman.base.ORANGE}Press any key to continue...{archcraftsman.base.NOCOLOR}\n\n",
            )

    @unittest.mock.patch("archcraftsman.base.pause")
    def test_print_error(self, _mock_pause):
        """
        Test the print_error function.
        """
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            archcraftsman.base.print_error("Error")
            self.assertEqual(
                mock_stdout.getvalue(),
                f"\n{archcraftsman.base.RED}  /!\\ Error{archcraftsman.base.NOCOLOR}\n\n",
            )

    @unittest.mock.patch("archcraftsman.base.execute")
    def test_print_step(self, _mock_execute):
        """
        Test the print_step function.
        """
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            archcraftsman.base.print_step("Step")
            self.assertEqual(
                mock_stdout.getvalue(),
                f"\n{archcraftsman.base.GREEN}Step{archcraftsman.base.NOCOLOR}\n",
            )

    @unittest.mock.patch("archcraftsman.base.execute")
    def test_print_sub_step(self, _mock_execute):
        """
        Test the print_sub_step function.
        """
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            archcraftsman.base.print_sub_step("Sub step")
            self.assertEqual(
                mock_stdout.getvalue(),
                f"{archcraftsman.base.CYAN}  * Sub step{archcraftsman.base.NOCOLOR}\n",
            )

    @unittest.mock.patch("archcraftsman.arguments.test", return_value=True)
    def test_log(self, _mock_test):
        """
        Test the log function.
        """
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            archcraftsman.base.log("Log")
            self.assertEqual(
                mock_stdout.getvalue(),
                f"{archcraftsman.base.GRAY}> Log{archcraftsman.base.NOCOLOR}\n",
            )

    @unittest.mock.patch("archcraftsman.base.pause")
    def test_print_help(self, _mock_pause):
        """
        Test the print_help function.
        """
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            archcraftsman.base.print_help("Test message", do_pause=True)
            self.assertEqual(
                mock_stdout.getvalue(),
                f"\n{archcraftsman.base.GREEN}Help :{archcraftsman.base.NOCOLOR}\n{archcraftsman.base.CYAN}  "
                f"* Test message{archcraftsman.base.NOCOLOR}\n",
            )

    def test_input_str(self):
        """
        Test the input_str function.
        """
        with unittest.mock.patch("archcraftsman.base.input", return_value="toto"):
            self.assertEqual(archcraftsman.base.input_str("Enter:"), "toto")
        with unittest.mock.patch(
            "archcraftsman.base.getpass.getpass", return_value="titi"
        ):
            self.assertEqual(
                archcraftsman.base.input_str("Enter:", password=True), "titi"
            )

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    @unittest.mock.patch("archcraftsman.base.pause")
    def test_prompt(self, _mock_pause, _mock_stdout):
        """
        Test the prompt function.
        """
        with unittest.mock.patch("archcraftsman.base.input_str") as mock_input:
            mock_input.return_value = "Titi"
            self.assertEqual(
                archcraftsman.base.prompt("Enter:", default="Toto", help_msg="Help"),
                "Titi",
            )
        with unittest.mock.patch("archcraftsman.base.input_str") as mock_input:
            mock_input.return_value = ""
            self.assertEqual(
                archcraftsman.base.prompt("Enter:", default="Toto", help_msg="Help"),
                "Toto",
            )
        with unittest.mock.patch("archcraftsman.base.input_str") as mock_input:
            mock_input.side_effect = ["?", ""]
            self.assertEqual(
                archcraftsman.base.prompt("Enter:", default="Toto", help_msg="Help"),
                "Toto",
            )
        with unittest.mock.patch("archcraftsman.base.input_str") as mock_input:
            mock_input.side_effect = ["", "Tata"]
            self.assertEqual(
                archcraftsman.base.prompt("Enter:", help_msg="Help", required=True),
                "Tata",
            )

    def test_prompt_ln(self):
        """
        Test the prompt_ln function.
        """
        with unittest.mock.patch("archcraftsman.base.prompt", return_value="Titi"):
            self.assertEqual(
                archcraftsman.base.prompt_ln("Enter:", default="Toto", help_msg="Help"),
                "Titi",
            )

    def test_prompt_password(self):
        """
        Test the prompt_password function.
        """
        with unittest.mock.patch("archcraftsman.base.prompt", return_value="Titi"):
            self.assertEqual(archcraftsman.base.prompt_passwd("Enter:"), "Titi")
