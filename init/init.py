import usb.core
from time import sleep


class BitPattern(object):
    
    __slots__ = ['arm', 'base', 'led']

    def __init__(self, arm, base, led):
        self.arm = arm
        self.base = base
        self.led = led

    def __iter__(self):
        return iter([self.arm, self.base, self.led])

    def __getitem__(self, item):
        return [self.arm, self.base, self.led][item]

    def __or__(self, other):
        return BitPattern(self.arm | other.arm,
                          self.base | other.base,
                          self.led | other.led)
    
    def __eq__(self, other):
        return self.arm == other.arm and self.base == other.base and self.led == other.led

    def __repr__(self):
        return "<BitPattern arm:%s base:%s led:%s>" % (self.arm, self.base, self.led)

    def __str__(self):
        return self.__repr__()    

GripsClose =       BitPattern(1, 0, 0)
CloseGrips =       GripsClose
GripsOpen =        BitPattern(2, 0, 0)
OpenGrips =        GripsOpen
Stop =             BitPattern(0, 0, 0)
WristUp =          BitPattern(0x4, 0, 0)
WristDown =        BitPattern(0x8, 0, 0)
ElbowUp =          BitPattern(0x10, 0, 0)
ElbowDown =        BitPattern(0x20, 0, 0)
ShoulderUp =       BitPattern(0x40, 0, 0)
ShoulderDown =     BitPattern(0x80, 0, 0)
BaseClockWise =    BitPattern(0, 1, 0)
BaseCtrClockWise = BitPattern(0, 2, 0)
LedOn =            BitPattern(0, 0, 1)


class Arm(object):
    
    __slots__ = ['dev']

    def __init__(self):
        self.dev = usb.core.find(idVendor=0x1267)
        self.dev.set_configuration()

    def tell(self, msg):
        
        self.dev.ctrl_transfer(0x40, 6, 0x100, 0, msg)

    def safe_tell(self, fn):
        
		
		
        try:
            fn()
        except:
            self.tell(Stop)
            raise

    def move(self, pattern, time=1):
      
        try:
        	self.tell(pattern)
        	sleep(time)
        finally:
        	self.tell(Stop)

    def doActions(self, actions):
        
		
        #Validate
        for action in actions:
            if not 1 <= len(action) <= 2:
                raise ValueError("Wrong number of parameters in action %s" %
                                 (repr(action)))
            if not isinstance(action[0], BitPattern):
                raise ValueError("Not a valid action")
        #Do
        for action in actions:
            if len(action) == 2:
                time = action[1]
            else:
                time = 1
            self.move(action[0], time)

def makeGrabAndMove(baseDir):
	return [[CloseGrips, 1.1],
                [ShoulderUp | ElbowUp | WristDown | baseDir],
                [baseDir, 8.5],
                [ShoulderDown | ElbowDown | WristUp | baseDir],
                [OpenGrips]]

blink = [[LedOn, 0.5], [Stop, 0.5]] * 3
block_left = makeGrabAndMove(BaseClockWise) + blink
block_right = makeGrabAndMove(BaseCtrClockWise) + blink
