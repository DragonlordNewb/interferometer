import tkinter as tk
import statistics
import datetime
import zlib
import time
import sys

class DataReader:
	def __init__(self, root, df):
		self.df = df
		self.index = 10
		self.root = root
		self.root.title("Gravantenna Interferometer Data Reader")
		self.root.configure(bg="black")
		
		### Graphs ###

		self.canvas_width = 800
		self.canvas_height = 400
		self.max_points = 100
		
		self.graph_frame = tk.Frame(root, bg="black")
		self.graph_frame.grid(row=1, column=1)

		self.canvas = tk.Canvas(self.graph_frame, width=self.canvas_width, height=self.canvas_height, bg="black")
		self.canvas.grid(row=1, column=1)

		self.percent_change_canvas = tk.Canvas(self.graph_frame, width=self.canvas_width, height=self.canvas_height, bg="black")
		self.percent_change_canvas.grid(row=1, column=2)
		
		self.new_data_label = tk.Label(self.graph_frame, text="Reading: Awaiting data relay ...\n ", font=("OCR A Extended", 12), bg="black", fg="white", justify="left", anchor="w", width=50)
		self.new_data_label.grid(row=2, column=1)
		
		### Graph Configuration ###

		self.graph_config_frame = tk.Frame(self.graph_frame, bg="black")
		self.graph_config_frame.grid(row=3, column=1, columnspan=2)

		self.max_points_entry = tk.Entry(self.graph_config_frame, bg="black", fg="white", font=("OCR A Extended", 12), width=20)
		self.max_points_entry.grid(row=1, column=1)

		self.max_points_button = tk.Button(self.graph_config_frame, text="Set data range", bg="black", fg="white", font=("OCR A Extended", 12), width=20, command=self.set_max_points)
		self.max_points_button.grid(row=1, column=2)

		### Data ###

		self.all_data = df
		self.data_points = [0]
		self.percent_changes = [0]

		self.graph_min = -1
		self.graph_max = -1
		
		### Mainloop ###

		self.root.bind("<Shift_L>", self.forward)
		self.root.bind("<Control_L>", self.backward)
		
		self.forward()
		self.update_graph()

	### Menus ###

	def set_max_points(self):
		self.max_points = int(self.max_points_entry.get())
		self.max_points_entry.delete(0, "end")

	### Data and Graphing ###

	# Stats functions #

	def mean(self):
		return statistics.mean(self.data_points)

	def stdev(self):
		if len(self.data_points) < 2:
			return -1
		return statistics.stdev(self.data_points)

	def deviations(self, x):
		if self.stdev() != 0:
			return (x - self.mean()) / self.stdev()
		return 0

	# Graphing functions #

	def forward(self, evt=None):
		if index == len(self.df) - 1:
			return
		self.index += 1
		self.all_data = self.df[:self.index + 1]
		self.data_points = self.df[:self.index + 1][::-1][:self.max_points][::-1]
		self.update_graph()

	def backward(self, evt=None):
		if index == 0:
			return
		self.index -= 1
		self.all_data = self.df[:self.index + 1]
		self.data_points = self.df[:self.index + 1][::-1][:self.max_points][::-1]
		self.update_graph()

	def update_graph(self):
		# Update label
		self.new_data_label.config(
			text=f"Reading:            {self.data_points[-1]}\
			\nMean:               {round(self.mean(), 3)}\
			\nStandard deviation: {round(self.stdev(), 3)}\
			\nPoint deviation:    {round(self.deviations(self.data_points[-1]), 3)}"
		)
		
		# Ensure we only keep the last mwax_points data points
		if len(self.data_points) > self.max_points:
			self.data_points.pop(0)
			self.percent_changes.pop(0)
		
		self.draw_graph()
		self.draw_percent_change_graph()
		
		# self.root.after(10, self.update_graph)

	def draw_graph(self):
		self.canvas.delete("all")
		
		if len(self.data_points) > 1:
			step_x = self.canvas_width / (self.max_points - 1)
			max_data_value = min_data_value = None
			if (self.graph_max == -1 or self.graph_min == -1):
				max_data_value = self.graph_max = max(self.data_points) + 10
				min_data_value = self.graph_min = min(self.data_points) - 10
			else:
				max_data_value = self.graph_max = max(max(self.data_points)+10, self.graph_max + 0.01*(max(self.data_points) - self.graph_max))
				min_data_value = self.graph_min = min(min(self.data_points)-10, self.graph_min + 0.01*(min(self.data_points) - self.graph_min))
			data_range = max_data_value - min_data_value
			data_range = data_range if data_range > 0 else 1  # Avoid division by zero
			
			# Normalize data points to fit within canvas height
			normalized_points = [
				((dp - min_data_value) / data_range) * (self.canvas_height - 20) + 10
				for dp in self.data_points
			]
			
			# Draw the graph
			for i in range(1, len(normalized_points)):
				x1 = (i - 1) * step_x
				y1 = self.canvas_height - normalized_points[i - 1]
				x2 = i * step_x
				y2 = self.canvas_height - normalized_points[i]
				self.canvas.create_line(x1, y1, x2, y2, fill="cyan", width=2)
				
			# Draw the Y-axis with labels
			for i in range(5):
				y = self.canvas_height - (i * (self.canvas_height / 4))
				value = min_data_value + (i * (data_range / 4))
				self.canvas.create_line(0, y, 10, y, fill="white")
				self.canvas.create_text(20, y, text=f"{value:.1f}", fill="white", anchor="w")
				
			# Draw the X-axis with labels
			for i in range(0, self.max_points, int(self.max_points / 5)):
				x = i * step_x
				self.canvas.create_line(x, self.canvas_height, x, self.canvas_height - 10, fill="white")
				self.canvas.create_text(x, self.canvas_height - 20, text=f"{i}", fill="white", anchor="n")

	def draw_percent_change_graph(self):
		self.percent_change_canvas.delete("all")
		
		if len(self.percent_changes) > 1:
			step_x = self.canvas_width / (self.max_points - 1)
			max_percent_change = 100
			min_percent_change = -100
			percent_range = max_percent_change - min_percent_change
			
			# Normalize percent change points to fit within canvas height
			normalized_percent_changes = [
				((pc - min_percent_change) / percent_range) * (self.canvas_height - 40) + 20
				for pc in self.percent_changes
			]
			
			# Draw the percent change graph
			for i in range(1, len(normalized_percent_changes)):
				x1 = (i - 1) * step_x
				y1 = self.canvas_height - normalized_percent_changes[i - 1]
				x2 = i * step_x
				y2 = self.canvas_height - normalized_percent_changes[i]
				self.percent_change_canvas.create_line(x1, y1, x2, y2, fill="green", width=2)
				
			# Draw the Y-axis with labels
			for i in range(-4, 5):
				y = self.canvas_height - ((i + 4) * (self.canvas_height / 8))
				value = i * 25
				self.percent_change_canvas.create_line(0, y, 10, y, fill="white")
				self.percent_change_canvas.create_text(20, y, text=f"{value}%", fill="white", anchor="w")
				
			# Draw the X-axis with labels
			for i in range(0, self.max_points, int(self.max_points / 5)):
				x = i * step_x
				self.percent_change_canvas.create_line(x, self.canvas_height, x, self.canvas_height - 10, fill="white")
				self.percent_change_canvas.create_text(x, self.canvas_height - 20, text=f"{i}", fill="white", anchor="n")

	def percent_change(self, new_data):
		return (new_data - self.data_points[-2]) / self.data_points[-2] * 100

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Invalid syntax - \"python3 reader.py <filename>\"")
	root = tk.Tk()
	try:
		with open(sys.argv[1], "rb") as f:
			df = list(map(float, [x for x in zlib.decompress(f.read()).decode("utf-8").split("\r\n") if x not in ("\r", "\n", "\r\n", "", " ")]))
		app = DataReader(root, df)
		root.mainloop()
	except Exception as e:
		print("Error reading file:", e)
		raise e