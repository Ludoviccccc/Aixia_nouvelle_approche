class DistanceMethod:
    def __init__(self,method):
        self.method = method
    def __call__(self,goal,features):
        return self.method(goal,features)
