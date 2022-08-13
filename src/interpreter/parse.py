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

string.-2 : ESCAPED_STRING
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
ALLNONCONFLICTINGWITHNEWLINES: /([^\[\]\{\}\"\s\,\-]|[\n\-])/
ALLNONCONFLICTING: /([^\[\]\{\}\"\s\,\-]|[\-])/
ALLEXCEPTBRACKETS: /[^\[\]]/
ALLEXCEPTQUOTES: /[^\"]/
WHITESPACEEXCEPTNEWLINE: /[^\S\r\n]/
ESCAPED_STRING : "\"" ALLEXCEPTQUOTES* "\""


// common lib stuff
// imports from common library my beloved
%import common.DECIMAL
%import common.C_COMMENT
%import common.SIGNED_INT
%ignore WHITESPACEEXCEPTNEWLINE
%ignore C_COMMENT
%ignore COMMENT"""
parser = Lark(bstargrammar)


def parseCode(code):
    return parser.parse(code)