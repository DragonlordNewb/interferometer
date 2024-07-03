# Manual for these drivers

## Setting up the relay

1. Flash the desired driver code onto the Arduino Uno that is running the interferometer
2. Connect the Arduino to a Raspberry Pi onto which you have pulled this repository
3. SSH to the Raspberry Pi
4. On the Pi, the Arduino port should be `/dev/ttyACM0`. In any case, find this file and the requisite packages and run `python3 relay.py <ip> <port>`.

## Setting up the server

Once the relay is set up, there is very little left to do on the server side. Simply run `python3 server.py` and the server will boot up to start receiving data.
You can tweak the graph/statistics, and you can export data files with `Export all data`. Doing that will create a compressed binary data file.

## Reading old files

Using `python3 reader.py <filename>` will open up a reader instance of the server, which allows you to scroll through old data files with the left shift and control buttons.
The reader can't export new data files.