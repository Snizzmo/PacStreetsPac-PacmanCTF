# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint

"""
Useful items in util: 
Stack, queue, priority queue, priority queue with functions (we must define functions)
manhattanDistance, Counter (keeps track of counts for a set of keys)
"""
"""
Useful items in capture:
getLegalActions, generateSuccessors, getAgentState, getAgentPosition, getNumAgents
getScore, getRedFood, getBlueFood, getRedCapsules, getBlueCapsules, getWalls, hasFood, hasWall
getRedTeamIndices, getBlueTeamIndices, isOnRedTeam, getAgentDistances, getInitialAgentPosition, getCapsules
"""
#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'CenterAgent', second = 'DummyAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)

class ReflexCaptureAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class CenterAgent(ReflexCaptureAgent): 
  def __init__(self, index):
    CaptureAgent.__init__(self, index)
    self.target = None    

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.setCenter(gameState)

  def setCenter(self, gameState):
    centerX = (gameState.data.layout.width - 2) / 2
    if not self.red: 
      centerX += 1
    self.defaultPos = []

    for y in range(1, gameState.data.layout.height -1):
      #print(gameState.hasWall(centerX, 4))
      if not gameState.hasWall(centerX, y):
        self.defaultPos.append((centerX, y))
      #if gameState.hasWall(centerX, y): 
        #print(centerX, y, "has a wall")

    for y in range(len(self.defaultPos)):
      if len(self.defaultPos) > 2: 
        self.defaultPos.remove(self.defaultPos[0])
        self.defaultPos.remove(self.defaultPos[-1])
    # print(self.defaultPos)
    self.target = self.defaultPos[0] #Set the target 
    #Target is self.target = (#, #)

  def chooseAction(self, gameState):
    noPacActions = []
    actions = gameState.getLegalActions(self.index)
    # pos = gameState.getAgentPosition(self.index)
    
    # if pos == self.target: 
    #   self.target = None

    for a in actions: 
      newState = gameState.generateSuccessor(self.index, a)
      if not newState.getAgentState(self.index).isPacman: 
        noPacActions.append(a)
    # noPacActions.remove('Stop')
    centerX = (gameState.data.layout.width - 2) / 2
    enemy1pos = gameState.getAgentPosition((self.index+1) % 4)
    enemy2pos = gameState.getAgentPosition((self.index+3) % 4)
#logic for mirroring
    if self.red:
      if (gameState.getAgentPosition(self.index)[0] <= centerX) and (gameState.getAgentPosition(self.index)[0] > (gameState.data.layout.width / 2) - (gameState.data.layout.width / 8)):
        #print("corect eighth")
        mirrorX = ((enemy1pos[0] + enemy2pos[0]) / 2) #make this the nearest X that is less than 1/2 width that is not hasWall
        mirrorY = ((enemy1pos[1] + enemy2pos[1]) / 2)
        print("mirror")
        if (gameState.hasWall(mirrorX, mirrorY)): 
          #check +1 and -1 to both x and y
          if not gameState.hasWall(mirrorX-1, mirrorY): 
            self.target = (mirrorX-1, mirrorY)
          elif not gameState.hasWall(mirrorX-1, mirrorY-1): 
            self.target = (mirrorX-1, mirrorY-1)
          elif not gameState.hasWall(mirrorX, mirrorY-1): 
            self.target = (mirrorX, mirrorY-1)
          # pick closest on tie
        else: 
          self.target = (mirrorX, mirrorY)

  # Simple chasing defense  
    #if we red
    if self.red: 
      if enemy1pos[0] <= centerX: 
        self.target = enemy1pos
      elif enemy2pos[0] <= centerX: 
        self.target = enemy2pos
      else: 
        self.setCenter(gameState)
    #if we blue
    else: 
      if enemy1pos[0] >= centerX: 
        self.target = enemy1pos
      elif enemy2pos[0] >= centerX: 
        self.setCenter(gameState)
    
    
    # print enemy1pos
    # print enemy2pos


    fvalues = []
    for a in noPacActions: 
      nextState = gameState.generateSuccessor(self.index, a)
      newpos = nextState.getAgentPosition(self.index)
      fvalues.append(self.getMazeDistance(newpos, self.target))
    best = min(fvalues)
    bestActions = [a for a, v in zip(noPacActions, fvalues) if v == best]
    bestAction = random.choice(bestActions)
    return(bestAction) 

class AttackAgent(ReflexCaptureAgent): 
  def __init__(self, index):
    CaptureAgent.__init__(self, index)
    self.target = None    

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.setCenter(gameState)

  def setCenter(self, gameState):
    centerX = (gameState.data.layout.width - 2) / 2
    if not self.red: 
      centerX += 1
    self.defaultPos = []

    for y in range(1, gameState.data.layout.height -1):
      print(gameState.hasWall(centerX, 4))
      if not gameState.hasWall(centerX, y):
        self.defaultPos.append((centerX, y))
      if gameState.hasWall(centerX, y): 
        print(centerX, y, "has a wall")

    for y in range(len(self.defaultPos)):
      if len(self.defaultPos) > 2: 
        self.defaultPos.remove(self.defaultPos[0])
        self.defaultPos.remove(self.defaultPos[-1])
    # print(self.defaultPos)
    self.target = self.defaultPos[0] #Set the target 
    #Target is self.target = (#, #)

  def chooseAction(self, gameState):
    noPacActions = []
    actions = gameState.getLegalActions(self.index)
    pos = gameState.getAgentPosition(self.index)
    
    # if pos == self.target: 
    #   self.target = None

    for a in actions: 
      newState = gameState.generateSuccessor(self.index, a)
      if not newState.getAgentState(self.index).isPacman: 
        noPacActions.append(a)

    # noPacActions.remove('Stop')

    fvalues = []
    for a in noPacActions: 
      nextState = gameState.generateSuccessor(self.index, a)
      newpos = nextState.getAgentPosition(self.index)
      fvalues.append(self.getMazeDistance(newpos, self.target))

    best = min(fvalues)
    bestActions = [a for a, v in zip(noPacActions, fvalues) if v == best]
    bestAction = random.choice(bestActions)
    return(bestAction) 