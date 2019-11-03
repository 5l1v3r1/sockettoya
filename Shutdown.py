#####################################################################
# Test shutdown of web server given request to /                    #
#                                                                   #
#####################################################################
import argparse
import os
import socket

CHUNK_SIZE=1024

# get data from sock
def receive_all(sock, chunk_size=CHUNK_SIZE):
    chunks = []
    while True:
        chunk = sock.recv(int(chunk_size))
        if chunk:
            chunks.append(chunk)
        else:
            break

    return ''.join(chunks)


#start main with command line args. Port is the only useful command-line for this function
def main(max_clients, max_conns, cport):
    socks = []
    REQUEST = b"""\
POST / HTTP/1.1\r\nHost: localhost:""" + str(cport) + b"""\r\nUser-Agent: curl/7.54.0\r\nAccept: */*\r\nContent-Length: 0\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n"""
    SERVER_ADDRESS = '127.0.0.1', cport
    for client_num in range(max_clients):
        pid = os.fork()
        if pid == 0:
            for connection_num in range(max_conns):
                try:
                    # set up the socket options, print our request and print received data
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(SERVER_ADDRESS)
                    sock.sendall(REQUEST)
                    print(REQUEST)
                    socks.append(sock)
                    print(connection_num)
                    data = receive_all(sock, CHUNK_SIZE)
                    print(data)
                    # Look for response from web server that includes the key words indicating a shutdown is successful
                    if (data.find("Shutting down") != -1):
                        print("Success")
                    else:
                        print("Fail")
                    sock.close()
                finally:
                    os._exit(0)    #exit the child or we will be at risk of forking the child process as well


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Test client for LSBAWS.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--max-conns',
        type=int,
        default=1,
        help='Maximum number of connections per client.'
    )
    parser.add_argument(
        '--max-clients',
        type=int,
        default=1,
        help='Maximum number of clients.'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8888,
        help='Port server listens on.'
    )
    args = parser.parse_args()
    # add check on args
    main(args.max_clients, args.max_conns, args.port)