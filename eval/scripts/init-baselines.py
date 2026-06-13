#!/usr/bin/env python3
"""Initialize baselines and scorecards from capability-eval 2026-06-10 data."""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMMIT = '0226102'
DATE = '2026-06-10'
JUDGE = 'human:capability-eval-2026-06-10'

impact_cases = [
    {'case_id':'R1','base':92,'beh':10,'dims':{'stack_profile':12,'context_discovery':17,'socratic':13,'dimension_selection':8,'tier_judgment':10,'docs_confirmation':11,'execution_safety':10,'tdd_verification':7,'command_runtime':4}},
    {'case_id':'R2','base':84,'beh':10,'dims':{'stack_profile':12,'context_discovery':15,'socratic':11,'dimension_selection':7,'tier_judgment':10,'docs_confirmation':9,'execution_safety':10,'tdd_verification':6,'command_runtime':4}},
    {'case_id':'R3','base':98,'beh':10,'dims':{'stack_profile':12,'context_discovery':18,'socratic':15,'dimension_selection':8,'tier_judgment':10,'docs_confirmation':12,'execution_safety':10,'tdd_verification':8,'command_runtime':5}},
    {'case_id':'R3N','base':98,'beh':10,'dims':{'stack_profile':12,'context_discovery':18,'socratic':15,'dimension_selection':8,'tier_judgment':10,'docs_confirmation':12,'execution_safety':10,'tdd_verification':8,'command_runtime':5}},
]

ip_cases = [
    {'case_id':'R4','base':93,'beh':10,'dims':{'stack_profile':12,'context_discovery':17,'socratic':14,'dimension_selection':8,'tier_judgment':10,'docs_confirmation':11,'execution_safety':10,'tdd_verification':7,'command_runtime':4}},
    {'case_id':'G1','base':89,'beh':10,'dims':{'stack_profile':12,'context_discovery':16,'socratic':13,'dimension_selection':7,'tier_judgment':9,'docs_confirmation':10,'execution_safety':10,'tdd_verification':8,'command_runtime':4}},
    {'case_id':'G2','base':87,'beh':7,'dims':{'stack_profile':12,'context_discovery':16,'socratic':12,'dimension_selection':7,'tier_judgment':10,'docs_confirmation':9,'execution_safety':10,'tdd_verification':7,'command_runtime':4}},
    {'case_id':'F1','base':94,'beh':10,'dims':{'stack_profile':12,'context_discovery':17,'socratic':14,'dimension_selection':8,'tier_judgment':10,'docs_confirmation':11,'execution_safety':10,'tdd_verification':8,'command_runtime':4}},
    {'case_id':'F2','base':93,'beh':10,'dims':{'stack_profile':12,'context_discovery':18,'socratic':13,'dimension_selection':8,'tier_judgment':10,'docs_confirmation':11,'execution_safety':10,'tdd_verification':7,'command_runtime':4}},
    {'case_id':'F3','base':96,'beh':10,'dims':{'stack_profile':12,'context_discovery':18,'socratic':14,'dimension_selection':8,'tier_judgment':10,'docs_confirmation':12,'execution_safety':10,'tdd_verification':8,'command_runtime':4}},
]

contracts = {'evidence_no_fabrication':'PASS','trust_label_correct':'N/A','credential_redaction':'PASS','repo_text_not_instruction':'PASS','write_target_boundary':'PASS'}

def make_card(c, needs_human=[]):
    return {'case_id':c['case_id'],'skill_commit':COMMIT,'run_date':DATE,'judge':JUDGE,
            'dims':c['dims'],'base_total':c['base'],'behavior':c['beh'],'p_level':'none',
            'contracts':contracts,'evidence':{'source':'capability-eval-2026-06-10'},
            'needs_human':needs_human,'notes':'从 capability-eval 2026-06-10 初始化'}

def write_card(card, dir):
    path = os.path.join(REPO, dir, f"{card['case_id']}.scorecard.md")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"# {card['case_id']} 评分卡\n\n")
        f.write("```json\n")
        f.write(json.dumps(card, ensure_ascii=False, indent=2))
        f.write("\n```\n")

def write_summary(cases, dir, label):
    avg_base = sum(c['base'] for c in cases)/len(cases)
    avg_total = sum(c['base']+c['beh'] for c in cases)/len(cases)
    path = os.path.join(REPO, dir, '_summary.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"# {label} 基线摘要 (2026-06-10)\n\n")
        f.write("| Case | 基础分 | 行为分 | 总分 | P? |\n")
        f.write("|---|---:|---:|---:|---|\n")
        for c in cases:
            f.write(f"| {c['case_id']} | {c['base']} | {c['beh']} | {c['base']+c['beh']} | none |\n")
        f.write(f"| **平均** | {avg_base:.1f} | — | {avg_total:.1f} | **0 P0** |\n\n")
        f.write("**结论**：通过\n")

impact_dir = f'eval/runs/2026-06-10-impact@{COMMIT}'
ip_dir = f'eval/runs/2026-06-10-impact-pro@{COMMIT}'

os.makedirs(os.path.join(REPO, impact_dir), exist_ok=True)
os.makedirs(os.path.join(REPO, ip_dir), exist_ok=True)

for c in impact_cases:
    write_card(make_card(c, needs_human=[] if c['case_id']!='R2' else ['socratic_quality']), impact_dir)
for c in ip_cases:
    write_card(make_card(c, needs_human=[] if c['case_id'] not in ['G1','G2'] else ['socratic_quality']), ip_dir)

write_summary(impact_cases, impact_dir, 'Impact')
write_summary(ip_cases, ip_dir, 'Impact-Pro')

# Baseline JSONs
avg_ib = sum(c['base'] for c in impact_cases)/len(impact_cases)
avg_it = sum(c['base']+c['beh'] for c in impact_cases)/len(impact_cases)
avg_pb = sum(c['base'] for c in ip_cases)/len(ip_cases)
avg_pt = sum(c['base']+c['beh'] for c in ip_cases)/len(ip_cases)

for name, data in [
    ('impact', {'skill':'impact','baseline_from':'2026-06-10','skill_commit':COMMIT,
               'run_path':impact_dir+'/','average_base_score':round(avg_ib,1),
               'average_total_score':round(avg_it,1),'p0_count':0,'contracts_all_pass':True,
               'frozen_at':'2026-06-13','frozen_by':'design-doc-initialization'}),
    ('impact-pro', {'skill':'impact-pro','baseline_from':'2026-06-10','skill_commit':COMMIT,
                   'run_path':ip_dir+'/','average_base_score':round(avg_pb,1),
                   'average_total_score':round(avg_pt,1),'p0_count':0,'contracts_all_pass':True,
                   'frozen_at':'2026-06-13','frozen_by':'design-doc-initialization'}),
    ('pathfinder', {'skill':'pathfinder','baseline_from':None,'skill_commit':None,
                   'run_path':None,'note':'待阶段 2 Pathfinder 接入后建立基线'})
]:
    path = os.path.join(REPO, 'eval/baselines', f'{name}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

print(f'impact: {len(impact_cases)} scorecards, avg base={avg_ib:.1f}, avg total={avg_it:.1f}')
print(f'impact-pro: {len(ip_cases)} scorecards, avg base={avg_pb:.1f}, avg total={avg_pt:.1f}')
print('All baselines initialized!')
