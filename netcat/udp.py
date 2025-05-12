import socket

target_host = "127.0.0.1"
target_port = 8081

# 建立 socket 物件
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 傳送資料
client.sendto(b"AAABBBCCC", (target_host, target_port))

# 接收資料
data, addr = client.recvfrom(4096)

print(data.decode())
# 關閉 socket
client.close()
# 這段程式碼使用 UDP 協議建立了一個客戶端，並向指定的主機和端口發送了一個簡單的字串 "AAABBBCCC"。然後，它等待接收來自伺服器的回應，並將其打印出來。最後，關閉 socket 連接。