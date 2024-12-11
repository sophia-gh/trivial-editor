from tokenizer import tokenize
from pprint import pprint

# NOTE - ADD simple-expression = ... "(" expression ")"

grammar = """

    simple_expression = identifier | <boolean> | <number> | <string> | list_literal | object_literal | ("-" simple_expression) | ("!" simple_expression) | function_literal | ( "(" expression ")" ) ;

    list_literal = "[" expression { "," expression } "]" ;
    object_literal = "{" [ expression ":" expression { "," expression ":" expression } ] "}" ;
    function_literal = "function" "(" [ identifier { "," identifier } ] ")" statement_list ;

    complex_expression = simple_expression { ("[" expression "]") | ("." identifier) | "(" [ expression { "," expression } ] ")" } ;

    arithmetic_factor = complex_expression ;
    arithmetic_term = arithmetic_factor { ("*" | "/") arithmetic_factor } ;
    arithmetic_expression = arithmetic_term { ("+" | "-") arithmetic_term } ;
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression } ;
    logical_factor = relational_expression ;
    logical_term = logical_factor { "&&" logical_factor } ;
    logical_expression = logical_term { "||" logical_term } ;

    expression = logical_expression ;

    assignment_statement = expression [ "=" expression ] ;
    return_statement = "return" [ expression ] ;
    print_statement = "print" [ expression ] ;
    function_statement = "function" identifier "(" [ identifier { "," identifier } ] ")" statement_list ;

    if_statement = "if" "(" expression ")" statement_list [ "else" (if_statement | statement_list) ] ;
    while_statement = "while" "(" expression ")" statement_list ;
    statement_list = "{" statement { ";" statement } "}" ;

    statement = if_statement | while_statement | function_statement | return_statement | print_statement | assignment_statement ;

    program = [ statement { ";" statement } ] ;
    """

# BASIC EXPRESSIONS


def parse_simple_expression(tokens):
    """
    simple_expression = identifier | <boolean> | <number> | <string> | list_literal | object_literal | ("-" simple_expression) | ("!" simple_expression) | function_literal | ( "(" expression ")" ) ;
    """

    token = tokens[0]

    if token["tag"] in {"identifier", "boolean", "number", "string"}:
        return {"tag": token["tag"], "value": token["value"]}, tokens[1:]

    if token["tag"] == "[":
        return parse_list_literal(tokens)

    if token["tag"] == "{":
        return parse_object_literal(tokens)

    if token["tag"] == "-":
        value, tokens = parse_simple_expression(tokens[1:])
        return {"tag": "negate", "value": value}, tokens

    if token["tag"] == "!":
        value, tokens = parse_simple_expression(tokens[1:])
        return {"tag": "not", "value": value}, tokens

    if token["tag"] == "function":
        return parse_function_literal(tokens)

    if token["tag"] == "(":
        ast, tokens = parse_expression(tokens[1:])
        assert (
            tokens[0]["tag"] == ")"
        ), f"Expected ')' at position {tokens[0]['position']}"
        return ast, tokens[1:]

    assert False, f"Unexpected token '{token['tag']}' at position {token['position']}"


def test_parse_simple_expression():
    """
    simple_expression = identifier | <boolean> | <number> | <string> | list_literal | object_literal | ("-" simple_expression) | ("!" simple_expression) | function_literal | ( "(" expression ")" ) ;
    """
    print("testing parse_simple_expression...")

    node, remaining_tokens = parse_simple_expression(tokenize("x"))
    assert node["tag"] == "identifier"
    assert node["value"] == "x", f"Expected 'x', got {result}"
    assert remaining_tokens[0]["tag"] is None, "Expected end of tokens"

    for n in [1, 12, 1.3, 1.23]:
        node, remaining_tokens = parse_simple_expression(tokenize(str(n)))
        assert node["tag"] == "number"
        assert node["value"] == n, f"Expected {n}, got {result}"
        assert remaining_tokens[0]["tag"] is None, "Expected end of tokens"

    for s in ['""', '"hello"']:
        node, remaining_tokens = parse_simple_expression(tokenize(s))
        assert node["tag"] == "string"
        assert node["value"] == s.replace('"', ""), f"Expected {s}, got {result}"
        assert remaining_tokens[0]["tag"] is None, "Expected end of tokens"

    for s in ["[1,2,3]", "[]"]:
        t = tokenize(s)
        assert parse_simple_expression(t) == parse_list_literal(t)

    for s in ['{"a":4,"b":"x"}', "{}"]:
        t = tokenize(s)
        assert parse_simple_expression(t) == parse_object_literal(t)

    ast, tokens = parse_simple_expression(tokenize("-1"))
    assert ast == {"tag": "negate", "value": {"tag": "number", "value": 1}}

    ast, tokens = parse_simple_expression(tokenize("--2"))
    assert ast == {
        "tag": "negate",
        "value": {"tag": "negate", "value": {"tag": "number", "value": 2}},
    }

    ast, tokens = parse_simple_expression(tokenize("!1"))
    assert ast == {"tag": "not", "value": {"tag": "number", "value": 1}}

    ast, tokens = parse_simple_expression(tokenize("!!2"))
    assert ast == {
        "tag": "not",
        "value": {"tag": "not", "value": {"tag": "number", "value": 2}},
    }

    ast, tokens = parse_simple_expression(tokenize("(1+2)"))
    assert ast == {
        "tag": "+",
        "left": {"tag": "number", "value": 1},
        "right": {"tag": "number", "value": 2},
    }
    ast, tokens = parse_simple_expression(tokenize("(1+(2*3))"))
    assert ast == {
        "tag": "+",
        "left": {"tag": "number", "value": 1},
        "right": {
            "tag": "*",
            "left": {"tag": "number", "value": 2},
            "right": {"tag": "number", "value": 3},
        },
    }


