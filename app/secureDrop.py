import mysql.connector 
import getpass
from socket import *
import string 
import secrets 
import threading 
import re
import uuid
import time
from uuid import getnode as get_mac
import os
import sys
import multiprocessing

#*************************************************** THE REGISTRATION MODULE ********************************************************************
class Registration: # inherits the security class

	def insertDataBase(self, name, email, password):

		contactsTable = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(10)) # Generate a unique identifier Which will serve as the name of the Table of this contacts. 
		mycursor, cnx = Registration.connectToMySQL()

		# Generate a unique identifier which will server as the name of the MAC table. 
		macTable = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(10))
		try:
			mycursor.execute("INSERT INTO Users VALUES(%s, %s, %s, %s, %s)", (name, email, password, contactsTable, macTable))
			cnx.commit()
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_BAD_TABLE_ERROR:
				print("Creating table Users")
			else:
				raise

		#****** CREATE USER TABLE & MAC TABLE *****
		mycursor.execute("CREATE TABLE {} (fullName VARCHAR(255), email VARCHAR(255))".format(contactsTable))
		mycursor.execute("CREATE TABLE {} (email VARCHAR(255), IPaddress VARCHAR(255), MAC VARCHAR(255))".format(macTable))

	def checkPassword(self, password, re_pass, name, email):
		if password != re_pass:
			print("Passwords Didn't Match. \n\n Re-entere Credentials\n\n")
			self.userCredentials()
		self.insertDataBase(name, email, password)

	def userCredentials(self):
		fullName = input("\n\nEnter Full Name: ")
		email, password = Registration.userLogin()
		re_Pass = getpass.getpass("Re-enter Password: ")
		self.checkPassword(password, re_Pass, fullName, email )

	def welcomeMessage(self):
		print("\n\nNo Users are registered with this client. ")
		response = input("Do you want to register a new user (y/n)? ")
		if response == "y":
			self.userCredentials()
		# if no what do I do

	@staticmethod 
	def userLogin():
		email = input("Enter Email Address: ")
		password = getpass.getpass("Enter Password: ")
		return email, password

	@staticmethod
	def connectToMySQL():
		try:
			#cnx = mysql.connector.connect(user="centenumDB", password="hveqnrzuvr", host="centenum.csovrb8z7ap2.us-east-1.rds.amazonaws.com", port = 3306, database='secureDrop')
			cnx = mysql.connector.connect(user="root", password="", host="localhost", database='secureDrop')
			cursor = cnx.cursor(buffered=True)
			return cursor, cnx
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("There is a problem with your username and password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")

	@staticmethod
	def getUserTable(email):
		cursor, cnx = Registration.connectToMySQL()
		cursor.execute("SELECT contactsTable FROM Users WHERE email=%s", (email,)) # use password instead of email.
		retVal = cursor.fetchone()
		db = ""
		contactsTable = db.join(retVal)
		cursor.close() # close the connection 
		return contactsTable 

	@staticmethod
	def getMacTable(email):
		cursor, cnx = Registration.connectToMySQL()
		cursor.execute("SELECT macTable FROM Users WHERE email=%s", (email,))
		retVal = cursor.fetchone()
		db = ""
		macTable = db.join(retVal)
		cursor.close() # close the connections
		return macTable
#************************************************************ THE LOGIN MODULE *****************************************************************************
class Login: # inhertis the security class 

	def getCorrectPassword(self, cursor, email):
		cursor.execute("SELECT Password FROM Users WHERE email=%s", (email,))
		retVal = cursor.fetchone()

		querry = ""
		querry = querry.join(retVal)
		cursor.close()
		return querry

	def authenticateUser(self, password, querry):
		while password != querry:
			print("Email and Password Combination Invalid\n\n")
			email = input("Enter Email Address: ")
			password = getpass.getpass("Enter Password: ")

class udpThread(threading.Thread):
	def __init__(self, email):
		self.email = email
		threading.Thread.__init__(self)
		threading.Thread.daemon = True # run this in the back ground
	def run(self):
		print("starting the UDP SERVER for Broadcasting")
		# call the module that you want to run. 
		secureDrop.udpServer(self.email) # This should run forever.
		#secureDrop.tcpServer(self.email) # This should run forever
#************************************************************* THE SECUREDROP CLASS MODULE *********************************************************
class secureDrop(Login):

	email = True # class variable
	def ___init__(self):
		#self.email = email 
		print("This should do something")

	@staticmethod
	def getIP(address):
		address = str(address)
		address = address[:0] + address[2:]
		address = address[:9]
		return address # return the IP Address of the sender

	@staticmethod
	def getMAC():
		mac = "".join(re.findall('..', '%012x' % uuid.getnode()))
		mac = ':'.join(mac[i:i+2] for i in range(0,12,2))
		return mac
	@staticmethod
	def udpServer(mail): # I want this to run forever
		#mail, password = Registration.userLogin() FIND A DIFFERENT WAY TO GET THE EMAIL
		contactsTable = Registration.getUserTable(mail)
		macTable = Registration.getMacTable(mail)

		port = 50000
		server = socket(AF_INET, SOCK_DGRAM) # creatre a UDP socket
		server.setsockopt(SOL_SOCKET, SO_REUSEADDR, True) # allows for the port to be reusable.
		#server = socket(AF_INET, SOCK_STREAM) # TCP socket 
		server.bind(('', port)) # assigne a port to the the application 
-

		while True: 
			cursor, cnx = Registration.connectToMySQL()
			cursor2 = cursor
			#print("COMMUNICATION ATTEMPT 1\n")
			message, clientAddress = server.recvfrom(2024)
			#clientConnecton, clinetAddress = server.accept()
			message = message.decode()

			IPaddress = secureDrop.getIP(clientAddress) # this for testing purpose
			#print(f"This is the user IPaddress:{IPaddress}")

			# FOR RECIEVING ACTUAL DATA. if the inital messages is one, call a function that will recieve the actuall data and process it 
			#print(f"Clinet Message: {message}")
			message = message.split()
			email = message[0]
			#print(f"the email: {email}")
			mac = message[1]
			cursor.execute(f"SELECT EXISTS (SELECT fullName FROM  {contactsTable} WHERE email=%s)", (email,)) # select the name and email if it exists
			querry = cursor.fetchone()
			if querry is None:
				pass
				# check for MAC
				#print("Check point one")
			else:
				cursor.execute(f"SELECT EXISTS (SELECT * FROM {macTable} WHERE email=%s)", (email,))
				querry = cursor.fetchone()
				if querry is None:
					pass
					# INSERT email, IP and MAC
					#print("Check point two")
				else: 
					#print("Doing this")
					cursor.execute(f"INSERT INTO {macTable} VALUES(%s, %s, %s)", (email, IPaddress, mac))
					cnx.commit()
				#retVal = cursor.fetchone()
				#print("check point three")
				#db = ""
				#message = db.join(retVal)
				message = mail + " " + secureDrop.getMAC() # still need to pass the user email + the mac address
				server.sendto(message.encode(), clientAddress)
				#print("Check point FOUR")
				cursor.close() # close the connection
				cursor2.close()
			#print("COMMUNICATION ATTEMPT 2") 
	#@staticmethod
	def tcpServer(self, email):
		port = 50000
		server = socket(AF_INET, SOCK_STREAM)
		server.bind(('',port))
		server.listen(1)

		print("The TCP server is now listen in for connections")

		# open some path to a file to write data to 
		fp = open("inbox.txt", "w")
		while True:
			clientSocket, address = server.accept()
			print(f"This is Erastus computer IP: {address}")
			IPaddress = secureDrop.getIP(address)

			choice = secureDrop.sendAlert(IPaddress, email)
			#time.sleep(5)

			if choice == "y":
				data = clientSocket.recv(1024).decode()
				fp.write(data) # write to that file path that was opened!
				#*** SAVE THE FILE TO A LOCATION
				clientSocket.close() # close the connection

	def initMessage(self):
		print("Welcome to secureDrop \nType \"help\" For Commands.\n ")

	def welcomeMessage(self):
		command = input("secure_drop> ")
		#command = command.split() 
		if len(command) > 5:
			command = command.split() 
			_cmd = command[0]
			_contact = command[1]
			path = command[2]
			return _cmd, _contact, path
		else:
			return command, 9, 5

	def displayHelp(self):
		print("This is the help function ")
		print(" \"add\" -> Add a new contact ")
		print(" \"list\" -> List all online contact ")
		print(" \"send\" -> Transfer file to contact ")
		print(" \"exit\" -> Exit SecureDrop" )

	def addContacts(self, contactsTable):
		print("This is the add contacts function")
		fullName = input("Enter Full Name: ")
		email = input("Enter Email Address: ")
		self.email = email

		cursor, cnx = Registration.connectToMySQL()
		cursor.execute(f"INSERT INTO {contactsTable} VALUES(%s, %s)",(fullName, email)) #userTable is unique to one user
		cnx.commit()
		cursor.close() # close the connection 

		print("Contact Added")
	def threadUDPclient(slef, Socket, email, contactsTable):
		#print("*********** GOOOOOOOOOOOOO*******************")
		fp = open("contact.txt", "w")
		cursor, cnx = Registration.connectToMySQL()
		while True:
			response = Socket.recv(100000).decode()
			response = response.split()
			_email = response[0]
			if _email != email:
				#print(f"The server response: {response}")
				cursor.execute(f"SELECT fullName FROM {contactsTable} WHERE email=%s", (_email,))
				querry = cursor.fetchone()
				querry = "".join(querry)
				fp.write(_email)
				cursor.close()
				print(f"\t{querry} <{_email}>\n")


	def listContacts(self, email, contactsTable): # takes user email as argument
		cursor, cnx = Registration.connectToMySQL()
		port = 50000
		Socket = socket(AF_INET, SOCK_DGRAM) # Broad cast for UDP
		Socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		Socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		mac = self.getMAC()

		message = email + " " + mac
		#('<broadcast>', port)
		Socket.sendto(message.encode(), ('<broadcast>', port)) # broad cast the message over the network

		print("\tThe followin contacts are on online: \n")
		#self.threadUDPclient(Socket, email, contactsTable) # call the thread to process in coming messages

		thread = threading.Thread(target=self.threadUDPclient, args=(Socket, email, contactsTable,))
		thread.start()

	def sendFile(self, email, _contact, path):

		#querry Mac Address.
		mac = self.querryMAC(email, _contact)

		#cursor, cnx = Registration.connectToMySQL()
		port = 50000
		Socket = socket(AF_INET, SOCK_STREAM)
		Socket.connect((mac,port)) # connect to some uers IP and THE Custom port

		#open the file 
		with open(path, "r") as fp:
			data = fp.read()
			Socket.sendall(data.encode()) # send the client file
		Socket.close()

	@staticmethod
	def sendAlert(IPaddress, email):
		#print(f"Ipaddress: {IPaddress}")
		cursor, cnx = Registration.connectToMySQL()
		macTable = Registration.getMacTable(email)
		#print(f"this the the macTable you want: {macTable}")
		contactsTable = Registration.getUserTable(email)
		#print(f"This is the contactsTable you want: {contactsTable}")
		cursor.execute(f"SELECT email FROM {macTable} WHERE IPaddress=%s", (IPaddress,))
		# use the email to get the name from the user table
		_email = cursor.fetchone()
		_email = "".join(_email)
		#print(f"This is the email you wante: {_email}")

		cursor.execute(f"SELECT fullName FROM {contactsTable} WHERE email=%s", (_email,))
		fullName = cursor.fetchone()
		fullName = "".join(fullName)
		contact = fullName + " " + "<" + email + ">"
		choice = input(f"Contact {contact} is sending a file. Accept (y/n)?")
		print("Done sending Alert")
		return choice
		# Do something while the answer is Y or N
	def querryMAC(self, email, _contact):
		#print(f"This is the receiver email: {_contact}")
		cursor, cnx = Registration.connectToMySQL()
		macTable = Registration.getMacTable(email)
		#print(f"this is the mac talbe: {macTable}")
		cursor.execute(f"SELECT IPaddress FROM {macTable} WHERE email=%s", (_contact,))
		mac = cursor.fetchone()
		mac = "".join(mac)
		print(f"This is the mac you wanted: {mac}")
		return mac
#**************************************************************************** THE MAIN MODULE ***********************************************************
def main(): # Main method of the Login in module 

	Reg = Registration()
	Reg.welcomeMessage()

	email, password = Registration.userLogin() # get the email and password the user entered

	thread = udpThread(email)
	thread.start()

	contactsTable = Registration.getUserTable(email)

	user = secureDrop() # create an instace of the Login in clas
	# Create thread for TCP connection
	tcpS = threading.Thread(target=user.tcpServer, args=(email,), daemon=True)
	tcpS.start()

	cursor, cnx = Registration.connectToMySQL() # connect to the database and get the cursor
 
	querry = user.getCorrectPassword(cursor, email) # get the correct password for the user
	user.authenticateUser(password, querry) # authenticate the user 
	user.initMessage()

	while True:
		cmd, _contact, path = user.welcomeMessage()
		if cmd == "help":
			user.displayHelp()
		if cmd == "add":
			user.addContacts(contactsTable)
		if cmd == "list":
			user.listContacts(email, contactsTable)
			#time.sleep(1)
		if cmd == "send":
			user.sendFile(email, _contact, path)

if __name__ == '__main__':
	main()
