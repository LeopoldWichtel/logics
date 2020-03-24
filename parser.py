#!/usr/bin/python
#-*- coding: utf-8 -*-

# Parser module generated by unicc from logics.par.
# DO NOT EDIT THIS FILE MANUALLY, IT WILL GO AWAY!


class Node(object):
	"""
	This is an AST node.
	"""

	def __init__(self, emit = None, match = None, children = None):
		self.emit = emit
		self.match = match
		self.children = children or []

	def dump(self, level=0):
		if self.emit:
			txt = "%s%s" % (level * " ", self.emit)
			if self.match and self.match != self.emit:
				txt += " (%s)" % self.match

			print(txt)
			level += 1

		for child in self.children:
			if child:
				child.dump(level)


class ParseException(Exception):
	"""
	Exception to be raised on a parse error.
	"""

	def __init__(self, row, col, txt = None):
		if isinstance(txt, list):
			expecting = txt
			txt = ("Line %d, column %d: Parse error, expecting %s" %
					(row, col, ", ".join([("%r" % symbol[0])
						for symbol in txt])))
		else:
			expecting = None

		super(ParseException, self).__init__(txt)

		self.row = row
		self.col = col
		self.expecting = expecting


class ParserToken(object):
	state = 0
	line = 0
	column = 0

	node = None

	value = None


class ParserControlBlock(object):
	def __init__(self, input):

		# Stack
		self.stack = []
		self.tos = None

		# Values
		self.ret = None

		# State
		self.act = 0
		self.idx = None
		self.lhs = None

		# Lookahead
		self.sym = -1
		self.old_sym = -1
		self.len = 0

		# Lexical analysis
		self.lexem = None
		self.next = None
		self.eof = None
		self.is_eof = None

		# Input buffering
		self.input = input
		self.buf = ""

		# Error handling
		self.error_delay = 3
		self.error_count = 0

		self.line = 1
		self.column = 1

		


