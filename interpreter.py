#Native
import os.path
import subprocess
import sys
import shutil

#PyPy
pyInstallerInstalled = True

try:
    import PyInstaller.__main__ as PyInstaller
except ImportError:
    pyInstallerInstalled = False

#Custom
from parsing import Parser
from err import Error

version = "0.1.0"

class Interpreter:
    def Interpret(self, code : str) -> None:
        subprocess.call(["python", "output.py"])


def GetCode(filePath) -> str:
    if os.path.isfile(filePath):
        with open(filePath, 'r') as file:
            return file.read()
    else:
        Error("Input file not found")

def HandleArgs() -> None:
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        Error('''
        Command line arguments:
        --help -h: Prints this
        --version -b: Shows the interpreter version
        --run -r (default) [file]: Runs the interpreter on the give nfile
        --transpile -t [file] [out]: transpiles the given file into python and saves it to the output specified
        --compile -c [file] [out]: Compiles the given file into an executable and saves it to the output specified
            ''')
    elif sys.argv[1] == "--run" or sys.argv[1] == "-r":
        if len(sys.argv) < 3:
            Error("Invalid num of arg")
        else:
            if os.path.isfile(sys.argv[2]):
                parser = Parser(GetCode((sys.argv[2])))
                interpreter = Interpreter()
                interpreter.Interpret(parser.code)
            else:
                Error("File not found")
    elif os.path.isfile(sys.argv[1]):
        parser = Parser(GetCode(sys.argv[1]))
        interpreter = Interpreter()
        interpreter.Interpret(parser.code)
    elif sys.argv[1] == "--transpile" or sys.argv[1] == "-t":
        if len(sys.argv) < 4:
            Error("Invalid num of arg")
        else:
            if os.path.isfile(sys.argv[2]):
                parser = Parser(GetCode((sys.argv[2])))
                with open(sys.argv[3], "w") as f:
                    f.write(parser.code)
            else:
                Error("Input file not found")
    elif sys.argv[1] == "--compile" or sys.argv[1] == "-c":
        if pyInstallerInstalled == False:
            Error("PyInstaller not found, \n Are you sure its installed? If not, run \"pip install PyInstaller\"")
        if len(sys.argv) < 4:
            Error("Invalid num of arg")
        else:
            if os.path.isfile(sys.argv[2]):
                parser = Parser(GetCode((sys.argv[2])))
                fileName = sys.argv[3].split(".")[0]
                with open(fileName + ".py", "w") as f:
                    f.write(parser.code)
                if (os.path.isfile(fileName + ".exe")):
                    os.remove(fileName + ".exe")
                subprocess.call(["python3", "-m", "PyInstaller", fileName + ".py", "--onefile"])
                os.rename("dist/{}".format(fileName), "./"+sys.argv[3])
                os.remove(fileName + ".py")
                os.remove(fileName + ".spec")
                shutil.rmtree("build")
                shutil.rmtree("dist")
            else:
                Error("File not found")
    else:
        Error("Invalid argument")

    if (os.path.isfile("output.py")):
        os.remove("output.py")

def CheckArgs() -> str:
    if len(sys.argv) < 2:
        Error("Invalid number of arguments")
    HandleArgs()
    
if __name__ == "__main__":
    CheckArgs()