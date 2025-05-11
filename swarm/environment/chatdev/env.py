from swarm.environment.chatdev.codes import Codes
from swarm.environment.chatdev.documents import Documents
import os
import signal
import subprocess
import time
import re

code = Codes()
doc = Documents()
manual = Documents()


def fix_module_not_found_error(test_reports):
    if "ModuleNotFoundError" in test_reports:
        for match in re.finditer(r"No module named '(\S+)'", test_reports, re.DOTALL):
            module = match.group(1)
            try:
                # 自己创一个空的虚拟环境去单独安装生成的软件的依赖和测试其能否执行
                result = subprocess.run(
                    f"/Volumes/ZHITAI-macmini/zhuyuhan/venv/chatdev_agent-network/bin/python -m pip install {module}",
                    shell=True,
                    check=True,  # 自动在非零返回码时报错
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f"Failed to install module '{module}':\n{e.stderr}"
                ) from e


def exist_bugs(directory) -> tuple[bool, str]:
    success_info = "The software ran successfully without errors."

    try:
        python_files = [f for f in os.listdir(directory) if f.endswith('.py')]

        for py_file in python_files:
            full_path = os.path.join(directory, py_file)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if '__name__' in content and 'main' in content and '__main__' in content:
                    # 构造跨平台命令
                    if os.name == 'nt':
                        command = f'cd "{directory}" && /Volumes/ZHITAI-macmini/zhuyuhan/venv/chatdev_agent-network/bin/python "{py_file}"'
                        process = subprocess.Popen(
                            command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                        )
                    else:
                        # 自己创一个空的虚拟环境去单独安装生成的软件的依赖和测试其能否执行
                        command = f'cd "{directory}"; /Volumes/ZHITAI-macmini/zhuyuhan/venv/chatdev_agent-network/bin/python "{py_file}"'
                        process = subprocess.Popen(
                            command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            preexec_fn=os.setsid
                        )

                    time.sleep(3)  # 给程序执行时间

                    # 尝试终止仍在运行的程序
                    if process.poll() is None:
                        if hasattr(os, "killpg"):
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        else:
                            os.kill(process.pid, signal.SIGTERM)
                            if process.poll() is None:
                                os.kill(process.pid, signal.CTRL_BREAK_EVENT)

                    return_code = process.wait()
                    stderr_output = process.stderr.read().decode('utf-8', errors='ignore')

                    if return_code == 0 or return_code == -signal.SIGTERM:
                        return False, success_info
                    else:
                        if "Traceback" in stderr_output:
                            return True, f"Traceback detected:\n{stderr_output.strip()}"
                        elif stderr_output.strip():
                            return True, f"Error output:\n{stderr_output.strip()}"
                        else:
                            return True, "Exited with non-zero return code but no stderr."

        return True, "No Python file with a main function was found."

    except subprocess.CalledProcessError as e:
        return True, f"Error: {e}"
    except Exception as ex:
        return True, f"An exception occurred: {ex}"


def executable(directory) -> bool:
    try:
        python_files = [f for f in os.listdir(directory) if f.endswith('.py')]

        for py_file in python_files:
            full_path = os.path.join(directory, py_file)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 判断是否有主函数入口
                if '__name__' in content and 'main' in content and '__main__' in content:
                    # 构造执行命令
                    if os.name == 'nt':
                        command = f'cd "{directory}" && /Volumes/ZHITAI-macmini/zhuyuhan/venv/chatdev_agent-network/bin/python "{py_file}"'
                        process = subprocess.Popen(
                            command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                        )
                    else:
                        # 自己创一个空的虚拟环境去单独安装生成的软件的依赖和测试其能否执行
                        command = f'cd "{directory}"; /Volumes/ZHITAI-macmini/zhuyuhan/venv/chatdev_agent-network/bin/python "{py_file}"'
                        process = subprocess.Popen(
                            command,
                            shell=True,
                            preexec_fn=os.setsid,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )

                    time.sleep(3)  # 等一等程序执行

                    # 如果还在运行，终止它
                    if process.poll() is None:
                        if hasattr(os, "killpg"):
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        else:
                            os.kill(process.pid, signal.SIGTERM)
                            if process.poll() is None:
                                os.kill(process.pid, signal.CTRL_BREAK_EVENT)

                    return_code = process.wait()
                    if return_code == 0 or return_code == -signal.SIGTERM:
                        return True
                    else:
                        error_output = process.stderr.read().decode('utf-8')
                        print(f"Error running {py_file}: {error_output}")
                        return False

        # 没有找到带 main 的文件
        return False

    except Exception as e:
        print(f"Exception occurred: {e}")
        return False


def refresh():
    global code, doc, manual
    code = Codes()
    doc = Documents()
    manual = Documents()
