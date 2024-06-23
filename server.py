import socket
import statistics
import sys
import datetime
import zlib

alldps = []
last100 = [0, 1]
overall = 0
last10 = [10000 for _ in range(10)]
buildingUp = True

color = {
	'white': "\033[1;37m",
	"purple": '\033[95m',
	"cyan": '\033[96m',
	"darkcyan": '\033[36m',
	"blue": '\033[94m',
	"green": '\033[92m',
	"yellow": '\033[93m',
	"red": '\033[91m',
	"bold": '\033[1m',
	"underline": '\033[4m',
	"end": '\033[0m'
}

def mean():
	return sum(last100) / 100

def stdev():
	return statistics.stdev(last100)

def ts():
	return datetime.datetime.now(datetime.UTC).strftime("%m/%d/%y %H:%M:%S.%f")[:-3] + " UTC"

sigi = 0
scri = 0
starttime = None

def scr():
	global scri
	if len(last10) < 10:
		return color["blue"] + "?" + color["end"]
	k = sum([abs(i) for i in last10]) / 10
	if k > 3:
		scri = 0.1
		return color["purple"] + "F" + color["end"]
	if k > 2:
		scri = 0.25
		return color["red"] + "D" + color["end"]
	if k > 1:
		scri = 0.5
		return color["yellow"] + "C" + color["end"]
	if k > 0.5:
		scri = 1
		return color["green"] + "B" + color["end"]
	if k > 0.1:
		scri = 2.5
		return color["cyan"] + "A" + color["end"]
	if k > 0.05:
		scri = 5
		return color["underline"] + color["cyan"] + "S" + color["end"]		

def sig(i):
	global sigi
	k = round((i - mean()) / stdev(), 3)
	if k > 7.5:
		sigi = 5
		return color["underline"] + color["cyan"] + "S" + color["end"]
	if k > 5:
		sigi = 2.5
		return color["cyan"] + "A" + color["end"]
	if k > 4:
		sigi = 1
		return color["green"] + "B" + color["end"]
	if k > 3:
		sigi = 0.5
		return color["yellow"] + "C" + color["end"]
	if k > 2:
		sigi = 0.25
		return color["red"] + "D" + color["end"]
	sigi = 0
	return color["purple"] + "F" + color["end"]

def css(i):
	k = round(sigi * scri * 4, 2)

	if k == 100: return color["bold"] + color["underline"] + color["cyan"] +  "S  ███████████████" + color["end"]
	if k == 50.0: return color["bold"] + color["cyan"] + "A+ ██████████████" + color["end"]
	if k == 25.0: return color["bold"] + color["cyan"] + "A  █████████████" + color["end"]
	if k == 20: return color["bold"] + color["cyan"] + "A- ████████████" + color["end"]
	if k == 10.0: return color["bold"] + color["green"] + "B+ ███████████" + color["end"]
	if k == 5.0: return color["bold"] + color["green"] + "B  ██████████" + color["end"]
	if k == 4: return color["bold"] + color["green"] + "B- █████████" + color["end"]
	if k == 2.5: return color["bold"] + color["yellow"] + "C+ ████████" + color["end"]
	if k == 2.0: return color["bold"] + color["yellow"] + "C  ███████" + color["end"]
	if k == 1.0: return color["bold"] + color["yellow"] + "C- ██████" + color["end"]
	if k == 0.5: return color["bold"] + color["red"] + "D+ █████" + color["end"]
	if k == 0.4: return color["bold"] + color["red"] + "D  ████" + color["end"]
	if k == 0.25: return color["bold"] + color["red"] + "D- ███" + color["end"]
	if k == 0.2: return color["bold"] + color["purple"] + "F+ ██" + color["end"]
	return color["bold"] + color["purple"] + "F  █" + color["end"]

if __name__ == "__main__":
	starttime = datetime.datetime.now(datetime.UTC).strftime("d%m%d%yt%H%M%S")
	print(color["white"] + "Loading socket ...", end="")
	sys.stdout.flush()
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print("done.\nLoading hostname and IP ...", end="")
	sys.stdout.flush()
	hn = socket.gethostname()
	ip = socket.gethostbyname(hn)
	print("done, hostname", hn, "ip", ip, "\nAwaiting connection ...")
	sock.bind((ip, 7777))
	d = sock.recvfrom(1024)
	print("Got packet, receiving remote interferometer data ...")
	while True:
		try:
			d = sock.recv(1024)
			s = d.decode("utf-8")
			i = 0
			try:
				i = float(s.split(" ")[0])
				t = s.split(" ")[1]
			except:
				print("Error: corrupted data packet")
			if len(last100) < 100:
				print("\rBuilding up baseline data (" + str(len(last100)) + "%) ...", end="")
				last100.append(i)
			else:
				if buildingUp == True:
					buildingUp = False
					starttime = ts()
					print("\rCollected baseline data points for analysis.\nStarting session.")
				else:
					overall += 1
					alldps.append(s)
				print(
					color["white"] + starttime + ", " + str(float(t)/1000) + " s\t", overall, color["bold"] + "\tNew data point:" + color["end"] + color["white"], s, "\tpercent change", str(round(100 * ((i / last100[99]) - 1), 3)) + "%\tstd. deviation", str(round((i - mean()) / stdev(), 3)),
					"\tsignificance", sig(i), color["bold"] + color["white"] + "\t\tsignal coherence" + color["end"], scr(), color["white"] + "\tmean value", str(round(mean(), 3)), "\taverage std. deviation", 
					str(round(stdev(), 3)), "\t\t\tcombined statistical significance:", css(i)
				)
				last100.append(i)
				last100.pop(0)
				last10.append((i - mean()) / stdev())
				last10.pop(0)
		except KeyboardInterrupt:
			print(color["white"] + "Session finished, exporting data ...")
			note = input("Notes on this session: ")
			addendum = ""
			if note != "":
				addendum = "_" + note
			dfn = "session_" + starttime + addendum + ".interferometer.dat"
			print("  Data file:", dfn)
			print("  Data points:", len(alldps))
			with open(dfn, "x") as f:
				pass
			with open(dfn, "a") as f:
				for n, s in enumerate(alldps):
					f.write(s + "\n")
					print("\rWriting data ... (" + str(n+1) + "/" + str(len(alldps)) + " " + str(100 * round((n + 1) / len(alldps), 3)) + "%) ", end="")
			print("done.                                   \n  Data written. Compressing ...", end="")
			raw = None
			with open(dfn, "rb") as f:
				raw = f.read()
			with open(dfn, "wb") as f:
				f.write(zlib.compress(raw))
			print("done.\nData successfully exported.")
			break
	print(color["end"])