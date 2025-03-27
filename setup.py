from setuptools import setup, find_packages

setup(
    name="quickenqifimport",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0.0",
        "PyQt6>=6.0.0",
        "python-dateutil>=2.8.2",
        "pandas>=1.3.0",
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "qif-converter=quickenqifimport.cli:main",
        ],
        "gui_scripts": [
            "qif-converter-gui=quickenqifimport.gui.main:main",
        ],
    },
)
