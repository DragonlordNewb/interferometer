import serial
import socket
import sys
import time

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Invalid syntax: \"python3 relay.py <target> <port>\"")
		exit(-1)
	print("Loading serial connection ...", end="")
	sys.stdout.flush()
	ser = serial.Serial(sys.argv[2], 9600)
	print("done.\nLoading socket ...", end="")
	sys.stdout.flush()
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("done.\nConnecting to target ...", end="")
	sys.stdout.flush()
	try:
		sock.connect((sys.argv[1], 7777))
	except Exception as e:
		print("error connecting to server:", str(e))
		if input("Raise error? (y/n) ") == "y":
			raise e
		exit(-2)
	print("done, ready to transmit data.")


	ser.readline()

	try:
		while True:
			# Read data from Arduino
			if ser.in_waiting > 0:
				data = ser.readline().decode('utf-8').strip()
				print(f"Received from interferometer: {data}")
				
				# Send data to TCP client
				sock.sendall(data.encode('utf-8'))
			else:
				print("No feed.")
				time.sleep(1)

	except KeyboardInterrupt:
		print("Interrupted by user")

	finally:
		# Clean up
		sock.close()
		ser.close()
