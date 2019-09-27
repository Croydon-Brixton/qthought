import sys
import os
import warnings

# if pip install doesn't work for you, please uncomment and set to local path:
#sys.path.append(os.path.abspath('/Users/nuri/qthought/qthought')) 
#warnings.filterwarnings('ignore')

import numpy as np
from projectq.meta import Control
from projectq.ops import H, BasicGate, Measure

from qthought.interpretations.copenhagen_theory import observe
from qthought.protocol import ProtocolStep
from qthought.utils.general import readout, print_state


# TODO: Think of a way to more strongly implement the correct timing of the protocol and protocol steps. Also think
# of a way that the system can recognize if the state at two times is equivalent (i.e. if only the
# identity action was performed)

class FrauchigerRennerInit(BasicGate):
    """Gate to prepare initial state of qubit system R as
    sqrt(1/3) |0> + sqrt(2/3) |1>"""

    def __str__(self):
        return "init_R"

    @property
    def matrix(self):
        return np.matrix([[np.sqrt(1 / 3), -np.sqrt(2 / 3)],
                          [np.sqrt(2 / 3), np.sqrt(1 / 3)]])


InitR = FrauchigerRennerInit()


# Print step
# ----------------------------------------------------------
def exec_print(qsys):
    print_state(qsys['eng'])


printing_step = ProtocolStep(domain={},
                           descr='Print state',
                           time=0,
                           action=exec_print)

def print_step(i=0):
    return ProtocolStep(domain={},
                           descr='Print state',
                           time=i,
                           action=exec_print)
# Step 1: Initialize r
# ----------------------------------------------------------
def step1_action(qsys):
    InitR | qsys['r']


step1 = ProtocolStep(domain={'Qubit': ['r']},
                     descr='Initialize R',
                     time=1,
                     action=step1_action)


# Step 2: Alice observes r
# ----------------------------------------------------------
def step2_action(qsys):
    observe(qsys['Alice_memory'], qsys['r'])


step2 = ProtocolStep(domain={'AgentMemory(1)': ['Alice'],
                             'Qubit': ['r']},
                      descr='ALICE observes R',
                      time=2,
                      action=step2_action)


# Step 3: Alice makes inference
# ----------------------------------------------------------
def step3_action(qsys):
    qsys['Alice'].make_inference()


step3 = ProtocolStep(domain={'Agent(1,1)': ['Alice']},
                     descr='ALICE makes an inference',
                     time=3,
                     action=step3_action)


# Step 4: Alice prepares S
# ----------------------------------------------------------
def step4_action(qsys):
    with Control(qsys['eng'], qsys['Alice_memory']):
        H | qsys['s']


step4 = ProtocolStep(domain={'Qubit': ['s'],
                             'AgentMemory(1)': ['Alice']},
                     descr='Apply H to S controlled on ALICE_MEMORY',
                     time=4,
                     action=step4_action)


# Step 5: Bob measures S
# ----------------------------------------------------------
def step5_action(qsys):
    observe(qsys['Bob_memory'], qsys['s'])


step5 = ProtocolStep(domain={'Qubit': ['s'],
                             'AgentMemory(1)': ['Bob']},
                      descr='BOB measures S',
                      time=5,
                      action=step5_action)


# Step 6: Bob makes inference
# ----------------------------------------------------------
def step6_action(qsys):
    qsys['Bob'].make_inference()


step6 = ProtocolStep(domain={'Agent(1,1)': ['Bob']},
                     descr='BOB makes an inference',
                     time=6,
                     action=step6_action)


# Step 7: Reverse inference making in Alice
# ----------------------------------------------------------
def step7_action(qsys):
    qsys['Alice'].make_inference(reverse=True)
    observe(qsys['Alice_memory'], qsys['r'], reverse=True) #TODO: It makes differene if this is Alice or Alice_memory but should not - correct


step7 = ProtocolStep(domain={'Agent(1,1)': ['Alice']},
                      descr='Reverse Alice reasoning (Step1: in ok --> 1(R)',
                      time=7,
                      action=step7_action)


# Step 8: Hadamard on r
# ----------------------------------------------------------
def step8_action(qsys):
    H | qsys['r']


step8 = ProtocolStep(domain={'Qubit': ['r']},
                     descr='Perform Hadamard on R (Step2: in ok --> 1(R)',
                     time=8,
                     action=step8_action)


# Step 9: Ursula measures Alices lab
# ----------------------------------------------------------
def step9_action(qsys):
    observe(qsys['Ursula_memory'], qsys['r'])


step9 = ProtocolStep(domain={'Qubit': ['r'],
                             'AgentMemory(1)': ['Ursula']},
                      descr='URSULA measures ALICEs lab (i.e. r)',
                      time=9,
                      action=step9_action)


# Step 10: Ursula makes an inference
# ----------------------------------------------------------
def step10_action(qsys):
    qsys['Ursula'].make_inference()


step10 = ProtocolStep(domain={'Agent(1,1)': ['Ursula']},
                      descr='URSULA makes inference',
                      time=10,
                      action=step10_action)


# Step 11: Ursula announces her prediction
# ----------------------------------------------------------
def step11_action(qsys):
    Measure | qsys['Ursula_prediction']
    print('!Measurement made on Ursula_prediction!')
    print('Ursula prediction:', readout([qsys['Ursula_prediction']]))


step11 = ProtocolStep(domain={'Agent(1,1)': ['Ursula']},
                      descr='URSULA announces her prediction',
                      time=11,
                      action=step11_action)


# Step 12: Reverse Bob's reasoning
# ----------------------------------------------------------
def step12_action(qsys):
    qsys['Bob'].make_inference(reverse=True)
    # qsys['Bob'].observe(qsys['s'], reverse=True)
    observe(qsys['Bob_memory'], qsys['s'], reverse=True)


step12 = ProtocolStep(domain={'Agent(1,1)': ['Bob']},
                       descr='Reverse BOBs inference procedure',
                       time=12,
                       action=step12_action)


# Step 13: Apply Hadamard on s
# ----------------------------------------------------------
def step13_action(qsys):
    H | qsys['s']


step13 = ProtocolStep(domain={'Qubit': ['s']},
                      descr='Apply Hadamard on S, i.e. transform system S+BOB:  ok --> 1(s) ',
                      time=13,
                      action=step13_action)


# Step 14: Check if Bob is in ok state
# ----------------------------------------------------------
def step14_action(qsys):
    Measure | qsys['s']
    print('!Measurement made on s!')
    print('s-state:', readout([qsys['s']]))


step14 = ProtocolStep(domain={'Agent(1,1)': ['Bob']},
                      descr='Check if Bob+s is in ok state (corresponding to s: 1)',
                      time=14,
                      action=step14_action)
