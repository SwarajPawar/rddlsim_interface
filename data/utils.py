from RDDLEnv import RDDLEnv
from data.Elevators.utils import Elevators, convert_state_variables_Elevators
from data.Navigation.utils import Navigation, convert_state_variables_Navigation
from data.GameOfLife.utils import GameOfLife, convert_state_variables_GameOfLife

def get_env(dataset):

    if dataset == "Elevators":
        return RDDLEnv("elevators_inst_mdp__2")
    if dataset == "Navigation":
        return RDDLEnv("navigation_inst_mdp__2")
    if dataset == "GameOfLife":
        return RDDLEnv("game_of_life_inst_mdp__2")


def get_state_for_dataset(dataset):

    if dataset == "Elevators":
        return convert_state_variables_Elevators
    if dataset == "Navigation":
        return convert_state_variables_Navigation
    if dataset == "GameOfLife":
        return convert_state_variables_GameOfLife


def get_sequence_for_policy(dataset):

    if dataset == "Elevators":
        return ( Elevators())
    if dataset == "Navigation":
        return ( Navigation())
    if dataset == "GameOfLife":
        return ( GameOfLife())