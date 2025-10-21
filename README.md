# Sequence Engine Bprogram (SEB)

## Installing required dependencies

The serial-to-usb bridge requires the `pyserial` library to function. Create a virtual environment with 

`python -m venv env`

then activate the environment with

`source env/Scripts/activate` (bash terminal)

then install required dependencies:

`pip install -r 'requirements.txt'`

## Running the Serial-to-Ethernet Bridge (comms/usb_bridge.py)
*note: you must have installed the `pyserial` library (see above). Make sure the environment is activated*

### Step 1: Identifying your serial port
Mac Users:
- Open terminal **without** the serial connector plugged in and run `ls /dev/tty*`
- Connect your serial device and run `ls /dev/tty*`
- Compare the two results, the odd port out is the correct port; write it down (should be `/dev/tty.usbserial-*`)

Windows Users:
- Without the serial device connected, go to **Device Manager** -> **View/Show hidden devices** -> **Ports (COM & LPT)**
- Plug in the serial device and see what port it connects to; write it down (should be `COM*`)

### Step 2: Picking flags and running the program
---------Under construction----------
