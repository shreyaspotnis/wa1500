# WA-1500

Provides functions to communicate with the WA-1500 wavemeter via serial.

## Requires
- pyserial: `pip install pyserial`
- ZeroMQ: `pip install pyzmq`


## Usage
```
cd /path/to/wa1500
python wa1500 --serialport COM5'' --publishport 5557 --topic wa1500
```

Replace COM5 with the serial port that the device is connected to. For linux
systems, usually `/dev/ttyUSB0` will do. If no serial port is specified,
the default is `COM5`. wa1500 is the topic under which zmq will publish.
Use something different, if for example you want have multiple wavemeters
connected.


The command `python .` runs the `__main__.py` file.

This program prints the wavemeter reading along with a timestamp to `stdout`, and also publishes it on a ZeroMQ socket on port 5557 with the topic `wa1500`. See [this page](http://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/patterns/pubsub.html) for an introduction on ZeroMQ sub-pub pattern.

