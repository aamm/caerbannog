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
to become hard to read as they grow. Also, it is common for shell scripts to have to rely on external tools to do most
of the algorithmically complex functions such as parsing a JSON file.

Python, on the other hand, has a cleaner, more robust, OOP programming model. It can talk with a number of databases.
Python has a huge API library with powerful functions ranging from creating images to scientific computing. But, in
order to perform simple OS actions such as creating a new user or installing something using apt-get, Python needs to
rely on native calls which end up polluting the code with calls such as:

    subprocess.Popen(["apt-get", "install", "-y", "git"])

Another limitation of sprinkling such calls all over a Python code is that each call is a new OS process with a brand
new environment. So we cannot define shell variables that are later read using the $VARIABLE syntax. Neither we can
cd to a directory and call the following command from the same directory.

When we want to automate some Unix os MacOS processes we often see our selves first learning how to do the process
manually using Bash (typically). Then usually we try to turn the history of commands into a shell script and this is
where Caerbannog can help.

Instead of using Bash for programming, you can use Python and still keep your Bash lines readable and maintainable.

# Syntax

## References to variables in the other world

There really are two disjoint worlds: Python and Bash. For code in one of the worlds to access variables in the other
one, you should use the same syntax.

    # echo $<pythonvar>
    print $<bashvar>

In Bash all Python variable references are replaced by the string value of the Python variable. Then if the value of
pythonvar above is "a b c" the first line of code above is replaced with

    echo a b c

In the Python world all Bash variable references are replaced with the string value of the variable in Bash.

Each explicit call to a variable from the Bash environment creates a variable in the Python environment. Therefore
you can still refer to the variable in Python although any change in the original variable in Bash will be not
automatically propagated to the copy in Python. The exact same behavior takes place when Bash code accesses
Python variables. Run example 7 to see this mechanism in action.

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

This limitation is illustrated in the counter example 1:

    # for i in $(seq 3); do #
        print "Killer bunny!!" + $<i>
    # done #

The code above will block. Until we fix this bug the workaround for the case above is to use the loop to build an array
in Bash, which after the loop is read by Python. This workaround has the serious disadvantage of being less efficient
for large sequences.

## Multiple levels of context switching in nested blocks

This limitation is illustrated in the counter example 2:

    # for i in $(seq 3); do #
        for i in xrange(10):
    # echo "===> $<i>"
         print "a"
    # done #

In the code above we are trying to switch worlds twice in the same nesting structure: first from Bash to Python on
line 1, and then from Python back to Bash on line 2.

## Concurrency

You may have several threads on the Python world, and several processes on the Bash world, but only one thread or
process at a time can access the other world at a time. Concurrent accesses to the other world may have non-
deterministic results which includes deadlocks.
