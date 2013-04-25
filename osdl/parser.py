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

from . import tokenizer


class ParseError(RuntimeError):
    def __init__(self, message, location=None):
        self.message = message
        self.location = location


class ASTNode(object):
    def __init__(self, source=None):
        self.source = source

    def repr(self):
        return '<NULL>'

    def __repr__(self):
        return self.repr()


class IntegerASTNode(ASTNode):
    def __init__(self, value, source=None):
        self.source = source
        self.val_int = value

    def repr(self):
        return '%r' % (self.val_int,)


class FloatASTNode(ASTNode):
    def __init__(self, value, source=None):
        self.source = source
        self.val_float = value

    def repr(self):
        return '%r' % (self.val_float,)


class DeclarationASTNode(ASTNode):
    def __init__(self, name, typename,
                 default=None, extern=False, source=None):
        self.source = source
        self.name = name
        self.typename = typename
        self.default = default
        self.extern = extern

    def repr(self):
        chunks = [self.name, ' ~ ', self.typename]
        if self.default:
            chunks = chunks + ['(', self.default.repr(), ')']
        if self.extern:
            chunks.append(' extern')
        return ''.join(chunks)


class ReferenceASTNode(ASTNode):
    def __init__(self, name, source=None):
        self.source = source
        self.name = name

    def repr(self):
        return self.name


class BinaryOpASTNode(ASTNode):
    def __init__(self, op, lh, rh, source=None):
        self.source = source
        self.operator = op
        self.lh = lh
        self.rh = rh

    def repr(self):
        return '(%s %s %s)' % (self.lh.repr(),
                             self.operator,
                             self.rh.repr())


class StructureASTNode(ASTNode):
    def __init__(self, name, fields, source=None):
        self.source = source
        self.name = name
        self.fields = fields


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.next()

    def next(self):
        self.current = next(self.tokens)

    def expect(self, type_, next_=True):
        node = self.current
        if not isinstance(node, type_):
            raise ParseError('Expected %s, got %s' %
                             (type_.tokentype, node.tokentype()),
                             node.location)
        if next_:
            self.next()
        return node

    def checksymbol(self, sym, raise_=False, next_=True):
        try:
            node = self.expect(tokenizer.CharacterToken, next_=False)
        except ParseError:
            if raise_:
                raise
            return False
        if node.val_str != sym:
            if raise_:
                raise ParseError('Expected %s, got %s' %
                                 (sym, node.val_str),
                                 node.location)
            return False
        if next_:
            self.next()
        return True

    def checkidentifier(self, ident, raise_=False, next_=True):
        try:
            node = self.expect(tokenizer.IdentifierToken, next_=False)
        except ParseError:
            if raise_:
                raise
            return False
        if node.val_str != ident:
            if raise_:
                raise ParseError('Expected %s, got %s' %
                                 (ident, node.val_str),
                                 node.location)
            return False
        if next_:
            self.next()
        return True

    def declaration(self):
        # Get symbol name
        head = self.expect(tokenizer.IdentifierToken)
        name = head.val_str

        # There is a ~. There must be.
        self.checksymbol('~', except_=True)

        # Type name
        typename = self.expect(tokenizer.IdentifierToken).val_str

        default = None
        external = False

        # Is there a default value?
        if self.checksymbol('('):
            default = self.expression()
            self.checksymbol(')', except_=True)
        # Otherwise, is it external?
        elif self.checkidentifier('extern'):
            external = True

        return DeclarationASTNode(name, typename,
                                  default, external, head.location)

    def primary(self):
        token = self.current
        if isinstance(token, tokenizer.IntToken):
            self.next()
            return IntegerASTNode(token.val_int, token.location)
        elif isinstance(token, tokenizer.FloatToken):
            self.next()
            return FloatASTNode(token.val_float, token.location)
        elif isinstance(token, tokenizer.IdentifierToken):
            self.next()
            return ReferenceASTNode(token.val_str, token.location)
        elif self.checksymbol('('):
            contents = self.expression()
            self.checksymbol(')', raise_=True)
            return contents
        raise ParseError('Expected primary expression, got %s' %
                         (token.tokentype(),),
                         token.location)

    _precedence = {
        '<': 10,
        '+': 20,
        '-': 20,
        '*': 40,
        '/': 40
    }

    def precedence(self):
        if not isinstance(self.current, tokenizer.CharacterToken):
            return -1
        return Parser._precedence.get(self.current.val_str, -1)

    def binaryrhs(self, left, left_precedence):
        while True:
            precedence = self.precedence()
            if precedence < left_precedence:
                return left

            op = self.current.val_str
            location = self.current.location

            self.next()

            right = self.primary()
            next_precedence = self.precedence()
            if precedence < next_precedence:
                right = self.binaryrhs(right, precedence + 1)

            left = BinaryOpASTNode(op, left, right, location)

    def expression(self):
        left = self.primary()
        return self.binaryrhs(left, 0)
