import synthetic_adversarial_experiment as exp
import numpy as np 
import random
import torch

#hyperparameters to iterate through 
adv_lambda_params = [1., 2., 3., 4., 5.]
adv_hyp_encoder_lambda_params = [1., 2., 3., 4., 5.]
nli_net_adv_hyp_encoder_lambda_params = [0.0]
random_premise_frac_params = [0.0]

def run_experiment():

    #columns of the results csv file 
    adv_lambda_column = ['adv_lambda']
    adv_hyp_encoder_lambda_column = ['adv_hyp_encoder_lambda']
    nli_net_adv_hyp_encoder_lambda_column = ['nli_net_adv_hyp_encoder_lambda']
    random_premise_frac_column = ['random_premise_frac']
    nli_train_column = ['nli_train']
    hyp_train_column = ['hyp_train']
    nli_test_column = ['nli_test']
    hyp_test_column = ['hyp_test']
    
    #iterate through hyperparameters 
    args = exp.get_args()
    
    for c in adv_lambda_params:
        for d in adv_hyp_encoder_lambda_params:
            for e in nli_net_adv_hyp_encoder_lambda_params:
                for f in random_premise_frac_params:

                    #update the hyperparameters on each iteration  
                    args.adv_lambda = c 
                    args.adv_hyp_encoder_lambda = d
                    args.nli_net_adv_hyp_encoder_lambda = e 
                    args.random_premise_frac = f 
                            
                    seed = 1
                    random.seed(seed)
                    np.random.seed(seed)
                    torch.manual_seed(seed)

                    #run the experiment with specified hyperparameters
                    eval_acc_nli_train, eval_acc_hypoth_train, eval_acc_nli, eval_acc_hypoth = exp.main(args)

                    #attach results to lists 
                    adv_lambda_column.append(args.adv_lambda)
                    adv_hyp_encoder_lambda_column.append(args.adv_hyp_encoder_lambda)
                    nli_net_adv_hyp_encoder_lambda_column.append(args.nli_net_adv_hyp_encoder_lambda)
                    random_premise_frac_column.append(args.random_premise_frac)
                    nli_train_column.append(eval_acc_nli_train)
                    hyp_train_column.append(eval_acc_hypoth_train)
                    nli_test_column.append(eval_acc_nli)
                    hyp_test_column.append(eval_acc_hypoth)

    np.savetxt('synthetic_experiment_results.csv', [p for p in zip(adv_lambda_column, 
    	adv_hyp_encoder_lambda_column, nli_net_adv_hyp_encoder_lambda_column, random_premise_frac_column, nli_train_column, 
    	hyp_train_column, nli_test_column, hyp_test_column)], delimiter=',', fmt='%s')
    return 

if __name__ == '__main__':
	run_experiment()
    