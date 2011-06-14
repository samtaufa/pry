
__AutoTree__ is a __TestContainer__ class that provides a short-cut for
building trees of related tests. Methods of the form test_* are automatically
turned into __Test__ objects, and added to the container, with names equal to
the method names.

The following code is functionally equivalent to the example given in the
previous section:

<!--(block | syntax("py"))-->
$!showsrc("../examples/test_autotree.py")!$
<!--(end)-->

Test hierarchy:

$!examples.pry("examples", "-l test_autotree.py")!$

