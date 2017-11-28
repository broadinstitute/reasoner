import ipywidgets as widgets
import networkx
from reasoner.Agent import Agent

def print_dict(d):
    for k,v in d.items():
        print(k)
        for k2,v2 in v.items():
            print('    ' + k2 + ': ' + str(v2))
        print()
        
def run_query(question):
    agent = Agent(question)
    agent.acquire_knowledge()
    outcome_pathway = agent.analyze(drug, disease)

    p_total = 1
    for e in outcome_pathway['edges']:
        p_total = p_total*max(e['p'], 0.001)

    for node in outcome_pathway['nodes']:
        print(node['entity'] + ': ' + node['name'] + '\n')

    print('\nprobability: ' + str(p_total))
    
    agent.show_blackboard()
    
def handle(sender):
    print(question.value)
    run_query(question.value)
    
def start_agent():
    question = widgets.Text(placeholder='Enter a question', disabled=False)
    question.on_submit(handle)
    print('\n')
    display(question)
    print('\n\n')