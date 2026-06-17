class DistanceMethod:
    def __init__(self,method,weights=None):
        self.method = method
        self.weights = weights
    def __call__(self,goal,features,weights=None):
        if weights==None:
            return self.method(goal,features,self.weights)
        else:
            return self.method(goal,features,weights)
