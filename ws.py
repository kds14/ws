import socket

class Context():
	def __init__(self, ip: str, port: int, buf_size: int):
		self.ip = ip
		self.port = port
		self.buf_size = buf_size

def send_text(conn, text):
	msg = "{} {} {}\r\n".format("HTTP/1.1", 200, "OK")
	msg += "{}: {}\r\n".format("Content-Length", len(text))
	msg += "{}: {}\r\n".format("Content-Type", "text/html")
	msg += "\r\n"
	msg += text
	conn.send(bytes(msg, 'utf-8'))

def main():
	ctx = Context('127.0.0.1', 5000, 1024)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((ctx.ip, ctx.port))
	sock.listen(1)
	
	conn, addr = sock.accept()
	print("{} and {}".format(conn.getsockname(), conn.getpeername()))
	while True:
		data = conn.recv(ctx.buf_size)
		if not data:
			break
		print(data.decode('utf-8').split('\r\n'))
		send_text(conn, "HELLO! :D");
	conn.close()
	
if __name__ == "__main__":
	main()
