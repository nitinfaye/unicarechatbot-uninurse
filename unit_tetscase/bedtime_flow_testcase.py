from unit_testcase_utils import *


class Bedtime_Flow_Testcases(UnitTestcase):
    def __init__(self, chat, *args, **kwargs):
        super().__init__(chat, *args, **kwargs)
        self.flow = 'bed_time'
        self.end_of_chats = ["EOC",
            "Thanks Test! I have recorded your responses in your medical data logger"
            ]


class Bedtime_Flow_TestsContainer(TestsContainer):
    pass
