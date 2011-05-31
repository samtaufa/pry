import os, os.path, subprocess
import countershape.widgets
import countershape.layout
import countershape.grok
from countershape.doc import *

this.layout = countershape.layout.Layout("_layout.html")
this.markdown = markup.Markdown(extras=["code-friendly"])

ns.docTitle = "Pry Manual"
ns.docMaintainer = "Aldo Cortesi"
ns.docMaintainerEmail = "aldo@nullcube.com"
ns.foot = "Copyright Nullcube 2008"
ns.head = countershape.template.File(None, "_header.html")
ns.sidebar = countershape.widgets.SiblingPageIndex(
                '/index.html',
                exclude=['countershape']
            )
ns.cs = countershape.grok.parse("../libpry")

# This should be factored out into a library and tested...
class Examples:
    def __init__(self, d):
        self.d = os.path.abspath(d)

    def _wrap(self, proc, path):
        f = file(os.path.join(self.d, path)).read()
        if proc:
            f = proc(f)
        post = "<div class=\"fname\">(%s)</div>"%path
        return f + post

    def _preProc(self, f):
        return "<pre class=\"output\">%s</pre>"%f

    def pry(self, path, args):
        cur = os.getcwd()
        os.chdir(os.path.join(self.d, path))
        prog = "pry"
        pipe = subprocess.Popen(
                    "%s "% prog + args,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                ).stdout
        os.chdir(cur)

        content = "> pry %s\n"%args + pipe.read()
        return self._preProc(content)
    
rootPath = os.path.abspath(".")
def showsrc(path):        
    return readFrom(os.path.join(rootPath, path))

ns.showsrc = showsrc

ns.examples = Examples("..")
ns.libpry = countershape.grok.parse("../libpry")

pages = [
    Page("index.mdtext", "Introduction"),
    Page("cli.mdtext",   "Command-line"),
    Page("tests.mdtext", "Writing Tests"),
    Directory("tests"),
    
    Page("coverage.mdtext",   "Coverage"),
    Directory("coverage"),
    
    Page("profiling.mdtext",   "Profiling"),
    Page("api.mdtext",   "API"),
    Page("admin.mdtext", "Administrivia")
]
