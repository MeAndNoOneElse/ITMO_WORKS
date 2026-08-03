from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B  # pyright: ignore[reportMissingImports]
from math import pi, cos, sin, radians, atan2, copysign
from time import time
MAX_SPEED = 50.0
class Motor:
    def __init__(self, motor):
        self._motor = motor
    def set_power(self, power):
        self._motor.run_direct(duty_cycle_sp=min(MAX_SPEED, max(-MAX_SPEED, power)))
    def get_degree(self):
        return self._motor.position
class Robot:
    def __init__(self, left_motor, right_motor):
        self._left_motor = Motor(left_motor)
        self._right_motor = Motor(right_motor)
        self._prev_left_degree = self._left_motor.get_degree()
        self._prev_right_degree = self._right_motor.get_degree()
    def set_powers(self, left_power, right_power):
        # print("power", left_power, right_power)
        self._left_motor.set_power(left_power)
        self._right_motor.set_power(right_power)
    def get_delta_degrees(self):
        left_degree = self._left_motor.get_degree()
        right_degree = self._right_motor.get_degree()
        delta_left_degree = left_degree - self._prev_left_degree
        delta_right_degree = right_degree - self._prev_right_degree
        self._prev_left_degree = left_degree
        self._prev_right_degree = right_degree
        return delta_left_degree, delta_right_degree
class Odom:
    def __init__(self, robot, wheel_radius, base_length):
        self._robot = robot
        self._wheel_radius = wheel_radius
        self._base_length = base_length
        self._x = 0
        self._y = 0
        self._theta = 0
    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y
    @property
    def theta(self):
        return self._theta
    def update(self):
        delta_left_degree, delta_right_degree = self._robot.get_delta_degrees()
        delta_left_radians = radians(delta_left_degree)
        delta_right_radians = radians(delta_right_degree)
        delta_length = (
            (delta_left_radians + delta_right_radians) * self._wheel_radius * 0.5)
        delta_theta = (
            (delta_right_radians - delta_left_radians)
            * self._wheel_radius
            / self._base_length)
        theta = self._theta + delta_theta * 0.5
        self._x += delta_length * cos(theta)
        self._y += delta_length * sin(theta)
        self._theta += delta_theta
class P:
    def __init__(self, linear_speed_coef, angle_speed_coef):
        self._linear_speed_coef = linear_speed_coef
        self._angle_speed_coef = angle_speed_coef
    def calc_powers(self, length_error, theta_error):
        linear_speed = self._linear_speed_coef * length_error
        angle_speed = self._angle_speed_coef * theta_error
        angle_speed = min(MAX_SPEED, max(-MAX_SPEED, angle_speed))
        if abs(linear_speed) + abs(angle_speed) > MAX_SPEED:
            linear_speed = copysign(MAX_SPEED - abs(angle_speed), linear_speed)
        return linear_speed - angle_speed, linear_speed + angle_speed
class Tangential:
    def __init__(self, linear_speed_coef, angle_speed_coef):
        self._linear_speed_coef = linear_speed_coef
        self._angle_speed_coef = angle_speed_coef
    def calc_powers(self, length_error, theta_error):
        linear_speed = self._linear_speed_coef * length_error * cos(theta_error)
        angle_speed = (
            self._linear_speed_coef * cos(theta_error) * sin(theta_error)
            + self._angle_speed_coef * theta_error)
        angle_speed = min(MAX_SPEED, max(-MAX_SPEED, angle_speed))
        if abs(linear_speed) + abs(angle_speed) > MAX_SPEED:
            linear_speed = copysign(MAX_SPEED - abs(angle_speed), linear_speed)
        return linear_speed - angle_speed, linear_speed + angle_speed
class Planner:
    def __init__(self, robot, odom):
        self._robot = robot
        self._odom = odom
    @staticmethod
    def _wrap_angle(angle):
        while angle > pi:
            angle -= 2.0 * pi
        while angle < -pi:
            angle += 2.0 * pi
        return angle
    def move_to_position(self, target, target_length_error, regulator, file):
        target_x, target_y = target
        length_error = float("inf")
        start_time = time()
        while length_error > target_length_error:
            t = time()
            self._odom.update()
            x_error = target_x - self._odom.x
            y_error = target_y - self._odom.y
            length_error = (x_error**2 + y_error**2) ** 0.5
            theta_error = self._wrap_angle(atan2(y_error, x_error) - self._odom.theta)
            powers = regulator.calc_powers(length_error, theta_error)
            print("odom", self._odom.x, self._odom.y, length_error, theta_error)
            self._robot.set_powers(*powers)
            file.write(
                str(t - start_time)
                + " "
                + str(self._odom.x)
                + " "
                + str(self._odom.y)
                + "\n"
            )
        self._robot.set_powers(0, 0)
    def move_to_positions(self, targets, target_length_error, regulator, file):
        for target in targets:
            self.move_to_position(target, target_length_error, regulator, file)
robot = Robot(LargeMotor(OUTPUT_A), LargeMotor(OUTPUT_B))
odom = Odom(robot, 29.0, 120.0)
planner = Planner(robot, odom)
p = P(0.5, 2)
tangential = Tangential(0.5, 1)
path = [
    (1000, 1000),
    (-1000, 1000),
    (-1000, -1000),
    (1000, -1000),
    (1000,1000)
]
# with open("p10.txt", "w") as file:
#     file.write("time x y" + "\n")
#     planner.move_to_position((1000, 0), 20.0, p, file)
#
# with open("p01.txt", "w") as file:
#     file.write("time x y" + "\n")
#     planner.move_to_position((0, 1000), 20.0, p, file)

# with open("p-10.txt", "w") as file:
#     file.write("time x y" + "\n")
#     planner.move_to_position((-1000, 0), 20.0, p, file)

# with open("p0-1.txt", "w") as file:
#     file.write("time x y" + "\n")
#     planner.move_to_position((0, -1000), 20.0, p, file)

# with open("tangential10.txt", "w") as file:
#     file.write("time x y" + "\n")
#     planner.move_to_position((1000, 0), 20.0, tangential, file)

# with open("tangential01.txt", "w") as file:
#     file.write("time x y" + "\n")
#     planner.move_to_position((0, 1000), 20.0, tangential, file)

# with open("tangential-10.txt", "w") as file:
#     file.write("time x y" + "\n")
#     planner.move_to_position((-1000, 0), 20.0, tangential, file)

# with open("tangential0-1.txt", "w") as file:
#     file.write("time x y" + "\n")
#     planner.move_to_position((0, -1000), 20.0, tangential, file)

# with open("p_path.txt", "w") as file:
#     file.write("time x y" + "\n")
#     planner.move_to_positions(path, 25.0, p, file)
with open("tangential_path.txt", "w") as file:
    file.write("time x y" + "\n")
    planner.move_to_positions(path, 25.0, tangential, file)
