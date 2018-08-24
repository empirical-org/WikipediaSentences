#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper methods for preprocessing sentences"""
import textacy

def preprocess_sent(sentence_str):
    """Simple preprocessing to normalize whitespace, unpack contractions"""
    sentence_str = textacy.preprocess.normalize_whitespace(sentence_str)
    sentence_str = textacy.preprocess.unpack_contractions(sentence_str)
    return sentence_str
