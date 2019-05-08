from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='routinemaker',
    version='0.5.3',
    url='https://github.com/kathyqian/routinemaker',
    author='Kathy Qian',
    author_email='hello@kathyqian.com',
    description=('A Python CLI that generates strength, cardio, and HIIT '
                 'exercise routines using parametric curves'),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'pyfiglet',
        'XlsxWriter',
        'numpy',
        'setuptools'
    ],
    entry_points={
        'console_scripts': [
            'routinemaker=routinemaker.routinemaker:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
