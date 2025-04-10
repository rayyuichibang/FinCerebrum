"""
    Setup file for FinCerebrum.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.6.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""

from setuptools import setup

if __name__ == "__main__":
    try:
        setup(
            name="FinCerebrum",
            version="0.1",
            package_dir={"": "src"},
            install_requires=[
                "importlib_metadata==7.1.0",
                "numpy==2.2.4",
                "openai==1.72.0",
                "pandas==2.2.3",
                "pytest==8.3.5",
                "setuptools==65.5.0",
                "Sphinx==8.2.3",
                "ta_lib==0.6.3",
                "yfinance==0.2.54"
            ],
            use_scm_version={"version_scheme": "no-guess-dev"}
        )
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
