import sys
sys.path.append('../')


from option2.goal_generation import GoalGenerator
from option2.history import History

history = History()
goalgenerator = GoalGenerator(history=history)
goalgenerator()
