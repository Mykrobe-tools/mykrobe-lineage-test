from mlt import samples


def run(options):
    sample_set = samples.SampleSet(options.data_dir, options.samples_tsv)
    sample_set.gather_mykrobe_results(options.mykrobe_dir, options.outfile)
