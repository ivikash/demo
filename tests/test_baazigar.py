from baazigar.main import hello_world


def test_hello_world() -> None:
    if hello_world() != "Hello World":
        msg = 'Expected value to be "Hello World"'
        raise ValueError(msg)
