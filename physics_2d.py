import unittest
import math
import random

from collections import defaultdict


class Simulation:

    def __init__(self, plane):
        self.plane = plane
        self.states = []

    def simulate(self):
        is_collision = False
        steps = 0
        for step_number in range(0, 1000):
            self.plane.calculate_time_derivatives()
            self.plane.apply_object_actions()
            is_collision = self.plane.detect_collisions()

            if is_collision:
                break
            self.states.append(
                self.plane.dump_state()
            )
            steps += 1

        return (is_collision, steps)

class PhysicalPlane:
    def __init__(self):
        self.physical_objects = []
        self.time_delta_seconds = 0.01

    def add_physical_object(self, physical_object, position):
        self.physical_objects.append((physical_object, position))

    def calculate_time_derivatives(self):
        new_physical_objects = []

        for physical_object, position in self.physical_objects:
            physical_object.calculate_time_derivatives(self.time_delta_seconds)
            velocity = physical_object.get_velocity()
            new_position_x = position.x + (velocity.x * self.time_delta_seconds)
            new_position_y = position.y + (velocity.y * self.time_delta_seconds)
            new_physical_objects.append((physical_object, Vector2D(new_position_x, new_position_y)))

        self.physical_objects = new_physical_objects

    def apply_object_actions(self):
        for physical_object, _ in self.physical_objects:
            if hasattr(physical_object, 'apply_controls'):
                physical_object.apply_controls()

    def dump_state(self):
        objects = []
        for physical_object in self.physical_objects:
            objects.append(physical_object[1])

        return objects
    
    def detect_collisions(self):
        return False


class PhysicalPlaneWithTrack(PhysicalPlane):

    def __init__(self,  track_data):
        super().__init__()
        self.track_data = track_data
        self.track_granularity_m = 0.1

    def detect_collisions(self):
        for physical_object, position in self.physical_objects:
            track_position_x = math.floor(position.x / self.track_granularity_m)
            track_position_y = math.floor(position.y / self.track_granularity_m)
            try:
                is_collision = bool(self.track_data[track_position_x][track_position_y])
            except:
                is_collision = True
            return is_collision



