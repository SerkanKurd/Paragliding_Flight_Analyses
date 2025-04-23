from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = [line.strip()
                        for line in f if line.strip() and not line.startswith("#")]

setup(
    name="Paragliding_Flight_Analyses",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "Paragliding_Flight_Analyses = "
            "Paragliding_Flight_Analyses.main:main",
        ],
    },
    python_requires=">=3.10,<4.0",
)
