"""
@authors: Juan L. Trincado
@email: juanluis.trincado@upf.edu

run_netMHC-4.0: run netMHC-4.0 on each sample
"""

import pandas as pd
from argparse import ArgumentParser, RawTextHelpFormatter
import logging, sys, os, re
import subprocess
from Bio.Seq import Seq
# from Bio.Alphabet import IUPAC

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


def run_netMHC_classI_slurm_part1(input_list_path, HLAclass_path, HLAtypes_path, input_sequence_pieces_path, output_netMHC_path,
                                  output_peptides_path,output_peptides_all_path,output_peptides_path2, output_peptides_all_path2,
                                  output_list_path,netMHC_path,cluster):
    try:
        logger.info("Starting execution")

        # input_list_path = sys.argv[1]
        # HLAclass_path = sys.argv[2]
        # HLAtypes_path = sys.argv[3]
        # input_sequence_pieces_path = sys.argv[4]
        # output_netMHC_path = sys.argv[5]
        # output_peptides_path = sys.argv[6]
        # output_peptides_all_path = sys.argv[7]
        # output_peptides_path2 = sys.argv[8]
        # output_peptides_all_path2 = sys.argv[9]
        # output_list_path = sys.argv[10]
        # netMHC_path = sys.argv[11]
        #
        # input_list_path = "/projects_rg/SCLC_cohorts/cis_analysis/v5/SCLC_v5/tables_v2/IR_ORF_filtered_peptide_change.tab"
        # HLAclass_path = "/projects_rg/SCLC_cohorts/tables/PHLAT_summary_ClassI_all_samples.out"
        # HLAtypes_path = "/projects_rg/SCLC_cohorts/tables/NetMHC-4.0_HLA_types_accepted.tab"
        # input_sequence_pieces_path = "/projects_rg/SCLC_cohorts/cis_analysis/v5/SCLC_v5/tables_v2/RI_fasta_files"
        # output_netMHC_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_files"
        # output_peptides_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_3.tab"
        # output_peptides_all_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_3_all.tab"
        # output_peptides_path2 = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_2.tab"
        # output_peptides_all_path2 = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_2_all.tab"
        # output_list_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_junctions_ORF_filtered_neoantigens.tab"
        # netMHC_path = "/users/genomics/juanluis/Software/netMHC-4.0/netMHC"

        # input_list_path = "/projects_rg/SCLC_cohorts/Smart/IR_v2/IR_ORF_filtered_peptide_change.tab"
        # HLAclass_path = "/projects_rg/SCLC_cohorts/Smart/PHLAT/PHLAT_summary_ClassI.out"
        # HLAtypes_path = "/projects_rg/SCLC_cohorts/tables/NetMHC-4.0_HLA_types_accepted.tab"
        # input_sequence_pieces_path = "/projects_rg/SCLC_cohorts/Smart/IR_v2/RI_fasta_files"
        # output_netMHC_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_files"
        # output_peptides_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_3.tab"
        # output_peptides_all_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_3_all.tab"
        # output_peptides_path2 = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_2.tab"
        # output_peptides_all_path2 = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_2_all.tab"
        # output_list_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_junctions_ORF_filtered_neoantigens.tab"
        # netMHC_path = "/users/genomics/juanluis/Software/netMHC-4.0/netMHC"

        # Load the list of accepted HLA types
        logger.info("Load the list of accepted HLA types")
        HLA_accepted_types = set()
        with open(HLAtypes_path) as f:
            for line in f:
                tokens = line.rstrip()
                HLA_accepted_types.add(tokens)

        # Assign to each sample their corresponding HLA types according to the results with seq2HLA
        logger.info("Assigning the prediction for the HLA types to each sample")
        HLA_samples = {}
        with open(HLAclass_path) as f:
            next(f)
            cont = 0
            for line in f:
                cont += 1
                tokens = line.rstrip().split("\t")
                # Check if the HLA_types are significant and if that type exists
                aux = "HLA-" + tokens[1].replace("'", "").replace("*", "").replace(":", "")
                # A1 class
                if (float(tokens[2]) <= 0.05 and aux in HLA_accepted_types):
                    if (tokens[0] not in HLA_samples):
                        HLA_samples[tokens[0]] = [aux]
                    else:
                        if (aux not in HLA_samples[tokens[0]]):
                            HLA_samples[tokens[0]].append(aux)
                aux = "HLA-" + tokens[3].replace("'", "").replace("*", "").replace(":", "")
                # A2 class
                if (float(tokens[4]) <= 0.05 and aux in HLA_accepted_types):
                    if (tokens[0] not in HLA_samples):
                        HLA_samples[tokens[0]] = [aux]
                    else:
                        if (aux not in HLA_samples[tokens[0]]):
                            HLA_samples[tokens[0]].append(aux)
                aux = "HLA-" + tokens[5].replace("'", "").replace("*", "").replace(":", "")
                # B1 class
                if (float(tokens[6]) <= 0.05 and aux in HLA_accepted_types):
                    if (tokens[0] not in HLA_samples):
                        HLA_samples[tokens[0]] = [aux]
                    else:
                        if (aux not in HLA_samples[tokens[0]]):
                            HLA_samples[tokens[0]].append(aux)
                aux = "HLA-" + tokens[7].replace("'", "").replace("*", "").replace(":", "")
                # B2 class
                if (float(tokens[8]) <= 0.05 and aux in HLA_accepted_types):
                    if (tokens[0] not in HLA_samples):
                        HLA_samples[tokens[0]] = [aux]
                    else:
                        if (aux not in HLA_samples[tokens[0]]):
                            HLA_samples[tokens[0]].append(aux)
                aux = "HLA-" + tokens[9].replace("'", "").replace("*", "").replace(":", "")
                # C1 class
                if (float(tokens[10]) <= 0.05 and aux in HLA_accepted_types):
                    if (tokens[0] not in HLA_samples):
                        HLA_samples[tokens[0]] = [aux]
                    else:
                        if (aux not in HLA_samples[tokens[0]]):
                            HLA_samples[tokens[0]].append(aux)
                aux = "HLA-" + tokens[11].replace("'", "").replace("*", "").replace(":", "")
                # C2 class
                if (float(tokens[12]) <= 0.05 and aux in HLA_accepted_types):
                    if (tokens[0] not in HLA_samples):
                        HLA_samples[tokens[0]] = [aux]
                    else:
                        if (aux not in HLA_samples[tokens[0]]):
                            HLA_samples[tokens[0]].append(aux)

        # Go over the input file, running netMHC
        logger.info("Processing samples for running netMHC")
        cont = 0
        path1 = "/".join(output_peptides_path.split("/")[:-1])
        with open(input_list_path) as f:
            next(f)
            for line in f:
                cont += 1
                # if(cont==3):
                #     break
                logger.info("Index: " + str(cont))
                tokens1 = line.rstrip().split("\t")
                index = tokens1[0]
                exonization = tokens1[1]
                sample = tokens1[4].rstrip()
                #Format the sample
                sample = sample.replace("X","").replace(".","-")
                results_by_exon = []
                # Get the HLA types associated. Run netMHC for each HLA type
                if (sample in HLA_samples):
                    HLA_types = HLA_samples[sample]
                    cont2 = 0
                    for x in HLA_types:
                        if(cluster):
                            logger.info("Running jobs in parallel...")
                            logger.info("Running job HLA-type: " + output_netMHC_path + "/" + index + "_" + x + ".out")
                            cont2 += 1
                            command1 = netMHC_path + " -a " + x + " " + input_sequence_pieces_path + "/" + index + \
                                      ".fa > " + output_netMHC_path + "/" + index + "_" + x + ".out"
                            #Output this to an auxiliary script
                            open_peptides_file = open(path1+"/aux.sh", "w")
                            open_peptides_file.write("#!/bin/sh\n")
                            # open_peptides_file.write("#SBATCH --partition=lowmem\n")
                            open_peptides_file.write("#SBATCH --mem 2000\n")
                            open_peptides_file.write("#SBATCH -e "+path1+"/"+index + "_" + x + ".err"+"\n")
                            open_peptides_file.write("#SBATCH -o "+path1+"/"+index + "_" + x + ".out"+"\n")
                            open_peptides_file.write(command1+";\n")
                            open_peptides_file.close()
                            command2 = "sbatch -J " + index + "_" + x + " " + path1 + "/aux.sh; sleep 0.5"
                            os.system(command2)
                            logger.info("When all the jobs have finished, run part2.")

                        else:
                            logger.info("Running jobs sequentially...")
                            logger.info("Running job HLA-type: " + output_netMHC_path + "/" + index + "_" + x + ".out")
                            cont2 += 1
                            command1 = netMHC_path + " -a " + x + " " + input_sequence_pieces_path + "/" + index + \
                                       ".fa > " + output_netMHC_path + "/" + index + "_" + x + ".out"
                            os.system(command1)

                else:
                    pass

        logger.info("Done. Exiting program.")

    except Exception as error:
        logger.error('ERROR: ' + repr(error))
        logger.error("Aborting execution")
        sys.exit(1)

