import nidaqmx
import numpy as np
from nidaqmx.constants import EncoderType


class Encoder:
  def __init__(self, channel, name, steps_per_rev, pulses_per_rev, positive_dir):
    self._ctr_value = 0
    self._position = 0
    self._ang_position = .0
    self._last_ang_position = .0
    self._revolutions = .0

    self._last_ctr_value = self._ctr_value

    self._positive_dir = positive_dir
    self._steps_per_rev = steps_per_rev

    self.task = nidaqmx.Task()
    self.task.ci_channels.add_ci_ang_encoder_chan(
      channel,
      name,
      decoding_type=EncoderType.TWO_PULSE_COUNTING,
      pulses_per_rev=pulses_per_rev
    )

    self.task.start()

  def update(self, direction):
    self._last_ctr_value = self._ctr_value
    self._ctr_value = self.task.read()

    delta_ctr = (self._ctr_value - self._last_ctr_value)

    if direction == self._positive_dir:
      self._position += delta_ctr
    else:
      self._position -= delta_ctr

    self._revolutions = self._position / self._steps_per_rev

    self._last_ang_position = self._ang_position
    self._ang_position = self._revolutions * 2 * np.pi

    return self.read()

  def read(self, radians=True):
    if radians:
      return self._ang_position
    else:
      return np.rad2deg(self._ang_position)

  def destroy(self):
    self.task.stop()
