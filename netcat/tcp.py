import socket 

target_host = "www.google.com"
target_port = 80

# 建立 socket 物件
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 客戶端連接到主機
client.connect((target_host, target_port))

# 傳送資料
client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

# 接收資料
response = client.recv(4096)
print(response.decode())
# 關閉 socket
client.close()