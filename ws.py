import socket
import select

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
			self.routes[rt] = (lambda conn: send_response(conn, func()), reqs)
			return func
		return set_route

	def handle_route(self, conn, rt, req):
		# prevent bad reqs
		if rt in self.routes:
			r = self.routes[rt]
			if r[1] & req:
				r[0](conn)

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
		self.conns = {}

def handle_req(ctx: Context, conn, data: str):
	print(data)
	headers = data.split('\r\n')
	req_header = headers[0].split()
	req = req_header[0]
	route = req_header[1]
	router.handle_route(conn, route, ctx.req_dict[req])

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

def add2buff(buffer: str, add: str):
	buff = buffer + add
	return (buff, len(buff) >= 4 and buff[-4:] == "\r\n\r\n")

if __name__ == "__main__":
	ctx = Context('127.0.0.1', 5000, 1024)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((ctx.ip, ctx.port))
	sock.listen(1)
	sock_list = [sock]

	while True:
		read_rdy, write_rdy, err_rdy = select.select(sock_list, [], [])
		print(read_rdy)
		for conn in read_rdy:
			if conn is sock:
				s, addr = sock.accept()
				print("{} and {}".format(s.getsockname(), s.getpeername()))
				ctx.conns[s] = ""
				sock_list.append(s)
				continue
			print(1)
			data = conn.recv(ctx.buf_size)
			print(2)
			if not data:
				continue
			ctx.conns[conn], res = add2buff(ctx.conns[conn], data.decode('utf-8'))
			print(3)
			print(res)
			if res:
				handle_req(ctx, conn, ctx.conns[conn])
				ctx.conns[conn] = ""
			print(4)
	conn.close()

