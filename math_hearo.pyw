import wx
import random
import winsound
from text_viewer import Viewer
from time import sleep

class FocusableLabel(wx.StaticText):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	def AcceptsFocusFromKeyboard(self):
		return True


class Panel(wx.Panel):
	def __init__(self, parent):
		super().__init__(parent)
		self.Parent.Sizer.Add(self)
		self.Parent.active = self








class Frame(wx.Frame): # main window
	def __init__(self):
		wx.Frame.__init__(self, parent=None, title="عبقري الرياضيات", size=(500, 500))
		self.Centre()
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(sizer)
		panel = Panel(self)
		self.active = panel
		self.panels = {0: panel}
		self.startGame = wx.Button(panel, -1, "ابدأ اللعب", pos=(270, 210), size=(100, 50))
		self.startGame.Bind(wx.EVT_BUTTON, self.onStart)
		self.Show()
	def onStart(self, event):
		winsound.PlaySound(".\\effects\\click.wav", winsound.SND_FILENAME|winsound.SND_ASYNC)
		gameSettings = GameSettings(self)
		gameSettings.ShowModal()


class GameSettings(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent=parent, title="خيارات اللعب")
		self.Centre()
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer1 = wx.BoxSizer(wx.HORIZONTAL)
		sizer2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer3 = wx.BoxSizer(wx.HORIZONTAL)
		lbl = wx.StaticText(panel, -1, "اختر لعبة: ")
		self.gameChoice = wx.Choice(panel, -1, choices=["لعبة الضرب", "لعبة القسمة", "لعبة الجمع", "لعبة الطرح", "اللعبة الشاملة"])
		self.gameChoice.SetSelection(0)
		startButton = wx.Button(panel, -1, "إبدأ اللعب")
		startButton.Bind(wx.EVT_BUTTON, self.onStartGame)
		startButton.SetDefault()
		sizer1.Add(self.gameChoice, 1, wx.ALL)
		sizer1.Add(lbl, 1, wx.ALL)
		sizer3.Add(startButton, 1, wx.ALL)
		sizer.Add(sizer1, 1)
		sizer.Add(sizer2, 1)
		sizer.Add(sizer3, 1)
		panel.SetSizer(sizer)
	def onStartGame(self, event):
		winsound.PlaySound(".\\effects\\click.wav", winsound.SND_FILENAME|winsound.SND_ASYNC)
		gameNum = self.gameChoice.Selection+1
		rounds = 10
		self.Destroy()
		self.Parent.panels[0].Hide()
		self.playPanel = PlayPanel(self.Parent)
		self.playPanel.playing = Game(gameNum, rounds, self.playPanel)
		self.Parent.panels[1] = self.playPanel
		self.playPanel.Layout()
		self.Parent.Sizer.Fit(self.playPanel)
		self.playPanel.SetFocus()


class PlayPanel(Panel):
	def __init__(self, parent):
		super().__init__(parent)
		self.window = parent
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.questionField = FocusableLabel(self, -1,  "", pos=(30, 10), size=(170, 100))
		self.box = wx.StaticBox(self, -1, "الخيارات: ")
		self.btn1 = wx.Button(self.box, -1, "", name="choice")
		self.btn2 = wx.Button(self.box, -1, "", name="choice")
		self.btn3 = wx.Button(self.box, -1, "", name="choice")
		groupingSizer = wx.BoxSizer(wx.VERTICAL)

		sizer.Add(self.questionField, 1, wx.EXPAND)
		for button in self.box.GetChildren():
			if button.Name == "choice":
				button.Bind(wx.EVT_BUTTON, self.onAnswer)
				groupingSizer.Add(button)
		self.box.SetSizer(groupingSizer)
		sizer.AddStretchSpacer()
		sizer.Add(self.box)
		sizer.AddStretchSpacer()
		self.pointsArea = wx.StaticText(self, -1, "0 نقاط")
		sizer.Add(self.pointsArea)
		self.Bind(wx.EVT_CHAR_HOOK, self.onCancel)
		#self.Bind(wx.EVT_CLOSE, lambda e: self.cancel())
		self.SetSizer(sizer)

	def cancel(self):
		message = wx.MessageBox("هل تريد التوقف عن اللعب؟", "مهلًا", style=wx.YES_NO, parent=self)
		if message == 2:
			self.Hide()
			del self.window.panels[1]
			self.window.panels[0].Show()
			self.window.panels[0].SetFocus()


	def onCancel(self, event):
		event.Skip()
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.cancel()

	def onAnswer(self, event):
		answer = int(event.GetEventObject().Label)
		self.playing.send_answer(answer)
		#self.questionField.SetFocus()
