import json
import logging
import os
import subprocess
import sys


def syscall(command, cwd=None):
    logging.info(f"Run command: {command}")
    completed_process = subprocess.run(
        command,
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True,
        cwd=cwd,
    )
    logging.info(f"Return code: {completed_process.returncode}")
    if completed_process.returncode != 0:
        print("Error running this command:", command, file=sys.stderr)
        print("Return code:", completed_process.returncode, file=sys.stderr)
        print(
            "Output from stdout:", completed_process.stdout, sep="\n", file=sys.stderr
        )
        print(
            "Output from stderr:", completed_process.stderr, sep="\n", file=sys.stderr
        )
        raise Exception("Error in system call. Cannot continue")

    logging.info(f"stdout:\n{completed_process.stdout.rstrip()}")
    logging.info(f"stderr:\n{completed_process.stderr.rstrip()}")
    return completed_process


def genome_from_ncbi(accession, outdir, genbank_or_refseq):
    # ncbi-genome-download doesn't get eg CP010331. So try using it and
    # if it fails then try using wget eutils instead
    try:
        syscall(f"ncbi-genome-download -s {genbank_or_refseq} -A {accession} -o {outdir} --flat-output -F fasta bacteria")
    except:
        fasta_out = accession + ".fna"
        syscall(f"wget -q -O {fasta_out} 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nucleotide&rettype=fasta&retmode=text&id={accession}'", cwd=outdir)
        syscall(f"fastaq to_fasta {fasta_out} {fasta_out}.gz", cwd=outdir)
        os.unlink(os.path.join(outdir, fasta_out))

    fastas = [os.path.join(outdir, x) for x in os.listdir(outdir) if x.startswith(accession) and x.endswith(".fna.gz")]
    if len(fastas) != 1:
        raise Exception(f"Did not get exactly 1 file from ncbi-genome-download for accession {accession}. Got: {fastas}")
    return fastas[0]


def sim_reads_from_ncbi(accession, root_out, genbank_or_refseq):
    genbank_or_refseq = genbank_or_refseq.lower()
    assert genbank_or_refseq in ["genbank", "refseq"]
    outdir = os.path.join(root_out, accession)
    syscall(f"rm -rf {outdir}")
    os.mkdir(outdir)
    fasta = genome_from_ncbi(accession, outdir, genbank_or_refseq)
    insert = 200
    insert_sd = 1
    cov = 20
    length = 75
    fastq_out = os.path.join(outdir, "reads.fastq.gz")
    command = f"fastaq to_perfect_reads {fasta} {fastq_out} {insert} {insert_sd} {cov} {length}"
    syscall(command)


def get_reads_from_ena(run_id, root_out):
    # enaDataGet -d OUT option will put the output in OUT/RUN_ID
    outdir = os.path.join(root_out, run_id)
    if os.path.exists(outdir):
        syscall(f"rm -rf {outdir}", shell=True)
    # Run ERR159957 is weird, the usual FASTQ file is not available, but the
    # original uploaded one is available so we'll get that instead
    if run_id == "ERR159957":
        os.mkdir(outdir)
        syscall(f"wget -q -O {run_id}.fastq.gz ftp://ftp.sra.ebi.ac.uk/vol1/run/ERR159/ERR159957/MTB_BTBH0500.fastq.gz", cwd=outdir)
        return
    else:
        syscall(f"enaDataGet -f fastq -d {root_out} {run_id}")
    # Can happen where nothing found, but return code is still zero. Here's
    # the output from enaDataGet -f fastq ERR159957:
    # Checking availability of https://www.ebi.ac.uk/ena/browser/api/xml/ERR159957
    # No files of format fastq for ERR159957
    # Deleting directory ERR159957
    # Completed
    #
    # and then echo $? gives 0. So do a basic check that at least the output
    # directory exists.
    if not os.path.exists(outdir):
        raise Exception(f"No output directory after trying to get {run_id} from the ENA")



def run_mykrobe(reads_files, json_out, panels_dir=None):
    json_out = os.path.abspath(json_out)
    reads_files = [os.path.abspath(x) for x in reads_files]
    work_dir = os.path.dirname(json_out)
    seq_opt = "--seq " + " ".join(reads_files)
    command = f"mykrobe predict {seq_opt} --species tb --format json --output {json_out} --sample sample"
    if panels_dir is not None:
        panels_dir = os.path.abspath(panels_dir)
        command += f" --panels_dir {panels_dir}"
    syscall(command, cwd=work_dir)


def parse_mykrobe_json(json_file):
    with open(json_file) as f:
        results = json.load(f)

    try:
        phylo = results["sample"]["phylogenetics"]
    except:
        return "NO_PHYLO_IN_JSON", "NO_PHYLO_IN_JSON"

    try:
        species = ",".join(list(phylo["species"].keys()))
    except:
        species = "NOT_IN_JSON"

    try:
        lineage = ",".join(phylo["lineage"]["lineage"])
    except:
        lineage = "NOT_IN_JSON"

    return species, lineage
