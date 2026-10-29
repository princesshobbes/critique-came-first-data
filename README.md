# critique-came-first-data

Data and code for Gilly, T. (2026). *The Critique Came First: Citation and Authorship Continuity in Academic Challenges to the Youth Social Media Harm Thesis Before and After Meta's March 2023 Notes*. Working paper, Real Safety AI Foundation.

The paper tests whether academic critique of the claim that smartphones and social media drove the rise in adolescent depression and anxiety changed after Meta's internal notes of 7 and 8 March 2023. Methods, coding rules and limitations are in the paper.

## Files

| File | What it is |
|---|---|
| `critique_came_first_data.csv` | One row per work: 2,032 works from January 2017 to October 2026 that engage the harm thesis |
| `critique_came_first_recompute.py` | Recomputes the results in Section III and the tables of the paper from the CSV |

## Running the script

```
python3 critique_came_first_recompute.py critique_came_first_data.csv
```

Needs Python 3.9 or later and SciPy 1.10 or later. Output is labeled by the section or table of the paper it checks.

## Columns

| Column | Meaning |
|---|---|
| `work_id` | Identifier for the work (one work can join several versions, such as a preprint and a journal article) |
| `first_appearance` | Earliest public date of any version (YYYY-MM-DD) |
| `period` | `pre` (on or before 2023-02-28), `boundary` (March 2023, excluded from comparisons), or `post` (on or after 2023-04-01) |
| `final_stance` | Final code: `C` critique, `S` supportive, `N` neither |
| `first_pass_stance` | Code before verification |
| `verification_change` | Each change made during verification, with its stage and rule; changes separated by ` \| ` |
| `note` | Set when a book review coded from its title was reset to N before verification |
| `title` | Title |
| `doi` | Main DOI |
| `all_version_dois` | DOIs of every version of the work |
| `authors` | Author names as indexed |
| `author_keys` | Surname and first initial used for author matching (`surname\|initial`) |
| `n_resolved_references` | Number of references matched to a DOI |
| `resolved_reference_dois` | DOIs of those references |
| `entry_routes` | How the work entered the corpus: citing an anchor work, title and abstract search, or full text search |
| `on_check_list` | `yes` if the work is one of the 19 earlier critiques listed in Appendix C of the paper |
| `crossref_funders` | Funder names in the Crossref record |
| `reliability_first_pass`, `reliability_second_pass` | Codes from the two coding passes for the 110 records in the reliability sample |

List fields are separated by a semicolon followed by a space (`; `). Split on that exact string, since a few older Wiley DOIs contain a bare semicolon.

The seven check list critiques that are not in the corpus are counted as citation targets in the continuity measure. Their DOIs are listed in the script and in the paper's references.

## License

MIT. Reuse is permitted with credit; keep the copyright notice and cite the paper.
