# Required modules
import argparse
import gzip
import os
import sys
import shutil

def se_fq_validator(file, rename, sample_name):
    if rename:
        print(f"Validating SE_FQ mode with file: {file}, RENAME enabled, Sample Name: {sample_name}")
    else:
        print(f"Validating SE_FQ mode with file: {file}, RENAME disabled, Sample Name: {sample_name}")

def pe_fq_validator(file1, file2, rename, sample_name):
    if rename:
        print(f"Validating PE_FQ mode with files: {file1}, {file2}, RENAME enabled, Sample Name: {sample_name}")
    else:
        print(f"Validating PE_FQ mode with files: {file1}, {file2}, RENAME disabled, Sample Name: {sample_name}")

def fa_validator(file, gzip):
    if gzip:
        print(f"Running FA mode with file: {file}, and output fasta will be gzipped")
    else:
        print(f"Running FA mode with file: {file}, and output fasta will be not gzipped")

def file_structure(file_list):
    """
    Sets up the file structure for temp files and output files.
    Also moves input data into temp folder.
    """

    try:
        os.makedirs('data_val_temp', exist_ok=True)
        os.makedirs('Validated_Data', exist_ok=True)

        for file in file_list:
            file_base = os.path.basename(file)
            print(file_base)
            shutil.copy(file, 'data_val_temp/' + file_base)

    except Exception as e:
        print(f"Error creating folders or copying data: {e}", file=sys.stderr)


def decompress_file(file_in, file_out ):
    """
    This function takes a fastq input (either gzipped or no gzipped) and
    uncompresses it to a temporary file. If its already gzipped it just
    makes a copy to the temp file instead. It will name the temp file
    according to the sample_name string

    This returs the file name of the uncompressed fastq
    """
    print("Decompressing file")
    # Determining if the file is in gzip format
    try:
        with open(file_in, 'rb') as f:
            # Read the first two bytes
            magic_number = f.read(2)

        # Check if the magic number indicates gzip format
        if magic_number == b'\x1f\x8b':
            # Decompress a file
            with gzip.open(file_in, 'rb') as f_in:
                with open(file_out, 'wb') as f_out:
                    f_out.writelines(f_in)
            print('File ' + file_in + ' was unzipped and written to temporary file ' + file_out)

            # assume the file is plain text if not gzipped
        else:
            shutil.copy(file_in, file_out)
            print('File ' + file_in + ' was already unzipped and written to temporary file ' + file_out)

    except Exception as e:
        print(f"Error processing {file_in}: {e}", file=sys.stderr)

    return (file_out)


def check_fastq(fastq):
    """
    This function checks to make sure a fastq file seems to be in the correct format.

    This function expects fastqs to be uncompressed

    This function returns a True if its in the correct format.
    """
    print("Checking fastq")
    phred = {}
    for x in range(0, 94):
        phred[x] = chr(x + 33)

    # Determinging if the file is in standard fastq format
    try:
        with open(fastq, 'r') as f:
            valid_format = True
            line_num = 0
            for line in f:
                line = line.strip()
                line_num += 1

                if line_num % 4 == 1:
                    if not line.startswith('@'):
                        valid_format = False
                        raise ValueError("File Format Error Line " + str(line_num) + ' Does Not Start with a @')

                elif line_num % 4 == 2:
                    # sequence line, check for valid characters
                    for char in line:
                        if char not in 'ACGTN':
                            valid_format = False
                            raise ValueError(
                                "File Format Error Line " + str(line_num) + ' Contains Charcters other than ATGCN')

                elif line_num % 4 == 3:
                    if not line.startswith('+'):
                        valid_format = False
                        raise ValueError("File Format Error Line " + str(line_num) + ' Does Not Start with a +')

                elif line_num % 4 == 0:
                    for char in line:
                        if not char in phred.values():
                            valid_format = False
                            print(valid_format)
                            raise ValueError(
                                "File Format Error Line " + str(line_num) + ' Contains a non-standard phred score')

            # Check if the number of lines is a multiple of 4 (valid FASTQ format)
            if line_num % 4 != 0:
                valid_format = False
                raise ValueError("File Format Error: FastQ had " + str(line_num) + ' lines, not a multiple of 4')


    except Exception as e:
        print(f"Error processing {fastq}: {e}", file=sys.stderr)

    if valid_format:
        print(fastq + ' is a proper fastq file')
        return True
    else:
        print(fastq + ' is NOT a proper fastq file')
        return False

