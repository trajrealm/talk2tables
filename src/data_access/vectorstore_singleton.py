
vectorstore = None

def get_vectorstore():
    return vectorstore

def set_vectorstore(vstore):
    global vectorstore
    vectorstore = vstore