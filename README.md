# mykrobe-lineage-test

This repository contains code for testing mykrobe species and lineage calls,
and results of the testing.
It is intended for mykrobe developers, for testing mykrobe species/lineage calls
and tracking the results.

There are two directories:

1. `Python/`: this contains the code, and a Singularity definition file that
makes a container with the code plus the dependencies.
2. `Analysis/`: contains results of testing mykrobe species and lineage calls.

For results, please see the readme in the `Analysis/` directory.


## Installation

This repository has a main script called `mlt` (acronym for "mykrobe lineage
test", yes we are testing species calls as well but
"mykrobe lineage species test" seemed like a bad name!).

### Singularity

The easiest way is to build a singularity container.
```
cd Python
sudo singularity build mlt Singularity.def
```
Run like that, singularity will make a container file called `mlt`.
You can just treat it as an normal executable, no need to run
`singularity exec mlt` unless you want to.

### Source

If you want to run locally, then you will need these in your `$PATH`:
* `enaDataGet`, which is from enaBrowserTools (have a look in `Singularity.def`)
* `mykrobe`.
* (also `fastaq` and `ncbi-genome-download` are required, but are installed when
  you install `mlt` because they are in the requirements file.)

Then run `pip install .` from the `Python/` directory. The required python
packages will be installed (they are in `requirements.txt`).

Alternatively, you could not do pip install, and instead do this:
```
PYTHONPATH=/path_to/mykrobe-lineage-test/Python /path_to/mykrobe-lineage-test/Python/mlt/__main__.py
```
That command is equivalent to running the script `mlt`.


## Testing lineage calls

In short, the process is:

1. Put your sample info in a TSV file.
2. Download reads using `mlt download_data`
3. Run mykrobe on all samples using `mlt run_mykrobe`
4. Make a summary of the results using `mlt summary`.


### sample TSV

All the commands need a TSV of sample information. The format is like
this (this is made up data!):
```
accession   source  species                     lineage
SRR12345678 ena     Mycobacterium_tuberculosis  lineage1.2.3
GCF_1234567 genbank Mycobacterium_tuberculosis  lineage2.3.4
XY123456    refseq  Mycobacterium_tuberculosis  lineage3.4
```
You must have columns `accession`, `source`, `species` and `lineage`. They
can be in any order (and any extra columns are ignored). The lineage can
be "NA" if there is no lineage call and you just want to test the species
call.

The source must be `ena`, `genbank`, or `refseq`, and the `accession` column
should have the corresponding ENA run ID, or genbank/refseq genome accession.
Since reads are needed for mykrobe, reads are simulated from genomes using
`fastaq to_perfect_reads`, making perfect reads (ie no snp/indel errors)
of length 75bp, fragment size 200, and depth 20X.


### Download data

With a TSV file of samples `samples.tsv` in the above format, run:
```
mlt download_data --cpus 3 samples.tsv Reads
```
That example downloads 3 samples in parallel. It makes a directory called
`Reads` containing the downloaded data. It will (well, _should_) not crash
on failed downloads, but carry on and get all the samples it can. Check
stderr to see what happened.

You can rerun on an existing directory and it will only try to get data
that is missing and skip the samples that are already downloaded.
This also means you can do hacks like different sample TSV files run
against the same directory of a superset of reads, if you're feeling
fancy.

### Run mykrobe

Assuming you have a directory of downloaded reads from `mlt download_data`
called `Reads/`:
```
mlt run_mykrobe --cpus 10 samples.tsv Reads Results
```
That will run 10 samples in parallel. It makes a new directory (if it
doesn't exit already) called `Results`. As for `download_data`, you can
rerun against the same directory and it will only run samples that do not
already have a mykrobe json file of results. It will ignore samples in the TSV
with no reads in  `Reads/`. It's up to you to use the right TSV file/Reads
directory/results directory - there is no sanity checking. This does allow
for more hacking and testing of samples.

IMPORTANT: the first time a sample is run in `Results/`, there is no
skeletons file. If you ask for more than one CPU, the first sample will be
run on its own, making the skeletons file. Then the remaining samples are
run using multiprocessing, since they can then all use the skeletons file,
instead of all trying to make one at the same time and crashing.

There is an option `--panels_dir`, which will use that option with mykrobe,
so that you can override the default panels directory and use your own.
You probably want this, since the point here is to test species/lineage calls.
It is not recommended to change the panel and then use an existing results
directory because the skeletons file that is already might be used!

### Summarise results

Assuming you have a samples TSV file `samples.tsv`, a directory of reads
called `Reads/`, and a directory of mykrobe runs called `Results/`:
```
mlt summary samples.tsv Reads Results summary.tsv
```
That makes a new TSV file called `summary.tsv`. It is the same as `samples.tsv`,
but with added columns:
* `called_species` and `called_lineage`. These are the calls made by mykrobe.
* `correct`: this is `true|false`, showing if the both the called species and
  lineage were correct. If the expected lineage is "NA", then the true/false
  call only depends on the species.

Now be good and record the results in the `Analysis/` directory and push
to github.
