import re
pattern = r'\{([^}:]+)(:[^}]+)?\}'
template = "我叫{name}我的年龄是{age:28}"
matches = re.findall(pattern, template)
print(matches)