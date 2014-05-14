# S-expression input of exactly the same as serpent.

import io


# Convenience function.
def find_stringstart(string, arrays, i):
    for el in arrays:
        if string[:len(el[i])] == el[i]:
            return el
    return None


class SExprParser:

    # Class essentially just stops me from having to pass these all the time.
    # Just do SExprParser().parse(), dont neccesarily need a variable.
    def __init__(self, start_end = [('(', ')',  True,  True,  'call'),
                                    (';', '\n', False, False, 'scrub'),
                                    ('"', '"',  True,  True,  'str')],
                 wrong_end_warning=True,
                 white=[' ', '\t', ' '],
                 earliest_macro={}):
        self.start_end = start_end
        self.wrong_end_warning = wrong_end_warning
        self.white = white
        self.earliest_macro = {}  # Dictionary of functions that act as macros.

    def raw_parse_plain(self, stream, initial='', end=')'):
        cur = initial
        i = 0
        if len(cur) < len(end):
            cur = cur + stream.readline()

        while cur[i:i + len(end)] != end:
            i += 1
            n = 0
            while i + len(end) > len(cur):
                cur = cur + stream.readline()
                n += 1
                if n > 16:  # TODO need stream.eof
                    return cur[i + len(end):], cur[:i]

        return cur[i + len(end):], cur[:i]

    # Returns a pair of arguments, the result and the remaining string.
    def raw_parse_stream(self, stream, initial='',
                         se=('top', ')', False, False, 'top')):
        cur = initial
        out = []

        def add(what):
            if what != '':  # Dont do empty strings.
                out.append(what)

        def add_sub(added):
            if type(added[0]) is str and added[0] in self.earliest_macro:
                out.append(self.earliest_macro[added[0]](added))
            else:
                out.append(added)

        i = 0
        while True:

            while i < len(cur):

                if cur[i] in self.white:  # Whitespace separates symbols.
                    add(cur[:i])
                    cur = cur[i + 1:]  # Update cur and integer.
                    i = 0
                    continue

                # Potentially start subtree.
                start = find_stringstart(cur[i:], self.start_end, 0)
                if start is not None:
                    add(cur[:i])

                    if start[4] in ['scrub', 'plain']:  # Dont parse inside.
                        left, got = self.raw_parse_plain(stream,
                                                         cur[i + len(start[0]):], start[1])

                        if start[4] == 'plain':  # Use it.
                            add_sub([start[5], got])

                        cur = left
                    else:
                        left, ret = self.raw_parse_stream(stream,
                                                          cur[i + len(start[0]):], se=start)
                        # The ender-starter associated is optionally attached.
                        if start[4] is None:
                            add_sub(ret)
                        else:
                            add_sub([start[4]] + ret)
                        cur = left
                    i = 0  # As `cur` is set to be used with reset integer.
                    continue

                # Potentially stop substree.
                if self.wrong_end_warning and se[3]:

                    end = find_stringstart(cur[i:], self.start_end, 1)

                    if end is not None:
                        if end[1] != se[1] and end[2]:
                            raise((end, se, i))  # Error, starter and ender did not match.
                        else:  # Correct ending.
                            add(cur[:i])
                            return cur[i + len(se[1]):], out
                # (cheaper way, only checks the current one.)
                elif cur[i:i+len(se[1])] == se[1]:
                    add(cur[:i])
                    return cur[i + len(se[1]):], out

                i += 1

            n = 0

            extend = stream.readline()
            while extend == '':  # TODO need stream.eof
                extend = stream.readline()
                n += 1
                if n > 16:
                    if cur != '':
                        out.append(cur)
                        return '', out
                    else:
                        return '', out
            cur = cur + extend

        assert False

    def parse_stream(self, stream, initial=''):
        return self.raw_parse_stream(stream, initial=initial)[1]

    def parse(self, string):
        return self.parse_stream(io.StringIO(string))


# Note: it doesnt do indentation.. or newlines.
# also only does the s-expression way.
def s_expr_write(stream, input, o='(', c=')', w=' '):
    def handle_1(el):
        if type(el) is list:
            stream.write(str(o))
            s_expr_write(stream, el, o=0, c=c, w=w)
            stream.write(str(c))
        else:
            stream.write(str(el))

    handle_1(input[0])
    for el in input[1:]:
        stream.write(w)
        handle_1(el)


def s_expr_str(tree, o='(', c=')', w=' '):
    stream = io.StringIO("")
    s_expr_write(stream, tree, o=o, c=c, w=w)
    stream.seek(0)  # Dont forget to read back!
    return stream.read()
