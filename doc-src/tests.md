
Overview
========

The examples in this section are available with the __pry__ source distribution, 
in the _examples_ directory. Within this directory we can run __pry__ with the
_sample source code_ as the argument to see test results:

A basic example
===============

This example should look familiar to anyone who has used the built-in Python
__unittest__ module. The main points to note are:

* __setUpAll__ and __tearDownAll__ run before and after the group of
contained tests as a whole.

* __setUp__ and __tearDown__ run before and after each of the contained
tests.

* __pry__ is a tree-based test framework. __AutoTree__ turns methods with
names of the form "test_*" into test nodes automatically.

* Unlike the built-in __unittest__ module, __pry__ does _not_ automatically
instantiate test suites. Instead, they need to be instantiated manually and
added to a __tests__ list in the module scope.

* Test assertions are written using the __assert__ keyword.
Assertion errors are caught, and the failing expression is parsed and
re-evaluated to give an informative error message.

<!--(block | syntax("py"))-->
$!showsrc("../examples/test_basic.py")!$
<!--(end)-->

Remember:

<li>libpry.AutoTree</li>
<li>def test_mynameXYZ</li>
<li> the Test classes are specified in a _test_ list at the end of the file
<!--(block | syntax("py"))-->
        tests = [
                TestClass()
        ]
<!--(end)-->
</li>



Running the tests
=================

From the <span>examples</span> in the __pry__ distribution, and
Command Line documentation, we can run the
tests as follows:

$!examples.pry("examples", "test_basic.py")!$

