## DigiNurse flows - yes
* digi_nurse_flow
  - action_round
  - slot{"round": "configure"}
  - action_configure_flow
* affirm
  - slot{"round": "configure"}
  - action_improve_experience
> ask_configure

## DigiNurse flows - no
* digi_nurse_flow
  - action_round
  - slot{"round": "configure"}
  - action_configure_flow
* deny
  - slot{"round": "configure"}
  - action_comeback_later
  - action_restart

## New treatment flows - no
* digi_nurse_flow
  - action_round
  - slot{"round": "new_treatment"}
  - action_new_treatment_flow
* deny
  - action_recommend
> ask_change_anything

## New treatment flows - yes
* digi_nurse_flow
  - action_round
  - slot{"round": "new_treatment"}
  - action_new_treatment_flow
> ask_change_anything

## Wakeup flow
* digi_nurse_flow
  - action_round
  - slot{"round": "wake_up"}
  - action_wakeup_flow
> ask_wake_up

## Bed Time flow
* digi_nurse_flow
  - action_round
  - slot{"round": "bed_time"}
  - action_bed_time_flow

## Pre-Breakfast flow
* digi_nurse_flow
  - action_round
  - slot{"round": "pre_breakfast"}
  - action_pre_breakfast_flow
  - form_pre_post_meal
  - form{"name": "form_pre_post_meal"}
  - form{"name": null}
  - action_restart

## Post-Breakfast flow - yes
* digi_nurse_flow
  - action_round
  - slot{"round": "post_breakfast"}
  - action_post_breakfast_flow
* affirm
  - form_pre_post_meal
  - form{"name": "form_pre_post_meal"}
  - form{"name": null}
  - action_restart

## Post-Breakfast flow - no
* digi_nurse_flow
  - action_round
  - slot{"round": "post_breakfast"}
  - action_post_breakfast_flow
* deny
  - utter_remind
  - action_restart

## Pre-Lunch flow - yes
* digi_nurse_flow
  - action_round
  - slot{"round": "pre_lunch"}
  - action_pre_lunch_flow
  - form_pre_post_meal
  - form{"name": "form_pre_post_meal"}
  - form{"name": null}
  - action_restart

## Post-Lunch flow - yes
* digi_nurse_flow
  - action_round
  - slot{"round": "post_lunch"}
  - action_post_lunch_flow
* affirm
  - form_pre_post_meal
  - form{"name": "form_pre_post_meal"}
  - form{"name": null}
  - action_restart

## Post-Lunch flow - no
* digi_nurse_flow
  - action_round
  - slot{"round": "post_lunch"}
  - action_post_lunch_flow
* deny
  - utter_remind
  - action_restart

## Pre-Dinner flow
* digi_nurse_flow
  - action_round
  - slot{"round": "pre_dinner"}
  - action_pre_dinner_flow
  - form_pre_post_meal
  - form{"name": "form_pre_post_meal"}
  - form{"name": null}
  - action_restart

## Pre-Dinner flow - yes
* digi_nurse_flow
  - action_round
  - slot{"round": "post_dinner"}
  - action_post_dinner_flow
* affirm
  - form_pre_post_meal
  - form{"name": "form_pre_post_meal"}
  - form{"name": null}
  - action_restart

## Post-Dinner flow - no
* digi_nurse_flow
  - action_round
  - slot{"round": "post_dinner"}
  - action_post_dinner_flow
* deny
  - utter_remind
  - action_restart

## Pre Workout
* digi_nurse_flow
  - action_round
  - slot{"round": "pre_workout"}
  - action_pre_workout_flow
  - action_restart

# Post Workout
* digi_nurse_flow
  - action_round
  - slot{"round": "post_workout"}
  - action_post_workout_flow
> post_workout_flow

## Invalid flow 
* digi_nurse_flow
  - action_round
  - slot{"round": "invalid_flow"}
  - action_thank_you
  - action_restart

