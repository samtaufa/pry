import countershape.widgets
import countershape.layout
import countershape.grok
from countershape.doc import *

ns.docTitle = "Pry Manual"
ns.docMaintainer = "Aldo Cortesi"
ns.docMaintainerEmail = "aldo@nullcube.com"
ns.foot = "Copyright Nullcube 2008"
ns.head = "<h1> Pry - @!this.title!@ </h1>"
ns.sidebar = countershape.widgets.SiblingPageIndex(
                '/index.html',
                exclude=['countershape']
            )
this.layout = countershape.layout.TwoPane("yui-t2", "doc3")

ns.test_basic = readFrom("../examples/test_basic.py")
ns.test_trees = readFrom("../examples/test_trees.py")
ns.test_autotree = readFrom("../examples/test_autotree.py")

ns.libpry = countershape.grok.grok("../libpry")

pages = [
    Page("index.html", "Introduction"),
    Page("start.html", "Test Basics"),
    Directory("trees"),
    Page("coverage.html",   "Coverage"),
    Directory("coverage"),
    Page("cli.html",   "The pry tool"),
    Page("api.html",   "API"),
    Page("admin.html", "Administrivia")
]
