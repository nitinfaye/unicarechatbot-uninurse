#### This file contains tests to evaluate that your bot behaves as expected.

## diginurse configure left tree
* digi_nurse_flow: Ok Digi Nurse
    - action_round
    - slot{"round": "configure"}
    - action_configure_flow
* deny: No you don't
    - action_comeback_later
    - action_restart

## diginurse configure right tree
* digi_nurse_flow: Ok Digi Nurse
    - action_round
    - slot{"round": "configure"}
    - action_configure_flow
* affirm: yes
    - action_improve_experience
* deny: No you don't
    - action_thank_you
    - action_restart

## diginurse configure right tree - No
* digi_nurse_flow: Ok Digi Nurse
    - action_round
    - slot{"round": "configure"}
    - action_configure_flow
* affirm: yes
    - action_improve_experience
* deny: No you don't
    - action_thank_you
    - action_restart

## diginurse configure right tree - Yes
* digi_nurse_flow: Ok Digi Nurse
    - action_round
    - slot{"round": "configure"}
    - action_configure_flow
* affirm: yes
    - action_improve_experience
* affirm: yes you have
    - utter_sleep_timings
    - form_sleep_time
    - form{"name": "form_sleep_time"}
* form: times: [7:00 - 8:00](time)
* form: times: [21:00 - 22:00](time)
    - slot{"sleep_time": "21:00 - 22:00"}
    - slot{"wakeup_time": "7:00 - 8:00"}
    - form{"name": null}
    - utter_meal_timings
    - form_meal_time
    - form{"name": "form_meal_time"}
* form: times: [9:00 - 10:00](time)
* form: times: [13:00 - 14:00](time)
* form: times: [20:00 - 20:30](time)
    - slot{"breakfast_time": "21:00 - 22:00"}
    - slot{"lunch_time": "21:00 - 22:00"}
    - slot{"dinner_time": "20:00 - 20:30"}
    - form{"name": null}
    - form_ask_smoke
    - form{"name": "form_ask_smoke"}
* form: affirm: Yes, I smoke
* form: how_often: Daily
    - slot{"smoking": "Yes"}
    - slot{"smoke_freq": "Daily"}
    - form{"name": null}
    - form_ask_drink
    - form{"name": "form_ask_drink"}
* form: affirm: Yes, I smoke
* form: how_often: Daily
    - slot{"drinking": "Yes"}
    - slot{"drink_freq": "Daily"}
    - form{"name": null}
    - form_ask_workout
    - form{"name": "form_ask_workout"}
* form: deny: No, i dont do workout
    - slot{"workingout": "No"}
    - slot{"workout_freq": "No"}
    - slot{"intence": "No"}
    - form{"name": null}
    - action_restart

