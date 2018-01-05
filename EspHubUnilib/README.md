
# EspHubUnilib

## Installation

Run this in EspHubUnilib folder:
```bash
$ sudo pip3 install .
```

# ImageTransmitter

ImageTransmitter script allow user to send bitmap (or other image data) to ESP device with connected display. 
All data are transfered over MQTT protocol so own MQTT broker is required.

Currently this script support only devices with SSD1306 OLED display and with uploaded library EspHubLib for ESP32, but can be modified for other devices.

## Main features

* Send single image
* Stream content of folder as video
* Send image from another application thru filesystem pipe
* List all devices with connected display (required running EspHubServer)


## Usage

Use help option for obtain all information about ussage.

```
$ python2 ImageTransmitter.py --help
```
Output:
```
Usage: ImageTransmitter.py [OPTIONS] COMMAND [ARGS]...

  This multi-tool provides several methods to send data to a devices which
  use EspHubLibrary. The MQTT protocol is used for data transmission so
  running MQTT broker is required.

Options:
  -b, --broker TEXT     MQTT broker domain name or IP address.  [required]
  -p, --port INTEGER    Network port of MQTT broker. Default 1883.
  -u, --user-name TEXT  User name for connection to MQTT broker.
  -P, --password TEXT   Password for connection to MQTT broker.
  --client-id TEXT      Specific client ID for connection to MQTT broker.
  -v, --verbose         Enable debug outputs.
  --help                Show this message and exit.

Commands:
  get-devices     Obtain list of display devices.
  pipe-interface  Create pipe interface for sending images.
  send-image      Send single image to specific device.
  send-images     Send content of directory to specific device.
```

Script has only one mandatory option **-b** (broker) which defined domain name or IP address of local MQTT broker, all display devices have to be connected to the same broker. There are more options for connection to broker but they are optional and depends on the setting of your broker.

### get-device command
Provide list of connected devices with display ability. For this command you need runnig EspServer connected to the same broker.

```
python3 ImageTransmitter.py -b mybroker.eu get-devices
```
Output:
```
-----------------------------------
| device name    | device id      |
-----------------------------------
| testHello      | 828529         |
| Output Test    | 828530         |
-----------------------------------
```

### send-image command
Send single image to selected device with name "ESP32 device". You have to specified bmp or png image (bmp has better quality) and device name or device ID (device name is available only when EspHubServer is running).

```
$ python3 ImageTransmitter.py -b tanas.eu send-image -d "ESP32 device" spock.bmp
```

All commands has their own detail help option:
```
$ pyton3 ImageTransmitter.py -b tanas.eu send-image --help
```
Output:
```
Usage: ImageTransmitter.py send-image [OPTIONS] BITMAP

  Send single image to specific device.

  Recommended format is monochrome .bmp with 1-bit color depth but also
  other format such as .png can be used if normalize option is enabled.
  Normalization process try to convert image into standardized monochrome
  format but quality of results is questionable.

Options:
  -d, --device TEXT             Device ID or device name.  [required]
  --normalize / --no-normalize  Normalize image to monochrome format. Default
                                Enabled.
  --help                        Show this message and exit.
```
 
### send-images command
Stream content of folder to display as video with defined frame rate.

```
$ python3 ImageTransmitter.py -b tanas.eu send-images -d "esp32 device" img_examples1
```

Command help:
```
Usage: ImageTransmitter.py send-images [OPTIONS] BITMAPS_FOLDER

  Send content of directory to specific device.

  List all files in given directory and send it to display with specific
  frame-rate.

  Recommended format is monochrome .bmp with 1-bit color depth but also
  other format such as .png can be used if normalize option is enabled.
  Normalization process try to convert image into standardized monochrome
  format but quality of results is questionable.

Options:
  -d, --device TEXT             Device ID or device name.  [required]
  -f, --frame-rate INTEGER      Send <INTEGER> frames per second. Default 10.
  --normalize / --no-normalize  Normalize image to monochrome format. Default
                                Enabled.
  --help                        Show this message and exit.
```

### pipe-interface command

Create named pipe in file system and listen for input on it. Is usefull for sending images from another aplication or commandline.

> This function is supported only on Linux system and in Linux Bash Shell on Windows 10.
> 

```
$ python3 ImageTransmitter.py -b tanas.eu pipe-interface -d "esp32 device" ~/pipeline
```
Then you can sand data to display thru pipe:

```
$ cat spock.bmp > ~/pipeline
```

Command help:
```
Usage: ImageTransmitter.py pipe-interface [OPTIONS] <PATH>

  Create pipe interface for sending images.

  CAUTION: This function is supported only from linux systems or in Linux
  subsystem on Windows. If you use Linux subsystem on Windows pipe path must
  be in Linux filesystem.

  Command create named pipe in given <PATH> and listen in forever loop for
  incoming data. Data incoming into pipe are immediately send to given
  device.

  If image content is bigger than given buffer data will be incomplete and
  image sending failed.

  Recommended format is monochrome .bmp with 1-bit color depth but also
  other format such as .png can be used if normalize option is enabled.
  Normalization process try to convert image into standardized monochrome
  format but quality of results is questionable.

Options:
  --buffer INTEGER              Size of input buffer in bytes. Default 4096.
  -d, --device TEXT             Device ID or device name.  [required]
  --normalize / --no-normalize  Normalize image to monochrome format. Default
                                Enabled.
  --help                        Show this message and exit.
```
