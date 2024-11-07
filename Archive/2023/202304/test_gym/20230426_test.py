# Lunar lander : https://goodboychan.github.io/python/reinforcement_learning/pytorch/udacity/2021/05/07/DQN-LunarLander.html 참고

import gym

env = gym.make('LunarLander-v2', render_mode='human')
env.reset()

for _ in range(1000):
    for _ in range(100):
        env.render()
        action = env.action_space.sample()
        env.step(action)
    env.reset()

env.close()