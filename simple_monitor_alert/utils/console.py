from itertools import combinations

import sys

import six


def get_terminal_size():
    # http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        ### Use get(key[, default]) instead of a try/catch
        #try:
        #    cr = (env['LINES'], env['COLUMNS'])
        #except:
        #    cr = (25, 80)
    return int(cr[1]), int(cr[0])


def pprint_list(input_list, terminal_size=None):
    # http://stackoverflow.com/questions/25026556/output-list-like-ls
    term_width, term_height = terminal_size or get_terminal_size()
    if len(str(input_list)) <= term_width:
        print(input_list)
        return

    repr_list = [x.decode('utf-8') if six.PY2 else x for x in input_list]
    # repr_list = [x.decode('utf-8') for x in input_list]
    # repr_list = [repr(x) for x in input_list]
    # min_chars_between = 3 # a comma and two spaces
    min_chars_between = 2
    # usable_term_width = term_width - 3 # For '[ ' and ']' at beginning and end
    usable_term_width = term_width
    min_element_width = min( len(x) for x in repr_list ) + min_chars_between
    max_element_width = max( len(x) for x in repr_list ) + min_chars_between
    if max_element_width >= usable_term_width:
        ncol = 1
        col_widths = [1]
    else:
        # Start with max possible number of columns and reduce until it fits
        ncol = int(min( len(repr_list), usable_term_width / min_element_width  ))
        while True:
            col_widths = [ max( len(x) + min_chars_between \
                                for j, x in enumerate( repr_list ) if j % ncol == i ) \
                                for i in range(ncol) ]
            if sum( col_widths ) <= usable_term_width: break
            else: ncol -= 1

    # # sys.stdout.write('[ ')
    # for i, x in enumerate(repr_list):
    #     # if i != len(repr_list)-1: x += ','
    #     sys.stdout.write( x.ljust( col_widths[ i % ncol ] ) )
    #     if i == len(repr_list) - 1:
    #         sys.stdout.write('\n')
    #         pass
    #     elif (i+1) % ncol == 0:
    #         sys.stdout.write('\n')
    #         # sys.stdout.write('\n  ')

    # sys.stdout.write('[ ')
    output = ''
    for i, x in enumerate(repr_list):
        # if i != len(repr_list)-1: x += ','
        output += x.ljust(col_widths[i % ncol])
        if (i + 1) % ncol == 0:
            output += '\n'
        # sys.stdout.write('\n  ')
    return output


# def print_columns(elements):
#     # http://stackoverflow.com/questions/9989334/create-nice-column-output-in-python
#     columns = list(grouper(2, elements))
#     col_width = max(len(word) if word else 0 for row in columns for word in row) + 2  # padding
#     return '\n'.join(["".join(word.ljust(col_width) if word else '' for word in row) for row in columns ])
