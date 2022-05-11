import nidaqmx as nq
import matplotlib.pyplot as plt
import numpy as np
import time
from encoder import Encoder


def generate_tasks():
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

base_enc_positions = np.zeros(iterations)
pendulum_enc_positions = np.zeros(iterations)

base_enc_velocities = np.zeros(iterations)
pendulum_enc_velocities = np.zeros(iterations)

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

    base_enc_positions[i] = base_pos
    pendulum_enc_positions[i] = pendulum_pos

    base_enc_velocities[i] = base_vel
    pendulum_enc_velocities[i] = pendulum_vel

    print(f"{pendulum_pos}")


# create 2 subplots
fig, ax = plt.subplots(2, 1)

# in subplot 1 print base and pendulum angular positionis
ax[0].plot(base_enc_positions, label='base')
ax[0].plot(pendulum_enc_positions, label='pendulum')
ax[0].legend(['base', 'pendulum'])

# in subplot 2 print base and pendulum angular velocities
ax[1].plot(base_enc_velocities, label='base')
ax[1].plot(pendulum_enc_velocities, label='pendulum')
ax[1].legend(['base', 'pendulum'])

np.save('base_enc_positions', base_enc_positions)
np.save('base_enc_positions.npy', base_enc_positions)
np.save('pendulum_enc_positions.npy', pendulum_enc_positions)
np.save('base_enc_velocities.npy', base_enc_velocities)
np.save('pendulum_enc_velocities.npy', pendulum_enc_velocities)

plt.show()

base_encoder.destroy()
pendulum_encoder.destroy()
direction.stop()
