import setuptools

requires = [
    "python-dotenv",
    "torch",
    "torchvision",
    "tqdm",
    "pp-ez==0.2.0",
    "psycopg2==2.8.5",
    "transformers==3.4.0"
]

test_requirements = [
    "pytest",
    "pytest-mock"
]

setuptools.setup(
    name='spec-builder',
    version='0.1',
    packages=setuptools.find_packages(),
    python_requires='>=3.8.5',
    install_requires=requires,
    tests_require=test_requirements,
    entry_points="""
    [console_scripts]
    spec-builder=spec_builder:main
    """
)