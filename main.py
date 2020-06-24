from kivy.uix.widget import Widget
from kivy.app import App
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
import shelve


class Player(Widget):
    velocity_X = NumericProperty(0)
    velocity_Y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_X, velocity_Y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def collision(self, bar):
        if self.collide_widget(bar):
            print("hit")


class Barrier(Widget):
    gap_width = NumericProperty(200)
    barrier_height = NumericProperty(50)
    barrier_Y = NumericProperty(0)
    gap_center = NumericProperty(0)
    center = [(Window.width / 4), (Window.width / 2), (Window.width * 3 / 4)]
    barrier_position = NumericProperty(0)
    left_barrier_position = NumericProperty(0)
    right_barrier_position = NumericProperty(0)
    left_barrier_size = NumericProperty(0)
    right_barrier_size = NumericProperty(0)
    barrier_Y_change = 0

    right_barrier_texture = ObjectProperty(None)
    left_barrier_texture = ObjectProperty(None)
    left_barrier_tex_coords = ListProperty((0, 0, 1, 0, 1, 1, 0, 1))
    right_barrier_tex_coords = ListProperty((0, 0, 1, 0, 1, 1, 0, 1))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.right_barrier_texture = Image(source="BarrierCloud.png").texture
        self.right_barrier_texture.wrap = "repeat"
        self.left_barrier_texture = Image(source="BarrierCloud.png").texture
        self.left_barrier_texture.wrap = "repeat"

    barrier_velocity_X = NumericProperty(0)
    barrier_velocity_Y = NumericProperty(0)
    velocity = ReferenceListProperty(barrier_velocity_X, barrier_velocity_Y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class SwiperGame(Widget):
    kite = ObjectProperty(Player)
    bar = ObjectProperty(Barrier)
    start = ObjectProperty(None)
    title = ObjectProperty(None)
    score = ObjectProperty(None)
    soundonbutton = ObjectProperty(None)
    soundoffbutton = ObjectProperty(None)
    highscore = ObjectProperty(None)
    music = "on"
    game_state = "ready"
    first_game = "yes"
    sound = SoundLoader.load("SwiperSoundtrackLoop.wav")
    pointsound = SoundLoader.load("PointSound.wav")
    crashsound = SoundLoader.load("CrashSound.wav")
    menunavsound = SoundLoader.load("MenuNavSound.wav")

    high_score_num = NumericProperty(0)
    score_num = NumericProperty(0)
    initial = NumericProperty(0)

    def on_touch_down(self, touch):
        self.initial = touch.x
        if ((Window.width / 2) - 50 < touch.x < (Window.width / 2) + 50) and (
                (Window.height / 2) - 30 < touch.y < (Window.height / 2) + 30) and self.game_state == "ready":
            self.game_state = "play"
            self.first_game = "no"
            self.score_num = 0
            SwiperApp.speed_up = 0
            SwiperApp.start_game(self)
            if self.music == "on":
                self.menunavsound.play()
        if ((Window.width / 10) - 22.5 < touch.x < (Window.width / 10) + 22.5) and (
                Window.height - 100) - 22.5 < touch.y < (
                Window.height - 100) + 22.5 and self.game_state == "ready" and self.music == "on":
            self.music = "off"
            self.menunavsound.play()
        elif ((Window.width / 10) - 22.5 < touch.x < (Window.width / 10) + 22.5) and (
                Window.height - 100) - 22.5 < touch.y < (
                Window.height - 100) + 22.5 and self.game_state == "ready" and self.music == "off":
            self.music = "on"
            if self.music == "on":
                self.menunavsound.play()

    def on_touch_up(self, touch):
        if touch.x - self.initial > 40 and self.kite.center_x < self.width * 3 / 4:
            self.kite.velocity_X += 10
        elif touch.x - self.initial < 40 and self.kite.center_x > self.width / 4:
            self.kite.velocity_X -= 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sound.loop = True
        self.sound.play()

    def barrier_collisions(self):
        for barrier in SwiperApp.barriers:
            if (barrier.barrier_Y < self.kite.y + 40 < barrier.barrier_Y + barrier.barrier_height and (
                    (barrier.gap_center + (barrier.gap_width / 2) < self.kite.center_x) or (
                    self.kite.center_x < barrier.gap_center - (barrier.gap_width / 2)))) or (
                    (barrier.barrier_Y <= self.kite.center_y <= barrier.barrier_Y + barrier.barrier_height) and (
                    (barrier.gap_center + (barrier.gap_width / 2) < self.kite.center_x) or (
                    self.kite.center_x < barrier.gap_center - (barrier.gap_width / 2)))):
                self.game_state = "ready"
                self.first_game = "no"
                self.start.center_y = Window.height / 2
                if self.music == "on":
                    self.crashsound.play()
                if self.score_num > self.high_score_num:
                    self.high_score_num = self.score_num
                print("hit")
            if barrier.barrier_Y + barrier.barrier_height - 1 <= self.kite.y + 40 <= barrier.barrier_Y + barrier.barrier_height + 1 and (
                    (barrier.gap_center + (barrier.gap_width / 2) > self.kite.center_x) or (
                    self.kite.center_x > barrier.gap_center - (barrier.gap_width / 2))):
                SwiperApp.speed_up += 0
                self.score_num += 1
                if self.music == "on":
                    self.pointsound.play()
                print(self.score_num)
                print(barrier.barrier_Y_change)
                print(barrier.barrier_Y + barrier.barrier_height - 1)
                print(barrier.barrier_Y + barrier.barrier_height + 1)
                print(self.kite.y + 40)

    def update(self, dt):
        self.kite.move()
        if self.kite.center_y >= 80:
            self.kite.velocity_Y = 0
        if self.first_game == "yes" and self.game_state == "ready":
            self.score.center_y += Window.height
            self.kite.velocity_Y = 0.5
            if self.kite.center_y >= 80:
                self.kite.velocity_Y = 0
        if self.first_game == "no" and self.game_state == "ready":
            self.highscore.center_y = Window.height - 100
            self.highscore.center_x = Window.width / 4 + 30
            for barrier in SwiperApp.barriers:
                barrier.barrier_Y += Window.height
                Barrier.barrier_Y_change = 0
        if self.game_state == "play":
            self.title.y = Window.height
            self.highscore.center_y += Window.height
            self.score.center_y = Window.height - 50
            SwiperApp.move_barriers(self.bar, dt, SwiperApp.speed_up)
            self.start.y = Window.height
            self.barrier_collisions()
            self.soundonbutton.center_x = Window.width - 1000
            self.soundoffbutton.center_x = Window.width - 1000
        if self.music == "on" and self.game_state == "ready":
            self.sound.volume = 0.6
            self.pointsound.volume = 0.4
            self.crashsound.volume = 0.4
            self.menunavsound.volume = 0.3
            self.soundonbutton.center_x = (Window.width / 10)
            self.soundoffbutton.center_x = (Window.width / 10) - 1000
        if self.music == "off" and self.game_state == "ready":
            self.sound.volume = 0
            self.soundonbutton.center_x = (Window.width / 10) - 1000
            self.soundoffbutton.center_x = (Window.width / 10)
        if self.kite.center_x > self.width * 3 / 4:
            self.kite.velocity_X = 0
            self.kite.center_X = self.width * 3 / 4
        if self.kite.center_x < self.width / 4:
            self.kite.velocity_X = 0
            self.kite.center_X = self.width / 4
        if self.kite.center_x == self.width / 2:
            self.kite.velocity_X = 0



class Start(Widget):
    pass


class Title(Widget):
    pass


class SoundOn(Widget):
    pass


class SoundOff(Widget):
    pass


class SwiperApp(App):
    barriers = []
    window_size = Window.width
    speed_up = 0

    def build(self):
        game = SwiperGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        if (game.game_state == "play"):
            self.start_game()
        return game

    def start_game(self):
        num_of_barriers = 4
        distance_between_barriers = Window.height / num_of_barriers
        for i in range(num_of_barriers):
            barrier = Barrier()
            r = list(range(5))
            barrier.size_hint = (None, None)
            barrier.barrier_Y = Window.height + (r[i] * distance_between_barriers) + distance_between_barriers
            barrier.left_barrier_size = (barrier.gap_center - (barrier.gap_width / 2), barrier.barrier_height)
            barrier.right_barrier_size = Window.width - barrier.gap_center - (
                    barrier.gap_width / 2), barrier.barrier_height
            barrier.gap_center = barrier.center[randint(0, 2)]
            barrier.id = "bar"
            if barrier.gap_center == barrier.center[0]:
                barrier.left_barrier_texture = Image(source="BarrierSmallCloud.png").texture
                print("small left")
            if barrier.gap_center == barrier.center[2]:
                barrier.right_barrier_texture = Image(source="BarrierSmallCloud.png").texture
                print("small right")

            SwiperApp.barriers.append(barrier)
            self.add_widget(barrier)

    def move_barriers(self, dt, speed_up):
        for barrier in SwiperApp.barriers:
            barrier.barrier_Y_change = 2 + SwiperApp.speed_up
            barrier.barrier_Y -= barrier.barrier_Y_change
            if barrier.barrier_Y + barrier.barrier_height < 0:
                barrier.barrier_Y = Window.height
                barrier.gap_center = barrier.center[randint(0, 2)]
                if barrier.gap_center == barrier.center[0]:
                    barrier.left_barrier_texture = Image(source="BarrierSmallCloud.png").texture
                else:
                    barrier.left_barrier_texture = Image(source="BarrierCloud.png").texture
                if barrier.gap_center == barrier.center[2]:
                    barrier.right_barrier_texture = Image(source="BarrierSmallCloud.png").texture
                else:
                    barrier.right_barrier_texture = Image(source="BarrierCloud.png").texture


SwiperApp().run()
