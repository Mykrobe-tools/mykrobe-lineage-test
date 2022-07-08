# Mykrobe species/lineage test results

| file                   | mykrobe version | main panel version | panel  |
| :---                   | :---            | :---               | :---   |
| `results.202010.tsv`   | v0.11.0         | tb 20201014        | 202010 |
| `results.20200705.tsv` | v0.12.1         | tb 20220705        | 202206 |

"main panel version" is the version you see in the "Species summary" section
when running `mykrobe panels describe". eg (showing the TB row only, not other
species):
```
$ mykrobe panels describe

Species summary:

Species Update_available Installed_version  Installed_url                                   Latest_version  Latest_url
tb      no               20201014           https://ndownloader.figshare.com/files/25103438	20201014        https://ndownloader.figshare.com/files/25103438
```

"panel" is the actual panel used. eg at the time of writing, panel 202010
was the default panel for the main panel download version 20201014.

# Notes

## `results.202010.tsv`

This is using latest mykrobe (at the time of
writing) v0.11.0, and the latest TB panel. The samples used were the same
as those used when lineage calling was updated in 2020 - details are in
the mykrobe github issue https://github.com/Mykrobe-tools/mykrobe/issues/94.
We essentially reproduce here there results that were in that issue. The
only "disagreements" are where mykrobe calls a sublineage of the expected
lineage:

```
$ grep -v True results.202010.tsv  | column -t
accession   source  species                     lineage       called_species              called_lineage    correct
SRR6650384  ena     Mycobacterium_tuberculosis  lineage4.1.1  Mycobacterium_tuberculosis  lineage4.1.1.3    False
ERR1465801  ena     Mycobacterium_tuberculosis  lineage4.1.2  Mycobacterium_tuberculosis  lineage4.1.2.1    False
SRR6896506  ena     Mycobacterium_tuberculosis  lineage4.3.2  Mycobacterium_tuberculosis  lineage4.3.2.1    False
ERR161193   ena     Mycobacterium_tuberculosis  lineage4.3.4  Mycobacterium_tuberculosis  lineage4.3.4.2.1  False
ERR228067   ena     Mycobacterium_tuberculosis  lineage4.4.1  Mycobacterium_tuberculosis  lineage4.4.1.1    False
ERR1199080  ena     Mycobacterium_tuberculosis  lineage4.6.1  Mycobacterium_tuberculosis  lineage4.6.1.1    False
```

## `results.20200705.tsv`

This is using mykrobe version 0.12.1, main panel 20220705 version, and its
default panel 202206. Since making `results.202010.tsv`, calling bovis/BCG was
fixed. Found that `ERR161048` was really BCG, so its expected lineage call was
changed from bovis to BCG. 49 more BCG samples, and 50 bovis samples were added
to the test samples. All previous test samples remained the same.

As for `results.202010.tsv`, the
only "disagreements" are where mykrobe calls a sublineage of the expected
lineage:

```
$ grep -v True results.20220705.tsv | column -t
accession   source  species                     lineage       called_species              called_lineage    correct
SRR6650384  ena     Mycobacterium_tuberculosis  lineage4.1.1  Mycobacterium_tuberculosis  lineage4.1.1.3    False
ERR1465801  ena     Mycobacterium_tuberculosis  lineage4.1.2  Mycobacterium_tuberculosis  lineage4.1.2.1    False
SRR6896506  ena     Mycobacterium_tuberculosis  lineage4.3.2  Mycobacterium_tuberculosis  lineage4.3.2.1    False
ERR161193   ena     Mycobacterium_tuberculosis  lineage4.3.4  Mycobacterium_tuberculosis  lineage4.3.4.2.1  False
ERR228067   ena     Mycobacterium_tuberculosis  lineage4.4.1  Mycobacterium_tuberculosis  lineage4.4.1.1    False
ERR1199080  ena     Mycobacterium_tuberculosis  lineage4.6.1  Mycobacterium_tuberculosis  lineage4.6.1.1    False
```
