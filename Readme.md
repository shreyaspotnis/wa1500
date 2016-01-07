# WD-1500

Provides functions to communicate with the WA-1500 wavemeter via serial.

## Requires
- pyserial: `pip install pyserial`
- ZeroMQ: `pip install pyzmq`
 

## Usage
```
cd /path/to/wa1500
cd wa1500
python .
```

The command `python .` runs the `__main__.py` file.

This program prints the wavemeter reading along with a timestamp to `stdout`, and also publishes it on a ZeroMQ socket on port 5556 with the topic `wa1500`. See [this page](http://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/patterns/pubsub.html) for an introduction on ZeroMQ sub-pub pattern.

