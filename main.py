import time

import nidaqmx as nq

from encoder import Encoder


def generate_tasks():
  task_dir = nq.Task()
  task_dir.di_channels.add_di_chan(
    "Dev1/port0/line0:7",
    "direction",
  )

  task_dir.start()

  return task_dir


def destroy_tasks(tasks):
  for task in tasks:
    task.stop()


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

# main loop
while True:
  dir_value = int(direction.read())

  base_dir = dir_value & (1 << 6)
  pendulum_dir = dir_value & (1 << 7)

  current_time = time.time()

  base_pos = base_encoder.update(base_dir)
  pendulum_pos = pendulum_encoder.update(pendulum_dir)

  print(f"{base_pos}, {pendulum_pos}")
