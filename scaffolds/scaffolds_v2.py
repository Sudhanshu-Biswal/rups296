"""
RUPS-296 Context Scaffolding Framework — v2
============================================
Validated scaffold preambles for all five failure modes.

Usage:
    from scaffolds.scaffolds_v2 import SCAFFOLDS, build_prompt

    # Build a scaffolded prompt for a problem
    prompt = build_prompt(problem, condition='context_scaffold')

    # Or access scaffolds directly
    preamble = SCAFFOLDS['F1']
"""

# ── Scaffold preambles (v2 — validated) ──────────────────────────────────────
# v1 → v2 changes:
#   F1: Removed "define every field" instruction — caused models to incorrectly
#       define fields rather than interpret them correctly
#   F2: Changed from "reconstruct timeline" to "identify trend direction" —
#       models over-focused on sequence order and missed clinical implication
#   F3: Changed from "flag mismatches" to "convert then compare" —
#       models invented mismatches that didn't exist
#   F5: Complete rewrite — original caused models to justify spurious features
#       rather than ignore them
#   F4: Unchanged from v1 — showed +44% recovery in pilot validation

SCAFFOLDS = {

    'F1': (
        'INSTRUCTION: Field and column names in the following data are precise '
        'technical terms — each has a specific meaning that may not be obvious '
        'from its value alone. Do not guess a field\'s meaning from its number. '
        'If a field name is abbreviated or technical, treat it as domain-specific '
        'terminology before drawing conclusions.'
    ),

    'F2': (
        'INSTRUCTION: The following records are time-ordered. The TREND and '
        'DIRECTION of change matters more than any single value. Before answering, '
        'identify whether each measured variable is improving, worsening, or stable '
        'over time, and what the combined trajectory implies.'
    ),

    'F3': (
        'INSTRUCTION: The following data may contain values in different units or '
        'scales. Before making any comparison or calculation, convert all values '
        'to the same unit. State the unit you are working in at the start of '
        'your answer.'
    ),

    'F4': (
        'INSTRUCTION: The following data contains both positive (present) and '
        'negative (absent/denied) findings. Negative findings are analytically '
        'significant. List all negations explicitly before drawing any conclusions.'
    ),

    'F5': (
        'INSTRUCTION: Assess this individual based solely on their specific '
        'profile values. Do not let category labels (job title, loan purpose, '
        'demographic fields) override what the individual\'s actual metrics show. '
        'Group-level statistics do not predict individual outcomes — focus on '
        'the numbers, not the labels.'
    ),

}


# ── Trigger detector ──────────────────────────────────────────────────────────
# Rule-based classifier that detects structural triggers in the input
# and returns the most likely failure mode(s) to scaffold against.

import re

F1_ABBREVIATION_PATTERNS = [
    r'\b(WBC|Hgb|Plt|Cr|BUN|INR|GCS|SpO2|ALT|AST|ALP|GGT|TSH|BNP|DTI)\b',
    r'\b(revol_util|bc_util|dti|fico|delinq|pub_rec|num_tl|pct_tl)\b',
    r'\b(CLTV|LTV|DSCR|DSO|AR_turnover|EV|EBITDA|YTM|OAS)\b',
    r'\b(no_stock_option|no_overtime_pay|no_training|no_wfh)\b',
]

F2_TEMPORAL_PATTERNS = [
    r'\b(Q[1-4]|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b',
    r'\b(Day \d+|Hour \d+|Month \d+|Year \d{4})\b',
    r'\b(time|timestamp|date|cycle|period|quarter|annual)\b',
    r'(\d{2}:\d{2}|\d{4}-\d{2}-\d{2})',
]

F3_UNIT_PATTERNS = [
    r'\b(mg/dL|mmol/L|mcg|µg|mL/hr|drops/min|bps|basis points)\b',
    r'\b(monthly|annual|quarterly|weekly)\b.*\b(income|revenue|rate|payment)\b',
    r'\b(decimal|percentage|percent|%)\b',
    r'0\.\d{3,}.*\d{1,3}\.\d+',  # decimal and percentage in same context
]

