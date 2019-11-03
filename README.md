# sockettoya
Messing with sockets in Python to make a web server using low level calls and forked processes for fun

**There are three files in the project...**
1) a HTTP server: WebServer.py
2) a HTTP multi-request client: Client.py
3) a HTTP client to call shutdown: Shutdown.py

**Runtime notes: The files have only been tested in Python 2.7**

**Why did I build it in Python?** 
A) Python has good socket support and I wanted to try a low level implementation of a asynchronous web server
B) I'm learning Python and it's fun to use in hacking related projects
C) I thought it would give me some practice before writing the back end of Hacker Mode in Python

**What does it do?**
It serves up a URL to return a hash and any request to / causes it to shut down while waiting for connections. The Client app simulates load and tests the values returned for the proper hash value. The Shutdown app simulates a CURL request to shut down the server.

**How to use the server and clients?**
Instantiate the server with: *python WebServer.py --port 8000*  
{Or replace 8000 with whatever port you want. If you leave off the port number it will default to 8888}

Instantiate the client with: *python Client.py --max-conns 1 --max-clients 5 --port 8000*
{Or replace the port number with whatever port you want. Default is 8888. --max-conns doesn't really affect things but it's probably best to leave it at 1, and change max-clients to however many users you want to simulate. Since it's a test application, I typically run it between 3 and 10}

Instantiate the shutdown test app with *Shutdown.py --port 8000*
{Or replace 8000 with the port number you want. Default is 8888}

Known Issues:
The test apps do not always yield the console prompt but do finish.





