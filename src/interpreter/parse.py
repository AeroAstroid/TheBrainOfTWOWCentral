from lark import Lark

bstargrammar = r"""
start: bstar*
    
?bstar:
    | function
    | ALLBUTBRACKETS
?arg:
    | ("true" | "True") -> true
    | ("false" | "False") -> false
    | string
    | integer
    | float
    | function
    | array
    | unescaped_string
string: ESCAPED_STRING
block: ALPHANUMERIC
float.-0: DECIMAL
integer.-1: SIGNED_INT
array: "{" [arg ("," arg)*] "}"
function: ("[") (block | function) arg* ("]")
COMMENT: ("[# ") ALLBUTBRACKETS ("]")
unescaped_string.-3: ALPHANUMERIC
ALLBUTBRACKETS: ALLEXCEPTBRACKETS+
DIGIT: "0".."9"
LCASE_LETTER: "a".."z"
UCASE_LETTER: "A".."Z"
LETTER: UCASE_LETTER | LCASE_LETTER
ALPHANUMERIC: (ALLNONCONFLICTING)+
ALLNONCONFLICTING: /([^\[\]\{\}\"\s\,\-]|\- )/
ALLEXCEPTBRACKETS: /[^\[\]]/
// imports from common library my beloved
%import common.ESCAPED_STRING
%import common.SIGNED_INT
%import common.DECIMAL
%import common.C_COMMENT
%import common.WS
%ignore WS
%ignore C_COMMENT
%ignore COMMENT"""
parser = Lark(bstargrammar)


def parseCode(code):
    return parser.parse(code)
