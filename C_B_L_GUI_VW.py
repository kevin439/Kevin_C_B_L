
import sys
import threading
import can
import time
import os
import RPi.GPIO as GPIO
import queue

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

led = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led,GPIO.OUT)
GPIO.output(led,True)

count = 0

ENGINE_COOLANT_TEMP = 0x2D
AIR_TEMP            = 0X2E
CHAN_PARAM          = 0X740
CHAN_SETUP          = 0x200
PID_REQUEST         = 0x740
PID_REPLY           = 0x300
PID_REPLY1          = 0x201

outfile = open('log.txt','w')

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

        self.isRunningTransmitThread = False
        self.transmitThread = None

        self.isRunningDiagnosticThread = False
        self.diagnosticThread = None

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
        top.title("Kavian Real CAN Bus Monitor VW ")
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
        self.Frame2.place(relx=0.59, rely=0.02, relheight=0.45, relwidth=0.37)
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
        self.Button2.place(relx=0.04, rely=0.85, height=24, width=95)
        self.Button2.configure(activebackground="#d9d9d9")
        self.Button2.configure(activeforeground="#000000")
        self.Button2.configure(background="#d9d9d9")
        self.Button2.configure(disabledforeground="#a3a3a3")
        self.Button2.configure(foreground="#000000")
        self.Button2.configure(highlightbackground="#d9d9d9")
        self.Button2.configure(highlightcolor="black")
        self.Button2.configure(pady="0")
        self.Button2.configure(text='''Transmit Data''')
        self.Button2.configure(command=self.onClickTransmitBtn)

        self.Button4 = Button(self.Frame2)
        self.Button4.place(relx=0.04, rely=0.1, height=24, width=75)
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
        self.Entry1.place(relx=0.04, rely=0.7, height=24, relwidth=0.68)
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
        self.Label2.place(relx=0.04, rely=0.53, height=21, width=91)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(activeforeground="black")
        self.Label2.configure(background="#d9d9d9")
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(highlightbackground="#d9d9d9")
        self.Label2.configure(highlightcolor="black")
        self.Label2.configure(text='''ID# DATA(HEX)''')

        self.Message1 = Message(self.Frame2)
        self.Message1.place(relx=0.04, rely=0.59, height=21, relwidth=0.56)
        self.Message1.configure(background="#d9d9d9")
        self.Message1.configure(foreground="#000000")
        self.Message1.configure(highlightbackground="#d9d9d9")
        self.Message1.configure(highlightcolor="black")
        self.Message1.configure(text='''ex: 250#ABCDEF123456789''')
        self.Message1.configure(width=160)

        self.Button3 = Button(self.Frame2)
        self.Button3.place(relx=0.04, rely=0.26, height=24, width=58)
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
        self.Frame3.place(relx=0.59, rely=0.48, relheight=0.49, relwidth=0.37)
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
        self.Label4.place(relx=0.07, rely=0.2, height=21, width=99)
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(activeforeground="black")
        self.Label4.configure(background="#777ae1")
        self.Label4.configure(disabledforeground="#a3a3a3")
        self.Label4.configure(foreground="#000000")
        self.Label4.configure(highlightbackground="#d9d9d9")
        self.Label4.configure(highlightcolor="black")
        self.Label4.configure(text='''Battery Voltage:''')

        self.Label6 = Label(self.Frame3)
        self.Label6.place(relx=0.07, rely=0.67, height=21, width=68)
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
        self.Label7.place(relx=0.07, rely=0.51, height=21, width=88)
        self.Label7.configure(activebackground="#f9f9f9")
        self.Label7.configure(activeforeground="black")
        self.Label7.configure(background="#777ae1")
        self.Label7.configure(disabledforeground="#a3a3a3")
        self.Label7.configure(foreground="#000000")
        self.Label7.configure(highlightbackground="#d9d9d9")
        self.Label7.configure(highlightcolor="black")
        self.Label7.configure(text='''Colant Temp:''')

        self.Label5 = Label(self.Frame3)
        self.Label5.place(relx=0.07, rely=0.36, height=21, width=93)
        self.Label5.configure(activebackground="#f9f9f9")
        self.Label5.configure(activeforeground="black")
        self.Label5.configure(background="#777ae1")
        self.Label5.configure(disabledforeground="#a3a3a3")
        self.Label5.configure(foreground="#000000")
        self.Label5.configure(highlightbackground="#d9d9d9")
        self.Label5.configure(highlightcolor="black")
        self.Label5.configure(text='''Engine Speed :''')

        self.Message2 = Message(self.Frame3)
        self.Message2.place(relx=0.49, rely=0.2, relheight=0.1, relwidth=0.19)
        self.Message2.configure(background="#fbfbfb")
        self.Message2.configure(foreground="#000000")
        self.Message2.configure(highlightbackground="#d9d9d9")
        self.Message2.configure(highlightcolor="black")
        self.Message2.configure(width=54)
        self.Message2.configure(text="Voltage")

        self.Message3 = Message(self.Frame3)
        self.Message3.place(relx=0.49, rely=0.36, relheight=0.1, relwidth=0.19)
        self.Message3.configure(background="#fdfdfd")
        self.Message3.configure(foreground="#000000")
        self.Message3.configure(highlightbackground="#d9d9d9")
        self.Message3.configure(highlightcolor="black")
        self.Message3.configure(width=54)
        self.Message3.configure(text="Speed")

        self.Message4 = Message(self.Frame3)
        self.Message4.place(relx=0.49, rely=0.51, relheight=0.1, relwidth=0.19)
        self.Message4.configure(background="#fdfdfd")
        self.Message4.configure(foreground="#000000")
        self.Message4.configure(highlightbackground="#d9d9d9")
        self.Message4.configure(highlightcolor="black")
        self.Message4.configure(width=54)
        self.Message4.configure(text="Temp")

        self.Message5 = Message(self.Frame3)
        self.Message5.place(relx=0.49, rely=0.67, relheight=0.1, relwidth=0.19)
        self.Message5.configure(background="#ffffff")
        self.Message5.configure(foreground="#000000")
        self.Message5.configure(highlightbackground="#d9d9d9")
        self.Message5.configure(highlightcolor="black")
        self.Message5.configure(width=54)
        self.Message5.configure(text="Air Temp")

        self.DiagnosticBtn = Button(self.Frame3)
        self.DiagnosticBtn.place(relx=0.04, rely=0.85, height=24, relwidth=0.8)
        self.DiagnosticBtn.configure(activebackground="#d9d9d9")
        self.DiagnosticBtn.configure(activeforeground="#000000")
        self.DiagnosticBtn.configure(background="#d9d9d9")
        self.DiagnosticBtn.configure(disabledforeground="#a3a3a3")
        self.DiagnosticBtn.configure(foreground="#000000")
        self.DiagnosticBtn.configure(highlightbackground="#d9d9d9")
        self.DiagnosticBtn.configure(highlightcolor="black")
        self.DiagnosticBtn.configure(pady="0")
        self.DiagnosticBtn.configure(text='''Diagnostic VW''')
        self.DiagnosticBtn.configure(command=self.onClickDiagnosticBtn)

    def receiveData(self):
        print("receiveData")
        while self.isRunningReceiveThread:

            # c = '{0:f} {1:x} {2:x} '.format(19384784.2834, 0x2932, 0x2932dd)
            # s=''
            # s +=  '{0:x} '.format(0x239ddd)
                
            # data = ' {}\n'.format(c+s)

            # self.Entry2.insert(INSERT, data)

            message = self.bus.recv()    # Wait until a message is received.
            
            c = '{0:f} {1:X} {2:X} '.format(message.timestamp, message.arbitration_id, message.dlc)
            s=''
            for i in range(message.dlc ):
                s +=  '{0:X} '.format(message.data[i])
                
            data = ' {} \n'.format(c+s)

            self.Entry2.insert(INSERT, data)
            self.Entry2.see(END)

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
            self.receiveThread = threading.Thread(name='receiveThread', target=self.receiveData)
            self.receiveThread.start()
            self.isRunningReceiveThread = True

    def transmitData(self):
        transParamStr = self.Entry1.get()
        transParams = transParamStr.split('#')

        if len(transParams) < 2:
            return

        id = int(transParams[0], 16)
        data = bytes.fromhex(transParams[1])
        
        print(id, data)

        while self.isRunningTransmitThread:
            GPIO.output(led,True)   
            msg = can.Message(arbitration_id=id,data=data,extended_id=False)
            self.bus.send(msg)
            time.sleep(0.000000001)
            GPIO.output(led,False)
            time.sleep(0)   
            print(count)    

    def onClickTransmitBtn(self):

        if self.isRunningTransmitThread:

            GPIO.output(led,False)
            os.system("sudo /sbin/ip link set can0 down")
            print('\n\rKeyboard interrtupt')    

            self.Button2.configure(text="Start transmitting.")
            self.isRunningTransmitThread = False

        else:
            print('\n\rCAN Rx test')
            print('Bring up CAN0....')

            # Bring up can0 interface at 500kbps
            os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
            time.sleep(0)   
            print('Press CTL-C to exit')

            try:
                self.bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
            except OSError:
                print('Cannot find PiCAN board.')
                GPIO.output(led,False)
                exit()

            self.Button2.configure(text="Stop transmitting.")
            self.transmitThread = threading.Thread(name='transmitThread', target=self.transmitData)
            self.transmitThread.start()
            self.isRunningTransmitThread = True

    def diagnosticData(self):
        temperature = 0
        vol = 0
        air_temp = 0
        c = ''
        count = 0

        print("diagnosticData")

        while self.isRunningDiagnosticThread:
            print("while diagnosticData")
            message = self.q.get()
                                               
            c = '{0:f},{1:d},'.format(message.timestamp, count)
