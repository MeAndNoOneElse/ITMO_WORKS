from ev3dev2.motor import LargeMotor, OUTPUT_A, SpeedPercent
import time

motor = LargeMotor(OUTPUT_A)

motor.position = 0
target = 90
kp = 10.0
dt = 0.05

file = open("../data/p_rel.txt", "w")
start = time.time()

try:
    while True:
        current = motor.position
        error = target - current

        U = kp * error
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

