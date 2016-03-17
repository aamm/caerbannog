# Caerbannog

Write shell scripts using Python. Or is it Python using shell?

# Introduction

Here is the example 1, found in the project's repository:

    #!/usr/bin/env python ../caerbannog.py
    ##
    ## And now for something completely new...
    ##

    print "This is python"

    # echo "And this is bash"

    ## And this is a comment.

The first line is the shebang telling the Python environment to use the Caerbannog script to interpret the script you
wrote.

All lines starting with two sharp characters are comments that will be simply ignored.

Lines that do not start with a sharp character is executed as Python. Lines with a single sharp are executed as Bash.

# Why?

Bash scripts are very powerful and expressive. A few bash lines can be used to start new processes, connect processes
using pipes, control the operating system, create new users, only to name a few possible usages. But shell scripts tend
to become hard to read as they grow. Also, it is common for shell scripts to have to rely on tools to do most of the
algorithmically complex functions such as parsing a JSON file.

Python, on the other hand, has a cleaner, more robust, OOP programming model. But, in order to perform simple OS actions
such as creating a new user or installing something using apt-get, Python needs to rely on native calls which end up
polluting the code with calls such as:

    subprocess.Popen(["apt-get", "install", "-y", "git"])

Another limitation of sprinkling such calls all over a Python code is that each call is a new OS process with a brand
new environment. So we cannot define shell variables that are later read using the $VARIABLE syntax. Neither we can
cd to a directory and call the following command from the same directory.

# How does it work?

Each execution of a Caerbannog script consists of three processes:

1. A Python process that reads the Caerbannog script, converts it into a conventinal Python script, and executes this
generated script.
1. The execution of this generated Python script, which creates the Bash process and controls it.
1. A Bash process created by the generated Python script.

The generated script process and the Bash process communicate through two named Unix pipes.

# Limitations

See the counter examples for more information.

## Accessing Bash variables from Python code inside of a Bash block

## Multiple levels of context switching in nested blocks

## Concurrency

You may have several threads on the Python world, and several processes on the Bash world, but only one thread or
process at a time can access the other world at a time. Concurrent accesses to the other world may have non-
deterministic results which includes deadlocks.
