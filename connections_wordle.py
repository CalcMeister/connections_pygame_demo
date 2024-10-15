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
			else:
				self.hint = 'Already guessed!'

			self.guess_history.append(selection)

			if len(self.completed_groups) == 4:
				print(len(self.guess_history))
				if len(self.guess_history) == 4:
					self.hint == 'Perfect!'
				elif len(self.guess_history) == 7:
					self.hint == 'Close one!'
				else:
					self.hint == 'Great!'
			elif self.guesses == 0:
				self.hint == 'Next time!'

	def shuffle(self):
		random.shuffle(self.words)

class Word:
	def __init__(self, w:str, group_name:str):
		self.w = w
		self.group_name = group_name
		self.is_selected = False

	def toggle_selection(self):
		self.is_selected = not(self.is_selected)

class Screenspace:
	def __init__(self, screen_size, **kwargs):
		self.screen_size = screen_size
		self.buttons = kwargs.get('buttons', [])

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

class Button:
	def __init__(self, name:str, screen_position:tuple, is_clickable=True):
		# screen position will be in the format ((x, y), (size_x, size_y))
		self.name = name
		self.screen_position = screen_position
		self.is_clickable = is_clickable

###Functions

def draw_centered_text(surface, position, text, font, color='black'):
	rendered_text = font.render(text, True, color, None)
	surface.blit(rendered_text, rendered_text.get_rect(center=position))

def draw_start_screen(surface, screen):
	# background color
	surface.fill((179, 167, 254))

	# logo
	white_squares = ((260,160),(280,140),(300,100),(320,120))
	pg.draw.rect(surface, (187, 112, 196), pg.Rect(260, 100, 80, 80))
	for s in white_squares:
		pg.draw.rect(surface, 'white', pg.Rect(s, (20,20)))
		pg.draw.rect(surface, 'black', pg.Rect((s[0]-2, s[1]-2), (24,24)), 4, 4)
	for i in (120,140,160):
		pg.draw.line(surface, 'black', (260, i), (340, i), 4)
	pg.draw.rect(surface, 'black', pg.Rect(258, 98, 84, 84), 4, 4)

	# play button
	pg.draw.rect(surface, 'black', pg.Rect((240, 350), (120, 40)), 0, 20)
	screen.buttons = [Button('play', ((240, 350), (120, 40)))]

	# text and date
	font = pg.font.Font(None, 50)
	draw_centered_text(surface, (300,240), 'Connections', font)
	font = pg.font.Font(None, 25)
	draw_centered_text(surface, (300,280), 'Group words that share a common thread.', font)
	draw_centered_text(surface, (300,370), 'Play', font, 'white')
	date = datetime.datetime.now().strftime('%B %d, %Y')
	draw_centered_text(surface, (300,500), date, font)

def draw_game_screen(surface, game, screen):
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

	screen.buttons = []

	# background color
	surface.fill('white')

	# completed groups
	font = pg.font.Font(None, 23)
	for i in range(len(game.completed_groups)):
		pg.draw.rect(surface, COLORS[COLOR_ORDER[i]], pg.Rect((44, 70*i+104), (516, 66)), 0, 7)
		draw_centered_text(surface, (300,70*i+124), game.completed_groups[i][0].upper(), font)
		draw_centered_text(surface, (300,70*i+148), str(game.completed_groups[i][1]).strip('[]\'').replace('\', \'', ', ').upper(), small_font)

	# words
	for i in range(len(game.completed_groups), 4):
		for j in range(4):
			word_list_index = 4*(i-len(game.completed_groups))+j
			word = game.words[word_list_index]
			box_position = ((130*j+44, 70*i+104), (126, 66))
			pg.draw.rect(surface, {False:COLORS['beige'], True:COLORS['dark-gray']}[word.is_selected], pg.Rect(box_position[0], box_position[1]), 0, 7)
			draw_centered_text(surface, (130*j+105, 70*i+135), word.w.upper(), font, {False:'black', True:'white'}[word.is_selected])
			screen.buttons.append(Button('word_'+str(word_list_index), box_position))

	draw_centered_text(surface, (300,50), 'Create four groups of four!', small_font)
	draw_centered_text(surface, (300,550), game.hint, small_font)

	# mistakes remaining:
	draw_centered_text(surface, (255,420), 'Mistakes remaining:', small_font)
	for i in range(game.guesses):
		pg.draw.circle(surface, COLORS['dark-gray'], (20*i+345,420), 7)

	# shuffle button
	color = {True:'black', False:COLORS['light-gray']}[len(game.completed_groups) < 4]
	pg.draw.rect(surface, 'black', pg.Rect((170, 450), (70, 40)), 1, 20)
	draw_centered_text(surface, (205,470), 'Shuffle', small_font)
	screen.buttons.append(Button('shuffle', ((170, 450), (70, 40))))

	# deselect button
	color = {True:'black', False:COLORS['light-gray']}[game.num_selected() > 0]
	pg.draw.rect(surface, color, pg.Rect((250, 450), (100, 40)), 1, 20)
	draw_centered_text(surface, (300,470), 'Deselect all', small_font, color)
	screen.buttons.append(Button('deselect all', ((250, 450), (100, 40))))

	# submit button
	color = {True:'black', False:COLORS['light-gray']}[game.num_selected() == 4]
	pg.draw.rect(surface, color, pg.Rect((360, 450), (70, 40)), 1, 20)
	draw_centered_text(surface, (395,470), 'Submit', small_font, color)
	screen.buttons.append(Button('submit', ((360, 450), (70, 40))))

def draw_win_screen(surface, game, screen):
	return None

###Loop

pg.init()
surface = pg.display.set_mode((600, 600))
clock = pg.time.Clock()
screen = Screenspace((600, 600))
game = Game(test_set)

current_screen = 'start'
# can be 'start', 'play', 'win', or 'loss'

events = []
while all(event.type != pg.QUIT for event in events):
	events = pg.event.get()
	click = screen.detect_clicked_button(events)

	if current_screen == 'start':
		if click == 'play':
			current_screen = 'play'
		else:
			draw_start_screen(surface, screen)

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

		if game.guesses == 0:
			current_screen = 'loss'

		draw_game_screen(surface, game, screen)

	pg.display.flip()
	clock.tick(60)

pg.quit()