F4_NEGATION_PATTERNS = [
    r'\bno_[a-z_]+\b',
    r'\b(denies|denied|absent|no history|not present|negative for)\b',
    r'=\s*0\b.*\b(no_|not_|absent)',
    r'\b(no ST elevation|denies chest pain|no fever)\b',
]

F5_LABEL_PATTERNS = [
    r'\b(loan_purpose|employment_type|job_role|home_ownership)\b',
    r'\b(self.employed|small.business|debt.consolidation|restaurant)\b',
    r'\b(age|demographic|gender|nationality)\b.*\b(risk|score|rate)\b',
]


def detect_triggers(context: str) -> list:
    """
    Detect structural triggers in a context string.
    Returns a list of suspected failure modes, ordered by confidence.
    """
    context_lower = context.lower()
    suspected = []

    for pattern in F1_ABBREVIATION_PATTERNS:
        if re.search(pattern, context, re.IGNORECASE):
            suspected.append('F1')
            break

    for pattern in F2_TEMPORAL_PATTERNS:
        if re.search(pattern, context, re.IGNORECASE):
            suspected.append('F2')
            break

    for pattern in F3_UNIT_PATTERNS:
        if re.search(pattern, context, re.IGNORECASE):
            suspected.append('F3')
            break

    for pattern in F4_NEGATION_PATTERNS:
        if re.search(pattern, context, re.IGNORECASE):
            suspected.append('F4')
            break

    for pattern in F5_LABEL_PATTERNS:
        if re.search(pattern, context, re.IGNORECASE):
            suspected.append('F5')
            break

    return suspected


# ── Prompt builder ────────────────────────────────────────────────────────────

def build_prompt(problem: dict, condition: str) -> str:
    """
    Build a prompt for a given problem and prompting condition.

    Args:
        problem:   A RUPS-296 problem dict with 'context', 'question', 'failure_mode'
        condition: One of 'baseline', 'cot', 'context_scaffold'

    Returns:
        The full prompt string ready to send to an LLM.
    """
    ctx = problem['context']
    q   = problem['question']

    if condition == 'baseline':
        return f"{ctx}\n\nQuestion: {q}"

    elif condition == 'cot':
        return (
            f"Think carefully step by step before your final answer.\n\n"
            f"{ctx}\n\nQuestion: {q}"
        )

    elif condition == 'context_scaffold':
        # Use labelled failure mode if available, else auto-detect
        fm = problem.get('failure_mode')
        if fm and fm in SCAFFOLDS:
            scaffold = SCAFFOLDS[fm]
        else:
            # Auto-detect from context
            detected = detect_triggers(ctx)
            scaffold = SCAFFOLDS[detected[0]] if detected else ''

        if scaffold:
            return f"{scaffold}\n\n{ctx}\n\nQuestion: {q}"
        else:
            return f"{ctx}\n\nQuestion: {q}"

    else:
        raise ValueError(f"Unknown condition: {condition}. Use 'baseline', 'cot', or 'context_scaffold'.")


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # Test with a sample problem
    sample = {
        'id': 'FIN-F5-001',
        'failure_mode': 'F5',
        'context': 'employment_type: Self-Employed | fico_range: 780-784 | dti: 8.4 | revol_util: 11.2',
        'question': 'Assess the default risk for this applicant.'
    }

    for cond in ['baseline', 'cot', 'context_scaffold']:
        print(f'\n=== {cond.upper()} ===')
        print(build_prompt(sample, cond))

    print('\n=== TRIGGER DETECTION TEST ===')
    test_contexts = [
        "WBC: 18.4 | Hgb: 7.2 | Cr: 3.2 | BUN: 68",
        "Jan: 1 | Feb: 2 | Mar: 3 | Apr: 5 | May: 8",
        "glucose: 7.2 mmol/L | lactate: 4.1 mmol/L",
        "no_PIP_history: 0 | complaint_flag: 1",
        "employment_type: Self-Employed | fico_range: 780-784",
    ]
    expected = ['F1', 'F2', 'F3', 'F4', 'F5']
    for ctx, exp in zip(test_contexts, expected):
        detected = detect_triggers(ctx)
        status = '✅' if exp in detected else '❌'
        print(f'  {status} Expected {exp}, got {detected} | {ctx[:50]}')
