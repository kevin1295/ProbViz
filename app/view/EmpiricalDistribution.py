from .ExpWidget import expWidget

class EmpiricalDistribution(expWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EmpiricalDistribution")
        self.setWindowTitle("empiricalDistribution")
        
        