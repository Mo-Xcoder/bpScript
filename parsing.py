from err import Error


class Parser:
    def __init__(self, code: str):
        # Pass in the code
        self.code = code
        # Parse the code
        self.code = self.parse(self.code)

    def parse(self, code: str) -> str:
        # Parse code into normal python
        code = self.parse_imports(code)
        code = self.parse_comment(code)
        code = self.parse_key_words(code)
        code = self.parse_end_of_line(code)
        code = self.parse_syntax_braces(code)
        code = self.parse_funcs(code)
        code = self.cleanup(code)
        code = self.entrypoint(code)
        # Dump the generated code to a file
        with open('output.py', 'w') as f:
            f.write(code)
        return code

    def parse_comment(self, code: str) -> str:
        for l in code.splitlines():
            if '!' in l:
                if not self.InString('!', l):
                    if list(l)[0] == '!':
                        code = code.replace(l, "")
                else:
                    nLine = l.partition("!")[0]
                    code = code.replace(l, nLine)
        return code

    def InString(self, word: str, l: str, return_if_multi=False) -> bool:
        if not word in l:
            return False
        if l.count(word) > 1:
            return return_if_multi
        leftSide = l.partition(word)[0]
        if leftSide.count("\"") > 0:
            if leftSide.count("\"") % 2 == 0:
                return False
            else:
                return True
        if leftSide.count("\'") > 0:
            if leftSide.count("\'") % 2 == 0:
                return False
            else:
                return True

    def parse_imports(self, code: str) -> str:
        includeName = ""
        for line in code.splitlines():
            words = line.split()
            for wordNo, word in enumerate(words):
                if words[wordNo] == "from" and not self.InString(words[wordNo], line):
                    if words[wordNo + 1]== "native":
                        if words[wordNo + 2] == "import":
                            words[wordNo] = f"from {words[wordNo + 3]} import *"
        for line in code.splitlines():
            words = line.split()
            for wordNo, word in enumerate(words):
                if word == "include" and not self.InString(word, line):
                    includeName = words[wordNo + 1]
                    code = code.replace(line, "")
                    with open(includeName.removesuffix(";") + ".bps", "r") as file:
                        code = file.read() + "\n" + code
        for line in code.splitlines():
            if "from native import " in line:
                if self.InString("from native import ", line, True):
                    continue
                code = code.replace(line, line.replace("from native import ", "import "))
                words = line.split()
                newLine = ""
                for wordNo, word in enumerate(words):
                    if words[wordNo] == "from" and not self.InString(words[wordNo], line):
                        if words[wordNo + 1] == "native":
                            if words[wordNo + 2] == "import":
                                words[wordNo] = "import"
                                words[wordNo] = ""
                                words[wordNo + 2] = ""
                                newLine = " ".join(words)
                if newLine != "":
                    code = code.replace(line, newLine)

        return code

    def parse_end_of_line(self, code: str) -> str:
        code = "".join([s for s in code.splitlines(True) if s.strip("\r\n")])

        for line in code.splitlines():
            skipLine = False
            for token in ("etch", "while", "for", "if", "else", "elif", "with", "from", "but"):
                if token in line and not self.InString(token, line):
                    skipLine = True
            if ''.join(line.split()).startswith(("{", "}", "\n", "class")):
                skipLine = True
            elif line.strip() == "":
                skipLine = True
            if skipLine:
                continue
            if ";" in line and not self.InString(";", line):
                lineChars = list(line)
                stringCount = 0
                for i in range(len(lineChars)):
                    if lineChars[i] == '"' or lineChars[i] == "'":
                        stringCount += 1
                    if lineChars[i] == ";":
                        if stringCount % 2 == 0:
                            lineChars[i] = "\n"
                            break

            elif line.endswith((":")):
                Error(f"Syntax error at: \n{line}")
            else:
                Error(f"Missing semicolon at: \n{line}")
            if line.endswith((":")):
                Error(f"Syntax error at: \n{line}")

        return code

    def parse_funcs(self, code: str) -> str:
        code = code
        for line in code.splitlines():
            if "etch" in line and not self.InString("etch", line):
                code = code.replace(line, line.replace("etch", "def"))
        for line in code.splitlines():
            if "def Start" in line and not self.InString("def Start", line):
                code = code.replace(line, line.replace(
                    "def Start", "def __init__"))
        for line in code.splitlines():
            if ") returns" in line and not self.InString(") returns", line):
                code = code.replace(line, line.replace(") returns", ") ->"))
        for line in code.splitlines():
            if "def" in line:
                if (line.partition("def")[0].strip() == ""):
                    code = code.replace(line, line.replace("(", "(self,"))
        return code

    def parse_key_words(self, code: str) -> str:
        for line in code.splitlines():
            if "reference" in line and not self.InString("reference", line):
                code = code.replace(line, line.replace("reference", "self"))
        for line in code.splitlines():
            if "true" in line and not self.InString("true", line):
                code = code.replace(line, line.replace("true", "True"))
        for line in code.splitlines():
            if "false" in line and not self.InString("false", line):
                code = code.replace(line, line.replace("false", "False"))
        for line in code.splitlines():
            if "nothing" in line and not self.InString("nothing", line):
                code = code.replace(line, line.replace("nothing", "None"))
        for line in code.splitlines():
            if "but" in line and not self.InString("but", line):
                code = code.replace(line, line.replace("but", "elif"))
        return code

    def parse_syntax_braces(self, code: str) -> str:
        leftBracesAmount = 0
        for line in code.splitlines():
            if "{" in line:
                lineChars = list(line)
                stringCount = 0
                for i in range(len(lineChars)):
                    if lineChars[i] == '"' or lineChars[i] == "'":
                        stringCount += 1
                    if lineChars[i] == "{":
                        if stringCount % 2 == 0 and stringCount != 0:
                            leftBracesAmount += 1
                            break
        rightBracesAmount = 0
        for line in code.splitlines():
            if "}" in line:
                lineChars = list(line)
                stringCount = 0
                for i in range(len(lineChars)):
                    if lineChars[i] == '"' or lineChars[i] == "'":
                        stringCount += 1
                    if lineChars[i] == "}":
                        if stringCount % 2 == 0 and stringCount != 0:
                            rightBracesAmount += 1
                            break

        if leftBracesAmount != rightBracesAmount:
            Error(("Braces do not equal!"))

        newCode = ""
        splitLines = code.splitlines()
        for line in splitLines:
            if ";" in line and not self.InString(";", line):
                lineChars = list(line)
                stringCount = 0
                for i in range(len(lineChars)):
                    if lineChars[i] == '"' or lineChars[i] == "'":
                        stringCount += 1
                    if lineChars[i] == ";":
                        if stringCount % 2 == 0:
                            lineChars[i] = "\n"
                            break
                line = "".join(lineChars)
            if "class" in line:
                if not self.InString("class", line):
                    line = "\n"+" ".join(line.split())
            if "etch" in line:
                if line.partition("etch")[0].count("\"") != 0 and line.partition("etch")[0].count("\"") % 2 == 0:
                    words = line.split()
                    for wordNo, word in enumerate(words):
                        if word == "etch":
                            speechCount = line.partition("etch")[2].count("\"")
                            otherCount = line.partition("etch")[2].count("'")
                            if speechCount % 2 == 0 and otherCount % 2 == 0:
                                words[wordNo] = "def"
                                break
                    line = " ".join(words)
            leftBraceExpression = ''.join(line.split())
            if not self.InString("{", leftBraceExpression):
                if ''.join(line.split()).startswith(("{")):
                    newCode += ":\n"
            if not self.InString("}", line):
                line = line.replace("}", "#endindent")
            if not self.InString("{", line):
                line = line.replace("{", "#startindent")
            line += "\n"
            newCode += line
            line += "\n"

        return newCode

    def cleanup(self, code: str) -> str:
        # I did mess up a bit, this will fix it.

        splitLines = code.splitlines()
        for lineNo, line in enumerate(splitLines):
            if line.startswith(":"):
                splitLines[lineNo - 1] = splitLines[lineNo - 1] + ":"
                splitLines[lineNo] = ""
        newCode = ""
        for line in splitLines:
            newCode += line + "\n"
        code = newCode

        splitLines = code.splitlines()
        newCode = ""
        for lineNo, line in enumerate(splitLines):
            i = 0
            indentCount = 0
            while i <= lineNo:
                if "#endindent" in splitLines[i]:
                    if not self.InString("#endindent", splitLines[i], True):
                        indentCount -= 1

                elif "#startindent" in splitLines[i] and not self.InString("#startindent", splitLines[i], True):
                    if not self.InString("#startindent", splitLines[i]):
                        indentCount += 1
                i += 1
            newCode += ("    " * indentCount) + line + "\n"
        code = newCode

        # Remove indent helpers
        newCode = ""
        for line in code.splitlines():
            if "#endindent" in line:
                if not self.InString("#endindent", line):
                    line = line.replace(line, "")
            if "#startindent" in line:
                if not self.InString("#startindent", line):
                    line = line.replace(line, "")
            newCode += line + "\n"
        code = newCode

        # Tidy code by removing empty lines
        newCode = ""
        for line in code.splitlines():
            if line.strip("\t\r\n") == "":
                line = line.replace(line, line.strip("\t\r\n"))
                newCode += line
            else:
                newCode += line + "\n"
        code = newCode

        code = "\n".join([ll.rstrip()
                         for ll in code.splitlines() if ll.strip()])

        return code

    def entrypoint(self, code: str) -> str:
        code += "\n"
        code += '''
if __name__ == "__main__":
    main = Main()
    main.Main()
        '''

        return code
