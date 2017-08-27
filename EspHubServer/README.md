# EspHubServer

## Instalation
### Virtualenv
The best way to run EspHubServer is **virtualenv** it keeps order in installed python libraries and prevents collision with other python packages.

**Step 0**

Install virtualenv on your computer. The simplest way is to use PIP package manager.

On Debian:
```
$ sudo apt-get install python-pip python3-dev
$ sudo pip install --upgrade virtualenv
```

**Step 1**

Download EspHub source.

```
$ cd ~   # change t oyour favourite working directory
$ git clone https://github.com/TanasVlachopulos/EspHubServer.git EspHubServer
$ cd EspHubServer
```

**Step 2**

Create virtualenv.

```
$ virtualenv -p python3 venv
# ...
# Installing setuptools, pip, wheel...done.
```

**Step 3**

Switch to virtualenv and install dependencies. 
EspHub use python settuptools to satisfy all dependencies, for instalation you can use PIP tool.
It is necessary to use Python 3.4 or higher, you can check it with `python --version`.

```
$ source venv/bin/activate
(venv) $ pip install .
# ...
#   Running setup.py install for EspHubServer ... done
# Successfully installed Click-6.7 Django-1.11 EspHubServer-0.1 Pillow-4.1.0 configparser-3.5.0 olefile-0.44 paho-mqtt-1.2.3 pygal-2.3.1 pytz-2017.2 schedule-0.4.2
```

> Optionally you can install package **cairosvg**, which is necessary for use remote display feature. 
> However, there are problems with cairosvg package on some computers, especially those with Windows system.
>
> `(venv) $ pip install cairosvg`

**Step 4**

EspHubServer provide simple CLI script **esphub**, to handle simple tasks.

```
(venv) $ esphub --help
(venv) $ esphub start --help
(venv) $ esphub start
```

**Step 5**

After all work you cant exit virtualenv context.

```
(venv) $ deactivate
```
