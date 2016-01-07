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

This program publishes the wavemeter readings on a ZeroMQ socket on port 5556.

