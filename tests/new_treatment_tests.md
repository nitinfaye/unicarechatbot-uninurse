#### This file contains tests to evaluate that your bot behaves as expected.

## diginurse new-treatment flow to update breakfast time
* digi_nurse_flow: Ok Digi Nurse
    - action_round
    - slot{"round": "new_treatment"}
    - action_new_treatment_flow
* affirm: Yes
    - form_changes
    - form{"name": "form_changes"}
* form: change_time: Change my breakfast time
    - slot{"change_field": "breakfast"}
* form: times: [09:00 - 10:00](time)
    - slot{"time": "09:00 - 10:00"}
* form: deny: No
    - slot{"loop": "no"}
    - form{"name": null}
    - action_deny_recommend
* deny: No
    - action_deny_recommend
    - action_restart


## diginurse new-treatment flow to update breakfast time then lunch time and then dinner time
* digi_nurse_flow: Ok Digi Nurse
    - action_round
    - slot{"round": "new_treatment"}
    - action_new_treatment_flow
* affirm: Yes
    - form_changes
    - form{"name": "form_changes"}
* form: change_time: Change my breakfast time
    - slot{"change_field": "breakfast"}
* form: times: [09:00 - 10:00](time)
    - slot{"time": "09:00 - 10:00"}
* form: deny: No
    - slot{"loop": "no"}
    - form{"name": null}
    - action_deny_recommend
* affirm: Yes
    - form_changes
    - form{"name": "form_changes"}
* form: change_time: Change my lunch time
    - slot{"change_field": "lunch"}
* form: times: [13:00 - 14:00](time)
    - slot{"time": "13:00 - 14:00"}
* form: deny: No
    - slot{"loop": "no"}
    - form{"name": null}
    - action_deny_recommend
* affirm: Yes
    - form_changes
    - form{"name": "form_changes"}
* form: change_time: Change my dinner time
    - slot{"change_field": "dinner"}
* form: times: [20:00 - 20:30](time)
    - slot{"time": "20:00 - 20:30"}
* form: deny: No
    - slot{"loop": "no"}
    - form{"name": null}
    - action_deny_recommend
* deny: No
    - action_deny_recommend
    - action_restart


## TODO ::::::::::::::::::: diginurse new-treatment flow to update breakfast time with overlap with lunch time 
