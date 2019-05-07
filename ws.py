import socket

class Req():
	GET=0x1
	POST=0x2

class Request():
	def __init__(self, req: int, content: str):
		self.req = req
		self.content = content

class Router():
	def route(self, rt, reqs):
		def set_route(func):
			self.routes[rt] = (lambda : send_response(self.conn, func()), reqs)
			return func
		return set_route

	def handle_route(self, rt, reqs):
		# prevent bad reqs
		if rt in self.routes:
			r = self.routes[rt]
			if r[1] & reqs:
				r[0]()

	def __init__(self):
		self.routes = {}
		self.conn = None

router = Router()

class Context():
	req_dict = {"GET":Req.GET,"POST":Req.POST}
	def __init__(self, ip: str, port: int, buf_size: int):
		self.ip = ip
		self.port = port
		self.buf_size = buf_size

def handle_req(ctx: Context, data: str):
	headers = data.split('\r\n')
	req_header = headers[0].split()
	req = req_header[0]
	route = req_header[1]
	router.handle_route(route, ctx.req_dict[req])

def send_response(conn, content):
	if conn is None:
		return
	msg = "{} {} {}\r\n".format("HTTP/1.1", 200, "OK")
	msg += "{}: {}\r\n".format("Content-Type", "text/html")
	msg += "{}: {}\r\n".format("Content-Length", len(content))
	msg += "\r\n"
	msg += content
	conn.send(bytes(msg, 'utf-8'))

@router.route("/", Req.GET)
def my_func():
	return "HELLO XD"

def main():
	ctx = Context('127.0.0.1', 5000, 8192)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((ctx.ip, ctx.port))
	sock.listen(1)
	
	conn, addr = sock.accept()
	router.conn = conn
	print("{} and {}".format(conn.getsockname(), conn.getpeername()))
	while True:
		data = conn.recv(ctx.buf_size)
		if data:
			handle_req(ctx, data.decode('utf-8'))
	conn.close()
	
if __name__ == "__main__":
	main()
