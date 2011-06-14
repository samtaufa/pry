
Overview
========

The examples in this section can be found in the _examples/project_ directory
in the __pry__ distribution. From this directory we can run __pry__ with the "-s test"
argument to provide a coverage summary (where _test_ is the directory with the test suite):

$!examples.pry("examples/project", "-s test")!$

As the output shows, the test suite does not completely cover the file _one.py_
- lines 5 and 8 to 11 have not been run. The contents of this file are as
follows:

<!--( block | syntax("py", linenos=True) )-->
$!showsrc("../examples/project/module/one.py")!$
<!--(end)-->

Line 5 is clearly not covered because it is unreachable. An inspection of the
relevant portion of the test suite shows that __method2__ is never called:

<!--( block | syntax("py") )-->
$!showsrc("../examples/project/test/test_one.py")!$
<!--(end)-->