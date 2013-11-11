from collections import defaultdict
import copy
import random
import time

from environment import Environment
import environment
import features


class TDLearningAgent(object):
    def __init__(self):
        self.environment = Environment()
        self._initialize_state()
        self.random = random.Random()
        self.Q = defaultdict(int)
        self.alpha = 0.1  # lernrate
        self.gamma = 0.8  # discount rate
        self.iterations = 0

    def _initialize_state(self):
        self.environment.reset_blocks()
        self._update_perceived_state()

    def _update_perceived_state(self):
        self.current_state = self._perceived_state()

    def run(self, episodes):
        for i in range(0, episodes):
            self._episode()
            self.iterations += 1

    def _episode(self):
        self._initialize_state()
        while not self.environment.is_game_over():
            self._step()

    def _step(self):
        action = self._choose_action()
        self.environment.execute_action(action)
        old_state = self.current_state
        self._update_perceived_state()
        reward = self._calculate_reward()
        self._q(old_state, action, reward)

    def _choose_action(self):
        actions = self._find_best_actions()
        return self.random.sample(actions, 1)[0]

    def _find_best_actions(self):
        actions = self.environment.possible_actions()
        best_actions = list(actions)
        best_value = 0
        for action in actions:
            value = self.Q[(self.current_state, action)]
            if value > best_value:
                best_value = value
                best_actions = [action]
            elif value == best_value:
                best_actions.append(action)

        return set(best_actions)

    def _q(self, old_state, action, reward):
        c = (old_state, action)

        self.Q[c] = (1 - self.alpha) * self.Q[
            c] + self.alpha * self._learned_value(reward, self.current_state)

    def _learned_value(self, reward, new_state):
        return reward + self.gamma * self._find_best_Q_value(new_state)

    def _find_best_Q_value(self, state):
        actions = self.environment.possible_actions()
        best = 0
        for action in actions:
            value = self.Q[(state, action)]
            if value > best:
                best = value

        return best

    def _perceived_state(self):
        return SimplePerceivedState(self.environment)

    def _calculate_reward(self):
        if self.environment.is_game_over():
            return -100
        return self.height_based_reward()

    def height_based_reward(self):
        highest = self.environment.highest_block_row()
        reward = 0
        if highest >= environment.BOTTOM_INDEX - 4:
            reward = 10
        elif highest >= environment.BOTTOM_INDEX - 8:
            reward = 0
        else:
            reward = -10
        return reward


class TDLearningAgentSlow(TDLearningAgent):
    def _step(self):
        TDLearningAgent._step(self)
        time.sleep(0.5)
        self.dataQ.put(1)

    def _episode(self):
        self._initialize_state()
        while (not self.stop_event.is_set() and
                   not self.environment.is_game_over()):
            self._step()


class PerceivedState(object):
    pass


class SimplePerceivedState(PerceivedState):
    def __init__(self, environment):
        self.blocks = copy.deepcopy(environment.blocks)
        self.shape = environment.current_shape


class HolePerceivedState(PerceivedState):
    def __init__(self, environment):
        self.number_holes = features.number_of_holes(environment)
