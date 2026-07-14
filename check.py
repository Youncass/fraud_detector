class Check:
    def __init__(self, detector):
        self.detector = detector
        self.df = detector.df
        self.config = detector.config
    
    def _add_risk(self, indices, score, reason):
        self.detector._add_risk(indices, score, reason)
    
    def _find_manager_column(self):
        return self.detector._find_manager_column()
    
    def run(self, columns, params=None):
        raise NotImplementedError
