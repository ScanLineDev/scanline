
from ailinter import ailinter 

def main():
    print ("👨🏻‍💻 Starting AI code review")
    #print(ailinter.get_file_diffs(["./ailinter/ailinter.py"]))
    ailinter.run()
    print ("✅ Code review complete")
    
if __name__ == "__main__":   
    main()
    