import sys
import ev3dev.ev3 as ev3
from time import sleep
import threading
import listener

receiver = listener.receiver()
listening = True
m1 = ev3.LargeMotor('outB')
m2 = ev3.LargeMotor('outC')

while listening:
	reply = receiver.communicate("", 5, True)
    reply_split = reply.split()

	if (reply_split[0] == 'm'):
        receiver.communicate('Handshake completed', 0.2, False)

		#motor functions begin
		m1.run_forever(speed_sp=200)
		m2.run_forever(speed_sp=200)

		receiver.communicate('Process finished', 0.2, False)

	elif (reply_split[0] == 'md'):
		#robot turns x degrees
		receiver.communicate('Handshake completed', 0.2, False)
        angle = reply_split[1]

		m1.run_to_rel_pos(position_sp = int(angle), speed_sp = 100, stop_action='brake')
		m2.run_to_rel_pos(position_sp = int(angle), speed_sp = 100, stop_action = 'brake')
		m1.wait_while('running')
		m2.wait_while('running')

		receiver.communicate('Process finished', 0.2, False)

	elif reply_split[0] == 'st'):
		receiver.communicate('Handshake completed', 0.2, False)

		print(message + ' STOP')
		#motor functions stop
		m1.stop(stop_action = 'brake')
		m2.stop(stop_action = 'brake')
		print('STOPPED')

		receiver.communicate('Process finished', 0.2, False)

	elif (reply_split[0] == 't'):
		#robot turns x degrees
		receiver.communicate('Handshake completed', 0.2, False)
        angle = reply_split[1]

		if (abs(int(angle)) >= 1):
			m1.run_to_rel_pos(position_sp = int(angle), speed_sp = 100, stop_action='brake')
			m2.run_to_rel_pos(position_sp = (int(angle)*-1), speed_sp = 100, stop_action = 'brake')
			m1.wait_while('running')
			m2.wait_while('running')
			sleep(0.3)
		m1.run_forever(speed_sp=200)
		m2.run_forever(speed_sp=200)

		receiver.communicate('Process finished', 0.2, False)

	elif (reply_split[0] == 'rt'):
		receiver.communicate('Handshake completed', 0.2, False)
        angle = reply_split[1]

		if (abs(int(angle)) >= 1):
			m1.run_to_rel_pos(position_sp=int(angle), speed_sp=100, stop_action='brake')
			m2.run_to_rel_pos(position_sp=(int(angle) * -1), speed_sp=100, stop_action='brake')
			m1.wait_while('running')
			m2.wait_while('running')
			sleep(0.5)

		receiver.communicate('Process finished', 0.2, False)

	elif (reply_split[0] == 'q'):
        receiver.communicate('Goodbye, connection terminated', 0.2, False)
		print ('terminated connection')
		listening = False