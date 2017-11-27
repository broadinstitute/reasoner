API
===

Agent
-----

The integrated agent implementation. This module provides the interface to all other classes. 

.. module:: reasoner.Agent
   
.. autoclass:: Agent
   :members:

Blackboard
----------

The agent's short-term memory, used to store acquired knowledge on specific instances.

.. module:: reasoner.Blackboard
   
.. autoclass:: Blackboard
   :members:

QueryParser
-----------

Classes to parse natural-language questions.

.. module:: reasoner.QueryParser
   
.. autoclass:: QueryParser
   :members:

ActionPlanner
-------------

The planning module of the agent. It provides an interface to planning with Markov decision processes.

.. module:: reasoner.ActionPlanner
   
.. autoclass:: ActionPlanner
   :members:
   
KnowledgeMap
------------

The agent's long-term memory. It stores knowledge about abstract entities and their connections. The Knowledge Map contains a high-level representation of knowledge sources and the actions they can perform. It forms the basic meta-knowledge with which the agent is able to plan how to acquire knowledge to answer a question.

.. module:: reasoner.KnowledgeMap
   
.. autoclass:: KnowledgeMap
   :members:
   
ConnectionPGM
-------------

A module to calculate connection probabilities with probabilistic graphical models.

.. module:: reasoner.ConnectionPGM
   
.. autoclass:: ConnectionPGM
   :members:


