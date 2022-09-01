//The database isn't working
from datetime import datetime, timedelta
from pprint import pprint
import sqlite3

from os.path import exists
import os
import codecs
import pickle

#Class for the Database creation and manipulation
class DataBaseHandler:

    #Define where to store the data. If the database does not exist, it gets created and then a connection is made
    def __init__(self, database_path):
        #Where to store our data
        file = database_path + 'elder.db'

        #If the file does not exist, ...
        if(exists(file) != True):
            try:
                #...try creating it
                open(file, 'a').close()

                #Connect to the DB
                self.connection = sqlite3.connect(file)

                #Create a cursor
                self.cursor = self.connection.cursor()

                #Initialize the database by creating the tables
                self.DBHFirstInit()

            #if the creation process encounters a problem, print the following error
            except OSError:
                print('Failed creating the file')

        #If the file esists, just establish a connection with it
        else:
                #Connect to the DB
                self.connection = sqlite3.connect(file)

                #Create a cursor
                self.cursor = self.connection.cursor()


    #Definitions of the queries to create the tables of our database with their relations
    def DBHFirstInit(self):

        #Creation of the table Elders
        self.cursor.execute("""
                            CREATE TABLE Elders (
                                name TEXT NOT NULL,
                                surname TEXT NOT NULL,
                                picture_location TEXT NOT NULL,
                                weight BLOB,
                                training_variable INTEGER NOT NULL,
                                PRIMARY KEY (name, surname)
                            );
                            """)

        #Creation of the table Moods
        self.cursor.execute("""
                            CREATE TABLE Moods (
                                name NOT NULL,
                                surname NOT NULL,
                                acquisition_time TEXT NOT NULL,
                                mood TEXT NOT NULL,
                                angry REAL NOT NULL,
                                disgust REAL NOT NULL,
                                fear REAL NOT NULL,
                                happiness REAL NOT NULL,
                                sad REAL NOT NULL,
                                surprise REAL NOT NULL,
                                neutral REAL NOT NULL,
                                FOREIGN KEY(name) REFERENCES Elders(name),
                                FOREIGN KEY(surname) REFERENCES Elders(surname),
                                PRIMARY KEY(name, surname, acquisition_time)
                            );
                            """)

        #Committing the changes through the connection
        self.connection.commit()


    #Definition of the query to insert a new person in the Elder table
    def DBHElderlyCommit(self, name, surname, picture):
        dictionary = {}
        tags = ("rain", "art", "sky", "waterfall", "pets", "nature", "landscape", "forest", "beach", "flowers", "countryside")

        for tag in tags:
            dictionary[tag] = 1

        blob = self.DBHEncryptBlob(dictionary=dictionary)
        pprint(blob)
        #Query to the database
        self.cursor.execute("INSERT INTO Elders (name, surname, picture_location, weight, training_variable) VALUES (?, ?, ?, ?, 0)" , (name, surname, picture, blob))


        #Committing the change through the connection
        self.connection.commit()


    #Definition of the query to insert a new emotion detection
    def DBHDetectionCommit(self, name, surname, mood, angry, disgust, fear, happiness, sad, surprise, neutral, acquisitionTime=None):

        #Get the id relative to the person whose emotions must be inserted

        #In case if the acquisition time is not specified...
        if acquisitionTime is None:
            #... Take the actual time and format it
            acquisitionTime = datetime.now()
            acquisitionTime.strftime("%m-%d-%Y, 00:00:00")

        #Insert query
        self.cursor.execute("INSERT INTO Moods (name, surname, acquisition_time ,mood ,angry ,disgust ,fear ,happiness ,sad ,surprise,neutral) VALUES (?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, surname, acquisitionTime, mood, angry, disgust, fear, happiness, sad, surprise, neutral))
        input('???')
        #Committing the change through the connection
        self.connection.commit()
        input('???')

    #Definition of the query to fetch the progressive number relative to a person
    def DBHGetProgressiveID(self, name,surname):

        #Query
        self.cursor.execute("""
                            SELECT rowid FROM Elders
                            WHERE name = "{}" AND surname = "{}"
                        """.format(name.capitalize(), surname.capitalize()))

        #Returning the value of the id
        #The function fetchall returns a list of tuple, so [0][0] is necessary to access the first (unique, in this case) value
        return self.cursor.fetchone()


    #Definition of the query to fetch the picture location relative to a person
    def DBHGetPicture(self, name, surname):

        #Query
        self.cursor.execute("""
                            SELECT picture_location FROM Elders
                            WHERE name = "{}" AND surname = "{}"
                        """.format(name.capitalize(), surname.capitalize()))

        #Returning the location of the picture
        #The function fetchall returns a list of tuple, so [0][0] is necessary to access the first (unique, in this case) value
        return self.cursor.fetchall()[0][0]


    #Definition of the query to get the last emotions detection relative to a person
    def DBHGetLastAcquisition(self, name, surname):

        #The function simply calls a more general function
        return self.DBHGetLastNAcquisition(name, surname, 1)


    #Definition of the query to get the last N emotions detections relative to a person
    def DBHGetLastNAcquisition(self, name, surname, n):

        #Get the id relative to a person
        id = self.DBHGetProgressiveID(name, surname)

        #Query to fecth all the detections relative to a person
        self.cursor.execute(""" SELECT acquisition_time, mood, angry, disgust, fear, happiness, sad, surprise, neutral FROM Moods
                                WHERE elder == {}
                                ORDER BY acquisition_time DESC
                            """.format(id))

        #Returning only the last n acquisitions
        return self.cursor.fetchmany(size=n)


    #Definition of the query to get all the detections of the last N days
    def DBHGetLastNDaysAcquisitions(self, name, surname, n):

        #Get today's date

        time = datetime.today()

        #If n is not zero, subtract n days from "time"
        if n != 0:
            time = time - timedelta(days=n)

        #Format the time value
        date_time = time.strftime("%m-%d-%Y, 00:00:00")

        #Get the id of the person whose emotions data we want to fecth
        id = self.DBHGetProgressiveID(name, surname)

        #Query
        self.cursor.execute("""
                                SELECT acquisition_time, mood, angry, disgust, fear, happiness, sad, surprise, neutral FROM Moods
                                WHERE elder = {} AND acquisition_time >='{}'
                                ORDER BY acquisition_time ASC
        """.format(id, date_time))

        #Return all values as a list of tuples
        return self.cursor.fetchall()


    #Definition of the query to get all the daily emotion detections
    def DBHGetDailyAcquisitions(self, name, surname):

        #This function calls a more general function
        return self.DBHGetLastNDaysAcquisitions(name, surname, 0)


    #Definition of the query to update the picture location
    def DBHUpdatePicture(self, name, surname, picture):

        #Query
        self.cursor.execute("""
                                UPDATE Elders
                                SET picture_location = '{}'
                                WHERE name = '{}' AND surname = '{}'
                            """.format(picture, name.capitalize(), surname.capitalize()))


        #Committing the change through the connection
        self.connection.commit()


    #Definition of the query to check if a particular entry in the Elder table esists
    def DBHElderExists(self, name, surname):

        #Query
        self.cursor.execute("""
                                SELECT EXISTS(
                                    SELECT rowid, *
                                    FROM Elders
                                    WHERE name == (?) AND surname == (?)
                                )
                            """, (name.lower(), surname.lower()))

        #Returning the result of the query as a simple binary value
        return self.cursor.fetchone()


    #Returns the dictionary where the weights of preferences relative to a certain person are stored
    def DBHGetBlobAndVariable(self, name, surname):

        #Gets the the id relative to the person
        id = self.DBHGetProgressiveID(name, surname)
        name = name.lower()
        surname = surname.lower()
        #Query
        self.cursor.execute("""
                            SELECT *
                            FROM Elders
                            WHERE name = :name AND surname = :surname
                            """, {'name': name, 'surname': surname} )

        pprint(self.cursor.fetchall())

        #Decrypting the query result
        return self.DBHDecryptBlob(self.cursor.fetchone()), self.cursor.fetchone()[1]

    #Updates the dictionary where the weights of preferences relative to a certain person are stored
    def DBHUpdateBlobAndVariable(self, name, surname, df, variable):

        #Gets the the id relative to the person
        id = self.DBHGetProgressiveID(name, surname)

        #Encrypting the data we have to store
        pickled = self.DBHEncryptBlob(df)

        #Query
        self.cursor.execute("""
                            UPDATE Elder
                            SET weight = ? AND training_variable = ?
                            WHERE rowid == ?
                            """, (pickled, variable, id))

        #Committing the changes through the connection
        self.connection.commit()


    #Encrypts the Dictionary into a BLOB format
    def DBHEncryptBlob(self, dictionary):
        return codecs.encode(pickle.dumps(dictionary), "base64").decode()


    #Decrypt the BLOB into a Dictionary
    def DBHDecryptBlob(self, pickle):
        return pickle.loads(codecs.decode(pickle[0][1].encode(), "base64"))


    #Connection closing
    def DBHClose(self):

        #Close the connection
        self.connection.close()
