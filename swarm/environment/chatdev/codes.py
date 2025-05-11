import difflib
import os
import re
import experiments.static as static


class Codes:
    def __init__(self, generated_content="", if_test=False):
        self.directory: str = static.output_dir
        self.version: float = 0.0
        self.generated_content: str = generated_content
        self.codebooks = {}
        self.if_test = if_test

        def extract_filename_from_line(lines):
            file_name = ""
            for candidate in re.finditer(r"(\w+\.\w+)", lines, re.DOTALL):
                file_name = candidate.group()
                file_name = file_name.lower()
            return file_name

        def extract_filename_from_code(code):
            file_name = ""
            regex_extract = r"class (\S+?):\n"
            matches_extract = re.finditer(regex_extract, code, re.DOTALL)
            for match_extract in matches_extract:
                file_name = match_extract.group(1)
            file_name = file_name.lower().split("(")[0] + ".py"
            return file_name

        if generated_content != "":
            regex = r"(.+?)\n```.*?\n(.*?)```"
            matches = re.finditer(regex, self.generated_content, re.DOTALL)
            for match in matches:
                header_text = match.group(1)
                code = match.group(2)
                if not code or "CODE" in code:
                    continue

                filename = extract_filename_from_line(header_text)

                if "__main__" in code:
                    filename = "main.py"

                if not filename or filename == "":
                    filename = extract_filename_from_code(code)

                assert filename != "" or filename != ".py"
                try:
                    if filename is not None and code is not None and len(filename) > 0 and len(code) > 0:
                        self.codebooks[filename] = self.format_code(code)
                except Exception as e:
                    print(f"Error formatting code for {filename}: {e}")


    def format_code(self, code):
        code = "\n".join([line for line in code.split("\n") if len(line.strip()) > 0])
        return code

    def update_codes(self, generated_content, instance='agent-network'):
        if_change = False
        new_codes = Codes(generated_content)
        if not os.path.exists(static.output_dir):
            os.makedirs(static.output_dir)
        with open(os.path.join(static.output_dir, 'code_change.log'), "a", encoding="UTF-8") as f:
            print('CODING INSTANCE: ' + instance, file=f)
        differ = difflib.Differ()
        for key in new_codes.codebooks.keys():
            if key not in self.codebooks.keys() or self.codebooks[key] != new_codes.codebooks[key]:
                if_change = True
                update_codes_content = "**[Update Codes]**\n\n"
                update_codes_content += "{} updated.\n".format(key)
                old_codes_content = self.codebooks[key] if key in self.codebooks.keys() else "# None"
                new_codes_content = new_codes.codebooks[key]
                if len(new_codes_content) < 20: continue

                lines_old = old_codes_content.splitlines()
                lines_new = new_codes_content.splitlines()

                unified_diff = difflib.unified_diff(lines_old, lines_new, lineterm='', fromfile='Old', tofile='New')
                unified_diff = '\n'.join(unified_diff)
                update_codes_content = update_codes_content + "\n\n" + """```
'''

'''\n""" + unified_diff + "\n```"

                # log_visualize(update_codes_content)
                with open(os.path.join(static.output_dir, 'code_change.log'), "a", encoding="UTF-8") as f:
                    print(update_codes_content, file=f)
                self.codebooks[key] = new_codes.codebooks[key]
        self.rewrite_codes("print", None,
                           os.path.join(self.directory, str(self.version)))
        return if_change

    def rewrite_codes(self, git_management, phase_info=None, directory=None) -> None:
        if directory is None:
            directory = self.directory
        else:
            self.version += 1.0
        rewrite_codes_content = "**[Rewrite Codes]**\n\n"
        # if os.path.exists(directory) and len(os.listdir(directory)) > 0:
        if not os.path.exists(directory):
            os.makedirs(directory)
            rewrite_codes_content += "{} Created\n".format(directory)

        for filename in self.codebooks.keys():
            filepath = os.path.join(directory, filename)
            if "/" in filename:
                file_dir = filepath[:filepath.rfind("/")]
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
            with open(filepath, "w", encoding="utf-8") as writer:
                writer.write(self.codebooks[filename])
                writer.flush()
                rewrite_codes_content += os.path.join(directory, filename) + " Wrote\n"

        # if git_management:
        #     if not phase_info:
        #         phase_info = ""
        #     log_git_info = "**[Git Information]**\n\n"
        #     if self.version == 1.0:
        #         os.system("cd {}; git init".format(self.directory))
        #         log_git_info += "cd {}; git init\n".format(self.directory)
        #     os.system("cd {}; git add .".format(self.directory))
        #     log_git_info += "cd {}; git add .\n".format(self.directory)
        #
        #     # check if there exist diff
        #     completed_process = subprocess.run("cd {}; git status".format(self.directory), shell=True, text=True,
        #                                        stdout=subprocess.PIPE)
        #     if "nothing to commit" in completed_process.stdout:
        #         self.version -= 1.0
        #         return
        #
        #     os.system("cd {}; git commit -m \"v{}\"".format(self.directory, str(self.version) + " " + phase_info))
        #     log_git_info += "cd {}; git commit -m \"v{}\"\n".format(self.directory,
        #                                                               str(self.version) + " " + phase_info)
        #     if self.version == 1.0:
        #         os.system("cd {}; git submodule add ./{} {}".format(os.path.dirname(os.path.dirname(self.directory)),
        #                                                             "WareHouse/" + os.path.basename(self.directory),
        #                                                             "WareHouse/" + os.path.basename(self.directory)))
        #         log_git_info += "cd {}; git submodule add ./{} {}\n".format(
        #             os.path.dirname(os.path.dirname(self.directory)),
        #             "WareHouse/" + os.path.basename(self.directory),
        #             "WareHouse/" + os.path.basename(self.directory))
        # log_visualize(rewrite_codes_content)
        # log_visualize(log_git_info)

    def get_codes(self) -> str:
        content = ""
        for filename in self.codebooks.keys():
            content += "{}\n```{}\n{}\n```\n\n".format(filename,
                                                       "python" if filename.endswith(".py") else filename.split(".")[
                                                           -1], self.codebooks[filename])
        return content

    def load_from_hardware(self, directory) -> None:
        assert len([filename for filename in os.listdir(directory) if filename.endswith(".py")]) > 0
        for root, directories, filenames in os.walk(directory):
            for filename in filenames:
                if self.if_test and filename.endswith(".py") and filename.startswith("test"):
                    code = open(os.path.join(directory, filename), "r", encoding="utf-8").read()
                    self.codebooks[filename] = self.format_code(code)
                if not self.if_test and filename.endswith(".py"):
                    code = open(os.path.join(directory, filename), "r", encoding="utf-8").read()
                    self.codebooks[filename] = self.format_code(code)
        # log_visualize("{} files read from {}".format(len(self.codebooks.keys()), directory))
