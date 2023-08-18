#server file (server.py)
import socket
import sys
import select
import os
from datetime import datetime


def server():
    """delivers the time or date to clients in the specified language"""
    list_of_parameters = sys.argv
    list_of_parameters.pop(0)
    
    fail = False
    for i in list_of_parameters:
        if int(i) < 1024 or int(i) > 64000:
            fail = True
    if fail:
        print("these port numbers are not in the range 1024~64000")
        return None
    
    english = int(list_of_parameters[0])
    maori = int(list_of_parameters[1])
    german = int(list_of_parameters[2])
    
    
    engish_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    maori_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    german_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    
    port_dictionary = {english:engish_socket, maori:maori_socket, german:german_socket}
    
    
    engish_socket.bind(("127.0.0.1", english))
    maori_socket.bind(("127.0.0.1", maori))
    german_socket.bind(("127.0.0.1", german))
    
   
    #infinate loop
    while True:
        
        try:
            print("Now listening...")
            
            read_ready = select.select([engish_socket,maori_socket,german_socket], [], [], None)
            print("informatin received")
            clientsocket_info = read_ready[0][0]
            print(clientsocket_info)
            to_extract = clientsocket_info.recvfrom(6)
    
            address_for_to_send = to_extract[1]
            byte_array_packet = to_extract[0]
    
            language = None
            #stores port number used for language
            portNumber = clientsocket_info.getsockname()[1]
            if portNumber == english:
                language = "english"
            elif portNumber == maori:
                language = "maori"
            else:
                language = "german"
            
            #checks validity and prints errors 
            if is_valid_request(byte_array_packet) == False:
                continue
             
            
            if byte_array_packet[5] == 1:
                date_time_info = get_date_time("date",language)
            else:
                date_time_info = get_date_time("time",language)
                
           
            
            lenght_text = len(date_time_info[0])
            if lenght_text > 255:
                print("the date or time has to many char please request again soon")
                continue
            
            #prepare responce packet
            responce_packet = packet_former(date_time_info,lenght_text,language)
            
            server_sock = port_dictionary[portNumber]
    
            #send info back to client
            server_sock.sendto(responce_packet,address_for_to_send)
            print("sent package")
        
        except KeyboardInterrupt:
            engish_socket.close()
            maori_socket.close()
            german_socket.close()
            print("\nServer has closed")
            return None


def is_valid_request(byte_array_packet):
    """checks if packet is valid, returns false if 
    packet is not valid true otherwise"""
    
    magicNumber = 0x497E
    magicNum = (byte_array_packet[0] << 8) | byte_array_packet[1]
    
    if magicNumber != magicNum:
        print("magicNumber is invalid")
        return False
    
    if byte_array_packet[3] != 1:
        print("packetType is incorrect")
        return False
    
   
    if byte_array_packet[5] != 1 and byte_array_packet[5] != 2:
        print("requestType is not valid")
        return False
    
    if len(byte_array_packet) != 6:
        print("length of packet is not 6 bytes")
        return False
    
    return True



def get_date_time(string,language):
    """returns current date or time in the specified language"""
    now = datetime.now()
    currentMonth_int = datetime.now().month
    month_tuple = get_month_string(currentMonth_int)
    #date
    year = datetime.now().year
    
    if language == "english":
        month = month_tuple[0]
        usefull_info = (year, month,datetime.now().day,datetime.now().hour,datetime.now().minute)
        date = now.strftime(f"Today’s date is {month} %d, {year}") 
        time = now.strftime("The current time is %H:%M")
    elif language == "maori":
        month = month_tuple[1]
        
        date = now.strftime(f"Ko te ra o tenei ra ko {month} %d, {year}")
        time = now.strftime("Ko te wa o tenei wa %H:%M")
    else:
        month = month_tuple[2]
       
        date = now.strftime(f"Heute ist der %d. {month} {year}")
        time = now.strftime("Die Uhrzeit ist %H:%M")
        
    usefull_info = (year,datetime.now().month,datetime.now().day,datetime.now().hour,datetime.now().minute)
    
    if string == "date":    
        return (date, usefull_info)
    return (time, usefull_info)
    
    
            

def get_month_string(currentMonth):
    """uses a dictionary to find the string representation of the date or time
    in the specified language"""
    month_dictionary = {1: ("January","Kohitatea","Januar"),2: ("February","Hui-tanguru","Februar"),3: ("March","Poutu-te-rangi","Marz"),4:
    ("April","Paenga-whawha","April"),5: ("May","Haratua","Mai"),6: ("June","Pipiri","Juni"),7: ("July","Hongongoi","Juli")
    ,8: ("August","Here-turi-koka","August"),9: ("September","Mahuru","September"),10: ("October","Whiringa-a-nuku","Oktober")
    ,11: ("November","Whiringa-a-rangi","November"),12: ("December","Hakihea","Dezember")}

    return month_dictionary[int(currentMonth)]
    
    
    
    
def packet_former(date_time_info,lenght_text,language):
    """forms the responce packet that gets sent back to client"""
    date_time_string = date_time_info[0]
    datemonth_dictionary = {1: ("January","Kohitatea","Januar"),2: ("February","Hui-tanguru","Februar"),3: ("March","Poutu-te-rangi","Marz"),4:
    ("April","Paenga-whawha","April"),5: ("May","Haratua","Mai"),6: ("June","Pipiri","Juni"),7: ("July","Hongongoi","Juli")
    ,8: ("August","Here-turi-koka","August"),9: ("September","Mahuru","September"),10: ("October","Whiringa-a-nuku","Oktober")
    ,11: ("November","Whiringa-a-rangi","November"),12: ("December","Hakihea","Dezember")}
    useful_info = date_time_info[1]
    bytearray_date_time = date_time_string.encode("utf-8")
    lenght_text = len(bytearray_date_time)
    response_packet = bytearray(13)
    magic_bit = 0x497E
    
    #byte1 
    byte1 = magic_bit >> 8
    response_packet[0] = byte1
    #byte2
    mask = 255
    byte2 = mask & magic_bit
    response_packet[1] = byte2    
    #byte3&4
    response_packet[2] = 0
    response_packet[3] = 2
    
    #byte5&6
    if language == "english":
        response_packet[4] = 0
        response_packet[5] = 1        
    elif language == "maori":
        response_packet[4] = 0
        response_packet[5] = 2        
    else:
        response_packet[4] = 0
        response_packet[5] = 3     
        
    #byte7&8
    response_packet[6] = useful_info[0] >> 8
    response_packet[7] = useful_info[0] & 255

    #byte9
    response_packet[8] = useful_info[1]
    #byte10
    response_packet[9] = useful_info[2]
    #byte11
    response_packet[10] = useful_info[3]
    #byte12
    response_packet[11] = useful_info[4]
    #byte13
    response_packet[12] = lenght_text
    
    #concatenate array (adds text to end of bytearray)
    combined_responce_packet = response_packet + bytearray_date_time
 
    return combined_responce_packet
    
server()


