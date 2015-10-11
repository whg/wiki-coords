
READ_STEP = 100

def grab_part(f, start_delimiter, end_delimiter, buffer=''):
    """
    return the bit we want and where to start from next time
    """
    
    while start_delimiter not in buffer:
        bit = f.read(READ_STEP)
        if len(bit) == 0:
            raise EOFError
        buffer+= bit

    start = buffer.find(start_delimiter)
    buffer = buffer[start:]

    while end_delimiter not in buffer:
        bit = f.read(READ_STEP)
        if len(bit) == 0:
            raise EOFError
            
        buffer+= bit

    end = buffer.find(end_delimiter) + len(end_delimiter)
    return (buffer[:end], buffer[end:])



def make_title(text):
    return text.replace(' ', '_').replace('/', ':')


