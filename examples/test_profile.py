import libpry

def fib1(n):
    lst, a, b = [], 0, 1
    while len(lst) < n:
       lst.append(b)
       a, b = b, a+b
    return lst

class ProfTest(libpry.AutoTree):
    def test_one(self):
        assert fib1(10) == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

tests = [
    ProfTest()
]
