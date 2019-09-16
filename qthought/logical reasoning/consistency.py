"""
Author: Simon Mathis (mathissi@ethz.ch)
Date: 25.12.2018

Library corresponding to assumption C in the RF paper.
Contains the semantics of the inference, i.e. the updating of inference
tables.
"""
from .agents import InferenceTable


def consistency(tbl_pre: InferenceTable, tbl_post: InferenceTable):
    """
    Maps inputs form tbl_pre to tbl_post.
    I.e. this funciton implements the consistency rule (C) in the Frauchiger-Renner paper
    in terms of inference table updates.
    """
    assert tbl_pre['output'] == tbl_post['input'], 'Output of tbl_pre (%s:t%d) does not' \
                                                   ' match Input of tbl_post(%s:t%d)' % (
                                                       tbl_pre['output'][0], tbl_pre['output'][1],
                                                       tbl_post['input'][0], tbl_post['input'][1])

    tbl_combined = {inpt: [] for inpt in tbl_pre['table'].keys()}

    for inpt, val_list in tbl_pre['table'].items():
        for val in val_list:
            tbl_combined[inpt] += tbl_post['table'][val]

    for key, val in tbl_combined.items():
        tbl_combined[key] = list(set(val))

    return InferenceTable(tbl_pre['input'][0], tbl_pre['input'][1],
                          tbl_post['output'][0], tbl_post['output'][1], tbl_combined)
