from setuptools import find_packages, setup

setup(
    name='flaskr',
    version='1.0.0',
    description='HvA Scripties implemented with flask',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
    python_requires='>=3'
)