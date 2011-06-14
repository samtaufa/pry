
Specifying Project Structure
============================

In order to perform coverage analysis, __pry__ must know a few things about the
structure of your project. The following parameters can be set in the
<strong>.pry</strong> configuration file, which can be placed in any directory
containing tests:

- __coverage__: the path to the base of the module under test.

- __exclude__: a list of paths that should be _excluded_ from from coverage
  analysis.

- __base__: the base of the project. This path is added to sys.path so that
  project imports function correctly.


#### Example

<pre class="output">
-- project
   |-- module
   |   |-- __init__.py
   |   |-- exclude.py
   |   |-- one.py
   |   `-- two.py
   `-- test
       |-- .pry
       |-- test_one.py
       `-- test_two.py
</pre>
<div class="fname">(examples/project)</div>

__module__ is the module under test, and __exclude.py__ is a source file that
should be excluded from coverage analysis. The pry unit test suite lives in a
parallel __test__ directory. The <strong>.pry</strong> file in the test
directory looks like this:

<!--( block | syntax("py") )-->
$!showsrc("../examples/project/test/.pry")!$
<!--(end)-->

More .pry syntax
================

The .pry syntax is very simple, and is very similar to that of the standard
Python ConfigParser module:

<pre class="output">
# .pry files can contain comments

# Multiple paths can be specified using newlines:
exclude = ../module/exclude.py
          ../module/exclude2.py
          ../module/exclude3.py
</pre>