##             
            if  message.arbitration_id == PID_REQUEST  and message.dlc==5 and message.data[0]==0x12 or message.arbitration_id == PID_REPLY  and message.dlc==8 and message.data[0]==ENGINE_COOLANT_TEMP:                 
                  temperature = message.data[6] - 100 #Convert data into temperature in degree C
                  vol = message.data[3]/10 #Convert data into voltage

            elif message.arbitration_id == PID_REPLY  and message.dlc==8 and message.data[0]==AIR_TEMP:
                  air_temp = message.data[2]-100 #Convert data into air temperature

            if count>70 :
                self.Message2.configure(text=vol)
                self.Message4.configure(text=temperature)
                self.Message5.configure(text=air_temp)
                print(message.timestamp,count,  temperature  ,  vol ,  air_temp) 
                print(c,file = outfile) # Save data to file

            count +=1
##and message.arbitration_id == PID_REQUEST  and message.dlc==5 and message.data[0]==0x12 :
    def onClickDiagnosticBtn(self):

        if self.isRunningDiagnosticThread:

            self.DiagnosticBtn.configure(text="Start Diagnostic.")
            self.isRunningDiagnosticThread = False

        else:

            print('\n\rCAN Rx test')
            print('Bring up CAN0....')

            # Bring up can0 interface at 500kbps
            os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
            time.sleep(0.1) 
            print('Ready')

            try:
                    self.bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
            except OSError:
                    print('Cannot find PiCAN board.')
                    GPIO.output(led,False)
                    exit()
            
            self.q = queue.Queue()
            rx = threading.Thread(target = self.can_rx_task)  
            rx.start()
            tx = threading.Thread(target = self.can_tx_task)
            tx.start()

            self.DiagnosticBtn.configure(text="Stop Diagnostic.")
            self.diagnosticThread = threading.Thread(name='diagnosticThread', target=self.diagnosticData)
            self.isRunningDiagnosticThread = True
            self.diagnosticThread.start()

    def can_rx_task(self):  # Receive thread
        while True:
            message = self.bus.recv()
            
            if message.arbitration_id == PID_REPLY:
                self.q.put(message) # Put message into queue

    def can_tx_task(self):  # Transmit thread
                
        msg = can.Message(arbitration_id=CHAN_SETUP,data=[0x01,0xC0,0x00,0x10,0x00,0x03,0x01],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        
        msg = can.Message(arbitration_id=CHAN_PARAM,data=[0xA0,0x0F,0x8A,0xFF,0x32,0xFF],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0x10,0x00,0x02,0x1A,0x9B],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB8],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0x11,0x00,0x04,0x31,0xB8,0x00,0x00],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.168616)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xBC],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        
        
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
        self.bus.send(msg)
        time.sleep(0.1)
    
        
        while True:
            GPIO.output(led,True)
            #Sent a Engine coolant temperature request
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x12,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
    
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB0],extended_id=False)
            self.bus.send(msg)
            time.sleep(0)
    
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x13,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB4],extended_id=False)
            self.bus.send(msg)
            time.sleep(0)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x14,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB8],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x15,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xBC],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x16,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB0],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x17,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB4],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x18,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB8],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x19,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xBC],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x1A,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB0],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x1B,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB4],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x1C,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB8],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x1D,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xBC],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x1E,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB0],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x1F,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB4],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x10,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xB8],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0x11,0x00,0x02,0x21,0x04],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.179618)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xBC],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
            msg = can.Message(arbitration_id=PID_REQUEST,data=[0xA3],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.1)
    
    
            
            GPIO.output(led,False)
            time.sleep(0.5)
                                            
if __name__ == '__main__':
    vp_start_gui()



