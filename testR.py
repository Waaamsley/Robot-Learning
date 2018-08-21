import sys
import ev3dev.ev3 as ev3
from time import sleep
import threading
import listener

receiver = listener.receiver()
listening = True
m1 = ev3.LargeMotor('outB')
m2 = ev3.LargeMotor('outC')


t1 = threading.Thread(target = receiver.receive, args = [])
t1.start()

def angle_check(index):
	try:
		int(receiver.messages[index])
		return True
	except ValueError:
		return False


while listening:
	count = 0
	while(receiver.received is False):
		sleep(0.05)
	text = receiver.messages[-1]
	receiver.received = False

	if (text is not None and text == 's'):
		mySocket.sendto(str.encode('Handshake completed'), address)
		(data, address) = mySocket.recvfrom(SIZE)

		speech = str(data)[2:-1]
		ev3.Sound.speak(speech)
		sleep(SPEAK + (len(speech) * 0.1))

		mySocket.sendto(str.encode('Process finished'), address)
	
	elif (text is not None and text == 'm'):
		receiver.send('Handshake completed')
		while (receiver.received is False):
			print('m loop')
			sleep(0.05)

		receiver.send('Received')
		message = receiver.messages[-1]
		receiver.received = False
		print (message)

		#motor functions begin
		m1.run_forever(speed_sp=200)
		m2.run_forever(speed_sp=200)

		receiver.send('Robot Moving')

	elif (text is not None and text == 'md'):
		#robot turns x degrees
		receiver.send('Handshake completed')
		while (receiver.received is False):
			print('md loop')
			sleep(0.05)

		receiver.send('Received')
		angle = receiver.messages[-1]
		receiver.received = False

		m1.run_to_rel_pos(position_sp = int(angle), speed_sp = 100, stop_action='brake')
		m2.run_to_rel_pos(position_sp = int(angle), speed_sp = 100, stop_action = 'brake')
		m1.wait_while('running')
		m2.wait_while('running')

		receiver.send('Process finished')

	elif (text is not None and text == 'st'):
		receiver.send('Handshake completed')
		while (receiver.received is False):
			print('st loop')
			sleep(0.05)

		receiver.send('Received')
		message = receiver.messages[-1]
		receiver.received = False

		print(message + ' STOP')
		#motor functions stop
		m1.stop(stop_action = 'brake')
		m2.stop(stop_action = 'brake')
		print('STOPPED')

		receiver.send('Robot Stopped')

	elif (text is not None and text == 't'):
		#robot turns x degrees
		receiver.send('Handshake completed')
		while (receiver.received is False):
			print('t loop')
			sleep(0.05)

		receiver.send('Received')
		angle = receiver.messages[-1]
		receiver.received = False

		if (abs(int(angle)) >= 1):
			m1.run_to_rel_pos(position_sp = int(angle), speed_sp = 100, stop_action='brake')
			m2.run_to_rel_pos(position_sp = (int(angle)*-1), speed_sp = 100, stop_action = 'brake')
			m1.wait_while('running')
			m2.wait_while('running')
			sleep(0.3)
		m1.run_forever(speed_sp=200)
		m2.run_forever(speed_sp=200)

		receiver.send('Process finished')

	elif (text is not None and text == 'rt'):
		receiver.send('Handshake completed')
		while (receiver.received is False):
			print ('rt loop')
			sleep(0.05)

		receiver.send('Received')
		angle = receiver.messages[-1]
		receiver.received = False

		sleep(0.5)
		if (abs(int(angle)) >= 1):
			m1.run_to_rel_pos(position_sp=int(angle), speed_sp=100, stop_action='brake')
			m2.run_to_rel_pos(position_sp=(int(angle) * -1), speed_sp=100, stop_action='brake')
			m1.wait_while('running')
			m2.wait_while('running')
			sleep(0.5)

		receiver.send('Process finished')

	elif (text is not None and text == 'q'):
		receiver.send('Goodbye, connection terminated')
		print ('terminated connection')
		listening = False
		receiver.listen = False
