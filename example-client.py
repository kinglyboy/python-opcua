import logging
import time

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()


from opcua import Client
from opcua import ua


class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    """

    def data_change(self, handle, node, val, attr):
        print("Python: New data change event", handle, node, val, attr)

    def event(self, handle, event):
        print("Python: New event", handle, event)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    #logger = logging.getLogger("KeepAlive")
    #logger.setLevel(logging.DEBUG)

    client = Client("opc.tcp://localhost:4841/freeopcua/server/")
    # client = Client("opc.tcp://admin@localhost:4841/freeopcua/server/") #connect using a user
    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        print("Root node is: ", root)
        objects = client.get_objects_node()
        print("Objects node is: ", root)

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        print("Children of root are: ", root.get_children())

        # get a specific node knowing its node id
        #var = client.get_node(ua.NodeId(1002, 2))
        #var = client.get_node("ns=3;i=2002")
        #print(var)
        #var.get_data_value() # get value of node as a DataValue object
        #var.get_value() # get value of node as a python builtin
        #var.set_value(ua.Variant([23], ua.VariantType.Int64)) #set node value using explicit data type
        #var.set_value(3.9) # set node value using implicit data type

        # Now getting a variable node using its browse path
        myvar = root.get_child(["0:Objects", "2:NewObject", "2:MyVariable"])
        obj = root.get_child(["0:Objects", "2:NewObject"])
        print("myvar is: ", myvar)

        # subscribing to a variable node
        handler = SubHandler()
        sub = client.create_subscription(500, handler)
        handle = sub.subscribe_data_change(myvar)
        time.sleep(0.1)

        # we can also subscribe to events from server
        sub.subscribe_events()
        # sub.unsubscribe(handle)
        # sub.delete()

        # calling a method on server
        res = obj.call_method("2:multiply", 3, "klk")
        print("method result is: ", res)

        embed()
    finally:
        client.disconnect()
