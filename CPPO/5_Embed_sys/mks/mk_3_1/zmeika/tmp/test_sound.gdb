set pagination off
set confirm off
target remote localhost:3333
monitor reset halt
break app_game.c:51
continue
delete breakpoints
set variable game.status = GAME_RUNNING
set variable game.food.x = game.body[0].x + 1
set variable game.food.y = game.body[0].y
break Board_SoundPlay
continue
printf "APPLE EVENT: "
p sound
finish
printf "PWM APPLE ARR/CCR: "
x/wd 0x4001002c
x/wd 0x40010034
disable breakpoints
monitor resume
monitor sleep 150
monitor halt
printf "PWM AFTER APPLE: "
x/wd 0x40010034
set variable game.body[0].x = 29
set variable game.direction = DIR_RIGHT
set variable game.pending = DIR_RIGHT
enable breakpoints
continue
printf "GAME OVER EVENT: "
p sound
finish
printf "PWM GAME OVER ARR/CCR: "
x/wd 0x4001002c
x/wd 0x40010034
disable breakpoints
monitor resume
monitor sleep 850
monitor halt
printf "PWM AFTER GAME OVER: "
x/wd 0x40010034
p game.status
p board_i2c_errors
p uxCurrentNumberOfTasks
monitor reset run
monitor shutdown
