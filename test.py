from tkinter import Tk, BOTH, RAISED, LEFT,RIGHT, Listbox, StringVar, END, SINGLE
from tkinter.ttk import Frame, Button, Style, Entry, Label

# --------------------------------------------------------------------------------
# --- Management of command list
# --------------------------------------------------------------------------------
class CommandList():
    def __init__(self,filename):
        try: 
            self.f=open(filename,'r')
            self.cmds=[l.strip() for l in self.f.readlines()]
            self.f.close()
        except IOError:
            self.cmds=[]

        self.f=open(filename,'a')
        self.f.write('hello\n')
    def __term__(self):
        self.f.close()

    def add(self,cmd):
        print('cmd add')
        self.f.write(cmd+'\n')


    
# --------------------------------------------------------------------------------
# --- UI 
# --------------------------------------------------------------------------------
class FuzzyUI(Frame):
  
    def __init__(self, parent,commands):
        Frame.__init__(self, parent)
        self.parent = parent
        self.commands=commands
        self.initUI()
        
    def initUI(self):
        frame = Frame(self)
        frame.pack(fill=BOTH, expand=1)
        self.pack(fill=BOTH, expand=1)
        closeButton = Button(self, text="Abort",command=self.quit)
        closeButton.pack(side=RIGHT, padx=5, pady=5)

    def quit(self):
        self.commands.add('Kill')
#         self.commands.__term__
#         Frame.quit(self)

# --------------------------------------------------------------------------------
# --- Main 
# --------------------------------------------------------------------------------
def main():
    import os
    script_dir=os.path.dirname(os.path.realpath(__file__))
    commands = CommandList(os.path.join(script_dir,'CommandList.txt'))
    root = Tk()
    ui = FuzzyUI(root,commands)
    root.mainloop()  


if __name__ == '__main__':
    main()  








