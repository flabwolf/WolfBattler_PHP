import argparse
class testserv(object):
    def send_msg_2(self,client,server,message):
        server.send_message(client,"{}".format(
            message).encode('iso-8859-1').decode("utf-8"))
        print(message.encode('iso-8859-1').decode("utf-8"))
        print(client)