
import sys
import threading
import can
import time
import os

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

try:
    import ttk
    py3 = 0
except ImportError:
    import tkinter.ttk as ttk
    py3 = 1

import C_B_L_GUI_support

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = Tk()
    top = Real_CAN_Bus_Monitor (root)
    C_B_L_GUI_support.init(root, top)
    root.mainloop()

w = None
def create_Real_CAN_Bus_Monitor(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = Toplevel (root)
    top = Real_CAN_Bus_Monitor (w)
    C_B_L_GUI_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_Real_CAN_Bus_Monitor():
    global w
    w.destroy()
    w = None


class Real_CAN_Bus_Monitor:
    def __init__(self, top=None):
        
        self.isRunningReceiveThread = False
        self.receiveThread = None

        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85' 
        _ana2color = '#d9d9d9' # X11 color: 'gray85' 
        font10 = "-family {Courier New} -size 10 -weight normal -slant"  \
            " roman -underline 0 -overstrike 0"
        font11 = "-family {Segoe UI} -size 12 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        top.geometry("776x550+405+117")
        top.title("Real CAN Bus Monitor")
        top.configure(background="#a2a2a2")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")



        self.Frame1 = Frame(top)
        self.Frame1.place(relx=0.01, rely=0.02, relheight=0.95, relwidth=0.57)
        self.Frame1.configure(relief=GROOVE)
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief=GROOVE)
        self.Frame1.configure(background="#969696")
        self.Frame1.configure(highlightbackground="#d9d9d9")
        self.Frame1.configure(highlightcolor="black")
        self.Frame1.configure(width=445)

        self.Label1 = Label(self.Frame1)
        self.Label1.place(relx=0.31, rely=0.02, height=27, width=171)
        self.Label1.configure(activebackground="#282828")
        self.Label1.configure(activeforeground="white")
        self.Label1.configure(activeforeground="black")
        self.Label1.configure(background="#d9d9d9")
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(font=font11)
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(highlightbackground="#d9d9d9")
        self.Label1.configure(highlightcolor="black")
        self.Label1.configure(text='''Normal CAN packets''')

        self.TLabel1 = ttk.Label(self.Frame1)
        self.TLabel1.place(relx=0.02, rely=0.08, height=19, width=426)
        self.TLabel1.configure(background="#f9f9f9")
        self.TLabel1.configure(foreground="#000000")
        self.TLabel1.configure(relief=FLAT)
        self.TLabel1.configure(text='''Time            ID            DLC            DATA''')

        self.Entry2 = Text(self.Frame1)
        self.Entry2.place(relx=0.02, rely=0.13, relheight=0.86, relwidth=0.95)
        self.Entry2.configure(background="white")
        # self.Entry2.configure(disabledforeground="#a3a3a3")
        self.Entry2.configure(font=font10)
        self.Entry2.configure(foreground="#000000")
        self.Entry2.configure(insertbackground="black")
        self.Entry2.configure(width=424)

        self.Frame2 = Frame(top)
        self.Frame2.place(relx=0.59, rely=0.02, relheight=0.55, relwidth=0.37)
        self.Frame2.configure(relief=GROOVE)
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief=GROOVE)
        self.Frame2.configure(background="#d9d9d9")
        self.Frame2.configure(highlightbackground="#d9d9d9")
        self.Frame2.configure(highlightcolor="black")
        self.Frame2.configure(width=285)

        self.Button1 = Button(self.Frame2)
        self.Button1.place(relx=0.42, rely=0.1, height=24, width=112)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#d9d9d9")
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(text='''Recieve(Monitor)''')
        self.Button1.configure(command=self.onClickReceiveBtn)

        self.Button2 = Button(self.Frame2)
        self.Button2.place(relx=0.11, rely=0.69, height=24, width=95)
        self.Button2.configure(activebackground="#d9d9d9")
        self.Button2.configure(activeforeground="#000000")
        self.Button2.configure(background="#d9d9d9")
        self.Button2.configure(disabledforeground="#a3a3a3")
        self.Button2.configure(foreground="#000000")
        self.Button2.configure(highlightbackground="#d9d9d9")
        self.Button2.configure(highlightcolor="black")
        self.Button2.configure(pady="0")
        self.Button2.configure(text='''Transmit Data''')

        self.Button4 = Button(self.Frame2)
        self.Button4.place(relx=0.07, rely=0.1, height=24, width=75)
        self.Button4.configure(activebackground="#d9d9d9")
        self.Button4.configure(activeforeground="#000000")
        self.Button4.configure(background="#d9d9d9")
        self.Button4.configure(disabledforeground="#a3a3a3")
        self.Button4.configure(foreground="#000000")
        self.Button4.configure(highlightbackground="#d9d9d9")
        self.Button4.configure(highlightcolor="black")
        self.Button4.configure(pady="0")
        self.Button4.configure(text='''Set Device''')

        self.Entry1 = Entry(self.Frame2)
        self.Entry1.place(relx=0.04, rely=0.59, relheight=0.07, relwidth=0.68)
        self.Entry1.configure(background="#f8f8f8")
        self.Entry1.configure(disabledforeground="#a3a3a3")
        self.Entry1.configure(font=font10)
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(highlightbackground="#d9d9d9")
        self.Entry1.configure(highlightcolor="black")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(selectbackground="#c4c4c4")
        self.Entry1.configure(selectforeground="black")

        self.Label2 = Label(self.Frame2)
        self.Label2.place(relx=0.04, rely=0.43, height=21, width=91)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(activeforeground="black")
        self.Label2.configure(background="#d9d9d9")
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(highlightbackground="#d9d9d9")
        self.Label2.configure(highlightcolor="black")
        self.Label2.configure(text='''ID# DATA(HEX)''')

        self.Message1 = Message(self.Frame2)
        self.Message1.place(relx=0.0, rely=0.49, relheight=0.08, relwidth=0.56)
        self.Message1.configure(background="#d9d9d9")
        self.Message1.configure(foreground="#000000")
        self.Message1.configure(highlightbackground="#d9d9d9")
        self.Message1.configure(highlightcolor="black")
        self.Message1.configure(text='''ex: 250#ABCDEF123456789''')
        self.Message1.configure(width=160)

        self.Button3 = Button(self.Frame2)
        self.Button3.place(relx=0.11, rely=0.26, height=24, width=58)
        self.Button3.configure(activebackground="#d9d9d9")
        self.Button3.configure(activeforeground="#000000")
        self.Button3.configure(background="#d9d9d9")
        self.Button3.configure(disabledforeground="#a3a3a3")
        self.Button3.configure(foreground="#000000")
        self.Button3.configure(highlightbackground="#d9d9d9")
        self.Button3.configure(highlightcolor="black")
        self.Button3.configure(pady="0")
        self.Button3.configure(text='''Bit rate''')

        self.Frame3 = Frame(top)
        self.Frame3.place(relx=0.59, rely=0.58, relheight=0.39, relwidth=0.37)
        self.Frame3.configure(relief=GROOVE)
        self.Frame3.configure(borderwidth="2")
        self.Frame3.configure(relief=GROOVE)
        self.Frame3.configure(background="#969696")
        self.Frame3.configure(highlightbackground="#d9d9d9")
        self.Frame3.configure(highlightcolor="black")
        self.Frame3.configure(width=285)

        self.Label3 = Label(self.Frame3)
        self.Label3.place(relx=0.07, rely=0.05, height=27, width=208)
        self.Label3.configure(activebackground="#f9f9f9")
        self.Label3.configure(activeforeground="black")
        self.Label3.configure(background="#d9d9d9")
        self.Label3.configure(disabledforeground="#a3a3a3")
        self.Label3.configure(font=font11)
        self.Label3.configure(foreground="#000000")
        self.Label3.configure(highlightbackground="#d9d9d9")
        self.Label3.configure(highlightcolor="black")
        self.Label3.configure(text='''Monitor Diagnostic Packet''')

        self.Label4 = Label(self.Frame3)
        self.Label4.place(relx=0.07, rely=0.23, height=21, width=99)
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(activeforeground="black")
        self.Label4.configure(background="#777ae1")
        self.Label4.configure(disabledforeground="#a3a3a3")
        self.Label4.configure(foreground="#000000")
        self.Label4.configure(highlightbackground="#d9d9d9")
        self.Label4.configure(highlightcolor="black")
        self.Label4.configure(text='''Battery Voltage:''')

        self.Label6 = Label(self.Frame3)
        self.Label6.place(relx=0.07, rely=0.79, height=21, width=68)
        self.Label6.configure(activebackground="#f9f9f9")
        self.Label6.configure(activeforeground="black")
        self.Label6.configure(anchor=N)
        self.Label6.configure(background="#777ae1")
        self.Label6.configure(disabledforeground="#a3a3a3")
        self.Label6.configure(foreground="#000000")
        self.Label6.configure(highlightbackground="#d9d9d9")
        self.Label6.configure(highlightcolor="black")
        self.Label6.configure(text='''Air Temp:''')

        self.Label7 = Label(self.Frame3)
        self.Label7.place(relx=0.07, rely=0.6, height=21, width=88)
        self.Label7.configure(activebackground="#f9f9f9")
        self.Label7.configure(activeforeground="black")
        self.Label7.configure(background="#777ae1")
        self.Label7.configure(disabledforeground="#a3a3a3")
        self.Label7.configure(foreground="#000000")
        self.Label7.configure(highlightbackground="#d9d9d9")
        self.Label7.configure(highlightcolor="black")
        self.Label7.configure(text='''Colant Temp:''')

        self.Label5 = Label(self.Frame3)
        self.Label5.place(relx=0.07, rely=0.42, height=21, width=93)
        self.Label5.configure(activebackground="#f9f9f9")
        self.Label5.configure(activeforeground="black")
        self.Label5.configure(background="#777ae1")
        self.Label5.configure(disabledforeground="#a3a3a3")
        self.Label5.configure(foreground="#000000")
        self.Label5.configure(highlightbackground="#d9d9d9")
        self.Label5.configure(highlightcolor="black")
        self.Label5.configure(text='''Engine Speed :''')

        self.Message2 = Message(self.Frame3)
        self.Message2.place(relx=0.49, rely=0.23, relheight=0.11, relwidth=0.19)
        self.Message2.configure(background="#fbfbfb")
        self.Message2.configure(foreground="#000000")
        self.Message2.configure(highlightbackground="#d9d9d9")
        self.Message2.configure(highlightcolor="black")
        self.Message2.configure(width=54)

        self.Message3 = Message(self.Frame3)
        self.Message3.place(relx=0.49, rely=0.42, relheight=0.11, relwidth=0.19)
        self.Message3.configure(background="#fdfdfd")
        self.Message3.configure(foreground="#000000")
        self.Message3.configure(highlightbackground="#d9d9d9")
        self.Message3.configure(highlightcolor="black")
        self.Message3.configure(width=54)

        self.Message4 = Message(self.Frame3)
        self.Message4.place(relx=0.49, rely=0.6, relheight=0.11, relwidth=0.19)
        self.Message4.configure(background="#fdfdfd")
        self.Message4.configure(foreground="#000000")
        self.Message4.configure(highlightbackground="#d9d9d9")
        self.Message4.configure(highlightcolor="black")
        self.Message4.configure(width=54)

        self.Message5 = Message(self.Frame3)
        self.Message5.place(relx=0.49, rely=0.79, relheight=0.11, relwidth=0.19)
        self.Message5.configure(background="#ffffff")
        self.Message5.configure(foreground="#000000")
        self.Message5.configure(highlightbackground="#d9d9d9")
        self.Message5.configure(highlightcolor="black")
        self.Message5.configure(width=54)

    def receiveData(self):
        print("receiveData")
        while self.isRunningReceiveThread:

            # c = '{0:f} {1:x} {2:x} '.format(19384784.2834, 0x2932, 0x2932dd)
            # s=''
            # s +=  '{0:x} '.format(0x239ddd)
                
            # data = ' {}\n'.format(c+s)

            # self.Entry2.insert(INSERT, data)

            message = self.bus.recv()    # Wait until a message is received.
            
            c = '{0:f} {1:x} {2:x} '.format(message.timestamp, message.arbitration_id, message.dlc)
            s=''
            for i in range(message.dlc ):
                s +=  '{0:x} '.format(message.data[i])
                
            data = ' {} \n'.format(c+s)

            self.Entry2.insert(INSERT, data)

    def onClickReceiveBtn(self):

        if self.isRunningReceiveThread:
            os.system("sudo /sbin/ip link set can0 down")
        
            print("running receiveThread")
            self.Button1.configure(text="Start receiving.")
            self.isRunningReceiveThread = False

        else:
            print('\n\rCAN Rx test')
            print('Bring up CAN0....')
            os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
            time.sleep(0.1) 
            
            try:
                self.bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
            except OSError:
                print('Cannot find PiCAN board.')
                exit()
                
            print('Ready')

            print("not running receiveThread")
            self.Button1.configure(text="Stop receiving.")
            self.receiveThread = threading.Thread(name='background', target=self.receiveData)
            self.receiveThread.start()
            self.isRunningReceiveThread = True

if __name__ == '__main__':
    vp_start_gui()



