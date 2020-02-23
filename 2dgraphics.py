import unittest
import math

from collections import defaultdict

class PhysicalPlane:
    def __init__(self):
        self.physical_objects = []
        self.collision_layers = defaultdict(list)
        self.time_delta_seconds = 0.01

    def add_physical_object(self, physical_object, position, collision_layer=None):
        self.physical_objects.append((physical_object, position))
        self.collision_layers[collision_layer].append(physical_object)


    def calculate_time_derivatives(self):
        new_physical_objects = []

        for physical_object, position in self.physical_objects:
            physical_object.calculate_time_derivatives(self.time_delta_seconds)
            velocity = physical_object.get_velocity()
            new_position_x = position.x + (velocity.x * self.time_delta_seconds)
            new_position_y = position.y + (velocity.y * self.time_delta_seconds)
            new_physical_objects.append((physical_object, Vector2D(new_position_x, new_position_y)))

        self.physical_objects = new_physical_objects

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
        x_velocity = self.velocity.x + ((self.mass/self.force.x) * time_delta_seconds)
        y_velocity = self.velocity.y + ((self.mass/self.force.y) * time_delta_seconds)
        self.velocity = Vector2D(x_velocity, y_velocity)

    def get_velocity(self):
        return self.velocity

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
        self.force.turn(agility_degrees_max * value)

    def set_acceleration(self, value):
        assert value >= -1
        assert value <= 1
        self.force.set_length(acceleration_force_max * value)

        
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


if __name__ == '__main__':
    unittest.main()

