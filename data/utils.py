from RDDLEnv import RDDLEnv
from data.Elevators.utils import Elevators, convert_state_variables_Elevators


def get_env(dataset):

    if dataset == "Elevators":
        return RDDLEnv("elevators_inst_mdp__2")


def get_state_for_dataset(dataset):

    if dataset == "Elevators":
        return convert_state_variables_Elevators


def get_sequence_for_policy(dataset):

    if dataset == "Elevators":
        return (new Elevators())