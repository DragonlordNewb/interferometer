import serial
import socket
import sys

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Invalid syntax: \"python3 relay.py <target>\"")
		exit(-1)
	print("Loading socket ...", end="")
	sys.stdout.flush()
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("done.\nFinding hostname and IP ...", end="")
	sys.stdout.flush()
	hn = socket.gethostname()
	ip = socket.gethostbyname(hn)
	print("done, host", hn, "ip", ip, "\nConnecting to target ...", end="")
	sys.stdout.flush()
	try:
		sock.connect((sys.argv[1], 7777))
	except Exception as e:
		print("error connecting to server:", str(e))
		exit(-2)
	print("done, ready to transmit data.")
	
