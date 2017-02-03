import numpy as np
import tensorflow as tf
from keras.models import *
from keras.layers import *

TAU = 0.001

class DDPG:
    def __init__(self, state_shape, action_dim):
        sess = tf.Session()
        self.actor = Actor(sess, state_shape, action_dim)
        self.critic = Critic(sess, state_shape, action_dim)

    def fit(self, states, actions, rewards, nstates, over):
        gradients = self.critic.get_gradients(states, actions)
        self.actor._train(states, gradients)

        targets = self.critic.get_rewards(states, actions)
        nrewards = self.critic.get_rewards(nstates, self.actor.get_actions(nstates))
        for i in range(states.shape[0]):
            if over[i]: targets[i] = rewards[i]
            else: targets[i] = rewards[i] + 0.7 * nrewards[i]
        history = self.critic._train(states, actions, targets)

        self.actor._update()
        self.critic._update()
        return history

    def get_actions(self, states):
        return self.actor.get_actions(states)

class Actor:

    def __init__(self, sess, state_shape, action_dim):
        self.sess = sess
        K.set_session(sess)

        def make_model():
            state = Input(shape=state_shape)

            conv = Convolution2D(16, 3, 3, subsample=(2, 2), activation='relu')(state)
            conv = Convolution2D(32, 3, 3, subsample=(2, 2), activation='relu')(conv)
            conv = Convolution2D(64, 3, 3, subsample=(2, 2), activation='relu')(conv)
            flat = Flatten()(conv)

            action = Dense(256, activation='relu')(flat)
            action = Dense(action_dim, activation='tanh')(action)
            model = Model(input=state, output=action)
            parameter = model.trainable_weights
            return model, state, action, parameter

        self.target_model, _, _, _ = make_model()
        model, state, action, parameter = make_model()
        self.model = model
        self.state = state

        action_gradient = tf.placeholder(tf.float32, [None, action_dim])
        parameter_gradient = tf.gradients(action, parameter, -action_gradient)
        optimize = tf.train.AdamOptimizer().apply_gradients(zip(parameter_gradient, parameter))
        self.optimize = optimize
        self.action_gradient = action_gradient

        sess.run(tf.global_variables_initializer())

    def _train(self, states, gradients):
        self.sess.run(self.optimize, feed_dict={
            self.state: states,
            self.action_gradient: gradients
        })

    def _update(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(weights)):
            target_weights[i] = TAU * weights[i] + (1 - TAU)* target_weights[i]
        self.target_model.set_weights(target_weights)

    def get_actions(self, states):
        return self.target_model.predict(states)

class Critic:

    def __init__(self, sess, state_shape, action_dim):
        self.sess = sess
        K.set_session(sess)

        def make_model():
            state = Input(shape=state_shape)
            action = Input(shape=[action_dim])

            conv = Convolution2D(16, 3, 3, subsample=(2, 2), activation='relu')(state)
            conv = Convolution2D(32, 3, 3, subsample=(2, 2), activation='relu')(conv)
            conv = Convolution2D(64, 3, 3, subsample=(2, 2), activation='relu')(conv)
            flat = Flatten()(conv)

            reward = merge([flat, action], mode='concat')
            reward = Dense(256, activation='relu')(reward)
            reward = Dense(1)(reward)
            model = Model(input=[state, action], output=reward)
            model.compile(loss='mse', optimizer='adam')
            return model, state, action

        self.target_model, _, _ = make_model()
        model, state, action = make_model()
        self.model = model
        self.state = state
        self.action = action

        self.action_gradient = tf.gradients(model.output, action)
        self.sess.run(tf.global_variables_initializer())

    def _train(self, states, actions, targets):
        return self.model.fit([states, actions], targets, nb_epoch=1, verbose=False)

    def _update(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(weights)):
            target_weights[i] = TAU * weights[i] + (1 - TAU) * target_weights[i]
        self.target_model.set_weights(target_weights)

    def get_rewards(self, states, actions):
        return self.target_model.predict([states, actions])

    def get_gradients(self, states, actions):
        return self.sess.run(self.action_gradient, feed_dict={
            self.state: states,
            self.action: actions
        })[0]
