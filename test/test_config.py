import libpry
import libpry.config as config

class uConfig(libpry.TestTree):
    def test_badkey(self):
        libpry.raises(
            "unknown options",
            config.Config, "config/badkey"
        )

    def test_simple(self):
        c = config.Config("config/simple")
        assert c.base == "one"
        assert c.coverage == "two"
        assert c.exclude == ["three"]

    def test_nonexistent(self):
        c = config.Config("nonexistent")
        assert c.base == ".."
        assert c.coverage == ".."
        assert c.exclude == ["."]

    def test_nonexistent(self):
        c = config.Config("config/magic")
        assert c._magic


tests = [
    uConfig()
]
