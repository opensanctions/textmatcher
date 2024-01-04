import json
import requests
import ahocorasick  # type: ignore
from typing import Optional
from followthemoney import model
from followthemoney.types import registry
from normality import ascii_text
from normality.util import Categories
from normality.scripts import is_latin
from normality.cleaning import category_replace
from normality.constants import WS

URL = 'https://data.opensanctions.org/datasets/latest/sanctions/entities.ftm.json'



NORM_FORM: Categories = {
    "Cc": None,
    "Cf": None,
    "Cs": None,
    "Co": None,
    "Cn": None,
    "Lm": None,
    "Mn": None,
    "Mc": WS,
    "Me": None,
    "No": None,
    "Zs": None,
    "Zl": None,
    "Zp": None,
    "Pc": None,
    "Pd": None,
    "Ps": None,
    "Pe": None,
    "Pi": None,
    "Pf": None,
    "Po": None,
    "Sm": None,
    "Sc": None,
    "Sk": None,
    "So": None,
}


def norm_text(text: Optional[str]) -> Optional[str]:
    ascii = ascii_text(text)
    ascii = category_replace(ascii, NORM_FORM)
    if ascii is not None and len(ascii) > 2:
        return ascii.upper()
    return None


def build_automaton() -> ahocorasick.Automaton:
    automaton = ahocorasick.Automaton()
    res = requests.get(URL, stream=True)
    res.raise_for_status()
    for line in res.iter_lines():
        proxy = model.get_proxy(json.loads(line))
        if not proxy.schema.is_a('LegalEntity'):
            continue
        tokens = set()
        for name in proxy.get_type_values(registry.name, matchable=True):
            if not is_latin(name):
                continue
            norm_name = norm_text(name)
            if norm_name is not None:
                tokens.add(norm_name)
        for tok in tokens:
            automaton.add_word(tok, proxy.id)
    automaton.make_automaton()
    return automaton

    
if __name__ == '__main__':
    aut = build_automaton()
    text = 'My name is Vladimir Putin, I am the President of Russia'
    for match in aut.iter(norm_text(text)):
        print(match)