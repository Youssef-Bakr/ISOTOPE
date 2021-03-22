"""
@authors: Juan L. Trincado
@email: juanluis.trincado@upf.edu

get_reads_exonizations: given the list with the possible exonizations, get the reads associate to each of them

"""

import pandas as pd
from argparse import ArgumentParser, RawTextHelpFormatter
import logging, sys, os, re, csv
import numpy as np

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

def get_reads_exonizations(exonization_file, readCounts_file, output_file, Intropolis_flag):

    try:
        logger.info("Starting execution")

        # Load the readCounts. They could come form Normal samples processed by Junckey or from Intropolis
        if(not Intropolis_flag):
            # Load the readCounts
            junction_reads, junction_reads1, junction_reads2 = {},{},{}
            cont = 0
            with open(readCounts_file) as f:
                header = next(f).rstrip()
                logger.info("Loading readCounts...")
                for line in f:
                    # cont += 1
                    # print(str(cont))
                    # if (cont == 1000):
                    #     break
                    tokens = line.rstrip().split("\t")
                    junction_id = tokens[0]
                    reads = list(map(float,tokens[8:]))
                    # Save this reads in the dictionary
                    if(junction_id not in junction_reads):
                        junction_reads[junction_id] = reads
                    else:
                        raise Exception("Junction id "+junction_id+" repeated")

        else:
            junction_reads = {}
            cont = 0
            with open(readCounts_file) as f:
                logger.info("Loading readCounts from Intropolis...")
                for line in f:
                    cont += 1
                    # print(str(cont))
                    # if (cont == 100):
                    #     break
                    tokens = line.rstrip().split("\t")
                    # junction_id = tokens[0]
                    # junction_id = "chr"+tokens[0].split("_")[0]+";"+tokens[0].split("_")[1]+";"+tokens[0].split("_")[2]
                    # Sustract 2 to the start and add 1 to the end
                    junction_id = tokens[0] + ";" + str(int(tokens[1]) - 2) + ";" + str(
                        int(tokens[2]) + 1) + ";" + str(
                        tokens[3])
                    # reads = list(map(int,tokens[8:]))
                    # reads = np.max(tokens[7].split(","))
                    reads = max(list(map(int, tokens[7].split(","))))
                    # Save this reads in the dictionary
                    if (junction_id not in junction_reads):
                        junction_reads[junction_id] = reads
                    else:
                        logger.info("Junction id " + junction_id + " repeated")
                        pass

        #Load the exonizations
        logger.info("Loading exonizations...")
        exonizations = pd.read_table(exonization_file, delimiter="\t")
        #Get the lists of junctions associated to each exonization
        Canonical_Junction_id = exonizations["Canonical_Junction_id"].tolist()
        Alt_Junction_id = exonizations["Alt_Junction_id"].tolist()
        final_counts_list = []
        logger.info("Processing files...")
        cont = 0
        #By line, check all the possible reads associated to each junction.
        for junction_can,junction_alt in zip(Canonical_Junction_id,Alt_Junction_id):
            # cont += 1
            # print(str(cont))
            # if (cont == 3):
            #     break
            # Get the reads associated to each junction
            if (junction_can in junction_reads):
                # print("Encontrada junction!!!")
                readCounts1 = junction_reads[junction_can]
            else:
                readCounts1 = list(np.repeat(0, len(tokens[8:])))
            if (junction_alt in junction_reads):
                # print("Encontrada junction!!!")
                readCounts2 = junction_reads[junction_alt]
            else:
                readCounts2 = list(np.repeat(0, len(tokens[8:])))

            #Check if totalCounts are lists. If not, convert it to lists, to use zip
            if not isinstance(readCounts1, list):
                readCounts1 = [readCounts1]
            if not isinstance(readCounts2, list):
                readCounts2 = [readCounts2]
            # From both lists, take the minimum value
            final_counts = [str(min(x, y)) for x, y in zip(readCounts1, readCounts2)]
            aux = "\t".join(final_counts)
            final_counts_list.append(aux)

        if(not Intropolis_flag):
            #Paste the readCounts
            logger.info("Creating output file...")
            exonizations["readCounts"] = final_counts_list
            columns = list(exonizations.columns.values)
            columns[-1] = "\t".join(header.split("\t")[8:])
            exonizations.columns = columns
            #Save the file
            exonizations.to_csv(output_file, sep="\t", index=False, quoting=csv.QUOTE_NONE, escapechar=' ')

        else:
            #Paste the readCounts
            logger.info("Creating output file...")
            exonizations["readCounts"] = final_counts_list
            #Save the file
            exonizations.to_csv(output_file, sep="\t", index=False, quoting=csv.QUOTE_NONE, escapechar=' ')

        logger.info("Saved "+output_file)
        logger.info("Done. Exiting program.")

    except Exception as error:
        logger.error('ERROR: ' + repr(error))
        logger.error("Aborting execution")
        sys.exit(1)
