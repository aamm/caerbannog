#!/usr/bin/env python
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import fileinput
import subprocess
import re
import os

variable_reference_regex = re.compile(r"\$<(?P<var_name>[a-zA-Z_]+[a-zA-Z0-9_]*)>")
indentation_regex = re.compile(r"(?P<indent>\s*)")
shebangLine_regex = re.compile(r"\s*\#!")
shell_line_regex = re.compile(r"\s*\#")
comment_line_regex = re.compile(r"\s*\#\#")
empty_comment_at_end_of_line_regex = re.compile(r"\#\s*$")
script_file_name = "/tmp/caerbannog-" + str(os.getpid()) + ".py"


def convert_python_var_references(code_line):
    """ Converts a line of Python code into a set of lines that communicate with the Bash process to retrieve
    the values of referenced Bash variables through a named pipe.
    :param code_line: The line of Python code to be converted
    :return: The Python line with calls to Bash variables converted into communication with the Bash process
    """
    match = variable_reference_regex.search(code_line)
    while match:
        var_name = match.group('var_name')
        code_line = code_line[:match.start()] + "\" + str(" + var_name + ") + \"" + code_line[match.end():]
        match = variable_reference_regex.search(code_line)
    return code_line


def convert_bash_var_references(code_line):
    """ Converts a Bash line of code into one in which all references to Python variables were replaced with their
    values in the Python process.
    :param code_line: Line of Bash code to be converted
    :return: The line with additional code having references to Python variables replaced by their values
    """
    match = variable_reference_regex.search(code_line)
    variable_fetch_script = ""
    while match:
        var_name = match.group('var_name')
        indentation = indentation_regex.search(code_line).group('indent')
        variable_fetch_script += indentation + var_name + " = None\n"
        variable_fetch_script += indentation + "process.stdin.write(\"echo \\\"" + var_name + "=$" + var_name + "\\\" > \" + bash_to_p_fifo + \"\\n\")\n"
        variable_fetch_script += indentation + "bash_var_sem.acquire()\n"
        variable_fetch_script += indentation + var_name + " = bash_vars[\"" + var_name + "\"]\n"
        code_line = code_line[:match.start()] + "str(" + var_name + ")" + code_line[match.end():]
        match = variable_reference_regex.search(code_line)
    return variable_fetch_script + code_line

inside_nested_python = False
nested_python_script = ""
callback_index = 0
callback_function_name = ""

first_line = True

