try:
    from tkinter import Tk, BOTH, RAISED, LEFT,RIGHT, Listbox, StringVar, END, SINGLE
    from tkinter.ttk import Frame, Button, Style, Entry, Label
except ImportError:
    from Tkinter import Tk, BOTH, RAISED, LEFT,RIGHT, Listbox, StringVar, END, SINGLE
    from ttk import Frame, Button, Style, Entry, Label


# Keyboard Shortcuts
key_dict={
        'launch'        : r"'\r'",  # Enter
        'history_newer' : r"'\n'",  # Ctrl-j
        'history_older' : r"'\x0b'",# Ctrl-k
        'next'          : r"'\x0e'",# Ctrl-n
        'prev'          : r"'\x10'",# Ctrl-p
        'exit'          : [r"'\x1b'",r"'\x03'"],# Esc,Ctrl-C
        'completion'    : [r"'\t'"],  # Tab
        }
# UI Layout 
N_RESULTS=4
N_HIST=4
WIDTH=60
HREF=17
HSPACE=4
XREF=80
XLAB=3



# --------------------------------------------------------------------------------
# --- Management of command list
# --------------------------------------------------------------------------------
class CommandList():
    def __init__(self,filename):
        self.filename=filename;
        try: 
            self.f=open(filename,'r')
            self.cmds=[l.strip() for l in self.f.readlines()]
            self.f.close()
        except IOError:
            self.cmds=[]

#         self.f=open(filename,'a')
#     def __term__(self):
#         self.f.close()

    def add(self,cmd):
        if cmd not in self.cmds:
            self.f=open(self.filename,'a')
            self.f.write(cmd+'\n')
            self.f.close()

# --------------------------------------------------------------------------------
# --- Management of command history
# --------------------------------------------------------------------------------
class CommandHistory():
    def __init__(self,filename):
        self.filename=filename;
        try: 
            self.f=open(filename,'r')
            self.cmds=[l.strip() for l in self.f.readlines()]
            self.f.close()
        except IOError:
            self.cmds=[]
# 
#         self.f=open(filename,'a')
#     
#     def __term__(self):
#         self.f.close()

    def add(self,cmd):
        if (len(self.cmds)>0 and cmd!=self.cmds[-1]) or (len(self.cmds)==0):
            self.f=open(self.filename,'a')
            self.f.write(cmd+'\n')
            self.f.close()


# --------------------------------------------------------------------------------
# --- Perform fuzzy query to find closest command
# --------------------------------------------------------------------------------
class FuzzyCommands():

    def __init__(self,commands,history):
        self.commands=commands
        self.history=history
    

    def querry(self,cmd):
        import Levenshtein as lv

        #print('Querrying for string: '+cmd)
        SelectedCommands=[l for l in self.commands.cmds if self.containsAllInOrderSmartCase(l,cmd) ];
#         SortedCommands=SelectedCommands
        Ratios=[lv.ratio(cmd,c) for c in SelectedCommands]
        #print Ratios
        Index=reversed(sorted(range(len(Ratios)), key=Ratios.__getitem__))
        SortedCommands=[SelectedCommands[i] for i in Index ];
#         print SortedCommands
        Results=SortedCommands[0:min(len(SortedCommands),N_RESULTS)]
        #print Results
        return Results
 
    # tools
    @staticmethod
    def containsAllInOrderSmartCase(str, set):
        i=0
        n=len(set)
        for c in str:
            if (set[i].istitle() and c==set[i]) or (not(set[i].istitle()) and c.lower()==set[i].lower()):
                i=i+1
                if i==n:
                    return 1;
        return 0;
    @staticmethod
    def containsAllInOrder(str, set):
        i=0
        n=len(set)
        for c in str:
            if c==set[i]:
                i=i+1
                if i==n:
                    return 1;
        return 0;
# --------------------------------------------------------------------------------
# --- UI 
# --------------------------------------------------------------------------------
class FuzzyUI(Frame):
  
    def __init__(self, parent,fuzz):
        Frame.__init__(self, parent)
        self.parent = parent
        # Text string
        self.sQuerry   = ''
        self.sSelected = StringVar()
        self.sTypedSaved = ''
        self.sEntry    = StringVar()
        self.sError    = StringVar()
        # Fuzzy Command searcher 
        self.fuzz=fuzz

        self.n_results=-1 # number of results found
        self.i_select=-1  # selected index within list
        self.n_hist  =len(fuzz.history.cmds)
        self.i_hist  =self.n_hist  # selected index within list
        self.hist_lock  =False
        self.i_completion  =0 # number of successive completions

        # Init Ui
        self.initUI()
        self.populate_history()


    def centerWindow(self):
        w = 570
        h = (4+N_HIST+N_RESULTS)*HREF+3*HSPACE
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
    def initUI(self):
      
        self.parent.title("fuzzy-run")
        self.style = Style()
        self.style.theme_use("default")
        self.centerWindow()
        #frame = Frame(self, relief=RAISED, borderwidth=1)
        frame = Frame(self)
        frame.pack(fill=BOTH, expand=1)
