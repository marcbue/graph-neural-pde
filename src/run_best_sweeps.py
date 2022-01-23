import yaml
import argparse

from greed_params import default_params, not_sweep_args, greed_run_params
from run_GNN import main

def run_best(cmd_opt, sweep, run_list, project_name, group_name, num_runs):
    if cmd_opt['run_id']:
        run_list = [cmd_opt['run_id']]
    if cmd_opt['sweep_id']:
        sweep = cmd_opt['sweep_id']

    for run in run_list:
        default_params_dict = default_params()
        greed_run_dict = greed_run_params(default_params_dict)
        greed_run_dict['use_best_params'] = False
        not_sweep_dict = not_sweep_args(greed_run_dict, project_name, group_name)

        yaml_path = f"./wandb/sweep-{sweep}/config-{run}.yaml"
        with open(yaml_path) as f:
            yaml_opt = yaml.load(f, Loader=yaml.FullLoader)
        temp_opt = {}
        for k, v in yaml_opt.items():
            if type(v) == dict:
                temp_opt[k] = v['value']
            else:
                temp_opt[k] = v
        yaml_opt = temp_opt

        opt = {**default_params_dict, **greed_run_dict, **not_sweep_dict, **yaml_opt, **cmd_opt}
        # opt = {**greed_run_dict, **not_sweep_dict, **yaml_opt, **cmd_opt}
        # loads all the needed params, eventually overiding with yaml and cmd line
        print(opt)
        if opt['run_group']:
            opt['wandb_best_run_id'] = run + "_" + str(opt['run_group'])
        else:
            opt['wandb_best_run_id'] = run

        for i in range(num_runs):
            main(opt)


def greed_runs(cmd_opt, project_name, group_name, num_runs):
    default_params_dict = default_params()
    not_sweep_dict = not_sweep_args(default_params_dict, project_name, group_name)
    opt = {**default_params_dict, **not_sweep_dict, **cmd_opt}

    opt['block'] = 'constant'
    opt['function'] = 'greed_linear_homo'
    opt['use_best_params'] = True
    opt['beltrami'] = True
    opt['pos_enc_type'] = 'GDC'

    #functional
    opt['test_omit_metric'] = False #True
    opt['test_linear_L0'] = True # flag to make the Laplacian form only dependent on embedding not time
    opt['test_grand_metric'] = True
    opt['test_tau_ones'] = True
    opt['use_mlp'] = False #True

    # redundant
    opt['test_tau_remove_tanh'] = False #True
    opt['test_tau_symmetric'] = False
    opt['test_R1R2_0'] = True

    for SLW in [0, 1]:
        opt['self_loop_weight'] = SLW
        for no_mix in [True, False]:
            opt['test_no_chanel_mix'] = no_mix
            for mu_0 in [False, True]:
                opt['test_mu_0'] = mu_0
                for stop_type in [False, True]:
                    opt['no_early'] = stop_type

                    run = f"run_NE_{stop_type}_SLW_{SLW}_nomix_{no_mix}_m0_{mu_0}"
                    opt['wandb_best_run_id'] = run
                    for i in range(num_runs):
                        main(opt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument('--tau_reg', type=int, default=2)
    # parser.add_argument('--test_mu_0', type=str, default='True')  # action='store_true')
    # parser.add_argument('--test_no_chanel_mix', type=str, default='True')  # action='store_true')
    # parser.add_argument('--test_omit_metric', type=str, default='True')  # action='store_true')
    # parser.add_argument('--test_tau_remove_tanh', type=str, default='True')  # action='store_true')
    # parser.add_argument('--test_tau_symmetric', type=str, default='True')  # action='store_true')
    # parser.add_argument('--test_tau_outside', type=str, default='True')  # action='store_true')
    parser.add_argument('--beltrami', action='store_true', help='perform diffusion beltrami style')
    parser.add_argument('--pos_enc_type', type=str, default="GDC",
                        help='positional encoder either GDC, DW64, DW128, DW256')

    parser.add_argument('--test_linear_L0', type=str, default='True')  # action='store_true')
    parser.add_argument('--test_R1R2_0', type=str, default='True')  # action='store_true')

    parser.add_argument('--function', type=str,
                        help='laplacian, transformer, greed, GAT, greed, greed_scaledDP, greed_linear', required=True)
    parser.add_argument('--sweep_id', type=str, default='', help="sweep_id for 1 best run")  # action='store_true')
    parser.add_argument('--run_id', type=str, default='', help="run_id for 1 best run")  # action='store_true')
    parser.add_argument('--run_group', type=str, default=None, help="run_id for 1 best run")  # action='store_true')

    args = parser.parse_args()
    cmd_opt = vars(args)

    sweep = 'ebq1b5hy'
    run_list = ['yv3v42ym', '7ba0jl9m', 'a60dnqcc', 'v6ln1x90', 'f5dmv6ow']
    project_name = 'grand_runs'
    group_name = 'eval'
    num_runs = 4
    # run_best(cmd_opt, sweep, run_list, project_name, group_name, num_runs)

    greed_runs(cmd_opt, project_name, group_name, num_runs)