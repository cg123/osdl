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


class ASTNode(object):
    def __init__(self, source=None):
        self.source = source


class IntegerASTNode(ASTNode):
    def __init__(self, value, source=None):
        self.source = source
        self.val_int = value


class FloatASTNode(ASTNode):
    def __init__(self, value, source=None):
        self.source = source
        self.val_float = value


class ReferenceASTNode(ASTNode):
    def __init__(self, name, source=None):
        self.source = source
        self.name = name


class BinaryOpASTNode(ASTNode):
    def __init__(self, op, lh, rh, source=None):
        self.source = source
        self.operator = op
        self.lh = lh
        self.rh = rh


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

    def parse(self):
        if isinstance(self.current, tokenizer.IntToken):
            res = IntegerASTNode(self.current.val_int, self.current.location)
            self.next()
            return res
        elif isinstance(self.current, tokenizer.FloatToken):
            res = FloatASTNode(self.current.val_float, self.current.location)
            self.next()
            return res
        raise NotImplementedError("welp (%r)" % self.current)
