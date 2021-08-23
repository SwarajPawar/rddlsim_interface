from RDDLEnv import RDDLEnv
from data.Elevators.utils import Elevators, convert_state_variables_Elevators
from data.Navigation.utils import Navigation, convert_state_variables_Navigation
from data.GameOfLife.utils import GameOfLife, convert_state_variables_GameOfLife
from data.SysAdmin.utils import SysAdmin, convert_state_variables_SysAdmin
from data.CrossingTraffic.utils import CrossingTraffic, convert_state_variables_CrossingTraffic
from data.SkillTeaching.utils import SkillTeaching, convert_state_variables_SkillTeaching

def get_env(dataset):

    if dataset == "Elevators":
        return RDDLEnv("elevators_inst_mdp__2")
    if dataset == "Navigation":
        return RDDLEnv("navigation_inst_mdp__2")
    if dataset == "GameOfLife":
        return RDDLEnv("game_of_life_inst_mdp__2")
    if dataset == "SysAdmin":
        return RDDLEnv("sysadmin_inst_mdp__2")
    if dataset == "CrossingTraffic":
        return RDDLEnv("crossing_traffic_inst_mdp__2")
    if dataset == "SkillTeaching":
        return RDDLEnv("skill_teaching_inst_mdp__2")


def get_state_for_dataset(dataset):

    if dataset == "Elevators":
        return convert_state_variables_Elevators
    if dataset == "Navigation":
        return convert_state_variables_Navigation
    if dataset == "GameOfLife":
        return convert_state_variables_GameOfLife
    if dataset == "SysAdmin":
        return convert_state_variables_SysAdmin
    if dataset == "CrossingTraffic":
        return convert_state_variables_CrossingTraffic
    if dataset == "SkillTeaching":
        return convert_state_variables_SkillTeaching


def get_sequence_for_policy(dataset):

    if dataset == "Elevators":
        return ( Elevators())
    if dataset == "Navigation":
        return ( Navigation())
    if dataset == "GameOfLife":
        return ( GameOfLife())
    if dataset == "SysAdmin":
        return ( SysAdmin())
    if dataset == "CrossingTraffic":
        return ( CrossingTraffic())
    if dataset == "SkillTeaching":
        return ( SkillTeaching())