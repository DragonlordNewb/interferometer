import socket
import statistics
import sys
import datetime

last100 = [x for x in range(100)]
last10 = [0.1 for _ in range(10)]
buildingUp = True

def mean():
	return sum(last100) / 100

def stdev():
	return statistics.stdev(last100)

def scr():
	sd = (sum(last10)/10)
	if sd > 2:
		return "F"
	if sd > 1:
		return "D"
	if sd > .5:
		return "C"
	if sd > .1:
		return "B"
	if sd > .05:
		return "A"
	return "S"

def sig(i):
	if i > 6:
		return "AAA"
	if i > 5:
		return "A"
	if i > 4:
		return "B"
	if i > 3:
		return "C"
	if i > 2:
		return "D"
	return "F"

def current_time_string():

    now = datetime.datetime.now()
    formatted_time = now.strftime("%m/%d/%Y %H:%M:%S.%f")[:-3]  # Format as mm/dd/yyyy xx:xx:xx.xxx
    return formatted_time

if __name__ == "__main__":
	print("Loading socket ...", end="")
	sys.stdout.flush()
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print("done.\nLoading hostname and IP ...", end="")
	sys.stdout.flush()
	hn = socket.gethostname()
	ip = socket.gethostbyname(hn)
	print("done, hostname", hn, "ip", ip, "\nAwaiting data ...")
	sock.bind((ip, 7777))
	d = sock.recvfrom(1024)
	while True:
		d = sock.recv(1024)
		s = d.decode("utf-8")
		i = 0
		try:
			i = float(s)
		except:
			print("Error: corrupted data packet")
		if len(last100) < 100 and "skip" not in sys.argv:
			print("\rBuilding up baseline data (" + str(len(last100)) + "%) ...", end="")
			last100.append(i)
		else:
			if buildingUp == True:
				buildingUp = False
				print("\rCollected baseline data points for analysis.")
			if last100[99] != 0:
				print(
					current_time_string(), "\t New data point:", s, "\t\t percent change", str(round(100 * ((i / last100[99]) - 1), 3)) + "%\t\t standard deviations:", str(round((i - mean()) / stdev(), 3)),
					"\tcurrent statistics:\tmean:", str(round(mean(), 3)), "\tstandard deviation:", str(round(stdev(), 3)), "\tsignal coherence:", scr(), "\tsignificance:", sig(round((i - mean()) / stdev(), 3))
				)
			else:
				print("Error: interferometer system failure")
			last100.append(i)
			last100.pop(0)
			last10.append(abs(stdev()))
			last10.pop(0)
	c.close()