def check_fasta(fasta):
    """
    This function checks to make sure a fasta file seems to be in the correct format.
    :param fasta: Uncompressed Fasta file
    :return: True if it's in the correct format. False otherwise.
    """
    print("Checking fasta")
    try:
        with open(fasta, 'r') as f:
            valid_format = True
            line_num = 0
            for line in f:
                line = line.strip()
                line_num += 1

                if line_num % 2 == 1:
                    if not line.startswith('>'):
                        valid_format = False
                        raise ValueError("File Format Error Line " + str(line_num) + ' Does Not Start with a <')

                elif line_num % 2 == 0:
                    # sequence line, check for valid characters
                    for char in line:
                        if char not in 'ATCGAUCGACDEFGHIKLMNPQRSTVWY-.RYSWKMBDHVNatcgaucgacdefghiklmnpqrstvwyryswkmbdhvn':
                            valid_format = False
                            raise ValueError(
                                "File Format Error Line " + str(line_num) + ' Contains Charcter ' + char + '. Accepted charcters are ATCGAUCGACDEFGHIKLMNPQRSTVWY-.RYSWKMBDHVNatcgaucgacdefghiklmnpqrstvwyryswkmbdhvn')

            # Check if the number of lines is a multiple of 4 (valid FASTQ format)
            if line_num % 2 != 0:
                valid_format = False
                raise ValueError("File Format Error: Fasta had " + str(line_num) + ' lines, not a multiple of 2')


    except Exception as e:
        print(f"Error processing {fasta}: {e}", file=sys.stderr)

    if valid_format:
        print(fasta + ' is a proper fasta file')
        return True
    else:
        print(fasta + ' is NOT a proper fasta file')
        return False

def multiline_fasta_convert(fasta, prefix):
    """
    This function remove whitespace from fasta sequences
    :param fasta:
    :param prefix:
    :return:
    """
    print("Converting fasta file")
    try:
        with open(fasta, 'r') as infile, open(prefix + '_singleline.fasta', 'w') as outfile:
            sequence = ''
            for line in infile:
                line = line.strip()
                if line.startswith('>'):
                    if sequence != '':
                        outfile.write(sequence + '\n')
                        sequence = ''
                outfile.write(line + '\n')
            else:
                sequence += line
        return prefix + '_singleline.fasta'
    except Exception as e:
        print(f"Error processing {fasta}: {e}", file=sys.stderr)

def rename_fastqs(in_fq, out_fq, prefix):
    """
    This function takes a fastq file (Uncompressed) and renames
    the sequences in the file. This function is used to rename
    complex sequene names typical of ONT sequencing. By defualt
    this function renames sequences using the supplied prefix and
    the read count after that ("{prefix}_{read#}")
    """
    print("Renaming fastqs sequences")
    try:
        with open(in_fq, 'r') as infile, open(out_fq, 'w') as outfile:
            line_num = 0
            read_count = 0
            for line in infile:
                line = line.strip()
                if line_num % 4 == 0:
                    # Sequence identifier line (starts with '@')
                    read_count += 1
                    sequence_name = f"{prefix}_{read_count}"
                    outfile.write(f"@{sequence_name}\n")
                else:
                    # Other lines (sequence, optional quality scores)
                    outfile.write(f"{line}\n")
                line_num += 1
            print(f"Successfully renamed sequences, written to {out_fq}")
            return out_fq
    except Exception as e:
        print(f"Error reading or writing files: {e}", file=sys.stderr)


