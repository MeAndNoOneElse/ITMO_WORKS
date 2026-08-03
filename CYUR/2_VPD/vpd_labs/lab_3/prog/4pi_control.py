from ev3dev2.motor import LargeMotor, OUTPUT_A, SpeedPercent
import time
motor = LargeMotor(OUTPUT_A)
motor.position = 0
target = 90
kp = 0.01
ki = 0.01
dt = 0.05
integral = 0
file = open("../data/pi_small.txt", "w")
start = time.time()
try:
    while True:
        current = motor.position
        error = target - current
        integral += error * dt
        integral = max(min(integral, 1000), -1000)
        U = kp * error + ki * integral
        U = max(min(U, 100), -100)
        motor.on(SpeedPercent(U))
        t = time.time() - start
        file.write("{}, {}, {}\n".format(t, current, U))
        file.flush()
        if t > 5:
            break
finally:
    motor.off()
    file.close()