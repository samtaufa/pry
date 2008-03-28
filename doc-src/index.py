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

pages = [
    Page("index.html", "Introduction"),
    Page("start.html", "Getting Started"),
    Page("tests.html", "Writing Tests"),
    Page("tree.html",  "Test Trees"),
    Page("cli.html",   "Command-Line Interface"),
    Page("coverage.html",   "Coverage analysis and profiling"),
    Page("api.html",   "API"),
    Page("admin.html", "Administrivia")
]
