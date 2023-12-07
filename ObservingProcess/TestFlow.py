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

seq1 = {"Pointer":F1, "Centrer":F1, "Guider":F2, "Acquisition":F3, "Flat":F4, "Dark":F5}

class ProcessObs:
    
    def __init__(self, seq):
        self.seq = seq
        self.err = "OK"
        self.ix = 'none'
        self.X = threading.Thread(target = self.thr_func)
    
    def thr_func(self):
        for step in self.seq:
            if self.err == "OK":
                self.ix = step
                self.err = self.seq[step]()
            else :
                print("BUG")
    
    def run(self):
        if self.X.is_alive() == False:
            self.X.start()
            return "Processus démarré"
        else :
            return "Le process tourne déjà"
    
    def state(self):
        if self.X.is_alive():
            return self.X.is_alive(), str(self.ix)
        else:
            return self.X.is_alive(), "Not running"

app = FastAPI()

@app.get('/state')
async def get_state():
    return A.state()

@app.get('/run')
async def get_state():
    return A.run()

if __name__ == "__main__":
    print("On démarre")
    A = ProcessObs(seq1)
    # ~ A.run()
    uvicorn.run(app, host="0.0.0.0", port=1235)

    # ~ for i in range(10) :
        # ~ print("Etape en cours : ", A.state())
        # ~ time.sleep(2)
