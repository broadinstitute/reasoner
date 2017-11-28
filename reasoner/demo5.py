%matplotlib inline

import numpy as np
import pandas as pd
from pandas.plotting import *
import matplotlib.pyplot as plt
import pyjags
from ipywidgets import widgets

from IPython.display import clear_output

from reasoner.ConnectionPGM import ConnectionPGM

plt.style.use('ggplot')

articles = widgets.IntSlider(
                value=10,
                min=0,
                max=400,
                step=5,
                disabled=False,
                continuous_update=False,
                orientation='horizontal',
                readout=True,
                readout_format='d'
            )

years = widgets.IntSlider(
            value=10,
            min=0,
            max=70,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )

causal = widgets.Checkbox(
            value=False,
            disabled=False
        )

is_connection = widgets.Checkbox(
            value=False,
            disabled=False
        )

use_articles = widgets.Checkbox(
            value=False,
            description='use',
            disabled=False
        )

use_years = widgets.Checkbox(
            value=False,
            description='use',
            disabled=False
        )

use_causal = widgets.Checkbox(
            value=False,
            description='use',
            disabled=False
        )

use_connection = widgets.Checkbox(
            value=False,
            description='use',
            disabled=False
        )

run_button = widgets.Button(
            description='run',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='run'
        )




def plot(trace, var):
    fig, axes = plt.subplots(1, 3, figsize=(9, 3))
    fig.suptitle(var, fontsize='xx-large')
 
    # Marginal posterior density estimate:
    trace[var].plot.density(ax=axes[0])
    axes[0].set_xlabel('Parameter value')
    axes[0].locator_params(tight=True)
 
    # Autocorrelation for each chain:
    axes[1].set_xlim(0, 100)
    for chain in trace[var].columns:
        autocorrelation_plot(trace[var,:,chain], axes[1], label=chain)
 
    # Trace plot:
    axes[2].set_ylabel('Parameter value')
    trace[var].plot(ax=axes[2])
 
    # Save figure
    plt.tight_layout()
    
def show_widgets():
    display(widgets.HBox([
        widgets.VBox([widgets.Label('is true connection:'), widgets.Label('connection phrase in abstract:'), 
                      widgets.Label('number of articles:'), widgets.Label('years since first article:')]),
        widgets.VBox([is_connection, causal, articles, years]),
        widgets.VBox([use_connection, use_causal, use_articles, use_years])
    ]))

    display(run_button)

def run_pgm(sender):
    clear_output()
    
    show_widgets()
    
    cp = ConnectionPGM()
    model_name = 'pubmed'
    
    evidence = dict()
    if use_connection.value:
        evidence['is_connection'] = is_connection.value

    if use_causal.value:
        evidence['causal'] = causal.value

    if use_articles.value:
        evidence['num_articles'] = articles.value

    if use_years.value:
        evidence['years_since_first_article'] = years.value
        
    variables = set(cp.models[model_name]['variables']) - set(evidence.keys())
    print(evidence)
    print(variables)
    samples = cp.evaluate('pubmed', evidence, variables)
    
    trace = pd.Panel({k: v.squeeze(0) for k, v in samples.items()})
    trace.axes[0].name = 'Variable'
    trace.axes[1].name = 'Iteration'
    trace.axes[2].name = 'Chain'

    # Point estimates:
    print(trace.to_frame().mean())

    # Bayesian equal-tailed 95% credible intervals:
    print(trace.to_frame().quantile([0.05, 0.95]))

    # Display diagnostic plots
    for var in trace:
        try:
            plot(trace, var)
        except Exception as inst:
            continue
        
run_button.on_click(run_pgm)
    