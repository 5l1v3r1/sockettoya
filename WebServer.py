##############################################################################
# Web Server App - takes a port number in the form of --port #               #
# The server forks multiple processes to handle requests from clients        #
# Child processes are waited for and zombies are cleaned up.                 #
#                                                                            # 
# App tested with Python 2.7.10 on Mac OS X                                  #
##############################################################################
import errno
import os
import signal
import socket
import argparse
import hashlib
import time
import json
import base64

REQUEST_QUEUE_SIZE = 1024  # how many threads are listening on port
canclose = True            # flag = true if there are no children running and no connection being served currently
shouldclose = False         # flag = true if a shutdown has been requested
resptimelist = list()          # time taken


# Kill Walkers AKA zombies
def rick_grimes(signum, frame):
    while True:
        try:
            pid, status = os.waitpid(
                -1,          # Wait for any child process
                 os.WNOHANG  # Do not block and return EWOULDBLOCK error
            )
        except OSError:
            return

        if pid == 0:  # zombies are dead
            return

# send a response to clients connecting to / or /hash
def handle_request(client_connection):
    request = client_connection.recv(1024)
    incoming = request.decode('utf-8', errors='replace')
    print (incoming, len(incoming))
    if len(incoming) > 0:
        try:
            verburl = incoming.split(' HTTP')[0]    # GET or POST in this case
            print ("verburl=",verburl)
            url = verburl.split(' ')[1]
            print ("url=" , url)
            if url == '/':
                print('Got request to shutdown')
                http_response = b"""\
HTTP/1.1 200 OK

Shutting down
"""
                client_connection.sendall(http_response)
                #print ("response=" + http_response)
                write_shutdown()
            if url == '/hash':
                pass2hash = incoming.split("password=", 1)[1]   #parse the item after the key password=
                print ("pass=", pass2hash)
                time.sleep(5)
                http_response = b"""\
HTTP/1.1 200 OK

""" + base64.b64encode(hashlib.sha512(pass2hash).digest()) + b"""\

"""
                client_connection.sendall(http_response)

        except:
            print ('Unable to process request.')
            http_response = b"""\
HTTP/1.1 404 Not Found

You have requested something that doesn't exist! Move along...

"""
            client_connection.sendall(http_response)


# serve forever unless we get a shutdown request from the client connection
def serve_forever(sport):
    stopme = False
    SERVER_ADDRESS = (HOST, PORT) = '', sport # ex: 8888
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port} ...'.format(port=PORT))

    # allow interrupt event go kill zombies
    signal.signal(signal.SIGCHLD, rick_grimes)

    while os.path.exists("shutdown.txt") is False:
        print ("stopme=", stopme)
        
        try:
            print ("Accepting client connection")
            client_connection, client_address = listen_socket.accept()
        except IOError as e:
            #normal way of handling would-be blocked connections
            code, msg = e.args
            # restart 'accept' if it was interrupted
            if code == errno.EINTR:
                continue
            else:
                raise

        pid = os.fork()
        if pid == 0:  # we are in the context of the child process which must exit when done
            print("in child proc")
            try:
                print('Trying to close child connection')
                listen_socket.close()  # close child copy
                handle_request(client_connection)
            finally:
                client_connection.close()
                print ("Closed child connection")
                os._exit(0)
        else:  # parent
            print("parent")
            client_connection.close()  # close parent copy and loop over
            if os.path.exists("shutdown.txt") is True:
                os._exit(0)


# write our average data to db/file and we'll load it and display it dynamically
def write_avg(newtime):
    try:
        fh = open("time.txt", "a+")
        fh.writelines(newtime)
        fh.close()
    except IOError as e:
        print("Could not create time.txt file")

# read our shutdown state data from a db or file
def read_avg():
    mydata = "no time data yet"
    try:
        fh = open("time.txt","r")
        mydata = json.load(fh)
        fh.close()
    except IOError as e:
        print("Could not read time data from time.txt")

# write our shutdown state to a db or file so it's visible to all processes
def write_shutdown():
    print("Writing shutdown")
    with open("shutdown.txt", "w") as f:
        json.dump("{closeme}", f)
    f.close()


# get command-line args and validate them
if __name__ == '__main__':
    if os.path.exists("shutdown.txt"):
        os.remove("shutdown.txt")
    parser = argparse.ArgumentParser(
        description='WebServer.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8888,
        help='Port server listens on.'
    )
    args = parser.parse_args()
    if args.port in range(1,32767):
        serve_forever(args.port)
        
    else:
        print ("Argument --port is not in the integer range and cannot be assigned to a socket.")
        os.exit(0)