class Parser(object):

	# Actions
	_ERROR = 0
	_REDUCE = 1
	_SHIFT = 2
	_SUCCESS = 4

	# Parse tables
	_symbols = (
		("&eof", "", 3, 0, 0, 1),
		("False", "False", 2, 0, 0, 1),
		("True", "True", 2, 0, 0, 1),
		("**", "**", 2, 0, 0, 1),
		("!=", "!=", 2, 0, 0, 1),
		("<>", "<>", 2, 0, 0, 1),
		(">", ">", 2, 0, 0, 1),
		("<", "<", 2, 0, 0, 1),
		("<=", "<=", 2, 0, 0, 1),
		(">=", ">=", 2, 0, 0, 1),
		("==", "==", 2, 0, 0, 1),
		("IN", "", 2, 0, 0, 1),
		("NOT", "", 2, 0, 0, 1),
		("AND", "", 2, 0, 0, 1),
		("OR", "", 2, 0, 0, 1),
		("ELSE", "", 2, 0, 0, 1),
		("IF", "", 2, 0, 0, 1),
		("FOR", "", 2, 0, 0, 1),
		("NUMBER", "NUMBER", 2, 0, 0, 1),
		("STRING", "STRING", 2, 0, 0, 0),
		("IDENT", "IDENT", 2, 0, 0, 1),
		("whitespace", "", 2, 0, 1, 1),
		(",", "", 1, 0, 0, 1),
		(".", "", 1, 0, 0, 1),
		(":", "", 1, 0, 0, 1),
		("]", "", 1, 0, 0, 1),
		("[", "", 1, 0, 0, 1),
		(")", "", 1, 0, 0, 1),
		("(", "", 1, 0, 0, 1),
		("~", "", 1, 0, 0, 1),
		("%", "", 1, 0, 0, 1),
		("/", "", 1, 0, 0, 1),
		("*", "", 1, 0, 0, 1),
		("-", "", 1, 0, 0, 1),
		("+", "", 1, 0, 0, 1),
		("&embedded_5*", "", 0, 0, 0, 1),
		("&embedded_5+", "", 0, 0, 0, 1),
		("&embedded_5", "", 0, 0, 0, 1),
		("&embedded_4?", "", 0, 0, 0, 1),
		("&embedded_4", "", 0, 0, 0, 1),
		("comprehension", "", 0, 0, 0, 1),
		("STRING+", "", 0, 0, 0, 1),
		("&embedded_3", "", 0, 0, 0, 1),
		("list", "", 0, 0, 0, 1),
		("opt_expression", "", 0, 0, 0, 1),
		("trailer+", "", 0, 0, 0, 1),
		("trailer", "", 0, 0, 0, 1),
		("atom", "", 0, 0, 0, 1),
		("entity", "", 0, 0, 0, 1),
		("power", "", 0, 0, 0, 1),
		("factor", "", 0, 0, 0, 1),
		("term", "", 0, 0, 0, 1),
		("&embedded_2+", "", 0, 0, 0, 1),
		("&embedded_2", "", 0, 0, 0, 1),
		("expr", "", 0, 0, 0, 1),
		("comparison_op", "", 0, 0, 0, 1),
		("not_in", "", 0, 0, 0, 1),
		("in", "", 0, 0, 0, 1),
		("comparison", "", 0, 0, 0, 1),
		("&embedded_1+", "", 0, 0, 0, 1),
		("&embedded_1", "", 0, 0, 0, 1),
		("not_test", "", 0, 0, 0, 1),
		("&embedded_0+", "", 0, 0, 0, 1),
		("&embedded_0", "", 0, 0, 0, 1),
		("and_test", "", 0, 0, 0, 1),
		("or_test", "", 0, 0, 0, 1),
		("if_else", "", 0, 0, 0, 1),
		("test", "", 0, 0, 0, 1),
		("expression", "", 0, 0, 0, 1),
		("logic", "", 0, 0, 0, 1)
	)
	_productions = (
		("logic : expression ~&eof", "", 2, 69),
		("expression : test", "", 1, 68),
		("test : if_else", "", 1, 67),
		("test : or_test", "", 1, 67),
		("if_else : or_test @IF or_test @ELSE test", "if_else", 5, 66),
		("or_test : and_test &embedded_0+", "or_test", 2, 65),
		("&embedded_0 : @OR and_test", "", 2, 63),
		("&embedded_0+ : &embedded_0+ &embedded_0", "", 2, 62),
		("&embedded_0+ : &embedded_0", "", 1, 62),
		("or_test : and_test", "", 1, 65),
		("and_test : not_test &embedded_1+", "and_test", 2, 64),
		("&embedded_1 : @AND not_test", "", 2, 60),
		("&embedded_1+ : &embedded_1+ &embedded_1", "", 2, 59),
		("&embedded_1+ : &embedded_1", "", 1, 59),
		("and_test : not_test", "", 1, 64),
		("not_test : @NOT not_test", "not_test", 2, 61),
		("not_test : comparison", "", 1, 61),
		("in : @IN", "in", 1, 57),
		("not_in : @NOT @IN", "not_in", 2, 56),
		("comparison_op : \"==\"", "", 1, 55),
		("comparison_op : \">=\"", "", 1, 55),
		("comparison_op : \"<=\"", "", 1, 55),
		("comparison_op : \"<\"", "", 1, 55),
		("comparison_op : \">\"", "", 1, 55),
		("comparison_op : \"<>\"", "", 1, 55),
		("comparison_op : \"!=\"", "", 1, 55),
		("comparison_op : in", "", 1, 55),
		("comparison_op : not_in", "", 1, 55),
		("comparison : expr &embedded_2+", "comparison", 2, 58),
		("&embedded_2 : comparison_op expr", "", 2, 53),
		("&embedded_2+ : &embedded_2+ &embedded_2", "", 2, 52),
		("&embedded_2+ : &embedded_2", "", 1, 52),
		("comparison : expr", "", 1, 58),
		("expr : expr '+' term", "add", 3, 54),
		("expr : expr '-' term", "sub", 3, 54),
		("expr : term", "", 1, 54),
		("term : term '*' factor", "mul", 3, 51),
		("term : term '/' factor", "div", 3, 51),
		("term : term '%' factor", "mod", 3, 51),
		("term : factor", "", 1, 51),
		("factor : '+' factor", "plus", 2, 50),
		("factor : '-' factor", "minus", 2, 50),
		("factor : '~' factor", "complement", 2, 50),
		("factor : power", "", 1, 50),
		("power : entity \"**\" factor", "power", 3, 49),
		("power : entity", "", 1, 49),
		("entity : atom trailer+", "entity", 2, 48),
		("trailer+ : trailer+ trailer", "", 2, 45),
		("trailer+ : trailer", "", 1, 45),
		("entity : atom", "", 1, 48),
		("opt_expression : expression", "", 1, 44),
		("opt_expression : ", "null", 0, 44),
		("trailer : '(' list ')'", "", 3, 46),
		("trailer : '[' expression ']'", "", 3, 46),
		("trailer : '[' opt_expression ':' opt_expression ']'", "slice", 5, 46),
		("trailer : '.' @IDENT", "", 2, 46),
		("&embedded_3 : \"True\"", "", 1, 42),
		("&embedded_3 : \"False\"", "", 1, 42),
		("atom : &embedded_3", "", 1, 47),
		("atom : @NUMBER", "", 1, 47),
		("atom : @IDENT", "", 1, 47),
		("atom : @STRING", "", 1, 47),
		("STRING+ : STRING+ @STRING", "", 2, 41),
		("STRING+ : @STRING", "", 1, 41),
		("atom : STRING+", "concat", 1, 47),
		("atom : comprehension", "", 1, 47),
		("atom : '[' list ']'", "", 3, 47),
		("atom : '(' expression ')'", "atom", 3, 47),
		("comprehension : '[' expression @FOR @IDENT @IN or_test &embedded_4? ']'", "comprehension", 8, 40),
		("&embedded_4 : @IF expression", "", 2, 39),
		("&embedded_4? : &embedded_4", "", 1, 38),
		("&embedded_4? : ", "", 0, 38),
		("list : expression &embedded_5*", "list", 2, 43),
		("&embedded_5 : ',' expression", "", 2, 37),
		("&embedded_5+ : &embedded_5+ &embedded_5", "", 2, 36),
		("&embedded_5+ : &embedded_5", "", 1, 36),
		("&embedded_5* : &embedded_5+", "", 1, 35),
		("&embedded_5* : ", "", 0, 35),
		("list : ", "list", 0, 43)
	)
	_act = (
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((19, 1, 63), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((0, 3, 0), ),
		((16, 2, 17), ),
		((14, 2, 18), ),
		((13, 2, 20), ),
		((12, 2, 22), (11, 3, 17), (10, 3, 19), (9, 3, 20), (8, 3, 21), (7, 3, 22), (6, 3, 23), (5, 3, 24), (4, 3, 25), (34, 2, 25), (33, 2, 26), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((32, 2, 27), (31, 2, 28), (30, 2, 29), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((3, 2, 30), ),
		((28, 2, 32), (26, 2, 33), (23, 2, 34), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((19, 3, 62), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((14, 2, 18), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((13, 2, 20), ),
		((11, 3, 18), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((12, 2, 22), (11, 3, 17), (10, 3, 19), (9, 3, 20), (8, 3, 21), (7, 3, 22), (6, 3, 23), (5, 3, 24), (4, 3, 25), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((28, 2, 32), (26, 2, 33), (23, 2, 34), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((20, 3, 55), ),
		((27, 3, 67), ),
		((17, 2, 46), (22, 2, 47), ),
		((25, 3, 66), ),
		((15, 2, 49), ),
		((34, 2, 25), (33, 2, 26), ),
		((32, 2, 27), (31, 2, 28), (30, 2, 29), ),
		((32, 2, 27), (31, 2, 28), (30, 2, 29), ),
		((22, 2, 47), ),
		((27, 3, 52), ),
		((25, 3, 53), ),
		((24, 2, 50), ),
		((20, 2, 51), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((22, 2, 47), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((11, 2, 53), ),
		((25, 3, 54), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((16, 2, 55), ),
		((20, 3, 60), (19, 2, 1), (18, 3, 59), (12, 2, 2), (34, 2, 8), (33, 2, 10), (29, 2, 11), (28, 2, 14), (26, 2, 15), (2, 3, 56), (1, 3, 57), ),
		((25, 3, 68), )
	)
	_go = (
		((68, 2, 3), (67, 3, 1), (66, 3, 2), (65, 2, 4), (64, 2, 5), (61, 2, 6), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		(),
		((61, 3, 15), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		(),
		(),
		((63, 3, 8), (62, 2, 19), ),
		((60, 3, 13), (59, 2, 21), ),
		((57, 3, 26), (56, 3, 27), (55, 2, 23), (53, 3, 31), (52, 2, 24), ),
		((50, 3, 40), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		(),
		((50, 3, 41), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((50, 3, 42), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		(),
		((46, 3, 48), (45, 2, 31), ),
		((68, 2, 35), (67, 3, 1), (66, 3, 2), (65, 2, 4), (64, 2, 5), (61, 2, 6), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((68, 2, 36), (67, 3, 1), (66, 3, 2), (65, 2, 4), (64, 2, 5), (61, 2, 6), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (43, 2, 37), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		(),
		((65, 2, 38), (64, 2, 5), (61, 2, 6), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((64, 3, 6), (61, 2, 6), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((63, 3, 7), ),
		((61, 3, 11), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((60, 3, 12), ),
		(),
		((54, 2, 39), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((57, 3, 26), (56, 3, 27), (55, 2, 23), (53, 3, 30), ),
		((51, 2, 40), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((51, 2, 41), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((50, 3, 36), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((50, 3, 37), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((50, 3, 38), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((50, 3, 44), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((46, 3, 47), ),
		((68, 2, 42), (67, 3, 1), (66, 3, 2), (65, 2, 4), (64, 2, 5), (61, 2, 6), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (43, 2, 43), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((68, 2, 44), (67, 3, 1), (66, 3, 2), (65, 2, 4), (64, 2, 5), (61, 2, 6), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (44, 2, 45), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		(),
		(),
		((37, 3, 75), (36, 2, 48), (35, 3, 72), ),
		(),
		(),
		(),
		(),
		(),
		((37, 3, 75), (36, 2, 48), (35, 3, 72), ),
		(),
		(),
		(),
		(),
		((68, 3, 73), (67, 3, 1), (66, 3, 2), (65, 2, 4), (64, 2, 5), (61, 2, 6), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((37, 3, 74), ),
		((67, 3, 4), (66, 3, 2), (65, 2, 4), (64, 2, 5), (61, 2, 6), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((68, 3, 50), (67, 3, 1), (66, 3, 2), (65, 2, 4), (64, 2, 5), (61, 2, 6), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (44, 2, 52), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		(),
		(),
		((65, 2, 54), (64, 2, 5), (61, 2, 6), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		((39, 3, 70), (38, 2, 56), ),
		((68, 3, 69), (67, 3, 1), (66, 3, 2), (65, 2, 4), (64, 2, 5), (61, 2, 6), (58, 3, 16), (54, 2, 7), (51, 2, 9), (50, 3, 39), (49, 3, 43), (48, 2, 12), (47, 2, 13), (42, 3, 58), (41, 2, 16), (40, 3, 65), ),
		()
	)

	_def_prod = (-1, 61, -1, -1, 3, 9, 14, 32, -1, 35, -1, -1, 45, 49, -1, 78, 64, -1, -1, 5, -1, 10, -1, -1, 28, -1, -1, -1, -1, -1, -1, 46, 78, 51, -1, -1, 77, -1, -1, 29, 33, 34, 77, -1, 50, -1, -1, -1, 76, -1, 51, -1, -1, -1, 71, -1, -1)

	# Lexical analysis
	_dfa_select = ()
	_dfa_index = (
		(0, 41, 48, 49, 50, 51, 55, 57, 60, 61, 64, 65, 67, 68, 69, 70, 72, 73, 74, 75, 80, 85, 90, 91, 92, 93, 94, 95, 96, 97, 102, 107, 112, 117, 122, 127, 129, 138, 139, 141, 147, 153, 160, 166, 170, 177, 183, 190, 192, 199, 205, 212, 216, 221, 227, 233, 240, 247, 254, 261, 268, 275, 282, 289, 296),
	)
	_dfa_chars = ((110, 110), (111, 111), (126, 126), (9, 10), (13, 13), (32, 32), (65, 69), (71, 83), (85, 90), (95, 95), (98, 100), (103, 104), (106, 109), (112, 122), (105, 105), (102, 102), (101, 101), (97, 97), (93, 93), (91, 91), (84, 84), (70, 70), (62, 62), (61, 61), (60, 60), (58, 58), (48, 57), (47, 47), (46, 46), (45, 45), (44, 44), (43, 43), (42, 42), (41, 41), (40, 40), (39, 39), (37, 37), (35, 35), (34, 34), (33, 33), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 113), (115, 122), (114, 114), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (9, 10), (13, 13), (32, 32), (-1, -1), (61, 61), (-1, -1), (62, 62), (61, 61), (-1, -1), (-1, -1), (48, 57), (46, 46), (-1, -1), (-1, -1), (48, 57), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (42, 42), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (61, 61), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 101), (103, 109), (111, 122), (110, 110), (102, 102), (-1, -1), (-1, -1), (48, 57), (-1, -1), (92, 92), (39, 39), (0, 38), (40, 91), (93, 65535), (-1, -1), (92, 92), (39, 39), (0, 38), (40, 91), (93, 65535), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 110), (112, 122), (111, 111), (-1, -1), (92, 92), (34, 34), (0, 33), (35, 91), (93, 65535), (-1, -1), (10, 10), (0, 9), (11, 65535), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 109), (111, 122), (110, 110), (-1, -1), (92, 92), (34, 34), (0, 33), (35, 91), (93, 65535), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 113), (115, 122), (114, 114), (-1, -1), (61, 61), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 107), (109, 122), (108, 108), (-1, -1), (0, 38), (40, 91), (93, 65535), (92, 92), (39, 39), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 110), (112, 122), (111, 111), (-1, -1), (0, 9), (11, 65535), (10, 10), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (0, 33), (35, 91), (93, 65535), (92, 92), (34, 34), (-1, -1), (48, 57), (65, 90), (95, 95), (98, 122), (97, 97), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 116), (118, 122), (117, 117), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 115), (117, 122), (116, 116), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 99), (101, 122), (100, 100), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 114), (116, 122), (115, 115), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 100), (102, 122), (101, 101), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 100), (102, 122), (101, 101), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 100), (102, 122), (101, 101), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 113), (115, 122), (114, 114), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 114), (116, 122), (115, 115), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 107), (109, 122), (108, 108), (-1, -1))
	_dfa_trans = (41, 46, 4, 5, 5, 5, 52, 52, 52, 52, 52, 52, 52, 52, 36, 50, 48, 44, 2, 3, 1, 54, 6, 35, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 40, 18, 43, 45, 47, -1, 52, 52, 52, 52, 52, 55, -1, -1, -1, -1, 5, 5, 5, -1, 22, -1, 24, 25, -1, -1, 9, 38, -1, -1, 38, -1, -1, -1, -1, 26, -1, -1, -1, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, -1, -1, -1, -1, -1, -1, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 23, -1, 52, 52, 52, 52, 52, 52, 19, 20, -1, -1, 38, -1, 49, 27, 40, 40, 40, -1, 49, 27, 40, 40, 40, -1, 52, 52, 52, 52, 52, 56, -1, 53, 27, 45, 45, 45, -1, 37, 51, 51, -1, 52, 52, 52, 52, 52, 57, -1, 53, 27, 45, 45, 45, -1, 52, 52, 52, 52, 52, 21, -1, 28, -1, 52, 52, 52, 52, 52, 58, -1, 40, 40, 40, 49, 39, -1, 52, 52, 52, 52, 52, 62, -1, 51, 51, 37, -1, 52, 52, 52, 52, -1, 45, 45, 45, 53, 42, -1, 52, 52, 52, 52, 64, -1, 52, 52, 52, 52, 52, 59, -1, 52, 52, 52, 52, 52, 29, -1, 52, 52, 52, 52, 52, 30, -1, 52, 52, 52, 52, 52, 60, -1, 52, 52, 52, 52, 52, 32, -1, 52, 52, 52, 52, 52, 33, -1, 52, 52, 52, 52, 52, 34, -1, 52, 52, 52, 52, 52, 31, -1, 52, 52, 52, 52, 52, 61, -1, 52, 52, 52, 52, 52, 63, -1)
	_dfa_accept = (
		(0, 21, 26, 27, 30, 22, 7, 8, 25, 19, 32, 24, 34, 23, 35, 33, 28, 29, 31, 12, 17, 15, 10, 11, 6, 9, 4, 20, 5, 13, 14, 18, 3, 16, 2, 0, 21, 22, 19, 20, 0, 21, 20, 0, 21, 0, 21, 0, 21, 0, 21, 0, 21, 0, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21),
	)

	# Parsing actions



	# Parsing algorithm

	def _get_act(self, pcb):
		# Get action table entry

		# Check action table first
		for (sym, pcb.act, pcb.idx) in self._act[pcb.tos.state]:
			if sym == pcb.sym:
				return True if pcb.act else False #enforced parse error

		# Otherwise, apply default production
		pcb.idx = self._def_prod[pcb.tos.state]
		if pcb.idx > -1:
			pcb.act = self._REDUCE
			return True

		return False

	def _get_go(self, pcb):
		# Get goto table entry

		for (sym, pcb.act, pcb.idx) in self._go[pcb.tos.state]:
			if sym == pcb.lhs:
				return True

		return False

	def _get_char(self, pcb):
		# Get next character from input stream

		if callable(pcb.input):
			return pcb.input()

		if pcb.input:
			ch = pcb.input[0]
			pcb.input = pcb.input[1:]
		else:
			ch = pcb.eof

		return ch

	def _get_input(self, pcb, offset):
		# Performs input buffering

		while offset >= len(pcb.buf):
			if pcb.is_eof:
				return pcb.eof

			ch = self._get_char(pcb)
			if ch == pcb.eof:
				pcb.is_eof = True
				return pcb.eof

			pcb.buf += ch

		#print("_get_input", pcb.buf, offset, pcb.buf[offset], ord(pcb.buf[offset]))

		return ord(pcb.buf[offset])

	def _clear_input(self, pcb):
		# Purge input from buffer that is not necessary anymore

		if pcb.buf:

			# Perform position counting.
			for ch in pcb.buf[0: pcb.len]:
				if ch == '\n':
					pcb.line += 1
					pcb.column = 0
				else:
					pcb.column += 1

			pcb.buf = pcb.buf[pcb.len:]

		pcb.len = 0
		pcb.sym = -1

	def _lex(self, pcb):
		# Lexical analysis

		state = length = 0
		machine = self._dfa_select[pcb.tos.state] if not 1 else 0
		next = self._get_input(pcb, length)

		if next == pcb.eof:
			pcb.sym = 0
			return

		while state > -1 and next != pcb.eof:
			idx = self._dfa_index[machine][state]
			state = -1

			while self._dfa_chars[idx][0] > -1:
				if (next >= self._dfa_chars[idx][0]
					and next <= self._dfa_chars[idx][1]):

					length += 1
					state = self._dfa_trans[idx]

					if self._dfa_accept[machine][state] > 0:
						pcb.sym = self._dfa_accept[machine][state] - 1
						pcb.len = length

						# Test! (??)
						if pcb.sym == 0:
							state = -1
							break

						# Stop if matched symbol should be parsed nongreedy
						if not self._symbols[pcb.sym][5]:
							state = -1
							break

					next = self._get_input(pcb, length)
					break

				idx += 1

			# TODO: Semantic Terminal Selection?

		#print("_lex", pcb.sym, pcb.len)

	def _get_sym(self, pcb):
		# Get lookahead symbol

		pcb.sym = -1
		pcb.len = 0

		# insensitive mode
		if 1:
			while True:
				self._lex(pcb)

				# check for whitespace
				if pcb.sym > -1 and self._symbols[pcb.sym][4]:
					self._clear_input(pcb)
					continue

				break

		# sensitive mode
		else:
			if self._dfa_select[pcb.tos.state] > -1:
				self._lex(pcb)

			# If there is no matching DFA state machine, try to identify the
			# end-of-file symbol. If this also fails, a parse error will raise.
			elif self._get_input(pcb, 0) == pcb.eof:
				pcb.sym = 0

		return pcb.sym > -1

	def parse(self, s = None):
		if s is None:
			try:
				s = raw_input(">")
			except NameError:
				s = input(">")

		pcb = ParserControlBlock(s)
		pcb.act = self._SHIFT

		pcb.tos = ParserToken()
		pcb.stack.append(pcb.tos)

		while True:
			#print("state = %d" % pcb.tos.state)

			# Reduce
			while pcb.act & self._REDUCE:

				# Set default left-hand side
				pcb.lhs = self._productions[pcb.idx][3]

				#print("REDUCE", pcb.idx, self._productions[pcb.idx][0])
				#print("state", pcb.tos.state)

				# Call reduce function
				#print("CALL", "_reduce_action_%d" % pcb.idx)
				reduce_fn = getattr(self, "_reduce_action_%d" % pcb.idx, None)
				if reduce_fn:
					reduce_fn(pcb)

				# Drop right-hand side
				cnodes = None
				for _ in range(0, self._productions[pcb.idx][2]):
					item = pcb.stack.pop()

					if item.node:
						if cnodes is None:
							cnodes = []

						if isinstance(item.node, list):
							cnodes = item.node + cnodes
						else:
							cnodes.insert(0, item.node)

				pcb.tos = pcb.stack[-1]
				pcb.tos.value = pcb.ret

				# Handle AST nodes
				if self._productions[pcb.idx][1]:
					#print("%s = %s" % (self._productions[pcb.idx][0], self._productions[pcb.idx][1]))
					node = Node(self._productions[pcb.idx][1],
											children=cnodes)

				else:
					node = None

				# Error enforced by semantics?
				if pcb.act == self._ERROR:
					break

				# Goal symbol reduced, and stack is empty?
				if pcb.lhs == 69 and len(pcb.stack) == 1:
					pcb.tos.node = node or cnodes
					self._clear_input(pcb)
					pcb.act = self._SUCCESS;
					break

				self._get_go(pcb)

				pcb.tos = ParserToken()
				pcb.stack.append(pcb.tos)

				pcb.tos.symbol = self._symbols[pcb.lhs]
				pcb.tos.state = -1 if pcb.act & self._REDUCE else pcb.idx
				pcb.tos.value = pcb.ret
				pcb.tos.node = node or cnodes
				pcb.tos.line = pcb.line
				pcb.tos.column = pcb.column

			if pcb.act == self._SUCCESS or pcb.act == self._ERROR:
				break

			# Get next input symbol
			self._get_sym(pcb)

			#print("pcb.sym = %d (%s)" % (pcb.sym, self._symbols[pcb.sym][0]))
			#print("pcb.len = %d" % pcb.len)

			# Get action table entry
			if not self._get_act(pcb):
				# TODO: Error Recovery
				raise ParseException(pcb.line, pcb.column,
					[self._symbols[sym]
						for (sym, pcb.act, pcb.idx)
							in self._act[pcb.tos.state]])

			#print("pcb.act = %d" % pcb.act)

			# Shift
			if pcb.act & self._SHIFT:
				#print("SHIFT", pcb.sym, self._symbols[pcb.sym])

				pcb.tos = ParserToken()
				pcb.stack.append(pcb.tos)

				# Execute scanner actions, if existing.
				scan_fn = getattr(self, "_scan_action_%d" % pcb.sym, None)
				if scan_fn:
					scan_fn(pcb)

				pcb.tos.state = -1 if pcb.act & self._REDUCE else pcb.idx
				pcb.tos.symbol = self._symbols[pcb.sym]

				pcb.tos.line = pcb.line
				pcb.tos.column = pcb.column
				pcb.stack[-1 - 0].value = pcb.buf[:pcb.len]

				if pcb.tos.symbol[1]:
					pcb.tos.node = Node(pcb.tos.symbol[1], pcb.stack[-1 - 0].value)

				if pcb.sym != 0 and pcb.sym != -1:
					self._clear_input(pcb)
					pcb.old_sym = -1

		if pcb.ret is None and pcb.tos.node:
			if isinstance(pcb.tos.node, list):
				if len(pcb.tos.node) > 1:
					node = Node(children=pcb.tos.node)
				else:
					node = pcb.tos.node[0]
			else:
				node = pcb.tos.node
		else:
			node = None

		return pcb.ret or node



if __name__ == "__main__":
	import sys

	p = Parser()
	ret = p.parse(sys.argv[1] if len(sys.argv) > 1 else None)

	if isinstance(ret, Node):
		ret.dump()
	else:
		print(ret)

