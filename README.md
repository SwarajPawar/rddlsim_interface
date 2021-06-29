## RL-LAB
   [Part of Summer School](http://icaps18.icaps-conference.org/summerschool)

### Installation
   1. Install  [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
   2. Install [Vagrant](https://www.vagrantup.com/downloads.html)
   3. Create a new directory (eg. ```summer_school```) and place the  [Vagrantfile](http://icaps18.icaps-conference.org/fileadmin/alg/conferences/icaps18/summerschool/labs/Vagrantfile) in it. Rename it to just Vagrantfile (without .dms)
   For more info, Please refer to : [Summer School - Lab Materials](http://icaps18.icaps-conference.org/summerschool/labmaterial)

### Usage:
* Start the VM:
    * Open a new terminal and change directory to ```summer_school```
    * Run command ```vagrant up```  to set up and boot the virtual machine.
    For more details; visit :  https://www.vagrantup.com/intro/getting-started/up.html
* Start the RDDL Server
    * Open a new terminal and change directory to ```summer_school```
    * SSH to VM : ```vagrant ssh```
    * Change directory: ```cd /vagrant/RDDLSim```
    * Run command:

        ```./run rddl.competition.Server /vagrant/RL/env/wildfire```

        OR

        ```./run rddl.competition.Server /vagrant/RL/env/wildfire_single_action```    _(Easier)_

        (if using this command; please change all ---inst name accordingly in further instructions)

* Algorithms:
    * Open a new terminal and change directory to ```summer_school```
    * SSH to VM: ```vagrant ssh```
    * Change directory: ```cd /vagrant/RL```
    * #### Q-Learning :
        * Arguments info : ```python3 q_learning.py --help```
        * Training Example: ```python3 q_learning.py --inst wildfire_inst_mdp__1 --scratch --eps 0.3 --norm_reward --path_suffix "normalized"```
        * Test Example: ```python3 q_learning.py --inst wildfire_inst_mdp__1  --path_suffix "normalized"``` _(Notice: We don't use --scratch so that it can load previously saved model)_
    * #### Q-Learning with Experience Replay :
        * Arguments info : ```python3 q_learning_exp_replay.py --help```
        * Example: ```python3 q_learning_exp_replay.py --inst wildfire_inst_mdp__1 --scratch --eps 0.3 --norm_reward --path_suffix "normalized" --batch_size 32 --capacity 100```
    * #### Advantage Actor Critic  (A2C):
         * Arguments info : ```python3 main_a2c.py --help```
        * Example: ```python3 main_a2c.py --env "wildfire_inst_mdp__1"```

    _(Results are stored in the current working directory)_

* Run command ```exit``` to close the two ssh sessions

* Run command ```vagrant halt``` to shutdown the VM
