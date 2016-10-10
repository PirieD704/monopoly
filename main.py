from flask import Flask
from flaskext.mysql import MySQL
from random import randint


#create an instance of the mysql class
mysql = MySQL()
app = Flask(__name__)
#add to the app (Flask object) some config data for our connection
app.config['MYSQL_DATABASE_USER'] = 'x'
app.config['MYSQL_DATABASE_PASSWORD'] = 'x'
#The name of the database we want to connect to at the DB server
app.config['MYSQL_DATABASE_DB'] = 'monopoly'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
# user the mysql object's method "init_app" and pass it the flask object
mysql.init_app(app)
conn = mysql.connect()
#set up a cursor object, which is what the sql uses to connect and run queries
cursor = conn.cursor()

player1 = {
	'id': 1,
	'die_1': 0,
	'die_2': 0,
	'double_counter': 0,
	'jail_counter': False,
	'in_jail_counter': 0,
	'go_to_jail_counter': 0
}

player2 = {
	'id': 2,
	'die_1': 0,
	'die_2': 0,
	'double_counter': 0,
	'jail_counter': False,
	'in_jail_counter': 0,
	'go_to_jail_counter': 0
}

def dice_roll(player):
	double = False
	dice1 = randint(1,6)
	dice2 = randint(1,6)
	player['die_1'] = dice1
	player['die_2'] = dice2
	dice_total = dice1 + dice2
	if dice1 == dice2:
		double = True
		player['double_counter'] += 1
	return player, dice_total, double

# def starting_space_query(player):
# 	starting_space_query = "SELECT space FROM turns WHERE player = %s ORDER BY id DESC LIMIT 1" % player['id']
# 	cursor.execute(starting_space_query)
# 	starting_space = cursor.fetchone()

# def save_turn_query(player):
# 	save_turn_query = "INSERT INTO turns (player, die1, die2, roll_total, space, doubles) VALUES ('%s','%s','%s','%s','%s','%s')"
# 	cursor.execute(save_turn_query,(player['id'],player['die_1'],player['die_2'],roll[1],ending_space,roll[2]))
# 	conn.commit()

def turn(player):
	roll = dice_roll(player)
	if player['jail_counter']:
		if roll[2] or player['in_jail_counter'] == 2:
			player['jail_counter'] = False
			print "I got out of Jail!"
			player['in_jail_counter'] = 0
			starting_space_query = "SELECT space FROM turns WHERE player = %s ORDER BY id DESC LIMIT 1" % player['id']
			cursor.execute(starting_space_query)
			starting_space = cursor.fetchone()
			if starting_space == None:
				starting_space = 1
			else:
				starting_space = starting_space[0]

			ending_space = roll[1] + starting_space
			if ending_space >= 40:
				ending_space = ending_space - 40

			save_turn_query = "INSERT INTO turns (player, die1, die2, roll_total, space, doubles) VALUES ('%s','%s','%s','%s','%s','%s')"
			cursor.execute(save_turn_query,(player['id'],player['die_1'],player['die_2'],roll[1],ending_space,roll[2]))
			conn.commit()

			if roll[2]:
					turn(player)
			else:
				player['double_counter'] = 0
		else:
			print "still in jail :("
			player['in_jail_counter'] += 1
			starting_space_query = "SELECT space FROM turns WHERE player = %s ORDER BY id DESC LIMIT 1" % player['id']
			cursor.execute(starting_space_query)
			starting_space = cursor.fetchone()
			if starting_space == None:
				starting_space = 1
			else:
				starting_space = starting_space[0]

			ending_space = starting_space

			save_turn_query = "INSERT INTO turns (player, die1, die2, roll_total, space, doubles) VALUES ('%s','%s','%s','%s','%s','%s')"
			cursor.execute(save_turn_query,(player['id'],player['die_1'],player['die_2'],roll[1],ending_space,roll[2]))
			conn.commit()
	else:
		starting_space_query = "SELECT space FROM turns WHERE player = %s ORDER BY id DESC LIMIT 1" % player['id']
		cursor.execute(starting_space_query)
		starting_space = cursor.fetchone()
		if starting_space == None:
			starting_space = 1
		else:
			starting_space = starting_space[0]

		ending_space = roll[1] + starting_space

		if ending_space == 31:
			print "you landed on go to jail!"
			player['go_to_jail_counter'] += 1

		if player['double_counter'] == 3 or ending_space == 31:
			ending_space = 11
			player['jail_counter'] = True
		elif ending_space >= 40:
			ending_space = ending_space - 40

		save_turn_query = "INSERT INTO turns (player, die1, die2, roll_total, space, doubles) VALUES ('%s','%s','%s','%s','%s','%s')"
		cursor.execute(save_turn_query,(player['id'],player['die_1'],player['die_2'],roll[1],ending_space,roll[2]))
		conn.commit()

		if roll[2]:
			print "double rolled"
			if player['double_counter'] < 3:
				turn(player)
		else:
			player['double_counter'] = 0


for i in range(1,100):
	turn(player1)
	turn(player2)	

print "#########################################"
print "Queries for the finish"
print "#########################################"

most_common_roll_ply1_query = "SELECT player, roll_total, COUNT(roll_total) as count FROM turns WHERE player = 1 GROUP BY roll_total ORDER BY count DESC LIMIT 1"
cursor.execute(most_common_roll_ply1_query)
most_common_roll_ply1 = cursor.fetchone()
print "most common roll by player 1:"
print "roll: "+str(most_common_roll_ply1[1])
print "# of times: "+ str(most_common_roll_ply1[2])

most_common_roll_ply2_query = "SELECT player, roll_total, COUNT(roll_total) as count FROM turns WHERE player = 2 GROUP BY roll_total ORDER BY count DESC LIMIT 1"
cursor.execute(most_common_roll_ply2_query)
most_common_roll_ply2 = cursor.fetchone()
print "most common roll by player 2:"
print "roll: "+ str(most_common_roll_ply2[1])
print "# of times: "+ str(most_common_roll_ply2[2])

print "%%%%%%%%%%%%%%%%%%%%%%"
most_common_landed_on_ply1_query = "SELECT player, space, COUNT(space) as count, square, board_id FROM turns LEFT JOIN the_board ON turns.space = the_board.board_id WHERE player = 1 GROUP BY space ORDER BY count DESC LIMIT 1 "
cursor.execute(most_common_landed_on_ply1_query)
most_common_landed_on_ply1= cursor.fetchone()
print "most common space landed on by player 1:"
print "space: "+ str(most_common_landed_on_ply1[3])
print "# of times: "+ str(most_common_landed_on_ply1[2])

most_common_landed_on_ply2_query = "SELECT player, space, COUNT(space) as count, square, board_id FROM turns LEFT JOIN the_board ON turns.space = the_board.board_id WHERE player = 2 GROUP BY space ORDER BY count DESC LIMIT 1 "
cursor.execute(most_common_landed_on_ply2_query)
most_common_landed_on_ply2 = cursor.fetchone()
print "most common space landed on by player 2:"
print "space: "+ str(most_common_landed_on_ply2[3])
print "# of times: "+ str(most_common_landed_on_ply2[2])

print "%%%%%%%%%%%%%%%%%%%%%%"
print "# of times player 1 landed on go to jail:"
print str(player1['go_to_jail_counter'])
print "# of times player 2 landed on go to jail:"
print str(player2['go_to_jail_counter'])








