#ifndef RDDL_INSTANCE_H
#define RDDL_INSTANCE_H

struct RDDLInstance {
    int num_state_vars;
    int num_action_vars;
    int num_enum_actions;
    int horizon;
    int num_rounds;
    double remaining_time;
    int* initial_state;
    double min_reward;
    double max_reward;
};

#endif
