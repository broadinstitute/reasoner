import pyjags
import numpy as np

class ConnectionPGM:
    def __init__(self):
        np.set_printoptions(precision=1)
        self.set_models()

    def set_models(self):
        self.models = {
            'pubmed':{'model':  '''
                                model {
                                    theta ~ dbeta(1,1)
                                    is_connection ~ dbern(theta)
                                    
                                    lambda_y ~ dnorm(50, 50)
                                    years_since_first_article ~ dpois(lambda_y)
                                    
                                    lambda_n = 10 * ((1.7^(years_since_first_article/7))*is_connection + (1.5^(years_since_first_article/7))*(1-is_connection))
                                    num_articles ~ dpois(lambda_n)

                                    p_causal = 0.1 + 0.7*is_connection
                                    causal_phrase ~ dbern(p_causal)
                                }
                                ''',
                      'variables':['is_connection', 'num_articles', 'causal_phrase', 'years_since_first_article']
                     }
        }

        
    def evaluate(self, model_name, observations, variables, n_iter=1000, chains=4):
        model = pyjags.Model(self.models[model_name]['model'], data=observations, chains=chains)
        samples = model.sample(n_iter, vars=variables)
        return(samples)

    def get_mean(self, samples, varname):
        return(np.mean(samples[varname]))
            
    def summary(self, samples, varname, p=95):
        values = samples[varname]
        ci = np.percentile(values, [100-p, p])
        print('{:<6} mean = {:>5.1f}, {}% credible interval [{:>4.1f} {:>4.1f}]'.format(
          varname, np.mean(values), p, *ci))