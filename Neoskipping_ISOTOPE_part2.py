"""
@authors: Juan L. Trincado
@email: juanluis.trincado@upf.edu
Neoskipping_ISOTOPE.py: get significant neoskipping events
"""

from lib.Neoskipping.run_netMHC_classI_slurm_part1 import *
from lib.Neoskipping.run_netMHCpan_classI_slurm_part1 import *
from lib.Neoskipping.run_netMHC_classI_slurm_part2 import *
from lib.Neoskipping.run_netMHCpan_classI_slurm_part2 import *
from lib.Neoskipping.format_to_SPADA import *

from argparse import ArgumentParser, RawTextHelpFormatter
import argparse

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


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

description = \
"Description: Get alternative splice site events\n\n"

parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter,
                        add_help=True)
parser.add_argument("-HLAclass", "--HLAclass", required=True, help = "HLA genotype of the samples")
parser.add_argument("-HLAtypes", "--HLAtypes", required=True, help = "HLA alelles recognized by NetMHC")
parser.add_argument("-HLAtypespan", "--HLAtypespan", required=True, help = "HLA alelles recognized by NetMHCpan")
parser.add_argument("-netMHC", "--netMHC", required=True, help = "netMHC path")
parser.add_argument("-netMHCpan", "--netMHCpan", required=True, help = "netMHCpan path")
parser.add_argument("-o", "--output", required=True, help = "Output path")

# def main():
def main(HLAclass_path, HLAtypes_path, HLAtypes_pan_path, netMHC_path, netMHC_pan_path, output_path):
    try:

        logger.info("Starting execution Neoskipping_ISOTOPE_part2")

        # HLAclass_path = "/projects_rg/SCLC_cohorts/Smart/PHLAT/PHLAT_summary_ClassI.out"
        # HLAtypes_path = "/projects_rg/SCLC_cohorts/tables/NetMHC-4.0_HLA_types_accepted.tab"
        # HLAtypes_pan_path = "/projects_rg/SCLC_cohorts/tables/NetMHCpan-4.0_HLA_types_accepted.tab"
        # netMHC_path = "/projects_rg/SCLC_cohorts/soft/netMHC-4.0/netMHC"
        # netMHC_pan_path = "/projects_rg/SCLC_cohorts/soft/netMHCpan-4.0/netMHCpan"
        # output_path = "/users/genomics/juanluis/SCLC_cohorts/Smart/epydoor/neoskipping"

        # 10. Run netMHC-4.0_part2
        logger.info("Part10...")
        run_netMHC_classI_slurm_part2(output_path + "/all_neoskipping_filtered_peptide_change.tab", HLAclass_path, HLAtypes_path,
                                      output_path + "/neoskipping_fasta_files",output_path + "/neoskipping_NetMHC-4.0_files", output_path + "/neoskipping_NetMHC-4.0_neoantigens_type_3.tab",
                                      output_path + "/neoskipping_NetMHC-4.0_neoantigens_type_3_all.tab", output_path + "/neoskipping_NetMHC-4.0_neoantigens_type_2.tab",
                                      output_path + "/neoskipping_NetMHC-4.0_neoantigens_type_2_all.tab", output_path + "/neoskipping_NetMHC-4.0_junctions_ORF_neoantigens.tab",
                                      netMHC_path)

        # 11. Run netMHCpan-4.0_part2
        logger.info("Part11...")
        run_netMHCpan_classI_slurm_part2(output_path + "/all_neoskipping_filtered_peptide_change.tab", HLAclass_path, HLAtypes_pan_path,
                                      output_path + "/neoskipping_fasta_files",output_path + "/neoskipping_NetMHCpan-4.0_files", output_path + "/neoskipping_NetMHCpan-4.0_neoantigens_type_3.tab",
                                      output_path + "/neoskipping_NetMHCpan-4.0_neoantigens_type_3_all.tab", output_path + "/neoskipping_NetMHCpan-4.0_neoantigens_type_2.tab",
                                      output_path + "/neoskipping_NetMHCpan-4.0_neoantigens_type_2_all.tab", output_path + "/neoskipping_NetMHCpan-4.0_junctions_ORF_neoantigens.tab",
                                      netMHC_pan_path)

        # # 12. Run format_to_SPADA
        # logger.info("Part12...")
        # format_to_SPADA(output_path + "/all_neoskipping_ORF.tab", output_path + "/all_neoskipping_ORF_sequences.tab",
        #                 output_path + "/all_neoskipping_Interpro.tab",
        #                 output_path + "/all_neoskipping_IUPred.tab", output_path + "/all_neoskipping_SPADA.tab",
        #                 output_path + "/all_neoskipping_SPADA.fasta", output_path + "/all_neoskipping_SPADA_features.tab")
        logger.info("Done.")

        exit(0)

    except Exception as error:
        logger.error('ERROR: ' + repr(error))
        logger.error("Aborting execution")
        sys.exit(1)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args.HLAclass,args.HLAtypes,args.HLAtypespan,args.netMHC,args.netMHCpan,args.output)