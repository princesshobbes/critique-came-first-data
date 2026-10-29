"""Recompute the numbers in Section III and the tables of "The Critique Came First" (working paper v1, October 2026)
from the released data file, critique_came_first_data.csv.

Usage:   python3 critique_came_first_recompute.py critique_came_first_data.csv
Needs:   Python 3.9 or later and SciPy 1.10 or later (for exact odds ratio intervals).

Every block below is labeled with the place in the paper it checks. The script reads only the
data file and the DOIs of the 19 check list critiques (Appendix C; full entries in the References).
"""
import csv, collections, math, statistics, sys
from scipy.stats import fisher_exact
from scipy.stats.contingency import odds_ratio

# Appendix C: 19 critiques published before the notes, listed before the corpus rules were run.
# They are used to measure recall and, because all predate the notes, as citation targets for
# "cites an earlier critique" (Section II.F).
CHECK_LIST = """10.1177/0956797616678438 10.1177/2167702617750869 10.1038/d41586-018-02109-8
10.1038/s41562-018-0506-1 10.1177/2167702618812727 10.1177/0956797619830329 10.1073/pnas.1902058116
10.1177/2167702619849412 10.1177/2167702619859336 10.1177/1089268019880891 10.1007/s00127-019-01825-4
10.1111/jcpp.13190 10.1016/j.chb.2019.106160 10.1038/s41562-020-0840-y 10.1177/1745691620919372
10.1038/s41598-020-67727-7 10.1177/2167702621994549 10.1016/j.copsyc.2021.08.017 10.1037/pro0000426""".split()

def split(s): return [t for t in (s or "").split("; ") if t]

W = list(csv.DictReader(open(sys.argv[1], newline="", encoding="utf-8")))
for w in W:
    w["refs"] = set(split(w["resolved_reference_dois"])); w["dois"] = set(split(w["all_version_dois"]))
    w["au"] = set(split(w["author_keys"]))

def pct(a, b): return f"{100 * a / b:.1f}%" if b else "n/a"
def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"[{100 * (c - h):.1f}, {100 * (c + h):.1f}]"
def test(label, table):
    r = odds_ratio(table, kind="conditional"); ci = r.confidence_interval(0.95); p = fisher_exact(table)[1]
    print(f"   {label}: OR {r.statistic:.2f} (95% CI {ci.low:.2f} to {ci.high:.2f}), Fisher p = {p:.4f}")

print("== Corpus size:", len(W), "works")
print("\n== Table 1: works by period and stance")
for per in ("pre", "boundary", "post"):
    c = collections.Counter(w["final_stance"] for w in W if w["period"] == per)
    print(f"   {per:9s} C {c['C']:4d}  S {c['S']:4d}  N {c['N']:5d}  total {sum(c.values())}")
c = collections.Counter(w["final_stance"] for w in W); print(f"   all       C {c['C']:4d}  S {c['S']:4d}  N {c['N']:5d}")

print("\n== Section II.A: entry routes (a work can enter by more than one)")
rc = collections.Counter(t for w in W for t in set(split(w["entry_routes"])))
print("  ", dict(rc), "| citation route only:", sum(1 for w in W if split(w["entry_routes"]) == ["cites an anchor work"]))

print("\n== Figure 1: works per half year (all dated works, boundary month included)")
hy = collections.defaultdict(collections.Counter)
for w in W:
    d = w["first_appearance"]; hy[f"{d[:4]}H{1 if int(d[5:7]) <= 6 else 2}"][w["final_stance"]] += 1
for k in sorted(hy):
    cs = hy[k]["C"] + hy[k]["S"]; print(f"   {k}: C {hy[k]['C']:3d}  S {hy[k]['S']:3d}  critique share {pct(hy[k]['C'], cs)}")

def window(col, a1, b1, a2, b2, label):
    f = lambda a, b, s: sum(1 for w in W if a <= w["first_appearance"] < b and w[col] == s)
    c1, s1, c2, s2 = f(a1, b1, "C"), f(a1, b1, "S"), f(a2, b2, "C"), f(a2, b2, "S")
    print(f"   {label}: before {c1}/{c1 + s1} ({pct(c1, c1 + s1)})  after {c2}/{c2 + s2} ({pct(c2, c2 + s2)})")
    test("after vs before", [[c2, s2], [c1, s1]])
print("\n== Table 2: critique share of C and S works before and after the notes")
for col, tag in (("final_stance", "verified"), ("first_pass_stance", "first pass")):
    window(col, "2021-03-01", "2023-03-01", "2023-04-01", "2025-04-01", f"24 months, {tag}")
    window(col, "2022-03-01", "2023-03-01", "2023-04-01", "2024-03-01", f"12 months before, 11 after, {tag}")

