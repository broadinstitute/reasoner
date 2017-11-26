import pyjags
import numpy as np

class ConnectionPGM:
    """Calculate connection probabilites using probabilistic graphical models.
    
    Given observations for a connection between two entities, ``ConnectionPGM`` samples from a
    probabilstic graphical model (PGM) to calculate the probability that the connection is reliable.
    ``ConnectionPGM`` uses the MCMC sampler JAGS.

    """
    def __init__(self):
        np.set_printoptions(precision=1)
        self.set_models()

    def set_models(self):
        #initialize class with predefined JAGS model strings
        self.models = {
            'pubmed':{'model':  '''
                        model {
                            theta ~ dbeta(1,10)
                            is_connection ~ dbern(theta)
                            
                            tau_y <- pow(30, -2)
                            lambda_y ~ dnorm(50, tau_y)
                            years_since_first_article ~ dpois(lambda_y)

                            p_pub_prior_conn ~ dbeta(2,8)
                            p_pub_prior_notconn ~ dbeta(7,3)
                            p_pub <- p_pub_prior_conn * is_connection  + p_pub_prior_notconn * (1-is_connection) 
                            r_pub <- years_since_first_article
                            num_articles ~ dnegbin(p_pub, r_pub)

                            p_causal_prior ~ dbeta(1,10)
                            p_causal <- p_causal_prior + 0.29*is_connection
                            causal_phrase ~ dbern(p_causal)
                        }
                        ''',
              'variables':['is_connection', 'num_articles', 'causal_phrase', 'years_since_first_article']
             }
        }

        
    def evaluate(self, model_name, observations, variables, n_iter=1000, chains=4):
        """Run JAGS MCMC on a model.
        
        Parameters
        ----------
        model_name : str
            The name of the model.
            
        observations : dict
            A dictionary of observation variables (keys) and their values.
            
        variables : list
            The variables for which samples should be generated.
            
        n_iter : int, optional
            The number of iterations for MCMC. [default: 1000]
            
        chains : int, optional
            The number of MCMC chains to be run. [default: 4]
            
        Returns
        -------
        samples : dict
            A dictionary that contains sample values. Keys are variable names. The value for each
            variable is a list that, for each iteration, contains another list with
            values for each MCMC chain.
        
         """
        model = pyjags.Model(self.models[model_name]['model'], data=observations, chains=chains)
        samples = model.sample(n_iter, vars=variables)
        return samples

    def get_mean(self, samples, varname):
        """Calculate the mean value of samples
        
        Parameters
        ----------
        samples : list
            Samples from an MCMC run.
            
        varname : str
            The name of the variable for which to calculate the mean.
        
        Returns
        -------
        numpy.float64
            The sample mean for variable ``varname``.
        
        """
        return np.mean(samples[varname])
            
    def summary(self, samples, varname, p=95):
        #calculate summary statistics for samples
        values = samples[varname]
        ci = np.percentile(values, [100-p, p])
        print('{:<6} mean = {:>5.1f}, {}% credible interval [{:>4.1f} {:>4.1f}]'.format(
          varname, np.mean(values), p, *ci))
