from mlt import samples


def run(options):
    sample_set = samples.SampleSet(options.data_dir, options.samples_tsv)
    sample_set.run_mykrobe(
        options.outdir, panels_dir=options.panels_dir, cpus=options.cpus
    )
