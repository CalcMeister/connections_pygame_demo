import pygame as pg
import random
import datetime

test_set = {
'Flowering Trees':['Dogwood','Wisteria','Crape Myrtle', 'Redbud'],
'McLaren Models':['Senna','Saber','Speedtail','Artura'],
'Shades Of Green':['Chartreuse','Aquamarine','Jade','Celadon'],
'Roads In Detroit':['Earle','Hayes','Lahser','Mack']
}

###Classes

class Game:
	def __init__(self, groups:dict, **kwargs):
		#groups should be in the form {'name':[word1, word2, word3, word4]...}
		self.guesses = kwargs.get('guesses', 4)
		self.groups = groups
		self.words = sum(list(list(Word(w, group_name) for w in groups[group_name]) for group_name in groups), [])
		self.completed_groups = []
		self.guess_history = []
		self.shuffle()
		self.hint = None

	def select(self, index):
		if self.words[index].is_selected or self.num_selected() < 4:
			self.words[index].toggle_selection()
			return True
		else:
			return False

	def deselect_all(self):
		for w in self.words:
			w.is_selected = False

	def num_selected(self):
		return sum(i.is_selected for i in self.words)

	def submit(self):
		selection = set(i for i in self.words if i.is_selected)
		if self.num_selected() == 4:
			selected_groups = set(i.group_name for i in selection)
			if len(selected_groups) == 1:
				completed_group_name = selected_groups.pop()
				self.completed_groups.append([completed_group_name, self.groups[completed_group_name]])
				self.words = list(i for i in self.words if not(i.is_selected))
				self.hint = None
			elif selection not in self.guess_history:
				self.guesses -= 1
				if max(sum(i.group_name == list(self.groups.keys())[j] for i in selection) for j in range(4)) == 3:
					self.hint = 'One away!'
				else:
					self.hint = None
			else:
				self.hint = 'Already guessed!'

			self.guess_history.append(selection)

			if self.is_game_over():
				if self.guesses == 0:
					self.deselect_all()
					self.hint = 'Next time!'
				elif len(self.guess_history) == 4:
					self.hint = 'Perfect!'
				elif len(self.guess_history) == 7:
					self.hint = 'Close one!'
				else:
					print('bruh')
					self.hint = 'Great!'

	def shuffle(self):
		random.shuffle(self.words)

	def is_game_over(self):
		return len(self.completed_groups) == 4 or self.guesses < 1

class Word:
	def __init__(self, w:str, group_name:str):
		self.w = w
		self.group_name = group_name
		self.is_selected = False

	def __lt__(self, other):
		return self.group_name < other.group_name

	def toggle_selection(self):
		self.is_selected = not(self.is_selected)

