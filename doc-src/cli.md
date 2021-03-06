The Command Line
==============

The pry command-line is self-documented, and hopefully self-explanatory.
The "Quick-Start" basic THREE commands are:

- __pry --help__ 
- __pry__ : To run tests in the _current directory_ 
- __pry tests__ :  to run the tests in the sub-directory __tests__

Sample Output
------

The following output displays  output from pry --help, a quick review of available
command-line options

$!examples.pry("", "--help")!$

The following output displays the results of running pry in the 
examples directory of the source distribution.

$!examples.pry("examples", "")!$

Test Selection
==============

pry provides for fine grain selection of tests and  
by default loads all tests in the current directory (and 
recursively if the -r flag is specified.)  When the optional 
_testfilter_ is specified pry will select a subset of tests based 
on a partial match strategy from the existing directory.

The -l list option allows dicovery of tests availability.

Sample Execution
==============

The following examples illustrate test selection by using
pry's list facility to view available tests.

- __pry__ load all tests in current directory, __pry -l__ to discover a list of tests
- __pry filename__ load all tests in filename, __pry -l filename__ to discover tests inside the file filename
- __pry test_suite__ load all tests with the name test_suite, __pry -l test_suite__ to discover tests titled "test_suite"
- __pry Class.Test__ load all tests in Class "Class" with name "Test", __pry -l Class.Test__ to discover said tests

Execution samples are based in the _examples_ subdirectory

- __pry__ load all tests in current directory (default behaviour)

$!examples.pry("examples", "")!$

Argghhh, an error in ./test_basic.MySuite.test_three, and although the tests are few and we are given the listing at the head, we can review just the known tests using -l.

- __pry -l__  To discover the list of tests in the current directory.

$!examples.pry("examples", "-l")!$

The output displays a tree hierarchy of 4 files with various test classes and a total of 8 tests. ./test_autotree references ./test_autotree.py likewise ./test_basic for ./test_basic.py.

Given the discoverability of tests, we can refine test runs by drilling into the specific file, test, or test-class.

- __pry -l filename__  Use partial matching to interrogate by filename, get a list of tests inside the file _test_basic.py_:

$!examples.pry("examples", "-l test_basic")!$

The output displays 1 file containing 1 class (_MySuite_) with 3 tests.

We can now run only the tests in filename (test_basic.py)

$!examples.pry("examples", "test_basic")!$

Oops, there's an error in that test suite. When you've got pages of tests that known to be passing,
why wade through them when you can just rerun the component of the tests that are failing?

- __pry -l test_suite__  Use partial matching to interrogate by class or test name, get a list of tests in the current directory titled _test_one_

You may want to run a number of test suites in different test files. Rediscover these tests.

$!examples.pry("examples", "-l test_one")!$

The output displays a tree hierarchy of 4 files containing test classes and 4 occurrences of _test_one_.

We can run all test suites, from various test files, starting with the title _test_one_.

$!examples.pry("examples", "test_one")!$

Wow, freedom becons.

- __pry -l Class.Test__  Use partial matching to interrogate by Class.Test name, get a list of  tests in class _ProfTest_ and function _test_one_

$!examples.pry("examples", "-l ProfTest.test_one")!$

The output displays a tree hierarchy of 1 file containing the test class ProfTest and the test _test_one_.

We are now into more specifics of how you can use pry. We can run only those tests
for which we've made related changes. Obviously this significantly cuts down
the noise.

$!examples.pry("examples", "ProfTest.test_one")!$

Sub-Directories
-----

And yes if you like to keep your tests across multiple directories, all these features 
are also available with subdirectories. You can specify sub-directories expelicitly

- __pry sub-directory.filename__

$!examples.pry("examples", "-l project/test")!$

Or, you can just recurse into the subdirectories implicitly

- __pry test__

$!examples.pry("examples", "--recurse --list test_a")!$

