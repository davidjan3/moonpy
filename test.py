import random
import tensorflow as tf

model = tf.keras.models.Sequential(
    [
        tf.keras.layers.Input(shape=(2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(8, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(4, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(1, activation=tf.keras.activations.tanh),
    ]
)

x_train = []
y_train = []

for i in range(100):
    choice = random.choice([1, 2, 3, 4])
    x00 = x01 = x10 = x11 = 0
    y = 0
    if choice == 1:
        x00 = random.uniform(-0.6, 0.6)
        x01 = x00 + random.uniform(0.01, 0.2)
        x10 = x00 + random.uniform(-0.2, 0.2)
        x11 = x10 + random.uniform(0.01, 0.2)
        y = 0
    elif choice == 2:
        x00 = random.uniform(-0.6, 0.6)
        x01 = x00 - random.uniform(0.01, 0.2)
        x10 = x00 + random.uniform(-0.2, 0.2)
        x11 = x10 - random.uniform(0.01, 0.2)
        y = 0
    elif choice == 3:
        x00 = random.uniform(-0.6, 0.6)
        x01 = x00 - random.uniform(0.01, 0.2)
        x10 = x00 + random.uniform(-0.2, 0.2)
        x11 = x10 + random.uniform(0.01, 0.2)
        y = 1
    elif choice == 4:
        x00 = random.uniform(-0.6, 0.6)
        x01 = x00 + random.uniform(0.01, 0.2)
        x10 = x00 + random.uniform(-0.2, 0.2)
        x11 = x10 - random.uniform(0.01, 0.2)
        y = -1
    # x00 = (x00 + 1) * 0.5
    # x01 = (x01 + 1) * 0.5
    # x10 = (x10 + 1) * 0.5
    # x11 = (x11 + 1) * 0.5
    x_train.append([[x00, x01], [x10, x11]])
    y_train.append(y)

# print(x_train, y_train)

model.compile(
    optimizer=tf.keras.optimizers.RMSprop(0.05),
    loss=tf.keras.losses.MeanAbsoluteError(),
)

model.fit(x_train, y_train, epochs=100)

x_test = [
    [[0.5, 0.6], [0.4, 0.5]],
    [[-0.2, -0.3], [-0.1, 0.0]],
    [[0.4, 0.5], [0.6, 0.45]],
    [[0.2, 0.1], [0.1, 0.0]],
]

y_test = [0, 1, -1, 0]

model.evaluate(x_test, y_test, verbose=2)
print(model.predict(x_test))