def gzip_file(in_fq, out_fq):
    """
    Takes a uncompressed file and gzips it.
    """
    print("Compressing file")
    try:
        with open(in_fq, 'rb') as f_in, gzip.open(out_fq, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        print(f"Successfully compressed {in_fq} to {out_fq}")

    except Exception as e:
        print(f"Error compressing file: {e}", file=sys.stderr)


def clean_files(file_list):
    """
    cleans up temp files
    """
    print("Cleaning up temp files")
    try:
        for file in file_list:
            os.remove(file)
            print(f"Successfully deleted {file}")

    except Exception as e:
        print(f"Error deleting file: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='Data Validator Program')

    subparsers = parser.add_subparsers(dest='mode', help='Mode of operation')

    # SE_FQ mode subparser
    se_fq_parser = subparsers.add_parser('SE_FQ', help='Single-end FASTQ mode')
    se_fq_parser.add_argument('file', help='Input file (R1)')
    se_fq_parser.add_argument('--rename', action='store_true', help='Rename option')
    se_fq_parser.add_argument('--sample_name', type=str, help='Sample name')

    # PE_FQ mode subparser
    pe_fq_parser = subparsers.add_parser('PE_FQ', help='Paired-end FASTQ mode')
    pe_fq_parser.add_argument('file1', help='Input file (R1)')
    pe_fq_parser.add_argument('file2', help='Input file (R2)')
    pe_fq_parser.add_argument('--rename', action='store_true', help='Rename option')
    pe_fq_parser.add_argument('--sample_name', type=str, help='Sample name')

    # FA mode subparser
    fa_parser = subparsers.add_parser('FA', help='FASTA mode')
    fa_parser.add_argument('file', help='Input file')
    fa_parser.add_argument('--gzip', action='store_true', help='gzip output fasta')

    args = parser.parse_args()

    if args.mode == 'SE_FQ':
        se_fq_validator(args.file, args.rename, args.sample_name)

        file_structure([args.file])

        file_base = os.path.basename(args.file)

        decom_finename = 'data_val_temp/' + args.sample_name + '.fastq'
        decompressed = decompress_file('data_val_temp/' + file_base, decom_finename)  # Decompressin (or not if it already is) input file and renamming it

        if check_fastq(decompressed):  # Checking if it is a standard fastq
            if args.rename:
                decompressed = rename_fastqs(decompressed, 'data_val_temp/' + args.sample_name + '_rename.fastq',
                                             args.sample_name)  # renamming sequences if specified

            output_sample = 'Validated_Data/' + args.sample_name + '.fastq.gz'  # creating file file name based on sample name

            gzip_file(decompressed, output_sample)  # gziping final file

            shutil.rmtree('data_val_temp') # Removing Temp Files

            print('fastq for ' + args.sample_name + ' was checked and compressed. It can be found at ' + output_sample)

        else:
            print('Sample ' + args.sample_name + ' did not pass fastq check. See errors above')

    elif args.mode == 'PE_FQ':
        pe_fq_validator(args.file1, args.file2, args.rename, args.sample_name)

        file_structure([args.file1, args.file2])

        print("Processing R1 " + args.file1)

        file_base_r1 = os.path.basename(args.file1)

        decom_finename = 'data_val_temp/' + args.sample_name + '_1.fastq'
        decompressed = decompress_file('data_val_temp/' + file_base_r1,
                                       decom_finename)  # Decompressin (or not if it already is) input file and renamming it

        if check_fastq(decompressed):  # Checking if it is a standard fastq
            if args.rename:
                decompressed = rename_fastqs(decompressed, 'data_val_temp/' + args.sample_name + '_rename_1.fastq',
                                             args.sample_name)  # renamming sequences if specified

            output_sample = 'Validated_Data/' + args.sample_name + '_1.fastq.gz'  # creating file file name based on sample name

            gzip_file(decompressed, output_sample)  # gziping final file

            print('R1 fastq for ' + args.sample_name + ' was checked and compressed. It can be found at ' + output_sample)

        else:
            print('Sample R1 ' + args.sample_name + ' did not pass fastq check. See errors above')

        print("Processing R2 " + args.file2)

        file_base_r2 = os.path.basename(args.file2)

        decom_finename = 'data_val_temp/' + args.sample_name + '_2.fastq'
        decompressed = decompress_file('data_val_temp/' + file_base_r2,
                                       decom_finename)  # Decompressin (or not if it already is) input file and renamming it

        if check_fastq(decompressed):  # Checking if it is a standard fastq
            if args.rename:
                decompressed = rename_fastqs(decompressed, 'data_val_temp/' + args.sample_name + '_rename_2.fastq',
                                             args.sample_name)  # renamming sequences if specified

            output_sample = 'Validated_Data/' + args.sample_name + '_2.fastq.gz'  # creating file file name based on sample name

            gzip_file(decompressed, output_sample)  # gziping final file

            shutil.rmtree('data_val_temp')  # Removing Temp Files

            print(
                'R2 fastq for ' + args.sample_name + ' was checked and compressed. It can be found at ' + output_sample)

        else:
            print('Sample R2 ' + args.sample_name + ' did not pass fastq check. See errors above')


    elif args.mode == 'FA':
        fa_validator(args.file, args.gzip)

        file_structure([args.file])

        normalized_path = os.path.normpath(args.file)
        file_base = os.path.basename(normalized_path)
        file_name_fa = os.path.splitext(file_base)[0].split('.')[0]

        decom_finename = 'data_val_temp/' + file_name_fa + '.fasta'
        decompressed = decompress_file('data_val_temp/' + file_base, decom_finename)  # Decompressing (or not if it already is) input
        # file and renamming it

        if check_fasta(decompressed):
            if args.gzip:
                gzip_file(decompressed, 'Validated_Data/' + file_name_fa + '.fasta.gz')
                shutil.rmtree('data_val_temp')  # Removing Temp Files
                print('Fasta File ' + args.file + ' was checked and compressed. It can be found at Validated_Data/' + file_name_fa + '.fasta.gz')

            else:
                shutil.copy(decompressed, 'Validated_Data/' + file_name_fa + '.fasta')
                shutil.rmtree('data_val_temp')  # Removing Temp Files
                print('Fasta File ' + args.file + ' was checked. It can be found at Validated_Data/' + file_name_fa + '.fasta')

        else:
            multiline_convert = multiline_fasta_convert(decompressed, 'data_val_temp/' + file_name_fa)

            if check_fasta(multiline_convert):
                if args.gzip:
                    gzip_file(multiline_convert, 'Validated_Data/' + file_name_fa + '.fasta.gz')
                    shutil.rmtree('data_val_temp')  # Removing Temp Files
                    print('Fasta File ' + args.file + ' was checked and whitespace removed. It can be found at Validated_Data/' + file_name_fa + '.fasta.gz')
                else:
                    shutil.copy(multiline_convert, 'Validated_Data/' + file_name_fa + '.fasta')
                    shutil.rmtree('data_val_temp')  # Removing Temp Files
                    print('Fasta File ' + args.file + ' was checked, whitespace removed, and compressed. It can be found at Validated_Data/' + file_name_fa + '.fasta')
            else:
                print('File ' + args.file + ' did not pass fasta check, or multi-line fasta check')

    else:
        print("Unknown mode")

if __name__ == '__main__':
    main()