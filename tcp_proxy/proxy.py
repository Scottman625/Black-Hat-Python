import sys
import socket
import threading

HEX_FILTER = ''.join([(len(repr(chr(i)))==3) and chr(i) or '.' for i in range(256)])

def hexdump(src, length=16,show=True):
    if isinstance(src, bytes):
        src = src.decode()
    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])

        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results
    
def receive_from(connection):
    buffer = b''
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        print(f"[!] Error receiving data: {e}")
    return buffer

def request_handler(buffer):
    # # 統一轉換行尾符號為CRLF
    # if b'\r\n' not in buffer:
    #     buffer = buffer.replace(b'\n', b'\r\n')
    # # 示例: 打印FTP登錄憑證
    # if buffer.startswith(b'USER') or buffer.startswith(b'PASS'):
    #     print(f"[*] 截獲認證信息: {buffer.decode().strip()}")
    return buffer

def response_handler(buffer):
    # 這裡放入修改封包的程式
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    try:
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((remote_host, remote_port))
        print(f"[*] Connected to remote host {remote_host}:{remote_port}")

        remote_buffer = b''  # 初始化 remote_buffer

        if receive_first:
            remote_buffer = receive_from(remote_socket)
            if remote_buffer:
                print("[<==] Received initial data from remote:")
                hexdump(remote_buffer)
                remote_buffer = response_handler(remote_buffer)
                if len(remote_buffer):
                    print(f"[<==] Sending {len(remote_buffer)} bytes to localhost.")
                    client_socket.send(remote_buffer)

        while True:
            local_buffer = receive_from(client_socket)
            if len(local_buffer):
                print(f"[==>] Received {len(local_buffer)} bytes from localhost.")
                hexdump(local_buffer)

                local_buffer = request_handler(local_buffer)
                remote_socket.send(local_buffer)
                print("[==>] Sent to remote.")

            remote_buffer = receive_from(remote_socket)
            if len(remote_buffer):
                print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
                hexdump(remote_buffer)

                remote_buffer = response_handler(remote_buffer)
                client_socket.send(remote_buffer)
                print("[<==] Sent to localhost.")

            if not len(local_buffer) and not len(remote_buffer):
                print("[*] No more data. Closing connections.")
                break

    except Exception as e:
        print(f"[!] Error in proxy_handler: {e}")
    finally:
        try:
            client_socket.close()
            remote_socket.close()
        except:
            pass

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f'[!] Problem on bind: {e}')
        print(f"[!!] Failed to listen on {local_host}:{local_port}")
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(1)

    print(f"[*] Listening on {local_host}:{local_port}")
    server.listen(5)
    
    try:
        while True:
            client_socket, addr = server.accept()
            print(f"> Received incoming connection from {addr[0]}:{addr[1]}")
            proxy_thread = threading.Thread(
                target=proxy_handler,
                args=(client_socket, remote_host, remote_port, receive_first)
            )
            proxy_thread.start()
    except KeyboardInterrupt:
        print("\n[!] Server shutting down...")
    finally:
        server.close()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(1)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5].lower() == 'true'
    
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()