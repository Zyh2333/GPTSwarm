#!/usr/bin/env python
# -*- coding: utf-8 -*-
from swarm.environment.operations.demand_analysis import DemandAnalysis
from swarm.environment.operations.language_choose import LanguageChoose
from swarm.environment.operations.coding import Coding
from swarm.environment.operations.code_complete import CodeComplete
from swarm.environment.operations.code_review_comment import CodeReviewComment
from swarm.environment.operations.code_review_modification import CodeReviewModification
from swarm.environment.operations.code_test_error_summary import CodeTestErrorSummary
from swarm.environment.operations.code_test_error_modification import CodeTestErrorModification
from swarm.environment.operations.code_enviroment_doc import EnvironmentDoc
from swarm.environment.operations.code_manual import Manual
from swarm.graph import Graph
from swarm.environment.agents.agent_registry import AgentRegistry


@AgentRegistry.register('CodeTOT')
class CodeTOT(Graph):
    def build_graph(self):

        demand = DemandAnalysis(self.domain, self.model_name)
        language = LanguageChoose(self.domain, self.model_name)
        coding = Coding(self.domain, self.model_name)
        # codeComplete = CodeComplete(self.domain, self.model_name)
        # codeReviewComment = CodeReviewComment(self.domain, self.model_name)
        # codeReviewModification = CodeReviewModification(self.domain, self.model_name)
        # codeTestErrorSummary = CodeTestErrorSummary(self.domain, self.model_name)
        # codeTestErrorModification = CodeTestErrorModification(self.domain, self.model_name)
        environmentDoc = EnvironmentDoc(self.domain, self.model_name)
        manual = Manual(self.domain, self.model_name)

        demand.add_successor(language)
        language.add_successor(coding)
        codeTestErrorSummarys = []
        codeTestErrorModifications = []
        j = 0
        while j < 3:
            codeTestErrorSummary = CodeTestErrorSummary(self.domain, self.model_name)
            self.add_node(codeTestErrorSummary)
            codeTestErrorModification = CodeTestErrorModification(self.domain, self.model_name)
            self.add_node(codeTestErrorModification)
            # codeTestErrorSummary.add_successor(codeTestErrorModification)
            codeTestErrorModifications.append(codeTestErrorModification)
            codeTestErrorSummarys.append(codeTestErrorSummary)
            codeTestErrorModification.add_successor(environmentDoc)
            j += 1
        j = 0
        codeReviewComments = []
        codeReviewModifications = []
        while j < 3:
            codeReviewComment = CodeReviewComment(self.domain, self.model_name)
            self.add_node(codeReviewComment)
            codeReviewModification = CodeReviewModification(self.domain, self.model_name)
            self.add_node(codeReviewModification)
            # codeReviewComment.add_successor(codeReviewModification)
            codeReviewModifications.append(codeReviewModification)
            codeReviewComments.append(codeReviewComment)
            if j == 2:
                for i in range(len(codeTestErrorSummarys)):
                    codeReviewModification.add_successor(codeTestErrorSummarys[i])
                    codeReviewModification.add_successor(codeTestErrorModifications[i])
            j += 1
        i = 0
        while i < 10:
            codeComplete = CodeComplete(self.domain, self.model_name)
            self.add_node(codeComplete)
            coding.add_successor(codeComplete)
            if i == 9:
                for t in range(len(codeReviewComments)):
                    codeComplete.add_successor(codeReviewComments[t])
                    codeComplete.add_successor(codeReviewModifications[t])
            i += 1
        environmentDoc.add_successor(manual)

        # combine = CombineAnswer(self.domain, self.model_name)
        # file_analysis.add_successor(combine)
        # web_search.add_successor(combine)

        self.input_nodes = [demand]
        self.output_nodes = [manual]

        self.add_node(demand)
        self.add_node(language)
        self.add_node(coding)
        # self.add_node(codeComplete)
        # self.add_node(codeReviewComment)
        # self.add_node(codeReviewModification)
        # self.add_node(codeTestErrorSummary)
        # self.add_node(codeTestErrorModification)
        self.add_node(environmentDoc)
        self.add_node(manual)
