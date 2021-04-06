#gmail account : sillycoderminesweeper
#password : uQ0{vE8<gZ3$cU4}uH7"uM1#hA9@zA6*

from tkinter import *
import tkinter.ttk as ttk
from ttkthemes import ThemedTk
from tkinter.font import Font
from tkinter import EventType
from tkinter import messagebox
from PIL import ImageTk, Image

from itertools import product
from functools import partial

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import smtplib
import secrets
import base64
import random
import time
import math
import sys
import os

#Counter for timer and bomb_left
class Counter(object):
	def __init__(self):
		self.sec_block = [
             [1, 1, 1, 0, 1, 1, 1],
             [0, 0, 1, 0, 0, 1, 0], 
             [1, 0, 1, 1, 1, 0, 1], 
             [1, 0, 1, 1, 0, 1, 1],
             [0, 1, 1, 1, 0, 1, 0],
             [1, 1, 0, 1, 0, 1, 1],
             [1, 1, 0, 1, 1, 1, 1],
             [1, 0, 1, 0, 0, 1, 0],
             [1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 0, 1, 1]
         ]

	def draw(self, canvas, sec):
		canvas.create_polygon(3, 2, 11, 2, 9, 4, 5, 4, outline='red' if self.sec_block[sec][0] else 'black', fill='red' if self.sec_block[sec][0] else 'black')
		canvas.create_polygon(2, 3, 2, 11, 4, 9, 4, 5, outline='red' if self.sec_block[sec][1] else 'black', fill='red' if self.sec_block[sec][1] else 'black')
		canvas.create_polygon(12, 3, 12, 11, 10, 9, 10, 5, outline='red' if self.sec_block[sec][2] else 'black', fill='red' if self.sec_block[sec][2] else 'black')
		canvas.create_polygon(3, 12, 5, 11, 9, 11, 11, 12, 10, 13, 4, 13, outline='red' if self.sec_block[sec][3] else 'black', fill='red' if self.sec_block[sec][3] else 'black')
		canvas.create_polygon(2, 13, 2, 21, 4, 19, 4, 15, outline='red' if self.sec_block[sec][4] else 'black', fill='red' if self.sec_block[sec][4] else 'black')
		canvas.create_polygon(12, 13, 12, 21, 10, 19, 10, 15, outline='red' if self.sec_block[sec][5] else 'black', fill='red' if self.sec_block[sec][5] else 'black')
		canvas.create_polygon(9, 20, 5, 20, 3, 22, 11, 22, outline='red' if self.sec_block[sec][6] else 'black', fill='red' if self.sec_block[sec][6] else 'black')

