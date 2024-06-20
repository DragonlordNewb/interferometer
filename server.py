import socket
import sys

if __name__ == "__main__":
	print("Loading socket ...", end="")
	sys.stdout.flush()
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("done.\nLoading hostname and IP ...", end="")
	sys.stdout.flush()
	hn = socket.gethostname()
	ip = socket.gethostbyname(hn)
	print("done, hostname", hn, "ip", ip, "\nAwaiting connection ...")
	sock.bind((ip, 7777))
	sock.listen(1)
	c, a = sock.accept()
	print("Got connection from", a[0] + ":" + str(a[1]) + ", receiving remote interferometer data ...")
	while True:
		d = c.recv(1024)
		print(d.decode("utf-8"))
	c.close()
