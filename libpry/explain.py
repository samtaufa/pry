"""
    A module for printing "nice" messages from assertion statements.
"""
import tokenize, parser

class _Wrap:
    def __init__(self, *lines):
        self.lines = list(lines)

    def __call__(self):
        if not self.lines:
            raise StopIteration
        else:
            return self.lines.pop(0)


class Expression:
    def __init__(self, s):
        self.s = s.strip()

    def show(self, glob, loc):
        try:
            return repr(eval(self.s, glob, loc))
        except SyntaxError as v:
            return "<could not be evaluated>"

    def __eq__(self, other):
        return self.s == other.s


class Explain:
    _specialOps = set(["==", "!=", "<", ">", ])
    _specialNames = set(["not", "and", "or"])
    def __init__(self, expr=None, glob=None, loc=None):
        self.expr, self.glob, self.loc = expr, glob, loc
        if self.expr:
            self.parsed, self.expr = self.parseExpression(self.expr)

    def parseExpression(self, expr):
        """
            Parses an expression into components. It understands the following
            delimiters: ==, !=, >, <, not, and, or  
                
            In each of these cases, the variables "x" and "y" will be evaluated.
            Discards the second (message) clause of an assertion expression.

            Returns None if the expression could not be interpreted.
        """
        nest = 0
        rem = expr
        # A list of (str, start, end) tuples.
        delimiters = []
        try:
            for i in list(tokenize.generate_tokens(_Wrap(expr))):
                name, txt = tokenize.tok_name[i[0]], i[1]
                start, end = i[2][1], i[3][1]
                if name == "OP" and (txt == "(" or txt == "["):
                    nest += 1
                elif name == "OP" and (txt == ")" or txt == "]"):
                    nest -= 1
                elif nest == 0:
                    if name == "OP" and txt in self._specialOps:
                        delimiters.append((txt, start, end))
                    elif name == "NAME" and txt in self._specialNames:
                        delimiters.append((txt, start, end))
                    elif name == "OP" and txt == ",":
                        rem = expr[:start]
                        break
        except tokenize.TokenError:
            return None, None
        if delimiters:
            ret = []
            cur = 0
            for s, start, end in delimiters:
                if start > cur:
                    ret.append(Expression(rem[cur:start]))
                ret.append(s)
                cur = end
            ret.append(Expression(rem[end:]))
            return ret, rem
        else:
            return [Expression(rem)], rem
    
    def __str__(self):
        l = []
        l.append("    :: Re-evaluating expression:\n")
        l.append("   :: %s\n"%self.expr)
        l.append("   ::")
        for i in self.parsed:
            if isinstance(i, Expression):
                l.append(i.show(self.glob, self.loc))
            else:
                l.append(i)
        return " ".join(l)
