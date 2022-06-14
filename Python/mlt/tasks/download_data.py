from mlt import samples


def run(options):
    sample_set = samples.SampleSet(options.outdir, options.samples_tsv)
    sample_set.download_data(cpus=options.cpus)