class GeometricVector2D:

    def __init__(self, length, angle):
        self.length = float(length)
        self.angle = float(angle)

    @property
    def x(self):
        return math.sin(math.radians(self.angle)) * self.length

    @property
    def y(self):
        return math.cos(math.radians(self.angle)) * self.length

    def turn(self, degrees):
        self.angle += degrees

    def __repr__(self):
        return "(%s, %s)" % (self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def set_length(self, length):
        self.length = length

class Vector2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "(%s, %s)" % (self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class PhysicalObject:

    def __init__(self, mass):
        self.velocity = Vector2D(0, 0)
        self.mass = mass
        self.force = GeometricVector2D(0, 0)

    def apply_force(self, force):
        self.force = force

    def calculate_time_derivatives(self, time_delta_seconds):
        x_velocity = self.velocity.x
        y_velocity = self.velocity.y
        if self.force.x != 0:
            x_velocity += ((self.mass/self.force.x) * time_delta_seconds)
        if self.force.y != 0:
            y_velocity += ((self.mass/self.force.y) * time_delta_seconds)
        self.velocity = Vector2D(x_velocity, y_velocity)

    def get_velocity(self):
        return self.velocity

    def get_boundaries(self, *args, **kwargs):
        raise NotImplementedError()

    def __repr__(self):
        return str("V: %s, F: %s, m: %s" % (
            str(self.velocity),
            str(self.force),
            str(self.mass),
        ))


class PhysicalRect(PhysicalObject):

    def __init__(self, mass, x_length, y_length):
        super().__init__(mass)
        self.x_length = x_length
        self.y_length = y_length
    

    def get_boundaries(self, position):
        x1 = position.x - (self.x_length/2)
        x2 = position.x + (self.x_length/2)
        y1 = position.y - (self.y_length/2)
        y2 = position.y + (self.y_length/2)

        return (
            Vector2D(x1, y1),
            Vector2D(x2, y2),
        )
    

class Car(PhysicalRect):

    def __init__(self, mass, x_length, y_length, acceleration_force_max, agility_degrees_max):
        super().__init__(mass, x_length, y_length)
        self.acceleration_force_max = acceleration_force_max
        self.agility_degrees_max = agility_degrees_max

    def turn(self, value):
        assert value >= -1
        assert value <= 1
        self.force.turn(self.agility_degrees_max * value)

    def set_acceleration(self, value):
        assert value >= -1
        assert value <= 1
        self.force.set_length(self.acceleration_force_max * value)
    
    def apply_controls(self):
        angle, acceleration = self.control_manager.decide_actions(None) # TODO inputs
        self.set_acceleration(acceleration)
        self.turn(angle)

    def set_control_manager(self, control_manager):
        self.control_manager = control_manager

        
class TestPhysicalPlaneWithBasicObject(unittest.TestCase):

    def test_simple_derivatives_with_one_object(self):
        plane = PhysicalPlane()
        thing = PhysicalObject(10)
        thing.apply_force(Vector2D(1, 1))
        plane.add_physical_object(thing, Vector2D(0, 0))

        for x in range(0, 10):
            plane.calculate_time_derivatives()
        
        self.assertEqual(
                plane.physical_objects[0][0].velocity.x,
                0.9999999999999999
        )
        self.assertEqual(
                plane.physical_objects[0][0].velocity.y,
                0.9999999999999999
        )
        self.assertEqual(
                plane.physical_objects[0][1].x, #x position
                0.05499999999999999
        )
        self.assertEqual(
                plane.physical_objects[0][1].y, #y position
                0.05499999999999999
        )

    def test_boundaries_of_rect(self):
        thing = PhysicalRect(1, 10, 10)
        boundaries = thing.get_boundaries(Vector2D(0, 0))
        self.assertEqual(
            boundaries,
            (Vector2D(-5, -5), Vector2D(5, 5))
        )
        thing = PhysicalRect(1, 20, 10)
        boundaries = thing.get_boundaries(Vector2D(50, 50))
        self.assertEqual(
            boundaries,
            (Vector2D(40, 45), Vector2D(60, 55))
        )

    def test_geo_vector2d(self):
        vector = GeometricVector2D(10, 45)
        self.assertEqual(
            round(vector.x, 5),
            round(7.07107, 5)
        )
        self.assertEqual(
            round(vector.y, 5),
            round(7.07107, 5)
        )

        vector = GeometricVector2D(10, 0)
        vector.turn(45)
        self.assertEqual(
            round(vector.x, 5),
            round(7.07107, 5)
        )
        self.assertEqual(
            round(vector.y, 5),
            round(7.07107, 5)
        )



class CarRandomControlManager:

    def __init__(self):
        pass

    def decide_actions(self, inputs):
        # ignore inputs and return random decision
        turn = random.uniform(0, 1)
        acceleration = random.uniform(0, 1)
        return (turn, acceleration)


def load_track_data_from_image(image_path):
    from PIL import Image
    img = Image.open(image_path)
    track = img.load()

    track_data = []
    for x in range(0, img.size[0]):
        track_line = []
        for y in range(0, img.size[1]):
            if track[x,y] == (255, 255, 255, 255):
                track_line.append(0)
            else:
                track_line.append(1)

        track_data.append(track_line)
    return track_data


if __name__ == '__main__':
    track_data = load_track_data_from_image('track.png')
    plane = PhysicalPlaneWithTrack(track_data)
    sim = Simulation(plane)
    car = Car(10, 20, 20, 20, 20)
    random_control_manager = CarRandomControlManager()
    car.set_control_manager(random_control_manager)
    force = GeometricVector2D(1, 1)
    car.force = force
    plane.add_physical_object(car, Vector2D(2.4, 45.9))

    collision, last_step = sim.simulate()
    print(collision, last_step)

    import pickle
    pickle.dump(sim, open("result.sim", "wb"))

    unittest.main()


