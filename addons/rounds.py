from rasa.core.slots import Slot
from actions.action_utils import rounds


class Rounds(Slot):

    def feature_dimensionality(self):
        return len(rounds)

    # def as_feature(self):
    #     r = [0.0] * self.feature_dimensionality()
    #     if self.value == "configure":
    #         r[0] = 1.0
    #     elif self.value == "new_treatment":
    #         r[1] = 1.0
    #     elif self.value == "wake_up":
    #         r[2] = 1.0
    #     elif self.value == "exercise":
    #         r[3] = 1.0
    #     elif self.value == "bed_time":
    #         r[4] = 1.0
    #     elif self.value == "midday_round":
    #         r[5] = 1.0
    #     return r

    def as_feature(self):
        r = [0.0] * self.feature_dimensionality()
        for i, v in enumerate(rounds):
            if self.value == v:
                r[i] = 1.0
        # print(f" as_feature = {r}")
        return r
