import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='c2vb',
    packages=['c2vb'],
    version='0.0.4',
    license='MIT',
    description='A program convert simple C / C++ code to Visual Basic 6 code',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Chaigidel',
    author_email='chaigidel@outlook.com',
    url='https://github.com/Chaigidel/c2vb',
    keywords=['c', 'cpp', 'visualbasic', 'ast'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'c2vb=c2vb:console',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
