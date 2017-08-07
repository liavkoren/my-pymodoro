from setuptools import setup

setup(
    name='pymodoro',
    entry_points={
        'console_scripts': [
            'pymodoro = cli:cli',
        ],
    }
)