#Main Class for the game
class MineSweeper(object):
	#initialize all the required stuff
	def __init__(self, root, difficulty=0):
		#variable
		self.difficulty_data = [(9, 9, 10), (16, 16, 40), (30, 16, 99)]
		self.difficulty = difficulty
		self.width, self.height, self.total_mine = self.difficulty_data[self.difficulty]
		self.root = root
		self.root.config(bg='#C0C0C0')
		self.root.geometry('{}x{}'.format(self.width*20+24, self.height*20+73))
		self.root.resizable(False, False)
		self.is_developer = False
		self.current_dev_pass = None
		self.color = ['#0100FE', '#017F01', '#FE0000', '#010080', '#810102', '#008081', '#000000', '#808080']
		self.unvisited = sum([[(height, width) for width in range(self.width)] for height in range(self.height)], [])
		self.grid = [[0 for j in range(self.width)] for i in range(self.height)]
		self.visited = []
		self.block = []
		self.marked = []
		self.bombed = []
		self.current_time = '000'
		self.bomb_left = str(self.total_mine).zfill(3)
		self.first = True
		self.timer = Counter()
		self.bomb_left_counter = Counter()
		self.timer_start = False
		self.nav_bar_dif_val = IntVar()
		self.nav_bar_dif_val.set(self.difficulty)
		#image
		self.bomb = PhotoImage(file='asset/bomb.png')
		self.flag = PhotoImage(file='asset/flag.png')
		self.smile, self.shock, self.cool, self.died = [PhotoImage(file='asset/{}.png'.format(i)) for i in range(1, 5)]
		#anonymous function
		self.neighbour = lambda x, y: [(y, x) for y, x in [(y+1, x), (y-1, x), (y, x+1), (y, x-1), (y+1, x+1), (y-1, x-1), (y+1, x-1), (y-1, x+1)] if 0<=y<self.height and 0<=x<self.width]
		self.lose = lambda x, y: bool(self.grid[y][x])
		#game record
		if not os.path.exists('minesweeper_record.dat'):
			self.record = [[999, 'Anonymous'], [999, 'Anonymous'], [999, 'Anonymous']]
			with open('minesweeper_record.dat', 'wb') as record_file:
				record_file.write(base64.b64encode(str(self.record).encode('utf-8')))
		else:
			self.record = eval(base64.b64decode(open('minesweeper_record.dat', 'r').read()))
		#menubar
		self.navbar=Menu(self.root)
		self.root.config(menu=self.navbar)
		self.game_menu= Menu(self.navbar, tearoff=0)
		self.navbar.add_cascade(label="Game", menu=self.game_menu)
		self.game_menu.add_command(label="New                     F2", command=lambda: self.cleanup(difficulty=self.difficulty))
		self.game_menu.add_separator()
		self.game_menu.add_radiobutton(label='Beginner', variable=self.nav_bar_dif_val, value=0, command=lambda: self.cleanup(difficulty=0))
		self.game_menu.add_radiobutton(label='Intermidiate', variable=self.nav_bar_dif_val, value=1, command=lambda: self.cleanup(difficulty=1))
		self.game_menu.add_radiobutton(label='Expert', variable=self.nav_bar_dif_val, value=2, command=lambda: self.cleanup(difficulty=2))
		self.game_menu.add_radiobutton(label='Custom...', variable=self.nav_bar_dif_val, value=3, command=self.custom_game)
		self.game_menu.add_separator()
		self.game_menu.add_command(label="Best Times...", command=self.show_record)
		self.game_menu.add_command(label="Statistic...", command=0)
		self.game_menu.add_separator()
		self.game_menu.add_command(label="Exit", command=self.root.quit)
		#widget
		self.grid_border = Label(self.root, relief=SUNKEN, bd=3, bg='#C0C0C0')
		self.top_container_frame = Frame(self.root, relief=SUNKEN, bd=3, bg='#C0C0C0')
		self.top_container = Frame(self.root, relief=FLAT, bg='#C0C0C0')
		self.timer_container = Frame(self.top_container, relief=SUNKEN, bd=1)
		self.bomb_left_counter_container = Frame(self.top_container, relief=SUNKEN, bd=1)
		self.face_button = Button(self.top_container, image=self.smile, relief=RAISED, bd=3, bg='#C0C0C0', command=lambda: self.cleanup(difficulty=self.difficulty))
		self.timer_block1 = Canvas(self.timer_container, width=15, height=25, bg='black', highlightbackground='black', highlightthickness=0)
		self.timer_block2 = Canvas(self.timer_container, width=15, height=25, bg='black', highlightbackground='black', highlightthickness=0)
		self.timer_block3 = Canvas(self.timer_container, width=15, height=25, bg='black', highlightbackground='black', highlightthickness=0)
		self.bomb_left_block1 = Canvas(self.bomb_left_counter_container, width=15, height=25, bg='black', highlightbackground='black', highlightthickness=0)
		self.bomb_left_block2 = Canvas(self.bomb_left_counter_container, width=15, height=25, bg='black', highlightbackground='black', highlightthickness=0)
		self.bomb_left_block3 = Canvas(self.bomb_left_counter_container, width=15, height=25, bg='black', highlightbackground='black', highlightthickness=0)
		self.timer.draw(self.timer_block1, 0)
		self.timer.draw(self.timer_block2, 0)
		self.timer.draw(self.timer_block3, 0)
		self.bomb_left_counter.draw(self.bomb_left_block1, int(self.bomb_left[0]))
		self.bomb_left_counter.draw(self.bomb_left_block2, int(self.bomb_left[1]))
		self.bomb_left_counter.draw(self.bomb_left_block3, int(self.bomb_left[2]))
		self.root.bind('<F2>', lambda e: self.cleanup(e, difficulty=self.difficulty))
		self.root.bind('<Control-Alt-d><Control-Alt-v>', self.developer_verify)
		self.root.bind('<Control-Alt-d><Control-Alt-r>', self.developer_register)
		self.root.bind('<Control-Alt-d><Control-Alt-c>', self.developer_create)

	def developer_register(self, e):
		self.current_dev_pass = secrets.token_hex(nbytes=64)

		mail=smtplib.SMTP('smtp.gmail.com', 587)
		mail.ehlo()
		mail.starttls()
		message = MIMEMultipart("alternative")
		message["Subject"] = "Minesweeper Registration Code"
		message["From"] = 'sillycoderminesweeper@gmail.com'
		message["To"] = 'melvinchia623600@gmail.com'
		message.attach(MIMEText(r"<html> <body> <p>Hi,<br> This is your Minesweeper registration code:</p> <br/> <strong>"+self.current_dev_pass+"</strong> </body> </html> ", "html"))
		
		sender='sillycoderminesweeper@gmail.com'
		recipient='melvinchia623600@gmail.com'
		mail.login('sillycoderminesweeper@gmail.com', r'uQ0{vE8<gZ3$cU4}uH7"uM1#hA9@zA6*')
		mail.sendmail('sillycoderminesweeper@gmail.com', 'melvinchia623600@gmail.com', message.as_string())
		mail.close()

		messagebox.showwarning('Registration Code Sent', 'Registration code has been sent to your mail box.\nGo and check it out!')

	def developer_create(self, e):
		dev_code_verify_win = ThemedTk(theme='breeze')

		registration_code_label = ttk.Label(dev_code_verify_win, text='Enter registration code:')
		registration_code_input = ttk.Entry(dev_code_verify_win, width=64)
		registration_proceed_btn = ttk.Button(dev_code_verify_win, text='Register')

		registration_code_label.grid(row=0, column=0, padx=10, pady=10, sticky=W)
		registration_code_input.grid(row=1, column=0, padx=10, pady=(0, 10))

		dev_code_verify_win.mainloop()

	def developer_verify(self, e):
		dev_verify_win = ThemedTk(theme='breeze')
		dev_verify_win.resizable(False, False)
		dev_verify_win.title('Dev Login')

		dev_key_label = ttk.Label(dev_verify_win, text='Dev Key:')
		dev_pass_label = ttk.Label(dev_verify_win, text='Password:')

		dev_key_input = ttk.Entry(dev_verify_win, width=30)
		dev_pass_input = ttk.Entry(dev_verify_win, show='\u25CF', width=30)

		cancel_button = ttk.Button(dev_verify_win, text='Cancel', command=dev_verify_win.destroy)
		OK_button = ttk.Button(dev_verify_win, text='OK', command=lambda: self.dev_verify_second(dev_key_input.get(), dev_pass_input.get(), dev_verify_win))

		dev_key_label.grid(row=0, column=0, padx=10, pady=(10, 0))
		dev_pass_label.grid(row=1, column=0, padx=10, pady=(5, 10))

		dev_key_input.grid(row=0, column=1, columnspan=2, padx=10, pady=(10, 0))
		dev_pass_input.grid(row=1, column=1, columnspan=2, padx=10, pady=(5, 10))

		cancel_button.grid(row=2, column=1, sticky=E, pady=(0, 10))
		OK_button.grid(row=2, column=2, sticky=E, pady=(0, 10), padx=(0, 10))

		dev_verify_win.mainloop()

	def dev_verify_second(self, key, pass_, win):
		win.destroy()
		print(key, pass_)

	#unbind all key after game stop
	def unbind_all(self, current_y, current_x):
		self.block[current_y][current_x].unbind('<Button-3>')
		self.block[current_y][current_x].unbind('<ButtonPress-1>')
		self.block[current_y][current_x].unbind('<ButtonRelease-1>')
	
	#check update grid status after user left clicked
	def check_grid(self, current_y, current_x, recur=False):
		#generate bomb after player's first click
		if self.first:
			self.bomb_coor = random.sample(sum([[(y, x) for x in range(self.width) if (y, x) not in self.neighbour(current_x, current_y)+[(current_y, current_x)]] for y in range(self.height)], []), self.total_mine)
			for y, x in self.bomb_coor: self.grid[y][x] = 1
			self.run_time = time.time()
			self.timer_start = True
			threading.Thread(target=self.start_timer).start()
		self.first = False

		#check if user lose
		if self.lose(current_x, current_y) and not recur:
			self.timer_start = False
			for y in range(len(self.block)):
				for x in range(len(self.block[0])):
					self.block[y][x].config(state=DISABLED, text='' if self.grid[y][x] else self.block[y][x].cget('text'), disabledforeground='black' if self.grid[y][x] else self.block[y][x]['disabledforeground'])
					self.bombed.append(Label(self.root, image=self.bomb, relief=RAISED, bd=3)) if self.grid[y][x] else None
					self.bombed[-1].place(x=13+x*20, y=63+y*20, width=20, height=20) if self.grid[y][x] else None
					self.unbind_all(y, x)
					root.update()
			return

		#check if player clicked a cell that is not where the bombs is:
			#if all the neighbour cells is not bomb, uncover the cell with no number and do recursion to all the neighbour cell
			#if there are/is bomb(s) in neighbour cells: then uncover the that cell with number of bomb in neighbour cell inside
		self.bomb_count = len([1 for y, x in self.neighbour(current_x, current_y) if self.grid[y][x]])
		if self.bomb_count:
			self.block[current_y][current_x].config(state=DISABLED, text=str(self.bomb_count), disabledforeground=self.color[self.bomb_count])
			root.update()
			self.visited.append((current_y, current_x))
			self.unvisited.remove((current_y, current_x))
			self.unbind_all(current_y, current_x)
		else:
			self.block[current_y][current_x].config(state=DISABLED, bg='#C0C0C0', relief=RIDGE, bd=1, highlightbackground='#C0C0C0')
			root.update()
			self.visited.append((current_y, current_x))
			self.unvisited.remove((current_y, current_x))
			self.unbind_all(current_y, current_x)
			for cell_y, cell_x in self.neighbour(current_x, current_y):
				if not self.grid[current_y][current_x] and (cell_y, cell_x) not in self.visited and self.block[cell_y][cell_x]['text'] != 'O':
					self.check_grid(cell_y, cell_x, recur=True)

		#check if player win the game
		if sorted(self.unvisited) == sorted(self.bomb_coor):
			self.timer_start = False
			self.face_button.config(image=self.cool)
			self.bomb_left = '000'
			self.update_bomb_left()
			for y in range(len(self.block)):
				for x in range(len(self.block[0])):
					self.block[y][x].config(command=0)
					self.unbind_all(y, x)
			self.update_record()

	def update_record(self):
		if self.difficulty < 3 and self.record[self.difficulty][0] > int(self.current_time):
			self.record[self.difficulty][0] = int(self.current_time)-1
			self.record[self.difficulty][1] = self.ask_record_name()
			with open('minesweeper_record.dat', 'wb') as record_file:
				record_file.write(base64.b64encode(str(self.record).encode('utf-8')))

	#mark a flag when user right click in a covered cell
	#remove the flag when user right click on a covered cell that have flag on top of it
	def mark_bomb(self, current_y, current_x, e):
		if self.block[current_y][current_x]['text'] != 'O':
			self.marked.append((current_y, current_x))
			self.block[current_y][current_x].config(text='O', image=self.flag, foreground='#000000', command=0)
			self.bomb_left = str(int(self.bomb_left)-1).zfill(3) if int(self.bomb_left)-1 >= 0 else '000'
			self.update_bomb_left()

		elif self.block[current_y][current_x]['text'] == 'O':
			self.marked.remove((current_y, current_x))
			self.temp_command = partial(self.check_grid, current_y, current_x)
			self.block[current_y][current_x].config(image='', text='', command=self.temp_command)
			self.bomb_left = str(int(self.bomb_left)+1).zfill(3) if int(self.bomb_left)+1 <= self.total_mine else str(self.total_mine).zfill(3)
			self.update_bomb_left()

	#when user click a button, change the face to shock
	#when user died, change the face to died
	#when user release the click, change the face back to smile
	#when user win, change the face to cool face (code is not in this function)
	def change_face(self, current_y, current_x, e):
		if e.type == EventType.ButtonPress:
			self.face_button.config(image=self.shock)
		elif e.type == EventType.ButtonRelease:
			if self.grid[current_y][current_x] and (current_y, current_x) not in self.marked:
				self.face_button.config(image=self.died)
			else:
				self.face_button.config(image=self.smile)

	#function to update the bomb left counter
	def update_bomb_left(self):
		self.bomb_left_block1.delete('all')
		self.bomb_left_block2.delete('all')
		self.bomb_left_block3.delete('all')
		self.bomb_left_counter.draw(self.bomb_left_block1, int(self.bomb_left[0]))
		self.bomb_left_counter.draw(self.bomb_left_block2, int(self.bomb_left[1]))
		self.bomb_left_counter.draw(self.bomb_left_block3, int(self.bomb_left[2]))

	#start the timer after user first click in game grid
	def start_timer(self):
		if not self.timer_start: return
		self.timer_block1.delete('all')
		self.timer_block2.delete('all')
		self.timer_block3.delete('all')
		self.timer.draw(self.timer_block1, int(self.current_time[0]))
		self.timer.draw(self.timer_block2, int(self.current_time[1]))
		self.timer.draw(self.timer_block3, int(self.current_time[2]))
		self.current_time = str(math.ceil(time.time()-self.run_time)).zfill(3)
		self.root.after(1000, self.start_timer)
		self.timer_start = True

	#window to prompt user to input width, height, and mine amount in custom game
	def custom_game(self):		

		#change the width, height, and total_mine value and soft initialize the game (without reinitialize all stuff)
		def return_custom():
			self.width, self.height, self.total_mine = int(width_input.get()), int(height_input.get()), int(bomb_amount_input.get())
			custom_prompt.destroy()
			self.cleanup(difficulty=3)

		#initialize the prompt window (I used a themed window so it looks better)
		custom_prompt = ThemedTk(theme='breeze')
		custom_prompt.geometry('265x166')
		custom_prompt.title('Custom')
		custom_prompt.focus_force()

		#initialize all the widget inside the window
		height_label = ttk.Label(custom_prompt, text='Height:')
		width_label = ttk.Label(custom_prompt, text='Width:')
		bomb_amount_label = ttk.Label(custom_prompt, text='Mines:')

		width_input = ttk.Spinbox(custom_prompt, width=5, from_=9, to=24)
		height_input = ttk.Spinbox(custom_prompt, width=5, from_=9, to=30)
		bomb_amount_input = ttk.Spinbox(custom_prompt, width=5, from_=9, to=99)

		ok_button = ttk.Button(custom_prompt, text='OK', command=return_custom)
		cancel_button = ttk.Button(custom_prompt, text='Cancel', command=custom_prompt.destroy)

		#place them one by one inside the window (grid system will perform better here (because I don't need to calculate x and y lol))
		height_label.grid(row=0, column=0, padx=15, pady=(30, 0))
		width_label.grid(row=1, column=0, padx=15, pady=(5, 0))
		bomb_amount_label.grid(row=2, column=0, padx=15, pady=(5, 0))

		height_input.grid(row=0, column=1, padx=15, pady=(30, 0))
		width_input.grid(row=1, column=1, padx=15, pady=(5, 0))
		bomb_amount_input.grid(row=2, column=1, padx=15, pady=(5, 0))

		ok_button.grid(row=0, column=2, pady=(30, 0))
		cancel_button.grid(row=2, column=2, pady=(5, 0))

		#initialize the value in the input box to current value
		width_input.set(self.width)
		height_input.set(self.height)
		bomb_amount_input.set(self.total_mine)

		#show the window up
		custom_prompt.mainloop()

	#soft initialize the game and reset all the previous game data
	def cleanup(self, *args, difficulty=0):
		[i.place_forget() for i in self.bombed]
		self.width, self.height, self.total_mine = self.difficulty_data[difficulty] if difficulty != 3 else \
												  (
												  	self.width if self.width <= 30 else 30, 
												   	self.height if self.height <= 24 else 24, 
												   	self.total_mine if self.total_mine <= 99 else 99
												  )
		self.root.geometry('{}x{}'.format(self.width*20+24, self.height*20+73))
		self.unvisited = sum([[(y, x) for x in range(self.width)] for y in range(self.height)], [])
		self.visited = []
		self.marked = []
		self.bombed = []
		self.first = True
		self.grid = [[0 for x in range(self.width)] for y in range(self.height)]
		self.face_button.config(image=self.smile)
		self.timer_start = False
		self.current_time = '000'
		self.timer.draw(self.timer_block1, 0)
		self.timer.draw(self.timer_block2, 0)
		self.timer.draw(self.timer_block3, 0)
		self.bomb_left = str(self.total_mine).zfill(3)
		self.update_bomb_left()

		#we don't need to initialize all stuff if new game difficulty is the same as the previous one
		if difficulty == self.difficulty and self.difficulty != 3:
			for y in range(len(self.block)):
				for x in range(len(self.block[0])):
					self.temp_command = partial(self.check_grid, y, x)
					self.right_click_event = partial(self.mark_bomb, y, x)
					self.change_face_event = partial(self.change_face, y, x)
					self.block[y][x].config(command=self.temp_command, relief=RAISED, bd=3, font=Font(weight='bold', family='small fonts', size=7), bg='SystemButtonFace', state=NORMAL, text='', image='')
					self.block[y][x].bind('<Button-3>', self.right_click_event)
					self.block[y][x].bind('<ButtonPress-1>', self.change_face_event)
					self.block[y][x].bind('<ButtonRelease-1>', self.change_face_event)
		#but we need to initialize more stuff when the gamemode is custom or the gamemode changed
		else:
			self.difficulty = difficulty
			self.timer_container.place(x=self.width*20-3.5, y=3.5, width=47, height=27, anchor=NE)
			self.face_button.place(x=(self.width*20+2)//2-2, y=17, anchor=CENTER, width=25, height=25)
			self.top_container_frame.place(x=10, y=10, width=self.width*20+6, height=40)
			self.top_container.place(x=12, y=12, width=self.width*20+2, height=36)
			self.grid_border.place(x=11, y=60, width=self.width*20+4, height=self.height*20+4)
			for y in range(len(self.block)):
				for x in range(len(self.block[y])):
					self.block[y][x].place_forget()
			self.block.clear()
			for y in range(self.height):
				self.block.append([])
				for x in range(self.width):
					self.temp_command = partial(self.check_grid, y, x)
					self.right_click_event = partial(self.mark_bomb, y, x)
					self.change_face_event = partial(self.change_face, y, x)
					self.block[y].append(Button(self.root, command=self.temp_command, relief=RAISED, bd=3, font=Font(weight='bold', family='small fonts', size=7)))
					self.block[y][x].bind('<Button-3>', self.right_click_event)
					self.block[y][x].bind('<ButtonPress-1>', self.change_face_event)
					self.block[y][x].bind('<ButtonRelease-1>', self.change_face_event)
			for y in range(len(self.block)):
				for x in range(len(self.block[y])):
					self.block[y][x].place(x=13+x*20, y=62+y*20, width=20, height=20)
					self.root.update()

	def ask_record_name(self):

		def return_name():
			global return_, name
			return_ = True
			name = ask_name_input.get()
			prompt_record_name.destroy()

		global return_
		return_ = False
			
		prompt_record_name = ThemedTk(theme='breeze')
		prompt_record_name.title('Fastest Time')

		ask_name_label = ttk.Label(prompt_record_name, text='You have the fastest time for Intermidiate level.\nPlease enter your name:', anchor=CENTER, justify=CENTER)
		ask_name_input = ttk.Entry(prompt_record_name)
		ok_button = ttk.Button(prompt_record_name, text='OK', command=return_name)

		ask_name_label.grid(row=0, column=0, padx=10, pady=10)
		ask_name_input.grid(row=1, column=0, padx=10)
		ok_button.grid(row=2, column=0, padx=10, pady=10)

		while not return_:
			try:
				prompt_record_name.update()
			except: pass
		return name

	#load the game record window
	def show_record(self):
		#initialize the prompt window (I used a themed window so it looks better)
		record_win = ThemedTk(theme='breeze')
		record_win.title('Game Record')
		record_win.geometry('292x106')
		record_win.focus_force()

		beginner_label = Label(record_win, text='Beginner:')
		intermidiate_label = Label(record_win, text='Intermidiate:')
		expert_label = Label(record_win, text='Expert:')

		beginner_best = Label(record_win, text='{} seconds'.format(self.record[0][0]))
		intermidiate_best = Label(record_win, text='{} seconds'.format(self.record[1][0]))
		expert_best = Label(record_win, text='{} seconds'.format(self.record[2][0]))

		beginner_name = Label(record_win, text=self.record[0][1])
		intermidiate_name = Label(record_win, text=self.record[1][1])
		expert_name = Label(record_win, text=self.record[2][1])

		beginner_label.grid(row=0, column=0, padx=15, pady=(20, 0), sticky=W)
		intermidiate_label.grid(row=1, column=0, padx=15, sticky=W)
		expert_label.grid(row=2, column=0, padx=15, sticky=W)

		beginner_best.grid(row=0, column=1, pady=(20, 0), sticky=W)
		intermidiate_best.grid(row=1, column=1, sticky=W)
		expert_best.grid(row=2, column=1, sticky=W)

		beginner_name.grid(row=0, column=2, pady=(20, 0), padx=(15, 0), sticky=W)
		intermidiate_name.grid(row=1, column=2, padx=(15, 0), sticky=W)
		expert_name.grid(row=2, column=2, padx=(15, 0), sticky=W)

		record_win.update()

		record_win.mainloop()

	#play the game! place down all the widget and ready for infinite fun!
	def play(self):
		for y in range(self.height):
			self.block.append([])
			for x in range(self.width):
				self.temp_command = partial(self.check_grid, y, x)
				self.right_click_event = partial(self.mark_bomb, y, x)
				self.change_face_event = partial(self.change_face, y, x)
				self.block[y].append(Button(self.root, command=self.temp_command, relief=RAISED, bd=3, font=Font(weight='bold', family='small fonts', size=7)))
				self.block[y][x].bind('<Button-3>', self.right_click_event)
				self.block[y][x].bind('<ButtonPress-1>', self.change_face_event)
				self.block[y][x].bind('<ButtonRelease-1>', self.change_face_event)
		self.timer_container.place(x=self.width*20-3.5, y=3.5, width=47, height=27, anchor=NE)
		self.bomb_left_counter_container.place(x=3.5, y=3.5, width=47, height=27)
		self.timer_block1.place(x=0, y=0)
		self.timer_block2.place(x=15, y=0)
		self.timer_block3.place(x=30, y=0)
		self.bomb_left_block1.place(x=0, y=0)
		self.bomb_left_block2.place(x=15, y=0)
		self.bomb_left_block3.place(x=30, y=0)
		self.top_container_frame.place(x=10, y=10, width=self.width*20+6, height=40)
		self.top_container.place(x=12, y=12, width=self.width*20+2, height=36)
		self.face_button.place(x=(self.width*20+2)//2-2, y=17, anchor=CENTER, width=25, height=25)
		self.grid_border.place(x=11, y=60, width=self.width*20+4, height=self.height*20+4)
		for y in range(len(self.block)):
			for x in range(len(self.block[y])):
				self.block[y][x].place(x=13+x*20, y=62+y*20, width=20, height=20)
				self.root.update()

#if this game is not imported(run by itself), then start the game (no one will use it as module, believe me (but you can do it if you want))
if __name__ == '__main__':
	root = Tk()
	root.title('Minesweeper')
	#MineSweeper_difficulty(root).generate_ui()
	MineSweeper(root, difficulty=0).play()
	root.mainloop()
