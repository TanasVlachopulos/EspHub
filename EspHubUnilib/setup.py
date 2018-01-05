from setuptools import setup, find_packages

setup(
    name='EspHubUnilib',
    version='0.9',
    author='Tanasis Vlachopulos',
    # package_dir={'.': 'EspHubServer'},
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'paho-mqtt',
        'Pillow',
        'configparser',
    ],
    # entry_points='''
    #     [console_scripts]
    #     esphub=EspHubServer.esphub:cli
    # ''',
        # tcmd=Plots.test:cli
)