import app
import asyncio
import random

from app_components import YesNoDialog, clear_background
from events.input import Buttons, BUTTON_TYPES

class FlappyBirdApp(app.App):
    def __init__(self):
        # Need to call to access overlays
        super().__init__()
        self.button_states = Buttons(self)
        self.bird_y = 16
        self.bird_velocity = 0
        self.obstacles = []
        self.score = 0
        self.game = "READY"  # Initial state of the game is READY
        self.dialog = None
        self.gravity = 0.25
        self.flap_strength = -1
        self.step = 0
        self.next_obstacle_distance = random.randint(16, 32)  # Variable distance for the next obstacle

    def _reset(self):
        self.bird_y = 16
        self.bird_velocity = 0
        self.obstacles = []
        self.score = 0
        self.dialog = None
        self.game = "READY"  # Reset game state to READY
        self.next_obstacle_distance = random.randint(16, 32)  # Reset variable distance for the next obstacle

    def _exit(self):
        self._reset()
        self.button_states.clear()
        self.minimise()

    def update(self, delta):
        if self.game == "READY":
            if self.button_states.get(BUTTON_TYPES["RIGHT"]) or self.button_states.get(BUTTON_TYPES["UP"]):
                self.bird_velocity = self.flap_strength
                self.game = "ON"
        elif self.game == "ON":
            if self.button_states.get(BUTTON_TYPES["RIGHT"]) or self.button_states.get(BUTTON_TYPES["UP"]):
                self.bird_velocity = self.flap_strength

            self._move_bird(delta)
            self._move_obstacles(delta)
            self._check_collisions()
        elif self.game == "OVER":
            self.dialog = YesNoDialog(
                message="Game Over.\nPlay Again?",
                on_yes=self._reset,
                on_no=self._exit,
                app=self,
            )
            self.game = ""

        # Only move obstacles every half second
        self.step = self.step + delta
        if self.step > 500:
            self.step = 0
            if self.game == "ON":
                self._move_obstacles(delta)

    def _move_bird(self, delta):
        self.bird_velocity += self.gravity
        self.bird_y += self.bird_velocity

        if self.bird_y < 0 or self.bird_y > 31:
            self.game = "OVER"

    def _move_obstacles(self, delta):
        for obstacle in self.obstacles:
            obstacle["x"] -= 1
        if len(self.obstacles) == 0 or self.obstacles[-1]["x"] < 31 - self.next_obstacle_distance:
            self._generate_obstacle()
            self.next_obstacle_distance = random.randint(16, 32)

    def _generate_obstacle(self):
        gap_y = random.randint(5, 25)
        gap_size = 6
        self.obstacles.append({"x": 31, "gap_y": gap_y, "gap_size": gap_size})

    def _check_collisions(self):
        for obstacle in self.obstacles:
            if obstacle["x"] < 4 and obstacle["x"] > 0:
                if not (obstacle["gap_y"] < self.bird_y < obstacle["gap_y"] + obstacle["gap_size"]):
                    self.game = "OVER"
            if obstacle["x"] == 0:
                self.score += 1
        self.obstacles = [obs for obs in self.obstacles if obs["x"] > -1]

    async def background_task(self):
        while True:
            await asyncio.sleep(5)

    def draw(self, ctx):
        clear_background(ctx)
        ctx.save()

        # draw score
        ctx.font_size = 12
        width = ctx.text_width("Score: {}".format(self.score))
        ctx.rgb(1, 0, 0).move_to(0 - width / 2, 100).text("Score: {}".format(self.score))

        ctx.translate(-80, -80)
        # draw game board
        ctx.rgb(0, 0, 0).rectangle(0, 0, 160, 160).fill()

        # draw bird
        ctx.rgb(1, 1, 0).rectangle(4 * 5, self.bird_y * 5, 5, 5).fill()

        # draw obstacles
        for obstacle in self.obstacles:
            ctx.rgb(0, 1, 0).rectangle(obstacle["x"] * 5, 0, 5, obstacle["gap_y"] * 5).fill()
            ctx.rgb(0, 1, 0).rectangle(obstacle["x"] * 5, (obstacle["gap_y"] + obstacle["gap_size"]) * 5, 5, (32 - (obstacle["gap_y"] + obstacle["gap_size"])) * 5).fill()

        ctx.restore()

        if self.dialog:
            self.dialog.draw(ctx)

__app_export__ = FlappyBirdApp
