class Vessel:
    def __init__(self, idx = -1, s = 0, a = 0, p = 0, w = 0):
        # Infomation variable
        self.idx = idx # index of vessel i in list of vessels
        self.p = p # process time of vessel (time)
        self.s = s # size of vessel (length)
        self.a = a # arrival time of vessel (time)
        self.w = w # weight of vessel (priority) more and more important

        # Decision variable
        self.is_solve = False
        self.start_time = -1
        self.end_time = -1
        self.start_berth = -1
        self.end_berth = -1


    def set_solution(self, start_time, end_time, start_berth, end_berth):
        self.is_solve = True
        self.start_time = start_time
        self.end_time = end_time
        self.start_berth = start_berth
        self.end_berth = end_berth


    def __repr__(self):
        s = ""
        s += "Vessel: " + str(self.idx) + "\n"
        s += "\t*** Information variables ***\n"
        s += "\tVessel size: " + str(self.s) + "\n"
        s += "\tArrival time: " + str(self.a) + "\n"
        s += "\tProcessing time: " + str(self.p) + "\n"
        s += "\tWeight (Priority): " + str(self.w) + "\n"
       

        if self.is_solve:
            s += "\n\t*** Decision variables ***\n"
            s += "\tStart time: " + str(self.start_time) + "\n"
            s += "\tEnd time: " + str(self.end_time) + "\n"
            s += "\tStart berth: " + str(self.start_berth) + "\n"
            s += "\tEnd berth: " + str(self.end_berth) + "\n"

        return s