def parse_list_literal(tokens):
    """
    list_literal = "[" expression { "," expression } "]" ;
    """
    assert tokens[0]["tag"] == "[", f"Expected '[' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    items = []
    if tokens[0]["tag"] != "]":
        value, tokens = parse_simple_expression(tokens)
        items.append(value)
        while tokens[0]["tag"] == ",":
            value, tokens = parse_simple_expression(tokens[1:])
            items.append(value)
    assert tokens[0]["tag"] == "]", f"Expected ']' at position {tokens[0]['position']}"
    return {"tag": "list", "items": items}, tokens[1:]


def test_parse_list_literal():
    """
    list_literal = "[" expression { "," expression } "]" ;
    """
    print("testing parse_list_literal...")
    ast, tokens = parse_list_literal(tokenize("[1,2,3]"))
    assert ast == {
        "tag": "list",
        "items": [
            {"tag": "number", "value": 1},
            {"tag": "number", "value": 2},
            {"tag": "number", "value": 3},
        ],
    }
    ast, tokens = parse_list_literal(tokenize("[1,2,3,[4,5]]"))
    assert ast == {
        "tag": "list",
        "items": [
            {"tag": "number", "value": 1},
            {"tag": "number", "value": 2},
            {"tag": "number", "value": 3},
            {
                "tag": "list",
                "items": [{"tag": "number", "value": 4}, {"tag": "number", "value": 5}],
            },
        ],
    }

    ast, tokens = parse_list_literal(tokenize("[]"))
    assert ast == {"items": [], "tag": "list"}


def parse_object_literal(tokens):
    """
    object_literal = "{" [ expression ":" expression { "," expression ":" expression } ] "}" ;
    """
    assert tokens[0]["tag"] == "{", f"Expected '{{' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    items = []
    if tokens[0]["tag"] != "}":
        key, tokens = parse_simple_expression(tokens)
        assert (
            tokens[0]["tag"] == ":"
        ), f"Expected ':' at position {tokens[0]['position']}"
        tokens = tokens[1:]
        value, tokens = parse_simple_expression(tokens)
        items.append({"key": key, "value": value})
        while tokens[0]["tag"] == ",":
            tokens = tokens[1:]
            key, tokens = parse_simple_expression(tokens)
            assert (
                tokens[0]["tag"] == ":"
            ), f"Expected ':' at position {tokens[0]['position']}"
            tokens = tokens[1:]
            value, tokens = parse_simple_expression(tokens)
            items.append({"key": key, "value": value})
    assert tokens[0]["tag"] == "}", f"Expected '}}' at position {tokens[0]['position']}"
    return {"tag": "object", "items": items}, tokens[1:]


def test_parse_object_literal():
    """
    object_literal = "{" [ expression ":" expression { "," expression ":" expression } ] "}" ;
    """
    print("testing parse_object_literal...")
    ast, tokens = parse_object_literal(tokenize('{"a":4,"b":"x"}'))
    assert ast == {
        "tag": "object",
        "items": [
            {
                "key": {"tag": "string", "value": "a"},
                "value": {"tag": "number", "value": 4},
            },
            {
                "key": {"tag": "string", "value": "b"},
                "value": {"tag": "string", "value": "x"},
            },
        ],
    }
    ast, tokens = parse_object_literal(tokenize('{"a":4,"b":{"c":"d"},"e":[3,4]}'))
    assert ast == {
        "tag": "object",
        "items": [
            {
                "key": {"tag": "string", "value": "a"},
                "value": {"tag": "number", "value": 4},
            },
            {
                "key": {"tag": "string", "value": "b"},
                "value": {
                    "tag": "object",
                    "items": [
                        {
                            "key": {"tag": "string", "value": "c"},
                            "value": {"tag": "string", "value": "d"},
                        }
                    ],
                },
            },
            {
                "key": {"tag": "string", "value": "e"},
                "value": {
                    "tag": "list",
                    "items": [
                        {"tag": "number", "value": 3},
                        {"tag": "number", "value": 4},
                    ],
                },
            },
        ],
    }

    ast, tokens = parse_object_literal(tokenize("{}"))
    assert ast == {"tag": "object", "items": []}


