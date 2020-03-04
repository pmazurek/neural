import pickle
import arcade

from physics_2d import *



SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500


class SimulationVisualisation(arcade.Window):

    
    def __init__(self, width, height, title, simulation):
        super().__init__(width, height, title)

        self.simulation = simulation
        self.current_step = 0

    def setup(self):
        self.background = arcade.load_texture("tracks/1.png")

    def on_draw(self):
        arcade.start_render()
        try:
            step = self.simulation.states[self.current_step]
        except:
            step = self.simulation.states[-1]

        self.current_step +=1 
        arcade.draw_lrwh_rectangle_textured(
            0, 0,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            self.background
        )

        arcade.draw_rectangle_filled(
            step[0].x / self.simulation.plane.track_granularity_m,
            step[0].y / self.simulation.plane.track_granularity_m,
            10,
            10,
            arcade.color.ALIZARIN_CRIMSON
        )



def main():
    result_sim = pickle.load(open('result.sim', 'rb'))

    for step in result_sim.states:
        for an_object in step:
            print("object %s" % str(an_object))

    window = SimulationVisualisation(SCREEN_WIDTH, SCREEN_HEIGHT, "Sim", result_sim)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