with open(script_file_name, "w") as script_file:
    script_file.write("# Automatically generated script.\n")
    script_file.write("# If you edit it, you waste your time.\n")
    script_file.write("import subprocess\n")
    script_file.write("import os\n")
    script_file.write("import time\n")
    script_file.write("import thread\n")
    script_file.write("import threading\n")
    script_file.write("import sys\n")
    script_file.write("import re\n")
    script_file.write("from subprocess import call\n")
    script_file.write("\n")
    script_file.write("variableValueRegex = re.compile(r\"(?P<var_name>[a-zA-Z_]+[a-zA-Z0-9_]*)=(?P<var_value>.*)\")\n")
    script_file.write("\n")
    script_file.write("bash_vars = dict()\n")
    script_file.write("\n")
    script_file.write("my_pid = os.getpid()\n")
    script_file.write("p_to_bash_fifo = \"/tmp/pyshell-p-to-bash-\" + str(my_pid) + \".fifo\"\n")
    script_file.write("bash_to_p_fifo = \"/tmp/pyshell-bash-to-p-\" + str(my_pid) + \".fifo\"\n")
    # Function to remove FIFOs
    script_file.write("def removeFifos():\n")
    script_file.write("    try:\n")
    script_file.write("        if os.path.exists(p_to_bash_fifo):\n")
    script_file.write("            os.remove(p_to_bash_fifo)\n")
    script_file.write("        if os.path.exists(bash_to_p_fifo):\n")
    script_file.write("            os.remove(bash_to_p_fifo)\n")
    script_file.write("    except IOError:\n")
    script_file.write("        print \"SOMETHING WENT WRONG!\"\n")
    script_file.write("        pass\n")
    script_file.write("\n")
    script_file.write("removeFifos()\n")
    script_file.write("\n")
    script_file.write("semaphore = threading.Semaphore(0)\n")
    script_file.write("bash_var_sem = threading.Semaphore(0)\n")
    script_file.write("\n")
    script_file.write("thismodule = sys.modules[__name__]\n")
    script_file.write("process = subprocess.Popen([\"/bin/bash\"], stdin=subprocess.PIPE)\n")
    script_file.write("\n")
    script_file.write("\n")
    # Create the FIFOs
    script_file.write("process.stdin.write(\"mkfifo \" + p_to_bash_fifo + \"\\n\")\n")
    script_file.write("process.stdin.write(\"mkfifo \" + bash_to_p_fifo + \" \\n\")\n")
    # Wait until the FIFO exists
    script_file.write("while not os.path.exists(p_to_bash_fifo) or not os.path.exists(p_to_bash_fifo):\n")
    script_file.write("    time.sleep(0.05)\n")
    script_file.write("\n")
    script_file.write("def bash_terminated_signal():\n")
    script_file.write("    semaphore.release()\n")
    script_file.write("\n")
    # Create a new thread to receive calls from Bash
    script_file.write("def py_remote():\n")
    script_file.write("    while True:\n")
    script_file.write("        try:\n")
    script_file.write("            function_name = None\n")
    script_file.write("            for fifoLine in open(bash_to_p_fifo):\n")
    script_file.write("                function_name = fifoLine\n")
    script_file.write("            if function_name != None:\n")
    script_file.write("                search = variableValueRegex.search(function_name)\n")
    script_file.write("                if search == None:\n")
    script_file.write("                    thread.start_new_thread(getattr(thismodule, function_name.strip()), ())\n")
    script_file.write("                else:\n")
    script_file.write("                    bash_vars[search.group('var_name')] = search.group('var_value')\n")
    script_file.write("                    bash_var_sem.release()\n")
    script_file.write("        except IOError:\n")
    script_file.write("            pass\n")
    script_file.write("\n")
    script_file.write("thread.start_new_thread(py_remote, ())\n")
    script_file.write("\n")

    for line in fileinput.input():
        # Ignores the first line, which should be the shebang line
        if first_line and shebangLine_regex.match(line):
            first_line = False
            continue
        if shell_line_regex.match(line):
            if comment_line_regex.match(line):
                #
                # Comment line
                #
                script_file.write(line)
            else:
                #
                # Bash line
                #
                # TODO Detect such line instead of relying on the programmer to mark them
                if empty_comment_at_end_of_line_regex.search(line):
                    if inside_nested_python:
                        nested_python_script += "    f = open(p_to_bash_fifo, 'w')\n"
                        nested_python_script += "    f.write(\"EOF\\n\")\n"
                        nested_python_script += "    f.close()\n"
                        nested_python_script += "\n"
                        nested_python_script += "process.stdin.write(\"echo \\\"" + callback_function_name + "\\\" > \" + bash_to_p_fifo + \"\\n\")\n"
                        nested_python_script += "process.stdin.write(\"while true; do read var_name < \" + p_to_bash_fifo + \"; ( [ \\\"x$var_name\\\" = \\\"xEOF\\\" ] || [ \\\"x$var_name\\\" = \\\"x\\\" ] ) && break; echo -n \\$$var_name > \" + bash_to_p_fifo + \"; done \\n\")\n"
                        nested_python_script += "\n"
                        script_file.write(nested_python_script)
                        nested_python_script = ""
                    else:
                        callback_function_name = "callBackFunction" + str(callback_index)
                        callback_index += 1
                        nested_python_script = "def " + callback_function_name + "():\n"
                        nested_python_script += convert_bash_var_references(line)
                    inside_nested_python = not inside_nested_python
                # We need to remove the first # and the \n at the end of the line
                trimmedLine = line[line.index("#") + 1:len(line) - 1]
                trimmedLine = trimmedLine.replace("\\", "\\\\")
                trimmedLine = trimmedLine.replace("\"", "\\\"")
                linePrefix = line[0:line.index("#")]
                script_file.write(linePrefix + "process.stdin.write(\"" + convert_python_var_references(trimmedLine) +
                                 "\\n\")\n")
        else:
            #
            # Python line
            #
            if inside_nested_python:
                nested_python_script += convert_bash_var_references(line)
            else:
                script_file.write(convert_bash_var_references(line))

    script_file.write("process.stdin.write(\"echo -n \\\"bash_terminated_signal\\\" > \" + bash_to_p_fifo + \"\\n\")\n")
    script_file.write("semaphore.acquire()\n")
    script_file.write("removeFifos()\n")
    script_file.write("\n")

subProcess = subprocess.Popen(["python", script_file_name], stdin=subprocess.PIPE)
subProcess.communicate(input="exit 0")
os.remove(script_file_name)