def parse_function_literal(tokens):
    """
    function_literal = "function" "(" [ identifier { "," identifier } ] ")" statement_list ;
    """
    assert (
        tokens[0]["tag"] == "function"
    ), f"Expected 'function' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "(", f"Expected '(' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    parameters = []
    if tokens[0]["tag"] != ")":
        assert (
            tokens[0]["tag"] == "identifier"
        ), f"Expected identifier at position {tokens[0]['position']}"
        parameters.append(tokens[0])
        tokens = tokens[1:]
        while tokens[0]["tag"] == ",":
            tokens = tokens[1:]
            assert (
                tokens[0]["tag"] == "identifier"
            ), f"Expected identifier at position {tokens[0]['position']}"
            parameters.append(tokens[0])
            tokens = tokens[1:]
    assert tokens[0]["tag"] == ")", f"Expected ']' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    body_statement_list, tokens = parse_statement_list(tokens)
    return {
        "tag": "function",
        "parameters": parameters,
        "body": body_statement_list,
    }, tokens


def test_parse_function_literal():
    """
    function_literal = "function" "(" [ identifier { "," identifier } ] ")" statement_list ;
    """
    print("testing parse_function_literal...")
    ast, tokens = parse_function_literal(tokenize("function(x,y){}"))
    assert ast == {
        "tag": "function",
        "parameters": [
            {"tag": "identifier", "value": "x", "position": 9},
            {"tag": "identifier", "value": "y", "position": 11},
        ],
        "body": {"tag": "statement_list", "statements": []},
    }
    ast, tokens = parse_function_literal(tokenize("function(x,y){return x+y}"))
    assert ast == {
        "tag": "function",
        "parameters": [
            {"tag": "identifier", "value": "x", "position": 9},
            {"tag": "identifier", "value": "y", "position": 11},
        ],
        "body": {
            "tag": "statement_list",
            "statements": [
                {
                    "tag": "return",
                    "value": {
                        "tag": "+",
                        "left": {"tag": "identifier", "value": "x"},
                        "right": {"tag": "identifier", "value": "y"},
                    },
                }
            ],
        },
    }
    code = """
        x = 3; 
        function g(q)
            {return 2};
        g(4)
        """
    ast = parse(tokenize(code))
    print(ast)
    assert ast == {
        "tag": "program",
        "statements": [
            {
                "tag": "assign",
                "target": {"tag": "identifier", "value": "x"},
                "value": {"tag": "number", "value": 3},
            },
            {
                "tag": "assign",
                "target": {"tag": "identifier", "value": "g"},
                "value": {
                    "tag": "function",
                    "parameters": [{"tag": "identifier", "value": "q", "position": 36}],
                    "body": {
                        "tag": "statement_list",
                        "statements": [
                            {"tag": "return", "value": {"tag": "number", "value": 2}}
                        ],
                    },
                },
            },
            {
                "tag": "call",
                "function": {"tag": "identifier", "value": "g"},
                "arguments": [{"tag": "number", "value": 4}],
            },
        ],
    }

def parse_complex_expression(tokens):
    """
    complex_expression = simple_expression { ( ) | ("." identifier) | "(" [ expression { "," expression } ] ")" } ;
    """
    ast, tokens = parse_simple_expression(tokens)
    while tokens[0]["tag"] in ["[", ".", "("]:
        if tokens[0]["tag"] == "[":
            tokens = tokens[1:]
            index_ast, tokens = parse_expression(tokens)
            assert (
                tokens[0]["tag"] == "]"
            ), f"Expected ']' at position {tokens[0]['position']}"
            tokens = tokens[1:]
            ast = {"tag": "complex", "base": ast, "index": index_ast}
        if tokens[0]["tag"] == ".":
            tokens = tokens[1:]
            assert (
                tokens[0]["tag"] == "identifier"
            ), f"Expected identifier at position {tokens[0]['position']}"
            ast = {
                "tag": "complex",
                "base": ast,
                "index": {"tag": "string", "value": tokens[0]["value"]},
            }
        if tokens[0]["tag"] == "(":
            tokens = tokens[1:]
            items = []
            if tokens[0]["tag"] != ")":
                value, tokens = parse_expression(tokens)
                items.append(value)
                while tokens[0]["tag"] == ",":
                    value, tokens = parse_simple_expression(tokens[1:])
                    items.append(value)
            assert (
                tokens[0]["tag"] == ")"
            ), f"Expected ')' at position {tokens[0]['position']}"
            tokens = tokens[1:]
            ast = {"tag": "call", "function": ast, "arguments": items}
    return ast, tokens


def test_parse_complex_expression():
    """
    complex_expression = simple_expression { ("[" expression "]") | ("." identifier) | "(" [ expression { "," expression } ] ")" } ;
    """
    print("testing parse_complex_expression...")
    for s in ["x", '{"a":4,"b":"x"}', "{}"]:
        t = tokenize(s)
        assert parse_complex_expression(t) == parse_simple_expression(t)
    ast, tokens = parse_complex_expression(tokenize("x[3]"))
    assert ast == {
        "tag": "complex",
        "base": {"tag": "identifier", "value": "x"},
        "index": {"tag": "number", "value": 3},
    }
    ast, tokens = parse_complex_expression(tokenize('x["x"]'))
    assert ast == {
        "tag": "complex",
        "base": {"tag": "identifier", "value": "x"},
        "index": {"tag": "string", "value": "x"},
    }
    ast, tokens = parse_complex_expression(tokenize('x["x"][3]'))
    assert ast == {
        "tag": "complex",
        "base": {
            "tag": "complex",
            "base": {"tag": "identifier", "value": "x"},
            "index": {"tag": "string", "value": "x"},
        },
        "index": {"tag": "number", "value": 3},
    }
    ast, tokens = parse_complex_expression(tokenize("x.abc"))
    assert ast == {
        "tag": "complex",
        "base": {"tag": "identifier", "value": "x"},
        "index": {"tag": "string", "value": "abc"},
    }
    ast, tokens = parse_complex_expression(tokenize("x()"))
    assert ast == {
        "tag": "call",
        "function": {"tag": "identifier", "value": "x"},
        "arguments": [],
    }
    assert tokens[0]["tag"] == None

    ast, tokens = parse_complex_expression(tokenize("x(1,2)"))
    assert ast == {
        "tag": "call",
        "function": {"tag": "identifier", "value": "x"},
        "arguments": [{"tag": "number", "value": 1}, {"tag": "number", "value": 2}],
    }


# ARITHMETIC EXPRESSIONS


def parse_arithmetic_factor(tokens):
    """
    arithmetic_factor = complex_expression ;
    """
    return parse_complex_expression(tokens)


def test_parse_arithmetic_factor():
    """
    arithmetic_factor = complex_expression ;
    """
    print("testing parse_arithmetic_factor...")
    for expression in ["1", "1.2", "true", "x", "-1"]:
        t = tokenize(expression)
        assert parse_arithmetic_factor(t)[0] == parse_complex_expression(t)[0]


def parse_arithmetic_term(tokens):
    """
    arithmetic_term = arithmetic_factor { ("*" | "/") arithmetic_factor } ;
    """
    node, tokens = parse_arithmetic_factor(tokens)
    while tokens[0]["tag"] in ["*", "/"]:
        tag = tokens[0]["tag"]
        next_node, tokens = parse_arithmetic_factor(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def test_parse_arithmetic_term():
    """
    arithmetic_term = arithmetic_factor { ("*" | "/") arithmetic_factor } ;
    """
    print("testing parse_arithmetic_term...")
    ast, tokens = parse_arithmetic_term(tokenize("x"))
    assert ast == {"tag": "identifier", "value": "x"}

    ast, tokens = parse_arithmetic_term(tokenize("x*y"))
    assert ast == {
        "tag": "*",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }

    ast, tokens = parse_arithmetic_term(tokenize("x/y"))
    assert ast == {
        "tag": "/",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }

    ast, tokens = parse_arithmetic_term(tokenize("x*y/z"))
    assert ast == {
        "tag": "/",
        "left": {
            "tag": "*",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }


def parse_arithmetic_expression(tokens):
    """
    arithmetic_expression = arithmetic_term { ("+" | "-") arithmetic_term } ;
    """
    node, tokens = parse_arithmetic_term(tokens)
    while tokens[0]["tag"] in ["+", "-"]:
        tag = tokens[0]["tag"]
        next_node, tokens = parse_arithmetic_term(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def test_parse_arithmetic_expression():
    """
    arithmetic_expression = arithmetic_term { ("+" | "-") arithmetic_term } ;
    """
    print("testing parse_arithmetic_expression...")
    assert parse_arithmetic_expression(tokenize("x"))[0] == {
        "tag": "identifier",
        "value": "x",
    }
    assert parse_arithmetic_expression(tokenize("x*y"))[0] == {
        "tag": "*",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    assert parse_arithmetic_expression(tokenize("x+y"))[0] == {
        "tag": "+",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    assert parse_arithmetic_expression(tokenize("x-y"))[0] == {
        "tag": "-",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    assert parse_arithmetic_expression(tokenize("x+y-z"))[0] == {
        "tag": "-",
        "left": {
            "tag": "+",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }
    ast = parse_arithmetic_expression(tokenize("x+y*z"))[0]
    assert ast == {
        "tag": "+",
        "left": {"tag": "identifier", "value": "x"},
        "right": {
            "tag": "*",
            "left": {"tag": "identifier", "value": "y"},
            "right": {"tag": "identifier", "value": "z"},
        },
    }
    ast = parse_arithmetic_expression(tokenize("(x+y)*z"))[0]
    assert ast == {
        "tag": "*",
        "left": {
            "tag": "+",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }


# RELATIONAL EXPRESSIONS


def parse_relational_expression(tokens):
    """
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression } ;
    """
    node, tokens = parse_arithmetic_expression(tokens)
    while tokens[0]["tag"] in ["<", ">", "<=", ">=", "==", "!="]:
        tag = tokens[0]["tag"]
        next_node, tokens = parse_arithmetic_expression(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def test_parse_relational_expression():
    """
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression } ;
    """
    print("testing parse_relational_expression...")
    assert parse_relational_expression(tokenize("x"))[0] == {
        "tag": "identifier",
        "value": "x",
    }
    for tag in ["<", ">", "<=", ">=", "==", "!="]:
        assert parse_relational_expression(tokenize(f"x{tag}y"))[0] == {
            "tag": tag,
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        }
    assert parse_relational_expression(tokenize("x<y>z"))[0] == {
        "tag": ">",
        "left": {
            "tag": "<",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }


# LOGICAL EXPRESSIONS


def parse_logical_factor(tokens):
    """
    logical_factor = relational_expression ;
    """
    return parse_relational_expression(tokens)


def test_parse_logical_factor():
    """
    logical_factor = relational_expression ;
    """
    print("testing parse_logical_factor...")
    assert parse_logical_factor(tokenize("x"))[0] == {"tag": "identifier", "value": "x"}
    assert parse_logical_factor(tokenize("!x"))[0] == {
        "tag": "not",
        "value": {"tag": "identifier", "value": "x"},
    }


def parse_logical_term(tokens):
    """
    logical_term = logical_factor { "&&" logical_factor } ;
    """
    node, tokens = parse_logical_factor(tokens)
    while tokens[0]["tag"] == "&&":
        tag = tokens[0]["tag"]
        next_node, tokens = parse_logical_factor(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def test_parse_logical_term():
    """
    logical_term = logical_factor { "&&" logical_factor } ;
    """
    print("testing parse_logical_term...")
    assert parse_logical_term(tokenize("x"))[0] == {"tag": "identifier", "value": "x"}
    assert parse_logical_term(tokenize("x&&y"))[0] == {
        "tag": "&&",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    assert parse_logical_term(tokenize("x&&y&&z"))[0] == {
        "tag": "&&",
        "left": {
            "tag": "&&",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }


def parse_logical_expression(tokens):
    """
    logical_expression = logical_term { "||" logical_term } ;
    """
    node, tokens = parse_logical_term(tokens)
    while tokens[0]["tag"] == "||":
        tag = tokens[0]["tag"]
        next_node, tokens = parse_logical_term(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def test_parse_logical_expression():
    """
    logical_expression = logical_term { "||" logical_term } ;
    """
    print("testing parse_logical_expression...")

    assert parse_logical_expression(tokenize("x"))[0] == {
        "tag": "identifier",
        "value": "x",
    }
    assert parse_logical_expression(tokenize("x||y"))[0] == {
        "tag": "||",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    assert parse_logical_expression(tokenize("x||y&&z"))[0] == {
        "tag": "||",
        "left": {"tag": "identifier", "value": "x"},
        "right": {
            "tag": "&&",
            "left": {"tag": "identifier", "value": "y"},
            "right": {"tag": "identifier", "value": "z"},
        },
    }


def parse_expression(tokens):
    """
    expression = logical_expression ;
    """
    return parse_logical_expression(tokens)


def test_parse_expression():
    """
    expression = logical_expression ;
    """
    print("testing parse_expression...")
    for s in ["1", "1+1", "1 && 1", "1 < 2"]:
        t = tokenize(s)
        assert parse_expression(t) == parse_logical_expression(t)


# STATEMENTS


def parse_statement_list(tokens):
    """
    statement_list = "{" statement { ";" statement } "}" ;
    """
    assert tokens[0]["tag"] == "{", f"Expected '{{' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    statements = []
    if tokens[0]["tag"] != "}":
        statement, tokens = parse_statement(tokens)
        statements.append(statement)
        while tokens[0]["tag"] == ";":
            tokens = tokens[1:]
            statement, tokens = parse_statement(tokens)
            statements.append(statement)
    assert tokens[0]["tag"] == "}", f"Expected '}}' at position {tokens[0]['position']}"
    return {"tag": "statement_list", "statements": statements}, tokens[1:]


def test_parse_statement_list():
    """
    statement_list = "{" statement { ";" statement } "}" ;
    """
    print("testing parse_statement_list...")
    ast, tokens = parse_statement_list(tokenize("{}"))
    assert ast == {"tag": "statement_list", "statements": []}
    ast, tokens = parse_statement_list(tokenize("{print 2;print 3}"))
    assert ast == {
        "tag": "statement_list",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 2}},
            {"tag": "print", "value": {"tag": "number", "value": 3}},
        ],
    }
    ast, tokens = parse_statement_list(tokenize("{print 2; print 3}"))
    assert ast == {
        "tag": "statement_list",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 2}},
            {"tag": "print", "value": {"tag": "number", "value": 3}},
        ],
    }


def parse_if_statement(tokens):
    """
    if_statement = "if" "(" expression ")" statement_list [ "else" (if_statement | statement_list) ] ;
    """
    assert tokens[0]["tag"] == "if"
    tokens = tokens[1:]
    if tokens[0]["tag"] != "(":
        raise Exception(f"Expected '(': {tokens[0]}")
    condition, tokens = parse_expression(tokens[1:])
    if tokens[0]["tag"] != ")":
        raise Exception(f"Expected ')': {tokens[0]}")
    then_statement_list, tokens = parse_statement_list(tokens[1:])
    node = {
        "tag": "if",
        "condition": condition,
        "then": then_statement_list,
    }
    if tokens[0]["tag"] == "else":
        tokens = tokens[1:]
        assert tokens[0]["tag"] in [
            "{",
            "if",
        ], "Else must be followed by statement_list or if statement."
        if tokens[0]["tag"] == "{":
            else_statement_list, tokens = parse_statement_list(tokens)
        else:
            else_statement_list, tokens = parse_if_statement(tokens)
        node["else"] = else_statement_list
    return node, tokens


def test_parse_if_statement():
    """
    if_statement = "if" "(" expression ")" statement_list [ "else" (if_statement | statement_list) ] ;
    """
    print("testing parse_if_statement...")
    ast = parse_if_statement(tokenize("if(1){}"))[0]
    assert ast == {
        "tag": "if",
        "condition": {"tag": "number", "value": 1},
        "then": {"tag": "statement_list", "statements": []},
    }
    ast = parse_if_statement(tokenize("if(1){print 1}"))[0]
    assert ast == {
        "tag": "if",
        "condition": {"tag": "number", "value": 1},
        "then": {
            "tag": "statement_list",
            "statements": [{"tag": "print", "value": {"tag": "number", "value": 1}}],
        },
    }
    ast = parse_if_statement(tokenize("if(1){print 1}else{print 2}"))[0]
    assert ast == {
        "tag": "if",
        "condition": {"tag": "number", "value": 1},
        "then": {
            "tag": "statement_list",
            "statements": [{"tag": "print", "value": {"tag": "number", "value": 1}}],
        },
        "else": {
            "tag": "statement_list",
            "statements": [{"tag": "print", "value": {"tag": "number", "value": 2}}],
        },
    }


def parse_while_statement(tokens):
    """
    while_statement = "while" "(" expression ")" statement_list ;
    """
    assert tokens[0]["tag"] == "while"
    tokens = tokens[1:]
    if tokens[0]["tag"] != "(":
        raise Exception(f"Expected '(': {tokens[0]}")
    condition, tokens = parse_expression(tokens[1:])
    if tokens[0]["tag"] != ")":
        raise Exception(f"Expected ')': {tokens[0]}")
    do_statement_list, tokens = parse_statement_list(tokens[1:])
    return {"tag": "while", "condition": condition, "do": do_statement_list}, tokens


def test_parse_while_statement():
    """
    while_statement = "while" "(" expression ")" statement_list ;
    """
    print("testing parse_while_statement...")
    ast = parse_while_statement(tokenize("while(1){print 1}"))[0]
    assert ast == {
        "tag": "while",
        "condition": {"tag": "number", "value": 1},
        "do": {
            "tag": "statement_list",
            "statements": [{"tag": "print", "value": {"tag": "number", "value": 1}}],
        },
    }


def parse_return_statement(tokens):
    """
    return_statement = "return" [ expression ] ;
    """
    assert tokens[0]["tag"] == "return"
    tokens = tokens[1:]
    if tokens[0]["tag"] in ["}", ";", None]:
        value = None
        return {"tag": "return"}, tokens
    else:
        value, tokens = parse_expression(tokens)
        return {"tag": "return", "value": value}, tokens


def test_parse_return_statement():
    """
    return_statement = "return" [ expression ] ;
    """
    print("testing parse_return_statement...")
    ast = parse_return_statement(tokenize("return"))[0]
    assert ast == {"tag": "return"}
    ast = parse_return_statement(tokenize("return}12"))[0]
    assert ast == {"tag": "return"}
    ast = parse_return_statement(tokenize("return;34"))[0]
    assert ast == {"tag": "return"}
    ast = parse_return_statement(tokenize("return 5"))[0]
    assert ast == {"tag": "return", "value": {"tag": "number", "value": 5}}
    ast = parse_return_statement(tokenize("return (5)"))[0]
    assert ast == {"tag": "return", "value": {"tag": "number", "value": 5}}


def parse_print_statement(tokens):
    """
    print_statement = "print" [ expression ] ;
    """
    assert tokens[0]["tag"] == "print"
    tokens = tokens[1:]
    if tokens[0]["tag"] in ["}", ";", None]:
        # no expression
        return {"tag": "print", "value": None}, tokens
    else:
        value, tokens = parse_expression(tokens)
        return {"tag": "print", "value": value}, tokens


def test_parse_print_statement():
    """
    print_statement = "print" [ expression ] ;
    """
    print("testing parse_print_statement...")
    ast = parse_print_statement(tokenize("print 1"))[0]
    assert ast == {"tag": "print", "value": {"tag": "number", "value": 1}}


def parse_assignment_statement(tokens):
    """
    assignment_statement = expression [ "=" expression ] ;
    """
    target, tokens = parse_expression(tokens)
    if tokens[0]["tag"] == "=":
        tokens = tokens[1:]
        value, tokens = parse_expression(tokens)
        return {"tag": "assign", "target": target, "value": value}, tokens
    return target, tokens


def test_parse_assignment_statement():
    """
    assignment_statement = expression [ "=" expression ] ;
    """
    print("testing parse_assignment_statement...")
    ast, tokens = parse_assignment_statement(tokenize("i=2"))
    assert ast == {
        "tag": "assign",
        "target": {"tag": "identifier", "value": "i"},
        "value": {"tag": "number", "value": 2},
    }
    ast, tokens = parse_assignment_statement(tokenize("2"))
    assert ast == {"tag": "number", "value": 2}


def parse_function_statement(tokens):
    """
    function_statement = "function" identifier "(" [ identifier { "," identifier } ] ")" statement_list ;
    """
    assert tokens[0]["tag"] == "function"
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "identifier"
    identifier_token = tokens[0]
    tokens = tokens[1:]
    tokens = [
        identifier_token,
        {"tag": "=", "value": "="},
        {"tag": "function", "value": "function"},
    ] + tokens
    return parse_assignment_statement(tokens)


def test_parse_function_statement():
    """
    function_statement = "function" identifier "(" [ identifier { "," identifier } ] ")" statement_list ;
    """
    print("testing parse_function_statement...")
    ast, result = parse_function_statement(tokenize("function x(y){2}"))
    assert ast == {
        "tag": "assign",
        "target": {"tag": "identifier", "value": "x"},
        "value": {
            "body": {
                "statements": [{"tag": "number", "value": 2}],
                "tag": "statement_list",
            },
            "parameters": [{"position": 11, "tag": "identifier", "value": "y"}],
            "tag": "function",
        },
    }


def parse_statement(tokens):
    """
    statement = if_statement | while_statement |  function_statement | return_statement | print_statement | assignment_statement ;
    """
    tag = tokens[0]["tag"]
    # note: none of these consumes a token
    # if tag == "{":
    #     return parse_statement_list(tokens)
    if tag == "if":
        return parse_if_statement(tokens)
    if tag == "while":
        return parse_while_statement(tokens)
    if tag == "function":
        return parse_function_statement(tokens)
    if tag == "return":
        return parse_return_statement(tokens)
    if tag == "print":
        return parse_print_statement(tokens)
    return parse_assignment_statement(tokens)


def test_parse_statement():
    """
    statement = if_statement | while_statement | function_statement | return_statement | print_statement | assignment_statement ;
    """
    print("testing parse_statement...")

    # if statement
    assert (
        parse_statement(tokenize("if(1){print 1}"))[0]
        == parse_if_statement(tokenize("if(1){print 1}"))[0]
    )
    # # while statement
    assert (
        parse_statement(tokenize("while(1){print 1}"))[0]
        == parse_while_statement(tokenize("while(1){print 1}"))[0]
    )
    # return statement
    assert (
        parse_statement(tokenize("return 22"))[0]
        == parse_return_statement(tokenize("return 22"))[0]
    )
    # print statement
    assert (
        parse_statement(tokenize("print 1"))[0]
        == parse_print_statement(tokenize("print 1"))[0]
    )
    # function_statement (syntactic sugar)
    assert (
        parse_statement(tokenize("function x(y){2}"))[0]
        == parse_function_statement(tokenize("function x(y){2}"))[0]
    )


def parse_program(tokens):
    """
    program = [ statement { ";" statement } ] ;
    """
    statements = []
    if tokens[0]["tag"]:
        statement, tokens = parse_statement(tokens)
        statements.append(statement)
        while tokens[0]["tag"] == ";":
            tokens = tokens[1:]
            statement, tokens = parse_statement(tokens)
            statements.append(statement)
    assert (
        tokens[0]["tag"] == None
    ), f"Expected end of input at position {tokens[0]['position']}, got [{tokens[0]}]"
    return {"tag": "program", "statements": statements}, tokens[1:]


def test_parse_program():
    """program = [ statement { ";" statement } ] ;"""
    print("testing parse_program...")
    ast, tokens = parse_program(tokenize("print 1; print 2"))
    assert ast == {
        "tag": "program",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 1}},
            {"tag": "print", "value": {"tag": "number", "value": 2}},
        ],
    }


def parse(tokens):
    ast, tokens = parse_program(tokens)
    return ast


def test_parse():
    print("testing parse")
    tokens = tokenize("2+3*4+5")
    ast = parse(tokens)
    assert ast == {
        "statements": [
            {
                "left": {
                    "left": {"tag": "number", "value": 2},
                    "right": {
                        "left": {"tag": "number", "value": 3},
                        "right": {"tag": "number", "value": 4},
                        "tag": "*",
                    },
                    "tag": "+",
                },
                "right": {"tag": "number", "value": 5},
                "tag": "+",
            }
        ],
        "tag": "program",
    }
    tokens = tokenize("1*2<3*4||5>6&&7")
    ast = parse(tokens)
    assert ast == {
        "tag": "program",
        "statements": [
            {
                "tag": "||",
                "left": {
                    "tag": "<",
                    "left": {
                        "tag": "*",
                        "left": {"tag": "number", "value": 1},
                        "right": {"tag": "number", "value": 2},
                    },
                    "right": {
                        "tag": "*",
                        "left": {"tag": "number", "value": 3},
                        "right": {"tag": "number", "value": 4},
                    },
                },
                "right": {
                    "tag": "&&",
                    "left": {
                        "tag": ">",
                        "left": {"tag": "number", "value": 5},
                        "right": {"tag": "number", "value": 6},
                    },
                    "right": {"tag": "number", "value": 7},
                },
            }
        ],
    }


if __name__ == "__main__":
    # List of all test functions
    test_functions = [
        test_parse_simple_expression,
        test_parse_list_literal,
        test_parse_object_literal,
        test_parse_function_literal,
        test_parse_complex_expression,
        test_parse_arithmetic_factor,
        test_parse_arithmetic_term,
        test_parse_arithmetic_expression,
        test_parse_relational_expression,
        test_parse_logical_factor,
        test_parse_logical_term,
        test_parse_logical_expression,
        test_parse_expression,
        test_parse_statement_list,
        test_parse_if_statement,
        test_parse_while_statement,
        test_parse_return_statement,
        test_parse_print_statement,
        test_parse_assignment_statement,
        test_parse_function_statement,
        test_parse_statement,
        test_parse_program,
    ]

    test_grammar = grammar

    # Run each test function
    for test_function in test_functions:
        rule = test_function.__doc__.strip().replace("Tests  ", "")
        print("testing", rule.split(" = ")[0])
        assert rule in grammar, f"rule [[[ {rule} ]]] not in grammar."
        test_grammar = test_grammar.replace(rule + "\n", "")
        test_function()

    if test_grammar.strip() != "":
        print(f"Untested grammar = [[[ {test_grammar} ]]]")

    test_parse()