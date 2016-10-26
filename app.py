##
# coding=UTF-8
# General modules.
from MySQLdb import *
import settings as config
import os, os.path
import logging
import sys
from threading import Timer
import string
import random
# Tornado modules.
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.auth
import tornado.options
import tornado.escape
from tornado import gen
import time
# Redis modules.
import brukva
# Import application modules.
from base import BaseHandler
#from login import LoginHandler
from login import LogoutHandler
#import settings as config
# Define port from command line parameter.
tornado.options.define("port", default=8888, help="run on the given port", type=int)
#ioloop.IOLoop.instance().start()
class ChatEdit(tornado.web.RequestHandler):
    def post(self):
        print "Bing,je sert a rien"
class UploadHandler(tornado.web.RequestHandler):#tornado.web.RequestHandler):
    def post(self):
        print "post!"
        file1 = self.request.files['file1'][0]
        original_fname = file1['filename']
        try: # TODO : Better use mime type!
            current_location2 = self.request.protocol + "://" + self.request.host + "/static/uploads/" + original_fname
            print "i'm trying fname_tuple"
            fname_tuple = original_fname.rsplit('.', 1)
            print type(fname_tuple)
            print fname_tuple
            if fname_tuple[1] == 'jpg':
                file_url2 = '<img src ="' + current_location2 + '" width="50%" height="50%"/>'
                message2 = {"body": file_url2,
                "_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),	"from": "Guest"}
            elif fname_tuple[1] == 'gif':
                print "It's a JIF!"
                file_url2 = '<img src ="' + current_location2 + '" >'
                message2 = {"body": file_url2,
                "_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),	"from": "Guest"}
            elif fname_tuple[1] == 'png':
                file_url2 = '<img src ="' + current_location2 + '" width="50%" height="50%"/>'
                message2 = {"body": file_url2,
                "_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),	"from": "Guest"}
            elif fname_tuple[1] == 'bmp':
                file_url2 = '<img src ="' + current_location2 + '" width="50%" height="50%"/>'
                message2 = {"body": file_url2,
                "_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),	"from": "Guest"}
            elif fname_tuple[1] == 'mp4':
                file_url2 = '<video width="320" height="240" controls="controls">' + '<source src="'+ current_location2 + '" type="video/mp4" />' + '</video>'
                message2 = {"body": file_url2,
                "_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),	"from": "Guest"}
            else:
                print "j'ai tout cassé"
                file_url2 = ''
                message2 = ''
            output_file = open("static/uploads/" + original_fname, 'wb')
            output_file.write(file1['body'])
            #output.file.close(file1)
            #redistogo_url = os.getenv('REDISTOGO_URL', None)
            print "i'm in redistogo"
            REDIS_HOST = 'localhost'
            REDIS_PORT = 6379
            REDIS_PWD = None
            REDIS_USER = None
            client = brukva.Client(host=REDIS_HOST, port=int(REDIS_PORT), password=REDIS_PWD)
            client.connect()
            client.listen(self)
            #current_location = "<a href=" + self.request.protocol + "://" + self.request.host + self.request.uri + "s/" + original_fname + "></a>"
            current_location = "<a href=" + self.request.protocol + "://" + self.request.host + "/static/uploads/" + original_fname + ">" + self.request.protocol + "://" + self.request.host + "/static/uploads/" + original_fname + "</a>"
            print current_location
            file_url = "file " + original_fname + " has been uploaded to " + current_location
            #file_url2 = '<img src ="' + current_location2 + '" width="50%" height="50%"/>'
            message = {"body": file_url,
            "_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),	"from": "Guest"}
            message_encoded = tornado.escape.json_encode(message)
            room = "1" #FIXME : message will land in room 1 for all upload in all rooms
            print "1"
            logging.info('New user for upload connected to chat room ' + room)
            client.rpush(room, message_encoded)
            #Publish message in Redis channel.
            client.publish(room, message_encoded)
            print message2
            if message2 is not '':
                print "je balance la sauce"
                message2 = {"body": file_url2,
                "_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),	"from": "Guest"}
                message_encoded = tornado.escape.json_encode(message2)
                client.rpush(room, message_encoded)
                #Publish message in Redis channel.
                client.publish(room, message_encoded)
            else:
                pass
            #time.sleep(1)
            # t = Timer(0.1, client.disconnect)
            # t.start()
            self.redirect('/')
        except:
            print 'Hey, something went wrong!', sys.exc_info()

class MainHandler(BaseHandler):
    """
    Main request handler for the root path and for chat rooms.
    """

    @tornado.web.asynchronous
    def get(self, room=None):
        print "repere 1"
        if not room:
            self.redirect("/room/1")
            return
        # Set chat room as instance var (should be validated).
        self.room = str(room)
        # Get the current user.
        self._get_current_user(callback=self.on_auth)


    def on_auth(self, user):
        print 'onauthapppy', user
        # print "je passe dans MainHandler au lieu de LoginHandler ??"
        #if not user:
            # Redirect to login if not authenticated.
            # self.redirect("/login")
            # return
        # Load 50 latest messages from this chat room.
        db = connect (host = config.SQLSERVER, user = config.SQLUSER, passwd = config.SQLPASS, db = config.SQLDB)
        cursor = db.cursor ()
        """
        Callback for third party authentication (last step).
        """
        if not user:
            print "user est tu la inside app?", user
            self.redirect("/login") # TODO: Make this hard coded value fecthable from db for flexible configuration
        else:
            #try:
            print "est ce que je passe par la? edition 2"
            # username = str(user["email"])
            # print username
            print user
            sql = ("SELECT UserID FROM Users_info WHERE UserName = '%s'") % user
            cursor.execute(sql)
            useridresult = cursor.fetchone()
            sql = "SELECT SessionID FROM Users WHERE UserID = %s", [useridresult]
            print sql
            cursor.execute(*sql)
            SQLSessionID = cursor.fetchone()
            BroswerSessionID = self.get_secure_cookie('SessionID')
            print SQLSessionID[0]
            print 'SQLSessionID is ' + str(SQLSessionID) + ' and BroswerSessionID is ' + BroswerSessionID
            if SQLSessionID[0] == BroswerSessionID:
                print "je check la session"
                #self.redirect("/room/1") # TODO: Make this hard coded value fecthable from db for flexible configuration
                self.application.client.lrange(self.room, -50, -1, self.on_conversation_found)
            else:
                self.redirect("/login") # TODO: Make this hard coded value fecthable from db for flexible configuration
            #except:
            # print 'a eu un schisme'
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # print(exc_type, fname, exc_tb.tb_lineno)
            # self.redirect("/login")
            #self.redirect("/login") # TODO: Make this hard coded value fecthable from db for flexible configuration
    def on_conversation_found(self, result):
        db = connect(host=config.SQLSERVER, user=config.SQLUSER, passwd=config.SQLPASS, db=config.SQLDB)
        cursor = db.cursor()
        AppID = '1'
        RoomNumber = '1'
        sql = "SELECT RoomID FROM abcd_un WHERE RoomNumber = %s AND AppID = %s", [RoomNumber, AppID]
        cursor.execute(*sql)
        RoomIDS = cursor.fetchall()
        if isinstance(result, Exception):
            raise tornado.web.HTTPError(500)
        # JSON-decode messages.
        messages = []
        for message in result:
            messages.append(tornado.escape.json_decode(message))
        # Render template and deliver website.
        content = self.render_string("messages.html", messages=messages)
        #print content
        self.render_default("index.html", content=content, chat=1)
        db.close()



class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    """
    Handler for dealing with websockets. It receives, stores and distributes new messages.

    TODO: Not proper authentication handling!
    """
    def fileinfo(self):
        logging.info("i'm in")
        message = 'File ' + original_fname + ' has been uploaded'
        message_encoded = tornado.escape.json_encode(message)
        self.write_message(message_encoded)
        # Persistently store message in Redis.
        self.application.client.rpush(self.room, message_encoded)
        # Publish message in Redis channel.
        self.application.client.publish(self.room, message_encoded)
        fileflag = ''
        logging.info("i'm out")
    @gen.engine
    def open(self, room='root'):
        """
        Called when socket is opened. It will subscribe for the given chat room based on Redis Pub/Sub.
        """
        # Check if room is set.
        if not room:
            self.write_message({'error': 1, 'textStatus': 'Error: No room specified'})
            self.close()
            return
        self.room = str(room)
        self.new_message_send = False
        # Create a Redis connection.
        self.client = redis_connect()
        # Subscribe to the given chat room.
        self.client.subscribe(self.room)
        self.subscribed = True
        self.client.listen(self.on_messages_published)
        logging.info('New user connected to chat room ' + room)


    def on_messages_published(self, message):
        """
        Callback for listening to subscribed chat room based on Redis Pub/Sub. When a new message is stored
        in the given Redis chanel this method will be called.
        """
        try:
            # Decode message
            m = tornado.escape.json_decode(message.body)
            # Send messages to other clients and finish connection.
            self.write_message(dict(messages=[m]))
            time.sleep(1)
            print "gone in on_messages_published"
            print message
            print m
        except :
            print 'Hey, something went wrong in section on_messages_published!', sys.exc_info()


    def on_message(self, data):
        # truc = user.get("email")
        # machin = user.get("name")
        # chouette = user.get(user["email"])
        # print "truc: " + truc + ", machin: " + machin + ", chouette: " + chouette
        """
        Callback when new message received vie the socket.
        """
        # print "var message is " + trouveunvrainomdevariable(fileflag)
        # if trouveunvrainomdevariable.fileflag == 'fileinfo':
            # self.fileinfo()
        #if UploadHandler.message == 'fileinfo':
            #self.fileinfo()
        logging.info('Received new message %r', data)
        try:
            # Parse input to message dict.
            print "Data is" + data
            datadecoded = tornado.escape.json_decode(data)
            what = str(datadecoded['user'])
            print "whaaaaaaat!" + what
            rightdatadecoded = what.split('"', 1)
            rightdatadecoded = str(rightdatadecoded[1]) # Workaround because #tornado.escape.json_decode(data) keeps an unwanted leading " : [W 160909 14:32:41 web:2659] #Invalid cookie signature '"ZXhhbHRpYQ==|1473424358|015bc4923b6db19a0a7c084cdc60b81952868c12'
            #                          ^There
            #coded(JSON) example message is : #{"body":"222","_xsrf":"b8f28cd1a8184afeb9296d48bb943d0a","user":"\"ZXhhbHRpYQ==|1473424358|015b#c4923b6db19a0a7c084cdc60b81952868c12"} wich seems right
            print rightdatadecoded
            message = {
                '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                #'from': self.get_secure_cookie('user', str(datadecoded['user'])), # datadecoding keeps a #unwanted quotation mark, bug report TODO
                'from': self.get_secure_cookie('user', rightdatadecoded),
                'body': tornado.escape.linkify(datadecoded["body"]),
            }
            if not message['from']:
                logging.warning("Error: Authentication missing")
                message['from'] = 'Guest'
        except Exception, err:
            # Send an error back to client.
            self.write_message({'error': 1, 'textStatus': 'Bad input data ... ' + str(err) + data})
            return

        # Save message and publish in Redis.
        try:
            # Convert to JSON-literal.
            message_encoded = tornado.escape.json_encode(message)
            self.write_message(message_encoded)
            # Persistently store message in Redis.
            self.application.client.rpush(self.room, message_encoded)
            # Publish message in Redis channel.
            self.application.client.publish(self.room, message_encoded)
            print message_encoded
        except Exception, err:
            e = str(sys.exc_info()[0])
            # Send an error back to client.
            self.write_message({'error': 1, 'textStatus': 'Error writing to database: ' + str(err)})
            return

        # Send message through the socket to indicate a successful operation.
        self.write_message(message)
        return


    def on_close(self):
        """
        Callback when the socket is closed. Frees up resource related to this socket.
        """
        logging.info("socket closed, cleaning up resources now")
        if hasattr(self, 'client'):
            # Unsubscribe if not done yet.
            if self.subscribed:
                self.client.unsubscribe(self.room)
                self.subscribed = False
            # Disconnect connection after delay due to this issue:
            # https://github.com/evilkost/brukva/issues/25
            t = Timer(0.1, self.client.disconnect)
            t.start()



class Application(tornado.web.Application):
    """
    Main Class for this application holding everything together.
    """
    def __init__(self):

        # Handlers defining the url routing.
        handlers = [
            (r"/", MainHandler),
            (r"/room/([a-zA-Z0-9]*)$", MainHandler),
            (r"/logout", LogoutHandler),
            (r"/socket", ChatSocketHandler),
            (r"/socket/([a-zA-Z0-9]*)$", ChatSocketHandler),
            (r"/upload", UploadHandler),
            (r"/uploads", MainHandler),
            (r"/save", ChatEdit),
        ]

        # Settings:
        settings = dict(
            cookie_secret = "43osdETzKXasdQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=", #BAAAD, according to some devs, this cookie secret is as important as a ssl private key, so must be put outside of code
            login_url = "/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies= True,
            autoescape="xhtml_escape",
            # Set this to your desired database name.
            db_name = 'chat',
            # apptitle used as page title in the template.
            apptitle = 'Chat example: Tornado, Redis, brukva, Websockets',
            autoreload=True,
            debug=True,
        )

        # Call super constructor.
        tornado.web.Application.__init__(self, handlers, **settings)

        # Stores user names.
        self.usernames = {}

        # Connect to Redis.
        self.client = redis_connect()


def redis_connect():
    """
    Established an asynchronous resi connection.
    """
    # Get Redis connection settings for Heroku with fallback to defaults.
    redistogo_url = os.getenv('REDISTOGO_URL', None)
    if redistogo_url == None:
        REDIS_HOST = 'localhost'
        REDIS_PORT = 6379
        REDIS_PWD = None
        REDIS_USER = None
    else:
        redis_url = redistogo_url
        redis_url = redis_url.split('redis://')[1]
        redis_url = redis_url.split('/')[0]
        REDIS_USER, redis_url = redis_url.split(':', 1)
        REDIS_PWD, redis_url = redis_url.split('@', 1)
        REDIS_HOST, REDIS_PORT = redis_url.split(':', 1)
    client = brukva.Client(host=REDIS_HOST, port=int(REDIS_PORT), password=REDIS_PWD)
    client.connect()
    return client



def main():
    """
    Main function to run the chat application.
    """
     # This line will setup default options.
    tornado.options.parse_command_line()
    # Create an instance of the main application.
    application = Application()
    # Start application by listening to desired port and starting IOLoop.
    application.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    # global fileflag
    # trouveunvrainomdevariable = UploadHandler
    main()