## End of Newtreatment
> ask_change_anything
* deny
  - slot{"round": "new_treatment"}
  - action_deny_recommend
  - action_restart

## New treatment :  ask if user wants to change timing or lifestyle
> ask_change_anything
* affirm
  - slot{"round": "new_treatment"}
  - action_ask_changes
> ask_change_anything

## New treatment : as per the choice of routine now change user timings and lifestyle
> ask_change_anything
* change_routine
  - action_round
  - action_change_routine
  - action_recommend
> ask_change_anything


## Affirm improve experience
> ask_configure
* affirm
  - slot{"round": "configure"}
  - utter_sleep_timings
  - form_sleep_time
  - form{"name": "form_sleep_time"}
  - form{"name": null}
  - utter_meal_timings
  - form_meal_time
  - form{"name": "form_meal_time"}
  - form{"name": null}
  - form_ask_smoke
  - form{"name": "form_ask_smoke"}
  - form{"name": null}
  - form_ask_drink
  - form{"name": "form_ask_drink"}
  - form{"name": null}
  - form_ask_workout
  - form{"name": "form_ask_workout"}
  - form{"name": null}
  - action_restart

## Deny 
> ask_configure
* deny
  - slot{"round": "configure"}
  - action_thank_you 
  - action_restart


## ask how feeling now
> ask_wake_up
* better
 - slot{"round": "wake_up"}
 - action_last_sleep_night
> last_sleep_night

## apologize feeling worst - ask doctor support
> ask_wake_up
* not_better OR worse
 - slot{"round": "wake_up"}
  - form_doctor_support
  - form{"name": "form_doctor_support"}
  - form{"name": null}
  - action_last_sleep_night
> last_sleep_night

> last_sleep_night
* all_fine OR better
 - slot{"round": "wake_up"}
  - utter_great
  - action_remind_test_followup
  - action_thank_you

> last_sleep_night
* worse
 - slot{"round": "wake_up"}
  - utter_not_great
  - action_remind_test_followup
  - action_thank_you

* change_routine
  - action_ask_changes
> ask_change_anything



## Exercise round - Affirm
> post_workout_flow
* affirm
  - slot{"round": "post_workout"}
  - action_experience_pain
* affirm
  - action_first_pain
  - slot{"first_pain": "yes"}
  - form_about_pain
  - form{"name":"form_about_pain"}
  - form{"name": null}
  - action_restart


## Exercise round - Deny Pain
> post_workout_flow
* affirm
  - slot{"round": "post_workout"}
  - action_experience_pain
* deny
  - action_rock_tomorrow
  - action_restart

## Exercise round - Affirm
> post_workout_flow
* affirm
  - slot{"round": "post_workout"}
  - action_experience_pain
* affirm
  - action_first_pain
  - slot{"first_pain": "no"}
  - action_same_pain
> asked_same_pain


## Exercise round - same pain
> asked_same_pain
* affirm
  - action_report_about_pain
  - action_restart


## Exercise round - not same pain
> asked_same_pain
* deny
  - form_about_pain
  - form{"name":"form_about_pain"}
  - form{"name": null}
  - action_restart


## Exercise round - Deny
> post_workout_flow
* deny
  - slot{"round": "post_workout"}
  - action_because_of_pain
* affirm OR deny
  - action_same_pain
* affirm
  - action_report_about_pain
  - action_restart


## Exercise round - Deny
> post_workout_flow
* deny
  - slot{"round": "post_workout"}
  - action_because_of_pain
* affirm OR deny
  - action_same_pain
* deny
  - form_about_pain
  - form{"name":"form_about_pain"}
  - form{"name": null}  
  - action_restart

## fallback story
* out_of_context
  - action_default_fallback

## say goodbye
* goodbye
  - utter_goodbye
  - action_restart

## bot challenge
* bot_challenge
  - utter_iamabot


## thanks
* thanks
  - utter_thanks
