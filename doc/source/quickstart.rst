Quick Start
===========

The ``Agent`` class provides the main interface to the reasoning agent. It can be instantiated with a question, upon which it tries to parse the question, loads the Knowledge Map, and creates a plan to acquire knowledge::
   
    from reasoner import Agent
    
    drug = 'imatinib'
    disease = 'asthma'
    question = 'Which clinical outcome pathway connects ' + \
                drug + ' to ' + disease + '?'
    
    agent = Agent(question)

When creating a new ``Agent``, it will add all instances of biological entities to the blackboard. The current content of the blackboard can be shown with::
    
    agent.show_blackboard()

The next step is knowledge acquisition according to the developed plan. Start the process with::
    
    agent.acquire_knowledge()

The agent will then attempt to answer the input question by querying knowledge sources. After each step of the plan, the agent will observe the blackboard contents and derive its current state. If querying a specific knowledge source did not return the expected outcome, it will replan and try another one. The agent will continue until it reaches a goal state or runs out of actions to try.

Again, we can observe the current blackboard state after knowledge acquisition.
::
    
    agent.show_blackboard()

If ``acquire_knowledge()`` was successful, it will return ``True``. To start analysis of the knowledge on the blackboard, call::
    
    outcome_pathway = agent.analyze(drug, disease)

The agent will now attempt to calculate a probability for each edge in the knowledge graph by aggregating the evidence that the connection is real with a probabilistic graphical model. After that, it will attempt to find the best (i.e., maximum likelihood) path between ``drug`` and ``disease``.

If successful, the path will be returned as a dictionary with keys 'nodes' and 'edges'. These contain lists of the respective path elements. Each element is in turn a dictionary that contains information such as the name and entity of the node, associated identifiers, etc. To simply show the names of the nodes on the path in order, call::
    
    path_names = [node['name'] for node in outcome_pathway['nodes']]
    print(path_names)