class Game:
	def __init__(self, game_number, turns, window):
		self.log = []
		self.game_number = game_number
		self.window = window
		self.operations = {
			1: "*",
			2:"/",
			3:"+",
			4:"-",
			5: " "}
		self.ranges = {
			"*": (1, 145),
			"/": (1, 13),
			"+":(1, 201),
			"-":(0, 100)}
		self.turns = turns
		self.operation = self.operations[self.game_number]
		self.choices = []
		self.correct = 0
		self.count = 0
		self.new_question()
		self.points = 0
	def level_message(self):
		percentage = int((self.points/self.turns)*100)
		if percentage == 100:

			sleep(1)
			winsound.PlaySound(".\\effects\\tada.wav", winsound.SND_FILENAME|winsound.SND_ASYNC)
			return "تهانينا, لقد نجحت في حل جميع الأسئلة بشكل صحيح. أنت عبقري حقًا."
		elif percentage >50 and percentage <100:
			return "جميل جدًا, لقد نجحت في حل معظم الأسئلة بشكل صحيح."
		elif percentage == 50:
			return "جيد, حاول بذل المزيد في المرات القادمة."
		else:
			return "للأسف, ستحتاج إلى الكثير من التركيز في المرات القادمة."

	def finish_game(self):
		report = f"""انتهت اللعبة. 
لقد تمكنت من جمع {self.points} من النقاط.
    ملخص الجولة:
{self.answers_report()}
{self.level_message()}"""
		Viewer(self.window.Parent, "الرياضيات للأطفال", report).ShowModal()
		self.window.Hide()
		del self.window.Parent.panels[1]
		self.window.Parent.panels[0].Show()
		self.window.Parent.panels[0].SetFocus()

	def set_choices(self):
		buttons = [i for i in self.window.box.GetChildren() if i.Name == "choice"]
		for i in zip(buttons, self.choices):
			i[0].SetLabel(str(i[1]))
	def new_question(self):
		if self.count == self.turns:
			self.finish_game()
			return
		if self.game_number == 5:
			index = random.randrange(1, 5)
			self.operation = self.operations[index]
		if self.operation in ("+", "-"):
			x = random.randrange(1, 101)
			y = random.randrange(1, 101)
		else:
			x =  random.randrange(1,13)
			y =  random.randrange(1,13)
		if self.operation == "/":
			while float(x/y)-int(x/y) != 0.0:
				x = random.randrange(1,13)
				y = random.randrange(1,13)
			if y > x:
				x, y = y, x
			self.correct = x/y
		elif self.operation == "*":
			self.correct = x*y
		elif self.operation == "+":
			self.correct = x+y
		else:
			if y > x:
				x, y = y, x
			self.correct = x-y
		self.correct = int(self.correct)
		r1 = random.randrange(*self.ranges[self.operation])
		r2 = random.randrange(*self.ranges[self.operation])
		while r1 == r2 or self.correct in (r1, r2):
			r1 = random.randrange(*self.ranges[self.operation])
			r2 = random.randrange(*self.ranges[self.operation])
		self.choices = [self.correct,r1,r2]
		random.shuffle(self.choices)
		self.window.questionField.SetLabel("{} {} {} = ?".format(x, self.operation, y))
		self.window.questionField.SetFocus()
		self.set_choices()
		self.count += 1
	def send_answer(self, answer):
		if answer == self.correct:
			winsound.PlaySound(".\\effects\\correct.wav", winsound.SND_FILENAME|winsound.SND_ASYNC)
			self.points += 1
		else:
			winsound.PlaySound(".\\effects\\error.wav", winsound.SND_FILENAME|winsound.SND_ASYNC)
		self.window.pointsArea.SetLabel(f"{self.points} نقطة")
		self.log.append((self.window.questionField.Label.replace(" = ?", ""), self.correct, answer, self.correct == answer))
		self.new_question()
	def answers_report(self):
		report = ""
		for count, element in enumerate(self.log, 1):
			question, correct, answer, state = element
			report += f"""السؤال رقم {count}:
{question}.
الإجابة الصحيحة هي: {correct}.
إجابتك على السؤال هي: {answer}.
حالة الإجابة: """
			strState = "صحيحة." if state else "خاطئة."
			report += strState+"\n\n"
		return report

app = wx.App()
Frame()
app.MainLoop()
