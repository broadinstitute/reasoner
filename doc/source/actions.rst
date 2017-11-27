Actions
=======

Actions specify how the agent interacts with knowledge sources. They are characterized by their preconditions (required state variables for the action to be executed) and effects (state variables the aciton modifies).
All actions extend the ``Action`` base class and follow a standardized interface to accept inputs, return outputs, and be executed by the agent.

The Action base class
---------------------

.. module:: reasoner.actions.action

.. autoclass:: Action
   :members:

module edit_actions
-------------------

.. automodule:: reasoner.actions.edit_actions
   :members:
   
module eutils
-------------

.. automodule:: reasoner.actions.eutils
   :members:

module file_actions
-------------------

.. automodule:: reasoner.actions.file_actions
   :members:

module pharos
-------------

.. automodule:: reasoner.actions.pharos
   :members:
   

module sparql
-------------

.. automodule:: reasoner.actions.sparql
   :members:
