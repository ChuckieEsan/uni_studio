from studio import r
sname = 'studio:global_interceptor'
def get_rules()->set:
    rules = set([])
    for path in r.smembers(sname):
        rules.add(str(path,encoding='utf-8'))
    return rules

def add_rule(rule:str):
    r.sadd(sname,rule)

def remove_rule(rule:str): 
    r.srem(sname,rule)   