import pickle
import arcade

from physics_2d import *

result_sim = pickle.load(open('result.sim', 'rb'))

for step in result_sim.states:
    for an_object in step:
        print("object %s" % str(an_object))


def on_draw(delta_time):
    arcade.start_render()
    step = on_draw.states[on_draw.current_step]
    on_draw.current_step +=1 

    arcade.draw_rectangle_filled(
        step[0].x,
        step[0].y,
        10,
        10,
        arcade.color.ALIZARIN_CRIMSON
    )


on_draw.current_step = 0 
on_draw.states = result_sim.states

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = ""

def main():
    arcade.open_window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.set_background_color(arcade.color.WHITE)
    arcade.schedule(on_draw, 1 / 100)
    arcade.run()


if __name__ == "__main__":
    main()