class Screenspace:
	def __init__(self, **kwargs):
		self.screen_size = kwargs.get('screen_size', (600,600))
		self.buttons = kwargs.get('buttons', [])
		self.tickrate = kwargs.get('tickrate', 60)

		self.COLORS = {
			'blue':(176,196,239),
			'yellow':(249,223,109),
			'green':(160,195,90),
			'purple':(187,129,197),
			'beige':(239,239,230),
			'light-gray':(127,127,127),
			'dark-gray':(90,89,78)
		}
		self.COLOR_ORDER = {
			0:'blue',
			1:'yellow',
			2:'green',
			3:'purple'
		}

		pg.init()
		self.surface = pg.display.set_mode(self.screen_size)
		self.clock = pg.time.Clock()

	def tick(self):
		pg.display.flip()
		self.clock.tick(self.tickrate)

	def detect_clicked_button(self, events):
		# IF the left mouse button is clicked:
		# will return the name of first clickable button the mouse is currently hovering over.
		# will return None if the first clicked button is not clickable.
		if max((ev.type == pg.MOUSEBUTTONUP for ev in events), default=False):
			mouse_pos = pg.mouse.get_pos()
		else:
			return None

		for b in self.buttons:
			if b.screen_position[0][0] <= mouse_pos[0] <= b.screen_position[0][0] + b.screen_position[1][0] and b.screen_position[0][1] <= mouse_pos[1] <= b.screen_position[0][1] + b.screen_position[1][1]:
				if b.is_clickable:
					return b.name
				else:
					return None

	def draw_centered_text(self, position, text, font, color='black'):
		rendered_text = font.render(text, True, color, None)
		self.surface.blit(rendered_text, rendered_text.get_rect(center=position))

	def draw_start_screen(self):
		# background color
		self.surface.fill((179, 167, 254))

		# logo
		white_squares = ((260,160),(280,140),(300,100),(320,120))
		pg.draw.rect(self.surface, (187, 112, 196), pg.Rect(260, 100, 80, 80))
		for s in white_squares:
			pg.draw.rect(self.surface, 'white', pg.Rect(s, (20,20)))
			pg.draw.rect(self.surface, 'black', pg.Rect((s[0]-2, s[1]-2), (24,24)), 4, 4)
		for i in (120,140,160):
			pg.draw.line(self.surface, 'black', (260, i), (340, i), 4)
		pg.draw.rect(self.surface, 'black', pg.Rect(258, 98, 84, 84), 4, 4)

		# play button
		pg.draw.rect(self.surface, 'black', pg.Rect((240, 350), (120, 40)), 0, 20)
		self.buttons = [Button('play', ((240, 350), (120, 40)))]

		# text and date
		font = pg.font.Font(None, 50)
		self.draw_centered_text((300,240), 'Connections', font)
		font = pg.font.Font(None, 25)
		self.draw_centered_text((300,280), 'Group words that share a common thread.', font)
		self.draw_centered_text((300,370), 'Play', font, 'white')
		date = datetime.datetime.now().strftime('%B %d, %Y')
		self.draw_centered_text((300,500), date, font)

	def draw_game_screen(self, game):
		COLORS = {
			'blue':(176,196,239),
			'yellow':(249,223,109),
			'green':(160,195,90),
			'purple':(187,129,197),
			'beige':(239,239,230),
			'light-gray':(127,127,127),
			'dark-gray':(90,89,78)
		}
		COLOR_ORDER = {
			0:'blue',
			1:'yellow',
			2:'green',
			3:'purple'
		}


		font = pg.font.Font(None, 23)
		small_font = pg.font.Font(None, 21)

		self.buttons = []

		# background color
		self.surface.fill('white')

		# completed groups
		font = pg.font.Font(None, 23)
		for i in range(len(game.completed_groups)):
			pg.draw.rect(self.surface, COLORS[COLOR_ORDER[i]], pg.Rect((44, 70*i+104), (516, 66)), 0, 7)
			self.draw_centered_text((300,70*i+124), game.completed_groups[i][0].upper(), font)
			self.draw_centered_text((300,70*i+148), str(game.completed_groups[i][1]).strip('[]\'').replace('\', \'', ', ').upper(), small_font)

		# words
		for i in range(len(game.completed_groups), 4):
			for j in range(4):
				word_list_index = 4*(i-len(game.completed_groups))+j
				word = game.words[word_list_index]
				box_position = ((130*j+44, 70*i+104), (126, 66))
				pg.draw.rect(self.surface, {False:COLORS['beige'], True:COLORS['dark-gray']}[word.is_selected], pg.Rect(box_position[0], box_position[1]), 0, 7)
				self.draw_centered_text((130*j+105, 70*i+135), word.w.upper(), font, {False:'black', True:'white'}[word.is_selected])
				self.buttons.append(Button('word_'+str(word_list_index), box_position))

		self.draw_centered_text((300,50), 'Create four groups of four!', small_font)
		self.draw_centered_text((300,550), game.hint, small_font)

		# mistakes remaining:
		if not(game.is_game_over()):
			self.draw_centered_text((255,420), 'Mistakes remaining:', small_font)
			for i in range(game.guesses):
				pg.draw.circle(self.surface, COLORS['dark-gray'], (20*i+345,420), 7)

		# shuffle button
		color = {True:'black', False:COLORS['light-gray']}[not(game.is_game_over())]
		pg.draw.rect(self.surface, color, pg.Rect((170, 450), (70, 40)), 1, 20)
		self.draw_centered_text((205,470), 'Shuffle', small_font, color)
		self.buttons.append(Button('shuffle', ((170, 450), (70, 40))))

		# deselect button
		color = {True:'black', False:COLORS['light-gray']}[game.num_selected() > 0]
		pg.draw.rect(self.surface, color, pg.Rect((250, 450), (100, 40)), 1, 20)
		self.draw_centered_text((300,470), 'Deselect all', small_font, color)
		self.buttons.append(Button('deselect all', ((250, 450), (100, 40))))

		# submit button
		color = {True:'black', False:COLORS['light-gray']}[game.num_selected() == 4]
		pg.draw.rect(self.surface, color, pg.Rect((360, 450), (70, 40)), 1, 20)
		self.draw_centered_text((395,470), 'Submit', small_font, color)
		self.buttons.append(Button('submit', ((360, 450), (70, 40))))

		# continue button
		if game.is_game_over():
			# pg.draw.rect(self.surface, 'black', pg.Rect((475, 555), (110, 30)), 1, 5)
			self.draw_centered_text((530,570), 'See results ->', small_font)
			self.buttons.append(Button('results', ((475,555), (110,30))))


	def draw_results_screen(self, game):
		# background color
		self.surface.fill('white')

		big_font = pg.font.Font(None, 50)
		small_font = pg.font.Font(None, 21)

		colors = {list(game.groups.keys())[i]:self.COLORS[self.COLOR_ORDER[i]] for i in range(4)}

		self.buttons = []

		self.draw_centered_text((300,140), game.hint, big_font)
		pg.draw.line(self.surface, 'black', (150, 200), (450, 200), 1)

		# guesses
		for g in range(len(game.guess_history)):
			guess = sorted(list(game.guess_history[g]))
			for i in range(4):
				pg.draw.rect(self.surface, colors[guess[i].group_name], pg.Rect((24*i+260, 26*g+250), (24, 24)), 0, 4)


		# back button
		self.draw_centered_text((530,570), 'Back to puzzle <-', small_font)
		self.buttons.append(Button('puzzle', ((475,555), (110,30))))

class Button:
	def __init__(self, name:str, screen_position:tuple, is_clickable=True):
		# screen position will be in the format ((x, y), (size_x, size_y))
		self.name = name
		self.screen_position = screen_position
		self.is_clickable = is_clickable

###Loop

screen = Screenspace()
game = Game(test_set)

current_screen = 'start'
# can be 'start', 'play', or 'results'

events = []
while all(event.type != pg.QUIT for event in events):
	events = pg.event.get()
	click = screen.detect_clicked_button(events)

	if current_screen == 'start':
		if click == 'play':
			current_screen = 'play'

		screen.draw_start_screen()

	elif current_screen == 'play':
		if click is not None:
			if click[:5] == 'word_':
				game.select(int(click[5:]))
			elif click == 'shuffle':
				game.shuffle()
			elif click == 'deselect all':
				game.deselect_all()
			elif click == 'submit':
				game.submit()
			elif click == 'results':
				current_screen = 'results'

		screen.draw_game_screen(game)

	elif current_screen == 'results':
		if click == 'puzzle':
			current_screen = 'play'

		screen.draw_results_screen(game)

	screen.tick()

pg.quit()
