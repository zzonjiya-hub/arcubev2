import http.server, ssl, os

D = r'C:\Users\Kiseok\Desktop\[오픈코드]\KSMS AR큐브 v2'
os.chdir(D)

server = http.server.ThreadingHTTPServer(('0.0.0.0', 8445), http.server.SimpleHTTPRequestHandler)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain('cert.pem', 'key.pem')
server.socket = ctx.wrap_socket(server.socket, server_side=True)
print('HTTPS: https://localhost:8445 또는 https://192.168.0.12:8445')
server.serve_forever()
