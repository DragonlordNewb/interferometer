import tkinter as tk
import random
import time
import socket

class InterferometerServer:
	def __init__(self, root):
		self.root = root
		self.root.title("Live Graph with Tkinter")

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		hn = socket.gethostname()
		ip = socket.gethostbyname(hn)
		self.sock.bind((ip, 7777))
		
		self.canvas_width = 800
		self.canvas_height = 400
		self.max_points = 10
		
		self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
		self.canvas.pack()
		
		self.label = tk.Label(root, text="Last Data Point: N/A", font=("Helvetica", 16))
		self.label.pack()
		
		self.data_points = []

		self.graph_min = -1
		self.graph_max = -1
		
		self.update_graph()

	def update_graph(self):
		# Simulate data collection
		raw_bytes = self.sock.recv(64)
		raw_string = raw_bytes.decode("utf-8")
		spl = raw_string.split(" ")
		new_data = float(spl[0])
		delta_t = int(spl[1])
		self.data_points.append(new_data)
		
		# Update label
		self.label.config(text=f"Last Data Point: {new_data}")
		
		# Ensure we only keep the last max_points data points
		if len(self.data_points) > self.max_points:
			self.data_points.pop(0)
		
		self.draw_graph()
		
		# Call this method again after 1000 ms (1 second)
		self.root.after(10, self.update_graph)
	
	def draw_graph(self):
		self.canvas.delete("all")
		
		if len(self.data_points) > 1:
			step_x = self.canvas_width / (self.max_points - 1)
			max_data_value = min_data_value = None
			if (self.graph_max == -1 or self.graph_min == -1):
				max_data_value = self.graph_max = max(self.data_points) + 10
				min_data_value = self.graph_min = min(self.data_points) - 10
			else:
				max_data_value = self.graph_max = max(max(self.data_points), self.graph_max)
				min_data_value = self.graph_min = min(min(self.data_points), self.graph_min)
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
				self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)

if __name__ == "__main__":
	root = tk.Tk()
	app = InterferometerServer(root)
	root.mainloop()
