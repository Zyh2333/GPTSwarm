#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from collections import defaultdict
from typing import List, Any, Optional

from swarm.llm.format import Message
from swarm.graph import Node
from swarm.environment.prompt.prompt_set_registry import PromptSetRegistry
from swarm.llm import LLMRegistry
from swarm.environment.chatdev.env import code
from swarm.utils.log import logger, swarmlog
from swarm.utils.globals import Cost
import experiments.static as static


class CodeReviewComment(Node):
    def __init__(self, 
                 domain: str,
                 model_name: Optional[str] = None,
                 operation_description: str = "code review comment to develop software.",
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
        #     operation = input.get('operation')
        #     if operation:
        #         self.materials[operation] += f'{input.get("output", "")}\n'
            # if operation == "FileAnalyse":
            #     files_list = input.get("files", [])
            #     self.materials["files"] = "\n".join(files_list)

            # self.materials["task"] = input.get('task')
        for input in node_inputs:
            task = input.get('task')
            modality = input.get('modality')
            language = input.get('language')
            ideas = input.get('ideas')
        codes = code.get_codes()
        prompt = self.prompt_set.get_code_review_comment_prompt(task, modality, language, codes, ideas)

        if meta_init:
            # According to node_inputs and memory history,
            # rewrite the meta_role, meta_constraint and meta_prompt
            pass

        return self.role, self.constraint, prompt


    async def _execute(self, inputs: List[Any] = [], **kwargs):

        node_inputs = self.process_input(inputs)

        role, constraint, prompt = self.meta_prompt(node_inputs, meta_init=False)
        inputs = node_inputs[-1]
        message = [Message(role="system", content=
        f'''
        "{constraint}",
        "You are Code Reviewer. we are both working at ChatDev. We share a common interest in collaborating to successfully complete a task assigned by a new customer.",
        "You can help programmers to assess source codes for software troubleshooting, fix bugs to increase code quality and robustness, and offer proposals to improve the source codes.",
        "Here is a new customer's task: {inputs.get('task')}.",
        "To complete the task, you must write a response that appropriately solves the requested instruction based on your expertise and customer's needs."
        '''),
                Message(role="user", content=prompt)]
        response = await self.llm.agen(message, max_tokens=self.max_token)
        executions = {"operation": self.node_name, "format": "natural language"}
        # executions["comments"] = response
        static.comments = response
        for input in inputs:
            if input not in executions:
                executions[input] = inputs.get(input)

        self.memory.add(self.id, executions)

        self.log()
        return [executions]
        #return executions
    
    