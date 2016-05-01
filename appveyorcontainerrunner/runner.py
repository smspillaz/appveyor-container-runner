# /appveyorcontainerrunner/runner.py
#
# The main runner script, opens appveyor.yml and then
# runs each command.
#
# See LICENCE.md for Copyright information

from contextlib import closing
import os
import subprocess
import tempfile
import yaml

_POWERSHELL_ONLY_ERROR = ("""appveyor-container-runner only works with """
                          """powershell commands.""")


def main():
    """Runs the appveyor.yml script."""

    with open("appveyor.yml", "r") as yaml_file:
        appveyor_yaml = yaml.load(yaml_file.read())

        commands = list()

        for section in ["install",
                        "before_build",
                        "after_build",
                        "before_test",
                        "test_script",
                        "after_test",
                        "on_finish"]:
            try:
                try:
                   section_list = appveyor_yaml[section]
                except KeyError:
                    continue

                commands += ([i["ps"] for i in section_list] or list())
            except KeyError:
                raise RuntimeError(_POWERSHELL_ONLY_ERROR)

        script_file_name = os.path.join(os.getcwd(), "build-script.ps1")

        with open(script_file_name, "wt") as script_file:
            for command in commands:
                script_file.write("{0}\n".format(command))

            script_file.flush()

        os.environ["APPVEYOR"] = "1"

        return subprocess.check_call(["powershell",
                                      "-ExecutionPolicy",
                                      "Bypass",
                                      os.path.basename(script_file.name)],
                                      env=os.environ)
