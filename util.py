import re

READ_STEP = 250

def grab_partn(f, start_delimiter, end_delimiter, buffer=''):
    """
    return the bit we want and where to start from next time
    """
    
    start_re = re.compile(start_delimiter)

    def next_bit(regex):
        nonlocal buffer
        lastbit = buffer
        while True:
            bit = f.read(READ_STEP)

            if len(bit) == 0:
                raise EOFError

            buffer+= bit
            match = re.search(regex, lastbit + bit)
            if match:
                if lastbit == buffer:
                    return (len(buffer) - len(bit)) + match.span()[0]
                else:
                    return (len(buffer) - len(bit) - len(lastbit)) + match.span()[0]
            lastbit = bit

    start_pos = next_bit(start_re)
    buffer = buffer[start_pos:]

    end_re = re.compile(end_delimiter)
    end_pos = next_bit(end_re) + len(end_delimiter)
    
    return (buffer[:end_pos], buffer[end_pos:])

def grab_parto(f, start_delimiter, end_delimiter, buffer=''):
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
    
#    print(start, end)
    return (buffer[:end], buffer[end:])


def make_title(text):
    return text.replace(' ', '_').replace('/', ':')


