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
	return datetime.datetime.now(datetime.UTC).strftime("%m/%d/%y %H:%M:%S.%f UTC")

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
	if len(sys.argv) != 2:
		print("Invalid syntax: \"python3 reader.py <filename>\"")
		exit(-1)
	raw = None
	lns = []
	with open(sys.argv[1], "rb") as f:
		raw = zlib.decompress(f.read())
	lns = [float(i.strip()) for i in raw.decode("utf-8").split("\r\n") if i not in ["", " ", "\r", "\n", "\r\n"]]
	for n in range(len(lns)):
		try:
			i = lns[n]
			if len(last100) < 100:
				last100.append(i)
			else:
				if buildingUp == True:
					buildingUp = False
					starttime = datetime.datetime.now(datetime.UTC).strftime("d%m%d%yt%H%M%S")
				else:
					overall += 1
					alldps.append(i)
				print(
					color["white"] + ts() + "\t", overall, color["bold"] + "\tNew data point:" + color["end"] + color["white"], str(i), "\tpercent change", str(round(100 * ((i / last100[99]) - 1), 3)) + "%\tstd. deviation", str(round((i - mean()) / stdev(), 3)),
					"\tsignificance", sig(i), color["bold"] + color["white"] + "\t\tsignal coherence" + color["end"], scr(), color["white"] + "\tmean value", str(round(mean(), 3)), "\taverage std. deviation", 
					str(round(stdev(), 3)), "\t\t\tcombined statistical significance:", css(i)
				)
				if not (n % 50):
					input()
				last100.append(i)
				last100.pop(0)
				last10.append((i - mean()) / stdev())
				last10.pop(0)
		except KeyboardInterrupt:
			break
	print(color["end"])