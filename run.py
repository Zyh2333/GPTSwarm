#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import yaml
import json
import time
import asyncio
from pathlib import Path
from swarm.utils.globals import Cost, PromptTokens, CompletionTokens

from swarm.graph.swarm import Swarm
from swarm.environment.tools.reader.readers import JSONReader, YAMLReader
from swarm.environment.agents.io import IO
from swarm.environment.agents.gaia.normal_io import NormalIO
from swarm.environment.agents.gaia.tool_io import ToolIO
from swarm.environment.agents.gaia.web_io import WebIO
from swarm.environment.agents.chatdev.code_tot import CodeTOT
from swarm.environment.operations import DirectAnswer
from swarm.memory.memory import GlobalMemory
from swarm.utils.globals import Time, Cost, CompletionTokens, PromptTokens
from swarm.utils.const import GPTSWARM_ROOT
from swarm.utils.log import initialize_log_file, logger, swarmlog
from swarm.environment.domain.gaia import question_scorer
from swarm.environment.operations.final_decision import MergingStrategy
import experiments.static as static
from swarm.environment.chatdev.env import code, doc, manual
import experiments.similarity as similarity
from datetime import datetime
import swarm.environment.chatdev.env as env

def dataloader(data_list):
    for data in data_list:
        yield data

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

async def main():
    parser = argparse.ArgumentParser(description="GPTSwarm Experiments on Chatdev")
    parser.add_argument("--config", type=str, help="Path to configuration YAML file.")
    parser.add_argument("--domain", type=str, default="chatdev")
    parser.add_argument("--agents", nargs='+', default=["IO"])
    # parser.add_argument("--dataset_json", type=str, default="/Volumes/ZHITAI-macmini/zhuyuhan/project/GPTSwarm/datasets/gaia/level_1_val.json") #level_1_val_solveable.json
    # parser.add_argument("--dataset_files", type=str, default="datasets/gaia/val_files")
    # parser.add_argument("--result_file", type=str, default=None)
    parser.add_argument('--task', type=str, default="Develop a basic Gomoku game.",
                        help="Prompt of software")
    parser.add_argument('--name', type=str, default="Gomoku",
                        help="Name of software")
    parser.add_argument('--org', type=str, default="chatdev",
                        help="Name of software")
    parser.add_argument("--llm", type=str, default="deepseek-chat") #gpt-4-1106-preview  gpt-3.5-turbo-1106 gpt-3.5-turbo gpt-4
    args = parser.parse_args()

    result_path = GPTSWARM_ROOT / "result"
    os.makedirs(result_path, exist_ok=True)

    current_time = Time.instance().value or time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    Time.instance().value = current_time


    log_file_path = initialize_log_file("chatdev", Time.instance().value)

    if args.config:
        config_args = YAMLReader.parse(args.config, return_str=False)
        for key, value in config_args.items():
            setattr(args, key, value)

    start_index = 0
    result_file = None

    # dataset = JSONReader.parse_file(args.dataset_json)

    ####################################

    # strategy = MergingStrategy.SelfConsistency #MergingStrategy.SelectBest #MergingStrategy.SelfConsistency #MergingStrategy.SelectBest #MergingStrategy.SelectBest #MergingStrategy.SelfConsistency # MergingStrategy.MajorityVote MergingStrategy.RandomChoice

    # experiment_name = "ToolTOT"

    # swarm = Swarm(["ToolTOT"]*7, 
    #               "gaia",
    #               model_name="mock", #args.llm, #"mock", #args.llm,#args.llm,
    #               final_node_class="FinalDecision",
    #               final_node_kwargs=dict(strategy=strategy)
    #             )
    # swarm.composite_graph.display()

    # print(args.llm)

    #agent = IO(domain="gaia", model_name=args.llm)
    #agent = WebIO(domain="gaia", model_name=args.llm)
    #agent = ToolIO(domain="gaia", model_name=args.llm)
    begin_t = time.time()
    agent = CodeTOT(domain="chatdev", model_name=args.llm)

    #io = DirectAnswer(domain="gaia", model_name=args.llm)

    # agent.display()

    now = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    suffix = "-2"
    tasks = []
    with open(f"result/2025-05-03-2.txt", mode="r") as rf:
        i = 0
        for line in rf.readlines():
            if i == 0:
                i += 1
                continue
            else:
                splits = line.split("$")
                if len(splits) == 6 or len(splits) == 8:
                    tasks.append(splits[0])
    task_name = args.name + '_' + args.org
    if task_name in tasks:
        print(f"任务 {task_name} 已存在，程序退出。")
        sys.exit(0)
    with open(f"result/2025-05-03-2.txt", mode="a+") as rf:
        rf.seek(0)
        if not rf.read():
            print(f"name$completeness$executable$similarity_score$quality$time$token$cost", file=rf)
        rf.seek(0, 2)
        static.app_start_time = now
        static.output_dir = f"app/{task_name}-{now}"
        code.directory = static.output_dir
        manual.directory = static.output_dir
        doc.directory = static.output_dir

        inputs = {"task": args.task, "name": args.name}

        swarmlog("🐝GPTSWARM SYS", f"Finish {i} samples...", Cost.instance().value, PromptTokens.instance().value, CompletionTokens.instance().value, log_file_path)

        answer = await agent.run(inputs=inputs)
        # answer = answer[-1].split("FINAL ANSWER: ")[-1]


        print("-----")
        print(f"AGENT ANSWER: {answer}")
        print("-----")

        """
        answer = await io._execute(inputs=inputs)
        answer = answer[-1]["output"].split("FINAL ANSWER: ")[-1]
    
        print("-----")
        print(f"OPERATION ANSWER: {answer}")
        print("-----")
        """

        end_t = time.time()
        code_str = code.get_codes()
        completeness = 0 if " pass " in code_str else 1
        executable = 1 if env.executable(static.output_dir) else 0
        similarity_score = similarity.calculate_semantic_similarity(code_str, args.task)
        q = completeness * executable * similarity_score
        total_token_num = PromptTokens.instance().value + CompletionTokens.instance().value
        total_token_cost = Cost.instance().value
        print(
            f"{task_name}${completeness}${executable}${similarity_score:.4f}${q}${end_t - begin_t}${total_token_num}${total_token_cost}",
            file=rf)

        # current_time = Time.instance().value or time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        # Time.instance().value = current_time

if __name__ == '__main__':
    asyncio.run(main())
