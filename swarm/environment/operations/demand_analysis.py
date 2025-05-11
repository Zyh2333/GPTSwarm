#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from collections import defaultdict
from typing import List, Any, Optional

from swarm.llm.format import Message
from swarm.graph import Node
from swarm.environment.prompt.prompt_set_registry import PromptSetRegistry
from swarm.llm import LLMRegistry
from swarm.utils.log import logger, swarmlog
from swarm.utils.globals import Cost


class DemandAnalysis(Node):
    def __init__(self, 
                 domain: str,
                 model_name: Optional[str] = None,
                 operation_description: str = "demand analysis to develop software.",
                 max_token: int = 30000,
                 id=None):
        super().__init__(operation_description, id, True)
        self.domain = domain
        self.llm = LLMRegistry.get(model_name)
        self.max_token = max_token
        self.prompt_set = PromptSetRegistry.get(self.domain)
        self.role = self.prompt_set.get_role()
        self.constraint = self.prompt_set.get_constraint()


    @property
    def node_name(self):
        return self.__class__.__name__

    def meta_prompt(self, node_inputs, meta_init=False):

        # self.materials = defaultdict(str)
        # for input in node_inputs:
        #     operation = input.get('operation')
        #     if operation:
        #         self.materials[operation] += f'{input.get("output", "")}\n'
            # if operation == "FileAnalyse":
            #     files_list = input.get("files", [])
            #     self.materials["files"] = "\n".join(files_list)

            # self.materials["task"] = input.get('task')

        prompt = self.prompt_set.get_demand_analysis_prompt()

        if meta_init:
            # According to node_inputs and memory history,
            # rewrite the meta_role, meta_constraint and meta_prompt
            pass

        return self.role, self.constraint, prompt


    async def _execute(self, inputs: List[Any] = [], **kwargs):

        node_inputs = self.process_input(inputs)

        outputs = []
        for input in node_inputs:
            task = input["task"]
            role, constraint, prompt = self.meta_prompt(node_inputs, meta_init=False)

            message = [Message(role="system", content=
            f'''
            "{constraint}",
            "You are Chief Product Officer. we are both working at ChatDev. We share a common interest in collaborating to successfully complete a task assigned by a new customer.",
            "You are responsible for all product-related matters in ChatDev. Usually includes product design, product strategy, product vision, product innovation, project management and product marketing.",
            "Here is a new customer's task: {task}.",
            "To complete the task, you must write a response that appropriately solves the requested instruction based on your expertise and customer's needs."
            '''),
                    Message(role="user", content=prompt)]
            response = await self.llm.agen(message, max_tokens=self.max_token, temperature=0.2)
            executions = {"operation": self.node_name, "format": "natural language", "task": task}
            if response:
                executions['modality'] = response.split("<INFO>")[-1].lower().replace(".", "").strip()
            # executions = {"operation": self.node_name,
                # "input": node_inputs,
                # "subtask": prompt,
                # "output": response,

            self.memory.add(self.id, executions)
            outputs.append(executions)

        self.log()
        # return [executions]
        return outputs
    
    