import tkinter as tk


class App(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("Test Tkinter")
		self.geometry("300x200")

		self.label = tk.Label(self, text="Ciao, Tkinter!")
		self.label.pack(pady=20)

		self.button = tk.Button(self, text="Cliccami", command=self.on_button_click)
		self.button.pack(pady=20)

	def on_button_click(self):
		self.label.config(text="Bottone cliccato!")

if __name__ == "__main__":
	app = App()
	app.mainloop()