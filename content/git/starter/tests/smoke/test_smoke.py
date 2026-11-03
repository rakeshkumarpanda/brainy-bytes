import app
from app.calc import add, divide


def test_runs_the_packaged_build():
    # QA tests the zip the build job made, not the source folder
    assert "calc-app.zip" in app.__file__


def test_version():
    assert app.__version__ == "1.0.0"


def test_basic_sums():
    assert add(1, 1) == 2
    assert divide(9, 3) == 3
