import time
import threading
from fastapi import FastAPI
import uvicorn

def F1():
    print("F1 - début")
    time.sleep(3)
    print("F1 - fin")
    return "OK"

def F2():
    print("F2 - début")
    time.sleep(3)
    print("F2 - fin")
    return "OK"

def F3():
    print("F3 - début")
    time.sleep(3)
    print("F3 - fin")
    return "OK"

def F4():
    print("F4 - début")
    time.sleep(3)
    print("F4 - fin")
    return "OK"

def F5():
    print("F5 - début")
    time.sleep(3)
    print("F5 - fin")
    return "OK"

sequence = {
'main':{"Pointage":F1, "Centrage":F1, "Guidage":F2, "Acquisition":F3, "Flat":F4, "Dark":F5},
'seq1':{"Pointer":F1, "Centrer":F2, "Acquisition":F3},
'seq2':{"Guider":F2, "Acquisition":F3, "Flat":F4, "Dark":F5}
}

class ProcessObs:
    
    def __init__(self, seq):
        self.seq = seq
        self.err = "OK"
        self.ix = 'none'
        self.stop = False
        self.X = threading.Thread(target = self.observing_process_thread)
        self.X.start()
    
    def observing_process_thread(self):
        for step in self.seq:
            if self.stop == True:
                print("Process interrompu")
                break
            if self.err == "OK":
                self.ix = step
                self.err = self.seq[step]()
            else :
                print("BUG")
                break
    
    def stop_process(self, message_stop):
        self.stop = True
        print("Interruption du process : ", message_stop)

def ObsProcessRun(process):
    global A
    if 'A' in globals() and A.X.is_alive() == True:
        return "Le process tourne déjà"
    else:
        if process in sequence.keys():
            A = ProcessObs(sequence[process])
            reply = "Processus démarré : " + process
            return reply
        else:
            return "Processus inconnu"

def ObsProcessStop(message_stop):
    global A
    if 'A' in globals() and A.X.is_alive() == True:
        A.stop_process(message_stop)
        return True
    else:
        print("The process is not running")
        return False
        
def ObsState():
    global A
    if 'A' in globals():
        if A.X.is_alive():
            return A.X.is_alive(), str(A.ix)
        else:
            return False, "Not running"
    else:
        return False, "Not running"

app = FastAPI()

@app.get("/state")
async def get_state():
    return ObsState()

@app.get("/run/{process}")
async def get_run(process):
    return ObsProcessRun(process)

@app.get("/stop/{message_stop}")
async def get_stop(message_stop):
    ObsProcessStop(message_stop)
    return True

if __name__ == "__main__":
    print("On démarre")
    uvicorn.run("TestFlow:app", host="0.0.0.0", port=1235, reload=True)
