#!/usr/bin/python3

import requests as rst
import time

UID = 704795484
# serv_addr = "http://3d8aa4a0.ngrok.io"
serv_addr = "http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com"

discovered = {}
gameOver = False
currentLevelOver = False
timeOut = False


def convertFormat(x, y):
	key = "{} {}".format(x, y)
	return key


def oppoDir(dir):
	if (dir == 'LEFT'):
		return 'RIGHT'
	if (dir == 'RIGHT'):
		return 'LEFT'
	if (dir == 'UP'):
		return 'DOWN'
	if (dir == 'DOWN'):
		return 'UP'

def createSession():

	r = rst.post('{}/session'.format(serv_addr), data = {'uid': UID}).json()
	TOKEN = r['token']

	return TOKEN


def solveMaze(dir, token, width, height):

	global currentLevelOver
	global gameOver
	global discovered
	global timeOut

	if currentLevelOver == True:
		return True
	
	r = rst.post('{}/game?token={}'.format(serv_addr, token), data = {'action': '{}'.format(dir)}).json()
	result = r['result']

	# print(result + " Coordinate {} {}".format(x, y))

	if result == "OUT_OF_BOUNDS":
		return False
	elif result == "WALL":
		# print("Coordinate Wall {} {}".format(x, y))
		return False
	elif result == "END":
		currentLevelOver = True
		return True
	
	game = rst.get('{}/game?token={}'.format(serv_addr, token)).json()
	status = game['status']

	if status == "NONE":
		timeOut = True
		return False

	x = game['current_location'][0]
	y = game['current_location'][1]

	# print(result + " Coordinate {} {}".format(x, y))
	
	key = convertFormat(x, y)
	discovered[key] = True

	ret1 = False
	ret2 = False
	ret3 = False
	ret4 = False

	key1 = convertFormat((x - 1), y)
	key2 = convertFormat((x + 1), y)
	key3 = convertFormat(x, (y - 1))
	key4 = convertFormat(x, (y + 1))

	if x > 0 and (not discovered.get(key1, False)):
		# print("Moving LEFT")
		ret1 = solveMaze("LEFT", token, width, height)
	if x < (width - 1) and (not discovered.get(key2, False)):
		# print("Moving RIGHT")
		ret2 = solveMaze("RIGHT", token, width, height)
	if y > 0 and (not discovered.get(key3, False)):
		# print("Moving UP")
		ret3 = solveMaze("UP", token, width, height)
	if y < (height - 1) and (not discovered.get(key4, False)):
		# print("Moving DOWN")
		ret4 = solveMaze("DOWN", token, width, height)

	# print("End reached for {} {}".format(x, y))

	if not (ret1 or ret2 or ret3 or ret4):
		newDir = oppoDir(dir)
		rst.post('{}/game?token={}'.format(serv_addr, token), data = {'action': '{}'.format(newDir)}).json()
		return False
	else:
		return True


def play(game, token):

	global discovered
	global currentLevelOver

	totalLevels = game['total_levels']

	noBreak = True

	for i in range(totalLevels):

		startTime = time.time()

		discovered = {}
		currentLevelOver = False

		r = rst.get('{}/game?token={}'.format(serv_addr, token)).json()

		if r['status'] == 'NONE':
			timeOut = True
			gameOver = False
			break

		width = r['maze_size'][0]
		height = r['maze_size'][1]

		x = r['current_location'][0]
		y = r['current_location'][1]

		status = r['status']

		if status == "NONE" or status == "GAME_OVER":
			gameOver = False
			noBreak = False
			break
		elif status == "FINISHED":
			gameOver = True
			noBreak = True
			print("Finished Game!")
			break

		key = convertFormat(x, y)
		discovered[key] = True

		# 目前假设

		print("Dimension: {}x{}".format(width, height))
		print("Current Location: ({},{})".format(x, y))

		if x > 0:
			dir = 'LEFT'
			# print(dir)
			result = solveMaze(dir, token, width, height)
			if result == True:
				endTime = time.time()
				runTime = endTime - startTime
				print("Finished Level {}\nTook {} seconds.".format((i + 1), runTime))
				continue

		if x < (width - 1):
			dir = 'RIGHT'
			# print(dir)
			result = solveMaze(dir, token, width, height)
			if result == True:
				endTime = time.time()
				runTime = endTime - startTime
				print("Finished Level {}\nTook {} seconds".format((i + 1), runTime))
				continue

		if y > 0:
			dir = 'UP'
			# print(dir)
			result = solveMaze(dir, token, width, height)
			if result == True:
				endTime = time.time()
				runTime = endTime - startTime
				print("Finished Level {}\nTook {} seconds".format((i + 1), runTime))
				continue

		if y < (height - 1):
			dir = 'DOWN'
			# print(dir)
			result = solveMaze(dir, token, width, height)
			if result == True:
				endTime = time.time()
				runTime = endTime - startTime
				print("Finished Level {}\nTook {} seconds".format((i + 1), runTime))
				continue

		print("None Applicable")
	
	if noBreak:
		gameOver = True
	else:
		gameOver = False
	

def main():

	counter = 0

	while gameOver == False:

		timeOut = False

		if (counter == 15):
			break

		counter = counter + 1

		print(counter)

		token = createSession()

		game = rst.get('{}/game?token={}'.format(serv_addr, token)).json()

		if game['status'] != "PLAYING":
			print("Right Here")
			continue

		play(game, token)

		if timeOut == True:
			print("Timeout")


	if not gameOver:
		print("Wrong\n")
		input("Press Anything to Exit")
	else:
		print("Game Finished\n")
		input("Press Anything to Exit")


if __name__ == '__main__':
	main()
