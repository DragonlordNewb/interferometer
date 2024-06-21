import socket
import statistics
import sys

last100 = []
buildingUp = True

def mean():
	sum(last100) / 100

def stdev():
	return statistics.stdev(last100)

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
		s = d.decode("utf-8")
		i = 0
		try:
			i = float(s)
		except:
			print("Error: corrupted data packet")
		if len(last100) < 100:
			print("\rBuilding up baseline data (" + str(len(last100)) + "%) ...", end="")
			last100.append(i)
		else:
			if buildingUp == True:
				buildingUp = False
				print("\rCollected baseline data points for analysis.")
			print("New data point:", s, "- percent change", str(100 * ((i / last100[99]) - 1)) + "% - standard deviation", str((i - mean()) / stdev()))
			last100.append(i)
			last100.pop(0)
	c.close()
