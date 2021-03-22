"""
@authors: Juan L. Trincado
@email: juanluis.trincado@upf.edu

overlap_with_repeats: find the overlap between the nex exonizations and repeatitions (RepeatMasker)

"""

import pandas as pd
from argparse import ArgumentParser, RawTextHelpFormatter
import logging, sys, os, re

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create console handler and set level to info
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def overlap_with_repeats(input_path, repeats_path, output_path):

    try:
        logger.info("Starting execution "+repeats_path)

        # Transform the alt exon cordinates to bed file
        logger.info("Formatting bed files...")
        junction_reads = pd.read_table(input_path, delimiter="\t")
        chr = junction_reads["Alt_Exon_id"].apply(lambda x: x.split(";")[0])
        start = junction_reads["Alt_Exon_id"].apply(lambda x: x.split(";")[1])
        end = junction_reads["Alt_Exon_id"].apply(lambda x: x.split(";")[2])
        strand = junction_reads["Alt_Exon_id"].apply(lambda x: x.split(";")[3])
        # Save this variables as bed file
        path1 = "/".join(input_path.split("/")[:-1])
        bed = [("chr", chr), ("start", start), ("end", end), ("id", junction_reads['Alt_Exon_id']),("strand", strand)]
        # bed_file = pd.DataFrame.from_items(bed)
        bed_file = pd.DataFrame.from_dict(dict(bed))
        bed_file['score'] = 0
        #Put columns in order
        cols = bed_file.columns.tolist()
        cols = cols[0:4] + [cols[-1]] + [cols[4]]
        bed_file = bed_file[cols]
        bed_file.to_csv(path1 + "/aux.bed", sep="\t", index=False, header=False)

        # Run interesectBed for obtaining the exons that overlapps with repeat regions
        logger.info("Running intersectBed...")
        command2 = "intersectBed -wao -a " + path1 + "/aux.bed -b " + repeats_path + \
                   " -s > " + path1 + "/aux2.bed"
        os.system(command2)

        #Load the new created file. Get all the repeatitions associated to the exons

        # Get the information of the gene and transform it ot bed
        exon_repeat = {}
        with open(path1 + "/aux2.bed") as f:
            logger.info("Generating output file...")
            for line in f:
                tokens = line.rstrip().split("\t")
                if(tokens[7]!="-1"):
                    #Save the associated repeat
                    if(tokens[3] not in exon_repeat):
                        exon_repeat[tokens[3]] = [tokens[9]]
                    else:
                        if(tokens[9] not in exon_repeat[tokens[3]]):
                            exon_repeat[tokens[3]].append(tokens[9])

        #Read the table with the A5_A3 junctions, adding the information of the repeats
        repeats = []
        for index, row in junction_reads.iterrows():
            if(row['Alt_Exon_id'] in exon_repeat):
                repeats.append(exon_repeat[row['Alt_Exon_id']])
            else:
                repeats.append("No repeat")

        junction_reads["Repeats"] = repeats
        #Put columns in order
        cols = junction_reads.columns.tolist()
        cols = cols[0:7] + [cols[-1]] + cols[7:-1]
        junction_reads = junction_reads[cols]
        #Save the file
        junction_reads.to_csv(output_path, sep="\t", index=False, header=True)
        logger.info("Saved " + output_path)

        # Remove auxiliary files
        #os.remove(path1 + "/aux.bed")
        #os.remove(path1 + "/aux2.bed")

        logger.info("Done. Exiting program.")

    except Exception as error:
        logger.error('ERROR: ' + repr(error))
        logger.error("Aborting execution")
        sys.exit(1)
