from bs4 import BeautifulSoup

import inquirer
import json

with open('./bpmn/example.bpmn', 'r') as f:
	file = f.read()

soup = BeautifulSoup(file, 'xml')

user_tasks = soup.find_all('bpmn:userTask')

tasks = []

for user_task in user_tasks:
    tasks.append(user_task['id'])

questions = [
    inquirer.List('id', message="What task to generate payload?", choices = tasks)
]

id_task = inquirer.prompt(questions)['id']


q = [
    inquirer.List("required_only", message="Required only?", choices=["yes", "no"], default="no")
]

required_only = inquirer.prompt(q)['required_only'] == 'yes'

task = soup.find('bpmn:userTask', { 'id': id_task})

inputs = {}

for form_field in task.findChildren('camunda:formField'):
    if required_only:
        if form_field.findChildren('camunda:constraint', {'name': 'required'}):
            inputs[form_field['id']] = form_field['type'] if 'type' in form_field.attrs else "none"
    else:
        inputs[form_field['id']] = form_field['type'] if 'type' in form_field.attrs else "none"

print(f"Payload for {id_task}:")
print(json.dumps(inputs, indent=4, ensure_ascii=False))
