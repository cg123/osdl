# Copyright (c) 2013, Charles O. Goddard
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import re


class Token(object):
    _tokentype = 'NULLTOKEN'

    def tokentype(self):
        return self._tokentype

    def __init__(self, location=None):
        self.location = location


class IntToken(Token):
    _tokentype = 'int'

    def __init__(self, value, location=None):
        self.val_int = value
        self.location = location

    re = re.compile('^(0x[0-9a-fA-F]+|' +
                    '0b[01]+|0o[0-7]+|' +
                    '[0-9]+)')

    @staticmethod
    def match(s):
        match = IntToken.re.match(s)
        if match:
            return len(match.group(0))

    @staticmethod
    def parse(match, location=None):
        value = 0
        if match[:2] == '0x':
            value = int(match[2:], 16)
        elif match[:2] == '0b':
            value = int(match[2:], 2)
        elif match[:2] == '0o':
            value = int(match[2:], 8)
        else:
            value = int(match)
        return IntToken(value, location)

    def repr(self):
        return 'IntToken(%r, %r)' % (self.val_int, self.location)
    __repr__ = repr


class FloatToken(Token):
    _tokentype = 'float'

    def __init__(self, value, location=None):
        self.val_float = value
        self.location = location

    re = re.compile('^([0-9]+\.[0-9]*|' +
                    '[0-9]*\.[0-9]+|' +
                    '[0-9]+e[+-][0-9]+)')

    @staticmethod
    def match(s):
        match = FloatToken.re.match(s)
        if match:
            return len(match.group(0))

    @staticmethod
    def parse(match, location=None):
        return FloatToken(float(match), location)

    def repr(self):
        return 'FloatToken(%r, %r)' % (self.val_float, self.location)
    __repr__ = repr


class IdentifierToken(Token):
    _tokentype = 'identifier'

    def __init__(self, value, location=None):
        self.val_str = value
        self.location = location

    re = re.compile('^[a-zA-Z][a-zA-Z0-9_]*')

    @staticmethod
    def match(s):
        match = IdentifierToken.re.match(s)
        if match:
            return len(match.group(0))

    @staticmethod
    def parse(match, location=None):
        return IdentifierToken(match, location)

    def repr(self):
        return 'IdentifierToken(%r, %r)' % (self.val_str, self.location)
    __repr__ = repr


class CharacterToken(Token):
    _tokentype = 'character'

    def __init__(self, value, location=None):
        self.val_str = value
        self.location = location

    def repr(self):
        return 'CharacterToken(%r, %r)' % (self.val_str, self.location)
    __repr__ = repr


class EOFToken(Token):
    _tokentype = 'EOF'

    def repr(self):
        return 'EOFToken(%r)' % (self.location,)
    __repr__ = repr


token_handlers = [
    (IdentifierToken.match, IdentifierToken.parse),
    (FloatToken.match, FloatToken.parse),
    (IntToken.match, IntToken.parse)
]


def tokenize(string, filename='<N/A>'):
    lineno = 1
    colno = 1
    while string:
        if string[0].isspace():
            if string[0] == '\n':
                lineno += 1
                colno = 1
            else:
                colno += 1
            string = string[1:]
            continue

        handled = False
        for (matcher, parser) in token_handlers:
            matched = matcher(string)
            if not matched:
                continue
            yield parser(string[:matched], (filename, lineno, colno))
            string = string[matched:]
            colno += matched
            handled = True
            break

        if not handled:
            yield CharacterToken(string[0], (filename, lineno, colno))
            string = string[1:]
    yield EOFToken((filename, lineno, colno))
