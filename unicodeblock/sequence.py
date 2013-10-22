import blocks


class UnicodeSequence(object):
    def __init__(self, val, lang):
        self.value = val
        self.lang = lang

    def __str__(self):
        return self.value.encode('utf-8')

    def __unicode__(self):
        return self.value

    def __repr__(self):
        return str(self)


def _init_states():
    class State(dict):
        def __init__(self, lang, d=None):
            dict.__init__(self, d or dict())
            self.lang = lang

        def next(self, ch):
            cht = blocks.of(ch)
            if cht in self:
                return self[cht](ch)
            return None

    number = State('digit')
    basic_latin = State('en')
    ext_latin = State('latin')
    basic_cjk = State('cjk')
    ja = State('ja')

    number['DIGIT'] = lambda _: number
    basic_latin['BASIC_LATIN'] = lambda _: basic_latin
    basic_latin['BASIC_PUNCTUATION'] = (
        lambda c: basic_latin if c == "'" or c == '-' else None)
    basic_latin['LATIN_EXTENDED_LETTER'] = lambda _: ext_latin
    ext_latin['BASIC_LATIN'] = lambda _: ext_latin
    ext_latin['BASIC_PUNCTUATION'] = (
        lambda c: ext_latin if c == "'" or c == '-' else None)
    ext_latin['LATIN_EXTENDED_LETTER'] = lambda _: ext_latin
    basic_cjk['CJK_UNIFIED_IDEOGRAPHS'] = lambda _: basic_cjk
    basic_cjk['HIRAGANA'] = lambda _: ja
    basic_cjk['KATAKANA'] = lambda _: ja
    ja['CJK_UNIFIED_IDEOGRAPHS'] = lambda _: ja
    ja['HIRAGANA'] = lambda _: ja
    ja['KATAKANA'] = lambda _: ja

    return State(None, {
        'DIGIT': lambda _: number,
        'BASIC_LATIN': lambda _: basic_latin,
        'CJK_UNIFIED_IDEOGRAPHS': lambda _: basic_cjk,
        'HIRAGANA': lambda _: ja,
        'KATAKANA': lambda _: ja,
    })

_START = _init_states()


def usplit(u):
    begin = 0
    record = False
    seqs = []
    state = _START

    for index, ch in enumerate(u):
        next_state = state.next(ch)
        if next_state is not None:
            state = next_state
            if not record:
                record = True
                begin = index
            continue
        if record:
            seqs.append(UnicodeSequence(u[begin: index], state.lang))
            record = False
        next_state = _START.next(ch)
        if next_state is None:
            state = _START
            continue
        state = next_state
        record = True
        begin = index

    if record:
        seqs.append(UnicodeSequence(u[begin:], state.lang))
    return seqs
