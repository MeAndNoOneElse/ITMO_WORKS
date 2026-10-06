from ev3dev2.motor import LargeMotor, OUTPUT_A, SpeedPercent
import time
motor = LargeMotor(OUTPUT_A)
motor.position = 0
target = 90
kp = 5.0
kd = 0.83
dt = 0.05
prev_error = 0
file = open("../data/pd_good.txt", "w")
start = time.time()
try:
    while True:
        current = motor.position
        error = target - current
        derivative = (error - prev_error) / dt
        U = kp * error + kd * derivative
        U = max(min(U, 100), -100)
        motor.on(SpeedPercent(U))
        t = time.time() - start
        file.write("{}, {}, {}\n".format(t, current, U))
        file.flush()
        prev_error = error
        if t > 5:
            break
finally:
    motor.off()
    file.close()