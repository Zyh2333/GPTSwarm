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
import swarm.environment.chatdev.env as env
import experiments.static as static


class CodeTestErrorSummary(Node):
    def __init__(self, 
                 domain: str,
                 model_name: Optional[str] = None,
                 operation_description: str = "code test error summary to develop software.",
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
            language = input.get('language')
        (exist_bugs_flag, test_reports) = env.exist_bugs(code.directory)
        if "ModuleNotFoundError" in test_reports:
            try:
                # kwargs.update(**self.pre_execute(message, **kwargs))
                env.fix_module_not_found_error(test_reports)
            except Exception:
                pass
        (exist_bugs_flag, test_reports) = env.exist_bugs(code.directory)
        static.test_reports = test_reports
        codes = code.get_codes()
        prompt = self.prompt_set.get_test_error_summary_prompt(language, codes, test_reports)

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
        "You are Software Test Engineer. we are both working at ChatDev. We share a common interest in collaborating to successfully complete a task assigned by a new customer.",
        "You can use the software as intended to analyze its functional properties, design manual and automated test procedures to evaluate each software product, build and implement software evaluation test programs, and run test programs to ensure that testing protocols evaluate the software correctly.",
        "Here is a new customer's task: {inputs['task']}.",
        "To complete the task, you must write a response that appropriately solves the requested instruction based on your expertise and customer's needs."
        '''),
                Message(role="user", content=prompt)]
        response = await self.llm.agen(message, max_tokens=self.max_token)
        executions = {"operation": self.node_name, "format": "natural language"}
        executions['error_summary'] = response
        static.error_summary = response
        for input in inputs:
            if input not in executions:
                executions[input] = inputs.get(input)

        self.memory.add(self.id, executions)

        self.log()
        return [executions]
        #return executions
    
    