#         self.bind("<Key>", self.special_key)
#         self.bind("<Button-1>", self.callback)
        self.pack(fill=BOTH, expand=1)
        
        # HISTORY (Label and listbox)
        Y=HSPACE
        H=HREF*N_HIST
        label = Label(self, text='History:')
        label.place(x=XLAB, y=Y)
        self.lbh = Listbox(self,selectmode=SINGLE,width=WIDTH)
        self.lbh.bind("<<ListboxSelect>>", self.onSelectHist)    
        self.lbh.place(x=XREF, y=Y,h=H)

        # The query text box and error label
        Y=Y+H+HSPACE
        H=HREF
        
        label = Label(self, text='Querry:')
        label.place(x=XLAB, y=Y)
        self.error_label = Label(self, text=0, textvariable=self.sError)        
        self.error_label.place(x=XREF-8, y=Y)

        self.sEntry.trace('w',self.string_modified)
        self.entry = Entry(self,textvariable=self.sEntry,width=WIDTH)
        self.entry.bind("<Key>", self.special_key)
        self.entry.place(x=XREF, y=Y)

        # List box of results
        Y=Y+H+HSPACE
        H=HREF*N_RESULTS
        label = Label(self, text='Match:')
        label.place(x=XLAB, y=Y)
        self.lb = Listbox(self,selectmode=SINGLE,width=WIDTH)
        self.lb.bind("<<ListboxSelect>>", self.onSelect)    
        self.lb.place(x=XREF, y=Y,h=H)


        # Command selected for run
        Y=Y+H+HSPACE
        label = Label(self, text='Command:')
        label.place(x=XLAB, y=Y)
        self.label = Label(self, text=0, textvariable=self.sSelected)        
        self.label.place(x=XREF, y=Y)

        # Buttons
        Y=Y+H+HSPACE
        closeButton = Button(self, text="Abort",command=self.quit)
        closeButton.pack(side=RIGHT, padx=5, pady=5)
        okButton = Button(self, text="Run command",command=self.launch_cmd)
        okButton.pack(side=RIGHT)

        self.entry.focus_set()
    
    
    def special_key(self,event):
        key=repr(event.char)
        if key in key_dict['launch']:
            self.launch_cmd()
        if key in key_dict['completion']:
            if self.i_completion==0:
                self.completion()
            else:
                self.result_down()
                self.completion()
            return "break"
        elif key in key_dict['next']:
            self.result_down()
            return "break"
        elif key in key_dict['prev']:
            self.result_up()
            return "break"
        elif key in key_dict['history_newer']:
            self.history_newer()
            return "break"
        elif key in key_dict['history_older']:
            self.history_older()
            return "break"
        elif key in key_dict['exit']:
            # escape, we exit or we cancel selection
            if self.hist_lock:
                self.clear_hist()
            elif self.n_results>0:
                self.purge_results()
            elif len(self.sEntry.get())>0:
                # then we clear
                self.clear()
            else:
                self.quit()
        else:
            self.hist_lock=False
            #print "pressed", repr(event.char)
            pass

    def string_modified(self,*args):
        #print('String modified !')
        if self.hist_lock:
            self.purge_results()
        else:
            self.sQuerry=self.sEntry.get() # we perfom a querry on what the user typed
            self.set_error(False)
            #print('sQuerry:',self.sQuerry)
            #print('sEntry:',self.sEntry.get())
            if len(self.sEntry.get())>0: 
                self.do_querry(self.sQuerry)
            else:
                self.purge_results()
        return "break"

# --------------------------------------------------------------------------------
# --- Result selection 
# --------------------------------------------------------------------------------
    def result_down(self):
        if self.n_results>0:
            self.i_select=(self.i_select+1) % self.n_results
            self.do_select()
    
    def result_up(self):
        if self.n_results>0:
            if self.i_select==-1:
                self.i_select=self.n_results-1
            else:
                self.i_select=(self.i_select-1) % self.n_results
            self.do_select()

    def do_select(self):
        self.lb.selection_clear(0,END)
        self.lb.selection_set(self.i_select)
