import libpry
import libpry.explain as explain

class uExpression(libpry.AutoTree):
    def test_show(self):
        e = explain.Expression("a + b")
        s = e.show(dict(a=1, b=2), {})
        assert s == "3"


class uExplain(libpry.AutoTree):
    def setUp(self):
        self.s = explain.Explain()

    def test_simple(self):
        r = self.s.parseExpression("1 == 1")
        assert r == [
                        explain.Expression("1"),
                        "==",
                        explain.Expression("1"),
                    ]

    def test_parens(self):
        r = self.s.parseExpression("True == (1 == 1)")
        assert r == [
                        explain.Expression('True'),
                        '==',
                        explain.Expression('(1 == 1)')
                    ]
        r = self.s.parseExpression("True == ((1) == (1))")
        assert r == [
                        explain.Expression('True'),
                        '==',
                        explain.Expression('((1) == (1))')
                    ]

    def test_unary(self):
        r = self.s.parseExpression("(1 == 1)")
        assert r == [
                        explain.Expression('(1 == 1)')
                    ]
        r = self.s.parseExpression("1+1")
        assert r == [
                        explain.Expression('1+1')
                    ]

    def test_not(self):
        r = self.s.parseExpression("not (1 == 1)")
        assert r == [
                        "not",
                        explain.Expression('(1 == 1)')
                    ]

    def test_and(self):
        r = self.s.parseExpression("a == b and c == d")
        r2 = self.s.parseExpression("assert a == b and c == d")
        expected = [
                        explain.Expression('a'),
                        '==',
                        explain.Expression('b'),
                        'and',
                        explain.Expression('c'),
                        '==',
                        explain.Expression('d')
                    ]
        assert r == expected
        assert r2 == expected

    def test_comma(self):
        r = self.s.parseExpression("a == b and c == d, foo")
        r2 = self.s.parseExpression("assert\ta == b and c == d, foo")
        expected = [
                        explain.Expression('a'),
                        '==',
                        explain.Expression('b'),
                        'and',
                        explain.Expression('c'),
                        '==',
                        explain.Expression('d')
                    ]
        assert r == expected
        assert r2 == expected

    def test_unbalanced(self):
        assert not self.s.parseExpression("a == (b and c == d, foo")
        assert not self.s.parseExpression("[a == b and c == d, foo")
        assert not self.s.parseExpression("a == b and c == d, foo]")

    def test_str(self):
        r = explain.Explain(
                "a == b and c == d, foo",
                dict(a = 1, b = 2, c = 3, d = 4),
                dict()
            )
        assert str(r) == "1 == 2 and 3 == 4"


tests = [
    uExpression(),
    uExplain()
]
