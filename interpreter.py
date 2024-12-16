import re

# Regular expressions for tokens
IDENTIFIER = r"[a-zA-Z_][a-zA-Z0-9_]*"  # Valid identifiers
LITERAL = r"0|[1-9][0-9]*"             # Valid literals: "0" or non-zero numbers
OPERATOR = r"[\+\-\*]"                 # Operators: +, -, *
ASSIGN = r"="                          # Assignment operator
SEMICOLON = r";"                       # Semicolon
PARENTHESIS = r"[\(\)]"                # Parentheses: ( and )

TOKENS = f"{IDENTIFIER}|{LITERAL}|{OPERATOR}|{ASSIGN}|{SEMICOLON}|{PARENTHESIS}"


class Interpreter:
    def __init__(self):
        self.variables = {}  # Store variable assignments

    def tokenize(self, program):
        """Tokenize the input program."""
        tokens = re.findall(TOKENS, program)
        program_no_spaces = re.sub(r'\s+', '', program)  # Remove spaces
        tokens_combined = ''.join(tokens)
        if tokens_combined != program_no_spaces:
            raise SyntaxError("Invalid syntax")
        return tokens

    def parse(self, tokens):
        """Parse tokens into assignments."""
        i = 0
        assignments = []
        while i < len(tokens):
            if re.match(IDENTIFIER, tokens[i]):
                var = tokens[i]
                i += 1
                if i >= len(tokens) or tokens[i] != "=":
                    raise SyntaxError("Expected '=' after variable")
                i += 1
                expr, i = self.parse_expression(tokens, i)
                if i >= len(tokens) or tokens[i] != ";":
                    raise SyntaxError("Expected ';' at the end of assignment")
                i += 1
                assignments.append((var, expr))
            else:
                raise SyntaxError("Invalid assignment statement")
        return assignments

    def parse_expression(self, tokens, i):
        """Parse expressions with addition and subtraction."""
        term, i = self.parse_term(tokens, i)
        while i < len(tokens) and tokens[i] in "+-":
            op = tokens[i]
            i += 1
            next_term, i = self.parse_term(tokens, i)
            term = (op, term, next_term)
        return term, i

    def parse_term(self, tokens, i):
        """Parse terms with multiplication."""
        fact, i = self.parse_fact(tokens, i)
        while i < len(tokens) and tokens[i] == "*":
            op = tokens[i]
            i += 1
            next_fact, i = self.parse_fact(tokens, i)
            fact = (op, fact, next_fact)
        return fact, i

    def parse_fact(self, tokens, i):
        """Parse factors: literals, identifiers, negation, or parenthesis."""
        token = tokens[i]
        if token == "(":
            i += 1
            expr, i = self.parse_expression(tokens, i)
            if i >= len(tokens) or tokens[i] != ")":
                raise SyntaxError("Expected ')'")
            i += 1
            return expr, i
        elif token == "-":  # Handle unary negation
            i += 1
            fact, i = self.parse_fact(tokens, i)
            return ("-", None, fact), i
        elif re.match(LITERAL, token):
            return int(token), i + 1
        elif re.match(IDENTIFIER, token):
            return token, i + 1
        else:
            raise SyntaxError("Invalid factor")

    def evaluate(self, expr):
        """Evaluate the parsed expression recursively."""
        if isinstance(expr, int):  # Literal
            return expr
        elif isinstance(expr, str):  # Identifier
            if expr not in self.variables:
                raise NameError(f"Uninitialized variable '{expr}'")
            return self.variables[expr]
        elif isinstance(expr, tuple):  # Operation
            op, left, right = expr
            if op == "+":  # Binary addition
                return self.evaluate(left) + self.evaluate(right)
            elif op == "-":  # Unary or binary subtraction
                if left is None:  # Unary negation
                    return -self.evaluate(right)
                return self.evaluate(left) - self.evaluate(right)  # Binary subtraction
            elif op == "*":  # Binary multiplication
                return self.evaluate(left) * self.evaluate(right)
        else:
            raise ValueError("Invalid expression")

    def execute(self, program):
        """Tokenize, parse, and evaluate the program."""
        try:
            tokens = self.tokenize(program)
            assignments = self.parse(tokens)
            for var, expr in assignments:
                self.variables[var] = self.evaluate(expr)
            for var, val in self.variables.items():
                print(f"{var} = {val}")
        except (SyntaxError, NameError, ValueError):
            print("error")


# Example usage
if __name__ == "__main__":
    interpreter = Interpreter()

    # Test Input Programs
    programs = [
        "x = 001;",  # Input 1
        "x_2 = 0;",  # Input 2
        "x = 0 y = x; z = ---(x+y);",  # Input 3
        "x = 1; y = 2; z = ---(x+y)*(x+-y);"  # Input 4
    ]

    for program in programs:
        print(f"Input: {program.strip()}")
        interpreter.execute(program)
        print()
