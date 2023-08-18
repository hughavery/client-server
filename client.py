#client file (client.py)
import socket
import sys 
import select

def client():
    """requests the date or time from the server
    in either english maori or german"""
    list_of_parameters = sys.argv
    print(list_of_parameters)
    list_of_parameters.pop(0)
    info_type = list_of_parameters[0]
    ip_adress = list_of_parameters[1]
    port_number = list_of_parameters[2]
    
    
   
    try:
        socket.getaddrinfo(ip_adress, port_number)
    except Exception:
        print("hostname does not exist or the IP address given is notwell-formed")
        return None
    localaddr = socket.getaddrinfo(ip_adress, port_number)
    
    if len(list_of_parameters) != 3:
        print("Error expected 3 arguments")
        return None
    
    elif info_type != "date" and info_type != "time":
        print("expected a date or time input got neither")
        return None
   

        
    elif int(list_of_parameters[2]) < 1024 or int(list_of_parameters[2]) > 64000:
        print("port number need to be between 1,024 and 64,000")
        return None
    
    
    
    request_packet = bytearray(6)
    magic_bit = 0x497E
    #byte1 
    byte1 = magic_bit >> 8
    request_packet[0] = byte1
    #byte2
    mask = 255
    byte2 = mask & magic_bit
    request_packet[1] = byte2
    #byte3&4
    request_packet[2] = 0
    request_packet[3] = 1
    #byte5&6 is num ok 
    if info_type == "date":
        request_packet[4] = 0
        request_packet[5] = 1
    else:
        request_packet[4] = 0
        request_packet[5] = 2        
        
    print("waiting")
    client_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)   
    
    client_sock.sendto(request_packet,(ip_adress,int(port_number)))
    
  
    read_ready = select.select([client_sock], [], [], 1.0)
    if len(read_ready[0]) == 0:
        print("DT responce packet has not arrived") 
        client_sock.close()
        return None
    dt_response_packet_info = read_ready[0][0]
    to_extract = dt_response_packet_info.recvfrom(512)
    
    dt_response_packet = to_extract[0]
    dt_resp_address = to_extract[1]
    
    
    if check_dt_response_packet_validity(dt_response_packet) == False:
        client_sock.close()
        return None
    
    #print contents of bytearray
    magic_num = (dt_response_packet[0] << 8) | dt_response_packet[1] 
    
    print(f"magic number is {magic_num}")
    print(f"packet Type is {dt_response_packet[3]}")

    
    print(f"language code is {dt_response_packet[5]}")
    #year
    year = (dt_response_packet[6] << 8) | dt_response_packet[7] 
    print(f"year is {year}")
    
    print(f"month is {dt_response_packet[8]}")
    print(f"day is {dt_response_packet[9]}")
    print(f"hour is {dt_response_packet[10]}")
    print(f"minute is {dt_response_packet[11]}")
    print(f"length field is {dt_response_packet[12]}")
    
    text = dt_response_packet[13:]
    text = text.decode("utf-8")
    
    print(text)
    
def check_dt_response_packet_validity(dt_response_packet):
    """does a full check of the validity of the response packet
    and prints any errors that occur returns false if packet is 
    not valid true otherwise"""
   
    
    if len(dt_response_packet) < 13:
        print("DT-responce packet contains less thatn 13 bytes")
        return False
    
    #magicNumberCheck
    magic_number = (dt_response_packet[0] << 8) | dt_response_packet[1]
    if magic_number != 0x497E:
        print("magic_number of DT-responce is invalid")
        return False
    
    if dt_response_packet[3] != 2:
        print("PacketType of DT-responce is invalid")
        return False
        
    if dt_response_packet[5] != 1 and dt_response_packet[5] != 2 and dt_response_packet[5] != 3:
        print("LanguageCode of DT-responce is invalid")
        return False
    
    #yearCheckfield.

    
    year = (dt_response_packet[6] << 8) | dt_response_packet[7]
    if year >= 2100:
        print("year of DT-responce is invalid")
        return False
        
    if dt_response_packet[8] < 1 or dt_response_packet[8] > 12:
        print("Month of DT-responce is invalid")
        return False
    
    if dt_response_packet[9] < 1 or dt_response_packet[9] > 31:
        print("Day of DT-responce is invalid")
        return False
    
    if dt_response_packet[10] < 0 or dt_response_packet[10] > 23:
        print("Hour of DT-responce is invalid")
        return False
    
    if dt_response_packet[11] < 0 or dt_response_packet[11] > 59:
        print("Minute of DT-responce is invalid")
        return False
    
    
        
    lenth_txt = dt_response_packet[12]
    if len(dt_response_packet) != 13 + lenth_txt:
        print("string representation of date/time is incorrect")
        return False
        
    return True
  
client()