#         self.lb.see(self.i_select)
        self.sSelected.set(self.lb.get(self.i_select))

    def onSelect(self, val):
        sender = val.widget
        idx = sender.curselection()
        if len(idx)>0:
            self.i_select=int(idx[0])
            self.do_select()
        
    
    # Clear selection (not used anymore)
    def clear_select(self):
        #print('Clear select')
        self.lb.selection_clear(0,END)
        self.i_select=-1
        self.sSelected.set(self.sEntry.get())
        self.i_completion=0
    
    def purge_results(self):
        #print('Purge results')
        self.lb.delete(0,END)
        self.n_results=0
        self.sSelected.set(self.sEntry.get())
        self.i_completion=0

    def populate_results(self,L):
        self.n_results=len(L)
        self.i_select=-1
        self.lb.delete(0,END)
        for i in L:
            self.lb.insert(END, i)
# --------------------------------------------------------------------------------
# --- History selection 
# --------------------------------------------------------------------------------
    def history_newer(self):
        self.i_hist=(self.i_hist+1) % self.n_hist
        self.do_hist()

    def history_older(self):
        self.i_hist=(self.i_hist-1) % self.n_hist
        self.do_hist()

    def do_hist(self):
        if self.n_hist>0:
            #print('hist:'+str(self.i_hist)+'/'+str(self.n_hist)+' '+ self.fuzz.history.cmds[self.i_hist])
            if not self.hist_lock:
                # we backup the user string and we put a lock
                self.sTypedSaved=self.sEntry.get()
                self.hist_lock=True
            self.lbh.selection_clear(0,END)
            self.lbh.selection_set(self.i_hist)
            self.lbh.see(self.i_hist)
            self.sSelected.set(self.lbh.get(self.i_hist))
            self.sEntry.set(self.fuzz.history.cmds[self.i_hist])
            self.entry.icursor(END)
    
    def onSelectHist(self, val):
        sender = val.widget
        idx = sender.curselection()
        if len(idx)>0:
            self.i_hist=int(idx[0])
            self.do_hist()

    def clear_hist(self):
        self.hist_lock=False
        self.i_hist=self.n_hist
        self.lbh.see(END)
        self.sEntry.set(self.sTypedSaved)
        self.sTypedSaved=''
    
    def populate_history(self):
        self.lbh.delete(0,END)
        for i in self.fuzz.history.cmds:
            self.lbh.insert(END, i)
        self.lbh.see(END)

# --------------------------------------------------------------------------------
# --- completion and cleaning
# --------------------------------------------------------------------------------
    def completion(self):
        # we count the number of times completion is done
        self.i_completion=self.i_completion+1 
        # We save the previous text (just in case, not used yet)
        self.sTypedSaved=self.sEntry.get()
        # We update entry we the selection
        self.sEntry.set(self.sSelected.get())
        self.entry.icursor(END)

    def clear(self):
        #print('Clearing')
        self.lb.delete(0,END)
        self.sEntry.set('')


# --------------------------------------------------------------------------------
# --- Querry
# --------------------------------------------------------------------------------
    def do_querry(self,querry):
        #print('Doing querry')
        Results=self.fuzz.querry(querry)
        self.populate_results(Results)
        if len(Results)>0:
            self.i_select=0
            self.do_select()
        else:
            self.sSelected.set(querry)

    def launch_cmd(self):
        cmd=self.sSelected.get()
        #print('Calling external:'+cmd)
        import os
        import sys
        import platform
        from subprocess import Popen, PIPE
        try:
            # set system/version dependent "start_new_session" analogs
            kwargs = {}
            if platform.system() == 'Windows':
                # from msdn [1]
                CREATE_NEW_PROCESS_GROUP = 0x00000200  # note: could get it from subprocess
                DETACHED_PROCESS = 0x00000008          # 0x8 | 0x200 == 0x208
                kwargs.update(creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)  
            elif sys.version_info < (3, 2):  # assume posix
                kwargs.update(preexec_fn=os.setsid)
            else:  # Python 3.2+ and Unix
                kwargs.update(start_new_session=True)
    #         p = Popen(cmd.split(' '), stdin=PIPE, stdout=PIPE, stderr=PIPE, **kwargs)
            p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, **kwargs)
            assert not p.poll()
            self.fuzz.history.add(cmd)
            self.fuzz.commands.add(cmd)
            self.quit()

        except OSError:
            #print('Error')
            self.set_error(True)


    def set_error(self,is_error):
        if is_error:
            self.sError.set('!')
        else:
            self.sError.set('')


    def callback(self,event):
        self.focus_set()


    def quit(self):
        Frame.quit(self)




# --------------------------------------------------------------------------------
# --- Main 
# --------------------------------------------------------------------------------
def main():
    import os
    script_dir=os.path.dirname(os.path.realpath(__file__))
    history  = CommandHistory(os.path.join(script_dir,'CommandHistory.txt'))
    commands = CommandList(os.path.join(script_dir,'CommandList.txt'))
    fuzz= FuzzyCommands(commands,history)
    root = Tk()
    ui = FuzzyUI(root,fuzz)
    root.mainloop()  


if __name__ == '__main__':
    main()  








