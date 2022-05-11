import nidaqmx as nq
import matplotlib.pyplot as plt
import numpy as np
import time
from encoder import Encoder


def generate_tasks():
    """
    Generate tasks for the encoder channels.

    Returns:
        list: List of tasks.
    """

    task_dir = nq.Task()
    task_dir.di_channels.add_di_chan(
        "Dev1/port0/line0:7",
        "direction",
    )

    task_dir.start()

    return task_dir


# generate tasks
direction = generate_tasks()

base_encoder = Encoder(
    channel="Dev1/ctr0",
    name='base',
    steps_per_rev=1024,
    pulses_per_rev=1440,
    positive_dir=64
)

pendulum_encoder = Encoder(
    channel="Dev1/ctr1",
    name='pendulum',
    steps_per_rev=360,
    pulses_per_rev=4096,
    positive_dir=128
)

iterations = 5000

time_values = np.zeros(iterations)
base_enc_values = np.zeros(iterations)
pendulum_enc_values = np.zeros(iterations)

start_time = time.time()

# main loop
for i in range(iterations):
    dir_value = int(direction.read())

    base_dir     = dir_value & (1 << 6)
    pendulum_dir = dir_value & (1 << 7)

    current_time = time.time()

    base_encoder.update(base_dir, current_time)
    pendulum_encoder.update(pendulum_dir, current_time)

    base_pos, base_vel = base_encoder.read()
    pendulum_pos, pendulum_vel = pendulum_encoder.read()

    time_values[i] = i
    base_enc_values[i] = base_pos
    pendulum_enc_values[i] = pendulum_pos


plt.plot(base_enc_values, label="base encoder")
plt.plot(pendulum_enc_values, label="pendulum encoder")
plt.legend(["base encoder", "pendulum encoder"])
plt.show()
