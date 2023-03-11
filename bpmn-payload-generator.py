from bs4 import BeautifulSoup

import inquirer
import json

with open("./bpmn/example.bpmn", "r") as f:
    file = f.read()

soup = BeautifulSoup(file, "xml")

user_tasks = soup.find_all("bpmn:userTask")

tasks = []

for user_task in user_tasks:
    tasks.append(user_task["id"])

questions = [
    inquirer.List(
        "id", message="What task to generate payload?", choices=tasks, carousel=True
    )
]

id_task = inquirer.prompt(questions)["id"]


q = [
    inquirer.List(
        "required_only",
        message="Required only?",
        choices=["yes", "no"],
        default="no",
        carousel=True,
    )
]

required_only = inquirer.prompt(q)["required_only"] == "yes"

task = soup.find("bpmn:userTask", {"id": id_task})

inputs = {}

form_fields = task.findChildren("camunda:formField")

object_fields = []

for input_object in task.find_all("camunda:inputParameter"):
    if input_object["name"].endswith("_object"):
        nome_input = input_object["name"].removesuffix("_object")
        inputs[nome_input] = {}

        for value in input_object.find_all("camunda:value"):
            inputs[nome_input][value.text] = "valor"
            object_fields.append(value.text)


for form_field in form_fields:
    if form_field["id"] in object_fields or form_field["type"] == "object":
        continue

    if required_only:
        if form_field.findChildren("camunda:constraint", {"name": "required"}):
            inputs[form_field["id"]] = (
                form_field["type"] if "type" in form_field.attrs else "none"
            )
    else:
        inputs[form_field["id"]] = (
            form_field["type"] if "type" in form_field.attrs else "none"
        )


print(f"Payload for {id_task}:")
print(json.dumps(inputs, indent=4, ensure_ascii=False))
