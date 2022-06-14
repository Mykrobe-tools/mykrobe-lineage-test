import csv
import itertools
import logging
import multiprocessing
import os

from mlt import utils


def _download_reads(accession, source, root_out):
    source = source.lower()
    try:
        if source == "ena":
            utils.get_reads_from_ena(accession, root_out)
        elif source in ["genbank", "refseq"]:
            utils.sim_reads_from_ncbi(accession, root_out, source)
        else:
            raise Exception(f"unknown source: {source} for accession {accession}")
    except Exception as e:
        return accession, False, e
    return accession, True, None


def _run_mykrobe(data, panels_dir):
    reads, accession, json_out = data
    try:
        utils.run_mykrobe(reads, json_out, panels_dir=panels_dir)
    except Exception as e:
        return accession, False, e
    return accession, True, None


class SampleSet:
    def __init__(self, root_dir, samples_tsv):
        self.root_dir = os.path.abspath(root_dir)
        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)

        self.samples = {}
        with open(samples_tsv) as f:
            for d in csv.DictReader(f, delimiter="\t"):
                assert d["accession"] not in self.samples
                self.samples[d["accession"]] = d

    def download_done_file(self, accession):
        return os.path.join(self.root_dir, accession + ".downloaded")

    def is_downloaded(self, accession):
        return os.path.exists(self.download_done_file(accession))

    def set_downloaded(self, accession):
        with open(self.download_done_file(accession), "w") as f:
            pass

    def download_data(self, cpus=1):
        to_get = {}
        for accession, sample_d in self.samples.items():
            if self.is_downloaded(accession):
                continue

            if sample_d["source"] not in to_get:
                to_get[sample_d["source"]] = []

            to_get[sample_d["source"]].append(accession)

        all_ok = True

        for source, to_get_list in to_get.items():
            logging.info(
                f"Getting {len(to_get_list)} samples from {source} using {cpus} cpu(s)"
            )
            with multiprocessing.Pool(cpus) as pool:
                samples_ok = pool.starmap(
                    _download_reads,
                    zip(
                        to_get_list,
                        itertools.repeat(source),
                        itertools.repeat(self.root_dir),
                    ),
                )

            for accession, success, error in samples_ok:
                if success:
                    self.set_downloaded(accession)
                else:
                    all_ok = False
                    logging.warn(f"Error getting data for {accession}. Error: {error}")

        if not all_ok:
            raise Exception(
                "At least one accession not downloaded (see previous error messages)"
            )

    def get_fastqs(self, accession):
        reads_dir = os.path.join(self.root_dir, accession)
        all_reads = [
            os.path.join(reads_dir, x)
            for x in os.listdir(reads_dir)
            if x.endswith("fastq.gz")
        ]
        # when there's a bonus unpaired file from a paired run, ignore the
        # unpaired file
        if len(all_reads) == 3:
            fwd = [x for x in all_reads if x.endswith("_1.fastq.gz")]
            rev = [x for x in all_reads if x.endswith("_2.fastq.gz")]
            if len(fwd) == len(rev) and len(fwd) > 0:
                all_reads = fwd + rev
        return tuple(all_reads)


    def run_mykrobe(self, outdir, panels_dir=None, cpus=1):
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        to_run = []
        for accession, sample_d in self.samples.items():
            if not self.is_downloaded(accession):
                logging.warn(
                    f"Skipping runnning mykrobe on {accession} because reads not downloaded"
                )
                continue

            reads = self.get_fastqs(accession)
            if len(reads) == 0:
                logging.warn(
                    f"Skipping runnning mykrobe on {accession} because reads not found"
                )
                continue

            json_out = os.path.join(outdir, f"{accession}.json")
            if os.path.exists(json_out):
                continue
            to_run.append((reads, accession, json_out))

        if len(to_run) == 0:
            raise Exception("No samples found that can have mykrobe run on them")

        # mykrobe makes skeletons file if it's not there. Means we need to
        # run one sample first, then can run the rest in parallel and they
        # will be faster because they use the skeleton
        skeletons_dir = os.path.join(outdir, "mykrobe", "data", "skeletons")
        if os.path.exists(skeletons_dir):
            ctx_files = [x for x in os.listdir(skeletons_dir) if x.endswith(".ctx")]
        else:
            ctx_files = []
        if len(ctx_files) == 0:
            _, ok, error = _run_mykrobe(to_run[0], panels_dir)
            if not ok:
                raise Exception(
                    f"Error running mykrobe on {to_run[0][1]}. Error: {error}"
                )
            to_run.pop(0)
            if len(to_run) == 0:
                return

        with multiprocessing.Pool(cpus) as pool:
            samples_ok = pool.starmap(
                _run_mykrobe,
                zip(
                    to_run,
                    itertools.repeat(panels_dir),
                ),
            )

        all_ok = True
        for accession, success, error in samples_ok:
            if not success:
                all_ok = False
                logging.warn(f"Error running mykrobe on {accession}. Error: {error}")

        if not all_ok:
            raise Exception("Some mykrobe runs failed (see previous error messages)")

    def gather_mykrobe_results(self, mykrobe_dir, outfile):
        with open(outfile, "w") as f:
            print(
                "accession",
                "source",
                "species",
                "lineage",
                "called_species",
                "called_lineage",
                "correct",
                sep="\t",
                file=f,
            )

            for accession, sample_d in self.samples.items():
                json_out = os.path.join(mykrobe_dir, f"{accession}.json")
                if not os.path.exists(json_out):
                    called_species = "NO_JSON"
                    called_lineage = "NO_JSON"
                    correct = False
                else:
                    called_species, called_lineage = utils.parse_mykrobe_json(json_out)
                    lineage_ok = (
                        sample_d["lineage"] == "NA"
                        or sample_d["lineage"] == called_lineage
                    )
                    correct = sample_d["species"] == called_species and lineage_ok
                print(
                    sample_d["accession"],
                    sample_d["source"],
                    sample_d["species"],
                    sample_d["lineage"],
                    called_species,
                    called_lineage,
                    correct,
                    sep="\t",
                    file=f,
                )
