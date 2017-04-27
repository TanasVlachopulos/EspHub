from setuptools import setup, find_packages

setup(
    name='esphub',
    version='0.1',
    author='Tanasis Vlachopulos',
    install_requires=[
        'Click',
        'Django',
        'paho-mqtt',
        'Pillow',
        'pygal',
        'schedule',
        # 'cairosvg',
    ],
    entry_points='''
        [console_scripts]
        esphub=esphub:start
    ''',
    # packages=find_packages(),
    # include_package_data=True,
)
