from ev3dev2.motor import LargeMotor, OUTPUT_A, SpeedPercent
import time

motor = LargeMotor(OUTPUT_A)

motor.position = 0
target = 90
dt = 0.02
start = time.time()

with open("../data/relay_100.txt", "w") as file:
    try:
        while True:
            current = motor.position
            error = target - current

            if error > 0:
                U = 50
            elif error < 0:
                U = -50
            else:
                U = 0

            motor.on(SpeedPercent(U))

            t = time.time() - start
            file.write("{}, {}, {}\n".format(t, current, U))
            file.flush()
            if t > 5:
                break

            time.sleep(dt)

    finally:
        motor.off()