def continuity(col, use_check_list=True, title=""):
    pre = lambda s: [w for w in W if w["period"] == "pre" and w[col] == s]
    preC_d = set().union(*[w["dois"] for w in pre("C")]) | (set(CHECK_LIST) if use_check_list else set())
    preS_d = set().union(*[w["dois"] for w in pre("S")])
    preC_a = set().union(*[w["au"] for w in pre("C")]); preS_a = set().union(*[w["au"] for w in pre("S")])
    out = {}
    print(f"\n== {title}")
    for lab, side, start in (("later C", "C", "2023-04-01"), ("later S", "S", "2023-04-01"), ("C 2024 on", "C", "2024-01-01"), ("S 2024 on", "S", "2024-01-01")):
        g = [w for w in W if w["period"] == "post" and w[col] == side and w["first_appearance"] >= start]
        own_d, oth_d, own_a = (preC_d, preS_d, preC_a) if side == "C" else (preS_d, preC_d, preS_a)
        wr = [w for w in g if len(w["refs"]) >= 5]
        own = [w for w in wr if w["refs"] & own_d]; oth = [w for w in wr if w["refs"] & oth_d]
        nr = [len(w["refs"]) for w in wr]; on = [len(w["refs"] & own_d) for w in wr]; ot = [len(w["refs"] & oth_d) for w in wr]
        au = [w for w in g if w["au"] & own_a]
        print(f"   {lab}: works {len(g)}, with >=5 resolved refs {len(wr)}; cite earlier same side {len(own)} ({pct(len(own), len(wr))}); "
              f"other side {len(oth)} ({pct(len(oth), len(wr))}); median refs {statistics.median(nr)}; median same side {statistics.median(on)}; "
              f"other side {statistics.median(ot)}; pooled same {100 * sum(on) / sum(nr):.1f}%, other {100 * sum(ot) / sum(nr):.1f}%; "
              f"author continuity {len(au)} ({pct(len(au), len(g))})")
        out[lab] = (g, wr, own, oth, au, preC_d, preC_a)
    return out

R = continuity("final_stance", True, "Table 3 and Sections III.C to III.D: continuity, verified codes")
gC, wrC, ownC, _, auC, preC_d, preC_a = R["later C"]; gS, wrS, _, othS, auS, _, _ = R["later S"]
print("\n== Section III.C and III.D: comparisons, later C vs later S")
print(f"   cite an earlier critique: C {len(ownC)}/{len(wrC)} {pct(len(ownC), len(wrC))} {wilson(len(ownC), len(wrC))}  vs  S {len(othS)}/{len(wrS)} {pct(len(othS), len(wrS))} {wilson(len(othS), len(wrS))}")
test("cite an earlier critique", [[len(ownC), len(wrC) - len(ownC)], [len(othS), len(wrS) - len(othS)]])
print(f"   same side author continuity: C {len(auC)}/{len(gC)} {pct(len(auC), len(gC))} {wilson(len(auC), len(gC))}  vs  S {len(auS)}/{len(gS)} {pct(len(auS), len(gS))} {wilson(len(auS), len(gS))}")
test("author continuity", [[len(auC), len(gC) - len(auC)], [len(auS), len(gS) - len(auS)]])
pre = collections.Counter(w["final_stance"] for w in W if w["period"] == "pre")
print(f"   earlier supportive / earlier critique works: {pre['S']}/{pre['C']} = {pre['S'] / pre['C']:.2f}")

print("\n== Section III.E: later critiques with neither link")
none = [w for w in gC if not (w["au"] & preC_a) and not (w["refs"] & preC_d)]
print(f"   {len(none)} works; with fewer than 5 resolved refs: {sum(1 for w in none if len(w['refs']) < 5)}")
for w in none: print(f"     {w['first_appearance']} refs {len(w['refs']):3d} | {w['title'][:90]}")

print("\n== Section III.F: Crossref funder metadata naming Meta, Facebook or Instagram")
import re
for w in W:
    if re.search(r"\bmeta\b|facebook|instagram", w["crossref_funders"], re.I):
        print(f"   {w['final_stance']} (first pass {w['first_pass_stance']}) {w['period']} {w['doi']} | {w['crossref_funders']}")

print("\n== Section III.G: first pass codes")
F = continuity("first_pass_stance", True, "continuity, first pass codes")
fp = collections.Counter((w["period"], w["first_pass_stance"]) for w in W)
print("   first pass C/S works:", sum(v for (p, s), v in fp.items() if s == "C"), "/", sum(v for (p, s), v in fp.items() if s == "S"))

print("\n== Section II.E: verification changes (final deduplication)")
vc = collections.Counter()
for w in W:
    for ch in [t for t in w["verification_change"].split(" | ") if t]:
        stage, rest = ch.split(": ", 1); vc[(stage, rest[:4])] += 1
for k, v in sorted(vc.items()): print("  ", k, v)
print("   works reset by the book review rule before verification:", sum(1 for w in W if w["note"]))

print("\n== Section II.E: check list recall")
inl = [w for w in W if w["on_check_list"] == "yes"]
print(f"   check list works in corpus: {len(inl)} of {len(CHECK_LIST)}; codes {dict(collections.Counter(w['final_stance'] for w in inl))}")

print("\n== Section II.D: reliability sample (record level)")
pairs = [(a, b) for w in W if w["reliability_second_pass"] for a, b in zip(w["reliability_first_pass"].split("/"), w["reliability_second_pass"].split("/"))]
n = len(pairs); po = sum(a == b for a, b in pairs) / n
ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
pe = sum(ca[k] * cb[k] for k in "CSN") / n / n
print(f"   n {n}, agreement {100 * po:.1f}%, kappa {(po - pe) / (1 - pe):.2f}, disagreements {dict(collections.Counter(f'{a}->{b}' for a, b in pairs if a != b))}")

continuity("final_stance", False, "Sensitivity: continuity without the check list DOIs as citation targets")

print("\n== Section III.B: shorter window extended through March 2024 (verified codes)")
window("final_stance", "2022-03-01", "2023-03-01", "2023-04-01", "2024-04-01", "12 months before, 12 after")

print("\n== Section III.F: Minich and Moreno (2024) coded C instead of N")
_orig = list(W)
W[:] = [dict(w, final_stance="C") if w["doi"] == "10.1371/journal.pone.0298422" else w for w in _orig]
window("final_stance", "2021-03-01", "2023-03-01", "2023-04-01", "2025-04-01", "24 months, verified, Minich as C")
continuity("final_stance", True, "continuity with Minich as C")
W[:] = _orig
