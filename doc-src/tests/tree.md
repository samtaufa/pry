
__pry__ test trees consist of two types of nodes:

- __TestContainer__ objects are internal nodes that can contain __Test__
  nodes or other __TestContainers__. The __TestContainer__ objects set up
  and tear down fixtures for the nodes they contain.
- __Test__ objects are leaf nodes corresponding to actual unit tests.
  Each __Test__ object corresponds to a single test. __Test__
  objects must be direct children of a __TestContainer__ object.

Example
----------

This example constructs a simple tree with one __TestContainer__ containing two
__Test__ nodes:

<!--( block | syntax("py") )-->
$!showsrc("../examples/test_trees.py")!$
<!--(end)-->

As this example shows, trees can be constructed using nested lists. An
equivalent idiom would be to pass the children of each container node as
instantiation arguments:

<!--(block | syntax("py"))-->
tests = [
    MyContainer(
        [MyTest("test_one"), MyTest("test_two")]
    )
]
<!--(end)-->

Since all nodes are full __TinyTree.Tree__ objects, there is also a rich object
interface for constructing and manipulating trees (see the <a
href="http://dev.nullcube.com">TinyTree</a> documentation for more
information).

It is now possible to interrogate and run this test suite using the __pry__
command-line tool. The following command gives a graphical representation of
the test tree structure:

$!examples.pry("examples", "-l test_trees.py")!$

We can illustrate the order in which __setUp__ and __tearDown__ methods are run
by running the suite. We silence __pry__'s output using the -q flag, so we can
focus on just the example output:

$!examples.pry("examples", "-q test_trees.py")!$


Test Paths
==========

Each test is uniquely identified by its path from the root of the test tree.
For example, we can run just test_one in the example above by specifying its
path to pry:

$!examples.pry("examples", "-q test_trees.MyContainer.test_one")!$

Note that the module in which the test occurs can be specified as the initial
part of the path.
