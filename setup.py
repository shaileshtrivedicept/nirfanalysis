from setuptools import setup, find_packages

setup(
    name="nirf-extraction-pipeline",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytesseract",
        "opencv-python-headless",
        "pandas",
        "numpy",
        "pillow",
        "rapidfuzz",
        "pytest"
    ],
    entry_points={
        "console_scripts": [
            "nirf-extract=src.main:main",
        ],
    },
    author="Jules",
    description="A production-grade NIRF image-to-dataset extraction pipeline.",
)
