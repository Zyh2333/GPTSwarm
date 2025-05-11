#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any

from swarm.environment.prompt.prompt_set import PromptSet
from swarm.environment.prompt.prompt_set_registry import PromptSetRegistry
from swarm.environment.prompt.common import get_combine_materials


@PromptSetRegistry.register('chatdev')
class ChatdevPromptSet(PromptSet):
    """
    GaiaPromptSet provides a collection of static methods to generate prompts
    for a general AI assistant. These prompts cover various tasks like answering questions,
    performing web searches, analyzing files, and reflecting on tasks.
    """

    # @staticmethod
    # def get_role():
    #     raise NotImplementedError
    #
    # @staticmethod
    # def get_constraint():
    #     raise NotImplementedError

    @staticmethod
    def get_format():
        raise NotImplementedError

    @staticmethod
    def get_answer_prompt(question):
        raise NotImplementedError

    @staticmethod
    def get_query_prompt(question):
        raise NotImplementedError

    @staticmethod
    def get_file_analysis_prompt(query, file):
        raise NotImplementedError

    @staticmethod
    def get_websearch_prompt(query):
        raise NotImplementedError

    @staticmethod
    def get_distill_websearch_prompt(query, results):
        raise NotImplementedError

    @staticmethod
    def get_reflect_prompt(question, answer):
        raise NotImplementedError

    @staticmethod
    def get_combine_materials(materials: Dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def get_adversarial_answer_prompt(materials: Dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def get_role():
        return "a general AI assistant"


    @staticmethod
    def get_constraint():
        # adapted from the GAIA paper: https://arxiv.org/pdf/2311.12983.pdf
        return (
"ChatDev is a software company powered by multiple intelligent agents, such as chief executive officer, chief human resources officer, chief product officer, chief technology officer, etc, with a multi-agent organizational structure and the mission of 'changing the digital world through programming'."
            )


    @staticmethod
    def get_format():
        return "natural language"


    @staticmethod
    def get_demand_analysis_prompt():
        return (
            "ChatDev has made products in the following form before:"
            "Image: can present information in line chart, bar chart, flow chart, cloud chart, Gantt chart, etc."
            "Document: can present information via .docx files."
            "PowerPoint: can present information via .pptx files."
            "Excel: can present information via .xlsx files."
            "PDF: can present information via .pdf files."
            "Website: can present personal resume, tutorial, products, or ideas, via .html files."
            "Application: can implement visualized game, software, tool, etc, via python."
            "Dashboard: can display a panel visualizing real-time information."
            "Mind Map: can represent ideas, with related concepts arranged around a core concept."
            f"As the \"Chief Product Officer\", to satisfy the new user's demand and the product should be realizable, you should keep discussing with me to decide which product modality do we want the product to be?"
            "Note that we must ONLY discuss the product modality and do not discuss anything else! Once we all have expressed our opinion(s) and agree with the results of the discussion unanimously, any of us must actively terminate the discussion by replying with only one line, which starts with a single word <INFO>, followed by our final product modality without any other words, e.g., \"<INFO> PowerPoint\"."
        )


    @staticmethod
    def get_language_choose_prompt(task, modality, ideas):
        return (
      "According to the new user's task and some creative brainstorm ideas listed below: "
      f"Task: \"{task}\"."
      f"Modality: \"{modality}\"."
      f"Ideas: \"{ideas}\"."
      "We have decided to complete the task through a executable software implemented via a programming language. "
      f"As the \"Chief Technology Officer\", to satisfy the new user's demand and make the software realizable, you should propose a concrete programming language. If python can complete this task via Python, please answer Python; otherwise, answer another programming language (e.g., Java, C++, etc,)."
      "Note that we must ONLY discuss the target programming language and do not discuss anything else! Once we all have expressed our opinion(s) and agree with the results of the discussion unanimously, any of us must actively terminate the discussion and conclude the best programming language we have discussed without any other words or reasons, return only one line using the format: \"<INFO> *\" where \"*\" represents a programming language."
    )


    @staticmethod
    def get_coding_prompt(task, modality, ideas, description, language, gui):
        return (
            "According to the new user's task and our software designs listed below: "
            f"Task: \"{task}\"."
            f"Task description: \"{description}\"."
            f"Modality: \"{modality}\"."
            f"Programming Language: \"{language}\""
            f"Ideas:\"{ideas}\""
            f"We have decided to complete the task through a executable software with multiple files implemented via {language}. As the Programmer, to satisfy the new user's demands, you should write one or multiple files and make sure that every detail of the architecture is, in the end, implemented as code. {gui}"
            "Think step by step and reason yourself to the right decisions to make sure we get it right."
            "You will first lay out the names of the core classes, functions, methods that will be necessary, as well as a quick comment on their purpose."
            "Then you will output the content of each file including complete code. Each file must strictly follow a markdown code block format, where the following tokens must be replaced such that \"FILENAME\" is the lowercase file name including the file extension, \"LANGUAGE\" in the programming language, \"DOCSTRING\" is a string literal specified in source code that is used to document a specific segment of code, and \"CODE\" is the original code:"
            "FILENAME"
            "```LANGUAGE"
            "'''"
            "DOCSTRING"
            "'''"
            "CODE"
            "```"
            "You will start with the \"main\" file, then go to the ones that are imported by that file, and so on."
            "Please note that the code should be fully functional. Ensure to implement all functions. No placeholders (such as 'pass' in Python)."
        )


    @staticmethod
    def get_code_complete_prompt(task, modality, language, codes, unimplemented_file):
        return (
              "According to the new user's task and our software designs listed below: "
              f"Task: \"{task}\"."
              f"Modality: \"{modality}\"."
              f"Programming Language: \"{language}\""
              "Codes:"
              f"\"{codes}\""
              "Unimplemented File:"
              f"\"{unimplemented_file}\""
              "In our software, each file must strictly follow a markdown code block format, where the following tokens must be replaced such that \"FILENAME\" is the lowercase file name including the file extension, \"LANGUAGE\" in the programming language, \"DOCSTRING\" is a string literal specified in source code that is used to document a specific segment of code, and \"CODE\" is the original code:"
              "FILENAME"
              "```LANGUAGE"
              "'''"
              "DOCSTRING"
              "'''"
              "CODE"
              "```"
              f"As the Programmer, to satisfy the complete function of our developed software, you have to implement all methods in the {unimplemented_file} file which contains a unimplemented class. Now, implement all methods of the {unimplemented_file} and all other codes needed, then output the fully implemented codes, strictly following the required format."
        )



    @staticmethod
    def get_code_review_comment_prompt(task, modality, language, codes, ideas):
        return (
        "According to the new user's task and our software designs: "
        f"Task: \"{task}\"."
        f"Modality: \"{modality}\"."
        f"Programming Language: \"{language}\""
        f"Ideas: \"{ideas}\""
        "Codes:"
        f"\"{codes}\""
        f"As the Code Reviewer, to make the software directly operable without further coding, ChatDev have formulated the following regulations:"
        "1) all referenced classes should be imported;"
        "2) all methods should be implemented;"
        "3) all methods need to have the necessary comments;"
        "4) no potential bugs;"
        "5) The entire project conforms to the tasks proposed by the user;"
        "6) most importantly, do not only check the errors in the code, but also the logic of code. Make sure that user can interact with generated software without losing any feature in the requirement;"
        "Now, you should check the above regulations one by one and review the codes in detail, propose one comment with the highest priority about the codes, and give me instructions on how to fix. Tell me your comment with the highest priority and corresponding suggestions on revision. If the codes are perfect and you have no comment on them, return only one line like \"<INFO> Finished\"."
        )


    @staticmethod
    def get_code_review_modification_prompt(task, modality, language, codes, comments, ideas):
        return (
            "According to the new user's task, our designed product modality, languages and ideas, our developed first-edition source codes are listed below: "
            f"Task: \"{task}\"."
            f"Modality: \"{modality}\"."
            f"Programming Language: \"{language}\""
            f"Ideas: \"{ideas}\""
            "Codes: "
            f"\"{codes}\""
            "Comments on Codes:"
            f"\"{comments}\""
            "In the software, each file must strictly follow a markdown code block format, where the following tokens must be replaced such that \"FILENAME\" is the lowercase file name including the file extension, \"LANGUAGE\" in the programming language, \"DOCSTRING\" is a string literal specified in source code that is used to document a specific segment of code, and \"CODE\" is the original code. Format:"
            "FILENAME"
            "```LANGUAGE"
            "'''"
            "DOCSTRING"
            "'''"
            "CODE"
            "```"
            "As the Programmer, to satisfy the new user's demand and make the software creative, executive and robust, you should modify corresponding codes according to the comments. Then, output the full and complete codes with all bugs fixed based on the comments. Return all codes strictly following the required format."
        )


    @staticmethod
    def get_test_error_summary_prompt(language, codes, test_reports):
        return (
        "Our developed source codes and corresponding test reports are listed below: "
        f"Programming Language: \"{language}\""
        "Source Codes:"
        f"\"{codes}\""
        "Test Reports of Source Codes:"
        f"\"{test_reports}\""
        "According to my test reports, please locate and summarize the bugs that cause the problem."
        )


    @staticmethod
    def get_test_error_modification_prompt(language, codes, test_reports, error_summary) -> str:
        return (
            "Our developed source codes and corresponding test reports are listed below: "
            f"Programming Language: \"{language}\""
            "Source Codes:"
            f"\"{codes}\""
            "Test Reports of Source Codes:"
            f"\"{test_reports}\""
            "Error Summary of Test Reports:"
            f"\"{error_summary}\""
            "Note that each file must strictly follow a markdown code block format, where the following tokens must be replaced such that \"FILENAME\" is the lowercase file name including the file extension, \"LANGUAGE\" in the programming language, \"DOCSTRING\" is a string literal specified in source code that is used to document a specific segment of code, and \"CODE\" is the original code:"
            "FILENAME"
            "```LANGUAGE"
            "'''"
            "DOCSTRING"
            "'''"
            "CODE"
            "```"
            "As the Programmer, to satisfy the new user's demand and make the software execute smoothly and robustly, you should modify the codes based on the error summary. Now, use the format exemplified above and modify the problematic codes based on the error summary. Output the codes that you fixed based on the test reported and corresponding explanations (strictly follow the format defined above, including FILENAME, LANGUAGE, DOCSTRING and CODE; incomplete \"TODO\" codes are strictly prohibited). If no bugs are reported, please return only one line like \"<INFO> Finished\"."
        )

    @staticmethod
    def get_environment_doc_prompt(task, modality, language, ideas, codes) -> str:
        return (
            "The new user's task and our developed codes are listed: "
            f"Task: \"{task}\"."
            f"Modality: \"{modality}\"."
            f"Programming Language: \"{language}\""
            f"Ideas: \"{ideas}\""
            "Codes: "
            f"\"{codes}\""
            f"As the Programmer, you should write a requirements.txt file, which is commonly used in Python projects to specify the dependencies or packages required for the project to run properly. It serves as a way to document and manage the project's dependencies in a standardized format. For example:"
            "requirements.txt"
            "```"
            "numpy==1.19.2"
            "pandas>=1.1.4"
            "```"
            "According to the codes and file format listed above, write a requirements.txt file to specify the dependencies or packages required for the project to run properly."
        )

    @staticmethod
    def get_manual_prompt(task, modality, language, ideas, codes, requirements) -> str:
        return (
            "The new user's task, our developed codes and required dependencies are listed: "
            f"Task: \"{task}\"."
            f"Modality: \"{modality}\"."
            f"Programming Language: \"{language}\""
            f"Ideas: \"{ideas}\""
            "Codes: "
            f"\"{codes}\""
            "Requirements:"
            f"\"{requirements}\""
            "As the Chief Product Officer, by using Markdown, you should write a manual.md file which is a detailed user manual to use the software, including introducing main functions of the software, how to install environment dependencies and how to use/play it. For example:"
            "manual.md"
            "```"
            "# LangChain"
            "Building applications with LLMs through composability"
            "Looking for the JS/TS version? Check out LangChain.js."
            "**Production Support:** As you move your LangChains into production, we'd love to offer more comprehensive support."
            "Please fill out this form and we'll set up a dedicated support Slack channel."
            "## Quick Install"
            "`pip install langchain`"
            "or"
            "`conda install langchain -c conda-forge`"
            "## 🤔 What is this?"
            "Large language models (LLMs) are emerging as a transformative technology, enabling developers to build applications that they previously could not. However, using these LLMs in isolation is often insufficient for creating a truly powerful app - the real power comes when you can combine them with other sources of computation or knowledge."
            "This library aims to assist in the development of those types of applications. Common examples of these applications include:"
            "**❓ Question Answering over specific documents**"
            "- Documentation"
            "- End-to-end Example: Question Answering over Notion Database"
            "**🤖 Agents**"
            "- Documentation"
            "- End-to-end Example: GPT+WolframAlpha"
            "## 📖 Documentation"
            "Please see [here](https://python.langchain.com) for full documentation on:"
            "- Getting started (installation, setting up the environment, simple examples)"
            "- How-To examples (demos, integrations, helper functions)"
            "- Reference (full API docs)"
            "- Resources (high-level explanation of core concepts)"
            "```"
        )

