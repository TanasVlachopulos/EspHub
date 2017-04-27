from setuptools import setup, find_packages

setup(
    name='EspHubServer',
    version='0.1',
    author='Tanasis Vlachopulos',
    # package_dir={'.': 'EspHubServer'},
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'Django',
        'paho-mqtt',
        'Pillow',
        'pygal',
        'schedule',
        'configparser',
        # 'cairosvg',
    ],
    entry_points='''
        [console_scripts]
        esphub=EspHubServer.esphub:cli
    ''',
        # tcmd=Plots.test:cli
)
